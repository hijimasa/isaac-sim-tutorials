---
title: 複数ロボットの ROS 2 Navigation
---

# 複数ロボットの ROS 2 Navigation

## 学習目標

このチュートリアルでは、Isaac Sim と ROS 2 Nav2 スタックを統合し、**複数ロボットの同時ナビゲーション**を行います。

## はじめに

!!! warning "サポートの制限"
    複数ロボットの ROS 2 Navigation は **Linux と、Pixi ベースでインストールした Windows で完全サポート**されています。Windows（WSL）ではエラーが発生する可能性があります。

### 前提条件

- [チュートリアル 18: ROS 2 Navigation](18_navigation.md)を完了していること。つまり：
    - ROS 2 と Nav2 がインストール済み
    - ROS 2 ブリッジが有効
    - `carter_navigation` と `isaac_ros_navigation_goal` を含む ros2_ws がビルド・source 済み

### 所要時間

約 30〜40 分

### 概要

複数のロボットを同じ環境で動かすには、[チュートリアル 15](15_auto_namespace.md) で学んだ**ネームスペース**を活用します。ネームスペースによって各 ROS 2 パッケージの rostopic・rosnode 名が分離され、同じ ROS 2 ノードの複数インスタンス（各ロボット用の Nav2 スタック一式）を同時に実行できるようになります。

このサンプルでは、各 `Nova_Carter_ROS_X` プリム配下の Action Graph 内の `node_namespace` が対応するロボット名に設定されており、`carter_navigation` パッケージの `multiple_robot_carter_navigation_hospital.launch.py` / `multiple_robot_carter_navigation_office.launch.py` launch ファイルにも同じネームスペースが設定されています。

## ステップ 1：占有マップを生成する（Hospital / Office）

Occupancy Map Generator を使って、Hospital と Office それぞれの環境のマップを生成します。手順は[チュートリアル 18 のステップ 1](18_navigation.md) と同じ流れです。

**Hospital 環境の場合：**

1. Content ブラウザの **Isaac Sim > Environments > Hospital** から `hospital.usd` をシーンにドラッグし、Translate をすべて 0 にして原点に配置します。
2. ビューポート左上の **Perspective** から **Top** を選択し、`/Hospital` プリムを選択して **F** キーで全体表示にします。
3. **Tools > Robotics > Occupancy Map** を開き、**Origin** X: 0.0, Y: 0.0, Z: 0.0、**Lower Bound** Z: 0.1、**Upper Bound** Z: 0.62 に設定します（0.62 m は Carter の Lidar の高さです）。
4. Stage で `Hospital` プリムを選択して **BOUND SELECTION** をクリックします。

    ![Hospital のマップパラメータ](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isaac_sample_ros_multiple_robot_nav_1.png)

    ![Hospital の範囲（Top ビュー）](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_5.0_ros_tut_viewport_ros_multiple_robot_nav_occupancy_map.png)

**Office 環境の場合**も同様に、`office.usd` を原点に配置し、次のパラメータでマップを設定します：

![Office のマップパラメータ](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isaac_sample_ros_multiple_robot_nav_3.png)

**共通の書き出し手順：**

1. **CALCULATE** → **VISUALIZE IMAGE** をクリックします。
2. **Rotate Image** で **180 度**、**Coordinate Type** で **ROS Occupancy Map Parameters File (YAML)** を選択し、**RE-GENERATE IMAGE** をクリックします。画像名を好みに変更します。
3. **Save YAML** をクリックし、`carter_navigation/maps/` ディレクトリに YAML ファイルを保存します（Hospital 用は `carter_hospital_navigation.yaml`、Office 用は `carter_office_navigation.yaml`）。
4. **Save Image** で、YAML と同じ名前・同じディレクトリに画像を保存します。

生成されるマップは次のようになります：

![Hospital のマップ](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isaac_sample_ros_nav_hospital_map.png)

![Office のマップ](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isaac_sample_ros_nav_office_map.png)

## ステップ 2：複数ロボットナビゲーションを実行する

!!! warning "Windows のマルチ GPU 環境での既知の問題"
    Windows のマルチ GPU システムでは、このシーンの読み込み・再生時にアプリケーションが致命的にクラッシュすることがあります。これは既知の問題で、将来のリリースで修正される予定です。

1. シナリオを読み込みます：
    - Hospital：**Window > Examples > Robotics Examples > ROS2 > Navigation > Multiple Robots > Hospital Scene**
    - Office：同 **> Office Scene**
2. **Play** をクリックしてシミュレーションを開始します。
3. 新しいターミナルで、環境に対応する launch ファイルを実行します：

    ```bash
    # Hospital 環境
    ros2 launch carter_navigation multiple_robot_carter_navigation_hospital.launch.py

    # Office 環境
    ros2 launch carter_navigation multiple_robot_carter_navigation_office.launch.py
    ```

    **3 つの RViz2 ウィンドウ**（ロボット 1 台につき 1 つ）が起動します。起動には少し時間がかかります。

