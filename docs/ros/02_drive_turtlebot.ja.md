---
title: ROS 2 メッセージで TurtleBot を駆動する
---

# ROS 2 メッセージで TurtleBot を駆動する

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- Turtlebot3 への**コントローラ**（Differential Controller / Articulation Controller）の追加
- **ROS 2 ブリッジ**と ROS 用 **OmniGraph（OG）ノード**の基礎
- ROS 2 の **Twist メッセージ**を購読（subscribe）してロボットを駆動する設定

## はじめに

### 前提条件

- リギング済みの Turtlebot を持っているか、[チュートリアル 1: URDF インポート: Turtlebot](01_urdf_import_turtlebot.md) を完了していること
- [ROS 2 セットアップ](00_setup.md)が完了しており、Isaac Sim 起動前に必要な環境変数が設定され、ROS 2 ブリッジエクステンションが有効化されていること（**Windows の場合、`ros2 topic pub` などの ROS 2 コマンドは WSL2 のターミナルで実行します**）

### 所要時間

約 20〜30 分

### 概要

ROS 2 ブリッジには、よく使われる rostopic 向けのノードがあらかじめパッケージされています。このチュートリアルでは、その使い方の手順に焦点を当てます。

Isaac Sim を ROS に接続する方法は 3 つあります：

1. **UI（OmniGraph ノード）を使う方法** ← 本チュートリアルで扱う方法
2. エクステンションワークフロー内でスクリプトを書く方法
3. スタンドアロン Python ワークフローでスクリプトを書く方法

## 主要な概念

### ロボットの駆動

[チュートリアル 1](01_urdf_import_turtlebot.md) の終了時点で、ロボットは駆動可能なジョイントを持ち、目標位置・目標速度を与えればジョイントを動かせる状態になっています。しかし実際に操縦するときは、**個々の車輪の速度ではなく、車体の速度**（前進速度・旋回速度）で制御したいはずです。そこで適切なコントローラを追加します。

2 輪の車輪型ロボットである Turtlebot3 に必要なノードは次の 2 つです：

| ノード | 役割 |
|---|---|
| **Differential Controller** | 車体速度（前進・旋回）を左右の車輪速度に変換する |
| **Articulation Controller** | 変換された指令をジョイントドライブに送る |

### ROS 2 への接続

!!! note "OmniGraph と Action Graph とは"
    **OmniGraph** は、ノード（処理単位）を線で繋いでロボットの挙動やデータの流れを定義する、Omniverse の**ビジュアルプログラミング機構**です。そのうち、再生中の毎ステップやイベントをきっかけに実行されるグラフを **Action Graph** と呼び、ROS 2 ブリッジの配信・購読はこの Action Graph 上にノードを並べて構成します。本セクションではまず使い方だけ覚えれば十分です（詳しい仕組みは OmniGraph セクションで解説します）。

ROS 2 ブリッジには、特定のメッセージのサブスクライバ／パブリッシャとなるノードのほか、シミュレーション時間やコンテキスト ID を管理するユーティリティノード、複雑な OmniGraph を隠蔽してくれる「Helper ノード」があります。

特定のトピックに対する ROS 2 ブリッジを確立する手順は、一般に次のようになります：

1. Action Graph を開く
2. 目的の ROS 2 トピックに対応する OG ノードを追加する
3. 必要に応じてプロパティを変更する
4. データのパイプラインを接続する

**パブリッシャノード**は Isaac Sim のデータを ROS メッセージに詰めて ROS ネットワークへ送信する場所、**サブスクライバノード**は ROS 2 メッセージを受信して Isaac Sim 側のパラメータに割り当てる場所です。各ノードのプロパティの指示に従って、必要なデータを出し入れするよう配線します。

## グラフを組み立てる

### ステップ 1：Action Graph を開く

