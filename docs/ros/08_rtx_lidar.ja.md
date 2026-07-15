---
title: RTX Lidar センサー
---

# RTX Lidar センサー

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- **RTX Lidar センサー**の概要と作成方法
- Lidar データを **LaserScan / PointCloud2** メッセージとして ROS 2 に配信する方法
- メニューショートカットによる Lidar パブリッシャの自動生成
- **複数センサー**を RViz2 でまとめて可視化する方法

## はじめに

### 前提条件

- [チュートリアル 5: ROS 2 カメラ](05_camera.md)を完了していること
- Isaac Sim の起動前に `FASTRTPS_DEFAULT_PROFILES_FILE` 環境変数が設定され、ROS 2 ブリッジが有効であること（[セットアップページ](00_setup.md)参照）
- [チュートリアル 1: URDF インポート: Turtlebot](01_urdf_import_turtlebot.md) を完了し、Turtlebot が読み込まれて動き回れる状態であること
- （オプション）RTX Lidar の内部動作について、公式センサードキュメントの Overview と RTX Sensor Annotators に目を通しておくこと

!!! note "RTX Lidar とは"
    RTX Lidar は、RTX GPU の**レイトレーシング**を使って Lidar のビームをシミュレートするセンサーです。**回転式（Rotating）**と**ソリッドステート（Solid State）**の両方の構成を JSON 設定ファイルでサポートしており、実在メーカーの機種別プロファイルも用意されています。各 RTX センサーは、正しくシミュレートするためにそれぞれ専用のレンダープロダクト（ビューポート）にアタッチされます。

!!! warning "シミュレーション中のウィンドウのドッキング操作に注意"
    RTX Lidar のシミュレーション実行中に Isaac Sim UI のウィンドウをドッキングし直すと、クラッシュする可能性が高いです。ウィンドウを動かす場合は、先にシミュレーションを一時停止してください。

!!! warning "Windows / WSL での RViz2"
    Windows 10 / 11 では、マシンの構成によって RViz2 が正しく開かないことがあります。また、**帯域を大きく使うトピック（ポイントクラウドなど）は WSL 内の RViz2 で可視化できない場合があります**。

### 所要時間

約 20〜30 分

## ステップ 1：RTX Lidar を Turtlebot に追加する

2D と 3D の 2 つの Lidar センサーを追加します。

1. **2D Lidar** を追加します：**Create > Sensors > RTX Lidar > NVIDIA > Example Rotary 2D**
2. ロボットの Lidar ユニットと同じ位置に配置するため、Stage パネルで Lidar プリムを `/World/turtlebot3_burger/base_scan` の下にドラッグします。Property タブの **Transform** の変位をすべて 0 にします。Lidar プリムがロボットのスキャンユニットと重なった状態になります。
3. **3D Lidar** も追加します：**Create > Sensors > RTX Lidar > NVIDIA > Example Rotary**
4. 同様に `/World/turtlebot3_burger/base_scan` の下に移動し、Transform を 0 にします。

## ステップ 2：ROS 2 ブリッジのグラフを構築する

**Window > Graph Editors > Action Graph** を開き、次のノードを追加・接続します（オプション：グラフを `/World/turtlebot3_burger/base_scan` の下に移動できます。グラフの配置場所は後のチュートリアルで扱う「自動ネームスペース生成」に関係します）：

| ノード | 設定・役割 |
|---|---|
| **On Playback Tick** | Play 後に他のノードをトリガーする |
| **ROS2 Context** | Domain ID（既定 0、または `ROS_DOMAIN_ID` 環境変数）でコンテキストを作成 |
| **Isaac Run One Simulation Frame** | レンダープロダクト作成パイプラインを開始時に 1 回だけ実行（パフォーマンスのため） |
| **Isaac Create Render Product**（1 つ目） | **cameraPrim** にステップ 1 で作成した **2D Lidar** を指定 |
| **Isaac Create Render Product**（2 つ目） | **cameraPrim** に **3D Lidar** を指定 |
| **ROS2 RTX Lidar Helper**（1 つ目） | LaserScan メッセージの配信を担当。入力の render product は 1 つ目の Create Render Product の出力。**frameId** を `base_scan` に設定 |
| **ROS2 RTX Lidar Helper**（2 つ目） | **type** を `point_cloud`、**topicName** を `point_cloud` に変更。入力は 2 つ目の Create Render Product の出力。**frameId** は `base_scan` |

