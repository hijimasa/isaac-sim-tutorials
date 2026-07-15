---
title: カメラデータのパブリッシュ
---

# カメラデータのパブリッシュ（Python スクリプティング）

## 学習目標

このチュートリアルでは、Isaac Sim のカメラのパブリッシャを **Python スクリプトからプログラム的に**セットアップし、おおよその指定周波数で配信する方法を学びます。

## はじめに

### 前提条件

- [チュートリアル 5: ROS 2 カメラ](05_camera.md)を完了していること
- [ROS 2 セットアップ](00_setup.md)が完了しており、Isaac Sim 起動前に必要な環境変数が設定されていること
- 公式リファレンスの Sensor Axes Representation（LiDAR / カメラの軸の慣例）に目を通しておくこと
- `isaacsim.sensors.camera` の Camera オブジェクトをプログラム的に作成する方法（公式センサードキュメント）を読んでおくこと
- ROS 2 ブリッジが有効であること

!!! warning "Windows での RViz2"
    Windows 10 / 11 では、マシンの構成によって RViz2 が正しく開かないことがあります（WSL2 の WSLg 経由での起動を推奨します）。

### 所要時間

約 30 分

### 概要

[チュートリアル 5](05_camera.md) では GUI（Action Graph）でカメラパブリッシャを組みましたが、カメラの数が多い場合や、構成をコードで管理したい場合は、**スタンドアロン Python スクリプト**でパブリッシャを構築するほうが便利です。このチュートリアルでは、Replicator のライター API を使って、CameraInfo・RGB・深度・ポイントクラウドの各パブリッシャと、カメラ姿勢の TF ツリーをスクリプトから設定します。

!!! note "「おおよその周波数」となる理由"
    各パブリッシャの配信レートは、ROS パブリッシャの上流にある **IsaacSimulationGate** ノードの `step` 入力で制御します。コード中の `step_size = int(60/freq)` は「レンダリングが約 60 FPS で動いている」ことを前提に、「何フレームに 1 回配信するか」を計算しています。実際のフレームレートは負荷によって変動するため、得られる配信周波数は**近似値**になります。

## ステップ 1：シーンとカメラをセットアップする

まず、倉庫環境とカメラを読み込むスクリプトの骨格を用意します。以降のステップで作る関数をこのスクリプトに貼り付けていきます：

```python
import carb
from isaacsim import SimulationApp
import sys

BACKGROUND_STAGE_PATH = "/background"
BACKGROUND_USD_PATH = "/Isaac/Environments/Simple_Warehouse/warehouse_with_forklifts.usd"

CONFIG = {"renderer": "RayTracedLighting", "headless": False}

# ステージの手動読み込みと画像の手動パブリッシュを行う ROS 2 ブリッジのサンプル
simulation_app = SimulationApp(CONFIG)
import omni
import numpy as np
from isaacsim.core.api import SimulationContext
from isaacsim.core.utils import stage, extensions, nucleus
import omni.graph.core as og
import omni.replicator.core as rep
import omni.syntheticdata._syntheticdata as sd

from isaacsim.core.utils.prims import set_targets
from isaacsim.sensors.camera import Camera
import isaacsim.core.utils.numpy.rotations as rot_utils
from isaacsim.core.utils.prims import is_prim_path_valid
from isaacsim.core.nodes.scripts.utils import set_target_prims

# ROS 2 ブリッジエクステンションを有効化
extensions.enable_extension("isaacsim.ros2.bridge")

simulation_app.update()

simulation_context = SimulationContext(stage_units_in_meters=1.0)

# 環境・ロボットのステージを読み込むため、Isaac Sim のアセットフォルダを取得
assets_root_path = nucleus.get_assets_root_path()
if assets_root_path is None:
    carb.log_error("Could not find Isaac Sim assets folder")
    simulation_app.close()
    sys.exit()

# 環境の読み込み
stage.add_reference_to_stage(assets_root_path + BACKGROUND_USD_PATH, BACKGROUND_STAGE_PATH)


###### パブリッシャをセットアップするヘルパー関数 ########

# 以降のステップの関数をここに貼り付ける
# def publish_camera_tf(camera: Camera): ...
# def publish_camera_info(camera: Camera, freq): ...
# def publish_pointcloud_from_depth(camera: Camera, freq): ...
# def publish_depth(camera: Camera, freq): ...
# def publish_rgb(camera: Camera, freq): ...

###################################################################

# Camera プリムを作成する。Camera クラスの位置・姿勢はワールド軸の慣例で指定する。
camera = Camera(
    prim_path="/World/floating_camera",
    position=np.array([-3.11, -1.87, 1.0]),
    frequency=20,
    resolution=(256, 256),
    orientation=rot_utils.euler_angles_to_quats(np.array([0, 0, 0]), degrees=True),
)
camera.initialize()

simulation_app.update()
camera.initialize()

############### カメラパブリッシュ関数の呼び出し ###############

# ヘルパー関数を貼り付けた上で、以下のコメントアウトを外して実行する

approx_freq = 30
#publish_camera_tf(camera)
#publish_camera_info(camera, approx_freq)
#publish_rgb(camera, approx_freq)
#publish_depth(camera, approx_freq)
#publish_pointcloud_from_depth(camera, approx_freq)

####################################################################

# 物理の初期化
simulation_context.initialize_physics()
simulation_context.play()

while simulation_app.is_running():
    simulation_context.step(render=True)

simulation_context.stop()
simulation_app.close()
```

