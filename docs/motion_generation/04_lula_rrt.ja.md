---
title: Lula RRT
---

# Lula RRT

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- `RRT` クラスで C 空間の開始位置からタスク空間ターゲットへの衝突回避パスを生成する方法
- RRT に必要な設定ファイルと主なパラメータ
- `PathPlannerVisualizer` でスパースなプランを Articulation アクションに変換する方法
- ターゲット移動時の再計画（replanning）の実装

## はじめに

### 前提条件

- [マニピュレータロボットの追加](../core_api/04_adding_a_manipulator_robot.md) を完了していること
- 未サポートのロボットで使う場合は [Robot Description エディタ](02_robot_description_editor.md) で `robot_description.yaml` を生成できること

### 所要時間

約 20〜25 分

### 概要

**Lula RRT** クラスは、C 空間（構成空間）の開始位置から、C 空間またはタスク空間のターゲットへの**衝突回避パス**を生成します。RMPflow が反応型のローカルポリシーであるのに対し、RRT は静的環境での**グローバルプランニング**を担います。

## ステップ 1：必要な設定ファイル

Lula RRT は、特定のロボットを識別するために 3 つの設定ファイルが必要です。これらのパスとロボット URDF 内のフレームに一致するエンドエフェクタ名で `RRT` クラスを初期化します。1 つのファイルは RRT アルゴリズム専用のパラメータを含み、他の Lula アルゴリズムとは共有されません。Franka 用 RRT 設定ファイルの例です。

```yaml
seed: 123456
step_size: 0.05
max_iterations: 50000
max_sampling: 10000
distance_metric_weights: [3.0, 2.0, 2.0, 1.5, 1.5, 1.0, 1.0]
task_space_frame_name: "panda_rightfingertip"
task_space_limits: [[0.0, 0.7], [-0.6, 0.6], [0.0, 0.8]]
cuda_tree_params:
    max_num_nodes: 10000
    max_buffer_size: 30
    num_nodes_cpu_gpu_crossover: 3000
c_space_planning_params:
    exploration_fraction: 0.5
task_space_planning_params:
    translation_target_zone_tolerance: 0.05
    orientation_target_zone_tolerance: 0.09
    translation_target_final_tolerance: 1e-4
    orientation_target_final_tolerance: 0.005
    # ... (勾配重み・探索/活用の割合・拡張サブステップなど)
```

各パラメータの説明は、API ドキュメントの `RRT.set_param()` の docstring を参照してください。

## ステップ 2：RRT の例

Franka を読み込み、RRT で障害物を回避してターゲットへ動かす例です。**60 フレームごと**に（ターゲットが移動していれば）現在のターゲット位置へ再計画します。失敗した場合はプランが `None` になり、アクションは取られません。

