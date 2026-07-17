---
title: Getting Started スクリプト
---

# Getting Started スクリプト

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- Replicator ワークフローの基本設定（**capture on play の無効化、orchestrator.step、RTSubframes、DLSS 品質モード、wait_for_render、write-to-fabric**）
- **BasicWriter** による基本のデータキャプチャ
- **カスタムライターとアノテータ**による複数カメラからのデータアクセス
- **Replicator グラフ＋カスタム USD API** の 2 方式のランダム化の併用
- 物理シミュレーション中の**イベントトリガーによるデータキャプチャ**
- **バッチランダム化**と `wait_for_render` / write-to-fabric による**パフォーマンス最適化**

## はじめに

### 前提条件

- Python プログラミングの基本
- USD（Universal Scene Description）の概念に慣れていること
- データキャプチャに十分なディスク容量（解像度とフレーム数に依存）
- レンダリングに十分なメモリを持つ GPU（推奨：8 GB 以上）

### 所要時間

約 40〜60 分

### 概要

このチュートリアルは、典型的な Isaac Sim Replicator ワークフローの出発点となる一連のサンプルスクリプトを解説します。各サンプルには 2 つの実行方法があります：

| 実行方法 | 特徴 |
|---|---|
| **Script Editor**（非同期） | 起動済みの Isaac Sim 内で実行。`await rep.orchestrator.step_async()` のように非同期 API を使う |
| **スタンドアロン**（同期） | `./python.sh` でスクリプトから Isaac Sim ごと起動。`rep.orchestrator.step()` のように同期 API を使う |

!!! note "このページでの表記について"
    公式ページには各サンプルの Script Editor 版とスタンドアロン版の両方の全文が掲載されていますが、**違いは定型部分だけ**です。本ページでは Script Editor 版のコードを掲載し、スタンドアロン版は同梱サンプルの実行コマンドを示します。スタンドアロン版との違いは共通して次の 3 点です：

    1. 冒頭で `SimulationApp` を起動する（`simulation_app = SimulationApp(launch_config={"headless": False})`）
    2. `step_async()` / `wait_until_complete_async()` の代わりに同期版の `step()` / `wait_until_complete()` を使う（`async` / `await` が不要）
    3. アプリ更新の待機に `await omni.kit.app.get_app().next_update_async()` ではなく `simulation_app.update()` を使う（例 4 など）

## 基本設定

サンプルに入る前に、このワークフローで共通して使われる設定を押さえます。

### orchestrator.step 関数

Replicator では、`orchestrator.step()` が SDG プロセス全体（ランダム化の実行とデータキャプチャ）をトリガーします。Isaac Sim のワークフローでは、この関数は**データキャプチャのトリガー専用**として使い、ランダム化はカスタムイベントに割り当てて手動でトリガーするのが定石です。

```python
rep.orchestrator.step(rt_subframes: int = -1, pause_timeline: bool = True, delta_time: float = None, wait_for_render: bool = True)
```

| 引数 | 意味 |
|---|---|
| `rt_subframes` | レンダリングするサブフレーム数。0 より大きい値でサブフレーム生成が有効になり、レンダリングアーティファクトの低減やマテリアルの完全な読み込みに役立つ |
| `pause_timeline` | True なら、ステップ後にタイムライン（再生中の場合）を一時停止する |
| `delta_time` | ステップ中にタイムラインを進める時間。None ならタイムラインのレートを使用 |
| `wait_for_render` | True なら、レンダラーが現在のフレームを描画し終えるまでブロックする。既定は True |

### Capture on Play の無効化

Replicator は既定では**再生中に毎フレーム**データをキャプチャします。Isaac Sim のワークフローでは、`step()` によるユーザー定義のタイミングでキャプチャするため、このフラグを無効にします：

```python
import omni.replicator.core as rep
rep.orchestrator.set_capture_on_play(False)
# または
import carb.settings
carb.settings.get_settings().set("/omni/replicator/captureOnPlay", False)
```

### RTSubframes

高速に動く／テレポートするアセットによるゴーストや、弱い照明条件によるアーティファクトを減らしたい場合、同じフレームを複数回レンダリングする **RTSubframes** を使います。通常は `step()` の引数で指定しますが、グローバル設定も可能です：

```python
# 特定のキャプチャステップに対して指定
rep.orchestrator.step(rt_subframes=4)

# グローバルに指定
import carb.settings
carb.settings.get_settings().set("/omni/replicator/RTSubframes", 4)
```

