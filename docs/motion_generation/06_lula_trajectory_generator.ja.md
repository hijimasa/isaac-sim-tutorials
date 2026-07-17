---
title: Lula Trajectory Generator
---

# Lula Trajectory Generator

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- `LulaCSpaceTrajectoryGenerator` で C 空間ウェイポイントをつなぐ軌道を生成する方法
- 時間最適（time-optimal）軌道とタイムスタンプ（time-stamped）軌道の違い
- `LulaTaskSpaceTrajectoryGenerator` でタスク空間の軌道を生成する方法
- `lula.TaskSpacePathSpec` / `CompositePathSpec` で円弧・円を含む複雑な軌道を定義する方法
- `ArticulationTrajectory` で軌道を ArticulationAction のシーケンスに変換する方法

## はじめに

### 前提条件

- [マニピュレータロボットの追加](../core_api/04_adding_a_manipulator_robot.md) を完了していること
- [Lula Kinematics Solver](05_lula_kinematics.md) を理解していること

### 所要時間

約 25〜30 分

### 概要

**Lula Trajectory Generator** は、シミュレートロボットの Articulation に簡単に適用できる、タスク空間・C 空間の軌道を生成します。この例では UR10 を使います。

![Lula Trajectory Generator](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_4.5_full_tut_gui_lula_trajectory_gen.webp)

## ステップ 1：C 空間の軌道を生成する

`LulaCSpaceTrajectoryGenerator` は、与えられた C 空間ウェイポイントの集合を**スプライン補間**でつなぐ軌道を生成します。まず、共通のセットアップで 3 つのジェネレータ／ソルバーを初期化します（robot_description と URDF は共通）。

```python
from isaacsim.robot_motion.motion_generation import (
    LulaCSpaceTrajectoryGenerator,
    LulaTaskSpaceTrajectoryGenerator,
    LulaKinematicsSolver,
    ArticulationTrajectory,
)
import lula

# setup() 内（rmp_config_dir は motion_policy_configs へのパス）
ur10 = "/universal_robots/ur10/"
self._c_space_trajectory_generator = LulaCSpaceTrajectoryGenerator(
    robot_description_path=rmp_config_dir + ur10 + "rmpflow/ur10_robot_description.yaml",
    urdf_path=rmp_config_dir + ur10 + "ur10_robot.urdf")
self._taskspace_trajectory_generator = LulaTaskSpaceTrajectoryGenerator(
    robot_description_path=rmp_config_dir + ur10 + "rmpflow/ur10_robot_description.yaml",
    urdf_path=rmp_config_dir + ur10 + "ur10_robot.urdf")
self._kinematics_solver = LulaKinematicsSolver(
    robot_description_path=rmp_config_dir + ur10 + "rmpflow/ur10_robot_description.yaml",
    urdf_path=rmp_config_dir + ur10 + "ur10_robot.urdf")
self._end_effector_name = "ee_link"
```

C 空間ウェイポイントから 2 種類の軌道を生成します。

```python
def setup_cspace_trajectory(self):
    c_space_points = np.array([
        [-0.41, 0.5, -2.36, -1.28, 5.13, -4.71],
        [-1.43, 1.0, -2.58, -1.53, 6.0, -4.74],
        [-2.83, 0.34, -2.11, -1.38, 1.26, -4.71],
        [-0.41, 0.5, -2.36, -1.28, 5.13, -4.71],
    ])
    timestamps = np.array([0, 5, 10, 13])

    # 時間最適な軌道
    trajectory_time_optimal = self._c_space_trajectory_generator.compute_c_space_trajectory(c_space_points)
    # 指定時刻に各ウェイポイントを通過するタイムスタンプ軌道
    trajectory_timestamped = self._c_space_trajectory_generator.compute_timestamped_c_space_trajectory(
        c_space_points, timestamps)

    if trajectory_time_optimal is None or trajectory_timestamped is None:
        carb.log_warn("No trajectory could be computed")
        self._action_sequence = []
    else:
        physics_dt = 1 / 60
        self._action_sequence = []
        # 2 つの軌道を続けて実行
        at_optimal = ArticulationTrajectory(self._articulation, trajectory_time_optimal, physics_dt)
        self._action_sequence.extend(at_optimal.get_action_sequence())
        at_timestamped = ArticulationTrajectory(self._articulation, trajectory_timestamped, physics_dt)
        self._action_sequence.extend(at_timestamped.get_action_sequence())
```

**ポイント**

- ジェネレータには 2 つの目的があります。**時間最適** … ロボットの速度・加速度・ジャークのいずれかのリミットを軌道全体で常に飽和させる。**タイムスタンプ** … 指定した時刻（例：`[0, 5, 10, 13]` 秒）に各ウェイポイントを通過する。
- 生成される `LulaTrajectory` オブジェクトを `ArticulationTrajectory` に渡すと、`get_action_sequence()` で ArticulationAction のリストが得られます。ここでは物理フレームレートを `1/60` 秒に固定していると仮定します。
- ウェイポイントをつなぐ軌道が計算できない場合（到達不能や関節リミットに極めて近いなど）、戻り値は `None` になります。

!!! tip "ウェイポイントの可視化"
    `kinematics_solver.compute_forward_kinematics(end_effector_name, point)` で各 C 空間点をタスク空間に変換し、フレーム prim を配置すると、ロボットが各ターゲットを通過しているか確認できます。

## ステップ 2：タスク空間の軌道を生成する（単純な例）

最も単純なケースでは、タスク空間の位置＋クォータニオン姿勢のターゲット集合を渡すと、タスク空間で**線形補間**した軌道が生成されます。

