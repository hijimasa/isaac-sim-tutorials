---
title: カメラセンサー
---

# カメラセンサー

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- GUI からカメラ prim を作成し、ビューポートに映像を表示する方法
- `isaacsim.sensors.experimental.rtx` の `RtxCamera`（オーサリング）と `CameraSensor`（ランタイム）を使って画像データを取得する方法
- `tick_rate` によるカメラのレンダリング頻度の制御
- OpenCV の内部パラメータ（intrinsics）・歪み係数を Isaac Sim のカメラに設定する方法（Pinhole / Fisheye）
- キャリブレーションツールキットの外部パラメータ（extrinsics）を Isaac Sim の座標系へ変換する方法
- 複数センサーをまとめた「カメラリグ」の考え方
- Camera Inspector 拡張機能で複数ビューポートを扱う方法

## はじめに

### 前提条件

- Isaac Sim 6.0 がインストール済みで起動できること
- USD ステージやビューポートの基本操作を理解していること
- Standalone Python の例を試す場合は、Isaac Sim のインストールディレクトリで `./python.sh`（Windows は `python.bat`）が実行できること

### 所要時間

約 15〜20 分

### 概要

Isaac Sim のカメラは、USD の **Camera** prim 型としてモデル化されます。カメラ prim からの画像データは **レンダープロダクト（render product）** を介して取得され、レンダープロダクトは `omni.replicator` をはじめとする複数の拡張機能から作成できます。

!!! note "レンダープロダクトとは"
    **レンダープロダクト**は、「どのカメラ prim を、どの解像度でレンダリングするか」を定義し、その出力（RGB・深度など）を保持する単位です。画面のビューポートも 1 つのレンダープロダクトです。センサーセクションで後述するアノテーターは、このレンダープロダクトに接続して必要なデータを取り出します。

!!! note "Omniverse カメラがベース"
    Isaac Sim のカメラ機能は、Omniverse のカメラをベースにしています。したがって、Omniverse / USD のカメラに関する知識はそのまま応用できます。