### DLSS 品質モード

SDG ワークフローでは、レンダリングアーティファクトを避けるために **DLSS**（Deep Learning Super Sampling：低解像度のレンダリング結果を AI で高解像度化する超解像機能）を **Quality モード**に設定することが推奨されます。低解像度（特に 600×600 未満）では、既定の Performance モードで、生成画像のエッジが透けたり正しく描画されなかったりする問題が起きることがあります：

```python
import carb.settings
# DLSS を Quality モード（2）に設定。選択肢：0（Performance）、1（Balanced）、2（Quality）、3（Auto）
carb.settings.get_settings().set("/rtx/post/dlss/execMode", 2)
```

### wait_for_render パラメータ

既定では、`step()` はレンダラーが現在のフレームを生成し終えるまでブロックしてから戻ります。`wait_for_render=False` を指定すると、キャプチャ要求をレンダリングパイプラインから切り離し、前のフレームのレンダリング中に次のランダム化を開始できます。`step()` の戻り時点のシミュレーション状態とキャプチャデータが厳密に一致する必要がないワークフローでは、スループットを大きく向上できます：

```python
# 既定の動作：フレームのレンダリング完了までブロック
rep.orchestrator.step(wait_for_render=True)

# ノンブロッキング：即座に戻り、次のランダム化を開始できる
rep.orchestrator.step(wait_for_render=False)
```

!!! warning
    `wait_for_render=False` では、アノテーションやライターのデータが、直近の `step()` 呼び出しでトリガーしたフレームではなく**前のフレームに対応する**場合があります。フレームとデータの厳密な対応が不要な場合にのみ使用してください。

### Write to Fabric モード

Fabric は、レンダラーが直接読み取るランタイムのデータレイヤーです。既定では、Replicator は属性の変更（位置・回転・色など）を USD ステージに書き込み、それがレンダリング前に Fabric へ同期されます。write-to-fabric モードを有効にすると、USD ステージを介さずに Fabric へ直接書き込むため、USD→Fabric の同期オーバーヘッドが減り、ランダム化のパフォーマンスが向上します：

```python
import carb.settings
# write-to-fabric モードを有効化
carb.settings.get_settings().set("/exts/omni.replicator.core/enableWriteToFabric", True)
```

!!! note
    変更は USD ステージをバイパスして Fabric に直接書き込まれるため、USD ステージには反映されず、シーンを保存しても永続化されません。このモードは、データ生成中の一時的なランダム化を想定したもので、恒久的なシーン変更には向きません。

### カスタムイベントによるランダム化

Replicator のランダマイザは、カスタムイベントで**キャプチャとは独立に**トリガーできます。`trigger.on_custom_event` でランダマイザを登録し、`utils.send_og_event` で起動します。この方式で登録したランダム化グラフは `step()` ではトリガーされません：

```python
# ドームライトを作成して色をランダム化するグラフを、カスタムイベントで登録
with rep.trigger.on_custom_event(event_name="randomize_dome_light_color"):
    rep.create.light(light_type="Dome", color=rep.distribution.uniform((0, 0, 0), (1, 1, 1)))

# カスタムイベント名を指定してランダム化グラフをトリガー
rep.utils.send_og_event(event_name="randomize_dome_light_color")
```

### 書き込み完了の待機

アプリケーションを閉じる前に、**すべてのデータがディスクに書き終わっている**ことを保証しないとデータを失う可能性があります。複数カメラや大きな解像度による高スループットでは I/O がボトルネックになることもあります（対策は公式の I/O Optimization Guide 参照）。書き込み完了は `wait_until_complete`（非同期版は `wait_until_complete_async`）で待ちます。

## 例 1：BasicWriter によるデータキャプチャ

キューブとドームライトのシーンを作り、キューブにセマンティックラベルを付けて、RGB と 2D バウンディングボックスをディスクに保存する最小構成の例です。

スタンドアロン版の実行（Windows では `python.sh` の代わりに `python.bat`）：

```bash
./python.sh standalone_examples/api/isaacsim.replicator.examples/sdg_getting_started_01.py
```

Script Editor 版：

