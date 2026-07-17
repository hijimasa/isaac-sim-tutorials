---
title: ROS 2 Quality of Service（QoS）
---

# ROS 2 Quality of Service（QoS）

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- すべての ROS 2 OmniGraph ノードに対する **QoS（Quality of Service）**の設定
- プリセットの汎用 ROS 2 パブリッシャ Action Graph の作成
- QoS プロファイルを使った**スタティックパブリッシャ**（1 回だけ配信し、後から接続したサブスクライバにも届くパブリッシャ）の作成

## はじめに

### 前提条件

- [ROS 2 セットアップ](00_setup.md)が完了しており、Isaac Sim 起動前に必要な環境変数が設定され、ROS 2 エクステンションが有効であること
- ROS 2 公式ドキュメントの [Quality of Service settings](https://docs.ros.org/en/humble/Concepts/Intermediate/About-Quality-of-Service-Settings.html) を読んでおくこと

### 所要時間

約 15〜20 分

### 概要

!!! note "QoS とは"
    ROS 2 の QoS は、トピック通信の「品質」を制御する仕組みです。**reliability**（確実に届けるか、最新性を優先するか）、**durability**（後から接続したサブスクライバに過去のメッセージを届けるか）、**history / depth**（何件のメッセージを保持するか）などのポリシーの組み合わせで構成されます。パブリッシャとサブスクライバの QoS に互換性がないと、**トピックは見えているのにメッセージが届かない**という事態になるため、センサーデータの取りこぼしやナビゲーションスタックとの接続問題を調べるときに重要な知識です。

!!! warning "既知の問題：カスタムプロファイルの保存"
    ROS2 QoS Profile OmniGraph ノードには既知の問題があります。**他のフィールドを変更する前に、まず `createProfile` 入力を「Custom」に設定**しないと、カスタムプロファイルを USD に保存できません。

## ステップ 1：ROS 2 OmniGraph ノードに QoS プロファイルを設定する

1. 新しいステージを開きます。
2. **Tools > Robotics > ROS 2 OmniGraphs > Generic Publisher** を開き、**Generic Publisher Graph** で **Publish String** を選択して **OK** をクリックします。
3. 作成された Graph プリムを展開し、`ROS_GenericPub` を右クリックして **Open Graph** を選択します。

ROS2 Publisher をはじめとするすべての ROS 2 OmniGraph ノードには、**qosProfile** という文字列入力があります。この入力は **JSON 文字列**の形式で、パブリッシャ／サブスクライバの既定 QoS 設定は次のようになっています：

```json
{
    "history": "keepLast",
    "depth": 10,
    "reliability": "reliable",
    "durability": "volatile",
    "deadline": 0.0,
    "lifespan": 0.0,
    "liveliness": "systemDefault",
    "leaseDuration": 0.0
}
```

JSON として有効であるためには、`depth` は正の整数、`deadline`・`lifespan`・`leaseDuration` は float で指定する必要があります。

任意の ROS 2 OmniGraph ノードの `qosProfile` に有効な JSON 文字列を直接設定することもできますが、**ROS2 QoS Profile ノード**を使えばこの文字列を自動生成し、出力を複数のパブリッシャ／サブスクライバノードにまとめて接続できます。

4. Action Graph ウィンドウで **ROS2 QoS Profile** ノードを追加し、次のように接続します。**createProfile** 入力には複数の[プリセット QoS プロファイル](https://docs.ros.org/en/humble/Concepts/Intermediate/About-Quality-of-Service-Settings.html#qos-profiles)が用意されており、その他の入力は個別に設定してカスタムプロファイルを作るための QoS ポリシーです。

    ![QoS Profile ノードの接続](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isaac_tutorial_ros2_qos_connect.png)

5. **createProfile** を **Sensor Data** に設定し、**Play** でシミュレーションを開始します。

    !!! tip "UI が更新されないとき"
        ノードの値が UI に反映されない場合は、一度ノードの外側をクリックしてから、もう一度ノードをクリックしてみてください。

6. ROS 2 ターミナルで、トピックの QoS 設定を確認します：

    ```bash
    ros2 topic info /topic -v
    ```

    出力の QoS Profile が Isaac Sim で設定した内容と一致するはずです。

!!! note "depth が UNKNOWN と表示される場合"
    Fast DDS（旧 Fast RTPS）は既定で depth を保存しないため、depth ポリシーが UNKNOWN と表示されることがあります。depth の情報を取得したい場合は、Isaac Sim と ROS 2 ノードを Cyclone DDS または Zenoh で動かしてみてください（[セットアップページ](00_setup.md)参照）。`rmw_cyclonedds_cpp` と `rmw_zenoh_cpp` はどちらも、設定した depth 値を `ros2 topic info -v` で報告します。ミドルウェアを切り替えても UNKNOWN のままの場合は、ハードウェア構成に起因する可能性があります。

## ステップ 2：スタティックパブリッシャを作成する

スタティックパブリッシャは、**メッセージを 1 回だけ配信するが、後からトピックに接続したサブスクライバにも同じメッセージが届いてほしい**場合に便利です（マップやパラメータのような「一度出せば変わらない」データに向いています）。ROS 2 では durability ポリシーを **transientLocal** にすることで実現します。

1. 先ほどの Action Graph に **On Stage Event** と **Countdown** ノードを追加し、次のように接続します：

    ![スタティックパブリッシャの接続](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isaac_tutorial_ros2_qos_static_connect.png)

2. **On Stage Event** の **eventName** を `Simulation Start Play` に設定します。
3. **Countdown** ノードの **duration** を `3`、**period** を `1` に設定します。これでシミュレーション再生後に ROS2 Publisher ノードが 3 回 tick されます。ROS2 Publisher ノードは最初の 2 フレームをセットアップに使い、**3 フレーム目でメッセージを配信**します。
4. **ROS2 QoS Profile** ノードの **createProfile** を **Default for publisher/subscribers** に設定します。
5. **depth** ポリシーを `1` に、**durability** ポリシーを `transientLocal` に設定します。
6. **Play** でシミュレーションを開始します。
7. 新しい ROS 2 ターミナルで、スタティックメッセージを確認します：

    ```bash
    ros2 topic echo /topic
    ```

8. さらに別の ROS 2 ターミナルで同じコマンドを実行すると、**配信はとっくに終わっているのに、2 つ目のサブスクライバにも同じメッセージが届く**ことを確認できます。これが `transientLocal` の効果です。

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. **qosProfile** 入力の JSON 形式と **QoS Profile ノード**による生成
2. すべての ROS 2 OmniGraph ノードへの **QoS 設定**と `ros2 topic info -v` での確認
3. カスタム QoS プロファイル（depth=1、transientLocal）による**スタティックパブリッシャ**の作成

## 次のステップ

- [チュートリアル 12: ROS 2 ジョイント制御](12_manipulation.md) - 直接のジョイント制御でマニピュレータを動かし、ジョイント状態を取得する方法を学びます。
