---
title: よく使う OmniGraph ショートカット
---

# よく使う OmniGraph ショートカット

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- OmniGraph ショートカットでコントローラグラフを数クリックで生成する方法
- Articulation（関節位置・速度）/ Differential / Gripper 各コントローラの設定項目
- 各コントローラの使い方とチューニングのポイント

## はじめに

### 前提条件

- [Isaac Sim OmniGraph チュートリアル](01_omnigraph_tutorial.md) を理解していること
- Articulation とロボットの関節構造の基礎を理解していること

### 所要時間

約 15〜20 分

### 概要

Isaac Sim には、よく使う OmniGraph を生成する**ショートカット**が用意されています。**Tools > Robotics > Omnigraph Controllers** から、作成したいグラフを選択すると、最小限のパラメータの入力を求められ、グラフが自動生成されます。

用意されているコントローラグラフは次のとおりです。

- **Joint Position Controller**（関節位置コントローラ）
- **Joint Velocity Controller**（関節速度コントローラ）
- **Differential Controller**（差動コントローラ）
- **Open Loop Gripper Controller**（オープンループグリッパコントローラ）

!!! note "ショートカット利用時の注意"
    - 同じタスクや同じロボットを制御するグラフの重複は検出されません。シーン内でグラフが一意になるように自分で管理する必要があります。
    - これらはあくまでグラフ生成の**ショートカット**です。生成後にグラフを自由に改変して用途に合わせられます。

!!! tip "Python スクリプトを確認する"
    ポップアップウィンドウ下部の **Python Script for Graph Generation** の横のアイコンをクリックすると、そのショートカットのグラフ生成に使われる Python スクリプトが開きます。生成処理は `make_graph()` で行われます。

## Articulation コントローラ（位置・速度）

位置・速度コントローラは、どちらも Articulation 内の各関節に直接コマンドを発行します。

| 項目 | 説明 |
|---|---|
| **Robot Prim** | ロボットの親 prim |
| **Graph Path** | 生成グラフのパス。既定は `/Graph/{type}_controller`。既存パスがあれば末尾に番号を付けて次の空きパスを探す |
| **Add to Existing Graph**（省略可） | 既定 False。有効にすると既存グラフにノードを追加し、既存の tick ノードがあれば再利用する（コントローラノードは既存の有無に関わらず新規追加） |

### 使い方

1. 生成されたグラフの下の **JointCommandArray** ノードを選択します。
2. Play を押してシミュレーションを開始します。
3. Property タブで JointCommandArray ノードの値を変更してロボットを動かします。

USD に位置・速度の初期ターゲットが保存されている場合、Play を押すとすぐにそのターゲットへ向かって動きます。

## Differential コントローラ

Differential Controller は、線速度・角速度を受け取り、各車輪の速度に変換します。

| 項目 | 説明 |
|---|---|
| **Robot Prim** | ロボットの prim |
| **Graph Path** | 生成グラフのパス（既定 `/Graph/{type}_controller`） |
| **Wheel Radius** | 車輪半径（メートル） |
| **Distance between wheels** | 2 輪間の距離（メートル） |
| **Right/Left Joint Names**（省略可） | 右・左車輪を制御する関節名 |
| **Right/Left Joint Index**（省略可） | Articulation チェーン内の右・左車輪関節のインデックス |
| **Use Keyboard Control**（省略可） | 有効にすると WASD キー入力で前後進・左右旋回するグラフも生成 |
| **Add to Existing Graph**（省略可） | 既定 False。既存グラフへの追加 |

### 使い方

- 制御可能な関節が 2 つだけのロボットでは、関節名・インデックスの指定は不要です。Articulation チェーンに複数の駆動関節があるロボットでは、右・左車輪を制御する関節の名前かインデックスを指定する必要があります。
- WASD キーボード制御を含めなかった場合は、生成された **DifferentialController** ノードの **Desired Angular Velocity** / **Desired Linear Velocity** を手動で変更してテストできます。

![差動コントローラの手動入力](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isaac_differential_controller_manual_inputs.png)

- WASD キーボード制御を使う場合、キーボードのバイナリ入力を車両サイズに見合った線速度・角速度にスケールする 2 つの値が **ScaleLinear** / **ScaleAngular** ノード内にあります。旋回コマンドが前後進コマンドと同程度の車輪速度変化になるよう調整するとよいでしょう。

![スケール値の調整](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isaac_differential_controller_scale.png)

!!! tip
    Isaac Sim アセットを使う場合、車輪半径と車輪間距離の既定値は Robot Assets の Wheeled Robots のページ下部で確認できます。

## Gripper コントローラ

Gripper Controller は、指ごとに 1 自由度のみを持つエンドエフェクタに対応します。平行ジョーグリッパのほか、各指が 1 自由度の多指・多自由度ハンドも含まれます。

| 項目 | 説明 |
|---|---|
| **Parent Robot** | グリッパを含むロボット。グリッパ単体でも、アームの一部ならマニピュレータ全体の prim でもよい |
| **Gripper Root** | すべてのグリッパ関節を含む prim |
| **Graph Path** | 生成グラフのパス（既定 `/Graph/{type}_controller`） |
| **Gripper Speed** | グリッパの開閉速度（メートル/秒 または ラジアン/秒） |
| **Gripper Joint Names** | グリッパの指を制御する関節名（カンマ区切りで全て列挙） |
| **Open/Close Position Limit**（省略可） | 完全開放とみなす関節位置（prismatic はメートル、revolute はラジアン）。空欄なら USD の関節リミットを既定使用 |
| **Use Keyboard Control**（省略可） | 有効にすると「O」「C」「N」キーで開く・閉じる・停止するグラフを生成 |
| **Add to Existing Graph**（省略可） | 既定 False。既存グラフへの追加 |

![Gripper コントローラ](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_ref_gui_omnigraph_gripper_controller.png)

### 使い方

- 関節リミットが与えられない場合、USD の関節リミットが既定で使われます。Open/Close の位置リミットが逆に指定されても自動補正されます。コントローラは「開放位置のリミット > 閉塞位置」を前提とするため、逆のグリッパでは開閉の定義を調整するか、Python スクリプトを改変する必要があります。
- ショートカットでは**一様な速度・同一の関節リミット**のみサポートされます。指ごとに可変速度や異なるリミットを使いたい場合は、速度・関節リミット入力を配列にしてグラフを改変します。
- アームとグリッパの両方を含む Articulation チェーンで、アームを Articulation Position Controller、グリッパを Gripper Controller で個別に制御したい場合は、アームコントローラグラフからグリッパを制御する関節を除外し、2 つのグラフ間で競合がないことを確認します。

!!! note "ROS グラフのショートカット"
    ROS グラフの使い方については、各 [ROS 2 チュートリアル](../ros/index.md)（Linux / Windows）を参照してください。

## まとめ

このチュートリアルでは、次の内容を学びました。

- **Tools > Robotics > Omnigraph Controllers** から各種コントローラグラフを数クリックで生成できること
- Articulation（位置・速度）/ Differential / Gripper コントローラの設定項目と使い方
- WASD / キーボード制御やスケール値のチューニングのポイント

## 次のステップ

- ロボット全体の制御は [Isaac Sim OmniGraph チュートリアル](01_omnigraph_tutorial.md) に戻って復習できます。
- コードからグラフを生成する方法は [OmniGraph の Python スクリプティング](02_omnigraph_scripting.md) を参照してください。
