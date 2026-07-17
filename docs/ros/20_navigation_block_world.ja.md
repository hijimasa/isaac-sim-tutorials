---
title: Block World Generator を使った ROS 2 Navigation
---

# Block World Generator を使った ROS 2 Navigation

!!! warning "Isaac Sim 6.0 での位置づけ"
    このチュートリアルは Isaac Sim 6.0 の公式ドキュメントからは削除されました。
    本ページは 5.1.0 時点の内容をもとにした本サイト独自の解説です。
    なお、Isaac Sim 6.0 の公式ドキュメントには、代替として 2.5D の高さマップ（heightmap）から
    ナビゲーション環境を構築する新しいチュートリアル
    [ROS 2 Navigation with Heightmap](https://docs.isaacsim.omniverse.nvidia.com/latest/ros2_tutorials/tutorial_ros2_navigation_heightmap.html)
    が追加されています。

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- **2D の占有マップから 3D ワールドを生成**する方法（Block World Generator）
- 生成した 3D ワールドで [Nav2](https://nav2.org/) によるナビゲーションを実行する方法

## はじめに

### 前提条件

- [チュートリアル 18: ROS 2 Navigation](18_navigation.md)を完了していること。つまり：
    - ROS 2 と Nav2 がインストール済みで、ROS 2 ブリッジが有効
    - `carter_navigation` と `isaac_ros_navigation_goal` を含む ros2_ws が source 済み
    - 占有マップ（`carter_warehouse_navigation.png`）が生成済み

### 所要時間

約 15〜20 分

### 概要

[チュートリアル 18](18_navigation.md) では「3D シーンから 2D 占有マップを作る」方向の変換をしましたが、このチュートリアルはその**逆方向**です。**Block World Generator** を使うと、手元にある 2D 占有マップ（実機で SLAM して作った地図でも構いません）から、壁がブロックとして立ち上がった 3D ワールドを生成できます。実環境の地図からすばやくシミュレーション環境を用意して、ナビゲーションのテストをしたい場合に便利です。

## ステップ 1：3D ワールドを生成する

1. メニューバーから **Tools > Robotics > Block World Generator** を開きます。
2. **Load Image** ボタンを押し、`carter_navigation/maps/carter_warehouse_navigation.png` にある占有マップの画像を開きます。**Visualization** というタイトルのウィンドウが表示されます。
3. **Generate** ボタンを押すと、入力した占有マップに対応するジオメトリが Stage に生成されます。

生成された 3D ワールドでは、占有されているピクセルすべてに**コリジョンメッシュが自動的に適用**されています。そのままロボットの走行や Lidar のスキャン対象になります。

## ステップ 2：ロボットをシーンに追加する

ROS 2 OmniGraph ノードがすべてセットアップ済みの Carter ロボットをこのシーンに追加します。

1. Content ブラウザから **Isaac Sim > Samples > ROS2 > Robots** を開きます。
2. `Nova_Carter_ROS.usd` アセットを、生成したシーンの中（壁に囲まれた空間内の床の上ならどこでも）にドラッグ＆ドロップします。

## ステップ 3：Clock をシーンに追加する

外部の ROS 2 ノードがすべてシミュレーション時刻を参照できるように、シミュレーション時刻を `/clock` トピックに配信する `Ros2PublishClock` ノードを含む **ROS_Clock** グラフを追加します。

[チュートリアル 3: ROS 2 Clock](03_clock.md) のグラフショートカットの手順（**Tools > Robotics > ROS 2 OmniGraphs > Clock**）で追加してください。

## ステップ 4：ナビゲーションを実行する

3D シーンとロボットの準備ができたので、Nav2 スタックを動かします。

1. Isaac Sim で **Play** をクリックしてシミュレーションを開始します。
2. 新しいターミナルを開き、`carter_navigation` パッケージを含む `<ros2_ws>` を source して、Nav2 の launch ファイルを実行します：

    ```bash
    ros2 launch carter_navigation carter_navigation.launch.py
    ```

    RViz2 が開いて占有マップの読み込みが始まります。マップが表示されない場合は、この手順をやり直してください。

3. **2D Pose Estimate** ボタンでロボットの位置を設定し直します。**ゴールを設定する前に**、位置推定がおおよそ正しいことを確認してください。

    !!! note "今回は 2D Pose Estimate が必須"
        [チュートリアル 18](18_navigation.md) ではロボットの初期位置がパラメータファイルに定義済みでしたが、今回はロボットを**手動で好きな場所に配置**したため、初期の自己位置推定が実際の位置と合っていません。必ず 2D Pose Estimate で合わせてから進めてください。

4. **Navigation2 Goal** ボタンをクリックし、マップ上の目的地でクリック＆ドラッグします。Nav2 が軌道を生成し、ロボットが目的地へ動き始めます。

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. **Block World Generator** による 2D 占有マップからの 3D ワールド生成（コリジョン付き）
2. 生成したワールドへのロボットの配置と **Nav2** の実行

## 次のステップ

- [チュートリアル 21: MoveIt 2](21_moveit.md) - マニピュレータを MoveIt 2 に接続する方法を学びます。