1. Stage パネルでロボットのメインプリム `/World/tb3_burger_processed` を選択します。こうすると、新しい Action Graph がロボットプリムの直下に作成されます。駆動系のコントローラグラフ（差動、アッカーマン、ホロノミックなど）はロボットのアーティキュレーション全体に作用するため、個別のリンクではなく**ロボットのルート直下**に置くのが適切です。
2. **Window > Graph Editors > Action Graph** を開きます。画面下部に Action Graph ウィンドウが表示されます（好きな場所にドッキングできます）。
3. ウィンドウ中央の **New Action Graph** アイコンをクリックし、グラフ名を `ROS_Drive` にします。グラフのパスは `/World/tb3_burger_processed/ROS_Drive` になります。

### ステップ 2：グラフを構築する

Action Graph ウィンドウの左側パネルにすべての OmniGraph ノード（OG ノード）が一覧表示されます。ROS 2 関連のノードは **Isaac Ros2** の下にまとまっており、名前で検索もできます。ノードはリストからグラフウィンドウへドラッグして配置します。

次のグラフと一致するように構築してください：

![Turtlebot 駆動グラフ](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_4.5_ros_tut_gui_ros2_turtlebot_graph.png)

![Make Array 部分](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_4.5_ros_tut_gui_turtlebot_make_array.png)

### ステップ 3：各ノードの役割を理解する

**On Playback Tick ノード** — シミュレーションが「Playing」の間、毎ステップ tick（実行信号）を発行します。このノードから tick を受け取るノードは、シミュレーションステップごとに計算を実行します。