```python
import asyncio
import os

import carb.settings
import omni.replicator.core as rep
import omni.usd


async def run_example_async():
    # 新しいステージを作成し、capture on play を無効化
    omni.usd.get_context().new_stage()
    rep.orchestrator.set_capture_on_play(False)

    # DLSS を Quality モード（2）に設定
    carb.settings.get_settings().set("rtx/post/dlss/execMode", 2)

    # ドームライトとキューブでステージをセットアップ（functional API）
    rep.functional.create.xform(name="World")
    rep.functional.create.dome_light(intensity=500, parent="/World", name="DomeLight")
    cube = rep.functional.create.cube(parent="/World", name="Cube")
    rep.functional.modify.semantics(cube, {"class": "my_cube"}, mode="add")

    # カメラを作成してレンダープロダクトを作成
    cam = rep.functional.create.camera(position=(5, 5, 5), look_at=(0, 0, 0), parent="/World", name="Camera")
    rp = rep.create.render_product(cam, (512, 512), name="MyRenderProduct")

    # DiskBackend + BasicWriter で RGB と 2D バウンディングボックス（tight）を書き込む
    backend = rep.backends.get("DiskBackend")
    out_dir = os.path.join(os.getcwd(), "_out_basic_writer")
    backend.initialize(output_dir=out_dir)
    print(f"Output directory: {out_dir}")
    writer = rep.writers.get("BasicWriter")
    writer.initialize(backend=backend, rgb=True, bounding_box_2d_tight=True)
    writer.attach(rp)

    # データキャプチャをリクエスト（データはライターがディスクに書き込む）
    for i in range(3):
        print(f"Step {i}")
        await rep.orchestrator.step_async()

    # データの書き込み完了を待ってからリソースを解放
    await rep.orchestrator.wait_until_complete_async()
    writer.detach()
    rp.destroy()


# 実行
asyncio.ensure_future(run_example_async())
```

出力ディレクトリには、RGB 画像と、`.npy` / `.json` 形式のバウンディングボックスアノテーションが保存されます：

![例 1 の出力](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_4.5_replicator_tut_external_getting_started_01.jpg)

## 例 2：カスタムライターとアノテータ・複数カメラ

カスタムライターでカメラパラメータや 3D バウンディングボックスなどのアノテータデータにアクセスし、2 台のカメラ（トップビューカメラと俯瞰の Perspective カメラ）から **PoseWriter** でデータを書き出す例です。**アノテータから直接データを取得する**方法（`get_data()`）も登場します。

```bash
./python.sh standalone_examples/api/isaacsim.replicator.examples/sdg_getting_started_02.py
```

Script Editor 版：

```python
import asyncio
import os

import carb.settings
import omni.replicator.core as rep
import omni.usd
from omni.replicator.core import Writer


# アノテータデータにアクセスするカスタムライターを作成
class MyWriter(Writer):
    def __init__(self, camera_params: bool = True, bounding_box_3d: bool = True):
        # データをレンダープロダクト視点で構成する（legacy / annotator / renderProduct から選択）
        self.data_structure = "renderProduct"
        self.annotators = []
        if camera_params:
            self.annotators.append(rep.annotators.get("camera_params"))
        if bounding_box_3d:
            self.annotators.append(rep.annotators.get("bounding_box_3d"))
        self._frame_id = 0

    def write(self, data: dict):
        print(f"[MyWriter][{self._frame_id}] data:")
        for key, value in data.items():
            print(f"  {key}: {value}")
        self._frame_id += 1


# ライターを登録
rep.writers.register_writer(MyWriter)


async def run_example_async():
    # 新しいステージを作成し、capture on play を無効化
    omni.usd.get_context().new_stage()
    rep.orchestrator.set_capture_on_play(False)

    # DLSS を Quality モード（2）に設定
    carb.settings.get_settings().set("rtx/post/dlss/execMode", 2)

    # ステージのセットアップ（functional API）
    rep.functional.create.xform(name="World")
    rep.functional.create.dome_light(intensity=500, parent="/World", name="DomeLight")
    cube = rep.functional.create.cube(parent="/World", name="Cube")
    rep.functional.modify.semantics(cube, {"class": "my_cube"}, mode="add")

    # トップビューカメラと俯瞰カメラの 2 視点からキャプチャ
    top_cam = rep.functional.create.camera(position=(0, 0, 5), look_at=(0, 0, 0), parent="/World", name="TopCamera")
    persp_cam = rep.functional.create.camera(position=(5, 5, 5), look_at=(0, 0, 0), parent="/World", name="PerspCamera")

    # レンダープロダクトを作成
    rp_top = rep.create.render_product(top_cam.GetPath(), (400, 400), name="top_view")
    rp_persp = rep.create.render_product(persp_cam.GetPath(), (512, 512), name="persp_view")

    # アノテータで直接データにアクセスする（アノテータはレンダープロダクトにアタッチする）
    rgb_annotator_top = rep.annotators.get("rgb")
    rgb_annotator_top.attach(rp_top)
    rgb_annotator_persp = rep.annotators.get("rgb")
    rgb_annotator_persp.attach(rp_persp)

    # カスタムライターでアノテータデータにアクセス
    custom_writer = rep.writers.get("MyWriter")
    custom_writer.initialize(camera_params=True, bounding_box_3d=True)
    custom_writer.attach([rp_top, rp_persp])

    # PoseWriter でデータをディスクに書き込む
    pose_writer = rep.WriterRegistry.get("PoseWriter")
    out_dir = os.path.join(os.getcwd(), "_out_pose_writer")
    print(f"Output directory: {out_dir}")
    pose_writer.initialize(output_dir=out_dir, write_debug_images=True)
    pose_writer.attach([rp_top, rp_persp])

    # データキャプチャをリクエスト
    for i in range(3):
        print(f"Step {i}")
        await rep.orchestrator.step_async()

        # アノテータからデータを取得
        rgb_data_cam = rgb_annotator_top.get_data()
        rgb_data_persp = rgb_annotator_persp.get_data()
        print(f"[Annotator][Cam][{i}] rgb_data_cam shape: {rgb_data_cam.shape}")
        print(f"[Annotator][Persp][{i}] rgb_data_persp shape: {rgb_data_persp.shape}")

    # データの書き込み完了を待ってからリソースを解放
    await rep.orchestrator.wait_until_complete_async()
    pose_writer.detach()
    custom_writer.detach()
    rgb_annotator_top.detach()
    rgb_annotator_persp.detach()
    rp_top.destroy()
    rp_persp.destroy()


# 実行
asyncio.ensure_future(run_example_async())
```

