---
title: カメラセンサー
---

# カメラセンサー

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- GUI からカメラ prim を作成し、ビューポートに映像を表示する方法
- `isaacsim.sensors.camera` の `Camera` クラスを使って Standalone Python から画像データを取得する方法
- OpenCV の内部パラメータ（intrinsics）・歪み係数を Isaac Sim のカメラに設定する方法（Pinhole / Fisheye）
- キャリブレーションツールキットの外部パラメータ（extrinsics）を Isaac Sim の座標系へ変換する方法
- 複数センサーをまとめた「カメラリグ」の考え方
- Camera Inspector 拡張機能で複数ビューポートを扱う方法

## はじめに

### 前提条件

- Isaac Sim 5.1 がインストール済みで起動できること
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

このチュートリアルは、次の流れで進みます。

1. **GUI でカメラを作成**して、ビューポートに映像を表示する
2. **Standalone Python の `Camera` クラス**で画像データを取得する
3. **レンズ歪みモデル（OpenCV Pinhole / Fisheye）** をキャリブレーション値から設定する
4. **外部パラメータ（extrinsics）** を Isaac Sim の座標系へ変換する
5. **カメラリグ**と **Camera Inspector 拡張機能**を使う

## ステップ 1：GUI でカメラを作成する

まずは GUI だけでカメラを作成し、その視点でシーンをレンダリングしてみます。

1. **Create > Shape > Cube** で立方体を作成し、**Property** パネルから位置とスケールを調整して、映りやすい位置に置きます。
2. **Create > Camera** でカメラ prim を作成します。**Stage** ウィンドウでカメラを選択すると、ビューポートに視野（Field of View）を示すワイヤーフレームが表示されます。
3. 作成したカメラの映像をレンダリングするには、デフォルトのビューポート（これ自体が 1 つのレンダープロダクトです）を、作成したカメラ prim に切り替えます。ビューポート上部の **ビデオアイコン** をクリックし、**Cameras** メニューから作成したカメラ prim を選択してください。

![カメラ prim をビューポートに割り当てる](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_full_ext-isaacsim.sensors.camera-0.2.5_gui_4.png)

!!! tip "カメラアイコンが表示されない場合"
    デフォルトではカメラアイコンは非表示です。表示するには、ビューポート上部の目（Eye）アイコンから **Show By Type > Cameras** を有効にしてください。

## ステップ 2：Standalone Python で画像データを取得する

カメラ prim に取り付けたレンダープロダクトからデータを取得する方法は複数あります。その 1 つが、`isaacsim.sensors.camera` 拡張機能の **`Camera`** クラスです。

`Camera` クラスを使った例は、次のコマンドで実行できます。

```bash
./python.sh standalone_examples/api/isaacsim.sensors.camera/camera.py
```

この例のコードを以下に示します（参考用）。ポイントは、`Camera` を生成したあと `my_world.reset()` に続けて `camera.initialize()` を呼び出し、シミュレーションループの中で `camera.get_rgba()` や `camera.get_current_frame()` からデータを取り出している点です。

