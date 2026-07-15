---
title: Getting Started スクリプト
---

# Getting Started スクリプト

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- Replicator ワークフローの基本設定（**capture on play の無効化、orchestrator.step、RTSubframes、DLSS 品質モード**）
- **BasicWriter** による基本のデータキャプチャ
- **カスタムライターとアノテータ**による複数カメラからのデータアクセス
- **Replicator グラフ＋カスタム USD API** の 2 方式のランダム化の併用
- 物理シミュレーション中の**イベントトリガーによるデータキャプチャ**

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
    3. 末尾で `simulation_app.is_running()` のループと `simulation_app.close()` を書く

## 基本設定

サンプルに入る前に、このワークフローで共通して使われる設定を押さえます。

### orchestrator.step 関数

Replicator では、`orchestrator.step()` が SDG プロセス全体（ランダム化の実行とデータキャプチャ）をトリガーします。Isaac Sim のワークフローでは、この関数は**データキャプチャのトリガー専用**として使い、ランダム化はカスタムイベントに割り当てて手動でトリガーするのが定石です。

```python
rep.orchestrator.step(rt_subframes: int = -1, pause_timeline: bool = True, delta_time: float = None)
```

| 引数 | 意味 |
|---|---|
| `rt_subframes` | レンダリングするサブフレーム数。0 より大きい値でサブフレーム生成が有効になり、レンダリングアーティファクトの低減やマテリアルの完全な読み込みに役立つ |
| `pause_timeline` | True なら、ステップ後にタイムライン（再生中の場合）を一時停止する |
| `delta_time` | ステップ中にタイムラインを進める時間。None ならタイムラインのレートを使用 |

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

SDG ワークフローでは、レンダリングアーティファクトを避けるために **DLSS を Quality モード**に設定することが推奨されます。低解像度（特に 600×600 未満）では、既定の Performance モードで、生成画像のエッジが透けたり正しく描画されなかったりする問題が起きることがあります：

```python
import carb.settings
# DLSS を Quality モード（2）に設定。選択肢：0（Performance）、1（Balanced）、2（Quality）、3（Auto）
carb.settings.get_settings().set("/rtx/post/dlss/execMode", 2)
```

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
from isaacsim.core.utils.semantics import add_labels
from pxr import Sdf


async def run_example_async():
    # 新しいステージを作成し、capture on play を無効化
    omni.usd.get_context().new_stage()
    rep.orchestrator.set_capture_on_play(False)

    # DLSS を Quality モード（2）に設定
    carb.settings.get_settings().set("rtx/post/dlss/execMode", 2)

    # ドームライトとキューブでステージをセットアップ
    stage = omni.usd.get_context().get_stage()
    dome_light = stage.DefinePrim("/World/DomeLight", "DomeLight")
    dome_light.CreateAttribute("inputs:intensity", Sdf.ValueTypeNames.Float).Set(500.0)
    cube = stage.DefinePrim("/World/Cube", "Cube")
    add_labels(cube, labels=["MyCube"], instance_name="class")

    # ビューポートの Perspective カメラでレンダープロダクトを作成
    rp = rep.create.render_product("/OmniverseKit_Persp", (512, 512))

    # BasicWriter で RGB と 2D バウンディングボックス（tight）を書き込む
    writer = rep.writers.get("BasicWriter")
    out_dir = os.path.join(os.getcwd(), "_out_basic_writer")
    print(f"Output directory: {out_dir}")
    writer.initialize(output_dir=out_dir, rgb=True, bounding_box_2d_tight=True)
    writer.attach(rp)

    # データキャプチャをリクエスト（データはライターがディスクに書き込む）
    for i in range(3):
        print(f"Step {i}")
        await rep.orchestrator.step_async()

    # ライターからデタッチしてからレンダープロダクトを破棄し、リソースを解放
    writer.detach()
    rp.destroy()

    # データの書き込み完了を待つ
    await rep.orchestrator.wait_until_complete_async()


