---
title: ROS 2 Clock
---

# ROS 2 Clock

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- ROS 2 における**時刻同期**（`/clock` トピックと `use_sim_time` パラメータ）の仕組み
- シミュレーション時刻を **Clock メッセージ**として ROS 2 にパブリッシュする方法
- ROS 2 の Clock メッセージを**サブスクライブ**する方法
- メニューショートカットによる Clock グラフの自動生成

## はじめに

### 前提条件

- [ROS 2 セットアップ](00_setup.md)が完了していること
- 複数マシンで使う場合は、Isaac Sim の起動前と、ROS メッセージを送受信するすべてのターミナルで `FASTRTPS_DEFAULT_PROFILES_FILE` 環境変数を設定しておくこと（[セットアップページ](00_setup.md)の該当節を参照）

!!! warning "Windows での RViz2"
    Windows 10 / 11 では、マシンの構成によって RViz2 が正しく開かないことがあります（WSL2 の WSLg 経由での起動を推奨します）。

### 所要時間

約 15 分

### 概要

シミュレータと ROS 2 ノード群を連携させるとき、**時刻を実時間ではなくシミュレーション時間に揃える**ことが重要になります。シミュレーションは実時間より速くも遅くも進み得るため、時刻がズレていると TF の補間やセンサーデータのタイムスタンプ照合が破綻するからです。このチュートリアルでは、Isaac Sim のシミュレーション時刻を `/clock` トピックとして配信し、ROS 2 ノード側で利用する方法を学びます。

## シミュレーション時刻と /clock トピック

外部の ROS 2 ノードがシミュレーション時刻に同期するには、通常 `/clock` トピックを使います。RViz2 をはじめ多くの ROS 2 ノードは **`use_sim_time`** パラメータを持っており、これを `True` に設定すると、そのノードは `/clock` トピックの購読を開始し、パブリッシュされたシミュレーション時刻に同期するようになります。

`use_sim_time` は ROS 2 の launch ファイルで設定するか、ROS 2 を source した新しいターミナルで次のコマンドで設定できます：

```bash
ros2 param set /node_name use_sim_time true
```

`/node_name` は実際に動かしているノード名に置き換えてください。ターミナルから設定する場合、**対象のノードが先に起動している**必要があります。

## ステップ 1：ROS 2 Clock パブリッシャを動かす

1. **Window > Graph Editors > Action Graph** で Action Graph を作成します。
2. 次の OmniGraph ノードをグラフに追加して接続します：

| ノード | 役割 |
|---|---|
| **On Playback Tick** | シミュレーションの毎フレーム、他のノードを実行する |
| **ROS2 Context** | 指定した Domain ID（または `ROS_DOMAIN_ID` 環境変数）でコンテキストを作成する |
| **Isaac Read Simulation Time** | 現在のシミュレーション時刻を取得する |
| **ROS2 Publish Clock** | シミュレーション時刻を `/clock` トピックにパブリッシュする |

![Clock パブリッシャグラフ](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_ros_tut_gui_ros2_clock_publisher.png)

!!! note "シミュレーション時刻は既定で単調増加する"
    **Isaac Read Simulation Time** が返す時刻は、既定ではシミュレーションを停止して再度 Play しても 0 に戻らず、増え続けます（単調増加）。これは、リセットで時刻が巻き戻ることによる問題（TF の順序逆転など）を防ぐためです。リセットのたびに時刻を 0 から始めたい場合は、このノードの **resetOnStop** を `True` に設定してください。

3. RViz2 で同期を確認します。新しい ROS 2 を source したターミナルで RViz2 を起動します：

    ```bash
    ros2 run rviz2 rviz2
    ```

    RViz ウィンドウ下部の **ROS Time** と **ROS Elapsed** に注目してください。この時点では実時間（Wall Time / Wall Elapsed とほぼ同じ値）が表示されています。