出力ディレクトリには、3D バウンディングボックスがオーバーレイされた RGB 画像と、フレームデータの `.json` ファイルが保存されます。アノテータとカスタムライターのデータはターミナルに出力されます：

![例 2 の出力](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_4.5_replicator_tut_external_getting_started_02.jpg)

## 例 3：カスタムランダム化（Replicator グラフ＋USD API）

2 種類のランダム化を組み合わせる例です：

- **Replicator のグラフベースランダマイザ**（カスタムイベントでトリガー）— ドームライトの色
- **カスタム USD API ランダム化**（通常の Python 関数）— キューブの位置

データは BasicWriter でセマンティックセグメンテーション付きでキャプチャします。

```bash
./python.sh standalone_examples/api/isaacsim.replicator.examples/sdg_getting_started_03.py
```

Script Editor 版：

```python
import asyncio
import os
import random

import carb.settings
import omni.replicator.core as rep
import omni.usd


# グラフベースのランダマイザを使わずにプリムの位置をランダム化する
def randomize_location(prim):
    random_pos = (random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1))
    rep.functional.modify.position(prim, random_pos)


async def run_example_async():
    # 新しいステージを作成し、capture on play を無効化
    omni.usd.get_context().new_stage()
    rep.orchestrator.set_capture_on_play(False)
    random.seed(42)
    rep.set_global_seed(42)

    # DLSS を Quality モード（2）に設定
    carb.settings.get_settings().set("rtx/post/dlss/execMode", 2)

    # ステージのセットアップ（functional API）
    rep.functional.create.xform(name="World")
    cube = rep.functional.create.cube(parent="/World", name="Cube")
    rep.functional.modify.semantics(cube, {"class": "my_cube"}, mode="add")

    # カスタムイベントでトリガーする Replicator ランダマイザを作成
    with rep.trigger.on_custom_event(event_name="randomize_dome_light_color"):
        rep.create.light(light_type="Dome", color=rep.distribution.uniform((0, 0, 0), (1, 1, 1)))

    # カメラを作成してレンダープロダクトを作成
    cam = rep.functional.create.camera(position=(5, 5, 5), look_at=(0, 0, 0), parent="/World", name="Camera")
    rp = rep.create.render_product(cam, (512, 512))

    # DiskBackend + BasicWriter で RGB とセマンティックセグメンテーションを書き込む
    backend = rep.backends.get("DiskBackend")
    out_dir = os.path.join(os.getcwd(), "_out_basic_writer_rand")
    backend.initialize(output_dir=out_dir)
    print(f"Output directory: {out_dir}")
    writer = rep.writers.get("BasicWriter")
    writer.initialize(backend=backend, rgb=True, semantic_segmentation=True, colorize_semantic_segmentation=True)
    writer.attach(rp)

    # データキャプチャをリクエスト
    for i in range(3):
        print(f"Step {i}")
        # 1 ステップおきにカスタムイベント（グラフベース）のランダマイザをトリガー
        if i % 2 == 1:
            rep.utils.send_og_event(event_name="randomize_dome_light_color")

        # カスタム USD API の位置ランダマイザを実行
        randomize_location(cube)

        # Replicator ランダマイザはカスタムイベントでトリガーされる設定なので、
        # step はライターのトリガーのみを行う
        await rep.orchestrator.step_async(rt_subframes=32)

    # データの書き込み完了を待ってからリソースを解放
    await rep.orchestrator.wait_until_complete_async()
    writer.detach()
    rp.destroy()


# 実行
asyncio.ensure_future(run_example_async())
```

