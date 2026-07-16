---
title: スタンドアロンワークフローでの ROS 2 ブリッジ
---

# スタンドアロンワークフローでの ROS 2 ブリッジ

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- スタンドアロン Python での ROS 2 サンプルの実行方法
- **ROS 2 コンポーネントを手動でステップ実行**する方法（OnImpulseEvent による厳密な配信制御）

## はじめに

### 前提条件

- 公式ドキュメントの Workflows と [Core API チュートリアル 1: Hello World](../core_api/01_hello_world.md) を完了し、2 つのワークフロー（Standalone と Extension）を理解していること
- スタンドアロンワークフローで ROS 2 メッセージングを使うため、[セットアップページ](00_setup.md)の「内部ライブラリをターミナルから明示的に指定する」の環境変数を設定しておくこと

!!! warning "Windows での RViz2"
    Windows 10 / 11 では、マシンの構成によって RViz2 が正しく開かないことがあります（WSL2 の WSLg 経由での起動を推奨します）。

### 所要時間

約 20〜30 分

### 概要

**スタンドアロンワークフロー**は、Isaac Sim 自体を Python スクリプトから起動し、レンダリングや物理のステップをコードで明示的に制御する方式です。GUI 操作なしで再現可能なシミュレーションを回したい場合や、CI・バッチ処理・学習パイプラインに組み込みたい場合に使います。このチュートリアルでは、ROS 2 の配信タイミングを厳密に制御する方法と、これまでの GUI チュートリアルに対応したスタンドアロン版サンプル群の実行方法を学びます。

## ROS 2 コンポーネントを手動でステップ実行する

スタンドアロンスクリプティングは、シミュレーションステップを手動制御したい場合に最適です。**OnImpulseEvent** OmniGraph ノードを任意の ROS 2 OmniGraph ノードに接続すると、パブリッシャ／サブスクライバの実行タイミングを 1 回単位で正確に制御できます。

次の例は、ROS 2 Domain ID を 1 に指定した Clock パブリッシャを、インパルスイベントでのみ配信されるようにセットアップするものです：

```python
import omni.graph.core as og
# /ActionGraph のパスに新しいグラフを作成
og.Controller.edit(
    {"graph_path": "/ActionGraph", "evaluator_name": "execution"},
    {
        og.Controller.Keys.CREATE_NODES: [
            ("ReadSimTime", "isaacsim.core.nodes.IsaacReadSimulationTime"),
            ("Context", "isaacsim.ros2.bridge.ROS2Context"),
            ("PublishClock", "isaacsim.ros2.bridge.ROS2PublishClock"),
            ("OnImpulseEvent", "omni.graph.action.OnImpulseEvent"),
        ],
        og.Controller.Keys.CONNECT: [
            # OnImpulseEvent の実行出力を PublishClock に接続する。
            # これでインパルスイベントが発火したときだけ配信される
            ("OnImpulseEvent.outputs:execOut", "PublishClock.inputs:execIn"),
            # ReadSimTime のシミュレーション時刻を Clock パブリッシャに接続
            ("ReadSimTime.outputs:simulationTime", "PublishClock.inputs:timeStamp"),
            # ROS2 Context を接続し、指定した Domain ID で動作させる
            ("Context.outputs:context", "PublishClock.inputs:context"),
        ],
        og.Controller.Keys.SET_VALUES: [
            # Clock パブリッシャのトピック名を設定
            ("PublishClock.inputs:topicName", "/clock"),
            # Context ノードに Domain ID 1 を設定
            ("Context.inputs:domain_id", 1),
            # 上で設定した Domain ID を確実に使うため useDomainIDEnvVar を無効化
            ("Context.inputs:useDomainIDEnvVar", False),
        ],
    },
)
```

任意のフレームで次を実行すると、インパルスイベントが設定され、Clock パブリッシャが 1 回だけ tick されます：

```python
og.Controller.set(og.Controller.attribute("/ActionGraph/OnImpulseEvent.state:enableImpulse"), True)
```

!!! note "スタンドアロン実行と実時間のズレ"
    スタンドアロンスクリプティングではレンダリングと物理のステップを明示的に制御するため、各ステップの所要時間は計算負荷に依存し、実時間とは一致しないのが普通です。同じアプリケーションを GUI で動かした場合と体感速度が異なることがありますが、その場合は**シミュレーションクロックを基準**にしてください。

## サンプル集

これまでの GUI チュートリアルのいくつかは、スタンドアロン Python サンプルとしても提供されています。以下、実行手順です（いずれも Isaac Sim のインストールディレクトリで実行し、CTRL-C で終了します）。

### ROS 2 Clock

ROS 2 コンポーネントノードを含む Action Graph を作成し、**異なるレートで tick** するデモです：

```bash
./python.sh standalone_examples/api/isaacsim.ros2.bridge/clock.py
```