## ステップ 2：CameraInfo（内部パラメータ）のパブリッシュ

カメラの内部パラメータを [sensor_msgs/CameraInfo](http://docs.ros2.org/latest/api/sensor_msgs/msg/CameraInfo.html) トピックに配信します：

```python
def publish_camera_info(camera: Camera, freq):
    from isaacsim.ros2.bridge import read_camera_info
    # カメラのレンダープロダクトをリンクし、指定トピックにデータを配信する
    render_product = camera._render_product_path
    step_size = int(60/freq)
    topic_name = camera.name+"_camera_info"
    queue_size = 1
    node_namespace = ""
    frame_id = camera.prim_path.split("/")[-1]  # TF ツリーが配信するフレーム名と一致させる

    writer = rep.writers.get("ROS2PublishCameraInfo")
    camera_info, _ = read_camera_info(render_product_path=render_product)
    writer.initialize(
        frameId=frame_id,
        nodeNamespace=node_namespace,
        queueSize=queue_size,
        topicName=topic_name,
        width=camera_info.width,
        height=camera_info.height,
        projectionType=camera_info.distortion_model,
        k=camera_info.k.reshape([1, 9]),
        r=camera_info.r.reshape([1, 9]),
        p=camera_info.p.reshape([1, 12]),
        physicalDistortionModel=camera_info.distortion_model,
        physicalDistortionCoefficients=camera_info.d,
    )
    writer.attach([render_product])

    gate_path = omni.syntheticdata.SyntheticData._get_node_path(
        "PostProcessDispatch" + "IsaacSimulationGate", render_product
    )

    # ROS パブリッシャ上流の IsaacSimulationGate の step で実行レートを制御する
    og.Controller.attribute(gate_path + ".inputs:step").set(step_size)
    return
```

## ステップ 3：深度画像からのポイントクラウドのパブリッシュ

深度画像とカメラの内部パラメータから再構成したポイントクラウドを [sensor_msgs/PointCloud2](https://docs.ros2.org/latest/api/sensor_msgs/msg/PointCloud2.html) として配信します：

```python
def publish_pointcloud_from_depth(camera: Camera, freq):
    # カメラのレンダープロダクトをリンクし、指定トピックにデータを配信する
    render_product = camera._render_product_path
    step_size = int(60/freq)
    topic_name = camera.name+"_pointcloud"  # トピック名はカメラ名から生成
    queue_size = 1
    node_namespace = ""
    frame_id = camera.prim_path.split("/")[-1]  # TF ツリーが配信するフレーム名と一致させる

    # このポイントクラウドパブリッシャは、カメラの内部パラメータを使って深度画像を
    # ポイントクラウドに変換する。この生成方法はセマンティックラベル付き
    # オブジェクトには対応していない。
    rv = omni.syntheticdata.SyntheticData.convert_sensor_type_to_rendervar(
        sd.SensorType.DistanceToImagePlane.name
    )

    writer = rep.writers.get(rv + "ROS2PublishPointCloud")
    writer.initialize(
        frameId=frame_id,
        nodeNamespace=node_namespace,
        queueSize=queue_size,
        topicName=topic_name
    )
    writer.attach([render_product])

    # ROS パブリッシャ上流の IsaacSimulationGate の step で実行レートを制御する
    gate_path = omni.syntheticdata.SyntheticData._get_node_path(
        rv + "IsaacSimulationGate", render_product
    )
    og.Controller.attribute(gate_path + ".inputs:step").set(step_size)

    return
```

## ステップ 4：RGB 画像のパブリッシュ

```python
def publish_rgb(camera: Camera, freq):
    # カメラのレンダープロダクトをリンクし、指定トピックにデータを配信する
    render_product = camera._render_product_path
    step_size = int(60/freq)
    topic_name = camera.name+"_rgb"
    queue_size = 1
    node_namespace = ""
    frame_id = camera.prim_path.split("/")[-1]  # TF ツリーが配信するフレーム名と一致させる

    rv = omni.syntheticdata.SyntheticData.convert_sensor_type_to_rendervar(sd.SensorType.Rgb.name)
    writer = rep.writers.get(rv + "ROS2PublishImage")
    writer.initialize(
        frameId=frame_id,
        nodeNamespace=node_namespace,
        queueSize=queue_size,
        topicName=topic_name
    )
    writer.attach([render_product])

    # ROS パブリッシャ上流の IsaacSimulationGate の step で実行レートを制御する
    gate_path = omni.syntheticdata.SyntheticData._get_node_path(
        rv + "IsaacSimulationGate", render_product
    )
    og.Controller.attribute(gate_path + ".inputs:step").set(step_size)

    return
```

## ステップ 5：深度画像のパブリッシュ

```python
def publish_depth(camera: Camera, freq):
    # カメラのレンダープロダクトをリンクし、指定トピックにデータを配信する
    render_product = camera._render_product_path
    step_size = int(60/freq)
    topic_name = camera.name+"_depth"
    queue_size = 1
    node_namespace = ""
    frame_id = camera.prim_path.split("/")[-1]  # TF ツリーが配信するフレーム名と一致させる

    rv = omni.syntheticdata.SyntheticData.convert_sensor_type_to_rendervar(
                            sd.SensorType.DistanceToImagePlane.name
                        )
    writer = rep.writers.get(rv + "ROS2PublishImage")
    writer.initialize(
        frameId=frame_id,
        nodeNamespace=node_namespace,
        queueSize=queue_size,
        topicName=topic_name
    )
    writer.attach([render_product])

    # ROS パブリッシャ上流の IsaacSimulationGate の step で実行レートを制御する
    gate_path = omni.syntheticdata.SyntheticData._get_node_path(
        rv + "IsaacSimulationGate", render_product
    )
    og.Controller.attribute(gate_path + ".inputs:step").set(step_size)

    return
```

## ステップ 6：カメラ姿勢の TF ツリーのパブリッシュ

上の関数で配信されるポイントクラウドは、**ROS のカメラ軸の慣例（-Y が上、+Z が前方）**で配信されます。RViz で可視化しやすいように、次の 2 つのフレームを含む TF ツリーを `/tf` に配信します：

| フレーム | 軸の慣例 | 役割 |
|---|---|---|
| `{camera_frame_id}` | ROS カメラ慣例（-Y 上、+Z 前方） | ポイントクラウドが配信されるフレーム |
| `{camera_frame_id}_world` | ワールド慣例（+Z 上、+X 前方） | カメラの実際の姿勢を表すフレーム |

![カメラフレーム（ROS 慣例）](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/camera_frames_v2.005.png)

![カメラフレーム（ワールド慣例）](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/camera_frames_v2.004.png)

TF ツリーの構造は次のとおりです：

![TF ツリー構造](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/transformation.png)

- `world -> {camera_frame_id}` は、原点からカメラ（ROS カメラ慣例）への**動的**な変換で、カメラの動きに追従します。
- `{camera_frame_id} -> {camera_frame_id}_world` は、回転のみ・並進ゼロの**静的**な変換です。この回転はクォータニオン `[0.5, -0.5, 0.5, 0.5]`（[w, x, y, z] 順）で表されます。

ポイントクラウドは `{camera_frame_id}` で配信されるため、ポイントクラウドトピックの `frame_id` にも `{camera_frame_id}` を設定することが推奨されます。こうすると RViz でワールドフレームから見た正しい位置にポイントクラウドが表示されます。

```python
def publish_camera_tf(camera: Camera):
    camera_prim = camera.prim_path

    if not is_prim_path_valid(camera_prim):
        raise ValueError(f"Camera path '{camera_prim}' is invalid.")

    try:
        # camera_frame_id を生成する。OmniActionGraph はカメラプリムのフルパスの
        # 最後の要素をフレーム名として使うため、ここで抽出してポイントクラウドの
        # frame_id にも使う。
        camera_frame_id=camera_prim.split("/")[-1]

        # カメラ TF 配信用の Action Graph を生成する
        ros_camera_graph_path = "/CameraTFActionGraph"

        # カメラグラフが見つからない場合は新規作成する
        if not is_prim_path_valid(ros_camera_graph_path):
            (ros_camera_graph, _, _, _) = og.Controller.edit(
                {
                    "graph_path": ros_camera_graph_path,
                    "evaluator_name": "execution",
                    "pipeline_stage": og.GraphPipelineStage.GRAPH_PIPELINE_STAGE_SIMULATION,
                },
                {
                    og.Controller.Keys.CREATE_NODES: [
                        ("OnTick", "omni.graph.action.OnTick"),
                        ("IsaacClock", "isaacsim.core.nodes.IsaacReadSimulationTime"),
                        ("RosPublisher", "isaacsim.ros2.bridge.ROS2PublishClock"),
                    ],
                    og.Controller.Keys.CONNECT: [
                        ("OnTick.outputs:tick", "RosPublisher.inputs:execIn"),
                        ("IsaacClock.outputs:simulationTime", "RosPublisher.inputs:timeStamp"),
                    ]
                }
            )

        # カメラごとに 2 つのノードを生成する：
        # world から ROS カメラ慣例への TF と、ワールド慣例フレーム
        og.Controller.edit(
            ros_camera_graph_path,
            {
                og.Controller.Keys.CREATE_NODES: [
                    ("PublishTF_"+camera_frame_id, "isaacsim.ros2.bridge.ROS2PublishTransformTree"),
                    ("PublishRawTF_"+camera_frame_id+"_world", "isaacsim.ros2.bridge.ROS2PublishRawTransformTree"),
                ],
                og.Controller.Keys.SET_VALUES: [
                    ("PublishTF_"+camera_frame_id+".inputs:topicName", "/tf"),
                    # 注意：topicName を "/tf" 以外に変更すると、
                    # ROS の TF ブロードキャスタに認識されない
                    ("PublishRawTF_"+camera_frame_id+"_world.inputs:topicName", "/tf"),
                    ("PublishRawTF_"+camera_frame_id+"_world.inputs:parentFrameId", camera_frame_id),
                    ("PublishRawTF_"+camera_frame_id+"_world.inputs:childFrameId", camera_frame_id+"_world"),
                    # ROS カメラ慣例からワールド慣例（+Z 上、+X 前方）への静的変換：
                    ("PublishRawTF_"+camera_frame_id+"_world.inputs:rotation", [0.5, -0.5, 0.5, 0.5]),
                ],
                og.Controller.Keys.CONNECT: [
                    (ros_camera_graph_path+"/OnTick.outputs:tick",
                        "PublishTF_"+camera_frame_id+".inputs:execIn"),
                    (ros_camera_graph_path+"/OnTick.outputs:tick",
                        "PublishRawTF_"+camera_frame_id+"_world.inputs:execIn"),
                    (ros_camera_graph_path+"/IsaacClock.outputs:simulationTime",
                        "PublishTF_"+camera_frame_id+".inputs:timeStamp"),
                    (ros_camera_graph_path+"/IsaacClock.outputs:simulationTime",
                        "PublishRawTF_"+camera_frame_id+"_world.inputs:timeStamp"),
                ],
            },
        )
    except Exception as e:
        print(e)

    # USD の姿勢を反映するターゲットプリムを追加する（他のフレームはすべて静的）
    set_target_prims(
        primPath=ros_camera_graph_path+"/PublishTF_"+camera_frame_id,
        inputName="inputs:targetPrims",
        targetPrimPaths=[camera_prim],
    )
    return
```

## 実行と確認

1. ヘルパー関数をスクリプトに貼り付け、呼び出し部分のコメントアウトを外して保存します。
2. `isaacsim.ros2.bridge` が有効な状態で、Isaac Sim フォルダの `python.sh` でスクリプトを実行します。この例では `{camera_frame_id}` はカメラのプリム名 `floating_camera` になります。
3. シーンに `/World/floating_camera` のカメラがあり、フォークリフトが映っていることを確認します：

    ![シミュレーションビュー](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isaac_tutorial_ros_camera_publishing_simview.png)

4. ターミナルでトピック一覧を確認します：

    ```bash
    ros2 topic list
    ```

    ```text
    /camera_camera_info
    /camera_depth
    /camera_pointcloud
    /camera_rgb
    /clock
    /parameter_events
    /rosout
    /tf
    ```

5. RViz2 を開き、**Fixed Frame** を `world` に設定してから、`/camera_depth`、`/camera_rgb`、`/camera_pointcloud`、`/tf` の表示を有効にします。

    ![RViz 設定](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/rviz.png)

6. 深度画像と RGB 画像、ポイントクラウド、TF の 2 つのフレーム（`{camera_frame_id}_world` と `{camera_frame_id}`）が正しく表示されることを確認します：

    ![RGB と深度](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isaac_tutorial_ros_camera_publishing_rgbd.png)

    ![ポイントクラウド（正面）](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isaac_tutorial_ros_camera_publishing_pc_frontview.png)

    ![ポイントクラウド（側面）](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isaac_tutorial_ros_camera_publishing_pc_sideview.png)

## まとめ

このチュートリアルでは、Isaac Sim のカメラの ROS 2 パブリッシャ（CameraInfo・RGB・深度・ポイントクラウド・TF）を、Python スクリプトからおおよその指定周波数でセットアップする方法を扱いました。

## 次のステップ

- [チュートリアル 8: RTX Lidar センサー](08_rtx_lidar.md) - Turtlebot3 に RTX Lidar センサーを追加する方法を学びます。