![RTX Lidar グラフ](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_ros_tut_gui_rtx_lidar_graph.png)

!!! note "LaserScan はフルスキャン完了時にのみ配信される"
    RTX Lidar Helper の type が `laser_scan` の場合、LaserScan メッセージは RTX Lidar が**フルスキャンを完了したときにのみ**配信されます。回転式ならフル 360°、ソリッドステートならプロファイルで設定された全方位角のスキャンです。

    回転レートとタイムステップによっては、フルスキャンに複数フレームかかります。たとえばレンダーステップが 1/60 秒で回転レート 10 Hz の回転式 Lidar なら、フルスキャンに 6 フレームかかるため、LaserScan は **6 フレームに 1 回**配信されます。ソリッドステートは 1 フレームでスキャンが完了するため毎フレーム配信されます。

    PointCloud メッセージは、RTX Lidar Helper の **Publish Full Scan** 設定に応じて、毎フレームまたはフルスキャン蓄積後に配信されます。

グラフを正しく設定したら **Play** を押します。RTX Lidar が LaserScan と PointCloud2 メッセージを配信し始めます。

## ステップ 3：RViz2 で確認する

1. ROS 2 を source したターミナルで `rviz2` を実行します。
2. Isaac Sim 側の Lidar のフレームは `base_scan` に設定したので、RViz の **Fixed Frame** を `base_scan` に変更します。
3. **LaserScan** 表示を追加し、トピックを `/scan` に設定します。
4. **PointCloud2** 表示を追加し、トピックを `/point_cloud` に設定します。

![RViz での Lidar 表示](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_ros_tut_gui_rtx_lidar_graph_rviz.png)

### グラフショートカット

Lidar センサーグラフもメニューからまとめて生成できます：**Tools > Robotics > ROS 2 OmniGraphs > RTX Lidar**

ポップアップで **Graph Path**、**Lidar Prim**、**frameId**、（あれば）**Node Namespace** を指定し、配信したいデータにチェックを入れます。**Add to an existing graph?** にチェックを入れると既存グラフにノードが追加され、既存の tick／コンテキスト／シミュレーション時刻ノードが再利用されます。

## ステップ 4：スタンドアロンスクリプトで実行する

GUI を使わずにスクリプトから Lidar を作成・配信することもできます。

1. ROS 2 環境を source した新しいターミナルで、Lidar ポイントクラウド表示用の設定済み RViz を起動します（`<ros2_ws>` は `humble_ws` などに読み替えてください）：

    ```bash
    rviz2 -d <ros2_ws>/src/isaac_tutorials/rviz2/rtx_lidar.rviz
    ```

2. サンプルスクリプトを実行します：

    ```bash
    ./python.sh standalone_examples/api/isaacsim.ros2.bridge/rtx_lidar.py
    ```

3. シーンの読み込みが終わると、回転式 Lidar センサーのポイントクラウドが表示されることを確認します。

### スクリプトのポイント

**3D RTX Lidar の作成** — `config` に JSON プロファイル名を指定します：

```python
_, sensor = omni.kit.commands.execute(
    "IsaacSensorCreateRtxLidar",
    path="/sensor",
    parent=None,
    config="Example_Rotary",
    translation=(0, 0, 1.0),
    orientation=Gf.Quatd(1.0, 0.0, 0.0, 0.0),
)
```

汎用プロファイルは `extsbuild/omni.sensors.nv.common/data/lidar/` に `Example_Rotary.json` と `Example_Solid_State.json` の 2 つが用意されています（メーカー・機種別プロファイルもあります）。ソリッドステート構成に切り替えるには `config="Example_Solid_State"` に置き換えるだけです。

**レンダープロダクトの作成とセンサーのアタッチ**：

