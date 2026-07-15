---
title: ROS 2 Ackermann コントローラ
---

# ROS 2 Ackermann コントローラ

## 学習目標

このチュートリアルでは、Leatherback（アッカーマンステアリングの車両型ロボット）を ROS ネットワーク経由の **AckermannDriveStamped** メッセージで走らせます。以下の内容を習得できます：

- Leatherback への **Articulation / Ackermann コントローラ**のセットアップ
- ROS 2 の **AckermannDriveStamped** メッセージによる駆動
- **Twist メッセージ**からの変換によるアッカーマン車両のキーボード操縦

## はじめに

### 前提条件

- [ROS 2 セットアップ](00_setup.md)が完了しており、ROS 2 ワークスペース環境が正しくセットアップされていること。このチュートリアルは IsaacSim-ros_workspaces リポジトリの `isaac_tutorials` と `cmdvel_to_ackermann` パッケージを使います
- `ackermann_msgs` ROS 2 パッケージが必要です：

    ```bash
    sudo apt install ros-$ROS_DISTRO-ackermann-msgs
    ```

- ROS 2 ブリッジエクステンション（`isaacsim.ros2.bridge`）が有効であること

### 所要時間

約 20〜25 分

### 概要

!!! note "アッカーマンステアリングとは"
    自動車のように**前輪の角度を変えて曲がる**方式のステアリングです。旋回時に左右の前輪が異なる角度になる（内側の車輪ほど深く切れる）のが特徴で、差動二輪（Turtlebot など）とは制御方法が根本的に異なります。ROS 2 では `ackermann_msgs/AckermannDriveStamped`（ステアリング角と速度の指令）でこの種の車両を制御するのが一般的です。

    Isaac Sim の **Ackermann Controller** ノードは、車両全体への指令（ステアリング角・速度）から、**個々の車輪のステアリング角と回転速度**を計算してくれます。

## ステップ 1：Ackermann コントローラとドライブのセットアップ

1. 新しいステージで **Create > Environments > Flat Grid** 環境を作成します。
2. Content ブラウザから **Isaac Sim > ROBOTS > NVIDIA > Leatherback** を開き、`leatherback.usd` をシーンにドラッグ＆ドロップします。Transform プロパティの Translate をすべて 0 にして原点に配置します。
3. **Window > Graph Editors > Action Graph** で新しい Action Graph を作成します。
4. 次のノードを追加して、画像のとおりに接続します：

| ノード | 役割・設定 |
|---|---|
| **On Playback Tick** | 毎フレーム他のノードを実行 |
| **ROS 2 Context** | Domain ID（または `ROS_DOMAIN_ID`）でコンテキストを作成 |
| **ROS 2 Subscribe AckermannDrive** | Ackermann 駆動指令を購読 |
| **ROS 2 QoS Profile** | QoS プロファイルを作成（サブスクライバに接続） |
| **Ackermann Controller** | 車両指令から個々の車輪のステアリング角と車輪速度を計算 |
| **Articulation Controller**（1 つ目） | **ステアリングジョイント**を駆動 |
| **Articulation Controller_01**（2 つ目） | **車輪**を駆動 |

5. 1 つ目の **Articulation Controller**（ステアリング用）の Property タブで：
    - **targetPrim** に Leatherback のプリム（`/Leatherback`）を追加
    - **jointNames** に **Add Element** で次の 2 つを追加：
        - `Knuckle__Upright__Front_Left`
        - `Knuckle__Upright__Front_Right`
6. 2 つ目の **Articulation Controller_01**（車輪用）の Property タブで：
    - **targetPrim** に `/Leatherback` を追加
    - **jointNames** に次の 4 つを追加：
        - `Wheel__Upright__Rear_Left`
        - `Wheel__Upright__Rear_Right`
        - `Wheel__Knuckle__Front_Left`
        - `Wheel__Knuckle__Front_Right`

![Ackermann グラフ](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_full_tut_gui_ackermann_omnigraph.png)

## ステップ 2：ノードのパラメータを設定する

1. **ROS 2 Subscribe AckermannDrive** ノードの Property タブで、**topicName** が `ackermann_cmd` になっていることを確認します。
2. **Ackermann Controller** ノードに、Leatherback の車体諸元を設定します：

