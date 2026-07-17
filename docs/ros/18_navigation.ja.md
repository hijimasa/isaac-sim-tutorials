---
title: ROS 2 Navigation（Nav2）
---

# ROS 2 Navigation（Nav2）

## 学習目標

このチュートリアルでは、Isaac Sim と **ROS 2 Nav2** を統合したナビゲーションを扱います。以下の内容を習得できます：

- **占有マップ（Occupancy Map）**の生成
- Nova Carter / iw.hub を使った **Nav2 の実行**
- `isaac_ros_navigation_goal` パッケージによる**ゴールのプログラム送信**
- **Waypoint Follower ActionGraph** によるゴール送信（ウェイポイント／パトロール）

## はじめに

!!! warning "サポートの制限"
    Isaac Sim との ROS 2 Navigation は **Linux と、Pixi ベースでインストールした Windows で完全サポート**されています。Windows（WSL）では部分的なサポートであり、エラーが発生する可能性があります。`isaac_ros_navigation_goal` パッケージは Linux のみ完全サポートです。

!!! warning "Windows のマルチ GPU 環境での既知の問題"
    Windows のマルチ GPU システムでは、このシーンの読み込み・再生時にアプリケーションが致命的にクラッシュすることがあります。これは既知の問題で、将来のリリースで修正される予定です。

### 前提条件