!!! warning "`isaacsim.sensors.camera` は 6.0 で非推奨"
    Isaac Sim 6.0 では、従来の `isaacsim.sensors.camera` 拡張機能（`Camera` / `CameraView` / `SingleViewDepthSensor` クラス）は **非推奨（deprecated）** となり、`isaacsim.sensors.experimental.rtx` に置き換えられました。新しい拡張機能は、prim を作成・設定する **オーサリングクラス**（`RtxCamera`）と、アノテーターを取り付けてデータを読み出す **ランタイムクラス**（`CameraSensor` / `TiledCameraSensor` / `SingleViewDepthCameraSensor` / `StructuredLightCamera`）に分かれています。移行方法の詳細は公式の [Camera Sensors 移行ガイド](https://docs.isaacsim.omniverse.nvidia.com/latest/migration_guides/isaac_sim_6_0/sensors_camera_to_experimental_rtx.html) を参照してください。

このチュートリアルは、次の流れで進みます。

1. **GUI でカメラを作成**して、ビューポートに映像を表示する
2. **`RtxCamera` と `CameraSensor`** で画像データを取得する
3. **レンズ歪みモデル（OpenCV Pinhole / Fisheye）** をキャリブレーション値から設定する
4. **外部パラメータ（extrinsics）** を Isaac Sim の座標系へ変換する
5. **カメラリグ**と **Camera Inspector 拡張機能**を使う

## ステップ 1：GUI でカメラを作成する

まずは GUI だけでカメラを作成し、その視点でシーンをレンダリングしてみます。

1. **Create > Shape > Cube** で立方体を作成し、**Property** パネルから位置とスケールを調整して、映りやすい位置に置きます。
2. **Create > Camera** でカメラ prim を作成します。**Stage** ウィンドウでカメラを選択すると、ビューポートに視野（Field of View）を示すワイヤーフレームが表示されます。
3. 作成したカメラの映像をレンダリングするには、デフォルトのビューポート（これ自体が 1 つのレンダープロダクトです）を、作成したカメラ prim に切り替えます。ビューポート上部の **ビデオアイコン** をクリックし、**Cameras** メニューから作成したカメラ prim を選択してください。

![カメラ prim をビューポートに割り当てる](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_4.5_full_ext-isaacsim.sensors.camera-0.2.5_gui_3.png)

!!! tip "カメラアイコンが表示されない場合"
    デフォルトではカメラアイコンは非表示です。表示するには、ビューポート上部の目（Eye）アイコンから **Show By Type > Cameras** を有効にしてください。

## ステップ 2：RtxCamera と CameraSensor で画像データを取得する

カメラ prim からデータを収集する推奨方法は、`isaacsim.sensors.experimental.rtx` 拡張機能の 2 つのクラスを組み合わせることです。

- **`RtxCamera`（オーサリング）** … USD の Camera prim を作成（または既存 prim をラップ）し、`OmniSensorAPI` スキーマを適用します。焦点距離・アパーチャ・クリッピング範囲などの光学パラメータは `.camera` プロパティ経由で操作できます。位置・姿勢は `positions` / `translations` / `orientations` のような **複数形の配列引数**（形状 `(N, 3)` / `(N, 4)`、カメラ 1 台につき `N=1`）で指定します。
- **`CameraSensor`（ランタイム）** … `RtxCamera` オブジェクトをラップし、指定解像度の Replicator レンダープロダクトを作成して、アノテーター（`rgb`、`distance_to_camera`、`semantic_segmentation` など）を取り付けます。`get_data("アノテーター名")` でレンダリング結果を `(データ配列, 情報辞書)` のタプルとして取得します。

最小限のコードは次のとおりです。

```python
from isaacsim.sensors.experimental.rtx import CameraSensor, RtxCamera

sensor = CameraSensor(
    RtxCamera(
        "/World/Camera",
        tick_rate=30.0,               # レンダリング頻度（Hz）
        translations=[[0.0, 0.0, 1.0]],  # 複数形・配列で指定する点に注意
    ),
    resolution=(640, 480),
    annotators=["rgb"],
)

data, info = sensor.get_data("rgb")
```

作成からデータ取得までの一連のワークフローは、次の Standalone 例で確認できます。倉庫環境を読み込み、`/World/camera` に `RtxCamera` を作成して、`rgb` と `distance_to_image_plane` アノテーターを `CameraSensor` で取り付け、100 ティックごとに RGB フレームを保存します。

```bash
./python.sh standalone_examples/api/isaacsim.sensors.experimental.rtx/create_camera_basic.py
```

![create_camera_basic.py が保存する RGB フレーム（tick 100）](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_6.0_base_tut_external_create_camera_basic_rgb.png)

!!! note "旧 `Camera` クラスからの主な対応関係"
    - `Camera(frequency=..., dt=...)` → `RtxCamera(tick_rate=...)`（Hz）
    - `camera.add_rgb_to_frame()` + `camera.get_current_frame()` → `CameraSensor(annotators=["rgb"])` + `sensor.get_data("rgb")`（フレーム辞書ではなくアノテーターごとの取得に変更）
    - `position= / orientation=`（単数形） → `positions= / orientations=`（複数形・配列）
    - `annotator_device=` → `CameraSensor` が CPU / CUDA を選択（`camera_annotator_devices.py` 例を参照）
    - `name=` 引数は削除（未使用だったため）

### 2-1. tick_rate によるレンダリング頻度の制御

`RtxCamera` の `tick_rate` パラメータ（Hz）は、カメラがレンダリングする頻度を制御します。デフォルトの `0` は **autotrigger モード**で、シミュレーションフレームごとにレンダリングします。0 以外の値を設定すると、シミュレーションのステップレートとは独立に指定周波数でレンダリングされます。この値は prim の `omni:sensor:tickRate` 属性に対応し、`OmniSensorAPI` スキーマが必要です（`RtxCamera` が自動で適用します）。

```python
from isaacsim.sensors.experimental.rtx import RtxCamera

# シミュレーションのフレームレートとは独立に 30 Hz でレンダリングする
camera = RtxCamera(path="/World/Camera", tick_rate=30.0)
```

!!! note "frameSkipCount の置き換え"
    `tick_rate` は、ROS2 Camera Helper / ROS2 Camera Info Helper / UCX Camera Helper ノードで非推奨となった `frameSkipCount` 入力の推奨代替手段です。詳細は公式の Multi-Tick Rendering ページを参照してください。

### 2-2. 複数カメラをまとめて扱う（TiledCameraSensor）

**`TiledCameraSensor`** は、多数のカメラを 1 つのタイル状レンダープロダクトにまとめてレンダリングします。カメラごとにレンダープロダクトを作るより大幅に効率が良く、強化学習やマルチ環境ワークフローに向いています。カメラ prim パスの明示的なリスト（または `isaacsim.core.experimental.objects.Camera` インスタンス）とタイルごとの解像度を渡します。

```python
from isaacsim.sensors.experimental.rtx import RtxCamera, TiledCameraSensor

RtxCamera("/World/env_0/Camera", positions=[[0.0, 0.0, 5.0]])
RtxCamera("/World/env_1/Camera", positions=[[2.0, 0.0, 5.0]])

tiled = TiledCameraSensor(
    paths=["/World/env_0/Camera", "/World/env_1/Camera"],
    resolution=(256, 256),
    annotators=["rgb"],
)
data, info = tiled.get_data("rgb", tiled=True)
```

エンドツーエンドの例は `./python.sh standalone_examples/api/isaacsim.sensors.experimental.rtx/camera_tiled.py` で実行できます。

!!! note "特化型カメラ"
    `RtxCamera` / `CameraSensor` をベースに、ステレオ深度シミュレーション用の **`SingleViewDepthCameraSensor`**（[深度センサー](02_depth_sensors.md) で扱います）と、パターン投影による深度復元用の **`StructuredLightCamera`**（6.0 の新機能。例：`camera_structured_light.py`）が用意されています。

## ステップ 3：レンズ歪みモデルを設定する

Omniverse のカメラは、さまざまなレンズ歪みモデルに対応しています。`RtxCamera` クラスは、`schemas` パラメータでレンズ歪みスキーマ（`OmniLensDistortionOpenCvFisheyeAPI`、`OmniLensDistortionOpenCvPinholeAPI` など）を適用し、`attributes` パラメータで歪み係数を設定できます。

OpenCV などのキャリブレーションツールキットは、通常キャリブレーション結果を **内部行列（intrinsic matrix）** と **歪み係数（distortion coefficients）** の形で提供します。Omniverse は **OpenCV pinhole** と **OpenCV fisheye** の歪みモデルをレンダラーがネイティブにサポートしています。

以下の 2 つの Standalone 例が、`RtxCamera` と OpenCV 歪みモデルの使い方を示しています。

- `standalone_examples/api/isaacsim.sensors.experimental.rtx/camera_opencv_pinhole.py`
- `standalone_examples/api/isaacsim.sensors.experimental.rtx/camera_opencv_fisheye.py`

!!! warning "非推奨になった API に注意"
    - 以前の `Camera` クラスには、`fisheyePolynomial` 歪みモデルの係数を設定して OpenCV pinhole / fisheye を近似する API がありました。OpenCV 歪みモデルがネイティブサポートされた現在、これらの API は **非推奨** です。
    - Omniverse RTX の **Camera Projection Attributes** は Isaac Sim 5.0 以降 **非推奨** となり、`OmniLensDistortion` スキーマに置き換えられました。Camera prim を選択したときの **Fisheye Lens** パネルには旧属性がまだ表示されますが、`OmniLensDistortion` スキーマを設定している場合は無視されます。

!!! warning "Isaac Sim 6.0 の既知の問題：OmniLensDistortionLutAPI"
    Isaac Sim 6.0 では、`OmniLensDistortionLutAPI` スキーマを Camera prim に適用して一般化投影モデルによる任意の歪みモデルを有効化する機能が正しく動作せず、設定した場合レンダラーはデフォルトのピンホールモデルにフォールバックします。任意の歪みモデルを指定するには、当面は上記の非推奨の Camera Projection Attributes を使用してください（将来のリリースで修正予定です）。

!!! warning "Camera prim の単位に注意"
    他の USD prim 型と異なり、Camera prim の一部の属性（焦点距離、アパーチャなど）は**ステージ単位の 1/10** で定義されます。異なるステージ単位で定義された Camera をステージに追加すると、これらの属性が誤ってスケーリングされます。`omni.usd.metrics.assembler.usdgeom` 拡張機能を有効にすると、Camera prim 追加時に属性が正しい単位へ自動調整されます（Isaac Sim フルアプリではデフォルトで有効です）。

### OpenCV Fisheye

`OmniLensDistortionOpenCvFisheyeAPI` スキーマを適用した `RtxCamera` を作成する Standalone 例を実行します。

```bash
./python.sh standalone_examples/api/isaacsim.sensors.experimental.rtx/camera_opencv_fisheye.py
```

歪みスキーマの適用は、`RtxCamera` のコンストラクタでスキーマ名と属性値を渡す形になります。

```python
from isaacsim.sensors.experimental.rtx import RtxCamera

camera = RtxCamera(
    "/World/camera",
    schemas=["OmniLensDistortionOpenCvFisheyeAPI"],
    attributes={...},  # 内部行列・歪み係数に対応する属性値
)
```

例を実行し、ビューポートを新しく作成したカメラに切り替えると、次のような画像が表示されるはずです。

![OpenCV Fisheye の出力例](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_5.0_full_ext-isaacsim.sensors.camera-1.1.0_viewport_camera-opencv-fisheye-test.png)

### OpenCV Pinhole

手順は Fisheye とほぼ同じで、適用するスキーマが `OmniLensDistortionOpenCvPinholeAPI` になる点だけが異なります。

```bash
./python.sh standalone_examples/api/isaacsim.sensors.experimental.rtx/camera_opencv_pinhole.py
```

![OpenCV Pinhole の出力例](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_5.0_full_ext-isaacsim.sensors.camera-1.1.0_viewport_camera-opencv-pinhole-test.png)

## ステップ 4：外部パラメータ（Extrinsic Calibration）を設定する

外部パラメータは、キャリブレーションツールキットから通常 **変換行列** の形で提供されます。軸の取り方と回転順序の規約はツールキットごとに異なるため、Isaac Sim の座標系へ変換する必要があります。

個々のカメラセンサーに外部パラメータを設定するには、次の例（疑似コード）を参考に変換行列を Isaac Sim の単位系へ変換します。軸の入れ替えとクォータニオンの並べ替えは、使用するツールキットに合わせて調整してください。

```python
# 疑似コード — 軸の入れ替え・クォータニオンの順序はツールキットに合わせて調整する
import numpy as np
from isaacsim.sensors.experimental.rtx import RtxCamera

dX, dY, dZ = _, _, _        # キャリブレーションツールキットからの並進ベクトル
rW, rX, rY, rZ = _, _, _, _  # 回転パラメータの順序に注意（ツールキット依存）

RtxCamera(
    "/rig/camera_color",
    positions=np.array([-dZ, dX, dY]),        # prim のローカル座標系での並進に注意
    orientations=np.array([rW, -rZ, rX, rY]),  # クォータニオン（wxyz）
)
```

別の方法として、カメラセンサーを prim に取り付けることもできます。その場合、カメラセンサーは取り付け先 prim の位置・姿勢を継承します。

```python
from isaacsim.sensors.experimental.rtx import RtxCamera

# OmniSensorAPI スキーマ付きのカメラ prim を作成する
cam = RtxCamera(
    "/World/camera",
    # translations = ...
    # orientations = ...
)
```

## ステップ 5：カメラリグと Camera Inspector

### カメラセンサーリグの作成

**カメラセンサーリグ** とは、1 つの prim に複数のカメラセンサーを取り付けたものです。手動で作成した、あるいはキャリブレーション値から導出した個々のセンサーを組み合わせて構築します。

公式ドキュメントでは、RealSense™ Depth Camera D455 のデジタルツインを例に説明しています。この USD は Content フォルダの `/Isaac/Sensors/RealSense/D455/rsd455.usd` にあります。RealSense には 3 つの視覚センサーと 1 つの IMU センサーがあり、カメラ原点に対する配置は Intel の TechSpec のレイアウト図から取得されています。

!!! note "実機からリグを作るときのポイント"
    - `fStop` は TechSpec の F Number の分母、`focalLength` は Focal Length、`fthetaMaxFov` は対角視野（Diagonal FOV）に対応します。
    - `focusDistance` のような一部のパラメータは、実際の出力と比較しながら推定する必要があります。
    - `horizontalAperture` / `verticalAperture` はセンサーのイメージエリア（例：OV9782 は 3896 × 2453 µm）から導出できます。
    - Pseudo Depth カメラは、ファームウェアがステレオから生成する深度画像の代替です。ステレオアルゴリズムを再現するわけではなく、左右カメラの中間位置から見たシーン深度を返す便宜的なカメラです。

### ISP カメラパイプラインの出力

`omni.sensors.nv.camera` 拡張機能は、カメラセンサーと ISP（Image Signal Processor）パイプラインをシミュレートします。Isaac Sim には、`OmniSensorGenericCameraCoreAPI` USD スキーマで ISP パイプラインを設定し、各パイプラインステージの出力を画像として保存する Standalone 例が含まれています。自作の ISP を RTX のレンダリング画像でテストしたい場合や、Omniverse のシミュレート ISP と比較したい場合に便利です。

```bash
./python.sh standalone_examples/api/isaacsim.sensors.experimental.rtx/camera_isp_pipeline.py
```

この例は 20 フレームをレンダリングし、各 ISP ステージの出力を `camera_isp_pipeline_outputs` ディレクトリに保存します。ステージは順に、**HDR テクスチャ読み出し → 色補正 → CFA エンコード（Bayer 化）→ ノイズシミュレーション → カンパンディング → ISP 出力 → YUV 変換** です。

!!! warning "サンプル ISP プログラムは Linux x86_64 のみ"
    `omni.sensors.nv.camera` に同梱されているサンプル ISP プログラムは Linux x86_64 でのみ利用できます。他のプラットフォームで例を実行するとメッセージを表示して早期終了します。自前の ISP プログラムがある場合は、スクリプト内の `_isp_program_path` 変数を書き換え、プラットフォームチェックをコメントアウトしてください。

### Camera Inspector 拡張機能

**Camera Inspector 拡張機能** では、次のことができます。

- カメラごとに複数のビューポートを作成する
- カメラのカバレッジを確認する
- 任意のフレームでカメラの姿勢を取得・設定する

**起動方法**

1. メニューバーから **Tools > Sensors > Camera Inspector** を選択します。
2. 起動後、ドロップダウンにカメラが表示されることを確認します。
3. 新しいカメラを追加したときは、**Refresh** ボタンをクリックして拡張機能に認識させます。
4. 検査したいカメラを選択します。

**Camera State テキストボックス**

![Camera State テキストボックス](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_4.5_base_ref_gui_camera_status_textbox.png)

拡張機能上部の Camera State テキストボックスには、カメラの位置と姿勢が表示されます。右側のコピーアイコンをクリックすると、そのままコードに貼り付けられる形式でクリップボードにコピーできます。

**ビューポートの作成**

カメラを選択した状態で **Create Viewport** ボタンをクリックすると、選択中のカメラを割り当てた新しいビューポートが作成されます。2 つのドロップダウンとボタンを使えば、複数のビューポートに異なるカメラを割り当てられます。ビューポート左上のメニューの **Viewport** から解像度も変更できます。

!!! warning "解像度のアスペクト比"
    解像度を変更する際、Omniverse Kit は正方形ピクセルのみをサポートします。つまり、解像度のアスペクト比はアパーチャ比と一致している必要があります。

## まとめ

このチュートリアルでは、次の内容を学びました。

- Isaac Sim のカメラは USD の **Camera** prim であり、データは **レンダープロダクト** を介して取得すること
- GUI でカメラを作成してビューポートに割り当てる方法
- `RtxCamera`（オーサリング）＋ `CameraSensor`（ランタイム）で画像データを取得し、`tick_rate` でレンダリング頻度を制御する方法
- OpenCV Pinhole / Fisheye の歪みスキーマと外部パラメータを Isaac Sim に設定する方法
- カメラリグ・ISP パイプライン・Camera Inspector 拡張機能の役割

!!! tip "その他の Standalone サンプル"
    `standalone_examples/api/isaacsim.sensors.experimental.rtx/` には、このほかにも `camera_annotator_devices.py`（CPU / CUDA バッファの選択）、`camera_structured_light.py`（構造化光カメラ）、`camera_ros.py`（ROS 2 へのフレーム配信）などの例があります。

## 次のステップ

- ステレオから深度を得る仕組みは [深度センサー](02_depth_sensors.md) で扱います。
- RTX ベースの高性能センサー（LiDAR / Radar）については [RTX センサー](03_rtx_sensors.md) を参照してください。
