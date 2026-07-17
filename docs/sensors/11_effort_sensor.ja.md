---
title: Effort センサー
---

# Effort センサー

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- Effort センサーが関節に加わるトルク・力を追跡する仕組み
- `EffortSensor` クラスでセンサーを作成・変更する方法
- `get_sensor_reading()` / `get_data()` による Python での読み取り方法
- OmniGraph で Effort センサーを扱う方法

## はじめに

### 前提条件

- [Physics ベースのセンサー](08_physics_sensors.md) の概要を理解していること
- Articulation（多関節構造）の基礎を理解していること

### 所要時間

約 10〜15 分

### 概要

Isaac Sim の Effort センサーは、個々の関節に加わる**トルクまたは力**を追跡します。回転関節（revolute）では**トルク**、直動関節（linear）では**力の大きさ**が測定されます。

!!! note "Isaac Sim 6.0 での API 変更"
    Isaac Sim 6.0 では、従来の `isaacsim.sensors.physics` 拡張機能の Effort センサーは非推奨（deprecated）となり、
    `isaacsim.sensors.experimental.physics.EffortSensor` に置き換えられました。本ページのコードは新 API に対応しています。
    詳細は[公式移行ガイド](https://docs.isaacsim.omniverse.nvidia.com/latest/migration_guides/isaac_sim_6_0/sensors_physics_to_experimental_physics.html)を参照してください。

## ステップ 1：シーンをセットアップする

Content Browser から Simple Articulation を追加します。

1. Content Browser で `simple_articulation` を検索するか、`Isaac Sim/Robots/IsaacSim/SimpleArticulation/simple_articulation.usd` を開きます。
2. `simple_articulation` を右側の Stage ウィンドウの **World** prim にドラッグして追加します。
3. 回転関節を駆動するため、Stage ウィンドウで `/World/simple_articulation/Arm/RevoluteJoint` を選択し、Property ウィンドウの **Drive** で target velocity を `90 deg/s`、stiffness を `0` に設定します。

## ステップ 2：Effort センサーを作成する

**Window > Script Editor** から Script Editor を開き、`EffortSensor` クラスに関節 prim のパスを渡してセンサーを作成します。このクラスは読み取り用の `get_sensor_reading()` / `get_data()` と、実行時の再設定用の `update_dof_name()` / `change_buffer_size()` を提供します（Contact・IMU・Raycast センサーと異なり、Effort センサーはスキーマを持つ独自の prim を作らないため、独立したオーサリングクラスはありません）。

```python
from isaacsim.sensors.experimental.physics import EffortSensor

sensor = EffortSensor(path="/World/simple_articulation/Arm/RevoluteJoint", enabled=True)
```

!!! note "センサー prim は関節そのもの"
    渡した関節 prim がセンサーの prim になります。`EffortSensor` は構築時に Stage パネルへ別の USD prim を作成しません。エフォートの読み値はシミュレーション再生中に `get_sensor_reading()` で取得でき、Play を押した後に `reading.is_valid` を確認するとセンサーが有効かどうか分かります。

!!! note "パラメータの変更"
    `enabled` などはクラスのメンバ変数を直接変更できます。読み値の `dof_name` や `buffer_size` を変えるには、メンバ関数 `update_dof_name` / `change_buffer_size` を使います。

## ステップ 3：Python で出力を読み取る

出力の読み取り方法は 2 つあります。

- `EffortSensor.get_sensor_reading()` … `is_valid` / `time` / `value` を含む `EffortSensorReading` オブジェクトを返す
- `EffortSensor.get_data()` … `value` / `is_valid` / `time` / `physics_step` を含む構造化された辞書を返す

センサーを作成したら **Play** で開始し、次の関数で現在フレームの読み値を取得します。

```python
reading = sensor.get_sensor_reading()
```

`get_data()` を使う例です。

```python
frame = sensor.get_data()
print(f"Effort: {frame['value']}, valid: {frame['is_valid']}, time: {frame['time']}")
```

## ステップ 4：OmniGraph ワークフロー

1. **Window > Graph Editors > Action Graph** で新しい Action Graph を作成します。
2. 次のノードを追加します。
    - **On Playback Tick** … 毎ステップでグラフを実行します。
    - **Isaac Read Effort Node** … Effort センサーを読み取ります。Property タブで **Effort Prim** を測定対象の関節（例：`/World/simple_articulation/Arm/RevoluteJoint`）に設定します。
    - **To String** … 読み値を文字列に変換します。
    - **Print Text** … 文字列をコンソールに出力します。Log Level を Warning に設定し、必要なら **To Screen** をチェックして画面にも表示します。
3. ノードを接続すると、Effort センサーの読み値が出力されます。

![Effort センサーの OmniGraph](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_4.5_full_tut_gui_effort_sensor_omnigraph.png)

!!! note
    期待どおりの読み値を得るには、関節を正しい軸に設定してください。

## まとめ

このチュートリアルでは、次の内容を学びました。

- Effort センサーが回転関節ではトルク、直動関節では力の大きさを測定すること
- `EffortSensor` クラスでの作成とパラメータ変更
- `get_sensor_reading()` / `get_data()` による読み取り
- OmniGraph での Effort センサーの扱い方

`EffortSensor` の詳細は [isaacsim.sensors.experimental.physics の API ドキュメント](https://docs.isaacsim.omniverse.nvidia.com/latest/py/source/extensions/isaacsim.sensors.experimental.physics/docs/index.html)を参照してください。

## 次のステップ

- [IMU センサー](12_imu_sensor.md) で、加速度・角速度の取得を学びます。
