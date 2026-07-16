---
title: ROS 2 パブリッシュレートの設定
---

# ROS 2 パブリッシュレートの設定

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- Isaac Sim の**シミュレーションフレームレート**の設定方法（2 通り）
- 複数の ROS 2 パブリッシャに**それぞれ異なる配信レート**を同時に設定する方法

## はじめに

### 前提条件

- [チュートリアル 1: URDF インポート: Turtlebot](01_urdf_import_turtlebot.md)、[チュートリアル 5: ROS 2 カメラ](05_camera.md)、[チュートリアル 8: RTX Lidar センサー](08_rtx_lidar.md)、[チュートリアル 9: ROS 2 Transform ツリーとオドメトリ](09_tf.md)を完了していること
- [ROS 2 セットアップ](00_setup.md)が完了しており、Isaac Sim 起動前に必要な環境変数が設定され、ROS 2 エクステンションが有効であること

### 所要時間

約 20〜30 分

### 概要

Action Graph は**シミュレーションの毎フレーム tick される**ため、OmniGraph ノードの実行レートはシミュレーションレートの**約数（整数分の 1）**に縛られます。実機では IMU は 200 Hz、カメラは 30 Hz、Lidar は 10 Hz…というように、センサーごとに配信レートが異なるのが普通です。このチュートリアルでは、この「センサーごとのレート設定」をシミュレーションレートの分周として構成する方法を学びます。

## ステップ 1：Isaac Simulation Gate ノードでレートを制御する

**Isaac Simulation Gate** ノードは、指定したフレーム数ごとに 1 回だけ下流のノードを tick させるノードです。ここでは IMU パブリッシャをこのノードと組み合わせてセットアップします。

1. Content ブラウザから **Isaac Sim > Samples > ROS2 > Scenario > turtlebot_tutorial.usd** を開きます。
2. `/World/turtlebot3_burger/base_link/imu_link` プリムを選択した状態で、**Create > Sensors > Imu Sensor** で IMU センサーを作成します。IMU センサーが `imu_link` プリムの下に作成されたことを確認します。
3. `/World/turtlebot3_burger/base_link/imu_link` プリムの下に新しい Action Graph を作成し、`ROS_IMU` と名付けます（グラフの配置場所は後のチュートリアルの「自動ネームスペース生成」に関係します）。プリムを選択した状態で **Window > Graph Editors > Action Graph** から作成してください。
4. Simulation Gate ノードを含む次のグラフを構築します：

    ![IMU パブリッシュレートグラフ](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isaac_tutorial_ros2_publish_rate_imu_graph.png)

5. 各ノードの属性を設定します：

| ノード | 設定 |
|---|---|
| **Isaac Simulation Gate** | **step** を `2` に設定。step が 2 なら下流のノードは **2 フレームに 1 回** tick される |
| **Isaac Read IMU Node** | **imuPrim** に IMU センサープリム `/World/turtlebot3_burger/base_link/imu_link/Imu_Sensor` を追加 |
| **ROS2 Publish Imu** | **frameId** を `imu_link` に設定。[チュートリアル 9](09_tf.md) でセットアップした TF ツリーの `imu_link` フレームと一致させる |

## ステップ 2：SDG パイプライン内のノードのレートを設定する

前のステップでは自分のグラフに Simulation Gate を追加しましたが、カメラや RTX Lidar のセンサーでは、Simulation Gate は **SDG パイプライン内に自動的に構成**されています。個々のパブリッシャの配信レートは、各 **ROS2 Helper ノードの `frameSkipCount` パラメータ**で変更します。

!!! note "frameSkipCount と step の関係"
    `frameSkipCount` は「配信の間に**スキップする**フレーム数」です。`frameSkipCount = 11` なら 11 フレームスキップ → **12 フレームに 1 回**配信され、SDG パイプライン内の Simulation Gate の step には自動的に対応する値が設定されます。

`turtlebot_tutorial.usd` のシーンで次のように設定してみましょう：

1. Lidar の Action Graph `/World/turtlebot3_burger/base_scan/ROS_LidarRTX` を開き、LaserScan 用の **Ros2RTXLidarHelper** ノード（`.../LaserScanPublish`）を選択して、**frameSkipCount** を `11` に設定します（＝12 フレームに 1 回配信）。
2. このチュートリアルではポイントクラウドは不要なので、ポイントクラウド用の Ros2RTXLidarHelper ノード（`.../PointCloudPublish`）の **enabled** のチェックを外して無効化します。
3. カメラの Action Graph `/World/ActionGraph_camera` を開き、2 台目のカメラのレンダープロダクト（`.../isaac_create_render_product_01`）の **enabled** を外して無効化します。
4. RGB 画像用の Camera Helper ノード（`.../ros2_camera_helper`）の **frameSkipCount** を `3` に設定します（＝4 フレームに 1 回配信。SDG パイプラインの Simulation Gate の step は 4 になります）。
5. 深度画像は不要なので、深度用 Camera Helper（`.../ros2_camera_helper_02`）の **enabled** を外します。
6. Camera Info 用の Camera Info Helper ノード（`.../ros2_camera_info_helper`）の **frameSkipCount** を `5` に設定します（＝6 フレームに 1 回配信）。

