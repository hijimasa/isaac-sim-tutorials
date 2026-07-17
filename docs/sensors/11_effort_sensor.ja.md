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

**Window > Script Editor** から Script Editor を開き、`EffortSensor` ラッパークラスでセンサーを作成します。

```python
from isaacsim.sensors.physics.scripts.effort_sensor import EffortSensor
import numpy as np

sensor = EffortSensor(
    prim_path="/World/simple_articulation/Arm/RevoluteJoint",
    sensor_period=0.1,
    use_latest_data=False,
    enabled=True
)
```

!!! note "パラメータの変更"
    `sensor_period` / `use_latest_data` / `enabled` はクラスのメンバ変数を直接変更できます。読み値の `dof_name` や `buffer_size` を変えるには、メンバ関数 `update_dof_name` / `change_buffer_size` を使います。

## ステップ 3：Python で出力を読み取る

`get_sensor_reading(self, interpolation_function=None, use_latest_data=False)` は次の 2 つのパラメータを受け取ります。

- **補間関数**（省略可）… デフォルトの線形補間の代わりに使う関数
- **use_latest_data フラグ**（省略可）… センサーが物理レートより遅い場合に現在の物理ステップからデータを取得

戻り値の `EsSensorReading` オブジェクトは `is_valid` / `time` / `value` を含みます。

センサーを作成したら **PLAY** で開始し、次の関数で現在フレームの読み値を取得します。

```python
from isaacsim.sensors.physics.scripts.effort_sensor import EffortSensor

# センサーの読み値を取得
reading = sensor.get_sensor_reading(use_latest_data=True)
```

カスタム補間関数を使う例です。

```python
from isaacsim.sensors.physics.scripts.effort_sensor import EffortSensor

# 入力: 過去の EsSensorReading のリスト、期待するセンサー読み取り時刻
def interpolation_function(data, time):
    interpolated_reading = EsSensorReading()
    # 補間処理を行う
    return interpolated_reading

# センサーの読み値を取得
reading = sensor.get_sensor_reading(interpolation_function)
```

## ステップ 4：OmniGraph ワークフロー

1. **Window > Graph Editors > Action Graph** で新しい Action Graph を作成します。
2. 次のノードを追加します。
    - **On Playback Tick** … 毎ステップでグラフを実行します。
    - **Isaac Read Effort Node** … Effort センサーを読み取ります。Property タブで **Effort Prim** を測定対象の関節（例：`/World/simple_articulation/Arm/RevoluteJoint`）に設定します。
    - **To String** … 読み値を文字列に変換します。
    - **Print Text** … 文字列をコンソールに出力します。Log Level を Warning に設定し、必要なら **To Screen** をチェックして画面にも表示します。
3. ノードを接続すると、Effort センサーの読み値が出力されます。

![Effort センサーの OmniGraph](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_full_tut_gui_effort_sensor_omnigraph.png)

!!! note
    期待どおりの読み値を得るには、関節を正しい軸に設定してください。

## まとめ

このチュートリアルでは、次の内容を学びました。

- Effort センサーが回転関節ではトルク、直動関節では力の大きさを測定すること
- `EffortSensor` ラッパークラスでの作成とパラメータ変更
- `get_sensor_reading()` とカスタム補間関数による読み取り
- OmniGraph での Effort センサーの扱い方

## 次のステップ

- [IMU センサー](12_imu_sensor.md) で、加速度・角速度の取得を学びます。
