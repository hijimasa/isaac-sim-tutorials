---
title: ROS 2 汎用パブリッシャとサブスクライバ
---

# ROS 2 汎用パブリッシャとサブスクライバ

!!! warning "既知の問題：入力値が消える"
    ROS2 Publisher / Subscriber ノードの Property パネルで `messagePackage` や `messageName` を入力した際、パネルの外をクリックすると値が消えることがあります。その場合は値を入力し直してください。再入力後は値が保持され、自動生成される属性が表示されます。

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- ROS 2 のメッセージ型の基礎
- **任意の型**のメッセージを ROS 2 トピックにパブリッシュする方法（汎用 ROS2 Publisher ノード）
- **任意の型**の ROS 2 トピックをサブスクライブする方法（汎用 ROS2 Subscriber ノード）

## はじめに

### 前提条件

- [ROS 2 セットアップ](00_setup.md)が完了していること（`.bashrc` で ROS 2 を source している場合は、Isaac Sim を直接起動できます）
- 複数マシンで使う場合は、Isaac Sim の起動前と ROS メッセージを送受信するすべてのターミナルで `FASTRTPS_DEFAULT_PROFILES_FILE` を設定し、ROS 2 エクステンションを有効にしておくこと

### 所要時間

約 20〜30 分

### 概要

これまでのチュートリアルで使ってきた専用ノード（Publish Joint State、Subscribe Twist など）は、よく使うメッセージ型ごとに用意されたものでした。**汎用の ROS2 Publisher / ROS2 Subscriber ノード**を使うと、専用ノードが用意されていないものも含め、**環境に存在する任意のメッセージ型**を配信・購読できます。

!!! note "ROS 2 のメッセージ型"
    ROS 2 の主要な通信インターフェースの 1 つが**トピック**です。ロボットの状態（`nav_msgs/msg/Odometry`）やセンサー（`sensor_msgs/msg/Imu`）のような連続データストリームの送受信に使われます。

    現在 source している ROS 2 ディストロ（とワークスペース）で利用可能なメッセージ型は、次のコマンドで一覧できます：

    ```bash
    ros2 interface list --only-msgs
    ```

## 汎用パブリッシャ

### 基本の使い方

1. **Window > Graph Editors > Action Graph** で Action Graph を作成します。
2. **On Playback Tick**、**ROS2 Context**、**ROS2 Publisher**（任意の型のメッセージをトピックに配信するノード）を追加・接続します。

    ![汎用パブリッシャ](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_6.0_ros_tut_gui_publisher.png)

3. ノードの Property パネルで、メッセージ型を `messagePackage` / `messageSubfolder` / `messageName` のパターンで指定します。有効な（存在する）メッセージ型を指定すると、**ノードの入力属性がそのメッセージの構造に合わせて自動的に再構成**されます。
4. 他のノードの出力を接続するか Property パネルで値を設定して、配信するデータを埋めます。
5. シミュレーションを **Play** すると配信が始まります。

!!! note "入力属性の再構成ルール"
    - 埋め込みメッセージ型のフィールド（例：`std_msgs/Header header`）は、新しい属性として**展開**されます。
    - 埋め込みメッセージの配列型のフィールド（例：`geometry_msgs/Point32[] points`）は、**token array 型の単一属性**として扱われ、各 token は JSON としてエンコードされます。

    なお、メッセージ型を変えたときの属性の再構成に、シミュレーションを再生する必要はありません。

![メッセージ型ごとの属性再構成の例](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_6.0_ros_tut_gui_publisher_message_types.png)

### 例 1：Joint State を汎用ノードで配信する

専用の Publish Joint State ノードの代わりに、汎用 ROS2 Publisher ノードで `sensor_msgs/msg/JointState` を `/joint_states` に配信してみます。

1. 新しいステージで、Content ブラウザから **Isaac Sim > Robots > FrankaRobotics > FrankaPanda > franka.usd** を開いて Franka ロボットを読み込みます。
2. Action Graph を作成し、次のノードを追加・接続・設定します：

| ノード | 役割 |
|---|---|
| **On Playback Tick** | 毎フレーム実行 |
| **Isaac Read Simulation Time** | シミュレーション時刻の取得（`resetOnStop` の挙動は[チュートリアル 3](03_clock.md) 参照） |
| **Isaac Time Splitter** | 時刻を秒とナノ秒に分割し、`std_msgs/Header` のタイムスタンプを埋める |
| **Articulation State** | ロボットのジョイント状態（位置・速度・トルク）を取得して JointState メッセージを埋める |
| **ROS2 Context** | コンテキストの作成 |
| **ROS2 Publisher** | 汎用パブリッシャ |

![Joint State 配信の例](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_6.0_ros_tut_gui_publisher_example_joint_states.png)

