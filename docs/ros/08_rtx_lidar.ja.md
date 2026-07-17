---
title: RTX Lidar センサー
---

# RTX Lidar センサー

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- **RTX Lidar センサー**の概要と作成方法
- Lidar データを **LaserScan / PointCloud2** メッセージとして ROS 2 に配信する方法
- メニューショートカットによる Lidar パブリッシャの自動生成
- （オプション）強度・Object ID・タイムスタンプなどの **RTX Lidar メタデータ**を PointCloud2 に含める方法

## はじめに

### 前提条件

- [チュートリアル 5: ROS 2 カメラ](05_camera.md)を完了していること
- Isaac Sim の起動前に `FASTRTPS_DEFAULT_PROFILES_FILE` 環境変数が設定され、ROS 2 ブリッジが有効であること（[セットアップページ](00_setup.md)参照）
- [チュートリアル 1: URDF インポート: Turtlebot](01_urdf_import_turtlebot.md) を完了し、Turtlebot が読み込まれて動き回れる状態であること
- 本チュートリアルのオプション部分（メタデータの購読）には、[IsaacSim-ros_workspaces](https://github.com/isaac-sim/IsaacSim-ros_workspaces) リポジトリの `isaac_tutorials` ROS 2 パッケージが必要です。[セットアップページ](00_setup.md)のワークスペースのビルドを完了しておいてください
- （オプション）RTX Lidar の内部動作について、公式センサードキュメントの Overview と RTX Sensor Annotators に目を通しておくこと

!!! note "RTX Lidar とは"
    RTX Lidar は、RTX GPU の**レイトレーシング**を使って Lidar のビームをシミュレートするセンサーです。**回転式（Rotating）**と**ソリッドステート（Solid State）**の両方の構成をサポートしており、実在メーカーの機種別プロファイルも用意されています。各 RTX センサーは、正しくシミュレートするためにそれぞれ専用のレンダープロダクト（ビューポート）にアタッチされます。

!!! note "配信レートは omni:sensor:tickRate で決まります（6.0 での変更点）"
    Isaac Sim 6.0 では、RTX Lidar の配信レートはヘルパーノードの `frameSkipCount` ではなく、**OmniLidar プリムの `omni:sensor:tickRate` 属性**で制御します。OmniLidar プリムでは、スキャンの蓄積が正しく動作するように **`omni:sensor:tickRate` を `omni:sensor:Core:scanRateBaseHz` と同じ値**にする必要があります。詳細は公式の [Multi-Tick Rendering](https://docs.isaacsim.omniverse.nvidia.com/latest/sensors/isaacsim_sensors_multitick_rendering.html) を参照してください。

!!! warning "シミュレーション中のウィンドウのドッキング操作に注意"
    RTX Lidar のシミュレーション実行中に Isaac Sim UI のウィンドウをドッキングし直すと、クラッシュする可能性が高いです。ウィンドウを動かす場合は、先にシミュレーションを一時停止してください。

!!! warning "Windows / WSL での RViz2"
    Windows 11 では、マシンの構成によって RViz2 が正しく開かないことがあります。また、**帯域を大きく使うトピック（ポイントクラウドなど）は WSL 内の RViz2 で可視化できない場合があります**。

### 所要時間

約 20〜30 分

## ステップ 1：RTX Lidar を Turtlebot に追加する

2D と 3D の 2 つの Lidar センサーを追加します。

1. **2D Lidar** を追加します：**Create > Sensors > RTX Lidar > NVIDIA > Example Rotary 2D**
2. ロボットの Lidar ユニットと同じ位置に配置するため、Stage パネルで Lidar プリムを `/World/tb3_burger_processed/Geometry/base_footprint/base_link/base_scan` の下にドラッグします。Property タブの **Transform** の変位をすべて 0 にします。Lidar プリムがロボットのスキャンユニットと重なった状態になります。
3. **3D Lidar** も追加します：**Create > Sensors > RTX Lidar > NVIDIA > Example Rotary**
4. 同様に `/World/tb3_burger_processed/Geometry/base_footprint/base_link/base_scan` の下に移動し、Transform を 0 にします。

## ステップ 2：ROS 2 ブリッジのグラフを構築する

Stage パネルで `/World/tb3_burger_processed/Geometry/base_footprint/base_link/base_scan` を選択します。Lidar のパブリッシャグラフは特定のセンサーに紐づくため、ロボットのルートではなく**センサープリムの隣**に置くのが適切です（グラフの配置場所は[チュートリアル 15: 自動 ROS 2 ネームスペース生成](15_auto_namespace.md)にも関係します）。

**Window > Graph Editors > Action Graph** を開き、**New Action Graph** をクリックしてグラフ名を `ROS_LidarRTX` にします。次のノードを追加・接続します：

| ノード | 設定・役割 |
|---|---|
| **On Playback Tick** | Play 後に他のノードをトリガーする |
| **ROS2 Context** | Domain ID（既定 0、または `ROS_DOMAIN_ID` 環境変数）でコンテキストを作成 |
| **Isaac Run One Simulation Frame** | レンダープロダクト作成パイプラインを開始時に 1 回だけ実行（パフォーマンスのため） |
| **Isaac Create Render Product**（1 つ目） | **cameraPrim** にステップ 1 で作成した **2D Lidar** を指定 |
| **Isaac Create Render Product**（2 つ目） | **cameraPrim** に **3D Lidar** を指定 |
| **ROS2 RTX Lidar Helper**（1 つ目） | LaserScan メッセージの配信を担当。入力の render product は 1 つ目の Create Render Product の出力。**topicName** を `scan`、**frameId** を `base_scan` に設定 |
| **ROS2 RTX Lidar Helper**（2 つ目） | **type** を `point_cloud`、**topicName** を `point_cloud`、**frameId** を `base_scan` に設定し、**Publish Full Scan** にチェック。入力は 2 つ目の Create Render Product の出力 |

![RTX Lidar グラフ](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_5.0_ros_tut_gui_rtx_lidar_graph.png)

!!! note "LaserScan はフルスキャン完了時にのみ配信される"
    RTX Lidar Helper の type が `laser_scan` の場合、LaserScan メッセージは RTX Lidar が**フルスキャンを完了したときにのみ**配信されます。回転式ならフル 360°、ソリッドステートならプロファイルで設定された全方位角のスキャンです。

    回転レートとタイムステップによっては、フルスキャンに複数フレームかかります。たとえばレンダーステップが 1/60 秒で回転レート 10 Hz の回転式 Lidar なら、フルスキャンに 6 フレームかかるため、LaserScan は **6 フレームに 1 回**配信されます。ソリッドステートは 1 フレームでスキャンが完了するため毎フレーム配信されます。

    PointCloud メッセージは、RTX Lidar Helper の **Publish Full Scan** 設定に応じて、毎フレームまたはフルスキャン蓄積後に配信されます。

グラフを正しく設定したら **Play** を押します。RTX Lidar が LaserScan と PointCloud2 メッセージを配信していることを確認します。

## ステップ 3：RViz2 で確認する

1. ROS 2 を source したターミナルで `rviz2` を実行します。
2. Isaac Sim 側の Lidar のフレームは `base_scan` に設定したので、RViz の **Fixed Frame** を `base_scan` に変更します。
3. **LaserScan** 表示を追加し、トピックを `/scan` に設定します。
4. **PointCloud2** 表示を追加し、トピックを `/point_cloud` に設定します。

![RViz での Lidar 表示](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_5.0_ros_tut_gui_rtx_lidar_graph_rviz.png)

### グラフショートカット

Lidar センサーグラフもメニューからまとめて生成できます：**Tools > Robotics > ROS 2 OmniGraphs > RTX Lidar**

ポップアップで **Graph Path**、**Lidar Prim**、**frameId**、（あれば）**Node Namespace** を指定し、配信したいデータにチェックを入れます。**Add to an existing graph?** にチェックを入れると既存グラフにノードが追加され、既存の tick／コンテキスト／シミュレーション時刻ノードが再利用されます。

## ステップ 4：スタンドアロンスクリプトで実行する

GUI を使わずにスクリプトから Lidar を作成・配信することもできます。

1. ROS 2 環境を source した新しいターミナルで、Lidar ポイントクラウド表示用の設定済み RViz を起動します（`<ros2_ws>` は `jazzy_ws` などに読み替えてください）：

    ```bash
    rviz2 -d <ros2_ws>/src/isaac_tutorials/rviz2/rtx_lidar.rviz
    ```

2. サンプルスクリプトを実行します：

    ```bash
    ./python.sh standalone_examples/api/isaacsim.ros2.bridge/rtx_lidar.py
    ```

3. シーンの読み込みが終わると、回転式 Lidar センサーのポイントクラウドが表示されることを確認します。

### スクリプトのポイント

このサンプルは、6.0 の **`isaacsim.sensors.experimental.rtx`** Python API を使って 2D / 3D の RTX Lidar を作成します。

**3D RTX Lidar の作成** — `config` に構成名を指定します：

```python
from isaacsim.sensors.experimental.rtx import Lidar

# Example_Rotary は 10 Hz でスキャンする。スキャンの蓄積とマルチティックレンダリングが
# 1 tick につきフルスキャンを生成するよう、tick_rate は scanRateBaseHz と一致させる
lidar = Lidar.create(
    path="/sensor",
    config="Example_Rotary",
    tick_rate=10.0,
    translations=[[0.0, 0.0, 1.0]],
)
```

`Example_Rotary` は 3D Lidar の構成 USD を選択します。ソリッドステート構成に切り替えるには `config="Example_Solid_State"` に置き換え、`tick_rate` をそのアセットの `omni:sensor:Core:scanRateBaseHz` の値に合わせて更新します。

!!! note "5.1 までの `IsaacSensorCreateRtxLidar` コマンドと JSON 設定ファイルによる作成方式は、6.0 では `Lidar.create` と構成 USD に置き換わりました。"

**レンダープロダクトの作成とセンサーのアタッチ**：

```python
import omni.replicator.core as rep

# RTX センサーはカメラの一種であり、専用のレンダープロダクトに割り当てる必要がある
hydra_texture = rep.create.render_product(lidar.paths[0], [1, 1], name="Isaac")
```

**ポイントクラウドを ROS に配信する後処理パイプラインの作成**：

```python
writer = rep.writers.get("RtxLidarROS2PublishPointCloud")
writer.initialize(topicName="point_cloud", frameId="base_scan")
writer.attach([hydra_texture])
```

**2D RTX Lidar（LaserScan）** も同様です：

```python
lidar_2D = Lidar.create(
    path="/sensor_2D",
    config="Example_Rotary_2D",
    tick_rate=10.0,
    translations=[[0.0, 0.0, 1.0]],
)

hydra_texture_2D = rep.create.render_product(lidar_2D.paths[0], [1, 1], name="Isaac")

writer = rep.writers.get("RtxLidarROS2PublishLaserScan")
writer.initialize(topicName="scan", frameId="base_scan")
writer.attach([hydra_texture_2D])
```

!!! note "その他のパラメータ"
    `Lidar.create` がサポートする追加パラメータ（`aux_output_level`、`accumulate_outputs` など）は、公式の RTX Lidar Sensor ドキュメントと API リファレンスを参照してください。

## ステップ 5：（オプション）RTX Lidar のメタデータを PointCloud2 に含める

RTX Lidar は、直交座標のポイントクラウドに加えて、**リターンの強度（intensity）・タイムスタンプ・リターンを生成したオブジェクトのマテリアルやプリムパス**といったメタデータを配信できます。

メタデータを生成するには、OmniLidar プリムの `_replicator:rendervar:GenericModelOutput:channels` 属性に `BASIC`（またはそれ以上のレベル）を含める必要があります。Python では `Lidar.create(..., aux_output_level="BASIC")`（またはそれ以上）で同じ設定ができます。さらに、メタデータを PointCloud2 メッセージに書き出すよう Isaac Sim を設定します。方法は 2 つあります。

### OmniGraph でメタデータを配信する

ステップ 1〜2 のグラフを作成した状態で：

1. シミュレーションを停止し、シーンを USD として保存して、Isaac Sim をいったん終了します。
2. 起動コマンドに `--/rtx-transient/stableIds/enabled=true` を付けて Isaac Sim を再起動します。この設定により、RTX レンダラーがメタデータの一部として 128 ビットの Object ID を生成できるようになります。
3. 保存した USD を開き直し、Action Graph エディタで先ほどのグラフを開きます。
4. **ROS2 RTX Lidar Point Cloud Config** ノードをグラフに追加し、**Include the Intensity** と **Include the ObjectId** にチェックを入れます。
5. Config ノードの **selectedMetadata** 出力を、3D Lidar 用 **ROS2 RTX Lidar Helper** ノードの **selectedMetadata** 入力に接続します。
6. 3D Lidar 用 Helper ノードの **enableObjectIdMap** にチェックを入れます。これにより、Object ID とプリムパスの対応表が String メッセージとして `/object_id_map` トピックに配信されます。
7. Example_Rotary の Lidar プリムを選択し、`_replicator:rendervar:GenericModelOutput:channels` 属性を `["FULL"]` に設定します。
8. **Play** を押してシミュレーションを開始します。

RViz2 では、Fixed Frame を `base_scan` にして PointCloud2 表示（トピック `/point_cloud`）を追加すると、**Channel Name** が `intensity`、**Color Transformer** が Intensity に自動設定され、強度チャネルが可視化されます。

### Python スクリプトでメタデータを配信する

`aux_output_level="FULL"` で Lidar を作成し、`output*` フラグで PointCloud2 に含める補助フィールドを選択します：

```python
import omni.replicator.core as rep
from isaacsim.sensors.experimental.rtx import Lidar

# FULL レベルで作成すると、GenericModelOutput バッファにポイントごとの
# 全メタデータ（強度、Object ID、法線など）が含まれる
lidar = Lidar.create(
    path="/World/sensor_with_metadata",
    config="Example_Rotary",
    tick_rate=10.0,
    aux_output_level="FULL",
    translations=[[0.0, 0.0, 1.0]],
)

hydra_texture = rep.create.render_product(lidar.paths[0], [1, 1], name="Isaac")

# output* フラグで、PointCloud2 メッセージに書き出す補助フィールドを選択する
writer = rep.writers.get("RtxLidarROS2PublishPointCloud")
writer.initialize(
    topicName="point_cloud",
    frameId="base_scan",
    outputIntensity=True,
    outputObjectId=True,
)
writer.attach([hydra_texture])

# Object ID → プリムパスの対応表を別トピックで配信する
object_id_map_writer = rep.writers.get("ROS2PublishObjectIdMap")
object_id_map_writer.initialize(topicName="object_id_map")
object_id_map_writer.attach([hydra_texture])
```

あわせて、`SimulationApp` の起動時に `--/rtx-transient/stableIds/enabled=true` を指定します：

```python
from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": False, "extra_args": ["--/rtx-transient/stableIds/enabled=true"]})
```

### タイムスタンプメタデータの解釈

Timestamp をメタデータに含めた場合、PointCloud2 メッセージには `timestamp_0` と `timestamp_1` という 2 つの uint32 フィールドが入ります。これらはそれぞれ、シミュレーション開始からのナノ秒を表す単一の uint64 値の下位 32 ビットと上位 32 ビットです：

```python
# 例：PointCloud2 のフィールドから読み出したポイントごとのタイムスタンプ
timestamp_0 = 0xCAFEBABE  # 下位 32 ビット
timestamp_1 = 0x12345678  # 上位 32 ビット

# 単一の uint64 ナノ秒値に再結合する
ts_uint64_ns = (int(timestamp_1) << 32) | int(timestamp_0)
```

!!! note "このエンコーディングは Isaac Sim 6.0 で導入されました"
    5.1 までは timestamp は単一の float32 フィールドとして配信されていました。旧エンコーディング向けに書かれたサブスクライバは、2 つの uint32 フィールドを読んで再結合するよう更新が必要です。

### Object ID メタデータの解釈

Object ID は、リターンを生成したオブジェクトのプリムパスに対応する、安定した一意の **128 ビット符号なし整数**です。ObjectId をメタデータに含めた場合、PointCloud2 には `object_id_0` 〜 `object_id_3` の 4 つの uint32 フィールドが入ります。

タイムラインを再生した状態で、Isaac Sim ROS ワークスペースを source した新しいターミナルから次のノードを実行すると、各リターンを生成したプリムのパスが出力されます：

```bash
ros2 run isaac_tutorials ros2_object_id_subscriber.py
```

このサブスクライバは、`/point_cloud` の 4 つの uint32 フィールドを little-endian で 128 ビット整数に再結合し、`/object_id_map` トピック（JSON の `id_to_labels`）でプリムパスに解決しています。詳細はスクリプト本体を参照してください。

## まとめ

このチュートリアルでは、RTX Lidar センサーと ROS 2 の連携を扱いました：

1. **RTX Lidar センサー**（2D / 3D）の追加
2. **RTX Lidar Helper ノード**による LaserScan / PointCloud2 の配信と、フルスキャンと配信周期の関係
3. スタンドアロンスクリプト（`Lidar.create`）による Lidar の作成と配信
4. （オプション）**メタデータ**（強度・Object ID・タイムスタンプ）の PointCloud2 への書き出し

複数センサーのタイムスタンプ同期と RViz2 での一括可視化は、[チュートリアル 9: ROS 2 Transform ツリーとオドメトリ](09_tf.md)で扱います。

## 次のステップ

- [チュートリアル 9: ROS 2 Transform ツリーとオドメトリ](09_tf.md) - グローバル・相対 Transform を TF ツリーに追加する方法を学びます。

### さらに学ぶには

- RTX Lidar の内部動作は、公式センサードキュメントの Overview と RTX Sensor Annotators を参照してください。
- Lidar プリムのパス（renderProductPath 経由）に基づくトピックのネームスペース自動生成：[チュートリアル 15: 自動 ROS 2 ネームスペース生成](15_auto_namespace.md)
