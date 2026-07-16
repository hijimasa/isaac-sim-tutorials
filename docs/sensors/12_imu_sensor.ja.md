---
title: IMU センサー
---

# IMU センサー

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- IMU センサーが加速度計・ジャイロの読み値を出力する仕組み
- IMU センサーのプロパティ（フィルタ幅など）
- GUI・Python コマンド・Python ラッパークラスでの作成方法
- OmniGraph での読み取り、重力の扱い、カスタム補間

## はじめに

### 前提条件

- [Physics ベースのセンサー](08_physics_sensors.md) の概要を理解していること
- 剛体（Rigid Body）の基礎を理解していること

### 所要時間

約 15〜20 分

### 概要

Isaac Sim の IMU センサーは、物体の運動を追跡し、シミュレートされた**加速度計**と**ジャイロスコープ**の読み値を出力します。実機の IMU と同様、ローカルの x, y, z 軸での加速度と角速度をステージ単位で測定します。

!!! note "IMU センサーのプロパティ"
    - **enabled** … センサーの動作/停止を切り替えます。
    - **sensor period** … 測定間隔。物理デルタタイムより短い周期は常に最新の物理データを出力します。センサー周波数が物理周波数を超えることはできません。
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

![IMU センサーの作成](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_full_tut_gui_create_imu_sensor_2.webp)

### IMU の例

1. **Windows > Examples > Robotics Examples** で Robotics Examples タブを有効にします。
2. **Robotics Examples > Sensors > IMU Sensor > Load Scene** をクリックします。
3. 加速度計とジャイロの各軸の読み値が表示されるウィンドウを確認します。
4. **Open Source Code** でソースコードを確認できます（Ant を読み込み、Python API でセンサーを追加する例）。
5. **PLAY** で開始し、**SHIFT + 左クリック**で Ant をドラッグすると読み値が変化します。

![IMU の例](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_full_tut_gui_create_imu_sensor.webp)

## ステップ 2：OmniGraph ワークフロー

### シーンのセットアップ

Simple Articulation を追加します。Content Browser で `Robots/IsaacSim/SimpleArticulation/simple_articulation.usd` を **World** prim にドラッグし、`/World/simple_articulation/Arm/RevoluteJoint` の **Drive** で target velocity を `90 deg/s`、stiffness を `0` に設定します。

その後、IMU センサーを追加します。

1. Stage タブで `/World/simple_articulation/Arm` prim を選択します。
2. **Create > Sensors > Imu Sensor** でセンサーを追加します。
3. Arm prim の横の **+** ボタンで、追加された IMU センサーを確認できます。

!!! note
    一般に、センサーは正しくデータを報告するために**剛体 prim** に追加する必要があります。このロボットの prim はすでに剛体なので、このケースでは特別な操作は不要です。

![IMU の OmniGraph シーン](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_full_tut_gui_create_imu_sensor_1.webp)

### OmniGraph のセットアップ

1. **Window > Graph Editors > Action Graph** で新しい Action Graph を作成します。
2. 次のノードを追加します。
    - **On Playback Tick** … 毎ステップでグラフを実行します。
    - **Isaac Read IMU Node** … IMU を読み取ります。Property タブで **IMU Prim** を `/World/simple_articulation/Arm/Imu_Sensor` に設定します。重力加速度を読みたい場合は **read gravity** を選択します。
    - **To String** … 読み値を文字列に変換します。
    - **Print Text** … 文字列をコンソールに出力します（Log Level を Warning に設定）。
3. ノードを接続し **Play** を押すと、内部コンソールに角速度が出力されます。

## ステップ 3：Standalone Python でセンサーを作成する

まず、GroundPlane・DynamicCuboid・PhysicsScene を追加してシーンを準備します。

```python
from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": False})

import numpy as np
from isaacsim.core.api.objects import DynamicCuboid
from isaacsim.core.api.objects.ground_plane import GroundPlane
from isaacsim.core.api.physics_context import PhysicsContext

PhysicsContext()
GroundPlane(prim_path="/World/groundPlane", size=10, color=np.array([0.5, 0.5, 0.5]))
DynamicCuboid(prim_path="/World/Cube",
    position=np.array([-.5, -.2, 1.0]),
    scale=np.array([.5, .5, .5]),
    color=np.array([.2, .3, 0.]))
```

### Python コマンドで作成する

`IsaacSensorCreateImuSensor` コマンドで作成します。必須引数は親パスのみです。