## ステップ 3：シミュレーションフレームレートを設定する

ここまでで各ノードの分周比を設定しましたが、すべての Action Graph はシミュレーションレートを上限として動作するため、大元の**シミュレーションフレームレート**も制御できると便利です。**Window > Script Editor** から Python で設定します。方法は 2 つあります：

**方法 1：carb 設定を変更する** — carb は Omniverse アプリの基盤フレームワークで、`/app/...` のようなキーでアプリ全体の設定を読み書きできます。ここではシミュレーションのタイムラインの実行レートを設定します。**On Playback Tick** ノード由来の時間に影響します。シーンを再生した後に実行してください：

```python
# carb 設定の変更。停止して再度再生すると設定は保持されない
import carb
physics_rate = 60  # fps
carb_settings = carb.settings.get_settings()
carb.settings.get_settings().set_bool("/app/runLoops/main/rateLimitEnabled", True)
carb.settings.get_settings().set_int("/app/runLoops/main/rateLimitFrequency", int(physics_rate))
carb.settings.get_settings().set_int("/persistent/simulation/minFrameRate", int(physics_rate))
```

**方法 2：SetTimeCodesPerSecond と set_target_framerate を変更する** — 物理の実行レートを設定します。**IsaacReadSimulationTime** ノード由来の時間に影響します：

```python
# ステージ読み込み後に実行すること。SetTimeCodesPerSecond と set_target_framerate の
# 設定時はタイムラインを停止しておくこと。停止→再生をまたいで設定が保持される
import omni
physics_rate = 60  # fps

timeline = omni.timeline.get_timeline_interface()
stage = omni.usd.get_context().get_stage()
timeline.stop()

stage.SetTimeCodesPerSecond(physics_rate)
timeline.set_target_framerate(physics_rate)

timeline.play()
```

!!! note "Time Codes Per Second はシーン再生前に 1 回だけ設定可能"
    Time Codes Per Second は、シーンを再生する前に 1 回しか設定できません。値を変更したい場合は、先にシーンをリロードしてください。

スクリプトを実行してシミュレーションレートへの影響を確認します。FPS の表示は、ビューポートの表示メニュー（目のアイコン）> **Heads Up Display > FPS** で有効化できます。`physics_rate` を別の値に変えて FPS の読みを確認してみてください。

!!! warning "設定できるのは「目標」フレームレート"
    どちらの方法も設定するのはシミュレーションの**目標**フレームレートです。実際のフレームレートはマシンの性能に依存します。

## ステップ 4：ROS 2 の配信レートを確認する

1. **Play** を押してシミュレーションを開始します。
2. 各 ROS トピックの配信レートをコマンドで確認します：

    ```bash
    ros2 topic hz /topic_name
    ```

ここまでの設定どおりなら、各トピックのレートは最大シミュレーション FPS（既定 60 Hz）の分周になっているはずです：

| トピック | 期待レート |
|---|---|
| `/clock` | シミュレーション FPS と同じ（約 60 Hz） |
| `/imu` | FPS / 2（約 30 Hz） |
| `/scan` | FPS / 12（約 5 Hz） |
| `/camera_1/rgb/image_raw` | FPS / 4（約 15 Hz） |
| `/camera_1/rgb/camera_info` | FPS / 6（約 10 Hz） |

配信レートは推定値です。高性能なマシンほど、最大 FPS は設定した `physics_rate` に近づきます。

このチュートリアルのすべての設定を済ませたシーンは、Content ブラウザの **Isaac Sim > Samples > ROS2 > Scenario > turtlebot_tutorial_multi_sensor_publish_rates.usd** にあります（開いた後、ステップ 3 の手順で目標シミュレーションレートを設定してください）。

!!! tip "画像トピックだけ想定より遅い場合"
    `/camera_1/rgb/image_raw` の配信が想定より遅い場合、画像メッセージのサイズが大きく、ネットワークや DDS のキュー管理がボトルネックになっている可能性があります。画像パブリッシャに接続されているレンダープロダクトノード（`/World/ActionGraph_camera/isaac_create_render_product`）の解像度を下げてから再生し直すと改善することがあります。

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

1. **Isaac Simulation Gate** ノードと **frameSkipCount** による、パブリッシャごとの配信レート設定
2. Python による**シミュレーションフレームレート**の設定（carb 設定／TimeCodesPerSecond の 2 通り）
3. `ros2 topic hz` による配信レートの確認

## 次のステップ

- [チュートリアル 11: ROS 2 Quality of Service（QoS）](11_qos.md) - ROS 2 OmniGraph ノードの QoS プロファイル設定を学びます。