# 実行
asyncio.ensure_future(run_example_async())
```

出力ディレクトリには、RGB 画像と、`.npy` / `.json` 形式のバウンディングボックスアノテーションが保存されます：

![例 1 の出力](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_replicator_tut_external_getting_started_01.jpg)

## 例 2：カスタムライターとアノテータ・複数カメラ

カスタムライターでカメラパラメータや 3D バウンディングボックスなどのアノテータデータにアクセスし、2 台のカメラ（カスタムカメラとビューポート Perspective）から **PoseWriter** でデータを書き出す例です。**アノテータから直接データを取得する**方法（`get_data()`）も登場します。

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
from isaacsim.core.utils.semantics import add_labels
from omni.replicator.core import Writer
from pxr import Sdf, UsdGeom


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

    def write(self, data):
        print(f"[MyWriter][{self._frame_id}] data:{data}")
        self._frame_id += 1


# ライターを登録
rep.writers.register_writer(MyWriter)


async def run_example_async():
    # 新しいステージを作成し、capture on play を無効化
    omni.usd.get_context().new_stage()
    rep.orchestrator.set_capture_on_play(False)

    # DLSS を Quality モード（2）に設定
    carb.settings.get_settings().set("rtx/post/dlss/execMode", 2)

    # ステージのセットアップ
    stage = omni.usd.get_context().get_stage()
    dome_light = stage.DefinePrim("/World/DomeLight", "DomeLight")
    dome_light.CreateAttribute("inputs:intensity", Sdf.ValueTypeNames.Float).Set(500.0)
    cube = stage.DefinePrim("/World/Cube", "Cube")
    add_labels(cube, labels=["MyCube"], instance_name="class")

    # カスタムカメラとビューポート Perspective の 2 視点からキャプチャ
    camera = stage.DefinePrim("/World/Camera", "Camera")
    UsdGeom.Xformable(camera).AddTranslateOp().Set((0, 0, 20))

    # レンダープロダクトを作成
    rp_cam = rep.create.render_product(camera.GetPath(), (400, 400), name="camera_view")
    rp_persp = rep.create.render_product("/OmniverseKit_Persp", (512, 512), name="perspective_view")

    # アノテータで直接データにアクセスする（アノテータはレンダープロダクトにアタッチする）
    rgb_annotator_cam = rep.annotators.get("rgb")
    rgb_annotator_cam.attach(rp_cam)
    rgb_annotator_persp = rep.annotators.get("rgb")
    rgb_annotator_persp.attach(rp_persp)

    # カスタムライターでアノテータデータにアクセス
    custom_writer = rep.writers.get("MyWriter")
    custom_writer.initialize(camera_params=True, bounding_box_3d=True)
    custom_writer.attach([rp_cam, rp_persp])

    # PoseWriter でデータをディスクに書き込む
    pose_writer = rep.WriterRegistry.get("PoseWriter")
    out_dir = os.path.join(os.getcwd(), "_out_pose_writer")
    print(f"Output directory: {out_dir}")
    pose_writer.initialize(output_dir=out_dir, write_debug_images=True)
    pose_writer.attach([rp_cam, rp_persp])

    # データキャプチャをリクエスト
    for i in range(3):
        print(f"Step {i}")
        await rep.orchestrator.step_async()

        # アノテータからデータを取得
        rgb_data_cam = rgb_annotator_cam.get_data()
        rgb_data_persp = rgb_annotator_persp.get_data()
        print(f"[Annotator][Cam][{i}] rgb_data_cam shape: {rgb_data_cam.shape}")
        print(f"[Annotator][Persp][{i}] rgb_data_persp shape: {rgb_data_persp.shape}")

    # アノテータ・ライターからレンダープロダクトをデタッチして破棄し、リソースを解放
    pose_writer.detach()
    custom_writer.detach()
    rgb_annotator_cam.detach()
    rgb_annotator_persp.detach()
    rp_cam.destroy()
    rp_persp.destroy()

    # データの書き込み完了を待つ
    await rep.orchestrator.wait_until_complete_async()


asyncio.ensure_future(run_example_async())
```

出力ディレクトリには、3D バウンディングボックスがオーバーレイされた RGB 画像と、フレームデータの `.json` ファイルが保存されます。アノテータとカスタムライターのデータはターミナルに出力されます：

![例 2 の出力](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_replicator_tut_external_getting_started_02.jpg)

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
import omni.kit.app
import omni.replicator.core as rep
import omni.usd
from isaacsim.core.utils.semantics import add_labels
from pxr import UsdGeom


# USD API を使ったカスタムランダマイザ関数
def randomize_location(prim):
    if not prim.GetAttribute("xformOp:translate"):
        UsdGeom.Xformable(prim).AddTranslateOp()
    translate = prim.GetAttribute("xformOp:translate")
    translate.Set((random.uniform(-2, 2), random.uniform(-2, 2), random.uniform(-2, 2)))


