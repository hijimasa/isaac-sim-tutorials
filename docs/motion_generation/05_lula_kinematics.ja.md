---
title: Lula Kinematics Solver
---

# Lula Kinematics Solver

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- `LulaKinematicsSolver` で順運動学（FK）・逆運動学（IK）を計算する方法
- `ArticulationKinematicsSolver` でロボットに直接適用できる形にする方法
- IK の収束判定とロボットベース姿勢の設定
- IK ソルバー単体の使いどころと限界

## はじめに

### 前提条件

- [マニピュレータロボットの追加](../core_api/04_adding_a_manipulator_robot.md) を完了していること
- 未サポートのロボットで使う場合は [Robot Description エディタ](02_robot_description_editor.md) で `robot_description.yaml` を生成できること

### 所要時間

約 15〜20 分

### 概要

**Lula Kinematics Solver** は、2 つの設定ファイル（robot_description / URDF）で定義されたロボットの順運動学・逆運動学を計算します。`ArticulationKinematicsSolver` と組み合わせると、結果をロボットの Articulation に直接適用できます。純粋に運動学的で外界と相互作用しないため、**衝突球は不要**です。

## ステップ：FK / IK を計算する

Franka を読み込み、IK でロボットをターゲットへ動かす例です。

```python
import numpy as np
import os
import carb

from isaacsim.core.utils.extensions import get_extension_path_from_name
from isaacsim.core.utils.stage import add_reference_to_stage
from isaacsim.core.prims import Articulation
from isaacsim.core.utils.nucleus import get_assets_root_path
from isaacsim.core.prims import XFormPrim
from isaacsim.core.utils.numpy.rotations import euler_angles_to_quats

from isaacsim.robot_motion.motion_generation import ArticulationKinematicsSolver, LulaKinematicsSolver
from isaacsim.robot_motion.motion_generation import interface_config_loader

class FrankaKinematicsExample():
    def __init__(self):
        self._kinematics_solver = None
        self._articulation_kinematics_solver = None
        self._articulation = None
        self._target = None

    def load_example_assets(self):
        robot_prim_path = "/panda"
        path_to_robot_usd = get_assets_root_path() + "/Isaac/Robots/FrankaRobotics/FrankaPanda/franka.usd"
        add_reference_to_stage(path_to_robot_usd, robot_prim_path)
        self._articulation = Articulation(robot_prim_path)

        add_reference_to_stage(get_assets_root_path() + "/Isaac/Props/UIElements/frame_prim.usd", "/World/target")
        self._target = XFormPrim("/World/target")
        self._target.set_local_scales([0.04, 0.04, 0.04])
        self._target.set_default_state(np.array([.3, 0, .5]), euler_angles_to_quats([0, np.pi, 0]))
        return self._articulation, self._target

    def setup(self):
        # このロボットの URDF と Lula Robot Description ファイルを読み込む
        mg_extension_path = get_extension_path_from_name("isaacsim.robot_motion.motion_generation")
        kinematics_config_dir = os.path.join(mg_extension_path, "motion_policy_configs")

        self._kinematics_solver = LulaKinematicsSolver(
            robot_description_path=kinematics_config_dir + "/franka/rmpflow/robot_descriptor.yaml",
            urdf_path=kinematics_config_dir + "/franka/lula_franka_gen.urdf"
        )
        # サポート済みロボットは次の簡易版でも読み込める：
        # kinematics_config = interface_config_loader.load_supported_lula_kinematics_solver_config("Franka")
        # self._kinematics_solver = LulaKinematicsSolver(**kinematics_config)

        # 運動学を計算できる有効なフレーム名の一覧を表示
        print("Valid frame names:", self._kinematics_solver.get_all_frame_names())

        end_effector_name = "right_gripper"
        self._articulation_kinematics_solver = ArticulationKinematicsSolver(
            self._articulation, self._kinematics_solver, end_effector_name)

    def update(self, step: float):
        target_position, target_orientation = self._target.get_world_pose()

        # ロボットベースの移動を追跡
        robot_base_translation, robot_base_orientation = self._articulation.get_world_pose()
        self._kinematics_solver.set_robot_base_pose(robot_base_translation, robot_base_orientation)

        action, success = self._articulation_kinematics_solver.compute_inverse_kinematics(
            target_position, target_orientation)

        if success:
            self._articulation.apply_action(action)
        else:
            carb.log_warn("IK did not converge to a solution.  No action is being taken")

        # 使っていない順運動学の例：
        # ee_position, ee_rot_mat = articulation_kinematics_solver.compute_end_effector_pose()

    def reset(self):
        # 運動学はステートレス
        pass
```

**ポイント**

- `LulaKinematicsSolver` は Lula ベースの RMPflow と同じロボット記述ファイルを使い、URDF に存在する**任意のフレーム**で FK / IK を解けます。`get_all_frame_names()` で認識されるフレーム一覧を確認できます（Franka では `panda_link0`〜`panda_hand`、`right_gripper` など）。
- `ArticulationKinematicsSolver` に Articulation・ソルバー・エンドエフェクタ名を渡すと、`compute_end_effector_pose()`（FK）や `compute_inverse_kinematics()`（IK）を 1 行で計算できます。IK は現在の Articulation 位置を**ウォームスタート**として使い、結果を ArticulationAction として返します。
- IK は成功/失敗のフラグを返します。**収束した場合のみ**アクションを適用し、失敗時は警告を出して何もしません。
- `LulaKinematicsSolver` は、指定しない限りロボットベースが原点にあると仮定します。毎フレーム `set_robot_base_pose()` でベース位置を渡すと、ワールド座標で FK / IK を計算できます。

![Lula Kinematics Solver](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_full_tut_gui_lula_kinematics.webp)

!!! note "IK ソルバー単体の限界"
    `LulaKinematicsSolver` は Articulation がステージ上になくても、任意の位置で FK を、任意のウォームスタートで IK を計算できます。ただし、IK 解をそのままロボットに送るのはデモ以上には役立ちません。現実のシナリオでは終端位置だけでなく**そこへ至る経路**も決める必要があり、IK 単体では最適とは言えない粗い軌道しか作れません。

## まとめ

このチュートリアルでは、次の内容を学びました。

- `LulaKinematicsSolver` で URDF の任意フレームの FK / IK を計算すること
- `ArticulationKinematicsSolver` で結果をロボットに直接適用すること
- IK の収束判定とベース姿勢の設定
- IK 単体の限界と、経路計画や軌道生成との組み合わせの必要性

## 次のステップ

- 時間最適な軌道生成は [Lula Trajectory Generator](06_lula_trajectory_generator.md) を参照してください。
