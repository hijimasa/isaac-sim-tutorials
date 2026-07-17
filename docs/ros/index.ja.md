---
title: ROS 2 チュートリアル
---

# ROS 2 チュートリアル

<span class="badge badge-intermediate">Intermediate</span>

Isaac Sim と ROS 2 を連携させるためのチュートリアルです（Linux / Windows 対応）。

## 概要

Isaac Sim には **ROS 2 ブリッジ**が用意されており、OmniGraph ノードを通じてシミュレーション内のロボット・センサーと ROS 2 ネットワークをつなぐことができます。このシリーズでは、URDF のインポートから始めて、Twist メッセージによる操縦、時刻同期、センサーデータのパブリッシュ、Nav2 / MoveIt 2 との接続、カスタムメッセージまでを段階的に学びます。

### 前提条件

シリーズ全体を通して、ROS 2 のインストールと Isaac Sim との接続設定が完了していることが前提です。**Windows では Pixi によるネイティブ ROS 2（Jazzy）が正式サポート**されました（従来の WSL2 方式は非推奨扱いです）。まず[セットアップページ](00_setup.md)を完了してください。

## チュートリアル

### セットアップ

!!! example "[ROS 2 セットアップ（Linux / Windows）](00_setup.md)"
    ROS 2 のインストールから Isaac Sim との接続確認までを、Linux と Windows（Pixi / WSL2）それぞれの手順で解説します。シリーズを始める前に必ず完了してください。

### インポートと操縦の基本

!!! example "[チュートリアル 1: URDF インポート: Turtlebot](01_urdf_import_turtlebot.md)"
    Turtlebot3 の URDF を xacro で前処理して Isaac Sim にインポートし、走行できる状態までロボットを調整します。

!!! example "[チュートリアル 2: ROS 2 メッセージで TurtleBot を駆動する](02_drive_turtlebot.md)"
    Differential Controller / Articulation Controller と ROS 2 ブリッジの OmniGraph ノードを組み合わせ、Twist メッセージ（/cmd_vel）でロボットを操縦します。

### タイミング

!!! example "[チュートリアル 3: ROS 2 Clock](03_clock.md)"
    `/clock` トピックと `use_sim_time` パラメータによる時刻同期の仕組みを学び、Clock のパブリッシャ／サブスクライバを構築します。

!!! example "[チュートリアル 4: ROS 2 RTF のパブリッシュ](04_rtf.md)"
    シミュレーションの実時間比（Real Time Factor）を Float32 メッセージとして配信します。

### センサーと制御

!!! example "[チュートリアル 5: ROS 2 カメラ](05_camera.md)"
    Camera Helper ノードで RGB・深度・ポイントクラウド・バウンディングボックスなどのグラウンドトゥルースデータを配信します。

!!! example "[チュートリアル 6: カメラへのノイズ付加](06_camera_noise.md)"
    Replicator の Augmentation でカメラ画像にノイズを加えて配信します。

!!! example "[チュートリアル 7: カメラデータのパブリッシュ](07_camera_publishing.md)"
    Python スクリプトからカメラの各種パブリッシャ（CameraInfo・RGB・深度・ポイントクラウド・TF）をセットアップします（配信レートはカメラの tick_rate で決まります）。

!!! example "[チュートリアル 8: RTX Lidar センサー](08_rtx_lidar.md)"
    レイトレーシングベースの RTX Lidar を追加し、LaserScan / PointCloud2 を配信して、複数センサーを RViz2 でまとめて可視化します。

!!! example "[チュートリアル 9: ROS 2 Transform ツリーとオドメトリ](09_tf.md)"
    TF パブリッシャの使い分け、オドメトリの配信、world → odom → base_link の TF 構成、TF Viewer での可視化を学びます。

!!! example "[チュートリアル 10: ROS 2 パブリッシュレートの設定](10_publish_rate.md)"
    Simulation Gate（非 RTX センサー）と omni:sensor:tickRate（RTX センサー）でセンサーごとの配信レートを設定し、シミュレーションフレームレートを制御します。

!!! example "[チュートリアル 11: ROS 2 Quality of Service（QoS）](11_qos.md)"
    QoS プロファイルの設定方法と、transientLocal を使ったスタティックパブリッシャの作成を学びます。