```python
from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": False})

from isaacsim.core.api.objects import DynamicCuboid
from isaacsim.sensors.camera import Camera
from isaacsim.core.api import World
import isaacsim.core.utils.numpy.rotations as rot_utils
import numpy as np
import matplotlib.pyplot as plt


my_world = World(stage_units_in_meters=1.0)

cube_2 = my_world.scene.add(
    DynamicCuboid(
        prim_path="/new_cube_2",
        name="cube_1",
        position=np.array([5.0, 3, 1.0]),
        scale=np.array([0.6, 0.5, 0.2]),
        size=1.0,
        color=np.array([255, 0, 0]),
    )
)

cube_3 = my_world.scene.add(
    DynamicCuboid(
        prim_path="/new_cube_3",
        name="cube_2",
        position=np.array([-5, 1, 3.0]),
        scale=np.array([0.1, 0.1, 0.1]),
        size=1.0,
        color=np.array([0, 0, 255]),
        linear_velocity=np.array([0, 0, 0.4]),
    )
)

camera = Camera(
    prim_path="/World/camera",
    position=np.array([0.0, 0.0, 25.0]),
    frequency=20,
    resolution=(256, 256),
    orientation=rot_utils.euler_angles_to_quats(np.array([0, 90, 0]), degrees=True),
)

my_world.scene.add_default_ground_plane()
my_world.reset()
camera.initialize()

i = 0
camera.add_motion_vectors_to_frame()

while simulation_app.is_running():
    my_world.step(render=True)
    print(camera.get_current_frame())
    if i == 100:
        points_2d = camera.get_image_coords_from_world_points(
            np.array([cube_3.get_world_pose()[0], cube_2.get_world_pose()[0]])
        )
        points_3d = camera.get_world_points_from_image_coords(points_2d, np.array([24.94, 24.9]))
        print(points_2d)
        print(points_3d)
        imgplot = plt.imshow(camera.get_rgba()[:, :, :3])
        plt.show()
        print(camera.get_current_frame()["motion_vectors"])
    if my_world.is_playing():
        if my_world.current_time_step_index == 0:
            my_world.reset()
    i += 1


simulation_app.close()
```

!!! note "`Camera` クラスの主な API"
    - `get_rgba()` … RGBA 画像を `numpy` 配列で取得します。
    - `get_current_frame()` … RGB やモーションベクターなど、フレームに追加したデータをまとめて取得します。
    - `get_image_coords_from_world_points()` … ワールド座標の点を画像上のピクセル座標へ投影します。
    - `get_world_points_from_image_coords()` … 画像座標＋深度からワールド座標を復元します。
    - `add_motion_vectors_to_frame()` … フレームにモーションベクターを追加します。

## ステップ 3：レンズ歪みモデルを設定する

Omniverse のカメラは、さまざまなレンズ歪みモデルに対応しています。`isaacsim.sensors.camera.Camera` クラスには、各歪みモデルのパラメータを設定する API が用意されています。

OpenCV などのキャリブレーションツールキットは、通常キャリブレーション結果を **内部行列（intrinsic matrix）** と **歪み係数（distortion coefficients）** の形で提供します。Omniverse は **OpenCV pinhole** と **OpenCV fisheye** の歪みモデルをレンダラーがネイティブにサポートしています。

以下の 2 つの Standalone 例が、`Camera` クラスと OpenCV 歪みモデルの使い方を示しています。

- `standalone_examples/api/isaacsim.sensors.camera/camera_opencv_pinhole.py`
- `standalone_examples/api/isaacsim.sensors.camera/camera_opencv_fisheye.py`

これらの一部は **Window > Script Editor** から開ける Script Editor でも実行できます。

!!! warning "非推奨になった API に注意"
    - 以前の `Camera` クラスには、`fisheyePolynomial` 歪みモデルの係数を設定して OpenCV pinhole / fisheye を近似する API がありました。OpenCV 歪みモデルがネイティブサポートされた現在、これらの API は **非推奨** です。
    - Omniverse RTX の **Camera Projection Attributes** は Isaac Sim 5.0 以降 **非推奨** となり、`OmniLensDistortion` スキーマに置き換えられました。Camera prim を選択したときの **Fisheye Lens** パネルには旧属性がまだ表示されますが、`OmniLensDistortion` スキーマを設定している場合は無視されます。

### OpenCV Fisheye

内部行列と歪み係数から焦点距離・アパーチャを計算し、`set_opencv_fisheye_properties()` で歪み係数を設定します。被写界深度（DOF）を無効にしたい場合は `f_stop` を `0.0` に設定します。

