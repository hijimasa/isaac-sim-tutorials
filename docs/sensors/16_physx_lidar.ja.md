---
title: PhysX SDK Lidar
---

# PhysX SDK Lidar

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- PhysX SDK Lidar がレイキャストで LiDAR を模擬する仕組みと、RTX LiDAR との違い
- GUI で回転式 LiDAR を作成し、可視化・衝突検出を設定する方法
- LiDAR を親ジオメトリやロボットに取り付ける方法
- Script Editor と Python API で LiDAR データを取得する方法
- 点群にセマンティックラベルを付けてセグメンテーションする方法

## はじめに

### 前提条件

- [PhysX SDK センサー](14_physx_sensors.md) の概要を理解していること
- コライダー（Collision）と Articulation の基礎を理解していること

### 所要時間

約 20〜25 分

### 概要

PhysX SDK Lidar センサーは、PhysX SDK のレイキャストを使って LiDAR を模擬します。水平・垂直のビーム解像度、回転レート、その他の LiDAR パラメータを設定でき、各ビームの深度情報を報告します。

!!! warning "Isaac Sim 6.0 での非推奨化"
    PhysX SDK Lidar センサー（`isaacsim.sensors.physx`）は Isaac Sim 6.0 で非推奨（deprecated）となりました。
    後継は **Physics Raycast センサー**（`isaacsim.sensors.experimental.physics.RaycastSensor`）です。
    回転式レイキャスト LiDAR の移行の対応関係は次のとおりです。

    | PhysX SDK Lidar | Physics Raycast センサー |
    |---|---|
    | `rotationRate` | `rayTimeOffsets`。レイを方位角の列ごとに分配し、各列にスイープ周期（`1.0 / rotation_rate`）内の時間オフセットを割り当てる。現在の物理ステップにオフセットが入るレイのみ発射される |
    | 水平・垂直解像度 | `rayDirections`。各ビームの方位角・仰角からデカルト方向ベクトルを計算する |
    | `minRange` / `maxRange` | `minRange` / `maxRange`。意味は同じ |
    | `drawLines` | **Isaac Read Physics Raycast Sensor** ノードの出力に **Debug Draw RayCast** OmniGraph ノードを接続する |
    | `_range_sensor` インターフェース（`get_linear_depth_data` / `get_point_cloud_data`） | `RaycastSensor.get_sensor_reading()` が深度・ヒット位置・ヒット法線・（オプションで）ヒットした prim のパスを返す |
    | `enable_semantics` / `get_prim_data` | `reportHitPrimPaths` 属性。有効にすると読み値に各ヒット面の USD prim パスが含まれる |
    | `rotationRate` を `0.0` に設定（毎ステップ全レイ発射） | `rayTimeOffsets` を省略する。時間オフセットなしでは全レイが毎物理ステップ発射される |

    詳細は[公式移行ガイド](https://docs.isaacsim.omniverse.nvidia.com/latest/migration_guides/isaac_sim_6_0/sensors_physx_lidar_to_physics_raycast.html)と
    [Physics Raycast センサーの公式ドキュメント](https://docs.isaacsim.omniverse.nvidia.com/latest/sensors/isaacsim_sensors_physics_raycast.html)を参照してください。
    時間オフセット付きで 360 度スイープを行う回転式センサー構成のサンプルは
    **Robotics Examples > Sensors > Physics Raycast Sensor** から **Load Scene** で試せます。

!!! note "RTX LiDAR との違い"
    PhysX SDK Lidar は**非可視マテリアルと相互作用しません**。常に ground truth 情報を報告します。たとえば、実際にはビームが透明なオブジェクトを透過する場合でも、PhysX SDK Lidar はその透明オブジェクトまでの深度を測定します。物理ベースの反射・透過をモデル化したい場合は [RTX LiDAR センサー](04_rtx_lidar.md) を使ってください。

## ステップ 1：サンプルを実行する

1. **Windows > Examples > Robotics Examples** で Robotics Examples タブを有効にします。
2. **Robotics Examples > Sensors > Physx Lidar Sensor** をクリックします。
3. **Load Sensor** → **Load Scene** の順にボタンを押します。
4. **Open Source Code** でソースコードを確認できます。
5. **PLAY** で開始します。

![回転式センサーの例](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_4.5_full_tut_viewport_rotating_sensor.webp)

## ステップ 2：GUI で LiDAR を作成する

### シーンのセットアップ

1. **Create > Physics > Physics Scene** で Physics Scene を作成します。右の Stage パネルに `PhysicsScene` prim ができることを確認します。
2. **Create > Sensors > PhysX Lidar > Rotating** で LiDAR を作成します。

次に、回転と可視化のプロパティを設定します。

1. Stage パネルで作成した LiDAR prim を選択します。
2. Property パネルの **Raw USD Properties** セクションまでスクロールします。
3. **drawLines** チェックボックスを有効にして線の描画を有効にします。
4. **rotationRate** を `1.0` に設定して回転を 1 Hz にします。

!!! tip "全方向へ一斉にレイを飛ばす"
    `rotationRate` を `0.0` にすると、FOV と解像度に基づいて全方向へ一斉にレイを飛ばします。Lidar のパラメータはステージ実行中にリアルタイムで更新できます。

![回転式 LiDAR の設定](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_4.5_full_tut_gui_rotating_sensor_2.webp)

### 衝突検出のセットアップ

LiDAR は **Collision が有効なオブジェクトのみ**を検出できます。検出対象を追加します。

1. **Create > Mesh > Cube** で立方体を作成し、`(2, 0, 0)` に移動します。
2. 立方体を選択し、Property パネルの **+ Add > Physics > Collider** で物理コライダーを追加します。

![衝突検出のセットアップ](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_4.5_full_tut_viewport_rotating_sensor_3.webp)

マウスで立方体を動かすと、LiDAR のレイがジオメトリと相互作用する様子を確認できます。

## ステップ 3：LiDAR をジオメトリ・ロボットに取り付ける

### 親ジオメトリに取り付ける

多くの場合、LiDAR は車やロボットなどのより複雑なアセンブリに取り付けます。ここでは Cylinder をプレースホルダーとして使います。

1. **Create > Mesh > Cylinder** でシリンダーを作成し、translation を `(0, 0, 0)` に設定します。
2. Stage パネルで LiDAR prim をシリンダーにドラッグ＆ドロップします。これでシリンダーが LiDAR の親になり、シリンダーが動くと LiDAR も一緒に動きます。LiDAR が報告する情報もすべてシリンダー基準になります。
3. LiDAR を選択して `(0.5, 0.5, 0)` に移動し、シリンダーに対する相対位置を設定します。シリンダーを動かすと、この相対変換が維持されます。
4. 確認後、LiDAR の Translate をデフォルトの `(0, 0, 0)` にリセットします。

![親ジオメトリに取り付け](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_4.5_full_tut_viewport_rotating_sensor_4.webp)

### 動くロボットに取り付ける

例として Carter V1 ロボットを使います。

1. Content Browser で `Robots/NVIDIA/Carter/carter_v1.usd` を開きます。
2. `carter/chassis_link/left_wheel` の左車輪ジョイントを開き、Target Velocity を `100` に設定します。右車輪 `carter/chassis_link/right_wheel` も同様にします。
3. Play すると Carter が自動的に前進します。
4. **Create > Sensors > PhysX LIDAR > Rotating** で LiDAR を作成します。
5. Stage パネルで LiDAR prim を `/carter/chassis_link` にドラッグします。
6. PhysX Lidar の translation を `-0.06, 0.0, 0.38` に設定して正しい位置に移動します。
7. デバッグしやすいよう draw lines を有効にし、rotation rate を 0 にします。

![ロボットに取り付け](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_4.5_full_tut_viewport_rotating_sensor_3.gif)

## ステップ 4：Python API でデータを取得する

LiDAR の Python API を使うと、スクリプトや拡張機能からセンサーを作成・制御・クエリできます。**Window > Script Editor** から Script Editor を開き、最後のスイープのデータを取得します。

### インポートとセットアップ

```python
import asyncio                                                  # レンダリングスレッドをブロックしないよう非同期実行に使用

import omni                                                     # コアの Omniverse API
from isaacsim.sensors.physx import _range_sensor                # Lidar センサーと対話する Python バインディング
from pxr import Gf, UsdGeom, UsdPhysics                         # 立方体の作成に使う pxr usd インポート
```

```python
import omni

stage = omni.usd.get_context().get_stage()                      # ジオメトリへのアクセス
timeline = omni.timeline.get_timeline_interface()               # シミュレーションとの対話
lidarInterface = _range_sensor.acquire_lidar_sensor_interface() # LIDAR との対話

# 以下は本チュートリアル前半の Python 版
omni.kit.commands.execute('AddPhysicsSceneCommand', stage=stage, path='/World/PhysicsScene')
lidarPath = "/LidarName"
result, prim = omni.kit.commands.execute(
    "RangeSensorCreateLidar",
    path=lidarPath,
    parent="/World",
    min_range=0.4,
    max_range=100.0,
    draw_points=False,
    draw_lines=True,
    horizontal_fov=360.0,
    vertical_fov=30.0,
    horizontal_resolution=0.4,
    vertical_resolution=4.0,
    rotation_rate=0.0,
    high_lod=False,
    yaw_offset=0.0,
    enable_semantics=False
)
```

### 障害物を作成する

```python
from isaacsim.core.experimental.utils.stage import get_current_stage
from pxr import Gf, UsdGeom, UsdPhysics

stage = get_current_stage()
CubePath = "/World/CubeName"                                    # 立方体を作成
cubeGeom = UsdGeom.Cube.Define(stage, CubePath)
cubePrim = stage.GetPrimAtPath(CubePath)
cubeGeom.AddTranslateOp().Set(Gf.Vec3f(2.0, 0.0, 0.0))          # LIDAR から離す
cubeGeom.CreateSizeAttr(1)                                      # 適切にスケール
collisionAPI = UsdPhysics.CollisionAPI.Apply(cubePrim)          # 物理コライダーを追加
```

### データを取得する

LiDAR は最初のフレームのデータを得るためにシミュレーションを 1 フレーム進める必要があります。`timeline.play()` で開始し、1 フレーム待ってから `timeline.pause()` で深度バッファを埋めます。スクリプトと非同期に実行されるため、`asyncio` と `ensure_future` を使います。

```python
import asyncio

import omni.timeline


async def get_lidar_param():                                    # LIDAR からデータを取得する関数
    await omni.kit.app.get_app().next_update_async()            # データのため 1 フレーム待つ
    timeline.pause()                                            # 深度バッファを埋めるため一時停止
    depth = lidarInterface.get_linear_depth_data("/World" + lidarPath)
    zenith = lidarInterface.get_zenith_data("/World" + lidarPath)
    azimuth = lidarInterface.get_azimuth_data("/World" + lidarPath)
    print("depth", depth)                                       # データを表示
    print("zenith", zenith)
    print("azimuth", azimuth)


timeline = omni.timeline.get_timeline_interface()
timeline.play()                                                 # シミュレーション開始
asyncio.ensure_future(get_lidar_param())                        # スイープ完了後にのみデータを要求
```

![Python での LiDAR データ取得](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isaac_range_sensor_lidar_python.png)

## ステップ 5：点群をセグメンテーションする

深度データにセマンティックラベルを付けて、結果の点群をセグメンテーションできます。前の例との主な違いは次のとおりです。

- LiDAR 作成時に `enable_semantics=True` を設定する
- Cube と Sphere に異なるセマンティックラベルを割り当てる
- `get_point_cloud_data` と `get_prim_data` で点群とセマンティック ID を取得する

```python
import asyncio

import omni
from isaacsim.sensors.physx import _range_sensor
from pxr import Gf, Semantics, UsdGeom, UsdPhysics

stage = omni.usd.get_context().get_stage()
timeline = omni.timeline.get_timeline_interface()
lidarInterface = _range_sensor.acquire_lidar_sensor_interface()
omni.kit.commands.execute('AddPhysicsSceneCommand', stage=stage, path='/World/PhysicsScene')
lidarPath = "/LidarName"
# Lidar prim を作成（セマンティクスを有効化）
result, prim = omni.kit.commands.execute(
    "RangeSensorCreateLidar",
    path=lidarPath,
    parent="/World",
    min_range=0.4,
    max_range=100.0,
    draw_points=True,
    draw_lines=False,
    horizontal_fov=360.0,
    vertical_fov=60.0,
    horizontal_resolution=0.4,
    vertical_resolution=0.4,
    rotation_rate=0.0,
    high_lod=True,
    yaw_offset=0.0,
    enable_semantics=True
)
UsdGeom.XformCommonAPI(stage.GetPrimAtPath("/World" + lidarPath)).SetTranslate((2.0, 0.0, 0.0))

# Cube と Sphere を作成し、コライダーと異なるセマンティックラベルを追加
primType = ["Cube", "Sphere"]
for i in range(2):
    prim = stage.DefinePrim("/World/" + primType[i], primType[i])
    UsdGeom.XformCommonAPI(prim).SetTranslate((-2.0, -2.0 + i * 4.0, 0.0))
    UsdGeom.XformCommonAPI(prim).SetScale((1, 1, 1))
    collisionAPI = UsdPhysics.CollisionAPI.Apply(prim)

    # セマンティックラベルを追加
    sem = Semantics.SemanticsAPI.Apply(prim, "Semantics")
    sem.CreateSemanticTypeAttr()
    sem.CreateSemanticDataAttr()
    sem.GetSemanticTypeAttr().Set("class")
    sem.GetSemanticDataAttr().Set(primType[i])

# Lidar のヒット点の点群とセマンティック ID を取得
async def get_lidar_param():
    await asyncio.sleep(1.0)
    timeline.pause()
    pointcloud = lidarInterface.get_point_cloud_data("/World" + lidarPath)
    semantics = lidarInterface.get_prim_data("/World" + lidarPath)
    print("Point Cloud", pointcloud)
    print("Semantic ID", semantics)

timeline.play()
asyncio.ensure_future(get_lidar_param())
```

![セグメンテーションされた点群](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_5.1_full_tut_viewport_range_sensor_lidar_segmented_point_cloud.png)

## まとめ

このチュートリアルでは、次の内容を学びました。

- PhysX SDK Lidar がレイキャストで LiDAR を模擬し、常に ground truth を返すこと（RTX LiDAR との違い）
- GUI で回転式 LiDAR を作成し、可視化・衝突検出・親子付けを設定する方法
- `_range_sensor` インターフェースと `RangeSensorCreateLidar` コマンドでデータを取得する方法
- `enable_semantics=True` と `get_point_cloud_data` / `get_prim_data` で点群をセグメンテーションする方法
- Isaac Sim 6.0 での後継が `isaacsim.sensors.experimental.physics.RaycastSensor` であること

## 次のステップ

- [PhysX SDK Lightbeam センサー](17_physx_lightbeam.md) で、ライトカーテン状のセンサーを学びます。