```python
def setup_taskspace_trajectory(self):
    task_space_position_targets = np.array([
        [0.3, -0.3, 0.1], [0.3, 0.3, 0.1], [0.3, 0.3, 0.5],
        [0.3, -0.3, 0.5], [0.3, -0.3, 0.1],
    ])
    task_space_orientation_targets = np.tile(np.array([0, 1, 0, 0]), (5, 1))

    trajectory = self._taskspace_trajectory_generator.compute_task_space_trajectory_from_points(
        task_space_position_targets, task_space_orientation_targets, self._end_effector_name)

    if trajectory is None:
        carb.log_warn("No trajectory could be computed")
        self._action_sequence = []
    else:
        physics_dt = 1 / 60
        articulation_trajectory = ArticulationTrajectory(self._articulation, trajectory, physics_dt)
        self._action_sequence = articulation_trajectory.get_action_sequence()
```

`compute_task_space_trajectory_from_points` には、各ウェイポイントの位置・姿勢と、URDF のエンドエフェクタフレームを指定します。つなげられない場合は `None` を返します。

## ステップ 3：複雑な軌道を定義する（PathSpec）

`lula.TaskSpacePathSpec` を使うと、線形補間だけでなく**円弧や円**を含むパスを、姿勢の指定方法を選びながら定義できます。さらに `lula.CompositePathSpec` で C 空間パスとタスク空間パスを組み合わせられます。

```python
def setup_advanced_trajectory(self):
    initial_c_space_robot_pose = np.array([0, 0, 0, 0, 0, 0])
    composite_path_spec = lula.create_composite_path_spec(initial_c_space_robot_pose)

    # Lula 独自の回転・6DOF 姿勢クラス: Rotation3, Pose3
    r0 = lula.Rotation3(np.pi/2, np.array([1.0, 0.0, 0.0]))
    t0 = np.array([.3, -.1, .3])
    task_space_spec = lula.create_task_space_path_spec(lula.Pose3(r0, t0))

    t1 = np.array([.3, -.1, .5]); r1 = lula.Rotation3(np.pi/3, np.array([1, 0, 0]))
    task_space_spec.add_linear_path(lula.Pose3(r1, t1))  # 6DOF を線形補間
    task_space_spec.add_translation(t0)                  # 並進のみ（回転は一定）
    task_space_spec.add_rotation(r0)                     # 回転のみ

    # 3 点円弧（midpoint を通る）
    t2 = np.array([.3, .3, .3]); midpoint = np.array([.3, 0, .5])
    task_space_spec.add_three_point_arc(t2, midpoint, constant_orientation=True)   # 姿勢一定
    task_space_spec.add_three_point_arc(t0, midpoint, constant_orientation=False)  # 円弧に接する姿勢
    task_space_spec.add_three_point_arc_with_orientation_target(lula.Pose3(r1, t2), midpoint)  # 姿勢ターゲット

    # 接線円弧（2 点をつなぐ円。midpoint 不要）
    task_space_spec.add_tangent_arc(t0, constant_orientation=True)
    task_space_spec.add_tangent_arc(t2, constant_orientation=False)
    task_space_spec.add_tangent_arc_with_orientation_target(lula.Pose3(r0, t0))

    # C 空間パススペック
    c_space_spec = lula.create_c_space_path_spec(np.array([0, 0, 0, 0, 0, 0]))
    c_space_spec.add_c_space_waypoint(np.array([0, 0.5, -2.0, -1.28, 5.13, -4.71]))

    # 2 つのスペックを composite に結合（transition_mode で接続方法を指定）
    composite_path_spec.add_task_space_path_spec(task_space_spec, lula.CompositePathSpec.TransitionMode.FREE)
    composite_path_spec.add_c_space_path_spec(c_space_spec, lula.CompositePathSpec.TransitionMode.FREE)

    trajectory = self._taskspace_trajectory_generator.compute_task_space_trajectory_from_path_spec(
        composite_path_spec, self._end_effector_name)
    # ... trajectory を ArticulationTrajectory に渡す（ステップ 2 と同様）
```

**タスク空間パスの基本操作**

- `add_translation` … 回転を固定して並進のみ線形補間
- `add_rotation` … 並進を固定して回転のみ線形補間
- `add_linear_path` … 回転・並進の両方を新しい 6DOF 点へ線形補間

**円弧・円**

- **3 点円弧**（`add_three_point_arc`）… midpoint を通って並進ターゲットへ移動
- **接線円弧**（`add_tangent_arc`）… midpoint なしで 2 点をつなぐ円

いずれも姿勢の指定に 3 通りあります：**一定（constant）** / **円弧に接する（tangent）** / **姿勢ターゲットへ補間（orientation target）**。

!!! note "TransitionMode（結合時の接続方法）"
    - `LINEAR_TASK_SPACE` … C 空間からタスク空間点へタスク空間内で線形につなぐ（task_space スペック追加時のみ）
    - `FREE` … 接続方法に制約を課さない
    - `SKIP` … 追加するスペックの最初の点をスキップし、直前の姿勢を代わりに使う

## まとめ

このチュートリアルでは、次の内容を学びました。

- `LulaCSpaceTrajectoryGenerator` で C 空間ウェイポイントを時間最適／タイムスタンプ軌道に変換すること
- `LulaTaskSpaceTrajectoryGenerator` でタスク空間ターゲットを線形につなぐ軌道を生成すること
- `lula.TaskSpacePathSpec` / `CompositePathSpec` で円弧・円・C 空間を組み合わせた複雑な軌道を定義すること
- `ArticulationTrajectory.get_action_sequence()` でロボットに適用可能なアクション列を得ること

## 次のステップ

- 新しいロボットへの RMPflow 適用は [新しいマニピュレータ用の RMPflow 設定](07_configure_rmpflow_denso.md) を参照してください。
- GPU 加速のモーション生成は [cuRobo と cuMotion](08_curobo.md) を参照してください。