**ROS2 Context ノード** — ROS 2 はミドルウェアに DDS を使っており、DDS は [Domain ID](https://docs.ros.org/en/humble/Concepts/Intermediate/About-Domain-ID.html) によって、物理ネットワークを共有しながら論理的に独立したネットワークを構成できます。同じドメインの ROS 2 ノード同士は自由に発見・通信できますが、異なるドメインとは通信できません。ROS2 Context ノードは指定した Domain ID（既定は 0）でコンテキストを作成します。**Use Domain ID Env Var** にチェックを入れると、Isaac Sim を起動した環境の `ROS_DOMAIN_ID` を読み込みます。

**ROS2 Subscribe Twist ノード** — Twist メッセージを購読します。Property タブの **topicName** フィールドにトピック名 `/cmd_vel` を指定します。

!!! note "サブスクライバの Exec Out を Differential Controller につながない理由"
    サブスクライバノードには **Exec Out** フィールドがあり、メッセージを受信したときに tick に似た信号を送出します。しかし Differential Controller は、新しい指令がいつ届くかに関係なく**毎フレーム tick される必要**があります。そのためこのグラフでは、Differential Controller の **Exec In** はサブスクライバではなく **On Playback Tick** の出力に接続します。

**Scale To/From Stage Unit ノード** — アセットや入力値をステージ単位に変換します。Twist メッセージの速度は SI 単位（m/s）で届くため、ステージがメートル以外の単位（cm など）で作られている場合の差をこのノードが吸収します。

**Break 3-Vector ノード** — Twist サブスクライバの出力は並進速度・角速度それぞれ 3 次元ベクトルです。一方、Differential Controller の入力は「前進速度」と「Z 軸まわりの旋回速度」の 2 つのスカラーだけなので、ベクトルを分解して対応する成分を取り出してから渡す必要があります。

**Differential Controller ノード** — 目標の車体速度を受け取り、車輪速度を計算します。計算には車輪半径と車輪間距離が必要です。オプションで速度上限も設定できます。Turtlebot に合わせて、Property タブに次の値を入力します：

| フィールド | 値 |
|---|---|
| Max Angular Speed | 1.0 |
| Max Linear Speed | 0.22 |
| Wheel Distance | 0.16 |
| Wheel Radius | 0.025 |

**Articulation Controller ノード** — 対象のロボットに割り当てられ、動かすジョイントの名前（またはインデックス）と、Position / Velocity / Effort Commands で与えられた指令を受け取ってジョイントを動かします。このノードも **On Playback Tick** で tick されるため、新しい Twist メッセージが届かない間は、直前に受け取った指令を実行し続けます。

!!! note "Articulation Controller のターゲット指定"
    Property タブで **Add Target** をクリックし、ターゲットにロボットのメインプリム `/World/tb3_burger_processed` を指定します。このアセットには **IsaacRobotAPI** と **ArticulationRootAPI** が適用されているため、アーティキュレーションは自動的に解決されます（詳細は[ロボットセットアップ チュートリアル 3](../robot_setup/03_articulate_robot.md)の Articulation の節を参照）。

**Constant Token ＋ Make Array ノード** — 車輪ジョイントの名前を配列として Articulation Controller に渡すために、各 **Constant Token** ノードにジョイント名を入力し、**Make Array** ノードで配列にまとめます。2 つの Constant Token ノードは、**`wheel_left_joint` を先、`wheel_right_joint` を後**の順で Make Array ノードに接続してください。この順序は Differential Controller の出力の順序と一致している必要があります。

!!! warning "Constant String ではなく Constant Token を使う"
    ジョイント名を **Constant String** ノードに入れてはいけません。OmniGraph には文字列配列（string-array）というデータ型がないため、配列として使う文字列は **token 型**である必要があります。

## ROS 接続を確認する

1. **Play** を押して、グラフの tick と物理シミュレーションを開始します。
2. 別の ROS を source したターミナルで、対応する ROS 2 トピックが存在することを確認します：

    ```bash
    ros2 topic list
    ```

    `/cmd_vel` が `/rosout`、`/parameter_events` と並んで表示されることを確認します。

3. `/cmd_vel` トピックに Twist メッセージをパブリッシュすると、ロボットを操縦できます。前進させてみましょう：

    ```bash
    ros2 topic pub /cmd_vel geometry_msgs/Twist "{'linear': {'x': 0.2, 'y': 0.0, 'z': 0.0}, 'angular': {'x': 0.0, 'y': 0.0, 'z': 0.0}}"
    ```

4. 停止させるには、速度ゼロの指令をパブリッシュします：

    ```bash
    ros2 topic pub /cmd_vel geometry_msgs/Twist "{'linear': {'x': 0.0, 'y': 0.0, 'z': 0.0}, 'angular': {'x': 0.0, 'y': 0.0, 'z': 0.0}}"
    ```

5. キーボードで手軽に操縦できるように、`teleop_twist_keyboard` をインストールします：

    ```bash
    sudo apt-get install ros-$ROS_DISTRO-teleop-twist-keyboard
    ```

    次のコマンドでキーボード操縦を開始します：

    ```bash
    ros2 run teleop_twist_keyboard teleop_twist_keyboard
    ```

!!! tip "トラブルシューティング：ロボットが動かない"
    ロボットが**床の上**にいることを確認してください。テーブルは床と異なる物理プロパティを持っているため、テーブルの上ではうまく走れません。地面や車輪のプロパティを変更する方法は[ロボットセットアップ チュートリアル 3: 基本ロボットのアーティキュレーション](../robot_setup/03_articulate_robot.md)を参照してください。

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. **Differential Controller** と **Articulation Controller** によるロボットの駆動
2. **ROS 2 ブリッジの OmniGraph ノード**の基礎
3. **ROS 2 Twist メッセージ**の購読によるロボットの操縦

## 次のステップ

- [チュートリアル 3: ROS 2 Clock](03_clock.md) - Isaac Sim で ROS 2 Clock のパブリッシャ／サブスクライバを設定する方法を学びます。

### さらに学ぶには

- エクステンションワークフローでのスクリプティング：[チュートリアル 12: ROS 2 ジョイント制御](12_manipulation.md)
- スタンドアロン Python ワークフロー：[チュートリアル 17: スタンドアロンワークフローでの ROS 2 ブリッジ](17_standalone_python.md)
- OmniGraph のスクリプティングとカスタムノードの作成：公式の OmniGraph チュートリアル
- グラフのプリムパスに基づくトピックのネームスペース自動生成：[チュートリアル 15: 自動 ROS 2 ネームスペース生成](15_auto_namespace.md)