```python
import isaacsim.core.utils.numpy.rotations as rot_utils
import numpy as np
from isaacsim.core.api import World
from isaacsim.core.api.objects import DynamicCuboid
from isaacsim.core.utils.stage import add_reference_to_stage
from isaacsim.sensors.camera import Camera
from isaacsim.storage.native import get_assets_root_path
from PIL import Image, ImageDraw

# 目標とする画像解像度、カメラ内部行列、歪み係数
width, height = 1920, 1200
camera_matrix = [[455.8, 0.0, 943.8], [0.0, 454.7, 602.3], [0.0, 0.0, 1.0]]
distortion_coefficients = [0.05, 0.01, -0.003, -0.0005]

# カメラのセンサーサイズと光学系パラメータ。これらは OpenCV カメラモデルの一部では
# ないが、被写界深度（DOF）効果をシミュレートするために必要。
#
# 注意: DOF 効果を無効にするには f_stop を 0.0 にする。デバッグ時に便利。
pixel_size = 3          # ピクセルサイズ（マイクロメートル）
f_stop = 1.8            # F値（焦点距離 / 入射瞳径、無次元）
focus_distance = 1.5    # フォーカス距離（メートル）。カメラから立方体までの距離に合わせた

# 地面を追加
usd_path = get_assets_root_path() + "/Isaac/Environments/Grid/default_environment.usd"
add_reference_to_stage(usd_path=usd_path, prim_path="/ground_plane")

# 立方体とカメラを追加
cube_1 = DynamicCuboid(prim_path="/new_cube_1", name="cube_1", position=np.array([0, 0, 0.5]),
                       scale=np.array([1.0, 1.0, 1.0]), size=1.0, color=np.array([255, 0, 0]))
cube_2 = DynamicCuboid(prim_path="/new_cube_2", name="cube_2", position=np.array([2, 0, 0.5]),
                       scale=np.array([1.0, 1.0, 1.0]), size=1.0, color=np.array([0, 255, 0]))
cube_3 = DynamicCuboid(prim_path="/new_cube_3", name="cube_3", position=np.array([0, 4, 1]),
                       scale=np.array([2.0, 2.0, 2.0]), size=1.0, color=np.array([0, 0, 255]))

camera = Camera(
    prim_path="/World/camera",
    position=np.array([0.0, 0.0, 2.0]),  # 立方体の側面から 1 メートル離した位置
    frequency=30,
    resolution=(width, height),
    orientation=rot_utils.euler_angles_to_quats(np.array([0, 90, 0]), degrees=True),
)
camera.initialize()

# カメラ内部行列から焦点距離とアパーチャサイズを計算
((fx, _, cx), (_, fy, cy), (_, _, _)) = camera_matrix  # fx, fy, cx, cy はピクセル単位
horizontal_aperture = pixel_size * width * 1e-6   # メートルに変換
vertical_aperture = pixel_size * height * 1e-6    # メートルに変換
focal_length_x = pixel_size * fx * 1e-6
focal_length_y = pixel_size * fy * 1e-6
focal_length = (focal_length_x + focal_length_y) / 2

# カメラパラメータを設定（Isaac Sim センサーと Kit の単位変換に注意）
camera.set_focal_length(focal_length)
camera.set_focus_distance(focus_distance)
camera.set_lens_aperture(f_stop)
camera.set_horizontal_aperture(horizontal_aperture)
camera.set_vertical_aperture(vertical_aperture)
camera.set_clipping_range(0.05, 1.0e5)

# 歪み係数を設定
camera.set_opencv_fisheye_properties(cx=cx, cy=cy, fx=fx, fy=fy, fisheye=distortion_coefficients)
```

上記のスニペットを実行し、ビューポートを新しく作成したカメラに切り替えると、次のような画像が表示されるはずです。

![OpenCV Fisheye の出力例](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_ext-isaacsim.sensors.camera-1.1.0_viewport_camera-opencv-fisheye-test.png)

### OpenCV Pinhole

手順は Fisheye とほぼ同じで、最後に `set_opencv_pinhole_properties()` を呼び出す点だけが異なります。