async def run_example_async():
    # 新しいステージを作成し、capture on play を無効化
    omni.usd.get_context().new_stage()
    rep.orchestrator.set_capture_on_play(False)
    random.seed(42)
    rep.set_global_seed(42)

    # DLSS を Quality モード（2）に設定
    carb.settings.get_settings().set("rtx/post/dlss/execMode", 2)

    # ステージのセットアップ
    stage = omni.usd.get_context().get_stage()
    cube = stage.DefinePrim("/World/Cube", "Cube")
    add_labels(cube, labels=["MyCube"], instance_name="class")

    # カスタムイベントでトリガーする Replicator ランダマイザを作成
    with rep.trigger.on_custom_event(event_name="randomize_dome_light_color"):
        rep.create.light(light_type="Dome", color=rep.distribution.uniform((0, 0, 0), (1, 1, 1)))

    # ビューポートの Perspective カメラでレンダープロダクトを作成
    rp = rep.create.render_product("/OmniverseKit_Persp", (512, 512))

    # BasicWriter で RGB とセマンティックセグメンテーションを書き込む
    writer = rep.writers.get("BasicWriter")
    out_dir = os.path.join(os.getcwd(), "_out_basic_writer_rand")
    print(f"Output directory: {out_dir}")
    writer.initialize(output_dir=out_dir, rgb=True, semantic_segmentation=True, colorize_semantic_segmentation=True)
    writer.attach(rp)

    # データキャプチャをリクエスト
    for i in range(3):
        print(f"Step {i}")
        # 1 ステップおきにカスタムイベントのランダマイザをトリガー
        if i % 2 == 1:
            rep.utils.send_og_event(event_name="randomize_dome_light_color")

        # カスタム USD API の位置ランダマイザを実行
        randomize_location(cube)

        # Replicator ランダマイザはカスタムイベントでトリガーされる設定なので、
        # step はライターのトリガーのみを行う
        await rep.orchestrator.step_async(rt_subframes=32)

    # ライターからデタッチしてからレンダープロダクトを破棄
    writer.detach()
    rp.destroy()

    # データの書き込み完了を待つ
    await rep.orchestrator.wait_until_complete_async()