| 入力フィールド | 値 | 意味 |
|---|---|---|
| backWheelRadius | 0.052 | 後輪半径 [m] |
| frontWheelRadius | 0.052 | 前輪半径 [m] |
| maxWheelRotation | 0.7854 | 最大ステアリング角 [rad]（= 45°） |
| maxWheelVelocity | 20.0 | 車輪の最大回転速度 |
| trackWidth | 0.24 | トレッド幅（左右車輪間距離）[m] |
| wheelBase | 0.32 | ホイールベース（前後車軸間距離）[m] |
| maxAcceleration | 1.0 | 最大加速度 |
| maxSteeringAngleVelocity | 1.0 | ステアリング角速度の上限 |

3. Isaac Sim で **Play** を押してシミュレーションを開始します。
4. 新しいターミナル（Isaac Sim ROS ワークスペースを source 済み）で、Ackermann 指令のパブリッシャを起動します：

    ```bash
    ros2 run isaac_tutorials ros2_ackermann_publisher.py
    ```

5. Leatherback が次のように走り出すことを確認します：

    ![Ackermann 走行](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_full_tut_viewport_ackermann_publisher.webp)

!!! tip "設定済みアセット"
    - Action Graph 設定済みの Leatherback アセット：Content ブラウザの **Isaac Sim > Sample > ROS2 > Robots > Leatherback_ROS**
    - レーストラック付き倉庫シーン：**Isaac Sim > Sample > ROS2 > Scenario > leatherback_ackermann**

## ステップ 3：Twist メッセージから AckermannDriveStamped への変換

teleop_twist_keyboard などの既存ツールは Twist メッセージを配信します。`cmdvel_to_ackermann` パッケージで Twist を AckermannDriveStamped に変換すれば、アッカーマン車両もキーボードで操縦できます。

1. Content ブラウザから **Isaac Sim > Sample > ROS2 > Scenario > leatherback_ackermann**（レーストラックシーン）を開きます。
2. **PLAY** を押してシミュレーションを開始します。
3. 先ほどのパブリッシャ（`ros2_ackermann_publisher.py`）は停止しておきます。
4. 新しいターミナル（Isaac Sim ROS ワークスペースを source 済み）で、`cmd_vel` から Ackermann 指令への変換ノードを起動します：

    ```bash
    ros2 launch cmdvel_to_ackermann cmdvel_to_ackermann.launch.py acceleration:=0.5 steering_velocity:=0.5
    ```

    !!! note "launch パラメータ"
        | パラメータ | 既定値 | 意味 |
        |---|---|---|
        | `publish_period_ms` | 20 | 配信周期 [ms] |
        | `track_width` | 0.2 | 車輪間距離 [m] |
        | `acceleration` | 0.0 | 加速度 [m/s²]。0 は「可能な限り速く速度を変える」 |
        | `steering_velocity` | 0.0 | ステアリング角の変化速度 [rad/s]。0 は「可能な限り速く角度を変える」 |

5. 別のターミナルで ROS を source し、teleop_twist_keyboard（または任意の Twist 配信パッケージ）を起動します：

    ```bash
    ros2 run teleop_twist_keyboard teleop_twist_keyboard
    ```

6. キーボードで Leatherback を操縦できます。レーストラックから外れずに走れるか試してみてください：

| 操作 | キー |
|---|---|
| 前進 | i |
| 後退 | , |
| 前進左折 | u |
| 前進右折 | o |
| 後退左折 | m |
| 後退右折 | . |
| 停止 | k |

![キーボード操縦](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_full_tut_viewport_ackermann_publisher_2.webp)

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. **Ackermann Controller** ノードと 2 つの Articulation Controller（ステアリング用・車輪用）のセットアップ
2. **AckermannDriveStamped サブスクライバ**から Ackermann Controller への指令の接続
3. `cmdvel_to_ackermann` による **Twist → AckermannDriveStamped 変換**とキーボード操縦

## 次のステップ

- [チュートリアル 15: 自動 ROS 2 ネームスペース生成](15_auto_namespace.md) - マルチロボットシミュレーションに必須の、ネームスペースの自動生成を学びます。
