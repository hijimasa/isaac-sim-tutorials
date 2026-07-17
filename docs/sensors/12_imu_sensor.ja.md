---
title: IMU センサー
---

# IMU センサー

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- IMU センサーが加速度計・ジャイロの読み値を出力する仕組み
- IMU センサーのプロパティ（フィルタ幅など）
- GUI・Python API（`IMU` オーサリングクラス + `IMUSensor` ランタイムクラス）での作成方法
- OmniGraph での読み取りと重力の扱い

## はじめに

### 前提条件

- [Physics ベースのセンサー](08_physics_sensors.md) の概要を理解していること
- 剛体（Rigid Body）の基礎を理解していること

### 所要時間

約 15〜20 分

### 概要

Isaac Sim の IMU センサーは、物体の運動を追跡し、シミュレートされた**加速度計**と**ジャイロスコープ**の読み値を出力します。実機の IMU と同様、ローカルの x, y, z 軸での加速度と角速度をステージ単位で測定します。

!!! note "Isaac Sim 6.0 での API 変更"
    Isaac Sim 6.0 では、従来の `isaacsim.sensors.physics` 拡張機能の IMU センサーは非推奨（deprecated）となり、
    `isaacsim.sensors.experimental.physics.IMUSensor` に置き換えられました。本ページのコードは新 API に対応しています。
    詳細は[公式移行ガイド](https://docs.isaacsim.omniverse.nvidia.com/latest/migration_guides/isaac_sim_6_0/sensors_physics_to_experimental_physics.html)を参照してください。

!!! note "IMU センサーのプロパティ"
    - **enabled** … センサーの動作/停止を切り替えます。
    - **sensorPeriod** … 測定間隔。`isaacsim.robot.schema` 6.2.0 以降は非推奨で、非推奨の `isaacsim.sensors.physics` 拡張機能でのみ使用されます。新しい `isaacsim.sensors.experimental.physics` 拡張機能は毎物理ステップで読み取ります。
    - **angularVelocityFilterWidth** … 角速度の移動平均のサイズ。大きくすると角速度出力が滑らかになります。
    - **linearAccelerationFilterWidth** … 線形加速度の移動平均のサイズ。大きくすると加速度出力が滑らかになります。
    - **orientationFilterWidth** … 姿勢の移動平均のサイズ。大きくすると姿勢出力が滑らかになります。

    補間に使うデータバッファのサイズは、フィルタ幅の最大値の 2 倍、または 20 のいずれか大きい方です。

## ステップ 1：GUI でセンサーを作成する

シーンに IMU を付けたい prim があるとして、次の手順で作成・変更します。

1. **Create > Physics > Physics Scene** で Physics Scene を作成します。右の Stage パネルに `PhysicsScene` prim ができることを確認します。
2. IMU を付けたい prim を選択し、**Create > Sensors > Imu Sensor** をクリックします。
3. 位置・姿勢は `Imu_Sensor` prim を選択して Property タブの **Transform** で変更します。
4. その他のプロパティ（filter width、enable/disable、sensor period）は **Raw USD Properties** から変更します。

![IMU センサーの作成](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_4.5_full_tut_gui_create_imu_sensor_2.webp)

### IMU の例

1. **Windows > Examples > Robotics Examples** で Robotics Examples タブを有効にします。
2. **Robotics Examples > Sensors > IMU Sensor > Load Scene** をクリックします。
3. 加速度計とジャイロの各軸の読み値が表示されるウィンドウを確認します。
4. **Open Source Code** でソースコードを確認できます（Ant を読み込み、Python API でセンサーを追加する例）。
5. **PLAY** で開始し、**SHIFT + 左クリック**で Ant をドラッグすると読み値が変化します。

![IMU の例](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_4.5_full_tut_gui_create_imu_sensor.webp)

## ステップ 2：OmniGraph ワークフロー

### シーンのセットアップ

Simple Articulation を追加します。Content Browser で `Robots/IsaacSim/SimpleArticulation/simple_articulation.usd` を **World** prim にドラッグし、`/World/simple_articulation/Arm/RevoluteJoint` の **Drive** で target velocity を `90 deg/s`、stiffness を `0` に設定します。

その後、IMU センサーを追加します。

1. Stage タブで `/World/simple_articulation/Arm` prim を選択します。
2. **Create > Sensors > Imu Sensor** でセンサーを追加します。
3. Arm prim の横の **+** ボタンで、追加された IMU センサーを確認できます。

!!! note
    一般に、センサーは正しくデータを報告するために**剛体 prim** に追加する必要があります。このロボットの prim はすでに剛体なので、このケースでは特別な操作は不要です。

![IMU の OmniGraph シーン](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_4.5_full_tut_gui_create_imu_sensor_1.webp)

### OmniGraph のセットアップ

1. **Window > Graph Editors > Action Graph** で新しい Action Graph を作成します。
2. 次のノードを追加します。
    - **On Playback Tick** … 毎ステップでグラフを実行します。
    - **Isaac Read IMU Node** … IMU を読み取ります。Property タブで **IMU Prim** を `/World/simple_articulation/Arm/Imu_Sensor` に設定します。重力加速度を読みたい場合は **read gravity** を選択します。
    - **To String** … 読み値を文字列に変換します。
    - **Print Text** … 文字列をコンソールに出力します（Log Level を Warning に設定）。
3. ノードを接続し **Play** を押すと、内部コンソールに角速度が出力されます。

## ステップ 3：Standalone Python でセンサーを作成する

まず、GroundPlane・コリジョンと剛体を設定した Cube prim・PhysicsScene を追加してシーンを準備します。

```python
from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": False})

import numpy as np
import omni.usd
from isaacsim.core.experimental.objects import Cube, GroundPlane
from isaacsim.core.experimental.prims import GeomPrim, RigidPrim
from pxr import UsdPhysics

# 物理シーンを作成する
stage = omni.usd.get_context().get_stage()
UsdPhysics.Scene.Define(stage, "/World/PhysicsScene")

# 地面と、コリジョン・剛体を設定した動的な立方体を追加する
GroundPlane("/World/groundPlane", sizes=10, colors=np.array([0.5, 0.5, 0.5]))
Cube(
    "/World/Cube",
    positions=np.array([-0.5, -0.2, 1.0]),
    scales=np.array([0.5, 0.5, 0.5]),
    colors=np.array([0.2, 0.3, 0.0]),
)
RigidPrim("/World/Cube")
GeomPrim("/World/Cube", apply_collision_apis=True)
```

### Python API で作成する

`IMU.create()`（オーサリングクラス）でセンサー prim を作成し、`IMUSensor`（ランタイムクラス）でラップしてデータにアクセスします。パスには親 prim のパスを含める必要があり、残りの引数は省略可能です。

```python
import numpy as np
from isaacsim.sensors.experimental.physics import IMU, IMUSensor

sensor = IMUSensor(
    IMU.create(
        "/World/Cube/imu_sensor",
        linear_acceleration_filter_size=10,
        angular_velocity_filter_size=10,
        orientation_filter_size=10,
        translations=np.array([[0.0, 0.0, 0.0]]),
        orientations=np.array([[1.0, 0.0, 0.0, 0.0]]),
    )
)
```

### Python ラッパーで作成する

`IMU` オーサリングオブジェクトを直接構築して `IMUSensor` でラップすることもできます。`IMU` コンストラクタは、既存のセンサー prim をラップするか、デフォルト属性で新規作成します。`IMUSensor` ランタイムは `get_sensor_reading()` / `get_data()` を提供します。USD 属性（フィルタ幅など）の変更は、構築後に `sensor.imu` でアクセスできるオーサリングオブジェクト経由で行います。

```python
import numpy as np
from isaacsim.sensors.experimental.physics import IMU, IMUSensor

IMUSensor(
    IMU(
        "/World/Cube/Imu",
        translations=np.array([[0.0, 0.0, 0.0]]),  # または positions=np.array([[0.0, 0.0, 0.0]])
        orientations=np.array([[1.0, 0.0, 0.0, 0.0]]),
        linear_acceleration_filter_size=10,
        angular_velocity_filter_size=10,
        orientation_filter_size=10,
    )
)
```

!!! note
    `translations`（ローカル座標系）と `positions`（ワールド座標系）は同時に指定できません（排他）。各入力引数の使い方は IMUSensor の Python API ドキュメントを参照してください。

    フィルタ幅を構築時に設定するには、上のスニペットのように `IMU.create()`（または `IMU(path, ...)`）に渡します。構築後に変更するには、センサー prim（`sensor.imu.prims[0]` でアクセス可能）の USD 属性（`linearAccelerationFilterWidth` / `angularVelocityFilterWidth` / `orientationFilterWidth`）を設定します。フィルタ幅はシミュレーション開始時にセンサーが作成される際に C++ ランタイムへ取り込まれるため、変更を反映するにはシミュレーションを停止して再開してください。`IMUSensor` は毎物理ステップで読み取ります。

## ステップ 4：センサー出力を読み取る

IMU は **PLAY 時に動的に作成**されます。実行中にセンサー prim を移動するとセンサーが無効になります。剛体の親を変えるなどの階層的変更をする場合は、停止 → 変更 → 再開してください。

読み取り方法は 3 つあります。

- `IMUSensor.get_sensor_reading(read_gravity=True)` … 生の C++ 構造体を直接返す
- `IMUSensor.get_data(read_gravity=True)` … 構造化された辞書を返す
- OmniGraph ノード **Isaac Read IMU Node**

### get_sensor_reading()

`IMUSensor.get_sensor_reading(read_gravity=True)` は、`is_valid` / `time` / `linear_acceleration_x, _y, _z` / `angular_velocity_x, _y, _z` / `orientation_w, _x, _y, _z` プロパティを持つ `ImuSensorReading`（C++ 構造体）を返します。センサーは毎物理ステップで C++ バックエンドを読み取ります。重力加速度を除外するには `read_gravity=False` を渡します。

重力の影響を含めて読み取る例です。

```python
from isaacsim.sensors.experimental.physics import IMUSensor

sensor = IMUSensor("/World/Cube/Imu")
sensor.get_sensor_reading(read_gravity=True)
```

重力なしで読み取る例です。

```python
from isaacsim.sensors.experimental.physics import IMUSensor

sensor = IMUSensor("/World/Cube/Imu")
sensor.get_sensor_reading(read_gravity=False)
```

### get_data()

`IMUSensor` ランタイムクラスの `get_data(read_gravity=True)` メンバー関数は `get_sensor_reading()` のラッパーで、`time` / `physics_step` / `linear_acceleration`（shape `(3,)` の np.ndarray）/ `angular_velocity`（shape `(3,)` の np.ndarray）/ `orientation`（shape `(4,)` の np.ndarray、wxyz 順）をキーとする辞書を返します。

```python
import numpy as np
from isaacsim.sensors.experimental.physics import IMU, IMUSensor

sensor = IMUSensor(
    IMU(
        "/World/Cube/Imu",
        translations=np.array([[0.0, 0.0, 0.0]]),
        orientations=np.array([[1.0, 0.0, 0.0, 0.0]]),
        linear_acceleration_filter_size=10,
        angular_velocity_filter_size=10,
        orientation_filter_size=10,
    )
)

value = sensor.get_data()
print(value)
```

## まとめ

このチュートリアルでは、次の内容を学びました。

- IMU センサーが加速度計・ジャイロの読み値をローカル軸で出力すること
- フィルタ幅で出力の滑らかさを調整できること
- GUI・Python API（`IMU` オーサリングクラス + `IMUSensor` ランタイムクラス）での作成方法
- `get_sensor_reading()` / `get_data()` での読み取りと重力の扱い

`IMUSensor` の詳細は [isaacsim.sensors.experimental.physics の API ドキュメント](https://docs.isaacsim.omniverse.nvidia.com/latest/py/source/extensions/isaacsim.sensors.experimental.physics/docs/index.html)を参照してください。

## 次のステップ

- [Proximity センサー](13_proximity_sensor.md) で、近接検出を学びます。
