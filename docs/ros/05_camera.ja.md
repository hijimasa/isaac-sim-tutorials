---
title: ROS 2 カメラ
---

# ROS 2 カメラ

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- シーンやロボットへの**カメラの追加**
- OmniGraph による**カメラパブリッシャ**の構築
- メニューショートカットによるカメラグラフの自動生成
- **グラウンドトゥルースの合成知覚データ**（深度・ポイントクラウド・バウンディングボックスなど）の ROS トピック配信

## はじめに

### 前提条件

- [ROS 2 セットアップ](00_setup.md)が完了していること（ROS 2 のインストール、ROS 2 エクステンションの有効化、Isaac Sim ROS 2 ワークスペースのビルド、環境変数の設定）
- ROS のトピックとパブリッシャ／サブスクライバの基本を理解していること
- カメラの追加方法（[ロボットセットアップ チュートリアル 4: カメラとセンサーの追加](../robot_setup/04_camera_sensors.md)）を完了していること
- [チュートリアル 1: URDF インポート: Turtlebot](01_urdf_import_turtlebot.md) を完了し、ステージに Turtlebot がある状態にしておくこと

!!! warning "Windows での RViz2"
    Windows 10 / 11 では、マシンの構成によって RViz2 が正しく開かないことがあります（WSL2 の WSLg 経由での起動を推奨します）。

### 所要時間

約 20〜30 分

### 概要

このチュートリアルでは、シーンに設置したカメラの映像を ROS 2 トピックとして配信する方法を学びます。RGB 画像だけでなく、深度・ポイントクラウド・バウンディングボックスといった**グラウンドトゥルース付きの合成知覚データ**を配信できるのが、シミュレータならではの強みです。

## ステップ 1：カメラをセットアップする

ビューポートに表示されている既定のカメラは **Perspective** カメラです。ビューポート左上の **Camera** ボタンをクリックすると、Top / Front / Right などのプリセット視点も選べます。

このチュートリアルでは、部屋を異なる視点から見る 2 つの固定カメラを追加し、`Camera_1`、`Camera_2` と名前を付けます。カメラの追加手順は[ロボットセットアップ チュートリアル 4](../robot_setup/04_camera_sensors.md)を参照してください。

複数のカメラ映像を同時に確認するには、ビューポートを追加します：

1. **Window > Viewports > Viewport 2** で 2 つ目のビューポートを開きます。
2. ビューポート左上の **Cameras** ボタンから表示したいカメラを選択します。

![ビューポートの追加](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_ros_tut_gui_camera_add_viewport.webp)

## ステップ 2：RGB パブリッシャのグラフを構築する

1. **Window > Graph Editors > Action Graph** を開きます。
2. **New Action Graph** アイコンをクリックします（既存のグラフに追加したい場合は **Edit Action Graph**）。
3. 次の画像のノードと接続でグラフを構築し、下の表のパラメータを設定します：

    ![カメラパブリッシャグラフ](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isaac_tutorial_ros2_camera_graph.png)

| ノード | 入力フィールド | 値 |
|---|---|---|
| Isaac Create Render Product | cameraPrim | /World/Camera_1 |
| Isaac Create Render Product | enabled | True |
| ROS 2 Camera Helper | type | rgb |
| ROS 2 Camera Helper | topicName | rgb |
| ROS 2 Camera Helper | frameId | turtle |

このグラフが tick されると、`Camera_1` に割り当てられたレンダープロダクトが自動的に作成されます。

### 各ノードの役割

| ノード | 役割 |
|---|---|
| **On Playback Tick** | シミュレーション再生中、毎ステップ tick を発行する |
| **ROS 2 Context** | Domain ID（既定 0、または `ROS_DOMAIN_ID` 環境変数）でコンテキストを作成する |
| **Isaac Create Render Product** | 指定したカメラプリムからレンダリングデータを取得する「レンダープロダクト」プリムを作成し、そのパスを出力する。**enabled** のオン／オフでレンダリングを制御できる |
| **Isaac Run One Simulation Frame** | パイプラインの構築処理を開始時に 1 回だけ実行させる |
| **ROS 2 Camera Helper** | 配信するデータの種類（type）と配信先トピック（topicName）を指定する |

!!! note "Camera Helper ノードの正体：SDGPipeline"
    Camera Helper ノードは、複雑な後処理ネットワークをユーザーから隠蔽する「ヘルパー」です。Camera Helper ノードを接続した状態で **Play** を押すと、Action Graph ウィンドウ左上のアイコンからグラフ一覧を開いたとき、`/Render/PostProcessing/SDGPipeline` という新しいグラフが現れます。

    このグラフは Camera Helper が自動生成したもので、レンダラーから必要なデータを取り出し、処理して、対応する ROS パブリッシャに送っています。SDGPipeline は**実行中のセッションにのみ存在**し、アセットの一部として保存されず、Stage ツリーにも表示されません。

## ステップ 3：深度などのグラウンドトゥルースデータを配信する

RGB 画像に加えて、任意のカメラから次の合成センサー・知覚情報を配信できます：

- **Depth**（深度）
- **Point Cloud**（ポイントクラウド）
- **BoundingBox 2D Tight / 2D Loose / 3D**（バウンディングボックス）
- **Semantic labels**（セマンティックラベル）
- **Instance Labels**（インスタンスラベル）

データの種類は、Camera Helper ノードの Property タブにある **type** フィールドのドロップダウンで指定します。**1 つの Camera Helper ノードが取得できるデータは 1 種類だけ**なので、複数の種類を配信するにはノードを種類ぶん用意します。