```python
hydra_texture = rep.create.render_product(sensor.GetPath(), [1, 1], name="Isaac")
```

**ポイントクラウドを ROS に配信する後処理パイプラインの作成**：

```python
writer = rep.writers.get("RtxLidar" + "ROS2PublishPointCloud")
writer.initialize(topicName="point_cloud", frameId="base_scan")
writer.attach([hydra_texture])
```

**2D RTX Lidar（LaserScan）** も同様です：

```python
_, sensor_2D = omni.kit.commands.execute(
    "IsaacSensorCreateRtxLidar",
    path="/sensor_2D",
    parent=None,
    config="Example_Rotary_2D",
    translation=(0, 0, 1.0),
    orientation=Gf.Quatd(1.0, 0.0, 0.0, 0.0),
)

hydra_texture_2D = rep.create.render_product(sensor_2D.GetPath(), [1, 1], name="Isaac")

writer = rep.writers.get("RtxLidar" + "ROS2PublishLaserScan")
writer.initialize(topicName="scan", frameId="base_scan")
writer.attach([hydra_texture_2D])
```

## ステップ 5：複数センサーを RViz2 でまとめて表示する

複数のセンサーを RViz2 で同時に表示するには、すべてのメッセージのタイムスタンプが正しく同期されている必要があります。ポイントは 3 つです。

**1. シミュレーションタイムスタンプ** — すべてのパブリッシャノードのタイムスタンプには **Isaac Read Simulation Time** ノードの出力を使います。

**2. ROS 2 clock** — シミュレーション時刻を `/clock` トピックに配信します。グラフは[チュートリアル 3: ROS 2 Clock](03_clock.md) のとおりです。

**3. frameId と topicName の命名規約** — RViz がすべてのセンサーと TF ツリーを一度に認識できるよう、次の規約に従います。実例は Content ブラウザの **Isaac Sim > Samples > ROS2 > Scenario > turtlebot_tutorial.usd** で確認できます：

| ソース | frameId | nodeNamespace | topicName | type |
|---|---|---|---|---|
| カメラ RGB | (デバイス名)\_(データ種別) | (デバイス名)/(データ種別) | image_raw | rgb |
| カメラ深度 | (デバイス名)\_(データ種別) | (デバイス名)/(データ種別) | image_rect_raw | depth |
| Lidar | base_scan | — | scan | laser_scan |
| Lidar | base_scan | — | point_cloud | point_cloud |
| TF | — | — | tf | tf |

シミュレーションを再生した状態で、設定済みの RViz を開きます：

```bash
ros2 run rviz2 rviz2 -d <ros2_ws>/src/isaac_tutorials/rviz2/camera_lidar.rviz
```

RViz ウィンドウの読み込みが終わったら、左側の **Display** パネルで各センサーストリームの表示を切り替えられます。

![複数センサーの RViz 表示](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_ros_tut_external_rtx_lidar_multisensor_rviz2.png)

!!! warning "RViz2 の use_sim_time を忘れずに"
    RViz2 ノードを起動したら、`use_sim_time` パラメータを true に設定してください。RViz2 が Lidar のデータ点の位置を補間する際などに、シミュレーションデータと同期するために必要です：

    ```bash
    ros2 param set /rviz use_sim_time true
    ```

## まとめ

このチュートリアルでは、RTX Lidar センサーと ROS 2 の連携を扱いました：

1. **RTX Lidar センサー**（2D / 3D）の追加
2. **RTX Lidar Helper ノード**による LaserScan / PointCloud2 の配信と、フルスキャンと配信周期の関係
3. スタンドアロンスクリプトによる Lidar の作成と配信
4. **複数センサー**のタイムスタンプ同期と RViz2 での一括可視化

## 次のステップ

- [チュートリアル 9: ROS 2 Transform ツリーとオドメトリ](09_tf.md) - グローバル・相対 Transform を TF ツリーに追加する方法を学びます。

### さらに学ぶには

- RTX Lidar の内部動作は、公式センサードキュメントの Overview と RTX Sensor Annotators を参照してください。