キューブの位置は毎キャプチャ、ドームライトの色は 1 回おきにランダム化されます：

![例 3 の出力](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_4.5_replicator_tut_external_getting_started_03.jpg)

## 例 4：イベントトリガーのデータキャプチャ（物理シミュレーション）

物理シミュレーション中に**特定の条件を満たしたときだけ**データをキャプチャする例です。キューブと球を落下させ、キューブの高さが一定間隔（0.5）下がるたびにキャプチャします。キャプチャ中はタイムラインを一時停止してデータの一貫性を保証します。

```bash
./python.sh standalone_examples/api/isaacsim.replicator.examples/sdg_getting_started_04.py
```

Script Editor 版（主要部分）：

```python
import asyncio
import os

import carb.settings
import omni.kit.app
import omni.replicator.core as rep
import omni.timeline
import omni.usd
from isaacsim.core.experimental.prims import RigidPrim
from pxr import UsdGeom


async def run_example_async():
    # 新しいステージを作成し、capture on play を無効化
    omni.usd.get_context().new_stage()
    rep.orchestrator.set_capture_on_play(False)

    # DLSS を Quality モード（2）に設定
    carb.settings.get_settings().set("rtx/post/dlss/execMode", 2)

    # ライトを追加
    rep.functional.create.xform(name="World")
    rep.functional.create.dome_light(intensity=500, parent="/World", name="DomeLight")

    # コライダーとリジッドボディ付きのキューブを高さ 2 に作成
    cube = rep.functional.create.cube(name="Cube", parent="/World")
    rep.functional.modify.position(cube, (0, 0, 2))
    rep.functional.modify.semantics(cube, {"class": "my_cube"}, mode="add")
    rep.functional.physics.apply_rigid_body(cube, with_collider=True)

    # 隣に球も作成
    sphere = rep.functional.create.sphere(name="Sphere", parent="/World")
    rep.functional.modify.position(sphere, (-1, -1, 2))
    rep.functional.modify.semantics(sphere, {"class": "my_sphere"}, mode="add")
    rep.functional.physics.apply_rigid_body(sphere, with_collider=True)

    # カメラとレンダープロダクトのセットアップ
    cam = rep.functional.create.camera(position=(5, 5, 5), look_at=(0, 0, 0), parent="/World", name="Camera")
    rp = rep.create.render_product(cam, (512, 512))

    # DiskBackend + BasicWriter のセットアップ
    backend = rep.backends.get("DiskBackend")
    out_dir = os.path.join(os.getcwd(), "_out_basic_writer_sim")
    backend.initialize(output_dir=out_dir)
    print(f"Output directory: {out_dir}")
    writer = rep.writers.get("BasicWriter")
    writer.initialize(backend=backend, rgb=True, semantic_segmentation=True, colorize_semantic_segmentation=True)
    writer.attach(rp)

    # タイムラインを開始（アプリの更新に合わせて進む）
    timeline = omni.timeline.get_timeline_interface()
    timeline.play()

    # ワールド座標・速度に簡単にアクセスできるよう、キューブを RigidPrim でラップ
    cube_rigid = RigidPrim(str(cube.GetPrimPath()))

    # キャプチャ中の表示切り替え用に Imageable としてもラップ
    cube_imageable = UsdGeom.Imageable(cube)

    # キャプチャ間隔（メートル）を定義
    capture_interval_meters = 0.5
    cube_pos = cube_rigid.get_world_poses(indices=[0])[0].numpy()
    previous_capture_height = cube_pos[0, 2]

    # アプリを更新してタイムライン（と暗黙的にシミュレーション）を進める
    for i in range(100):
        await omni.kit.app.get_app().next_update_async()
        cube_pos = cube_rigid.get_world_poses(indices=[0])[0].numpy()
        current_height = cube_pos[0, 2]
        distance_dropped = previous_capture_height - current_height
        print(f"Step {i}; cube height: {current_height:.3f}; drop since last capture: {distance_dropped:.3f}")

        # キューブが地面より下に落ちたらシミュレーションを停止
        if current_height < 0:
            print(f"\t Cube fell below the ground at height {current_height:.3f}, stopping simulation..")
            break

        # しきい値の距離だけ落下するたびにキャプチャ
        if distance_dropped >= capture_interval_meters:
            print(f"\t Capturing at height {current_height:.3f}")
            previous_capture_height = current_height

            # delta_time=0.0 にすると、キャプチャ中にタイムラインが進まない
            await rep.orchestrator.step_async(delta_time=0.0)

            # キューブを非表示にしてもう一度キャプチャ
            print("\t Capturing with cube hidden")
            cube_imageable.MakeInvisible()
            await rep.orchestrator.step_async(delta_time=0.0)
            cube_imageable.MakeVisible()

            # タイムラインを再開してシミュレーションを続行
            timeline.play()

    # シミュレーションを一時停止
    timeline.pause()

    # データの書き込み完了を待ってからリソースを解放
    await rep.orchestrator.wait_until_complete_async()
    writer.detach()
    rp.destroy()


# 実行
asyncio.ensure_future(run_example_async())
```