# 実行
asyncio.ensure_future(run_example_async())
```

キューブの位置は毎キャプチャ、ドームライトの色は 1 回おきにランダム化されます：

![例 3 の出力](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_replicator_tut_external_getting_started_03.jpg)

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
from isaacsim.core.utils.semantics import add_labels
from pxr import Sdf, UsdGeom, UsdPhysics


def add_colliders_and_rigid_body_dynamics(prim):
    # コライダーを追加
    if not prim.HasAPI(UsdPhysics.CollisionAPI):
        collision_api = UsdPhysics.CollisionAPI.Apply(prim)
    else:
        collision_api = UsdPhysics.CollisionAPI(prim)
    collision_api.CreateCollisionEnabledAttr(True)
    # リジッドボディダイナミクスを追加
    if not prim.HasAPI(UsdPhysics.RigidBodyAPI):
        rigid_body_api = UsdPhysics.RigidBodyAPI.Apply(prim)
    else:
        rigid_body_api = UsdPhysics.RigidBodyAPI(prim)
    rigid_body_api.CreateRigidBodyEnabledAttr(True)


async def run_example_async():
    # 新しいステージを作成し、capture on play を無効化
    omni.usd.get_context().new_stage()
    rep.orchestrator.set_capture_on_play(False)

    # DLSS を Quality モード（2）に設定
    carb.settings.get_settings().set("rtx/post/dlss/execMode", 2)

    # ライトを追加
    stage = omni.usd.get_context().get_stage()
    dome_light = stage.DefinePrim("/World/DomeLight", "DomeLight")
    dome_light.CreateAttribute("inputs:intensity", Sdf.ValueTypeNames.Float).Set(500.0)

    # コライダーとリジッドボディ付きのキューブを高さ 2 に作成
    cube = stage.DefinePrim("/World/Cube", "Cube")
    add_colliders_and_rigid_body_dynamics(cube)
    if not cube.GetAttribute("xformOp:translate"):
        UsdGeom.Xformable(cube).AddTranslateOp()
    cube.GetAttribute("xformOp:translate").Set((0, 0, 2))
    add_labels(cube, labels=["MyCube"], instance_name="class")

    # 隣に球も作成
    sphere = stage.DefinePrim("/World/Sphere", "Sphere")
    add_colliders_and_rigid_body_dynamics(sphere)
    if not sphere.GetAttribute("xformOp:translate"):
        UsdGeom.Xformable(sphere).AddTranslateOp()
    sphere.GetAttribute("xformOp:translate").Set((-1, -1, 2))
    add_labels(sphere, labels=["MySphere"], instance_name="class")

    # レンダープロダクトとライターのセットアップ
    rp = rep.create.render_product("/OmniverseKit_Persp", (512, 512))
    writer = rep.writers.get("BasicWriter")
    out_dir = os.path.join(os.getcwd(), "_out_basic_writer_sim")
    print(f"Output directory: {out_dir}")
    writer.initialize(output_dir=out_dir, rgb=True, semantic_segmentation=True, colorize_semantic_segmentation=True)
    writer.attach(rp)

    # タイムラインを開始（アプリの更新に合わせて進む）
    timeline = omni.timeline.get_timeline_interface()
    timeline.play()

    # アプリを更新してシミュレーションを進める
    drop_delta = 0.5
    last_capture_height = cube.GetAttribute("xformOp:translate").Get()[2]
    for i in range(100):
        # キューブの現在の高さと、前回キャプチャからの落下量を取得
        await omni.kit.app.get_app().next_update_async()
        current_height = cube.GetAttribute("xformOp:translate").Get()[2]
        drop_since_last_capture = last_capture_height - current_height
        print(f"Step {i}; cube height: {current_height:.3f}; drop since last capture: {drop_since_last_capture:.3f}")

        # キューブが地面より下に落ちたらシミュレーションを停止
        if current_height < 0:
            print(f"\t Cube fell below the ground at height {current_height:.3f}, stopping simulation..")
            timeline.pause()
            break

        # しきい値の距離だけ落下するたびにキャプチャ
        if drop_since_last_capture >= drop_delta:
            print(f"\t Capturing at height {current_height:.3f}")
            last_capture_height = current_height
            # 同じシミュレーション状態を複数フレームでキャプチャするため、タイムラインを一時停止
            timeline.pause()

            # delta_time=0.0 にすると、step 関数はキャプチャ中にシミュレーションを進めない
            await rep.orchestrator.step_async(delta_time=0.0)

            # キューブを非表示にしてもう一度キャプチャ
            UsdGeom.Imageable(cube).MakeInvisible()
            await rep.orchestrator.step_async(delta_time=0.0)
            UsdGeom.Imageable(cube).MakeVisible()

            # タイムラインを再開してシミュレーションを続行
            timeline.play()

    # ライターからデタッチしてからレンダープロダクトを破棄
    writer.detach()
    rp.destroy()

    # データの書き込み完了を待つ
    await rep.orchestrator.wait_until_complete_async()


# 実行
asyncio.ensure_future(run_example_async())
```

出力には、キューブの落下高さの間隔ごとのキャプチャと、キューブを非表示にした 2 回目のキャプチャが含まれます。`delta_time=0.0` によってキャプチャ中はタイムラインが進まないため、**同一のシミュレーション状態を複数回キャプチャ**できます：

![例 4 の出力](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_replicator_tut_external_getting_started_04.jpg)

## トラブルシューティング

Getting Started スクリプトに関するトラブルシューティングは、公式の Replicator Troubleshooting ページの Getting Started Scripts Issues 節を参照してください。

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. Replicator ワークフローの**基本設定**（capture on play 無効化、step 関数、RTSubframes、DLSS Quality）
2. **BasicWriter** による最小構成のデータキャプチャ
3. **カスタムライター／アノテータ**によるデータアクセスと複数カメラ・複数ライターの併用
4. **カスタムイベント（Replicator グラフ）と USD API** の 2 方式のランダム化
5. 物理シミュレーションの**条件付きキャプチャ**と `delta_time=0.0` による状態の固定

### さらに学ぶには

- 高度なランダム化：公式の [Randomizer Details](https://docs.omniverse.nvidia.com/extensions/latest/ext_replicator/randomizer_details.html)
- I/O 最適化：公式の [I/O Optimization Guide](https://docs.omniverse.nvidia.com/extensions/latest/ext_replicator/io_guidelines.html)

## 次のステップ

- [合成データ生成チュートリアル一覧](index.md)に戻る。今後、シーンベース／オブジェクトベースの SDG チュートリアルを追加予定です。