```python
import numpy as np
import os

from isaacsim.core.utils.extensions import get_extension_path_from_name
from isaacsim.core.utils.stage import add_reference_to_stage
from isaacsim.core.prims import Articulation
from isaacsim.core.utils.nucleus import get_assets_root_path
from isaacsim.core.api.objects.cuboid import VisualCuboid
from isaacsim.core.prims import XFormPrim
from isaacsim.core.utils.numpy.rotations import euler_angles_to_quats, quats_to_rot_matrices
from isaacsim.core.utils.distance_metrics import rotational_distance_angle

from isaacsim.robot_motion.motion_generation import PathPlannerVisualizer
from isaacsim.robot_motion.motion_generation.lula import RRT
from isaacsim.robot_motion.motion_generation import interface_config_loader

class FrankaRrtExample():
    def __init__(self):
        self._rrt = None
        self._path_planner_visualizer = None
        self._plan = []
        self._articulation = None
        self._target = None
        self._frame_counter = 0

    def load_example_assets(self):
        robot_prim_path = "/panda"
        path_to_robot_usd = get_assets_root_path() + "/Isaac/Robots/FrankaRobotics/FrankaPanda/franka.usd"
        add_reference_to_stage(path_to_robot_usd, robot_prim_path)
        self._articulation = Articulation(robot_prim_path)

        add_reference_to_stage(get_assets_root_path() + "/Isaac/Props/UIElements/frame_prim.usd", "/World/target")
        self._target = XFormPrim("/World/target", scale=[.04, .04, .04])
        self._target.set_default_state(np.array([.45, .5, .7]), euler_angles_to_quats([3*np.pi/4, 0, np.pi]))
        self._obstacle = VisualCuboid("/World/Wall", position=np.array([.3, .6, .6]), size=1.0, scale=np.array([.1, .4, .4]))
        return self._articulation, self._target

    def setup(self):
        mg_extension_path = get_extension_path_from_name("isaacsim.robot_motion.motion_generation")
        rmp_config_dir = os.path.join(mg_extension_path, "motion_policy_configs")
        rrt_config_dir = os.path.join(mg_extension_path, "path_planner_configs")

        # RRT オブジェクトを初期化
        self._rrt = RRT(
            robot_description_path=rmp_config_dir + "/franka/rmpflow/robot_descriptor.yaml",
            urdf_path=rmp_config_dir + "/franka/lula_franka_gen.urdf",
            rrt_config_path=rrt_config_dir + "/franka/rrt/franka_planner_config.yaml",
            end_effector_frame_name="right_gripper"
        )
        # サポート済みロボットは次の簡易版でも読み込める：
        # rrt_config = interface_config_loader.load_supported_path_planner_config("Franka", "RRT")
        # self._rrt = RRT(**rrt_config)

        self._rrt.add_obstacle(self._obstacle)
        # Isaac Sim を長時間ブロックしないよう最大反復回数を設定
        self._rrt.set_max_iterations(5000)
        # PathPlannerVisualizer で ArticulationAction の軌道を生成
        self._path_planner_visualizer = PathPlannerVisualizer(self._articulation, self._rrt)
        self.reset()

    def update(self, step: float):
        current_target_translation, current_target_orientation = self._target.get_world_pose()
        current_target_rotation = quats_to_rot_matrices(current_target_orientation)

        translation_distance = np.linalg.norm(self._target_translation - current_target_translation)
        rotation_distance = rotational_distance_angle(current_target_rotation, self._target_rotation)
        target_moved = translation_distance > 0.01 or rotation_distance > 0.01

        if (self._frame_counter % 60 == 0 and target_moved):
            # ターゲットが移動していれば 60 フレームごとに再計画
            self._rrt.set_end_effector_target(current_target_translation, current_target_orientation)
            self._rrt.update_world()
            self._plan = self._path_planner_visualizer.compute_plan_as_articulation_actions(max_cspace_dist=.01)
            self._target_translation = current_target_translation
            self._target_rotation = current_target_rotation

        if self._plan:
            action = self._plan.pop(0)
            self._articulation.apply_action(action)

        self._frame_counter += 1

    def reset(self):
        self._target_translation = np.zeros(3)
        self._target_rotation = np.eye(3)
        self._frame_counter = 0
        self._plan = []
```

**ポイント**

- RRT は、線形補間すると衝突回避パスになる**スパースなプラン**を出力します。
- `PathPlanner` インターフェースの実装として、RRT を `PathPlannerVisualizer` に渡すと、その出力を Articulation が直接使える形に変換できます。
- 再計画の流れ：`set_end_effector_target`（新ターゲットを通知）→ `update_world`（監視中の障害物位置を問い合わせ）→ `compute_plan_as_articulation_actions`（ArticulationAction のリストを生成）。
- `max_cspace_dist=.01` は、指令する 2 つのロボット位置間の L2 ノルムが最大 0.01 になるようスパース出力を補間します。毎フレーム、プランから 1 アクションを取り出してロボットに送ります。

![Lula RRT](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_full_tut_gui_rrt.webp)

## 現在の制限：プランを正確に追従するには

`PathPlannerVisualizer` が「Visualizer」と呼ばれるのは、出力プランの**可視化**を目的としており、それ以上の用途にはあまり適さないためです。RRT プランを密に線形補間した軌道は、時間最適でも滑らかでもありません。より理論的に妥当な形でプランを追従するには、RRT の出力を [Lula Trajectory Generator](06_lula_trajectory_generator.md) と組み合わせます。これは Robotics Examples タブの **Path Planning Example** で示されています（**Windows > Examples > Robotics Examples**）。

## まとめ

このチュートリアルでは、次の内容を学びました。

- `RRT` クラスで開始位置からタスク空間ターゲットへの衝突回避パスを生成すること
- 3 つの設定ファイルと `set_max_iterations` などの主なパラメータ
- `PathPlannerVisualizer` でスパースなプランを Articulation アクションに変換すること
- ターゲット移動時の再計画の実装と、正確な追従には Trajectory Generator が必要なこと

## 次のステップ

- 順運動学・逆運動学については [Lula Kinematics Solver](05_lula_kinematics.md) を参照してください。
- 時間最適な軌道生成は [Lula Trajectory Generator](06_lula_trajectory_generator.md) を参照してください。
