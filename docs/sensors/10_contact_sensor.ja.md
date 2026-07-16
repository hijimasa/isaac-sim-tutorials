---
title: Contact センサー
---

# Contact センサー

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- Contact センサーが PhysX Contact Report API 上でどう動作するか
- Contact センサーのプロパティ（radius / threshold / sensor period など）
- GUI・Python コマンド・Python ラッパークラスでセンサーを作成する方法
- OmniGraph で接触データを読み取り・可視化する方法
- 3 種類のデータ読み取り方法

## はじめに

### 前提条件

- [Physics ベースのセンサー](08_physics_sensors.md) の概要を理解していること
- 剛体・コライダーの基礎を理解していること

### 所要時間

約 15〜20 分

### 概要

Contact センサーは、PhysX の **Contact Report API** を使い、物体の表面に配置した接触セルや圧力センサーのような読み値を生成します。Contact センサー API は、センサーが配置されたオブジェクトでフィルタした接触データを提供し、オプションでオブジェクトの特定領域内の接触だけを考慮するフィルタも設定できます。

たとえば、足に接触センサーを持つ四足歩行ロボットを考えます。シミュレーション上では脚全体が 1 つの剛体として扱われますが、接触を測定したいのは足裏だけです。そこで**領域フィルタ**を追加すると、その境界外の接触を破棄できます。

Contact センサー API は、PhysX が計算時間節約のため接触のストリーミングを止めても、**接触データを保持し続けます**。単一セルの接触パッドで得られる実データに合わせて設計されていますが、完全な接触情報（接触ペア・法線・接触点）が必要な場合も、PhysX から取得したものと同じ情報をフィルタして返します。

!!! note "Contact センサーのプロパティ"
    - **radius** … 接触力を検知する距離を指定します。
    - **enabled** … センサーの動作/停止を切り替えます。
    - **min threshold** … 接触をトリガーする最小の力を指定します。
    - **max threshold** … センサーが出力する最大の力を指定します。
    - **sensor period** … センサー測定の間隔（時間）を指定します。物理ステップより短い周期を指定すると常に最新の物理データを出力します。センサー周波数が物理周波数を超えることはできません。

## ステップ 1：GUI でセンサーを作成する

シーンに接触センサーを付けたい prim があるとして、次の手順で作成・変更します。

1. **Create > Physics > Physics Scene** で Physics Scene を作成します。右の Stage パネルに `PhysicsScene` prim ができることを確認します。
2. 接触センサーを付けたい prim を選択し、**Create > Sensors > Contact_sensor** をクリックします。
3. 位置・姿勢は **Translate** / **Orientate** タブで変更します。
4. その他のプロパティ（min/max force threshold、enable/disable、sensor period）は **Raw USD Properties** から変更します。

### Contact センサーの例

1. **Windows > Examples > Robotics Examples** で Robotics Examples タブを有効にします。
2. **Robotics Examples > Sensors > Contact Sensor** をクリックします。
3. 各アームごとに色分けされた力の読み値ウィンドウが表示されることを確認します。
4. **Open Source Code** でソースコードを確認できます（Ant を読み込み、Python API でセンサーを追加する例）。
5. **PLAY** で開始し、**SHIFT + 左クリック**で Ant をドラッグすると読み値が変化します。

![Contact センサーの作成](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_full_tut_gui_create_contact_sensor.webp)

## ステップ 2：OmniGraph で読み取り・可視化する

### シーンのセットアップ

1. **Create > Mesh > Cube** で立方体を追加し、上方向に移動します。立方体を右クリックし **Add > Physics > Rigid Body with Colliders Preset** を適用します。
2. **Create > Physics > PhysicsScene** を追加します。
3. **Create > Physics > GroundPlane** を追加します。
4. 立方体を選択し **Create > Sensors > Contact Sensor** で接触センサーを追加します。

![OmniGraph シーンのセットアップ](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_full_tut_gui_create_contact_sensor_1.webp)

### OmniGraph のセットアップ

1. **Window > Graph Editors > Action Graph** で新しい Action Graph を作成します。
2. 次のノードを追加します。
    - **On Playback Tick** … 毎ステップでグラフを実行します。
    - **Isaac Read Contact Sensor** … 接触センサーを読み取ります。Property タブで **Contact Sensor Prim** を `/World/Cube/Contact_Sensor` に設定します。
    - **To String** … 読み値を文字列に変換します。
    - **Print Text** … 文字列をコンソールに出力します。Property タブで **Log Level** を **Warning** に設定します。
3. ノードを接続し、**Play** を押すと、Isaac Sim の内部コンソールに接触力が出力されます。

!!! tip "接触センサーの可視化"
    **Isaac xPrim Radius Visualizer** ノードで、接触センサーの位置と半径を可視化できます。xPrim 入力を Contact Sensor Prim に、Tick を Exec in に接続し、正しい半径・色・線の太さを設定すると、PLAY 時にセンサーが表示されます。