4. Isaac Sim のシミュレーションが**停止している**状態で、別の ROS 2 ターミナルから RViz ノードの `use_sim_time` を有効にします：

    ```bash
    ros2 param set /rviz use_sim_time true
    ```

    RViz の **ROS Time** と **ROS Elapsed** がどちらも 0 になることを確認します（まだ `/clock` が配信されていないため）。

5. Isaac Sim で **Play** をクリックします。RViz の **ROS Time** が、Isaac Sim から `/clock` トピック経由で配信されるシミュレーション時刻と一致するようになります。

## ステップ 2：システム時刻をパブリッシュする

シミュレーション時刻の配信が最も一般的ですが、ワークフローによってはメッセージに**システム時刻（実時間）**を載せたい場合もあります。その場合は、グラフの **Isaac Read Simulation Time** を **Isaac Read System Time** に置き換えるだけです：

1. Action Graph を作成し、**On Playback Tick**、**ROS2 Context**、**Isaac Read System Time**、**ROS2 Publish Clock** を接続します。

    ![システム時刻のパブリッシュ](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_ros_tut_gui_ros2_clock_publisher_system_time.png)

2. **Play** をクリックし、ROS 2 ターミナルで配信内容を確認します：

    ```bash
    ros2 topic echo /clock
    ```

!!! note "Camera Helper / RTX Lidar Helper ノードでシステム時刻を使うには"
    後のチュートリアルで登場する **ROS 2 Camera Helper** ノードと **ROS2 RTX Lidar Helper** ノードは、センサー配信パイプラインを自動生成します。これらのパブリッシャにシステム時刻のタイムスタンプを使わせたい場合は、各ノードの **useSystemTime** 入力を `True` に設定してください。

## ステップ 3：ROS 2 Clock サブスクライバを動かす

今度は逆に、外部からの時刻を Isaac Sim 側で受信してみます。

1. 新しいステージを開き、Action Graph を作成します。
2. **On Playback Tick**、**ROS2 Context**、**ROS2 Subscribe Clock**（外部のタイムスタンプデータを購読する）を接続します。

    ![Clock サブスクライバグラフ](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_ros_tut_gui_ros2_clock_subscriber.png)

3. **Play** をクリックしてシミュレーションを開始します。Action Graph 内で **ROS2 Subscribe Clock** ノードを選択し、Property ウィンドウで **timeStamp** 出力が 0 であることを確認します。
4. 新しい ROS 2 ターミナルから、Clock メッセージを 1 回だけ手動でパブリッシュします：

    ```bash
    ros2 topic pub -t 1 /clock rosgraph_msgs/Clock "clock: { sec: 1, nanosec: 200000000 }"
    ```

    **ROS2 Subscribe Clock** ノードの **timeStamp** の値が 1.2 に変わることを確認します。

5. `sec` と `nanosec` の値を変えて同じコマンドを実行し、**timeStamp** に反映されることを確認してください。

## グラフショートカット

ここまで手動でグラフを組みましたが、Clock グラフは数クリックで自動生成できます：

1. **Tools > Robotics > ROS 2 OmniGraphs > Clock** を開きます。

    ROS 2 のグラフがメニューに表示されない場合は、ROS 2 ブリッジが有効になっていません（[セットアップページ](00_setup.md)参照）。

2. パラメータを尋ねるポップアップが表示されるので、グラフのパスを指定して **OK** をクリックします。
3. シミュレーション時刻をパブリッシュするグラフがステージに生成されたことを確認します。

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. **`/clock` トピックと `use_sim_time` パラメータ**による時刻同期の仕組み
2. **Clock パブリッシャ**（シミュレーション時刻／システム時刻）の作成と RViz2 での確認
3. **Clock サブスクライバ**による外部時刻の受信
4. メニューショートカットによる**グラフ自動生成**

## 次のステップ

- [チュートリアル 4: ROS 2 Real Time Factor（RTF）のパブリッシュ](04_rtf.md) - シミュレーションの実時間比を配信する方法を学びます。
