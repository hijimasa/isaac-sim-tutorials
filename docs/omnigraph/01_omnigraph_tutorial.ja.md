---
title: Isaac Sim OmniGraph チュートリアル
---

# Isaac Sim OmniGraph チュートリアル

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- OmniGraph を使った**アクショングラフ**の構築方法
- Articulation Controller と Differential Controller で JetBot を制御する方法
- Constant Token / Make Array ノードで関節名リストを作る方法
- OmniGraph ショートカットで差動コントローラのグラフを自動生成する方法

## はじめに

### 前提条件

- Isaac Sim 5.1 が起動できること
- ステージ・ビューポート・Content Browser の基本操作を理解していること

!!! tip "OmniGraph の基礎も参照"
    OmniGraph は Omniverse Kit の重要なコンポーネントです。基礎概念については [OmniGraph チュートリアル一覧](index.md) と Omniverse の OmniGraph ドキュメントも合わせて参照することを強く推奨します。

### 所要時間

約 20〜30 分

### 概要

OmniGraph は Omniverse のビジュアルプログラミングフレームワークです。Isaac Sim では、Replicator・ROS 2 ブリッジ・センサーアクセス・コントローラ・外部入出力デバイス・UI など、多くの機能の中心エンジンとして使われています。このチュートリアルでは、ビジュアルプログラミングで JetBot（2 輪ロボット）を制御するアクショングラフを構築します。

## ステップ 1：ステージをセットアップする

1. 新規ステージで右クリックし、**Create > Physics > Ground Plane** で地面を作成します。
2. Content Browser で `Isaac Sim/Robots/NVIDIA/Jetbot/jetbot.usd` を開きます。
3. `jetbot.usd` をステージにドラッグ＆ドロップします。
4. JetBot を地面のすぐ上に配置します。
5. コンテキストツリーで JetBot が `/World/jetbot` の下にあることを確認します。

![ステージ上の JetBot](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_base_tut_viewport_omnigraph_jetbot.png)

!!! note "動作確認とカメラメッシュの非表示"
    Play を押して JetBot が地面に落下・着地することを確認し、続行前に Stop を押します。デフォルトのレンダー設定によっては JetBot のカメラにプレースホルダーメッシュ（灰色のテレビカメラ状）が表示されます。非表示にするには、ビューポートのアイコンから **Show By Type > Cameras** を無効にします。

## ステップ 2：グラフを構築する

1. **Window > Graph Editors > Action Graph** を選択します。Graph Editor が Content Browser と同じペインに表示されます。
2. **New Action Graph** をクリックして空のグラフを開きます。
3. 検索バーに `controller` と入力し、**Articulation Controller** と **Differential Controller** をグラフにドラッグします。

### コントローラの設定

**Articulation Controller** は、Articulation ルートを持つ prim の指定した関節に、駆動コマンド（力・位置・速度）を適用します。制御対象のロボットを指定します。

- Articulation Controller ノードを選択し、Property ペインを開きます。
- **usePath** をクリックして `robotPath` に `/World/jetbot` と入力するか、`input:targetPrim` の **Add Targets** から JetBot を選択します。

**Differential Controller** は、目標の線速度・角速度から 2 輪ロボットの駆動コマンドを計算します。

- Differential Controller ノードを選択し、Property ペインで **wheelDistance** を `0.1125`、**wheelRadius** を `0.03`、**maxAngularSpeed** を `0.2` に設定します。

### 関節名リストを作る

Articulation Controller には、動かす関節をトークンまたはインデックス値のリストで渡す必要があります。JetBot の `/World/jetbot/chassis` には `left_wheel_joint` と `right_wheel_joint` の 2 つの回転物理関節があります。

![ステージツリー](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_base_tut_gui_omnigraph_jetbot_joints.png)

1. 検索バーに `token` と入力し、**Constant Token** ノードを 2 つ追加します。
2. 1 つを選択し、Property ペインで値を `left_wheel_joint` に設定します。もう 1 つは `right_wheel_joint` に設定します。
3. 検索バーに `make array` と入力し、**Make Array** ノードを追加します。
4. Make Array ノードを選択し、入力セクションの **+** アイコンで 2 つ目の入力を追加します。**arraySize** を `2`、入力タイプを `token[]` に設定します。
5. Constant Token ノードを Make Array の `input0` / `input1` に接続し、Make Array の出力を Articulation Controller の **Joint Names** 入力に接続します。

### イベントノードを追加する

1. 検索バーに `playback` と入力し、**On Playback Tick** ノードを追加します。このノードはシミュレーション再生中、毎フレーム実行イベントを発行します。
2. On Playback Tick の **Tick** 出力を、両コントローラノードの **Exec In** 入力に接続します。
3. Differential Controller の **Velocity Command** 出力を、Articulation Controller の **Velocity Command** 入力に接続します。

![JetBot のシンプルな差動制御グラフ](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isaac_tutorial_omnigraph_jetbot_minimal.png)

### 動かしてみる

1. Play ボタンを押します。
2. グラフで Differential Controller ノードを選択します。
3. Property ペインで angular / linear velocity の値をドラッグまたは入力して変更すると、JetBot が動きます。

!!! tip "キーボード制御に挑戦"
    利用可能な OmniGraph ノードを調べて、キーボードで JetBot を制御するグラフを組んでみましょう。下図はその例です。<br>
    ![JetBot のキーボード制御グラフ](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isaac_tutorial_omnigraph_full.png)

## ステップ 3：OmniGraph ショートカットを使う

グラフをゼロから組むのは、特に反復作業では手間がかかります。よく使うグラフには**ショートカット**が用意されており、数クリックで複数ノードと接続を持つ複雑なグラフを生成できます。ショートカットは **Tools > Robotics > Omnigraph Controllers** にあります（詳細は [よく使う OmniGraph ショートカット](05_shortcuts.md) を参照）。

メニューショートカットから差動コントローラグラフを使う手順です。

1. JetBot を制御する既存の OmniGraph を削除（または無効化）します。
2. **Tools > Robotics > Omnigraph Controllers > Differential Controller** をクリックします。
3. パラメータの入力を求められます。**Articulation Root** に `/World/jetbot`、車輪間距離に `0.1125`、車輪半径に `0.03` を設定します。
4. JetBot は制御可能な関節が 2 つだけなので、残りのフィールドは空のままで構いません。
5. **Use Keyboard Control (WASD)** をオンにします。
6. **OK** をクリックしてグラフを生成します。生成されたグラフは `/Graph/differential_controller` で開けます。
7. Play を押し、キーボードの **WASD キー**で JetBot を動かせることを確認します。

![生成された JetBot コントローラグラフ](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_base_tut_gui_jetbot_controller_graph.webp)

## まとめ

このチュートリアルでは、次の内容を学びました。

- OmniGraph の基本概念とアクショングラフの構築
- Articulation Controller / Differential Controller で JetBot を制御する方法
- Constant Token / Make Array で関節名リストを作る方法
- OmniGraph ショートカットで差動コントローラグラフを自動生成する方法

## 次のステップ

- [OmniGraph の Python スクリプティング](02_omnigraph_scripting.md) で、グラフをコードから構築する方法を学びます。
- [カスタム Python ノード](03_custom_python_nodes.md) で、独自ノードの作り方を学びます。
- ショートカットの詳細は [よく使う OmniGraph ショートカット](05_shortcuts.md) を参照してください。