!!! example "[チュートリアル 12: ROS 2 ジョイント制御](12_manipulation.md)"
    Franka を対象に、Joint State パブリッシャ／サブスクライバを UI・ショートカット・Python API の 3 通りで構築し、位置制御と速度制御を混在させます。

!!! example "[チュートリアル 13: NameOverride 属性](13_name_override.md)"
    isaac:nameOverride 属性で、プリム名を変えずに ROS へ配信する名前だけをカスタマイズします。

!!! example "[チュートリアル 14: ROS 2 Ackermann コントローラ](14_ackermann.md)"
    アッカーマンステアリング車両（Leatherback）を AckermannDriveStamped で駆動し、Twist 変換でキーボード操縦します。

!!! example "[チュートリアル 15: 自動 ROS 2 ネームスペース生成](15_auto_namespace.md)"
    isaac:namespace 属性によるネームスペースの自動生成で、マルチロボット構成を属性 1 箇所の変更で実現します。

!!! example "[チュートリアル 16: 強化学習ポリシーの ROS 2 実行](16_rl_controller.md)"
    H1 の歩行ポリシーを外部 ROS 2 ノードで推論させ、物理ステップ同期の OmniGraph で観測・行動をやり取りします。

### スタンドアロンワークフロー

!!! example "[チュートリアル 17: スタンドアロンワークフローでの ROS 2 ブリッジ](17_standalone_python.md)"
    OnImpulseEvent による配信タイミングの厳密制御と、スタンドアロン Python サンプル集の実行方法を学びます。

### ROS 2 スタックとの接続

!!! example "[チュートリアル 18: ROS 2 Navigation（Nav2）](18_navigation.md)"
    占有マップの生成から Nav2 の実行、ゴールのプログラム送信、Waypoint Follower までを学びます。

!!! example "[チュートリアル 19: 複数ロボットの ROS 2 Navigation](19_multi_navigation.md)"
    ネームスペースを使って複数の Nova Carter を同時にナビゲーションさせます。

!!! example "[チュートリアル 20: Block World Generator を使った ROS 2 Navigation](20_navigation_block_world.md)"
    2D 占有マップから 3D ワールドを生成し、その中で Nav2 を実行します。

!!! example "[チュートリアル 21: MoveIt 2](21_moveit.md)"
    Franka を MoveIt 2 に接続し、ハンドとアームのモーションプランニングを実行します。

### その他の ROS 2 OmniGraph ノード

!!! example "[チュートリアル 22: ROS 2 汎用パブリッシャとサブスクライバ](22_generic_pub_sub.md)"
    任意のメッセージ型を配信・購読できる汎用ノードの使い方を、Joint State とオブジェクト姿勢の例で学びます。

!!! example "[チュートリアル 23: ROS 2 汎用サービスサーバとクライアント](23_generic_server_client.md)"
    任意の型のサービスを Isaac Sim で提供・呼び出しする汎用サーバー／クライアントノードを学びます。

!!! example "[チュートリアル 24: プリム属性を操作する ROS 2 サービス](24_prim_service.md)"
    プリムの一覧取得や属性の読み書きを ROS 2 サービスとして外部に公開します。

### カスタマイズ

!!! example "[チュートリアル 25: ROS 2 Python カスタムメッセージ](25_custom_message.md)"
    Python 3.12 でビルドしたカスタムメッセージパッケージを rclpy から使います（Linux / Windows は Pixi 方式のみ）。

!!! example "[チュートリアル 26: ROS 2 Python カスタム OmniGraph ノード](26_custom_python_node.md)"
    rclpy で購読と計算を行うカスタム OmniGraph Python ノードをエクステンションとして作成します。

!!! example "[チュートリアル 27: ROS 2 カスタム C++ OmniGraph ノード](27_custom_cpp_node.md)"
    Kit Extension Template C++ と rcl API で C++ のカスタムノードをビルドします（Linux + Humble のみ）。

### デプロイとシミュレーション制御

!!! example "[チュートリアル 28: ROS 2 Launch](28_launch.md)"
    ROS 2 launch ファイルから Isaac Sim を起動し、Nav2 との統合起動まで 1 コマンドで行います（Linux のみ）。

!!! example "[チュートリアル 29: ROS 2 Simulation Control](29_simulation_control.md)"
    標準の simulation_interfaces を使い、シミュレーション自体（状態・エンティティ・ワールド）を ROS 2 から制御します。
