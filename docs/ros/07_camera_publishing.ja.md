---
title: カメラデータのパブリッシュ
---

# カメラデータのパブリッシュ（Python スクリプティング）

## 学習目標

このチュートリアルでは、Isaac Sim のカメラの ROS 2 パブリッシャを **Python スクリプトからプログラム的に**セットアップする方法を学びます。

## はじめに

### 前提条件

- [チュートリアル 5: ROS 2 カメラ](05_camera.md)を完了していること
- [ROS 2 セットアップ](00_setup.md)が完了しており、Isaac Sim 起動前に必要な環境変数が設定されていること
- 公式リファレンスの Sensor Axes Representation（LiDAR / カメラの軸の慣例）に目を通しておくこと
- カメラプリムをプログラム的に作成する方法（公式センサードキュメントの `isaacsim.sensors.experimental.rtx`）を読んでおくこと
- ROS 2 ブリッジが有効であること

!!! warning "Windows での RViz2"
    Windows 11 では、マシンの構成によって RViz2 が正しく開かないことがあります。

### 所要時間

約 30 分

### 概要

[チュートリアル 5](05_camera.md) では GUI（Action Graph）でカメラパブリッシャを組みましたが、カメラの数が多い場合や、構成をコードで管理したい場合は、**スタンドアロン Python スクリプト**でパブリッシャを構築するほうが便利です。このチュートリアルでは、Replicator のライター API を使って、CameraInfo・RGB・深度・ポイントクラウドの各パブリッシャと、カメラ姿勢の TF ツリーをスクリプトから設定します。

!!! note "配信レートは tick_rate で決まります（6.0 での変更点）"
    Isaac Sim 6.0 の**マルチティックレンダリング**では、配信の周期はカメラの **`tick_rate`**（`RtxCamera` 作成時に指定）でスケジュールされます。5.1 までのように、パブリッシャごとに上流の IsaacSimulationGate の `step` を設定してレートを間引く必要は**なくなりました**。センサー種別ごとに配信レートを変える方法は[チュートリアル 10: ROS 2 パブリッシュレートの設定](10_publish_rate.md)を参照してください。

## ステップ 1：シーンとカメラをセットアップする

まず、倉庫環境を読み込むスクリプトの骨格を用意します。カメラの作成には、6.0 の `isaacsim.sensors.experimental.rtx` の **`RtxCamera`**（USD の Camera プリムを作成）と **`CameraSensor`**（レンダープロダクトとアノテータを紐付け）を使います。以降のステップで作る関数をこのスクリプトに貼り付けていきます：

```python
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument("--test", action="store_true", help="Run in test mode.")
args, _ = parser.parse_known_args()

import carb
from isaacsim import SimulationApp

BACKGROUND_STAGE_PATH = "/background"
BACKGROUND_USD_PATH = "/Isaac/Environments/Simple_Warehouse/warehouse_with_forklifts.usd"

CONFIG = {"renderer": "RayTracedLighting", "headless": False}

# ステージの手動読み込みと画像の手動パブリッシュを行う ROS 2 ブリッジのサンプル
simulation_app = SimulationApp(CONFIG)

import isaacsim.core.experimental.utils.app as app_utils
import isaacsim.core.experimental.utils.stage as stage_utils
import isaacsim.core.experimental.utils.transform as transform_utils
import numpy as np
import omni
import omni.graph.core as og
import omni.replicator.core as rep
import omni.syntheticdata._syntheticdata as sd
from isaacsim.core.nodes.scripts.utils import set_target_prims
from isaacsim.sensors.experimental.rtx import CameraSensor, RtxCamera
from isaacsim.storage.native import get_assets_root_path

# ROS 2 ブリッジエクステンションを有効化
app_utils.enable_extension("isaacsim.ros2.bridge")

simulation_app.update()

stage_utils.set_stage_units(meters_per_unit=1.0)

# 環境・ロボットのステージを読み込むため、Isaac Sim のアセットフォルダを取得
assets_root_path = get_assets_root_path()
if assets_root_path is None:
    carb.log_error("Could not find Isaac Sim assets folder")
    simulation_app.close()
    sys.exit()

# 環境の読み込み
stage_utils.add_reference_to_stage(assets_root_path + BACKGROUND_USD_PATH, BACKGROUND_STAGE_PATH)
```

以降の各パブリッシャ関数では、`CameraSensor` からレンダープロダクトパス・カメラプリムパス・frame_id を取り出す共通ヘルパーを使います：