!!! warning "type は一度アクティブ化すると変更できない"
    Camera Helper ノードの type を指定してアクティブ化（シミュレーションを開始して SDGPipeline が生成）された後は、**type を変更してノードを再利用することはできません**。新しいノードを使うか、ステージをリロードして変更後の type で SDGPipeline を再生成してください。

!!! note "バウンディングボックス・ラベル配信の前提"
    - バウンディングボックスやラベルを配信するには、シーンに**セマンティックアノテーション**が付いている必要があります。公式の Isaac Sim Replicator チュートリアルでアノテーション方法を確認してください。
    - BoundingBox パブリッシャノードは `vision_msgs` に依存します。システムにインストールされていることを確認してください（[セットアップページ](00_setup.md)参照）。
    - 各アノテータが使う単位系は公式の omni.replicator ドキュメント（Annotators Details）を参照してください。

複数カメラで複数の ROS トピックを配信する例は、Content ブラウザの **Isaac Sim > Samples > ROS2 > Scenario > turtlebot_tutorial.usd** で確認できます。

### Camera Info Helper ノードとカメラ内部パラメータ

**Camera Info Helper** ノードは、次の式でカメラの内部パラメータ行列 K、P、R を計算して `camera_info` トピックとして配信します：

$$
f_x = \frac{width \times focalLength}{horizontalAperture},\quad
f_y = \frac{height \times focalLength}{verticalAperture},\quad
c_x = \frac{width}{2},\quad
c_y = \frac{height}{2}
$$

**K 行列（内部パラメータ行列、3×3）：**

$$
K = \begin{pmatrix} f_x & 0 & c_x \\ 0 & f_y & c_y \\ 0 & 0 & 1 \end{pmatrix}
$$

**P 行列（射影行列、3×4）：**

$$
P = \begin{pmatrix} f_x & 0 & c_x & T_x \\ 0 & f_y & c_y & T_y \\ 0 & 0 & 1 & 0 \end{pmatrix}
$$

ステレオカメラの場合、2 台目のカメラの 1 台目に対するオフセットが $T_x$、$T_y$ に入ります（ノードに 2 つのレンダープロダクトを接続すると自動計算されます）。単眼カメラでは $T_x = T_y = 0$ です。

**R 行列（平行化行列、3×3）** は、ステレオ画像のエピポーラ線が平行になるようにカメラ座標系を理想的なステレオ画像平面に合わせる回転行列で、ステレオカメラでのみ使われます。

## ステップ 4：グラフショートカットで自動生成する

複数のカメラセンサーグラフは、メニューショートカットからまとめて生成できます：

1. **Tools > Robotics > ROS 2 OmniGraphs > Camera** を開きます（表示されない場合は ROS 2 ブリッジを有効化してください）。
2. ポップアップで **Graph Path**、**Camera Prim**、**frameId**、（あれば）**Node Namespace** を指定し、配信したいデータの種類にチェックを入れます。
3. 既存のグラフにノードを追加したい場合は **Add to an existing graph?** にチェックを入れます。既存の tick ノード・コンテキストノード・シミュレーション時刻ノードがあればそれらを再利用してくれます。

![カメラグラフショートカット](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isaac_tutorial_ros2_camera_og_shortcut.png)

## ステップ 5：ROS 接続を確認する

**Play** を押した状態で、次の方法で配信を確認します：

生データの確認：

```bash
ros2 topic echo /rgb
```

画像の表示（rqt_image_view）。なお `/depth` トピックは、ステップ 2 のグラフ（RGB のみ）には含まれていません。深度画像を確認する場合は、ステップ 3 で説明したように `type` を `depth` に設定したカメラ配信ノード一式を追加して深度を配信しておいてください（RGB だけを確認するなら引数を `/rgb` に変えます）：

```bash
ros2 run rqt_image_view rqt_image_view /depth
```

RViz2 での確認：

1. ROS 2 を source したターミナルで `rviz2` を起動します。
2. **Image** ディスプレイを追加し、トピックを `rgb` に設定します。

![RViz でのカメラ画像](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isaac_tutorial_ros2_rviz_camera.png)

!!! tip "トラブルシューティング：深度画像が白黒にしか見えない"
    深度画像が白と黒の領域だけになる場合は、視野内に「無限遠」の深度が含まれていてコントラストが偏っている可能性が高いです。画像内の深度の範囲が限られるように視野を調整してください。

## その他の配信オプション

オンデマンド配信や指定レートでの定期配信を行うには Python スクリプティングが必要です。次のチュートリアルで扱います。

## まとめ

このチュートリアルでは、ROS 2 でのカメラ・知覚データの配信方法を扱いました：

1. カメラの追加と**複数ビューポート**での確認
2. **Camera Helper ノード**による RGB パブリッシャの構築と SDGPipeline の仕組み
3. **深度・ポイントクラウド・バウンディングボックス**などのグラウンドトゥルース配信
4. **Camera Info** の内部パラメータ行列の計算式
5. グラフショートカットと **RViz2 / rqt_image_view** での確認

## 次のステップ

- [チュートリアル 6: カメラへのノイズ付加](06_camera_noise.md) - よりリアルなセンサーシミュレーションのため、カメラ画像にノイズを加える方法を学びます。

### さらに学ぶには

- 合成データ生成の詳細は公式の Replicator チュートリアルシリーズを参照してください。