!!! note "球状領域は境界のみを決める"
    球状領域は「考慮する接触の境界」を決めるだけです。すべての接触は、その球状領域で区切られたオブジェクトの表面でのみ発生します。

![接触の可視化](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isaac_tutorial_visualize_contact.png)

## ステップ 3：Standalone Python でセンサーを作成する

まず、PhysicsScene・GroundPlane・DynamicCuboid を追加してシーンを準備します（接触センサーは立方体に取り付けます）。

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

`IsaacSensorCreateContactSensor` コマンドで作成します。必須パラメータは親パスのみです。

```python
import omni.kit.commands
from pxr import Gf

success, _isaac_sensor_prim = omni.kit.commands.execute(
    "IsaacSensorCreateContactSensor",
    path="Contact_Sensor",
    parent="/World/Cube",
    sensor_period=1,
    min_threshold=0.0001,
    max_threshold=100000,
    translation=Gf.Vec3d(0, 0, 0),
)
```

### Python ラッパークラスで作成する

`ContactSensor` ラッパークラスを使うと、プロパティ設定やデータ取得のヘルパー関数が使えます。

```python
from isaacsim.sensors.physics import ContactSensor
import numpy as np

sensor = ContactSensor(
    prim_path="/World/Cube/Contact_Sensor",
    name="Contact_Sensor",
    frequency=60,
    translation=np.array([0, 0, 0]),
    min_threshold=0,
    max_threshold=10000000,
    radius=-1
)
```

!!! note "作成時の注意"
    - `translation` と `position`、`frequency` と `dt` は同時に指定できません。
    - 接触センサーは**コライダー API を持つ prim** にのみ作成でき、Contact Report API に依存します。コマンド・ラッパークラスのどちらも親 prim に Contact Report API を自動追加します。手動で追加する場合は次のようにします。

    ```python
    import omni
    from pxr import PhysxSchema

    stage = omni.usd.get_context().get_stage()
    parent_prim = stage.GetPrimAtPath("/World/Cube")
    contact_report = PhysxSchema.PhysxContactReportAPI.Apply(parent_prim)
    contact_report.CreateThresholdAttr(0.0)  # 接触レポートの最小しきい値を 0 に設定
    ```

## ステップ 4：センサー出力を読み取る

接触センサーは **PLAY 時に動的に作成**されます。シミュレーション実行中にセンサー prim を移動するとセンサーが無効になります。剛体の親を変えるなど階層的な変更をする場合は、シミュレータを停止 → 変更 → 再開してください。

出力の読み取り方法は 3 つあります。

- センサーインターフェースの `get_sensor_reading()`（**推奨**）
- `ContactSensor` クラスの `get_current_frame()`
- OmniGraph ノード **Isaac Read Contact Sensor**

### get_sensor_reading()

`get_sensor_reading(sensor_path, use_latest_data=False)` は、接触センサー prim のパスと、`use_latest_data` フラグ（センサーが物理レートより遅い場合に現在の物理ステップからデータを取得）を受け取ります。戻り値の `CsSensorReading` オブジェクトは `is_valid` / `time` / `value` / `in_contact` を含みます。

```python
from isaacsim.sensors.physics import _sensor

_contact_sensor_interface = _sensor.acquire_contact_sensor_interface()
_contact_sensor_interface.get_sensor_reading("/World/Cube/Contact_Sensor", use_latest_data=True)
```

### get_current_frame()

`get_current_frame()` は `get_sensor_reading()` と `get_contact_sensor_raw_data` のラッパーで、`in_contact` / `force` / `number_of_contacts` / `time` / `body0` / `body1` / `position` / `normal` / `impulse` / `contacts` / `physics_step` をキーとする辞書を返します。

```python
value = sensor.get_current_frame()
print(value)
```

### get_contact_sensor_raw_data()

生の接触 API データ `CsRawData`（`time` / `dt` / `body0` / `body1` / `position` / `normal` / `impulse`）のリストを出力します。生データはセンサーのしきい値を無視するため、しきい値未満の接触もここには現れます。

```python
from isaacsim.sensors.physics import _sensor

_contact_sensor_interface = _sensor.acquire_contact_sensor_interface()
raw_data = _contact_sensor_interface.get_contact_sensor_raw_data("/World/Cube/Contact_Sensor")
print(str(raw_data))
```

!!! warning
    `get_contact_sensor_raw_data()` は非推奨で、将来のリリースで置き換えられる予定です。

## まとめ

このチュートリアルでは、次の内容を学びました。

- Contact センサーが PhysX Contact Report API 上で動作し、領域フィルタで特定部位の接触だけを検出できること
- GUI・Python コマンド・`ContactSensor` ラッパークラスでの作成方法
- OmniGraph での読み取りと可視化
- `get_sensor_reading()`（推奨）を含む 3 つの読み取り方法

## 次のステップ

- [Effort センサー](11_effort_sensor.md) で、関節のトルク・力の追跡を学びます。