```python
def _get_sensor_info(sensor: CameraSensor) -> tuple[str, str, str]:
    """CameraSensor からレンダープロダクトパス・カメラプリムパス・frame_id を取り出す"""
    rp_path = str(sensor.render_product.GetPath())
    prim_path = sensor.authoring_object.paths[0]
    frame_id = prim_path.split("/")[-1]
    return rp_path, prim_path, frame_id
```

## ステップ 2：CameraInfo（内部パラメータ）のパブリッシュ

カメラの内部パラメータを [sensor_msgs/CameraInfo](http://docs.ros2.org/latest/api/sensor_msgs/msg/CameraInfo.html) トピックに配信します：

```python
def publish_camera_info(sensor: CameraSensor):
    from isaacsim.ros2.core import read_camera_info

    rp_path, _, frame_id = _get_sensor_info(sensor)
    topic_name = frame_id + "_camera_info"

    writer = rep.writers.get("ROS2PublishCameraInfo")
    camera_info, _ = read_camera_info(render_product_path=rp_path)
    writer.initialize(
        frameId=frame_id,
        nodeNamespace="",
        queueSize=1,
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
    writer.attach([rp_path])
```

!!! note "`read_camera_info` のインポート元が変わりました"
    5.1 までの `isaacsim.ros2.bridge` に代わり、6.0 では **`isaacsim.ros2.core`** から `read_camera_info` をインポートします。

## ステップ 3：深度画像からのポイントクラウドのパブリッシュ

深度画像とカメラの内部パラメータから再構成したポイントクラウドを [sensor_msgs/PointCloud2](https://docs.ros2.org/latest/api/sensor_msgs/msg/PointCloud2.html) として配信します：

```python
def publish_pointcloud_from_depth(sensor: CameraSensor):
    rp_path, _, frame_id = _get_sensor_info(sensor)
    topic_name = frame_id + "_pointcloud"

    # このポイントクラウドパブリッシャは、カメラの内部パラメータを使って深度画像を
    # ポイントクラウドに変換する。この生成方法はセマンティックラベル付き
    # オブジェクトには対応していない。
    rv = omni.syntheticdata.SyntheticData.convert_sensor_type_to_rendervar(sd.SensorType.DistanceToImagePlane.name)
    writer = rep.writers.get(rv + "ROS2PublishPointCloud")
    writer.initialize(frameId=frame_id, nodeNamespace="", queueSize=1, topicName=topic_name)
    writer.attach([rp_path])
```

## ステップ 4：RGB 画像のパブリッシュ

```python
def publish_rgb(sensor: CameraSensor):
    rp_path, _, frame_id = _get_sensor_info(sensor)
    topic_name = frame_id + "_rgb"

    rv = omni.syntheticdata.SyntheticData.convert_sensor_type_to_rendervar(sd.SensorType.Rgb.name)
    writer = rep.writers.get(rv + "ROS2PublishImage")
    writer.initialize(frameId=frame_id, nodeNamespace="", queueSize=1, topicName=topic_name)
    writer.attach([rp_path])
```

## ステップ 5：深度画像のパブリッシュ

```python
def publish_depth(sensor: CameraSensor):
    rp_path, _, frame_id = _get_sensor_info(sensor)
    topic_name = frame_id + "_depth"

    rv = omni.syntheticdata.SyntheticData.convert_sensor_type_to_rendervar(sd.SensorType.DistanceToImagePlane.name)
    writer = rep.writers.get(rv + "ROS2PublishImage")
    writer.initialize(frameId=frame_id, nodeNamespace="", queueSize=1, topicName=topic_name)
    writer.attach([rp_path])
```

## ステップ 6：カメラ姿勢の TF ツリーのパブリッシュ

上の関数で配信されるポイントクラウドは、**ROS のカメラ軸の慣例（-Y が上、+Z が前方）**で配信されます。RViz で可視化しやすいように、次の 2 つのフレームを含む TF ツリーを `/tf` に配信します：

| フレーム | 軸の慣例 | 役割 |
|---|---|---|
| `{camera_frame_id}` | ROS カメラ慣例（-Y 上、+Z 前方） | ポイントクラウドが配信されるフレーム |
| `{camera_frame_id}_world` | ワールド慣例（+Z 上、+X 前方） | カメラの実際の姿勢を表すフレーム |

![カメラフレーム（ROS 慣例）](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/camera_frames_v2.005.png)

![カメラフレーム（ワールド慣例）](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/camera_frames_v2.004.png)

TF ツリーの構造は次のとおりです：

![TF ツリー構造](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/transformation.png)

- `world -> {camera_frame_id}` は、原点からカメラ（ROS カメラ慣例）への**動的**な変換で、カメラの動きに追従します。
- `{camera_frame_id} -> {camera_frame_id}_world` は、回転のみ・並進ゼロの**静的**な変換です。この回転はクォータニオン `[0.5, -0.5, 0.5, 0.5]`（[w, x, y, z] 順）で表されます。

ポイントクラウドは `{camera_frame_id}` で配信されるため、ポイントクラウドトピックの `frame_id` にも `{camera_frame_id}` を設定することが推奨されます。こうすると RViz でワールドフレームから見た正しい位置にポイントクラウドが表示されます。

!!! note "6.0 での変更点：Isaac Compute Transform Tree 経由で配信する"
    6.0 では **ROS2 Publish Transform Tree** ノードへの直接の `targetPrims` 入力は非推奨になり、代わりに **Isaac Compute Transform Tree** ノード（`isaacsim.core.nodes.IsaacComputeTransformTree`）がプリム階層を走査して親子フレームと姿勢の配列を計算し、その出力を Publish ノードに接続する構成になりました（[公式移行ガイド](https://docs.isaacsim.omniverse.nvidia.com/latest/migration_guides/isaac_sim_6_0/ros2_omnigraph_migration.html)参照）。以下のコードでは、カメラごとに **3 つのノード**（ComputeTF・PublishTF・PublishRawTF）を作成します。

```python
def publish_camera_tf(sensor: CameraSensor):
    _, camera_prim_path, camera_frame_id = _get_sensor_info(sensor)

    try:
        # カメラ TF 配信用の Action Graph を生成する
        ros_camera_graph_path = "/CameraTFActionGraph"

        # カメラグラフが見つからない場合は新規作成する
        if not stage_utils.get_current_stage().GetPrimAtPath(ros_camera_graph_path).IsValid():
            og.Controller.edit(
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
                    ],
                },
            )

        # カメラごとに 3 つのノードを生成する：
        # プリム階層を走査して親子フレームと姿勢の配列を出力する ComputeTF ノード、
        # ComputeTF の出力を受けて配信する TF パブリッシャ、
        # カメラ慣例→ワールド慣例の静的回転を配信する Raw TF パブリッシャ
        og.Controller.edit(
            ros_camera_graph_path,
            {
                og.Controller.Keys.CREATE_NODES: [
                    ("ComputeTF_" + camera_frame_id, "isaacsim.core.nodes.IsaacComputeTransformTree"),
                    ("PublishTF_" + camera_frame_id, "isaacsim.ros2.bridge.ROS2PublishTransformTree"),
                    ("PublishRawTF_" + camera_frame_id + "_world", "isaacsim.ros2.bridge.ROS2PublishRawTransformTree"),
                ],
                og.Controller.Keys.SET_VALUES: [
                    ("PublishTF_" + camera_frame_id + ".inputs:topicName", "/tf"),
                    # 注意：topicName を "/tf" 以外に変更すると、
                    # ROS の TF ブロードキャスタに認識されない
                    ("PublishRawTF_" + camera_frame_id + "_world.inputs:topicName", "/tf"),
                    ("PublishRawTF_" + camera_frame_id + "_world.inputs:parentFrameId", camera_frame_id),
                    ("PublishRawTF_" + camera_frame_id + "_world.inputs:childFrameId", camera_frame_id + "_world"),
                    # ROS カメラ慣例からワールド慣例（+Z 上、+X 前方）への静的変換：
                    ("PublishRawTF_" + camera_frame_id + "_world.inputs:rotation", [0.5, -0.5, 0.5, 0.5]),
                ],
                og.Controller.Keys.CONNECT: [
                    (ros_camera_graph_path + "/OnTick.outputs:tick",
                        "ComputeTF_" + camera_frame_id + ".inputs:execIn"),
                    ("ComputeTF_" + camera_frame_id + ".outputs:execOut",
                        "PublishTF_" + camera_frame_id + ".inputs:execIn"),
                    ("ComputeTF_" + camera_frame_id + ".outputs:parentFrames",
                        "PublishTF_" + camera_frame_id + ".inputs:parentFrames"),
                    ("ComputeTF_" + camera_frame_id + ".outputs:childFrames",
                        "PublishTF_" + camera_frame_id + ".inputs:childFrames"),
                    ("ComputeTF_" + camera_frame_id + ".outputs:translations",
                        "PublishTF_" + camera_frame_id + ".inputs:translations"),
                    ("ComputeTF_" + camera_frame_id + ".outputs:orientations",
                        "PublishTF_" + camera_frame_id + ".inputs:orientations"),
                    (ros_camera_graph_path + "/OnTick.outputs:tick",
                        "PublishRawTF_" + camera_frame_id + "_world.inputs:execIn"),
                    (ros_camera_graph_path + "/IsaacClock.outputs:simulationTime",
                        "PublishTF_" + camera_frame_id + ".inputs:timeStamp"),
                    (ros_camera_graph_path + "/IsaacClock.outputs:simulationTime",
                        "PublishRawTF_" + camera_frame_id + "_world.inputs:timeStamp"),
                ],
            },
        )
    except Exception as e:
        print(e)

    # ターゲットプリムは ComputeTF ノード側に設定する（PublishTF ノードはその出力を受け取るだけ）
    set_target_prims(
        primPath=ros_camera_graph_path + "/ComputeTF_" + camera_frame_id,
        inputName="inputs:targetPrims",
        targetPrimPaths=[camera_prim_path],
    )
```

## ステップ 7：カメラを作成してパブリッシャを呼び出す

ヘルパー関数をすべて貼り付けたら、スクリプトの末尾でカメラを作成し、各パブリッシャを呼び出して、シミュレーションループを回します：

```python
# RtxCamera が USD の Camera プリムを作成し、CameraSensor がレンダープロダクトと
# 以降の ROS 2 ライターが使う rgb / distance_to_image_plane アノテータを紐付ける
rtx_camera = RtxCamera(
    "/World/floating_camera",
    tick_rate=30.0,
    positions=np.array([-3.11, -1.87, 1.0]),
    # USD カメラ（既定：-Z 前方、+Y 上）を回転させ、ワールド +X 方向（+Z 上）を向ける
    orientations=transform_utils.euler_angles_to_quaternion(np.array([90, 0, -90]), degrees=True).numpy(),
)

simulation_app.update()

camera_sensor = CameraSensor(rtx_camera, resolution=(256, 256), annotators=["rgb", "distance_to_image_plane"])

############### カメラパブリッシュ関数の呼び出し ###############

publish_camera_tf(camera_sensor)
publish_camera_info(camera_sensor)
publish_rgb(camera_sensor)
publish_depth(camera_sensor)
publish_pointcloud_from_depth(camera_sensor)

####################################################################

# シミュレーションの開始
app_utils.play()

i = 0
while simulation_app.is_running() and (not args.test or i < 100):
    simulation_app.update()
    i += 1

app_utils.stop()
simulation_app.close()
```

## 実行と確認

1. `isaacsim.ros2.bridge` が有効な状態で、Isaac Sim フォルダの `python.sh` でスクリプトを実行します。この例では `{camera_frame_id}` はカメラのプリム名 `floating_camera` になります。
2. シーンに `/World/floating_camera` のカメラがあり、フォークリフトが映っていることを確認します：

    ![シミュレーションビュー](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isaac_tutorial_ros_camera_publishing_simview.png)

3. ターミナルでトピック一覧を確認します：

    ```bash
    ros2 topic list
    ```

    ```text
    /clock
    /floating_camera_camera_info
    /floating_camera_depth
    /floating_camera_pointcloud
    /floating_camera_rgb
    /parameter_events
    /rosout
    /tf
    ```

4. RViz2 を開き、**Fixed Frame** を `world` に設定してから、`/floating_camera_depth`、`/floating_camera_rgb`、`/floating_camera_pointcloud`、`/tf` の表示を有効にします。

    ![RViz 設定](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/rviz.png)

5. 深度画像と RGB 画像、ポイントクラウド、TF の 2 つのフレーム（`{camera_frame_id}_world` と `{camera_frame_id}`）が正しく表示されることを確認します：

    ![RGB と深度](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isaac_tutorial_ros_camera_publishing_rgbd.png)

    ![ポイントクラウド（正面）](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isaac_tutorial_ros_camera_publishing_pc_frontview.png)

    ![ポイントクラウド（側面）](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isaac_tutorial_ros_camera_publishing_pc_sideview.png)

## まとめ

このチュートリアルでは、Isaac Sim のカメラの ROS 2 パブリッシャ（CameraInfo・RGB・深度・ポイントクラウド・TF）を Python スクリプトからセットアップする方法を扱いました。マルチティックレンダリングにより、配信の周期はカメラの `tick_rate` にそのまま従います。5.1 までと異なり、パブリッシャごとのゲートステップ（間引き）の設定は不要になりました。センサー種別（IMU・RTX Lidar・カメラ）ごとに配信レートを変える方法は[チュートリアル 10: ROS 2 パブリッシュレートの設定](10_publish_rate.md)を参照してください。

## 次のステップ

- [チュートリアル 8: RTX Lidar センサー](08_rtx_lidar.md) - Turtlebot3 に RTX Lidar センサーを追加する方法を学びます。
