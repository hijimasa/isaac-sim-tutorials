---
title: 強化学習ポリシーの ROS 2 実行
---

# 強化学習ポリシーの ROS 2 実行

## 学習目標

このチュートリアルでは、強化学習ポリシーを **ROS 2 経由**で Isaac Sim 上で動かします。以下の内容を習得できます：

- H1 平地ロコモーションポリシーのための、Isaac Sim との**観測の配信・行動の受信**を行う ROS 2 ノードのセットアップ
- 強化学習ポリシーを実行するための Isaac Sim 側の環境セットアップ（**On Demand グラフ**と物理設定）

## はじめに

### 前提条件

- **PyTorch** がインストールされていること（[PyTorch 公式のインストール手順](https://pytorch.org/get-started/locally)参照）。ポリシーは別プロセスで動くため、Isaac Sim の PyTorch バージョンと一致している必要はありません
- ROS 2 ブリッジエクステンション（`isaacsim.ros2.bridge`）が有効であること
- IsaacSim-ros_workspaces リポジトリの **`h1_fullbody_controller`** パッケージが必要です。[ROS 2 セットアップ](00_setup.md)でワークスペースが正しくビルドされていることを確認してください
- [ロボットセットアップ チュートリアル 13: 脚ロボットのリギング](../robot_setup/13_rig_legged_robot.md)を完了し、ロコモーションポリシーのパラメータに合わせたジョイント設定ができていること

!!! tip "インストールでのつまずき"
    - PyTorch のインストールで `error: externally-managed-environment` が出る場合は、Python の仮想環境（venv）内にインストールしてください。
    - `ModuleNotFoundError: No module named 'yaml'` が出る場合は、pip で PyYaml をインストールしてください。

### 所要時間

約 30〜40 分

### 概要

[Isaac Lab チュートリアル 1: ポリシーのデプロイ](../isaac_lab/01_policy_deployment.md)では、Isaac Sim の Python API（Policy Controller クラス）でポリシーを直接動かしました。このチュートリアルでは同じ H1 平地歩行ポリシーを、**ポリシーの推論を外部の ROS 2 ノードに切り出した構成**で動かします。Isaac Sim は観測（IMU・ジョイント状態）を ROS 2 トピックとして配信し、外部ノードがポリシーを推論して行動（ジョイント指令）を返します。実機では制御ノードが ROS 2 で動くことが多いため、**シミュレーションと実機で同じ制御スタックを使える**のがこの構成の利点です。

!!! note "H1 平地ロコモーションポリシーについて"
    このポリシーは Isaac Lab の `Isaac-Velocity-Flat-H1-v0` 環境で学習されたもので、H1 ヒューマノイドの平地での速度指令追従を行います。**前進と左右旋回**が可能です。**後退と横移動はサポートされていません**。

## ステップ 1：ロボットのジョイント設定

[ロボットセットアップ チュートリアル 13](../robot_setup/13_rig_legged_robot.md)の手順に従って、ロコモーションポリシーのパラメータに合わせたジョイント設定を行います。**ジョイント設定の不一致は予期しないロボットの挙動の原因になる**ため、このステップは非常に重要です。

- H1 平地ポリシーの環境定義ファイルは [h1_env.yaml](https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/5.1/Isaac/Samples/Policies/H1_Policies/h1_env.yaml) です。
- 環境定義ファイル内の角度は**ラジアン**で指定されていますが、Isaac Sim の USD GUI は**度**を期待します。単位変換に注意してください。
- リギング済みの H1 ロボットは、Content ブラウザの `Isaac/Samples/Rigging/H1/h1_rigged.usd` にあります。

## ステップ 2：IMU センサーを追加する

ポリシーの観測には、pelvis（骨盤）リンクの並進速度・角速度・重力ベクトルが必要です。これらを計算するために、pelvis リンクに IMU センサーを追加します。

- `/h1/pelvis` を右クリックし、**Create > Isaac > Sensors > Imu Sensor** で IMU センサーを作成します。

!!! warning "IMU は pelvis リンクに付けること"
    別のリンク（たとえば torso）に IMU を追加した場合は、ポリシーで使う前に IMU データを pelvis リンクのフレームへ変換する必要があります。

## ステップ 3：観測・行動をやり取りする OmniGraph を構築する

環境定義ファイルのとおり、ポリシーの観測には次の情報が必要です：

- ボディフレームの並進速度・角速度・重力ベクトル（→ **IMU データ**から計算）
- 指令（目標の並進・旋回速度）（→ ROS 2 の **Twist メッセージ**から取得）
- 相対ジョイント位置・速度（→ Isaac Sim の **joint state トピック**から計算）
- 前回の行動（→ ポリシーノード側で記録）

行動はジョイント名と目標位置の辞書、つまり **joint state メッセージ**です。

ここでは、**物理ステップに同期して**観測を配信し行動を受け取る OmniGraph ノードをセットアップします。

### 3-1. On Demand の ActionGraph を作成する

1. [チュートリアル 13](../robot_setup/13_rig_legged_robot.md)でリギングした H1 Unitree のロボットモデルを開きます。
2. ステージを右クリックして **Create > Scope** でスコープを作成し、「Graph」にリネームします（ActionGraph の置き場所です）。
3. ステージを右クリックして **Create > Visual Scripting > ActionGraph** を作成します。
4. ActionGraph を「ROS_Imu」にリネームし、「Graph」スコープにドラッグ＆ドロップします。
5. ActionGraph ノードを左クリックし、Property エディタで **pipelineStage** を **pipelineStageOnDemand** に設定します。

![On Demand グラフの設定](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_rl_ros_controller_1.png)

!!! note "pipelineStageOnDemand と On Physics Step"
    通常の Action Graph は**レンダリングフレーム**ごとに tick されますが、制御ループはレンダリングではなく**物理ステップ**（このチュートリアルでは 200 Hz）に同期させる必要があります。pipelineStage を **pipelineStageOnDemand** に設定し、トリガーに **On Physics Step** ノードを使うことで、グラフが物理ステップごとに実行されるようになります。

### 3-2. IMU パブリッシャノードを作成する

ボディフレームの並進加速度・角速度・姿勢を含む IMU データを ROS 2 に配信します。

1. ActionGraph ノードを右クリックして **Open Graph** を選択します。
2. 次のノードをグラフに追加します：

| ノード | 役割 |
|---|---|
| **On Physics Step** | 物理ステップごとにグラフ全体を実行する |
| **ROS2 Context** | ROS 2 ノードのコンテキストを作成 |
| **ROS2 QoS Profile** | QoS プロファイルを設定 |
| **Isaac Read IMU Node** | Isaac Sim から IMU データを読み取る |
| **Isaac Read Simulation Time** | シミュレーション時刻を読み取る |
| **ROS2 Publish IMU** | IMU データを ROS 2 に配信 |

3. 下の画像のとおりに接続します。
4. **Isaac Read IMU Node** の **IMU Prim** 入力を `/h1/pelvis/Imu_Sensor` に設定します。
5. **Isaac Read IMU Node** の **Read Gravity** 入力の**チェックを外します**。Read Gravity は IMU の加速度出力に重力成分を含めるかどうかの設定です。観測に必要な重力ベクトルは、IMU が出力する姿勢（クォータニオン）からポリシー制御ノード側で算出するため、ここでは加速度への重力の混入を避け、pelvis リンクの並進・角速度と姿勢だけを取得します。
6. **Read Simulation Time** ノードの **Reset on Stop** に**チェックを入れ**、シミュレーション停止時に時刻をリセットするようにします。

![IMU パブリッシャグラフ](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_rl_ros_controller_2.png)

### 3-3. Joint State パブリッシャ／サブスクライバノードを作成する

ジョイント名・位置・速度を配信し、外部ポリシーノードからのジョイント指令を購読します。

1. 新しい ActionGraph を作成して「ROS_Joint_States」にリネームし、**pipelineStage** を **pipelineStageOnDemand** に設定します。
2. 次のノードを追加し、画像のとおりに接続します：**On Physics Step**、**ROS2 Context**、**ROS2 QoS Profile**、**ROS2 Subscribe Joint State**（外部ポリシーノードからの指令を購読）、**ROS2 Publish Joint State**（現在のジョイント状態を配信）、**Isaac Read Simulation Time**、**Articulation Controller**（購読した指令を実行）。
3. **ROS2 Publish Joint State** の **Target Prim** を `/h1`、**Topic Name** を `/joint_states` に設定します。
4. **ROS2 Subscribe Joint State** の **Topic Name** を `/joint_command` に設定します。
5. **Articulation Controller** の **Target Prim** を `/h1` に設定します。
6. **Read Simulation Time** の **Reset on Stop** にチェックを入れます。

![Joint State グラフ](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_rl_ros_controller_3.png)

!!! tip "完成済みアセット"
    セットアップ済みのアセットが Content ブラウザの **Isaac Sim/Samples/ROS2/Robots/h1_ROS.usd** にあります。

## ステップ 4：シナリオと ROS Clock のセットアップ

アセットができたので、ロボットを配置するシーンを作り、物理設定と ROS 時刻の配信を構成します。

### 4-1. シミュレーションシナリオの作成

1. 新しいファイルを作成し、Content ブラウザの **Isaac Sim/Environments/Simple_Warehouse** から `warehouse.usd` をステージにドラッグします。
2. 先ほど作成した `h1_ROS.usd` アセットをステージにドラッグし、Z の Transform を `1.0` にして地面より上に配置します。
3. ステージを右クリックして **Create > Physics > Physics Scene** で物理シーンを作成します。
4. Physics Scene を選択し、**Time Steps Per Second** を **200** に設定します（ポリシーの学習時の物理レート 200 Hz に合わせます）。
5. ロボットは 1 台だけなので、パフォーマンスのため **CPU 物理**を使います：
    - **Enable GPU Dynamics** のチェックを外す
    - **Broadphase Type** を **MBP** に設定

### 4-2. ROS 2 Clock パブリッシャのセットアップ

1. 新しい ActionGraph を作成して「ROS_Clock」にリネームし、**pipelineStage** を **pipelineStageOnDemand** に設定します。
2. **On Physics Step**、**ROS2 Context**、**ROS2 QoS Profile**、**ROS2 Publish Clock**、**Read Simulation Time** を追加し、画像のとおりに接続します。
3. **Read Simulation Time** の **Reset on Stop** にチェックを入れます。

![Clock グラフ](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_rl_ros_controller_4.png)

!!! tip "完成済みシナリオ"
    セットアップ済みの環境が Content ブラウザの **Isaac Sim/Samples/ROS2/Scenario/h1_ros_locomotion_policy_tutorial.usd** にあります。

## ステップ 5：ROS 2 ポリシーを実行する

ROS 2 ワークスペースをビルドして `setup.bash` を source した上で、以下を実行します。

1. PyTorch がインストールされた環境で、`h1_fullbody_controller` パッケージを起動します：

    ```bash
    ros2 launch h1_fullbody_controller h1_fullbody_controller.launch.py
    ```

    !!! warning "ポリシーノードはシミュレーションより先に起動すること"
        この ROS 2 パッケージは、上で配信した ROS メッセージと平地ロコモーションポリシーを使って観測と行動を計算します。速度指令がないときはロボットは静止してバランスを保ちます。**必ずシミュレーションを開始する前に ROS 2 ポリシーを起動してください**。順番が逆だとロボットは転倒します。

2. 作成した H1 のシナリオを開き、**PLAY** でシミュレーションを開始します。
3. 別のターミナルで ROS を source し、teleop_twist_keyboard を起動します：

    ```bash
    ros2 run teleop_twist_keyboard teleop_twist_keyboard
    ```

4. キーボードで H1 を操縦し、期待どおり動くか確認します：

| 操作 | キー |
|---|---|
| 前進 | i |
| 前進＋左旋回 | u |
| 前進＋右旋回 | o |
| 左旋回 | j |
| 右旋回 | l |
| 静止 | k |

![H1 キーボード操縦](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_rl_ros_controller_5.webp)

!!! warning "ポリシーの制約"
    - このバージョンのポリシーは**後退をサポートしません**。`m`、`,`、`.` キーを押すとロボットは転倒します。
    - 並進・旋回速度を **0.75 より大きく**設定するとポリシーの速度制限を超え、ロボットは転倒します。
    - 速度指令がないとき、ロボットが時間とともに少しずつドリフトするのは想定内の挙動です。

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. H1 平地ロコモーションポリシーのための、**観測を配信し行動を受け取る ROS 2 ノード**構成のセットアップ
2. **On Demand（物理ステップ同期）の OmniGraph**（IMU／Joint State／Clock）の構築
3. ポリシーに合わせた**物理設定**（200 Hz、CPU 物理）とキーボード操縦での確認

## 次のステップ

- [Isaac Lab チュートリアル](../isaac_lab/index.md)で Isaac Lab について詳しく学ぶ
- Isaac Sim ネイティブな方法でのポリシー実行は[Isaac Lab チュートリアル 1: ポリシーのデプロイ](../isaac_lab/01_policy_deployment.md)を参照
