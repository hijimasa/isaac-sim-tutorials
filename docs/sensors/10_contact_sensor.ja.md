---
title: Contact センサー
---

# Contact センサー

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- Contact センサーが PhysX Contact Report API 上でどう動作するか
- Contact センサーのプロパティ（radius / threshold など）
- GUI・Python API（`Contact` オーサリングクラス + `ContactSensor` ランタイムクラス）でセンサーを作成する方法
- OmniGraph で接触データを読み取り・可視化する方法
- 3 種類のデータ読み取り方法

## はじめに

### 前提条件

- [Physics ベースのセンサー](08_physics_sensors.md) の概要を理解していること
- 剛体・コライダーの基礎を理解していること

### 所要時間

約 15〜20 分

### 概要

!!! note "Isaac Sim 6.0 での API 変更"
    Isaac Sim 6.0 では、従来の `isaacsim.sensors.physics` 拡張機能の Contact センサーは非推奨（deprecated）となり、
    `isaacsim.sensors.experimental.physics.ContactSensor` に置き換えられました。本ページのコードは新 API に対応しています。
    詳細は[公式移行ガイド](https://docs.isaacsim.omniverse.nvidia.com/latest/migration_guides/isaac_sim_6_0/sensors_physics_to_experimental_physics.html)を参照してください。

Contact センサーは、PhysX の **Contact Report API** を使い、物体の表面に配置した接触セルや圧力センサーのような読み値を生成します。Contact センサー API は、センサーが配置されたオブジェクトでフィルタした接触データを提供し、オプションでオブジェクトの特定領域内の接触だけを考慮するフィルタも設定できます。

たとえば、足に接触センサーを持つ四足歩行ロボットを考えます。シミュレーション上では脚全体が 1 つの剛体として扱われますが、接触を測定したいのは足裏だけです。そこで**領域フィルタ**を追加すると、その境界外の接触を破棄できます。

Contact センサー API は、PhysX が計算時間節約のため接触のストリーミングを止めても、**接触データを保持し続けます**。単一セルの接触パッドで得られる実データに合わせて設計されていますが、完全な接触情報（接触ペア・法線・接触点）が必要な場合も、PhysX から取得したものと同じ情報をフィルタして返します。

!!! note "Contact センサーのプロパティ"
    - **radius** … 接触力を検知する距離を指定します。`-1` を指定すると prim のコリジョン形状を使用します。
    - **enabled** … センサーの動作/停止を切り替えます。
    - **min threshold** … 接触をトリガーする最小の力を指定します。
    - **max threshold** … センサーが出力する最大の力を指定します。
    - **sensorPeriod** … センサー測定の間隔（時間）を指定します。`isaacsim.robot.schema` 6.2.0 以降は非推奨で、非推奨の `isaacsim.sensors.physics` 拡張機能でのみ使用されます。新しい `isaacsim.sensors.experimental.physics` 拡張機能は毎物理ステップで読み取ります。

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

![Contact センサーの作成](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_4.5_full_tut_gui_create_contact_sensor.webp)

## ステップ 2：OmniGraph で読み取り・可視化する

### シーンのセットアップ

1. **Create > Mesh > Cube** で立方体を追加し、上方向に移動します。立方体を右クリックし **Add > Physics > Rigid Body with Colliders Preset** を適用します。
2. **Create > Physics > PhysicsScene** を追加します。
3. **Create > Physics > GroundPlane** を追加します。
4. 立方体を選択し **Create > Sensors > Contact Sensor** で接触センサーを追加します。

![OmniGraph シーンのセットアップ](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_4.5_full_tut_gui_create_contact_sensor_1.webp)

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

![接触の可視化](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isaac_tutorial_visualize_contact.png)

## ステップ 3：Standalone Python でセンサーを作成する

まず、PhysicsScene・GroundPlane・コリジョンと剛体を設定した Cube prim を追加してシーンを準備します（接触センサーは立方体に取り付けます）。

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

`Contact.create()`（オーサリングクラス）でセンサー prim を作成し、返されたオーサリングオブジェクトを `ContactSensor`（ランタイムクラス）でラップしてデータにアクセスします。パスには親 prim のパスを含める必要があります。

```python
import numpy as np
from isaacsim.sensors.experimental.physics import Contact, ContactSensor

sensor = ContactSensor(
    Contact.create(
        "/World/Cube/Contact_Sensor",
        min_threshold=0.0001,
        max_threshold=100000,
        translations=np.array([[0.0, 0.0, 0.0]]),
    )
)
```

### Python ラッパーで作成する

`Contact` オーサリングオブジェクトを直接構築して `ContactSensor` でラップすることもできます。`Contact` コンストラクタは、既存のセンサー prim をラップするか、デフォルト属性で新規作成します。`ContactSensor` ランタイムは `get_sensor_reading()` / `get_data()` / `get_raw_data()` を提供します。プロパティの setter/getter（`set_min_threshold` / `set_max_threshold` / `set_radius` など）は、構築後に `sensor.contact` でアクセスできるオーサリングオブジェクト側にあります。

```python
import numpy as np
from isaacsim.sensors.experimental.physics import Contact, ContactSensor

sensor = ContactSensor(
    Contact(
        "/World/Cube/Contact_Sensor",
        translations=np.array([[0.0, 0.0, 0.0]]),
    )
)
```

!!! note "作成時の注意"
    - `translations`（ローカル座標系）と `positions`（ワールド座標系）は同時に指定できません（排他）。
    - 接触センサーの作成には**有効な剛体（Rigid Body）の祖先 prim** が必要で、Contact Report API に依存します。接触を発生させるジオメトリにはコリジョン API も必要です。`Contact.create()` はセンサー prim の作成時に剛体の祖先へ Contact Report API を適用します。既存のセンサー prim を `Contact(path)` でラップした場合は Python 側では適用されませんが、Play でセンサーが有効化される際に C++ ランタイムが接触レポートの有効化を保証します。手動で追加する場合は次のようにします。

    ```python
    import omni
    from pxr import PhysxSchema

    stage = omni.usd.get_context().get_stage()
    parent_prim = stage.GetPrimAtPath("/World/Cube")
    contact_report = PhysxSchema.PhysxContactReportAPI.Apply(parent_prim)
    contact_report.CreateThresholdAttr(0.0)  # 接触レポートの最小しきい値を 0 に設定
    ```

    実行時にセンサーパラメータを変更するには、`sensor.contact.set_min_threshold(value)` のように `sensor.contact` 経由のオーサリングオブジェクトを使います（`ContactSensor` 本体のショートハンドメソッドは 3.0.0 で削除されました）。

## ステップ 4：センサー出力を読み取る

接触センサーは **PLAY 時に動的に作成**されます。シミュレーション実行中にセンサー prim を移動するとセンサーが無効になります。剛体の親を変えるなど階層的な変更をする場合は、シミュレータを停止 → 変更 → 再開してください。

出力の読み取り方法は 3 つあります。

- `ContactSensor.get_sensor_reading()` … キャッシュされた `ContactSensorReading` を返す
- `ContactSensor.get_data()` … 構造化された辞書を返す
- OmniGraph ノード **Isaac Read Contact Sensor**

### get_sensor_reading()

`ContactSensor.get_sensor_reading()` は、`is_valid` / `time` / `value`（力の大きさ）/ `in_contact` を含む `ContactSensorReading` を返します。

```python
from isaacsim.sensors.experimental.physics import ContactSensor

sensor = ContactSensor("/World/Cube/Contact_Sensor")
sensor.get_sensor_reading()
```

### get_data()

`ContactSensor` ランタイムクラスの `get_data()` メンバー関数は、`time` / `physics_step` / `in_contact` / `force` / `number_of_contacts` をキーとする構造化された辞書を返します。内部では接触状態の取得に `get_sensor_reading()` を、`number_of_contacts` の計算に `get_raw_data()` を呼び出します。`add_raw_contact_data_to_frame()` を呼んでおくと、辞書に `contacts` リストが追加され、各エントリで接触点ごとの `body0` / `body1` / `position` / `normal` / `impulse` が得られます。

```python
import numpy as np
from isaacsim.sensors.experimental.physics import Contact, ContactSensor

sensor = ContactSensor(
    Contact(
        "/World/Cube/Contact_Sensor",
        translations=np.array([[0.0, 0.0, 0.0]]),
    )
)

value = sensor.get_data()
print(value)
```

### get_raw_data()

現在の物理ステップの接触イベントごとの生の接触レコード（`time` / `dt` / `body0` / `body1` / `position` / `normal` / `impulse`）のリストを返します。生データはセンサーの `min_threshold` / `max_threshold` によるフィルタリングを無視するため、しきい値未満の接触もここには現れます。フレーム（`get_data()`）側に含めたい場合は `ContactSensor.add_raw_contact_data_to_frame()` で `contacts` リストを有効にします。

```python
from isaacsim.sensors.experimental.physics import ContactSensor

sensor = ContactSensor("/World/Cube/Contact_Sensor")
raw_data = sensor.get_raw_data()
print(str(raw_data))
```

## まとめ

このチュートリアルでは、次の内容を学びました。

- Contact センサーが PhysX Contact Report API 上で動作し、領域フィルタで特定部位の接触だけを検出できること
- GUI・Python API（`Contact` オーサリングクラス + `ContactSensor` ランタイムクラス）での作成方法
- OmniGraph での読み取りと可視化
- `get_sensor_reading()` / `get_data()` / OmniGraph の 3 つの読み取り方法

`ContactSensor` の詳細は [isaacsim.sensors.experimental.physics の API ドキュメント](https://docs.isaacsim.omniverse.nvidia.com/latest/py/source/extensions/isaacsim.sensors.experimental.physics/docs/index.html)を参照してください。

## 次のステップ

- [Effort センサー](11_effort_sensor.md) で、関節のトルク・力の追跡を学びます。