| ノード | 入力フィールド | 値 |
|---|---|---|
| ROS2 Publisher | messagePackage | sensor_msgs |
| ROS2 Publisher | messageName | JointState |
| ROS2 Publisher | topicName | joint_states |
| Articulation State | targetPrim | /panda |

3. **Play** すると配信が始まります。
4. 配信を確認します：

    ```bash
    ros2 topic echo /joint_states
    ```

### 例 2：オブジェクトの姿勢を配信する

`geometry_msgs/msg/Pose` でオブジェクトの姿勢を `/object_pose` に配信します。

1. 新しいステージで **Create > Shape > Cube** でキューブを作成し、`/World/Cube` を選択して右クリック **Add > Physics > Rigid Body with Colliders Preset** で自由落下できるようにします。
2. Action Graph を作成し、**On Playback Tick**、**Read Prim Local Transform**（プリムのローカル変換行列を取得）、**Get Translation**（変換行列から並進成分を取得）、**Get Rotation Quaternion**（変換行列から回転成分をクォータニオンで取得）、**Break 3-Vector**（3 成分ベクトルの分解）、**Break 4-Vector**（4 成分ベクトルの分解）、**ROS2 Context**、**ROS2 Publisher** を追加・接続します：

    ![オブジェクト姿勢配信の例](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_6.0_ros_tut_gui_publisher_example_object_pose.png)

| ノード | 入力フィールド | 値 |
|---|---|---|
| ROS2 Publisher | messagePackage | geometry_msgs |
| ROS2 Publisher | messageName | Pose |
| ROS2 Publisher | topicName | object_pose |
| Read Prim Local Transform | prim | /World/Cube |

3. **Play** して配信を確認します：

    ```bash
    ros2 topic echo /object_pose
    ```

## 汎用サブスクライバ

### 基本の使い方

1. Action Graph に **On Playback Tick**、**ROS2 Context**、**ROS2 Subscriber**（任意の型のトピックを購読するノード）を追加・接続します。

    ![汎用サブスクライバ](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_6.0_ros_tut_gui_subscriber.png)

2. Property パネルでメッセージ型を `messagePackage` / `messageSubfolder` / `messageName` のパターンで指定します。有効な型を指定すると、今度は**出力属性**が再構成されます（再構成ルールはパブリッシャと同じです）。

    ![メッセージ型ごとの出力属性再構成の例](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_6.0_ros_tut_gui_subscriber_message_types.png)

3. ノードの出力を他のノードの入力に接続して、受信したデータを利用します。
4. **Play** すると、ROS 2 環境にメッセージが流れたときに受信されます。

### 例：受信した姿勢にオブジェクトをテレポートする

`/object_pose` トピック（`geometry_msgs/msg/Pose`）を購読し、受信した姿勢にキューブをテレポートさせます。

1. 新しいステージで **Create > Shape > Cube** でキューブを作成します。
2. Action Graph を作成し、**On Playback Tick**、**Read Prim Local Transform**（プリムのローカル変換行列を取得）、**Write Prim Local Transform**（プリムのローカル変換行列を設定）、**Set Translation**（変換行列の並進成分を設定）、**Set Rotation**（変換行列の回転成分を設定）、**Make 3-Vector**（3 成分からベクトルを作成）、**Make 4-Vector**（4 成分からベクトルを作成）、**ROS2 Context**、**ROS2 Subscriber** を追加・接続します：

    ![姿勢購読の例](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_6.0_ros_tut_gui_subscriber_example.png)

| ノード | 入力フィールド | 値 |
|---|---|---|
| ROS2 Subscriber | messagePackage | geometry_msgs |
| ROS2 Subscriber | messageName | Pose |
| ROS2 Subscriber | topicName | object_pose |
| Read Prim Local Transform | prim | /World/Cube |
| Write Prim Local Transform | prim | /World/Cube |

3. **Play** した状態で、ROS 2 ターミナルから姿勢を配信すると、キューブが指定した姿勢にテレポートします：

    ```bash
    ros2 topic pub -1 /object_pose geometry_msgs/msg/Pose "{position: {x: 1, y: 2, z: 3}, orientation: {x: 0.4619398, y: 0.1913417, z: 0.4619398, w: 0.7325378}}"
    ```

## まとめ

このチュートリアルでは、汎用の **ROS2 Publisher / ROS2 Subscriber** ノードを使って、利用可能な任意のメッセージ型の配信・購読を行いました。メッセージ型の指定によってノードの属性が自動再構成される仕組みが鍵です。

## 次のステップ

- [チュートリアル 23: ROS 2 汎用サービスサーバとクライアント](23_generic_server_client.md) - 任意の ROS 2 サービスを Isaac Sim から操作する方法を学びます。