出力には、キューブの落下高さの間隔ごとのキャプチャと、キューブを非表示にした 2 回目のキャプチャが含まれます。`delta_time=0.0` によってキャプチャ中はタイムラインが進まないため、**同一のシミュレーション状態を複数回キャプチャ**できます：

![例 4 の出力](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_4.5_replicator_tut_external_getting_started_04.jpg)

## 例 5：バッチランダム化とパフォーマンス最適化

functional API の**バッチ作成**（`rep.functional.create_batch`）と `ReplicatorRNG` を使って 100 個のキューブを一括作成・一括ランダム化する例です。パフォーマンス比較のため、3 つの構成——既定（`wait_for_render=True`）、ノンブロッキングキャプチャ（`wait_for_render=False`）、ノンブロッキング＋write-to-fabric 有効——を順に実行します。各実行では、ステップごとのランダム化・キャプチャ時間と、`wait_until_complete` までを含む合計時間が出力され、`wait_for_render` と write-to-fabric がスループットに与える影響を確認できます。

```bash
./python.sh standalone_examples/api/isaacsim.replicator.examples/sdg_getting_started_05.py
```

Script Editor 版：

```python
import asyncio
import os
import time

import carb.settings
import omni.replicator.core as rep
import omni.usd

NUM_CUBES = 100
NUM_CAPTURES = 10


async def run_example_async(wait_for_render, write_to_fabric):
    print(f"\n[SDG] Running with wait_for_render={wait_for_render}, write_to_fabric={write_to_fabric}")
    omni.usd.get_context().new_stage()
    rep.orchestrator.set_capture_on_play(False)

    settings = carb.settings.get_settings()
    settings.set("rtx/post/dlss/execMode", 2)
    settings.set("/exts/omni.replicator.core/enableWriteToFabric", write_to_fabric)

    rng = rep.rng.ReplicatorRNG(seed=42)

    # ドームライトとバッチ作成したキューブでステージをセットアップ
    rep.functional.create.xform(name="World")
    rep.functional.create.dome_light(intensity=500, parent="/World", name="DomeLight")
    cubes = rep.functional.create_batch.cube(
        count=NUM_CUBES,
        parent="/World",
        name="Cube",
        semantics={"class": "my_cube"},
    )
    rep.functional.modify.scale(cubes, (0.2, 0.2, 0.2))

    # カメラとレンダープロダクトを作成
    cam = rep.functional.create.camera(position=(5, 5, 5), look_at=(0, 0, 0), parent="/World", name="Camera")
    rp = rep.create.render_product(cam, (512, 512))

    # BasicWriter（rgb アノテータ）でデータを書き込む
    backend = rep.backends.get("DiskBackend")
    out_dir = os.path.join(os.getcwd(), f"_out_fabric_{write_to_fabric}_wait_{wait_for_render}")
    backend.initialize(output_dir=out_dir)
    print(f"[SDG] Output directory: {out_dir}")
    writer = rep.writers.get("BasicWriter")
    writer.initialize(backend=backend, rgb=True)
    writer.attach(rp)

    # ランダム化とキャプチャを行い、各フェーズの時間を計測
    randomization_times_ms = []
    capture_times_ms = []
    total_start = time.perf_counter()

    for i in range(NUM_CAPTURES):
        random_positions = rng.generator.uniform((-3.0, -3.0, -3.0), (3.0, 3.0, 3.0), size=(NUM_CUBES, 3))
        random_rotations = rng.generator.uniform((0.0, 0.0, 0.0), (360.0, 360.0, 360.0), size=(NUM_CUBES, 3))
        random_scales = rng.generator.uniform(0.1, 0.4, size=(NUM_CUBES, 3))

        rand_start = time.perf_counter()
        rep.functional.modify.pose(
            cubes,
            position_value=random_positions,
            rotation_value=random_rotations,
            scale_value=random_scales,
        )
        rep.functional.randomizer.display_color(cubes, rng=rng)
        rand_ms = (time.perf_counter() - rand_start) * 1000.0
        randomization_times_ms.append(rand_ms)

        cap_start = time.perf_counter()
        await rep.orchestrator.step_async(wait_for_render=wait_for_render)
        cap_ms = (time.perf_counter() - cap_start) * 1000.0
        capture_times_ms.append(cap_ms)

        print(f"[SDG] Step {i}: randomization {rand_ms:.1f} ms, capture {cap_ms:.1f} ms")

    # すべてのデータの書き込み完了を待つ
    print("[SDG] Waiting for all data to be written to disk..")
    await rep.orchestrator.wait_until_complete_async()
    total_ms = (time.perf_counter() - total_start) * 1000.0

    avg_rand = sum(randomization_times_ms) / len(randomization_times_ms)
    avg_cap = sum(capture_times_ms) / len(capture_times_ms)
    print(f"[SDG] Avg randomization: {avg_rand:.1f} ms, avg capture: {avg_cap:.1f} ms, total: {total_ms:.1f} ms")

    writer.detach()
    rp.destroy()


async def run_examples_async():
    # 構成を変えて実行し、パフォーマンスを比較
    await run_example_async(wait_for_render=True, write_to_fabric=False)
    await run_example_async(wait_for_render=False, write_to_fabric=False)
    await run_example_async(wait_for_render=False, write_to_fabric=True)


asyncio.ensure_future(run_examples_async())
```