```python
import omni.kit.commands
from pxr import Gf

success, _isaac_sensor_prim = omni.kit.commands.execute(
    "IsaacSensorCreateImuSensor",
    path="imu_sensor",
    parent="/World/Cube",
    sensor_period=1,
    linear_acceleration_filter_size=10,
    angular_velocity_filter_size=10,
    orientation_filter_size=10,
    translation=Gf.Vec3d(0, 0, 0),
    orientation=Gf.Quatd(1, 0, 0, 0),
)
```

### Python ラッパークラスで作成する

`IMUSensor` ラッパークラスを使うと、プロパティ設定やデータ取得のヘルパー関数が使えます。

```python
from isaacsim.sensors.physics import IMUSensor
import numpy as np

IMUSensor(
    prim_path="/World/Cube/Imu",
    name="imu",
    frequency=60,  # または dt=1./60
    translation=np.array([0, 0, 0]),  # または position=np.array([0, 0, 0])
    orientation=np.array([1, 0, 0, 0]),
    linear_acceleration_filter_size=10,
    angular_velocity_filter_size=10,
    orientation_filter_size=10,
)
```

!!! note
    `translation` と `position`、`frequency` と `dt` は同時に指定できません。パラメータ変更には `set_frequency` / `set_dt` などのクラス API や USD 属性 API を使います。

## ステップ 4：センサー出力を読み取る

IMU は **PLAY 時に動的に作成**されます。実行中にセンサー prim を移動するとセンサーが無効になります。剛体の親を変えるなどの階層的変更をする場合は、停止 → 変更 → 再開してください。

読み取り方法は 3 つあります。

- センサーインターフェースの `get_sensor_reading()`
- `IMUSensor` クラスの `get_current_frame()`
- OmniGraph ノード **Isaac Read IMU Node**

### get_sensor_reading()

`get_sensor_reading(sensor_path, interpolation_function=None, use_latest_data=False, read_gravity=True)` は、prim パス・補間関数（省略可）・use_latest_data フラグ（省略可）を受け取ります。戻り値の `IsSensorReading` は `is_valid` / `time` / `lin_acc_x, y, z` / `ang_vel_x, y, z` / `orientation` を持ちます。

重力の影響を含めて現在の物理ステップから読み取る例です。

```python
from isaacsim.sensors.physics import _sensor

_imu_sensor_interface = _sensor.acquire_imu_sensor_interface()
_imu_sensor_interface.get_sensor_reading("/World/Cube/Imu", use_latest_data=True, read_gravity=True)
```

重力なし・カスタム補間関数を使う例です。

```python
from isaacsim.sensors.physics import _sensor
from typing import List

# 入力: 過去の IsSensorReading のリスト、期待するセンサー読み取り時刻
def interpolation_function(data: List[_sensor.IsSensorReading], time: float) -> _sensor.IsSensorReading:
    interpolated_reading = _sensor.IsSensorReading()
    # 補間処理を行う
    return interpolated_reading

_imu_sensor_interface = _sensor.acquire_imu_sensor_interface()
_imu_sensor_interface.get_sensor_reading("/World/Cube/Imu", interpolation_function=interpolation_function, read_gravity=False)
```

!!! note "カスタム補間と重力"
    カスタム補間を使い、かつ read gravity フラグが有効な場合、センサーは生の加速度測定値を補間関数に渡し、その後に重力変換を適用します。

### get_current_frame()

`get_current_frame(read_gravity=True)` は `get_sensor_reading()` のラッパーで、`lin_acc` / `ang_vel` / `orientation` / `time` / `physics_step` をキーとする辞書を返します。

```python
from isaacsim.sensors.physics import IMUSensor
import numpy as np

sensor = IMUSensor(
    prim_path="/World/Cube/Imu",
    name="imu",
    frequency=60,
    translation=np.array([0, 0, 0]),
    orientation=np.array([1, 0, 0, 0]),
    linear_acceleration_filter_size=10,
    angular_velocity_filter_size=10,
    orientation_filter_size=10,
)

value = sensor.get_current_frame()
print(value)
```

## まとめ

このチュートリアルでは、次の内容を学びました。

- IMU センサーが加速度計・ジャイロの読み値をローカル軸で出力すること
- フィルタ幅で出力の滑らかさを調整できること
- GUI・Python コマンド・`IMUSensor` ラッパークラスでの作成方法
- `get_sensor_reading()` / `get_current_frame()` での読み取りと重力・カスタム補間の扱い

## 次のステップ

- [Proximity センサー](13_proximity_sensor.md) で、近接検出を学びます。
