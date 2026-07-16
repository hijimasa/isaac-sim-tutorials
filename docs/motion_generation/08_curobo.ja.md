---
title: cuRobo と cuMotion
---

# cuRobo と cuMotion

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- cuRobo が GPU 加速のモーション生成ライブラリであること
- cuMotion と cuRobo の関係
- cuRobo のインストールと利用の概要（衝突回避 IK・モーションプランニング・反応制御）
- nvblox と組み合わせた障害物認識モーション生成

## はじめに

### 前提条件

- [マニピュレータロボットの追加](../core_api/04_adding_a_manipulator_robot.md) を完了していること

### 所要時間

約 10 分（インストールを除く）

### 概要

**cuRobo** は、NVIDIA Research が開発した、マニピュレータ向けの高性能・GPU 加速のモーション生成ライブラリです。NVIDIA Isaac Sim と直接インターフェースするスタンドアロンの Python ライブラリで、シミュレーションでのテストと実機へのデプロイの両方を簡素化します。

**NVIDIA cuMotion**（Isaac 3.0 で Developer Preview として提供）は、マニピュレータ向けの本番向けモーション生成パッケージです。現行バージョンは cuRobo をバックエンドとして利用し、MoveIt 2 のプラグインと一連の ROS 2 パッケージを通じて衝突回避モーションプランニングを提供します。

![cuRobo](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isaac_tutorial_advanced_cuRobo.gif)

!!! warning "既知の制限"
    - cuRobo 内での NvBlox 例には既知の問題があります。cuRobo の更新で解決され次第、このチュートリアルも更新されます。
    - この cuRobo チュートリアルは **aarch64 プラットフォームではサポートされていません**。

## インストール

cuRobo および必要なライブラリのインストールは、cuRobo 公式のインストール手順に従ってください。cuRobo は NVIDIA Isaac Sim 2022.2.1 以降をサポートします。Isaac Sim は、ワークステーション向けインストール手順に従って導入します。

## 例

### Isaac Sim と cuRobo を使う

cuRobo のドキュメントの **「Using Isaac Sim」** セクションに、cuRobo が Isaac Sim とどうインターフェースするかの概要と、次を示す一連の Standalone 例があります。

- 衝突チェック（collision checking）
- モーション生成（motion generation）
- 逆運動学（inverse kinematics）
- モデル予測経路積分制御（MPPI: Model Predictive Path Integral。サンプリングベースのモデル予測制御手法）
- 複数アームのリーチング（multi-arm reaching）

### Isaac Sim + cuRobo + nvblox

cuRobo のドキュメントの **「Using with Depth Camera」** セクションに、Isaac Sim での障害物認識モーション生成の例があります。

- nvblox から事前生成した符号付き距離場（SDF）を使う例
- 実機の RealSense 深度カメラを使い、nvblox でオンラインマッピングする例

!!! note "cuMotion + ROS 2"
    ROS 2 ブリッジ経由で cuMotion を Isaac Sim と使う例は、Isaac ROS ドキュメントの該当セクションを参照してください（Isaac 3.0 時点ではやや限定的ですが、将来のリリースで拡充予定です）。

## まとめ

このチュートリアルでは、次の内容を学びました。

- cuRobo が GPU 加速のスタンドアロン Python モーション生成ライブラリであること
- cuMotion が cuRobo をバックエンドに MoveIt 2 / ROS 2 と統合されること
- 衝突回避 IK・モーションプランニング・MPPI・複数アームなどの例の所在
- nvblox と組み合わせた障害物認識モーション生成

## 次のステップ

- Lula ベースのモーション生成に戻るには [モーション生成の概要](01_overview.md) を参照してください。
- ROS 2 連携については [ROS 2 チュートリアル](../ros/index.md)（MoveIt 2 など）も参考になります。