配信を確認します：

```bash
ros2 topic echo /sim_time
ros2 topic echo /manual_time
```

GUI での Clock パブリッシャの作り方は[チュートリアル 3: ROS 2 Clock](03_clock.md) を参照してください。

### ROS 2 カメラ（周期配信と手動配信）

Camera Helper / Camera Info Helper を使って、RGB・深度・カメラ情報を**異なるレートで**配信する 2 つのサンプルです。どちらも結果は同じですが、実現方法が異なります：

- 毎フレーム：Camera Info を配信
- 5 フレームごと：RGB 画像を配信
- 60 フレームごと：深度画像を配信

**周期配信版** — SDGPipeline 内の各 Isaac Simulation Gate ノードの実行レート（N フレームごと）を設定する方式（[チュートリアル 10](10_publish_rate.md) の仕組み）：

```bash
./python.sh standalone_examples/api/isaacsim.ros2.bridge/camera_periodic.py
```

**手動配信版** — 各パブリッシャと Simulation Gate の間に **Branch** ノードを挿入する方式。Branch ノードはカスタムゲートのように働き、任意のタイミングで有効／無効を切り替えられます。有効な間、接続された ROS 2 パブリッシャが tick されます：

```bash
./python.sh standalone_examples/api/isaacsim.ros2.bridge/camera_manual.py
```

**結果の可視化** — 新しい ROS 2 ターミナルで設定済み RViz2 を開きます：

```bash
rviz2 -d <ros2_ws>/src/isaac_tutorials/rviz2/camera_manual.rviz
```

!!! tip "深度画像が黒くなる場合"
    RViz2 の問題により、深度画像の表示に黒いフレームが現れることがあります。Isaac Sim が正しく深度画像を配信しているかは、`ros2 run rqt_image_view rqt_image_view` を実行してトピックを `/depth` に設定して確認してください。

### Carter Stereo

**既存の USD ステージ**（ROS 2 ノード入りの Action Graph を含む）を読み込んで、既定設定を変更する方法のデモです。ステレオカメラペアが自動的に有効になり、2 つ目のビューポートが UI にドッキングされます。毎フレーム、Clock・RTX Lidar のポイントクラウド・オドメトリ・TF・左右カメラが配信され、Twist サブスクライバが spin されます（Twist 指令の配信は 2 フレームごと）：

```bash
./python.sh standalone_examples/api/isaacsim.ros2.bridge/carter_stereo.py
```

可視化：

```bash
rviz2 -d <ros2_ws>/src/isaac_tutorials/rviz2/carter_stereo.rviz
```

Displays 内の **Right Camera - RGB** と **Left Camera - RGB** が有効になっていることを確認してください。

!!! tip "画像が RViz2 に表示されない場合"
    一部の画像が表示されない場合は、シミュレータ側で Stop → Play すると表示されることがあります。

### 複数ロボットの ROS 2 ナビゲーション

既存の USD ステージを実行する方法のデモです。hospital と office の 2 つの環境で実行できます：

```bash
# Hospital 環境
./python.sh standalone_examples/api/isaacsim.ros2.bridge/carter_multiple_robot_navigation.py --environment hospital

# Office 環境
./python.sh standalone_examples/api/isaacsim.ros2.bridge/carter_multiple_robot_navigation.py --environment office
```

インタラクティブ版（GUI での手順）は後の複数ロボットナビゲーションのチュートリアルで扱います。

### MoveIt 2

**複数の USD ステージの追加**と、ROS 2 コンポーネントノード入りの Action Graph を手動で作成・手動で tick する方法のデモです。毎フレーム、Clock・Joint State が配信され、Joint State サブスクライバが spin され、TF が配信されます：

```bash
./python.sh standalone_examples/api/isaacsim.ros2.bridge/moveit.py
```

### ROS 2 メッセージの受信

基本のサブスクライバ例です。空の ROS 2 メッセージを受信するたびに、シーン内のキューブがランダムな位置にテレポートします。レンダリング有効で動くので、シーンとキューブの動きを目視で確認できます：

```bash
./python.sh standalone_examples/api/isaacsim.ros2.bridge/subscriber.py
```

キューブのシーンが読み込まれたら、別のターミナルから空メッセージを 1 Hz で配信します：

```bash
ros2 topic pub -r 1 /move_cube std_msgs/msg/Empty
```

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. **OnImpulseEvent** ノードによる ROS 2 コンポーネントの手動ステップ実行
2. スタンドアロン Python サンプル（Clock／カメラ周期・手動配信／Carter Stereo／マルチロボットナビゲーション／MoveIt 2／サブスクライバ）の実行方法

## 次のステップ

- [チュートリアル 18: ROS 2 Navigation](18_navigation.md) - Nav2 と Isaac Sim を組み合わせたナビゲーションを学びます。