- Isaac Sim を起動する前に、ターミナルで ROS 2 インストールを source しておくこと
- **Nav2** がインストールされていること（[Nav2 インストールページ](https://docs.nav2.org/getting_started/index.html#installation)参照）
- ROS 2 ブリッジエクステンション（`isaacsim.ros2.bridge`）が有効であること
- `carter_navigation`、`iw_hub_navigation`、`isaac_ros_navigation_goal` の各 ROS 2 パッケージが必要です。これらは [ROS 2 セットアップ](00_setup.md)でビルドした ros2_ws に含まれており、launch ファイル・ナビゲーションパラメータ・ロボットモデルを提供します。ワークスペースが正しくビルド・source されていることを確認してください

### 所要時間

約 40〜60 分

### 概要

!!! note "Nav2 とは"
    [Nav2](https://nav2.org/) は ROS 2 の標準ナビゲーションスタックです。占有マップと自己位置推定（AMCL）に基づいて経路を計画し、速度指令（Twist）を出力してロボットを目的地まで走らせます。Isaac Sim 側はセンサーデータ（Lidar・オドメトリ・TF）を配信し、Nav2 からの速度指令を受け取る、という役割分担になります。

このシナリオで Nav2 に配信されるトピックとメッセージ型は次のとおりです：

| ROS 2 トピック | メッセージ型 |
|---|---|
| `/tf` | tf2_msgs/TFMessage |
| `/odom` | nav_msgs/Odometry |
| `/map` | nav_msgs/OccupancyGrid |
| `/point_cloud` | sensor_msgs/PointCloud |
| `/scan` | sensor_msgs/LaserScan（外部の [pointcloud_to_laserscan](https://index.ros.org/p/pointcloud_to_laserscan/) ノードが配信） |

![Nav2 ブロック図](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isaac_sample_ros2_nav_1.png)

## ステップ 1：占有マップを生成する

Nav2 には環境の**占有マップ**が必要です。Isaac Sim の **Occupancy Map Generator** エクステンションで倉庫環境のマップを生成します。

1. **Window > Examples > Robotics Examples** を開き、**ROS2 > Navigation > Nova Carter** のサンプルを開いて、[Nova Carter ロボット](https://docs.isaacsim.omniverse.nvidia.com/latest/assets/nova_carter_landing_page.html)入りの倉庫シナリオを読み込みます。
2. ビューポート左上の **Camera** をクリックし、ドロップダウンから **Top** を選択します。
3. **Tools > Robotics > Occupancy Map** を開きます。
4. Occupancy Map エクステンションで、**Origin** が X: 0.0, Y: 0.0, Z: 0.0 になっていることを確認し、**Lower Bound** の Z を `0.1`、**Upper Bound** の Z を `0.62` に設定します。

    !!! note "Upper Bound Z = 0.62 の意味"
        この値は、Nova Carter に搭載された Lidar の**地面からの高さ**に合わせたものです。占有マップは「Lidar が見る高さの断面」で作る必要があるため、ロボットのセンサー高に合わせて設定します。

5. Stage で `warehouse_with_forklifts` プリムを選択し、Occupancy Map エクステンションで **BOUND SELECTION** をクリックします。マップの範囲が選択した倉庫プリムを含むように更新されたことを確認します：

    ![占有マップのパラメータ](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isaac_sample_ros_nav_2.png)

    ![占有マップの範囲（Top ビュー）](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_5.0_ros_tut_viewport_ros_nav_occupancy_map.png)

6. Stage から `Nova_Carter_ROS` プリムを**削除**します（ロボット自身がマップに写り込まないようにするためです）。
7. **CALCULATE** → **VISUALIZE IMAGE** の順にクリックすると、Visualization ポップアップが表示されます。
8. **Rotate Image** で **180 度**、**Coordinate Type** で **ROS Occupancy Map Parameters File (YAML)** を選択し、**RE-GENERATE IMAGE** をクリックします（ROS のカメラと Isaac Sim のカメラは座標系が異なるためです）。
9. **Save YAML** をクリックし、YAML ファイルを `carter_navigation` パッケージの maps ディレクトリ（`~/<ros2_ws>/src/navigation/carter_navigation/maps/carter_warehouse_navigation.yaml`）に保存します。
10. Isaac Sim の Visualization タブに戻り、**Save Image** をクリックします。画像は `carter_warehouse_navigation.png` という名前で、パラメータファイルと同じディレクトリに保存します。

保存した画像が次のようになっていることを確認します：

![倉庫の占有マップ](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isaac_sample_ros_nav_warehouse_map.png)

これで Nav2 で使える占有マップの準備ができました。

## ステップ 2：Nav2 を実行する（Nova Carter）

1. **Window > Examples > Robotics Examples** から **ROS2 > Navigation > Nova Carter** のサンプルを開きます。
2. **Play** をクリックしてシミュレーションを開始します。
3. 新しいターミナルで Nav2 の launch ファイルを実行します：

    ```bash
    ros2 launch carter_navigation carter_navigation.launch.py
    ```

    RViz2 が開いて占有マップの読み込みが始まります。マップが表示されない場合は、この手順をやり直してください。

4. ロボットの初期位置はパラメータファイル `carter_navigation_params.yaml` に定義されているため、既に正しく自己位置推定されているはずです。必要であれば、**2D Pose Estimate** ボタンでロボットの位置を設定し直せます。
5. **Navigation2 Goal** ボタンをクリックし、マップ上の目的地でクリック＆ドラッグします。Nav2 が軌道を生成し、ロボットが目的地へ動き始めます。

!!! note "知っておくと役立つポイント"
    - Carter は既定で RTX Lidar を使います。シーンに人のアセットを追加すると、Lidar が検出して Nav2 に伝わります（動的障害物として回避されます）。
    - パフォーマンスのため、Hawk カメラの一部の画像配信パイプラインは既定で無効です。画像を配信するには、ロボットプリム配下の `_hawk` Action Graph を開き、`_camera_render_product` ノードを有効化してください。下流の ROS カメラパブリッシャは既定で有効なので、レンダープロダクトを有効にすれば配信が始まります。Nova Carter のセンサー・画像はすべて **Sensor Data QoS** で配信されるため、RViz で画像を見る場合は Image タブの **Topic > Reliability Policy** を **Best Effort** に変更してください。
    - 開けた空間で自己位置推定に問題が出る場合は、性能不足に起因する既知の問題の可能性があります。シーンに物体を追加して特徴を増やすと改善します。
    - 次のような警告が出ることがありますが、無害なので無視して構いません：

        ```text
        [Warning] [omni.graph.core.plugin] .../differential_controller_01: invalid dt 0.000000, cannot check for acceleration limits, skipping current step
        ```

## ステップ 3：RViz にロボットモデルを表示する（robot description）

前のステップに加えて、ロボットの記述（メッシュ形状）を RViz 上に可視化できます。

1. `nova_carter_description` パッケージをインストールします（後述の「nova_carter_description パッケージのインストール」参照）。
2. Isaac Sim Workspaces に含まれる launch ファイルで Nova Carter の記述を配信します：

    ```bash
    ros2 launch carter_navigation nova_carter_description_isaac_sim.launch.py
    ```

3. Isaac Sim で **ROS2 > Navigation > Nova Carter** のシーンを開いて **Play** し、別ターミナルで Nav2 を起動します（ステップ 2 と同じ）。
4. RViz のシーンにロボットモデルが自動的に読み込まれることを確認します。

## ステップ 4：robot_state_publisher を使う構成（Nova Carter Joint States）

ここまでのシーンでは、ロボットの TF を **Isaac Sim から直接**配信していました。ロボットやシーンが複雑になるほど、静的な TF は ROS 2 標準の [robot_state_publisher](https://github.com/ros/robot_state_publisher) に任せるほうが**スケーラブルで高性能**です。この構成では：

- **robot_state_publisher** が URDF を解析して静的 TF を配信する
- **Isaac Sim** は可動ジョイントの joint states の配信だけを担当する
- robot_state_publisher が joint states を受け取り、対応する Transform に変換して TF ツリーに加える

この構成用に **Nova_Carter_Joint_States_ROS.usd** というアセットが用意されています。元の `Nova_Carter_ROS.usd` との違いは：

- `transform_tree_odometry` Action Graph が削除され、代わりにオドメトリ用グラフが追加された（TF パブリッシャはグラウンドトゥルース自己位置用の `odom -> base_link` の Raw TF 1 つだけ残る）
- 可動ジョイントの状態を配信する `joint_states` Action Graph が追加された
- 各 Hawk カメラのグラフに、カメラマウントフレームから左右カメラフレームへのサブ TF ツリーを作る静的 TF パブリッシャが追加された

!!! note "カメラごとに静的 TF パブリッシャがある理由"
    カメラのキャリブレーションの過程で、左右カメラの間隔は個体ごとに異なり得ます。そのため（マウント → 左カメラ）と（マウント → 右カメラ）の Transform はメインの URDF には含めず、**デバイスドライバが提供する**設計になっています。この構成では Isaac Sim がハードウェアのデバイスドライバの役割を果たし、これらの静的 Transform を配信します。

手順：

1. `nova_carter_description` パッケージをインストールします（次節参照）。
2. **ROS2 > Navigation > Nova Carter Joint States** のサンプルを開いて **Play** します。
3. 新しいターミナルで robot_state_publisher を起動します：

    ```bash
    ros2 launch carter_navigation nova_carter_description_isaac_sim.launch.py
    ```

4. さらに別のターミナルで Nav2 を起動します：

    ```bash
    ros2 launch carter_navigation carter_navigation.launch.py
    ```

5. RViz にロボットモデルが読み込まれ、joint states を使わない例と同じように動作することを確認します。

### nova_carter_description パッケージのインストール

!!! warning "Linux の ROS 2 Humble のみ対応"
    この節の手順は Linux の ROS 2 Humble でのみサポートされています。

1. 新しい ROS ターミナルでロケールを設定します：

    ```bash
    locale  # UTF-8 か確認

    sudo apt update && sudo apt install locales
    sudo locale-gen en_US en_US.UTF-8
    sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
    export LANG=en_US.UTF-8

    locale  # 設定を確認
    ```

2. 必要な依存パッケージをインストールします：

    ```bash
    sudo apt update && sudo apt install gnupg wget
    sudo apt install software-properties-common
    sudo add-apt-repository universe
    ```

3. NVIDIA の GPG キーとリポジトリを登録します（US CDN の例）：

    ```bash
    wget -qO - https://isaac.download.nvidia.com/isaac-ros/repos.key | sudo apt-key add -
    grep -qxF "deb https://isaac.download.nvidia.com/isaac-ros/release-3 $(lsb_release -cs) release-3.0" /etc/apt/sources.list || \
    echo "deb https://isaac.download.nvidia.com/isaac-ros/release-3 $(lsb_release -cs) release-3.0" | sudo tee -a /etc/apt/sources.list
    sudo apt-get update
    ```

4. パッケージをインストールします：

    ```bash
    sudo apt install ros-humble-nova-carter-description
    ```

## ステップ 5：iw.hub で Nav2 を実行する

別のロボット（iw.hub）でも同じ流れを体験できます。

1. **ROS2 > Navigation > iw_hub** のサンプルを開いて **Play** します。
2. 新しいターミナルで Nav2 を起動します（この倉庫環境のマップは生成済みのものが使われます）：

    ```bash
    ros2 launch iw_hub_navigation iw_hub_navigation.launch.py
    ```

3. 初期位置は `iw_hub_navigation_params.yaml` に定義済みです。**Navigation2 Goal** で目的地を指定し、ロボットが**初期マップに含まれていない動的障害物**（シーン内のパレットなど）を回避することを確認してください。

## ステップ 6：ゴールをプログラムから送信する

`isaac_ros_navigation_goal` ROS 2 パッケージを使うと、Python ノードからゴール姿勢を設定できます。ランダム生成したゴールも、ユーザー定義のゴール列も送信できます。

launch ファイル（`isaac_ros_navigation_goal/launch` 配下）のパラメータを必要に応じて変更します。**変更後はパッケージとワークスペースの再ビルドと source を忘れずに**。

| パラメータ | 説明 |
|---|---|
| `goal_generator_type` | ゴール生成の方式。ランダム生成は `RandomGoalGenerator`、ユーザー定義のゴールを順に送るには `GoalReader` |
| `map_yaml_path` | 占有マップパラメータ YAML のパス。生成した姿勢の周囲の障害物判定に使う。`RandomGoalGenerator` では必須 |
| `iteration_count` | ゴールを設定する回数 |
| `action_server_name` | アクションサーバー名 |
| `obstacle_search_distance_in_meters` | 生成した姿勢がこの距離以内に障害物を含まないことを保証する距離 [m] |
| `goal_text_file_path` | ユーザー定義ゴールのテキストファイルのパス。1 行 1 ゴールで `pose.x pose.y orientation.x orientation.y orientation.z orientation.w` の形式。`GoalReader` では必須 |
| `initial_pose` | 設定すると `/initialpose` トピックに配信され、その後にゴールが送信される。形式は `[pose.x, pose.y, pose.z, orientation.x, orientation.y, orientation.z, orientation.w]` |

実行手順：

1. **ROS2 > Navigation > Nova Carter** のシーンを開いて **Play** します。
2. Nav2 を起動します：

    ```bash
    ros2 launch carter_navigation carter_navigation.launch.py
    ```

3. ゴールの自動送信を開始します：

    ```bash
    ros2 launch isaac_ros_navigation_goal isaac_ros_navigation_goal.launch.py
    ```

!!! note "パッケージが停止する条件"
    次のいずれかを満たすと、パッケージはゴールの設定を停止します：

    - 送信したゴール数が `iteration_count` に達した
    - `GoalReader` 使用時に、設定ファイルのすべてのゴールを送信し終えた
    - アクションサーバーがゴールを拒否した
    - まれに、非常に密なマップで `RandomGoalGenerator` が無効な姿勢を生成し続け、最大イテレーション数を超えた

## ステップ 7：ActionGraph からゴールを送信する（Waypoint Follower）

!!! warning "内部 ROS 2 ライブラリでは動作しません"
    この節は Nav2 がインストールされ、**ターミナルで ROS 2 を source してから** Isaac Sim を起動した場合にのみ動作します。現時点では Isaac Sim の内部ライブラリだけでは動きません。

1. **Robotics Examples > ROS2 > Navigation > Nova Carter** で **Load Sample Scene** をクリックして倉庫シナリオを読み込みます。
2. **Robotics Examples > ROS2 > Navigation > Add Waypoint Follower** を開き、パラメータウィンドウを表示します。

    ![Waypoint Follower パラメータ](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_4.5_ros_tut_gui_waypoint_follower_parameters.png)

| パラメータ | 説明 |
|---|---|
| **Graph Path** | ステージ内のグラフのパス |
| **Frame ID** | ナビゲーションの基準フレーム |
| **Navigation Modes** | **Waypoint Mode**：単一のウェイポイントをゴールとして送信。**Patrolling Mode**：複数（2〜50 個）のウェイポイント間を連続巡回 |
| **Waypoint Count** | Patrolling で生成するウェイポイント数 |

3. **Load Waypoint Follower ActionGraph** をクリックすると、ウェイポイントが作成され、指定パスに Action Graph が追加されます。
4. **Play** でシミュレーションを開始し、別ターミナルで Nav2 を起動します（ステップ 2 と同じ）。
5. モードごとの実行方法：
    - **Waypoint**：シーン内のウェイポイント（`/World/Waypoints/waypoint_1`）を XY 平面で目的地に動かし、Stage から `ROS_Nav2_Waypoint_Follower` グラフを開いて **OnImpulseEvent** ノードの **Send Impulse** をクリックします。ゴール到達後、同じ手順で次のウェイポイントを設定できます。
    - **Patrolling**：複数のウェイポイント（`/World/Waypoints/waypoint_n`）で巡回経路を定義し、同様に **Send Impulse** をクリックすると巡回が始まります。

!!! note "補足"
    - このチュートリアルは AMCL による自己位置推定を使っており、Action Graph はこのローカライザで完全にサポートされています。
    - グラフの削除後に `Error executing python callback omni.graph.scriptnode...` のようなエラーが表示されることがありますが、無害です。グラフを削除する前に script ノードの「reload node」ボタンでクリーンアップすると、このログを防げます。

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. **Occupancy Map Generator** による占有マップの生成（YAML ＋画像）
2. **Nav2** と Nova Carter / iw.hub によるナビゲーション実行
3. **robot_state_publisher** を使ったスケーラブルな TF 構成
4. **isaac_ros_navigation_goal** によるゴールのプログラム送信
5. **Waypoint Follower ActionGraph** によるウェイポイント／パトロールナビゲーション

## 次のステップ

- [チュートリアル 19: 複数ロボットの ROS 2 Navigation](19_multi_navigation.md) - 複数のナビゲーションロボットを ROS 2 で同時に動かします。

### さらに学ぶには

- Nav2 の詳細は[プロジェクトサイト](https://nav2.org/)を参照してください。