```python
import isaacsim.core.utils.numpy.rotations as rot_utils
import numpy as np
from isaacsim.core.api import World
from isaacsim.core.api.objects import DynamicCuboid
from isaacsim.core.utils.stage import add_reference_to_stage
from isaacsim.sensors.camera import Camera
from isaacsim.storage.native import get_assets_root_path
from PIL import Image, ImageDraw

# 目標とする画像解像度、カメラ内部行列、歪み係数
width, height = 1920, 1200
camera_matrix = [[958.8, 0.0, 957.8], [0.0, 956.7, 589.5], [0.0, 0.0, 1.0]]
distortion_coefficients = [0.14, -0.03, -0.0002, -0.00003, 0.009, 0.5, -0.07, 0.017]

pixel_size = 3
f_stop = 1.8
focus_distance = 1.5

usd_path = get_assets_root_path() + "/Isaac/Environments/Grid/default_environment.usd"
add_reference_to_stage(usd_path=usd_path, prim_path="/ground_plane")

cube_1 = DynamicCuboid(prim_path="/new_cube_1", name="cube_1", position=np.array([0, 0, 0.5]),
                       scale=np.array([1.0, 1.0, 1.0]), size=1.0, color=np.array([255, 0, 0]))
cube_2 = DynamicCuboid(prim_path="/new_cube_2", name="cube_2", position=np.array([2, 0, 0.5]),
                       scale=np.array([1.0, 1.0, 1.0]), size=1.0, color=np.array([0, 255, 0]))
cube_3 = DynamicCuboid(prim_path="/new_cube_3", name="cube_3", position=np.array([0, 4, 1]),
                       scale=np.array([2.0, 2.0, 2.0]), size=1.0, color=np.array([0, 0, 255]))

camera = Camera(
    prim_path="/World/camera",
    position=np.array([0.0, 0.0, 2.0]),
    frequency=30,
    resolution=(width, height),
    orientation=rot_utils.euler_angles_to_quats(np.array([0, 90, 0]), degrees=True),
)
camera.initialize()

((fx, _, cx), (_, fy, cy), (_, _, _)) = camera_matrix
horizontal_aperture = pixel_size * width * 1e-6
vertical_aperture = pixel_size * height * 1e-6
focal_length_x = pixel_size * fx * 1e-6
focal_length_y = pixel_size * fy * 1e-6
focal_length = (focal_length_x + focal_length_y) / 2

camera.set_focal_length(focal_length)
camera.set_focus_distance(focus_distance)
camera.set_lens_aperture(f_stop)
camera.set_horizontal_aperture(horizontal_aperture)
camera.set_vertical_aperture(vertical_aperture)
camera.set_clipping_range(0.05, 1.0e5)

# 歪み係数を設定
camera.set_opencv_pinhole_properties(cx=cx, cy=cy, fx=fx, fy=fy, pinhole=distortion_coefficients)
```

![OpenCV Pinhole の出力例](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_ext-isaacsim.sensors.camera-1.1.0_viewport_camera-opencv-pinhole-test.png)

## ステップ 4：外部パラメータ（Extrinsic Calibration）を設定する

外部パラメータは、キャリブレーションツールキットから通常 **変換行列** の形で提供されます。軸の取り方と回転順序の規約はツールキットごとに異なるため、Isaac Sim の座標系へ変換する必要があります。

個々のカメラセンサーに外部パラメータを設定するには、次の例を参考に変換行列を Isaac Sim の単位系へ変換します。

```python
import numpy as np
import isaacsim.core.utils.numpy.rotations as rot_utils   # クォータニオン操作の便利関数

dX, dY, dZ = ...      # キャリブレーションツールキットからの並進ベクトル
rW, rX, rY, rZ = ...  # 回転パラメータの順序に注意（ツールキット依存）

Camera(
    prim_path="/rig/camera_color",
    position=np.array([-dZ, dX, dY]),       # prim のローカル座標系での並進に注意
    orientation=np.array([rW, -rZ, rX, rY]), # ワールド/ローカル座標系でのクォータニオン
)
```

別の方法として、カメラセンサーを prim に取り付けることもできます。その場合、カメラセンサーは取り付け先 prim の位置・姿勢を継承します。

