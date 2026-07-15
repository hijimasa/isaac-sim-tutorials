---
title: "ROS 2 ジョイント制御: Extension Python Scripting"
---

# ROS 2 ジョイント制御: Extension Python Scripting

## 学習目標

このチュートリアルでは、マニピュレータ（Franka Emika Panda）を対象に、以下の内容を習得します：

- OmniGraph での **Joint State パブリッシャ／サブスクライバ**の追加
- メニューショートカットによる Joint State グラフの自動生成
- Script Editor から **OmniGraph Python API** で同じグラフを構築する方法
- **位置制御と速度制御**の混在（ジョイントごとの制御モード指定）

## はじめに

### 前提条件

- 公式ドキュメントの Workflows を読み、Extension ワークフローを理解していること
- Python スクリプトを実行するターミナルで、適切な ros2_ws（[セットアップページ](00_setup.md)でビルドしたワークスペース）が source されていること
- Isaac Sim 起動前に `FASTRTPS_DEFAULT_PROFILES_FILE` 環境変数が設定され、ROS 2 ブリッジが有効であること

### 所要時間

約 20〜25 分

### 概要

ここまでのチュートリアルはモバイルロボット（Turtlebot）が中心でしたが、このチュートリアルでは**マニピュレータ**を扱います。ロボットアームの制御では、`/joint_states` トピックで現在のジョイント状態を配信し、`/joint_command` トピックで目標値を受け取るのが ROS 2 の定番構成です（MoveIt 2 などのモーションプランナもこの構成を前提とします）。この双方向の接続を、UI・ショートカット・Python スクリプトの 3 通りで構築します。

## ステップ 1：UI で Joint State グラフを構築する

1. Content ブラウザから **Isaac Sim > Robots > FrankaRobotics > FrankaPanda > franka.usd** を開きます。
2. **Window > Graph Editors > Action Graph** で Action Graph を作成します。
3. 次の OmniGraph ノードを追加します：

| ノード | 役割 |
|---|---|
| **On Playback Tick** | 毎シミュレーションフレーム、他のノードを実行する |
| **Isaac Read Simulation Time** | 現在のシミュレーション時刻を取得する |
| **ROS2 Publish Joint State** | ジョイント状態を `/joint_states` トピックに配信する |
| **ROS2 Subscribe Joint State** | `/joint_command` トピックからジョイント指令を受信する |
| **Articulation Controller** | サブスクライバが受け取った指令どおりにアーティキュレーションを動かす |

4. **ROS2 Publish Joint State** ノードを選択し、**targetPrim** に `/panda` のロボットアーティキュレーションを追加します。
5. **Articulation Controller** ノードで、動かすロボットを指定します。**targetPrim** に `/panda` を追加するか、**robotPath** フィールドに `/panda` と入力します。
6. **On Playback Tick** の Tick 出力を、**ROS2 Publish Joint State**、**ROS2 Subscribe Joint State**、**Articulation Controller** の Execution 入力に接続します。
7. **Isaac Read Simulation Time** の Simulation Time 出力を **ROS2 Publish Joint State** の Timestamp 入力に接続し、残りの接続を次の画像のとおりに設定します（サブスクライバの jointNames / positionCommand / velocityCommand / effortCommand 出力 → Articulation Controller の対応する入力）：

    ![Joint State グラフ](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_ros_tut_gui_ros2_manipulation_1.png)

8. **Play** を押すと、`/joint_states` への配信と `/joint_command` の購読が始まります。
9. ROS 2 ブリッジの動作確認として、付属の Python スクリプトでジョイント指令を配信します。ROS 2 を source したターミナルで：

    ```bash
    ros2 run isaac_tutorials ros2_publisher.py
    ```

    Franka の各関節が滑らかに動き始めます。

10. ロボットが動いている間に、別の ROS 2 ターミナルでジョイント状態を確認します：

    ```bash
    ros2 topic echo /joint_states
    ```

!!! note "Articulation Root の位置"
    Articulation Root は、シミュレーション内のロボットを構成するリンクとジョイントの集合（アーティキュレーションツリー）の起点を表します。Franka のような**固定ベース**のロボットではワールドへのルートジョイントに、**移動可能な**ロボットでは最も深いツリーを持つリジッドボディ（典型的には胴体や `chassis_link`）に指定されます。

## ステップ 2：グラフショートカット

Joint State のパブリッシャ／サブスクライバグラフは、数クリックで自動生成できます：

1. **Tools > Robotics > ROS 2 OmniGraphs > JointStates** を開きます（表示されない場合は ROS 2 ブリッジを有効化してください）。
2. ポップアップで **Graph Path**、（必要なら）**Node Namespace**、**Articulation Root API を含むプリム**を指定します。
3. サブスクライバを使う場合は、ロボットを動かすのに必要な **Articulation Controller ノードを追加するオプション**も選べます。

## ステップ 3：Python スクリプトでグラフを構築する

UI で行った操作は、OmniGraph の Python API でも実行できます。

1. **franka.usd** を開きます。
2. **Window > Script Editor** を開き、次のコードを貼り付けます（ステップ 1 の 2〜7 に相当します）。ロボットが `/panda` 以外のパスで表示されている場合は、Articulation Controller と Publish Joint State のターゲット（下から 2 行）を実際のプリムパスに合わせてください：

