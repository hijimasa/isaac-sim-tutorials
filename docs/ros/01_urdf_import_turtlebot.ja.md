---
title: "URDF インポート: Turtlebot"
---

# URDF インポート: Turtlebot

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- ROS の記述パッケージから取得した URDF（xacro）の**前処理**の方法
- [Turtlebot3](https://emanual.robotis.com/docs/en/platform/turtlebot3/overview) を Isaac Sim にインポートしてシーンに配置する方法
- インポート後のロボットの**調整**（摩擦・質量・ジョイントプロパティ）

Isaac Sim には ROS システムとの統合を支援するツール（ROS 2 ブリッジ、URDF インポートなど）が多数用意されています。この ROS 2 チュートリアルシリーズでは、それらの使い方を例を通して学びます。本チュートリアルはその第 1 回として、Turtlebot3 を Isaac Sim にセットアップし、走行できる状態まで準備します。

!!! tip "すでにリギング済みの USD ロボットを持っている場合"
    ジョイントとプロパティが設定済みの USD 形式のロボットをすでに持っていて、すぐに ROS 2 ブリッジを使い始めたい場合は、次の[チュートリアル 2: ROS 2 メッセージで TurtleBot を駆動する](02_drive_turtlebot.md)へ進んでください。

## はじめに

### 前提条件

- [ROS 2 セットアップ](00_setup.md)が完了しており、ROS 2 が利用可能で、ROS 2 ブリッジエクステンションが有効化され、必要な環境変数が設定されていること（**Windows の場合は WSL2 上に ROS 2 をセットアップします**）
- ROS ワークスペースの基本を理解していること
- xacro をインストールしておくこと：

```bash
sudo apt install ros-$ROS_DISTRO-xacro
```

### 所要時間

約 15〜20 分

### 概要

このチュートリアルでは、ROBOTIS が公開している Turtlebot3 の記述パッケージから URDF を取得し、前処理を行った上で Isaac Sim にインポートします。その後、モバイルロボットとして走行できるようにジョイントドライブなどを調整します。

## ステップ 1：Turtlebot3 の URDF を準備する

### 1-1. 記述パッケージをクローンする

ROS 2 を source したターミナルで、Turtlebot3 の記述パッケージをクローンします（まだの場合）：

```bash
git clone -b $ROS_DISTRO https://github.com/ROBOTIS-GIT/turtlebot3.git turtlebot3
```

!!! note "`-b $ROS_DISTRO` の意味"
    Turtlebot3 リポジトリは ROS ディストリビューションごとにブランチが分かれています。`$ROS_DISTRO` は ROS 2 を source すると設定される環境変数（例：`humble`）で、使用中のディストリビューションに対応したブランチをチェックアウトしています。

### 1-2. URDF を前処理する

Turtlebot3 Burger の URDF ファイルは `turtlebot3/turtlebot3_description/urdf/turtlebot3_burger.urdf` にあります。そのディレクトリへ移動します：

```bash
cd turtlebot3/turtlebot3_description/urdf
```

同じターミナルで、URDF ファイルを前処理して名前空間（namespace）の引数を除去し、`tb3_burger_processed.urdf` として保存します：

```bash
namespace=""
xacro ./turtlebot3_burger.urdf "namespace:=${namespace:+$namespace/}" > tb3_burger_processed.urdf
```

!!! note "なぜ前処理が必要か"
    Turtlebot3 の URDF には xacro の変数（`$(arg namespace)` など）が埋め込まれており、そのままでは Isaac Sim の URDF インポーターが解釈できません。`xacro` コマンドで変数を展開（この場合は空の名前空間で置換）した「純粋な URDF」を生成してからインポートします。

## ステップ 2：環境を準備する

このチュートリアルシリーズでは Isaac Sim 付属の環境を使います（あとで任意の環境に差し替え可能です）。

1. 新しいステージを作成します。
2. Isaac Sim の Content ブラウザから **Isaac Sim/Environments/Simple_Room/simple_room.usd** を探し、ステージにドラッグします。
3. Transform プロパティの **Translate** をすべて 0 にして、部屋を原点に配置します。少しズームインすると部屋の中のテーブルが見えます。

!!! note "自前の環境を使う場合"
    付属の環境を使わない場合は、環境に **GroundPlane**（地面）と **PhysicsScene**（物理シーン）があることを確認してください。どちらも **Create > Physics** から作成できます。また、照明が必要な場合は **Create > Light** の各種ライトを試してください。

## ステップ 3：URDF をインポートする

1. **File > Import** をクリックし、前処理した URDF ファイル（`tb3_burger_processed.urdf`）を選択します。
2. インポート設定ウィンドウで次のように設定します：
    - **Referenced Model** を選択します。
    - **Links** セクションで **Moveable Base** に設定します（モバイルロボットのため）。
    - **Joints & Drives** セクションで、`wheel_left_joint` と `wheel_right_joint` のターゲットを **Velocity** に変更します。あとで車輪を速度指令で駆動できるようにするためです。
3. 設定が次の画像と一致していることを確認します：

    ![Turtlebot URDF インポート設定](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.1_ros_tut_gui_tb_urdf_import.png)

4. **Import** をクリックします。

!!! note "USD ファイルの自動保存先"
    インポートが完了すると、アセットの USD 版のコピーが自動的に保存されます。保存先は **USD Output** で指定でき（既定は URDF と同じフォルダ）、指定ディレクトリの中に URDF ファイル名と同名のフォルダが作られ、その中に `.usd` ファイルが保存されます。

## ステップ 4：配置して動作を確認する

1. インポート直後の Turtlebot はテーブルの上に乗っています。ギズモ（移動ツール）を使って、部屋の**床のすぐ上**に移動します。
2. **Play** を押して、Turtlebot が床に着地することを確認します。

![Turtlebot 配置確認](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.1_ros_tut_gui_tb_urdf_import_2.png)

## ステップ 5：ロボットを調整する

URDF のインポートでは、対応するカテゴリが Isaac Sim 側にあれば、マテリアル・物理・ジョイントのプロパティが自動的に取り込まれます。ただし、対応するカテゴリがない場合や、両システムで単位が異なる場合には、自動設定された値が不正確でロボットの挙動が変わってしまうことがあります。挙動がおかしいときは次のプロパティを調整します。

### 摩擦プロパティ

車輪がスリップする場合は、車輪（および必要なら地面）の摩擦係数を変更してみてください。手順は[ロボットセットアップ チュートリアル 2: シンプルなロボットの組み立て](../robot_setup/02_assemble_robot.md)を参照してください。

### 物理プロパティ（質量・慣性）

URDF に質量や慣性が明示されていない場合、物理エンジンがジオメトリメッシュから推定します。質量・慣性を修正するには：

1. 対象リンクのリジッドボディを含むプリムを探します（Property タブに **Physics > Rigid Body** があるプリム）。
2. Physics プロパティに **Mass** カテゴリが既にあればその値を修正します。
3. Mass カテゴリがなければ、Property タブ上部の **+Add** ボタンから **Physics > Mass** を追加します。

### ジョイントプロパティ

ジョイントが振動する、または動きが遅すぎる場合は、Stiffness と Damping を調整します：

- **Stiffness（剛性）**が高いほどジョイントは目標へ速く鋭く追従します
- **Damping（ダンピング）**が高いほど動きは滑らかになりますが、目標への到達は遅くなります
- **位置制御**のジョイントは「高めの Stiffness ＋ 低めの Damping」
- **速度制御**のジョイントは「**Stiffness = 0** ＋ 非ゼロの Damping」

この Turtlebot では、車輪ジョイントの **Damping を 10000000.0**、**Stiffness を 0.0** に設定してみてください。

!!! note "パラメータが保存できないとき：Reference の仕組み"
    URDF インポートが完了すると、ステージ上のロボットは通常 **Reference（参照）**として読み込まれています。Stage ツリーのロボットプリムにオレンジまたは青の矢印が付いていることで確認できます。

    ![Reference アイコン](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isaac_reference_eyecon.png)

    パラメータの変更や保存がうまくいかない場合は、参照先の**元の USD ファイルを直接編集**してください。元ファイルのパスは、Property タブの **References > Asset Path** で確認できます。

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. xacro による URDF の**前処理**と **URDF インポート**
2. インポート後の**ロボットパラメータの調整**（摩擦・質量・ジョイント）

## 次のステップ

- [チュートリアル 2: ROS 2 メッセージで TurtleBot を駆動する](02_drive_turtlebot.md) - OmniGraph ノードでロボットを動かし、ROS 2 ブリッジノードで ROS ネットワークに接続する方法を学びます。

### さらに学ぶには

- [URDF インポートチュートリアル](../importer_exporter/01_import_urdf.md)と公式の URDF Importer Extension ドキュメント
- ワールド構築の詳細：[ロボットセットアップ チュートリアル 3: 基本ロボットのアーティキュレーション](../robot_setup/03_articulate_robot.md)
- ゲイン調整：[ロボットセットアップ チュートリアル 11: ジョイントドライブゲインの調整](../robot_setup/11_joint_tuning.md)