```python
import isaacsim.core.utils.prims as prim_utils

camera_prim = prim_utils.create_prim(
    name,
    "Xform",
    translation=...,
    orientation=...,
)

camera = Camera(
    prim_path=f"{name}/camera",
    ...
)
```

## ステップ 5：カメラリグと Camera Inspector

### カメラセンサーリグの作成

**カメラセンサーリグ** とは、1 つの prim に複数のカメラセンサーを取り付けたものです。手動で作成した、あるいはキャリブレーション値から導出した個々のセンサーを組み合わせて構築します。

公式ドキュメントでは、Intel® RealSense™ Depth Camera D455 のデジタルツインを例に説明しています。この USD は Content フォルダの `/Isaac/Sensors/Intel/RealSense/rsd455.usd` にあります。RealSense には 3 つの視覚センサーと 1 つの IMU センサーがあり、カメラ原点に対する配置は Intel の TechSpec のレイアウト図から取得されています。

!!! note "実機からリグを作るときのポイント"
    - `fStop` は TechSpec の F Number の分母、`focalLength` は Focal Length、`fthetaMaxFov` は対角視野（Diagonal FOV）に対応します。
    - `focusDistance` のような一部のパラメータは、実際の出力と比較しながら推定する必要があります。
    - `horizontalAperture` / `verticalAperture` はセンサーのイメージエリア（例：OV9782 は 3896 × 2453 µm）から導出できます。
    - Pseudo Depth カメラは、ファームウェアがステレオから生成する深度画像の代替です。ステレオアルゴリズムを再現するわけではなく、左右カメラの中間位置から見たシーン深度を返す便宜的なカメラです。

### Pre-ISP カメラパイプラインの出力

`omni.sensors.nv.camera` 拡張機能は、カメラセンサーと ISP（Image Signal Processor）パイプラインをシミュレートします。Isaac Sim 5.1 には、色補正・CFA エンコード・カンパンディングなど、**ISP 前**の各ステップの出力をレンダリングして保存する Standalone 例が含まれています。自作の ISP を Omniverse のレンダリング画像でテストしたい場合や、Omniverse のシミュレート ISP と比較したい場合に便利です。

```bash
./python.sh standalone_examples/api/isaacsim.sensors.camera/camera_pre_isp_pipeline.py --draw-output
```

この例は、既定で `pre_isp_camera_pipeline_outputs` ディレクトリに 3 つの ISP 前ステップ（HDR バッファ、生センサー出力、ISP 出力）の画像を保存します。

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

![Camera State テキストボックス](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_base_ref_gui_camera_status_textbox.png)

拡張機能上部の Camera State テキストボックスには、カメラの位置と姿勢が表示されます。右側のコピーアイコンをクリックすると、そのままコードに貼り付けられる形式でクリップボードにコピーできます。

**ビューポートの作成**

カメラを選択した状態で **Create Viewport** ボタンをクリックすると、選択中のカメラを割り当てた新しいビューポートが作成されます。2 つのドロップダウンとボタンを使えば、複数のビューポートに異なるカメラを割り当てられます。ビューポート左上のメニューの **Viewport** から解像度も変更できます。

!!! warning "解像度のアスペクト比"
    解像度を変更する際、Omniverse Kit は正方形ピクセルのみをサポートします。つまり、解像度のアスペクト比はアパーチャ比と一致している必要があります。

## まとめ

このチュートリアルでは、次の内容を学びました。

- Isaac Sim のカメラは USD の **Camera** prim であり、データは **レンダープロダクト** を介して取得すること
- GUI でカメラを作成してビューポートに割り当てる方法
- `Camera` クラスで画像データを取得し、2D/3D 座標を相互変換する方法
- OpenCV Pinhole / Fisheye の歪みモデルと外部パラメータを Isaac Sim に設定する方法
- カメラリグと Camera Inspector 拡張機能の役割

## 次のステップ

- ステレオから深度を得る仕組みは [深度センサー](02_depth_sensors.md) で扱います。
- RTX ベースの高性能センサー（LiDAR / Radar）については [RTX センサー](03_rtx_sensors.md) を参照してください。
