---
title: ROS 2 パブリッシュレートの設定
---

# ROS 2 パブリッシュレートの設定

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- Isaac Sim の**シミュレーションレート**の設定方法
- センサーの種類（IMU・RTX Lidar・カメラ）ごとに**異なる ROS 2 配信レート**を同時に設定する方法

## はじめに

### 前提条件

- [チュートリアル 1: URDF インポート: Turtlebot](01_urdf_import_turtlebot.md)、[チュートリアル 5: ROS 2 カメラ](05_camera.md)、[チュートリアル 8: RTX Lidar センサー](08_rtx_lidar.md)、[チュートリアル 9: ROS 2 Transform ツリーとオドメトリ](09_tf.md)を完了していること
- [ROS 2 セットアップ](00_setup.md)が完了しており、Isaac Sim 起動前に必要な環境変数が設定され、ROS 2 エクステンションが有効であること

### 所要時間

約 20〜30 分

### 概要

Action Graph は**シミュレーションの毎フレーム tick される**ため、OmniGraph ノードの実行レートはシミュレーションレートに縛られます。実機では IMU は 200 Hz、カメラは 30 Hz、Lidar は 10 Hz…というように、センサーごとに配信レートが異なるのが普通です。このチュートリアルでは、センサーごとに配信レートを設定する 2 つの方法を学びます：