```python
import omni.graph.core as og

og.Controller.edit(
    {"graph_path": "/ActionGraph", "evaluator_name": "execution"},
    {
        og.Controller.Keys.CREATE_NODES: [
            ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),
            ("PublishJointState", "isaacsim.ros2.bridge.ROS2PublishJointState"),
            ("SubscribeJointState", "isaacsim.ros2.bridge.ROS2SubscribeJointState"),
            ("ArticulationController", "isaacsim.core.nodes.IsaacArticulationController"),
            ("ReadSimTime", "isaacsim.core.nodes.IsaacReadSimulationTime"),
        ],
        og.Controller.Keys.CONNECT: [
            ("OnPlaybackTick.outputs:tick", "PublishJointState.inputs:execIn"),
            ("OnPlaybackTick.outputs:tick", "SubscribeJointState.inputs:execIn"),
            ("OnPlaybackTick.outputs:tick", "ArticulationController.inputs:execIn"),

            ("ReadSimTime.outputs:simulationTime", "PublishJointState.inputs:timeStamp"),

            ("SubscribeJointState.outputs:jointNames", "ArticulationController.inputs:jointNames"),
            ("SubscribeJointState.outputs:positionCommand", "ArticulationController.inputs:positionCommand"),
            ("SubscribeJointState.outputs:velocityCommand", "ArticulationController.inputs:velocityCommand"),
            ("SubscribeJointState.outputs:effortCommand", "ArticulationController.inputs:effortCommand"),
        ],
        og.Controller.Keys.SET_VALUES: [
            # Articulation Controller ノードに /panda ロボットのパスを渡す
            # robotPath の指定は targetPrim の設定と等価
            # ("ArticulationController.inputs:usePath", True),  # 古いバージョンの Isaac Sim ではこの行を有効化
            ("ArticulationController.inputs:robotPath", "/panda"),
            ("PublishJointState.inputs:targetPrim", "/panda")
        ],
    },
)
```

3. Script Editor で **Run** を押すと、必要なノードがすべて揃った Action Graph が追加されます（Stage ツリーで確認できます）。

!!! warning "このスクリプトは 1 回だけ実行すること"
    このスクリプトはステージに ActionGraph が存在しないことを前提としています。再実行したい場合は、新しいステージを開いてから実行してください。

4. ステップ 1 と同様に `ros2 run isaac_tutorials ros2_publisher.py` で動作確認し、`ros2 topic echo /joint_states` でジョイント状態を確認します。

## ステップ 4：位置制御と速度制御の混在

Joint State サブスクライバは**位置制御と速度制御**をサポートします。各ジョイントは同時に 1 つのモードでしか制御できませんが、**同じアーティキュレーションツリー内のジョイントごとに異なるモード**を使えます。

!!! note "制御モードとゲインの対応"
    各ジョイントの Stiffness / Damping は、使う制御モードに合わせて設定してください：

    - **位置制御**：Stiffness ≫ Damping
    - **速度制御**：Stiffness = 0、Damping > 0

    詳しくは[ロボットセットアップ チュートリアル 11: ジョイントドライブゲインの調整](../robot_setup/11_joint_tuning.md)を参照してください。

次のスニペットは、同じモードのジョイントを 1 つのメッセージにまとめ、位置制御用と速度制御用の 2 つのメッセージで指令する例です（整理のため、また配信レートを分けられるようにするための分割です）：

```python
import threading

import rclpy
from sensor_msgs.msg import JointState

rclpy.init()
node = rclpy.create_node('position_velocity_publisher')
pub = node.create_publisher(JointState, 'joint_command', 10)

# 別スレッドで spin する
thread = threading.Thread(target=rclpy.spin, args=(node, ), daemon=True)
thread.start()

joint_state_position = JointState()
joint_state_velocity = JointState()

joint_state_position.name = ["joint1", "joint2", "joint3"]
joint_state_velocity.name = ["wheel_left_joint", "wheel_right_joint"]
joint_state_position.position = [0.2, 0.2, 0.2]
joint_state_velocity.velocity = [20.0, -20.0]

rate = node.create_rate(10)
try:
    while rclpy.ok():
        pub.publish(joint_state_position)
        pub.publish(joint_state_velocity)
        rate.sleep()
except KeyboardInterrupt:
    pass
rclpy.shutdown()
thread.join()
```

1 つのメッセージにまとめることもできます。その場合、そのモードで制御しないジョイントには `nan` を指定します：

```python
joint_state = JointState()
joint_state.name = ["joint1", "joint2", "joint3", "wheel_left_joint", "wheel_right_joint"]
joint_state.position = [0.2, 0.2, 0.2, float('nan'), float('nan')]
joint_state.velocity = [float('nan'), float('nan'), float('nan'), 20.0, -20.0]
```

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. **Joint State パブリッシャ／サブスクライバ**の UI での構築と動作確認
2. メニューショートカットによる自動生成
3. **OmniGraph Python API**（`og.Controller.edit`）によるグラフのスクリプト構築
4. **位置制御と速度制御の混在**と `nan` による部分指定

## 次のステップ

- [チュートリアル 13: NameOverride 属性](13_name_override.md) - `isaac:nameOverride` 属性でプリムにカスタム名を付けて ROS に配信する方法を学びます。