4. 各 RViz2 ウィンドウの Displays パネルで **Map** をクリックしてトピック名を確認し、そのウィンドウがどのロボットのネームスペース（`/carter1` など）に対応しているかを把握します。
5. 各ロボットの初期位置は `carter_navigation/params/hospital/` または `params/office/` のパラメータファイルに定義済みなので、既に自己位置推定されているはずです。
6. `/carter1` の RViz2 ウィンドウで **Navigation2 Goal** ボタンをクリックし、マップ上の目的地でクリック＆ドラッグします。Nav2 が軌道を生成し、carter1 が動き始めます。
7. `/carter2`、`/carter3` のウィンドウでも同じ操作を繰り返します。

!!! note "画像配信は既定で無効"
    パフォーマンスのため、ROS 2 の画像配信パイプラインは既定で無効です。配信するには、各 `Nova_Carter_ROS` プリム配下の `_hawk` Action Graph で `_camera_render_product` ノードを有効化してください。画像は **Sensor Data QoS** で配信されるため、RViz で見る場合は **Topic > Reliability Policy** を **Best Effort** に変更します。

### トラブルシューティング

このチュートリアルは CPU 使用率が高くなります。ロボット同士の衝突や自己位置推定の問題が起きる場合、Nav2 スタックがセンサーデータと同期できず、コントローラの指令を取りこぼしている可能性が高いです。改善策：

1. 各 `Nova_Carter_ROS_X` ロボット配下の `ros_lidars` Action Graph にある `publish_front_3d_lidar_scan` ノードの **Publish Full Scan** チェックボックスを有効にしてみてください。
2. それでも問題が残る場合は、Isaac Sim をターミナルから次のコマンドで起動してみてください（実験的機能。全機能はサポートされませんが、全体的な性能が向上する場合があります）：

    ```bash
    ./isaac-sim.fabric.sh --reset-user
    ```

!!! tip "Python から直接実行する"
    このサンプル環境を Python から直接読み込む方法は、[チュートリアル 17: スタンドアロンワークフロー](17_standalone_python.md)の「複数ロボットの ROS 2 ナビゲーション」を参照してください。ROS コンポーネントの配信タイミングとタイムステップを手動制御できます。

## ステップ 3：複数ロボットへゴールをプログラム送信する

`isaac_ros_navigation_goal` パッケージで、複数ロボットへ同時にゴール姿勢を送信できます。パッケージの設定とパラメータは[チュートリアル 18 のステップ 6](18_navigation.md) を参照してください。

複数ロボットへ同時にゴールを送るには、ノードの**ネームスペース設定**が必要です。Python の launch ファイルでは、各 Node オブジェクトの `namespace` 引数で設定します。

1. `isaac_ros_navigation_goal/launch/isaac_ros_navigation_goal.launch.py` で、`namespace` 引数を使って「carter1」のノードを定義します：

    ```python
    navigation_goal_node = Node(
        name="set_navigation_goal",
        package="isaac_ros_navigation_goal",
        executable="SetNavigationGoal",
        namespace="carter1",
        parameters=[
            {
                "map_yaml_path": map_yaml_file,
                "iteration_count": 3,
                "goal_generator_type": "RandomGoalGenerator",
                "action_server_name": "navigate_to_pose",
                "obstacle_search_distance_in_meters": 0.2,
                "goal_text_file_path": goal_text_file,
                "initial_pose": [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
            }
        ],
        output="screen",
    )
    ```

    マップ YAML のパスと carter1 の初期姿勢は、Hospital / Office のシナリオに合わせて更新してください。

    !!! note
        `goal_generator_type` が `RandomGoalGenerator` の場合、ゴールテキストファイルは使われません。逆に `GoalReader` を使う場合は、**ネームスペースごとに別のゴールテキストファイル**を作る必要があります。

2. carter1 のノード宣言をコピーして 2 回貼り付け、`carter2`・`carter3` 用に修正します（ノードの変数名は一意にします）。マップ YAML のパスは 3 ノードで同一で構いませんが、**carter2・carter3 の初期姿勢は必ず更新**してください。
3. launch ファイルの末尾で、作成した 3 つのノードを LaunchDescription に追加します：

    ```python
    return LaunchDescription([
        navigation_goal_node,
        navigation_goal_node_2,
        navigation_goal_node_3
    ])
    ```

4. 修正した launch ファイルを実行します（**先にステップ 2 の 1〜4 を実行しておくこと**）：

    ```bash
    ros2 launch isaac_ros_navigation_goal isaac_ros_navigation_goal.launch.py
    ```

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. Hospital / Office 環境の**占有マップ生成**
2. **ネームスペース**を使った複数ロボットの同時 Nav2 実行と、RViz2 ウィンドウごとのゴール指定
3. 高 CPU 負荷時の**トラブルシューティング**
4. launch ファイルの `namespace` 引数による**複数ロボットへのゴールのプログラム送信**

## 次のステップ

- [チュートリアル 20: Block World Generator を使った ROS 2 Navigation](20_navigation_block_world.md) - 2D 占有マップから 3D ワールドを生成してナビゲーションします。