- **非 RTX センサー（IMU など）**：**Isaac Simulation Gate** ノードでフレームを分周する
- **RTX センサー（カメラ・RTX Lidar）**：センサープリムの **`omni:sensor:tickRate`** 属性でレートを直接指定する（[マルチティックレンダリング](https://docs.isaacsim.omniverse.nvidia.com/latest/sensors/isaacsim_sensors_multitick_rendering.html)の仕組みによりシミュレーションレートから独立してスケジュールされます）

## ステップ 1：非 RTX センサー — Isaac Simulation Gate ノード

RTX レンダリングに依存しないセンサー（IMU など）は、**Isaac Simulation Gate** ノードでシミュレーションレートと異なるレートを設定できます。このノードは、指定したフレーム数ごとに 1 回だけ下流のノードを tick させます。ここでは IMU パブリッシャをこのノードと組み合わせてセットアップします。

1. Content ブラウザから **Isaac Sim > Samples > ROS2 > Scenario > turtlebot_tutorial.usd** を開きます。
2. `imu_link` プリムの下に IMU センサーを作成します。IMU センサーの追加方法は 2 通りあり、作成される場所が異なります：
    - **右クリックメニュー（推奨）**：Stage パネルで `/World/turtlebot3_burger_processed/Geometry/base_footprint/base_link/imu_link` プリムを右クリックし、コンテキストメニューから **Create > Isaac > Sensors > Imu Sensor** を選択します。選択中の `imu_link` プリムの直下にセンサーが作成されます。
    - **メニューバー**：画面上部の **Create > Sensors > Imu Sensor** から作成すると、センサーは**ステージのルート**に作成されます。この方法を使った場合は、Stage パネルで作成されたセンサープリムを `imu_link` の下にドラッグして、以降の手順と階層を一致させてください。

    いずれの方法でも、先に進む前に IMU センサーが `imu_link` プリムの下にあることを確認します。

3. `/World/turtlebot3_burger_processed/Geometry/base_footprint/base_link/imu_link` プリムの下に新しい Action Graph を作成し、`ROS_IMU` と名付けます（グラフの配置場所は後のチュートリアルの「自動ネームスペース生成」に関係します）。プリムを選択した状態で **Window > Graph Editors > Action Graph** から作成してください。
4. Simulation Gate ノードを含む次のグラフを構築します：

    ![IMU パブリッシュレートグラフ](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isaac_tutorial_ros2_publish_rate_imu_graph.png)

5. 各ノードの属性を設定します：

| ノード | 設定 |
|---|---|
| **Isaac Simulation Gate** | **step** を `2` に設定。step が 2 なら下流のノードは **2 フレームに 1 回** tick される |
| **Isaac Read IMU Node** | **imuPrim** に IMU センサープリム `/World/turtlebot3_burger_processed/Geometry/base_footprint/base_link/imu_link/Imu_Sensor` を追加 |
| **ROS2 Publish Imu** | **frameId** を `imu_link` に設定。[チュートリアル 9](09_tf.md) でセットアップした TF ツリーの `imu_link` フレームと一致させる |

## ステップ 2：RTX センサー — omni:sensor:tickRate 属性

カメラと RTX Lidar は、センサープリムの **`omni:sensor:tickRate`** 属性でシミュレーションレートと異なる配信レートを設定できます（詳細は公式の [Configuring Per-Sensor Tick Rates](https://docs.isaacsim.omniverse.nvidia.com/latest/sensors/isaacsim_sensors_multitick_rendering.html#isaac-sim-sensors-multitick-configuring-per-sensor-tick-rates) を参照）。

!!! warning "frameSkipCount は非推奨（deprecated）になりました"
    以前の Isaac Sim では ROS2 Helper ノードの `frameSkipCount` パラメータでセンサーの配信レートを制御していましたが、この方法は**非推奨**になりました。`frameSkipCount` に 0 以外の値が設定され、かつ対応するセンサープリムの `omni:sensor:tickRate` にも 0 以外の値が設定されていると、両者の周期が一致せず配信頻度が想定外になることがあります。移行の詳細は公式の [Configuring Per-Sensor Tick Rates](https://docs.isaacsim.omniverse.nvidia.com/latest/sensors/isaacsim_sensors_multitick_rendering.html#isaac-sim-sensors-multitick-configuring-per-sensor-tick-rates) と [Multi-Tick Rendering](https://docs.isaacsim.omniverse.nvidia.com/latest/sensors/isaacsim_sensors_multitick_rendering.html) を参照してください。

`turtlebot_tutorial.usd` のシーンで次のように設定してみましょう：

1. 2D Lidar プリム `/World/turtlebot3_burger_processed/Geometry/base_footprint/base_link/base_scan/Example_Rotary_2D` を選択します（`.../base_scan/ROS_LidarRTX/LaserScanPublish` に接続された Isaac Create Render Product ノードの **cameraPrim** に指定されている OmniLidar です）。Property タブで **omni:sensor:tickRate** を `5` に設定します。LaserScan は 1 tick につき 1 回配信されるため、配信レートは **R_lidar = 5 Hz** になります（シミュレーションレートが 5 Hz 以上である限り、シミュレーションレートから独立します）。
2. あわせて **omni:sensor:Core:scanRateBaseHz** も `5` に設定します。この 2 つの値が等しくないと、Lidar は 1 tick で 1 周分のスキャンを蓄積できず、フレームごとの部分スキャンにフォールバックします（公式の [OmniLidar Tick Rate Must Equal scanRateBaseHz](https://docs.isaacsim.omniverse.nvidia.com/latest/sensors/isaacsim_sensors_multitick_rendering.html#isaac-sim-sensors-multitick-lidar-tickrate-must-match-scanrate) を参照）。同梱の Example_Rotary_2D アセットの既定値は `10` なので、下げる必要があります。
3. このチュートリアルではポイントクラウドは不要なので、ポイントクラウド用の Ros2RTXLidarHelper ノード（`.../base_scan/ROS_LidarRTX/PointCloudPublish`）の **enabled** のチェックを外して無効化します。
4. カメラの Action Graph `/World/ActionGraph_camera` を開き、2 台目のカメラのレンダープロダクト（`.../isaac_create_render_product_01`）の **enabled** を外して無効化します。
5. カメラプリム `/World/Camera_1` を選択します（`/World/ActionGraph_camera/ros2_camera_helper` と `.../ros2_camera_info_helper` の両方に接続された Isaac Create Render Product ノードの **cameraPrim** に指定されている Camera です）。**OmniSensorAPI** スキーマを適用して **omni:sensor:tickRate** を `15` に設定すると、`/camera_1/rgb/image_raw` と `/camera_1/rgb/camera_info` の両方が **R_cam = 15 Hz** で配信されます（シミュレーションレートが 15 Hz 以上である限り独立）。Script Editor（**Window > Script Editor**）から次のスクリプトを実行して、各カメラにスキーマを適用しレートを設定します：

    ```python
    import isaacsim.core.experimental.utils.prim as prim_utils

    # Create > Camera メニューで作成したカメラには OmniSensorAPI スキーマがなく、
    # スキーマを適用するまで omni:sensor:tickRate 属性は使えない。既存の各カメラに
    # スキーマを適用してから、配信レート（Hz）を設定する。
    for path in ("/World/Camera_1", "/World/Camera_2"):
        camera_prim = prim_utils.get_prim_at_path(path)
        camera_prim.ApplyAPI("OmniSensorAPI")
        camera_prim.GetAttribute("omni:sensor:tickRate").Set(15)
    ```

    !!! note "Create > Camera で作ったカメラには omni:sensor:tickRate がない"
        メニューバーの **Create > Camera** で作成したカメラ（[チュートリアル 5](05_camera.md) の手順など）には OmniSensorAPI スキーマがないため、既定では `omni:sensor:tickRate` 属性を持ちません。同梱の `turtlebot_tutorial.usd` では `/World/Camera_1` と `/World/Camera_2` に適用済みです。スキーマの適用後は、Property タブから `omni:sensor:tickRate` を直接編集することもできます。

6. 深度画像は不要なので、深度用 Camera Helper（`.../ros2_camera_helper_02`）の **enabled** を外します。

## ステップ 3：ROS 2 の配信レートを確認する

1. **Play** を押してシミュレーションを開始します。
2. 各 ROS トピックの配信レートをコマンドで確認します：

    ```bash
    ros2 topic hz /topic_name
    ```

トピックは、目標レート（`target_hz`、既定 60 Hz）に対するスケールの仕方が異なる 2 つのグループに分かれます：

| グループ | トピック | 期待レート |
|---|---|---|
| OnPlaybackTick 駆動（アプリ更新にゲート） | `/clock` | `target_hz`（約 60 Hz。アプリ更新 1 回につき 1 メッセージ） |
| 〃 | `/imu` | `target_hz / 2`（約 30 Hz。分母はステップ 1 で設定した Simulation Gate の step） |
| マルチティックスケジュールの RTX センサー | `/scan` | `min(R_lidar, target_hz)` = **5 Hz**（`target_hz` ≥ 5 なら一定） |
| 〃 | `/camera_1/rgb/image_raw` | `min(R_cam, target_hz)` = **15 Hz**（`target_hz` ≥ 15 なら一定） |
| 〃 | `/camera_1/rgb/camera_info` | RGB と同じ（両ヘルパーが同じ Camera プリムの tick レートを共有するため） |

配信レートは推定値です。高性能なマシンほど、最大 FPS は設定した `target_hz`（既定 60 Hz）に近づきます。

このチュートリアルのすべての設定を済ませたシーンは、Content ブラウザの **Isaac Sim > Samples > ROS2 > Scenario > turtlebot_tutorial_multi_sensor_publish_rates.usd** にあります（開いた後、ステップ 4 の手順で目標シミュレーションレートを設定してください）。

!!! tip "画像トピックだけ想定より遅い場合"
    `/camera_1/rgb/image_raw` の配信が想定より遅い場合、画像メッセージのサイズが大きく、ネットワークや DDS のキュー管理がボトルネックになっている可能性があります。画像パブリッシャに接続されているレンダープロダクトノード（`/World/ActionGraph_camera/isaac_create_render_product`）の解像度を下げてから再生し直すと改善することがあります。

## ステップ 4：シミュレーションレートを設定する（応用）

Isaac Sim にはレートに関わるクロックが 3 つあります：**物理シーンのステップレート**（`UsdPhysicsScene.timeStepsPerSecond`）、**タイムラインの 1 tick あたりの dt**（`stage.timeCodesPerSecond` とタイムラインの `targetFramerate` の組み合わせ）、**アプリのランループの tick レート**（`/app/runLoops/main/rateLimitFrequency`）です。リアルタイム再生のためには、この 3 つを同じ値に揃える必要があります。`isaacsim.core.simulation_manager.SimulationManager.setup_simulation()` が物理シーンのステップレートを、`isaacsim.core.rendering_manager.RenderingManager.set_dt()` がタイムラインとランループをまとめて設定するので、**この 2 つをペアで使います**。

!!! warning "Isaac Sim 6.0 の既知の不具合"
    Isaac Sim 6.0 では、物理シーンのステップレートとタイムラインの dt を既定値の 60.0 から変更した後にシミュレーションを再生すると、フル UI アプリが致命的にクラッシュする既知の問題があります。将来のリリースで修正予定です。

次のスニペットを、Isaac Sim ディレクトリ内のスタンドアロン Python スクリプト（例：`test_ros2_publish_rates.py`）として保存します：

```python
from isaacsim import SimulationApp

app = SimulationApp({"headless": False})

import carb
import isaacsim.core.experimental.utils.app as app_utils
import isaacsim.core.experimental.utils.stage as stage_utils
from isaacsim.core.rendering_manager import RenderingManager
from isaacsim.core.simulation_manager import SimulationManager
from isaacsim.storage.native import get_assets_root_path

app_utils.enable_extension("isaacsim.ros2.bridge")
app.update()

assets_root_path = get_assets_root_path()
stage_utils.open_stage(
    assets_root_path + "/Isaac/Samples/ROS2/Scenario/turtlebot_tutorial_multi_sensor_publish_rates.usd"
)

# Play の前に、物理・タイムライン・ランループのレートを揃えて設定する。
# `/app/runLoops/main/rateLimitEnabled` が true であることが前提（フル UI 版
# Isaac Sim では既定で true。`isaacsim.exp.base.kit` / スタンドアロン Python では
# false）。false の場合は先に True に設定しないとループが無制限に tick される。
# 効果の一覧は `RenderingManager.set_dt` の docstring を参照。
target_hz = 60
SimulationManager.setup_simulation(dt=1.0 / target_hz)
RenderingManager.set_dt(1.0 / target_hz)

app_utils.play()

while app.is_running():
    app.update()

app_utils.stop()
app.close()
```

次のコマンドで実行します：

```bash
./python.sh test_ros2_publish_rates.py \
--/app/runLoops/main/rateLimitEnabled=true \
--/app/runLoops/main/rateLimitFrequency=60 \
--/app/runLoops/main/manualModeEnabled=true
```

これでシミュレーションは実時間 1 秒あたり 60 フレーム（FPS）で動作します。ROS 2 をセットアップした別のターミナルで `ros2 topic hz /topic_name` を実行して配信レートを確認してください。

スクリプト内の `target_hz` を変更して再実行すると、トピックのゲート機構の違いによってスケールの仕方が変わります：

- **OnPlaybackTick 駆動のヘルパー**（`/clock` パブリッシャと、Simulation Gate を介した IMU グラフ）はアプリ更新ごとに 1 回発火するため、実時間レートは `target_hz` に比例します（IMU は gate の step で割った値）。
- **マルチティックスケジュールの RTX センサー**（`/scan`、`/camera_1/rgb/image_raw`、`/camera_1/rgb/camera_info`）は、レンダラーのシミュレーション時間が `1 / omni:sensor:tickRate` 進むごとに発火するため、`target_hz` に依存せず設定した Hz を維持します。ただし `target_hz` が設定 tick レートを下回ると、アプリ更新 1 回につき 1 tick に頭打ちになります。

このチュートリアルの設定（Lidar の `omni:sensor:tickRate` = R_lidar = 5、カメラの `omni:sensor:tickRate` = R_cam = 15、IMU の gate step = 2）での実時間配信レートは次のとおりです：

| target_hz (Hz) | `/clock` | `/imu` | `/scan` | `/camera_1/rgb/image_raw`, `.../camera_info` |
|---|---|---|---|---|
| 30 | 30 | 15 | 5 | 15 |
| 60 | 60 | 30 | 5 | 15 |
| 120 | 120 | 60 | 5 | 15 |
| 240 | 240 | 120 | 5 | 15 |
| 10 | 10 | 5 | 5 | 10（target_hz で頭打ち） |

一般式は次のとおりです：

```text
clock_hz   = target_hz
imu_hz     = target_hz / k_imu                 # k_imu = Isaac Simulation Gate の step（ここでは 2）
scan_hz    = min(R_lidar, target_hz)
camera_hz  = min(R_cam, target_hz)
```

!!! warning "設定できるのは「目標」フレームレート"
    実際のフレームレートはマシンの性能に依存します。レンダラーが `target_hz` を維持できない場合、センサーの配信レートも比例して低下します。3 つのクロックの関係と、同期が崩れたときの挙動（スローモーション・早送り）については公式の [Architecture: Timeline, Physics, and the Renderer](https://docs.isaacsim.omniverse.nvidia.com/latest/sensors/isaacsim_sensors_multitick_rendering.html#isaac-sim-sensors-multitick-clock-relationships) を参照してください。

!!! note "Lidar の tickRate を変えるときは scanRateBaseHz も揃える"
    Lidar プリムの `omni:sensor:tickRate` を変更する場合は、`omni:sensor:Core:scanRateBaseHz` も同じ値に変更する必要があります。2 つの値が等しくないと、Lidar は 1 tick で 1 周分のスキャンを蓄積せず、毎フレーム部分スキャンを出力してしまいます。

### トラブルシューティング

目標シミュレーションフレームレートと大きく異なる配信レートになる場合：

- 永続化されたフレームレート設定をクリアするため、Isaac Sim を工場出荷設定で起動してみてください：

    ```bash
    ./isaac-sim.sh --reset-user
    ```

- CPU 使用率を確認してボトルネックを特定してください。Isaac Sim の使用率が非常に高い場合は、Fabric（USD のシーンデータを高速に読み書きするための Omniverse のランタイムデータ層。シーン更新のオーバーヘッドを減らせます）を有効にした起動を試せます：

    ```bash
    ./isaac-sim.fabric.sh --reset-user
    ```

    ただしこのコマンドは実験的なもので、Isaac Sim の全機能はサポートされていません（全体的な性能は向上する場合があります）。`--reset-user` フラグが必要なのは Fabric での初回起動時のみです。

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. **Isaac Simulation Gate** ノードによる非 RTX センサー（IMU）の配信レート設定
2. センサープリムの **`omni:sensor:tickRate`** 属性による RTX センサー（Lidar・カメラ）の配信レート設定
3. `SimulationManager.setup_simulation` と `RenderingManager.set_dt` による一貫したシミュレーションレートの設定と、`ros2 topic hz` による確認

## 次のステップ

- [チュートリアル 11: ROS 2 Quality of Service（QoS）](11_qos.md) - ROS 2 OmniGraph ノードの QoS プロファイル設定を学びます。
