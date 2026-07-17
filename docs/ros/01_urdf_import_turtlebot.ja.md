---
title: "URDF インポート: Turtlebot"
---

# URDF インポート: Turtlebot

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- ROS の記述パッケージから取得した URDF（xacro）の**前処理**の方法
- [Turtlebot3](https://emanual.robotis.com/docs/en/platform/turtlebot3/overview) を Isaac Sim にインポートしてシーンに配置する方法
- インポート後のロボットの**調整**（摩擦・質量・ジョイントゲイン）

Isaac Sim には ROS システムとの統合を支援するツール（ROS 2 ブリッジ、URDF インポートなど）が多数用意されています。この ROS 2 チュートリアルシリーズでは、それらの使い方を例を通して学びます。本チュートリアルはその第 1 回として、Turtlebot3 を Isaac Sim にセットアップし、走行できる状態まで準備します。

!!! tip "すでにリギング済みの USD ロボットを持っている場合"
    ジョイントとプロパティが設定済みの USD 形式のロボットをすでに持っていて、すぐに ROS 2 ブリッジを使い始めたい場合は、次の[チュートリアル 2: ROS 2 メッセージで TurtleBot を駆動する](02_drive_turtlebot.md)へ進んでください。

## はじめに

### 前提条件

- [ROS 2 セットアップ](00_setup.md)が完了しており、ROS 2 が利用可能で、ROS 2 ブリッジエクステンションが有効化され、必要な環境変数が設定されていること
- ROS ワークスペースの基本を理解していること
- xacro をインストールしておくこと：

    Linux の場合：

    ```bash
    sudo apt install ros-$ROS_DISTRO-xacro
    ```

    Windows（Pixi）の場合：

    ```bat
    pixi add ros-$ROS_DISTRO-xacro
    ```

### 所要時間

約 15〜20 分

### 概要

このチュートリアルでは、ROBOTIS が公開している Turtlebot3 の記述パッケージから URDF を取得し、前処理を行った上で Isaac Sim にインポートします。その後、モバイルロボットとして走行できるようにジョイントゲインなどを調整し、部屋のシーンに配置します。

## ステップ 1：Turtlebot3 の URDF を準備する

### 1-1. 記述パッケージをクローンする

ROS 2 を source したターミナルで、Turtlebot3 の記述パッケージをクローンします（まだの場合）：

```bash
git clone -b $ROS_DISTRO https://github.com/ROBOTIS-GIT/turtlebot3.git turtlebot3
```

!!! note "`-b $ROS_DISTRO` の意味"
    Turtlebot3 リポジトリは ROS ディストリビューションごとにブランチが分かれています。`$ROS_DISTRO` は ROS 2 を source すると設定される環境変数（例：`jazzy`）で、使用中のディストリビューションに対応したブランチをチェックアウトしています。

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

!!! note "Windows（Pixi）での前処理"
    コマンドプロンプト（`pixi shell` を起動したシェル）の場合：

    ```bat
    xacro .\turtlebot3_burger.urdf "namespace:=" > tb3_burger_processed.urdf
    ```

    PowerShell の場合、`>` リダイレクトは UTF-16 LE で書き出されて URDF インポーターが解釈できないため、`Out-File -Encoding utf8` を経由して UTF-8 で保存します：

    ```powershell
    xacro .\turtlebot3_burger.urdf "namespace:=" | Out-File -Encoding utf8 tb3_burger_processed.urdf
    ```

!!! note "なぜ前処理が必要か"
    Turtlebot3 の URDF には xacro の変数（`$(arg namespace)` など）が埋め込まれており、そのままでは Isaac Sim の URDF インポーターが解釈できません。`xacro` コマンドで変数を展開（この場合は空の名前空間で置換）した「純粋な URDF」を生成してからインポートします。

## ステップ 2：URDF をインポートする

1. **File > Import** をクリックし、前処理した URDF ファイル（`tb3_burger_processed.urdf`）を選択します。
2. インポート設定ウィンドウで次のように設定します：
    - **Base Type** を **Mobile** にします（可動ベースを持つロボットであることを示します）。
    - （オプション）**Robot Type** を **Wheeled** にすると、ロボットスキーマ上で車輪型ロボットであることが明示されます。
3. 設定が次の画像と一致していることを確認します：

    ![Turtlebot URDF インポート設定](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_6.0_ros_tut_gui_tb_urdf_import.png)

4. **Import** をクリックします。インポートが完了すると、生成された USD ファイルが URDF インポーターによって自動的に開かれます。

!!! note "USD ファイルの保存先"
    インポートすると、アセットの USD 版が自動的に保存されます。保存先は **USD Output** で指定でき（既定は URDF と同じフォルダ）、指定ディレクトリの中に URDF ファイル名と同名のフォルダが作られ、その中に `.usd` ファイルが保存されます。以降のチュートリアルでは、このロボットのプリムパスを `/World/tb3_burger_processed` として参照します。

## ステップ 3：ロボットを調整する

URDF のインポートでは、対応するカテゴリが Isaac Sim 側にあれば、マテリアル・物理・ジョイントのプロパティが自動的に取り込まれます。ただし、対応するカテゴリがない場合や、両システムで単位が異なる場合には、自動設定された値が不正確でロボットの挙動が変わってしまうことがあります。挙動がおかしいときは次のプロパティを調整します。

### 摩擦プロパティ

車輪がスリップする場合は、車輪（および必要なら地面）の摩擦係数を変更してみてください。手順は[ロボットセットアップ チュートリアル 2: シンプルなロボットの組み立て](../robot_setup/02_assemble_robot.md)を参照してください。

### 物理プロパティ（質量・慣性）

URDF に質量や慣性が明示されていない場合、物理エンジンがジオメトリメッシュから推定します。質量・慣性を修正するには：

1. 対象リンクのリジッドボディを含むプリムを探します（Property タブに **Physics > Rigid Body** があるプリム）。
2. Physics プロパティに **Mass** カテゴリが既にあればその値を修正します。
3. Mass カテゴリがなければ、Property タブ上部の **+Add** ボタンから **Physics > Mass** を追加します。

### ジョイントプロパティ（Gain Tuner）

ジョイントが振動する、または動きが遅すぎる場合は、Stiffness と Damping を調整します：

- **Stiffness（剛性）**が高いほどジョイントは目標へ速く鋭く追従します
- **Damping（ダンピング）**が高いほど動きは滑らかになりますが、目標への到達は遅くなります
- **位置制御**のジョイントは「高めの Stiffness ＋ 低めの Damping」
- **速度制御**のジョイントは「**Stiffness = 0** ＋ 非ゼロの Damping」

この Turtlebot では、**Gain Tuner** ツールを使って車輪ジョイントのゲインを設定します：

1. **Tools > Robotics > Asset Editors > Gain Tuner** を開きます。
2. Stage ツリーでロボットを選択します。
3. `wheel_left_joint` と `wheel_right_joint` の **Damping** を `10000000.0` に設定します。
4. **Save Gains to Physics Layer** ボタンをクリックして、ゲインを物理レイヤーに保存します。

![Gain Tuner](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_6.0_ros_tut_gui_gain_tuner.png)

## ステップ 4：シーンを組み立てて動作を確認する

!!! warning "マルチ GPU の Windows 環境での既知の問題"
    マルチ GPU 構成の Windows では、このシーンの読み込み・再生時にアプリケーションがクラッシュする既知の問題があります（将来のリリースで修正予定です）。

このチュートリアルシリーズでは Isaac Sim 付属の環境を使います（あとで任意の環境に差し替え可能です）。

1. 新しいステージを作成し、Isaac Sim の Content ブラウザから **Isaac Sim/Environments/Simple_Room/simple_room.usd** を探してステージにドラッグします。
2. Transform プロパティの **Translate** をすべて 0 にして、部屋を原点に配置します。少しズームインすると部屋の中のテーブルが見えます。
3. ステップ 2〜3 で作成した Turtlebot のロボットアセット（USD ファイル）をステージにドラッグして追加します。
4. 追加直後の Turtlebot はテーブルの上に乗っています。ギズモ（移動ツール）を使って、部屋の**床のすぐ上**に移動します（公式のスクリーンショットでは Translate が `(0, 1.5, -0.75)` です）。
5. **Play** を押して、Turtlebot が床に着地することを確認します。

![Turtlebot 配置確認](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_6.0_ros_tut_gui_tb_urdf_import_2.png)

!!! note "自前の環境を使う場合"
    付属の環境を使わない場合は、環境に **GroundPlane**（地面）と **PhysicsScene**（物理シーン）があることを確認してください。どちらも **Create > Physics** から作成できます。また、照明が必要な場合は **Create > Lights** の各種ライトを試してください。

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. xacro による URDF の**前処理**と **URDF インポート**
2. インポート後の**ロボットパラメータの調整**（摩擦・質量・Gain Tuner によるジョイントゲイン）
3. 環境へのロボットの**配置と動作確認**

## 次のステップ

- [チュートリアル 2: ROS 2 メッセージで TurtleBot を駆動する](02_drive_turtlebot.md) - OmniGraph ノードでロボットを動かし、ROS 2 ブリッジノードで ROS ネットワークに接続する方法を学びます。

### さらに学ぶには

- [URDF インポートチュートリアル](../importer_exporter/01_import_urdf.md)と公式の URDF Importer Extension ドキュメント
- ワールド構築の詳細：[ロボットセットアップ チュートリアル 3: 基本ロボットのアーティキュレーション](../robot_setup/03_articulate_robot.md)
- ゲイン調整：[ロボットセットアップ チュートリアル 11: ジョイントドライブゲインの調整](../robot_setup/11_joint_tuning.md)