構成ごとに別々のディレクトリへ出力され、ターミナルにはステップごとのランダム化・キャプチャ時間（ミリ秒）と合計時間が表示されるため、3 つのモードを直接比較できます。

## トラブルシューティング

Getting Started スクリプトに関するトラブルシューティングは、公式の Replicator Troubleshooting ページの Getting Started Scripts Issues 節を参照してください。

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. Replicator ワークフローの**基本設定**（capture on play 無効化、step 関数、RTSubframes、DLSS Quality、wait_for_render、write-to-fabric）
2. **BasicWriter** による最小構成のデータキャプチャ（`rep.functional` API と DiskBackend）
3. **カスタムライター／アノテータ**によるデータアクセスと複数カメラ・複数ライターの併用
4. **カスタムイベント（Replicator グラフ）と USD API** の 2 方式のランダム化
5. 物理シミュレーションの**条件付きキャプチャ**と `delta_time=0.0` による状態の固定
6. **バッチ作成・バッチランダム化**（`rep.functional.create_batch`、`ReplicatorRNG`）とパフォーマンス比較

### さらに学ぶには

- 高度なランダム化：公式の [Randomizer Details](https://docs.omniverse.nvidia.com/extensions/latest/ext_replicator/randomizer_details.html)
- I/O 最適化：公式の [I/O Optimization Guide](https://docs.omniverse.nvidia.com/extensions/latest/ext_replicator/io_guidelines.html)

## 次のステップ

- [合成データ生成チュートリアル一覧](index.md)に戻る。今後、シーンベース／オブジェクトベースの SDG チュートリアルを追加予定です。
