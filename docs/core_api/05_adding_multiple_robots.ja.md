---
title: 複数ロボットの追加
---

# 複数ロボットの追加

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます:

- 異なる種類のロボット（移動ロボットとマニピュレータ）を同じシミュレーションに追加する方法
- `Cube`・`GeomPrim`・`RigidPrim` で押せるオブジェクトを作成する方法
- `Articulation` クラスで種類の異なるロボットを制御する方法
- ステートマシンロジックを使ってロボット間の動作を協調させる方法
- `Franka` クラスによる IK ベースのエンドエフェクタ制御とグリッパー操作

## はじめに

### 前提条件

- [チュートリアル 4: マニピュレータロボットの追加](04_adding_a_manipulator_robot.md) を完了していること

### 所要時間

約 15〜20 分

### ソースコードの準備

このチュートリアルでは、再び Extension Workflow に戻り、Hello World サンプルの `hello_world.py` を編集していきます。以下の手順でソースコードを開いてください。

1. **Windows > Examples > Robotics Examples** をアクティブにして、Robotics Examples タブを開きます。
2. **Robotics Examples > General > Hello World** をクリックします。
3. **Open Source Code** ボタンをクリックし、Visual Studio Code で `hello_world.py` を開きます。

詳しい手順は [Hello World の「サンプルを開く」セクション](01_hello_world.md#hello-world_1)を参照してください。

!!! warning "注意"
    **STOP** → **PLAY** の操作ではワールドが正しくリセットされない場合があります。シミュレーションをやり直す場合は、**RESET** ボタンを使用してください。

## 全体の流れ

このチュートリアルでは、Jetbot と Franka の2台のロボットが連携して以下の一連の動作を行うシミュレーションを段階的に構築します：

1. **Jetbot** がキューブを Franka の近くまで押して運ぶ
2. **Jetbot** が後退して Franka に作業スペースを譲る
3. **Franka** がキューブを拾い上げ、目標位置に配置する

コードを3段階に分けて段階的に実装していきます。

## ステップ 1: シーンの作成

まず、これまでのチュートリアルで使った Jetbot・Franka・キューブをシーンに配置します。`stage_utils.add_reference_to_stage()` でロボットのアセットを読み込み、`XformPrim` で Franka の位置を調整します。

```python linenums="1" hl_lines="14-54 56-63"
import isaacsim.core.experimental.utils.stage as stage_utils
import numpy as np
from isaacsim.core.experimental.materials import PreviewSurfaceMaterial
from isaacsim.core.experimental.objects import Cube
from isaacsim.core.experimental.prims import Articulation, GeomPrim, RigidPrim, XformPrim
from isaacsim.examples.base.base_sample_experimental import BaseSample
from isaacsim.storage.native import get_assets_root_path


class HelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()

    # -- setup_scene ここから -- #
    def setup_scene(self):
        assets_root_path = get_assets_root_path()

        # 地面を追加
        stage_utils.add_reference_to_stage(
            usd_path=assets_root_path + "/Isaac/Environments/Grid/default_environment.usd",
            path="/World/ground",
        )

        # 移動ロボット Jetbot を追加
        stage_utils.add_reference_to_stage(
            usd_path=assets_root_path + "/Isaac/Robots/NVIDIA/Jetbot/jetbot.usd",
            path="/World/Jetbot",
        )

        # Jetbot が押すためのキューブを Jetbot の前方に追加
        visual_material = PreviewSurfaceMaterial("/World/Materials/red")
        visual_material.set_input_values("diffuseColor", [1.0, 0.0, 0.0])
        cube_shape = Cube(
            paths="/World/Cube",
            positions=np.array([[0.15, 0.0, 0.025]]),  # Jetbot の前方
            sizes=[1.0],
            scales=np.array([[0.05, 0.05, 0.05]]),
            reset_xform_op_properties=True,
        )
        GeomPrim(paths=cube_shape.paths, apply_collision_apis=True)
        RigidPrim(paths=cube_shape.paths)
        cube_shape.apply_visual_materials(visual_material)

        # Jetbot がキューブを押し届ける先にマニピュレータ Franka を追加
        stage_utils.add_reference_to_stage(
            usd_path=assets_root_path + "/Isaac/Robots/FrankaRobotics/FrankaPanda/franka.usd",
            path="/World/Franka",
        )

        # キューブが作業範囲内に押し込まれるように Franka を配置
        franka_xform = XformPrim("/World/Franka")
        franka_xform.set_world_poses(positions=np.array([[0.8, -0.5, 0.0]]))

    # -- setup_scene ここまで -- #

    async def setup_post_load(self):
        # 両方のロボットの Articulation ハンドルを作成
        self._jetbot = Articulation("/World/Jetbot")
        self._franka = Articulation("/World/Franka")

        # ロボットの情報を出力
        print(f"Jetbot DOFs: {self._jetbot.num_dofs}, names: {self._jetbot.dof_names}")
        print(f"Franka DOFs: {self._franka.num_dofs}, names: {self._franka.dof_names}")
```

このコードのポイント：

| 処理 | 説明 |
|---|---|
| `stage_utils.add_reference_to_stage()` | ロボットの種類を問わず、USD アセットをステージに配置する |
| `XformPrim.set_world_poses()` | プリムのワールド座標を設定する（ここでは Franka の配置に使用） |
| `Articulation` | Jetbot（2 DOF）も Franka（9 DOF）も同じクラスでラップして制御できる |

**Ctrl+S** で保存し、**File > New From Stage Template > Empty** → **LOAD** を実行すると、2台のロボットとキューブがシーンに表示されます。

## ステップ 2: 複数ロボットの制御

次に、物理演算コールバックを追加して両方のロボットを同時に制御します。まずはシンプルに、Jetbot がキューブを前方に押し、一定ステップ後に停止する動作を実装します。

制御ロジックは以下の通りです：

```python linenums="1"
        self._step_counter += 1
        if self._step_counter < 300:
            # Jetbot を前進させてキューブを押す
            self._jetbot.set_dof_velocity_targets([[10.0, 10.0]])
        else:
            # 押し終わったら Jetbot を停止
            self._jetbot.set_dof_velocity_targets([[0.0, 0.0]])
```

コード全体は以下の通りです：

```python linenums="1" hl_lines="6 14-15 57-61 63-68 70-79 81-84"
import isaacsim.core.experimental.utils.stage as stage_utils
import numpy as np
from isaacsim.core.experimental.materials import PreviewSurfaceMaterial
from isaacsim.core.experimental.objects import Cube
from isaacsim.core.experimental.prims import Articulation, GeomPrim, RigidPrim, XformPrim
from isaacsim.core.simulation_manager import SimulationManager
from isaacsim.examples.base.base_sample_experimental import BaseSample
from isaacsim.storage.native import get_assets_root_path


class HelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        self._physics_callback_id = None
        self._step_counter = 0

    def setup_scene(self):
        assets_root_path = get_assets_root_path()

        # 地面を追加
        stage_utils.add_reference_to_stage(
            usd_path=assets_root_path + "/Isaac/Environments/Grid/default_environment.usd",
            path="/World/ground",
        )

        # 移動ロボット Jetbot を追加
        stage_utils.add_reference_to_stage(
            usd_path=assets_root_path + "/Isaac/Robots/NVIDIA/Jetbot/jetbot.usd",
            path="/World/Jetbot",
        )

        # Jetbot が押すためのキューブを Jetbot の前方に追加
        visual_material = PreviewSurfaceMaterial("/World/Materials/red")
        visual_material.set_input_values("diffuseColor", [1.0, 0.0, 0.0])
        cube_shape = Cube(
            paths="/World/Cube",
            positions=np.array([[0.15, 0.0, 0.025]]),
            sizes=[1.0],
            scales=np.array([[0.05, 0.05, 0.05]]),
            reset_xform_op_properties=True,
        )
        GeomPrim(paths=cube_shape.paths, apply_collision_apis=True)
        RigidPrim(paths=cube_shape.paths)
        cube_shape.apply_visual_materials(visual_material)

        # マニピュレータ Franka を追加
        stage_utils.add_reference_to_stage(
            usd_path=assets_root_path + "/Isaac/Robots/FrankaRobotics/FrankaPanda/franka.usd",
            path="/World/Franka",
        )

        # Jetbot の進路の前方右側に Franka を配置
        franka_xform = XformPrim("/World/Franka")
        franka_xform.set_world_poses(positions=np.array([[0.8, -0.5, 0.0]]))

    async def setup_post_load(self):
        # Articulation ハンドルを作成
        self._jetbot = Articulation("/World/Jetbot")
        self._franka = Articulation("/World/Franka")
        self._cube = RigidPrim("/World/Cube")
        self._step_counter = 0

        # 物理演算コールバックを登録
        from isaacsim.core.simulation_manager.impl.isaac_events import IsaacEvents

        self._physics_callback_id = SimulationManager.register_callback(
            self.physics_step, IsaacEvents.POST_PHYSICS_STEP
        )

    def physics_step(self, dt, context):
        # -- Jetbot の制御ここから -- #
        self._step_counter += 1
        if self._step_counter < 300:
            # Jetbot を前進させてキューブを押す
            self._jetbot.set_dof_velocity_targets([[10.0, 10.0]])
        else:
            # 押し終わったら Jetbot を停止
            self._jetbot.set_dof_velocity_targets([[0.0, 0.0]])
        # -- Jetbot の制御ここまで -- #

    def physics_cleanup(self):
        if self._physics_callback_id is not None:
            SimulationManager.deregister_callback(self._physics_callback_id)
            self._physics_callback_id = None
```

コードを保存して **LOAD** を実行すると、Jetbot がキューブを Franka に向かって押していく様子を確認できます。

![Jetbot がキューブを押す様子](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/core_api_tutorials_5_1.webp)

## ステップ 3: ステートマシンロジックの追加

最後に、2台のロボットを協調させるステートマシンを作成します。まず Jetbot がキューブを Franka に向かって押し、次に後退してスペースを空け、最後に Franka が `Franka` クラス（チュートリアル 4 参照）の IK ベースのエンドエフェクタ制御でピック＆プレースの一連の動作を実行します。

状態遷移は以下の通りです：

| 状態 | 動作 | 遷移条件 |
|---|---|---|
| `0` | Jetbot がキューブを目標位置まで押す | キューブが目標位置に十分近づいたら `1` へ |
| `1` | Jetbot が後退する | 100 ステップ経過で `2` へ（グリッパーを開く） |
| `2` | Franka がピック＆プレースを実行 | `_pick_phase`（0〜5）で細分化 |

ステートマシンの中核部分は以下の通りです：

```python linenums="1"
        if self._state == 0:
            # Jetbot がキューブを Franka まで押す
            cube_pos = self._cube.get_world_poses()[0].numpy()[0]
            if np.linalg.norm(cube_pos[:2] - self._cube_goal[:2]) > 0.05:
                self._jetbot.set_dof_velocity_targets([[10.0, 10.0]])
            else:
                self._jetbot.set_dof_velocity_targets([[0.0, 0.0]])
                print("Cube delivered! Backing up...")
                self._state = 1
                self._step_counter = 0

        elif self._state == 1:
            # Jetbot が後退する
            self._jetbot.set_dof_velocity_targets([[-8.0, -8.0]])
            self._step_counter += 1
            if self._step_counter > 100:
                self._jetbot.set_dof_velocity_targets(np.array([[0.0, 0.0]]))
                print("Franka starting pick-and-place...")
                self._state = 2
                self._step_counter = 0
                self._franka.open_gripper()

        elif self._state == 2:
            # ステップカウンタを使った Franka のピック＆プレースシーケンス
            cube_pos = self._cube.get_world_poses()[0].numpy()[0]
            down_orient = self._franka.get_downward_orientation()
            self._step_counter += 1

            if self._pick_phase == 0:
                # キューブの上方へ移動（120 ステップ待機）
                self._franka.set_end_effector_pose(
                    np.array([[cube_pos[0], cube_pos[1], cube_pos[2] + 0.2]]), down_orient
                )
                if self._step_counter > 120:
                    self._pick_phase = 1
                    self._step_counter = 0
            elif self._pick_phase == 1:
                # キューブへ下降（100 ステップ待機）
                self._franka.set_end_effector_pose(
                    np.array([[cube_pos[0], cube_pos[1], cube_pos[2] + 0.1]]), down_orient
                )
                if self._step_counter > 100:
                    self._franka.close_gripper()
                    self._pick_phase = 2
                    self._step_counter = 0
            elif self._pick_phase == 2:
                # グリッパーを閉じる（50 ステップ待機）
                self._franka.close_gripper()
                if self._step_counter > 50:
                    self._pick_phase = 3
                    self._step_counter = 0
            elif self._pick_phase == 3:
                # キューブを持ち上げる（100 ステップ待機）
                self._franka.set_end_effector_pose(
                    np.array([[cube_pos[0], cube_pos[1], cube_pos[2] + 0.25]]), down_orient
                )
                if self._step_counter > 100:
                    self._pick_phase = 4
                    self._step_counter = 0
            elif self._pick_phase == 4:
                # 目標位置へ移動（150 ステップ待機）
                self._franka.set_end_effector_pose(np.array([[0.3, 0.3, 0.15]]), down_orient)
                if self._step_counter > 150:
                    self._franka.open_gripper()
                    self._pick_phase = 5
                    self._step_counter = 0
            elif self._pick_phase == 5:
                # アームを持ち上げる（150 ステップ待機）
                self._franka.set_end_effector_pose(
                    np.array([[cube_pos[0], cube_pos[1], cube_pos[2] + 0.5]]), down_orient
                )
                if self._step_counter > 150:
                    self._step_counter = 0
```

コード全体は以下の通りです：

```python linenums="1" hl_lines="8 16 47-50 52-57 66-141 143-147"
import isaacsim.core.experimental.utils.stage as stage_utils
import numpy as np
from isaacsim.core.experimental.materials import PreviewSurfaceMaterial
from isaacsim.core.experimental.objects import Cube
from isaacsim.core.experimental.prims import Articulation, GeomPrim, RigidPrim, XformPrim
from isaacsim.core.simulation_manager import SimulationManager
from isaacsim.examples.base.base_sample_experimental import BaseSample
from isaacsim.robot.experimental.manipulators.examples.franka import Franka
from isaacsim.storage.native import get_assets_root_path


class HelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        self._physics_callback_id = None
        self._state = 0

    def setup_scene(self):
        assets_root_path = get_assets_root_path()

        # 地面を追加
        stage_utils.add_reference_to_stage(
            usd_path=assets_root_path + "/Isaac/Environments/Grid/default_environment.usd",
            path="/World/ground",
        )

        # 原点に Jetbot を追加
        stage_utils.add_reference_to_stage(
            usd_path=assets_root_path + "/Isaac/Robots/NVIDIA/Jetbot/jetbot.usd",
            path="/World/Jetbot",
        )

        # Jetbot の前方にキューブを追加
        visual_material = PreviewSurfaceMaterial("/World/Materials/blue")
        visual_material.set_input_values("diffuseColor", [0.0, 0.0, 1.0])
        cube_shape = Cube(
            paths="/World/Cube",
            positions=np.array([[0.15, 0.0, 0.0258]]),
            sizes=[1.0],
            scales=np.array([[0.05, 0.05, 0.05]]),
            reset_xform_op_properties=True,
        )
        GeomPrim(paths=cube_shape.paths, apply_collision_apis=True)
        RigidPrim(paths=cube_shape.paths)
        cube_shape.apply_visual_materials(visual_material)

        # IK とグリッパー制御のため Franka クラスを使って Franka を追加
        self._franka = Franka(robot_path="/World/Franka", create_robot=True)
        franka_xform = XformPrim("/World/Franka")
        franka_xform.set_world_poses(positions=[[0.8, -0.3, 0.0]])

    async def setup_post_load(self):
        self._jetbot = Articulation("/World/Jetbot")
        self._cube = RigidPrim("/World/Cube")
        self._cube_goal = np.array([1.2, 0.0, 0.0])  # 目標: Franka が横から届く位置
        self._step_counter = 0
        self._pick_phase = 0

        from isaacsim.core.simulation_manager.impl.isaac_events import IsaacEvents

        self._physics_callback_id = SimulationManager.register_callback(
            self.physics_step, IsaacEvents.POST_PHYSICS_STEP
        )
        self._state = 0

    def physics_step(self, dt, context):
        # -- ステートマシンここから -- #
        if self._state == 0:
            # Jetbot がキューブを Franka まで押す
            cube_pos = self._cube.get_world_poses()[0].numpy()[0]
            if np.linalg.norm(cube_pos[:2] - self._cube_goal[:2]) > 0.05:
                self._jetbot.set_dof_velocity_targets([[10.0, 10.0]])
            else:
                self._jetbot.set_dof_velocity_targets([[0.0, 0.0]])
                print("Cube delivered! Backing up...")
                self._state = 1
                self._step_counter = 0

        elif self._state == 1:
            # Jetbot が後退する
            self._jetbot.set_dof_velocity_targets([[-8.0, -8.0]])
            self._step_counter += 1
            if self._step_counter > 100:
                self._jetbot.set_dof_velocity_targets(np.array([[0.0, 0.0]]))
                print("Franka starting pick-and-place...")
                self._state = 2
                self._step_counter = 0
                self._franka.open_gripper()

        elif self._state == 2:
            # ステップカウンタを使った Franka のピック＆プレースシーケンス
            cube_pos = self._cube.get_world_poses()[0].numpy()[0]
            down_orient = self._franka.get_downward_orientation()
            self._step_counter += 1

            if self._pick_phase == 0:
                # キューブの上方へ移動（120 ステップ待機）
                self._franka.set_end_effector_pose(
                    np.array([[cube_pos[0], cube_pos[1], cube_pos[2] + 0.2]]), down_orient
                )
                if self._step_counter > 120:
                    self._pick_phase = 1
                    self._step_counter = 0
            elif self._pick_phase == 1:
                # キューブへ下降（100 ステップ待機）
                self._franka.set_end_effector_pose(
                    np.array([[cube_pos[0], cube_pos[1], cube_pos[2] + 0.1]]), down_orient
                )
                if self._step_counter > 100:
                    self._franka.close_gripper()
                    self._pick_phase = 2
                    self._step_counter = 0
            elif self._pick_phase == 2:
                # グリッパーを閉じる（50 ステップ待機）
                self._franka.close_gripper()
                if self._step_counter > 50:
                    self._pick_phase = 3
                    self._step_counter = 0
            elif self._pick_phase == 3:
                # キューブを持ち上げる（100 ステップ待機）
                self._franka.set_end_effector_pose(
                    np.array([[cube_pos[0], cube_pos[1], cube_pos[2] + 0.25]]), down_orient
                )
                if self._step_counter > 100:
                    self._pick_phase = 4
                    self._step_counter = 0
            elif self._pick_phase == 4:
                # 目標位置へ移動（150 ステップ待機）
                self._franka.set_end_effector_pose(np.array([[0.3, 0.3, 0.15]]), down_orient)
                if self._step_counter > 150:
                    self._franka.open_gripper()
                    self._pick_phase = 5
                    self._step_counter = 0
            elif self._pick_phase == 5:
                # アームを持ち上げる（150 ステップ待機）
                self._franka.set_end_effector_pose(
                    np.array([[cube_pos[0], cube_pos[1], cube_pos[2] + 0.5]]), down_orient
                )
                if self._step_counter > 150:
                    self._step_counter = 0
        # -- ステートマシンここまで -- #

    async def setup_post_reset(self):
        self._state = 0
        self._step_counter = 0
        self._pick_phase = 0
        self._franka.reset_to_default_pose()

    def physics_cleanup(self):
        if self._physics_callback_id is not None:
            SimulationManager.deregister_callback(self._physics_callback_id)
            self._physics_callback_id = None
```

!!! note "Articulation と Franka クラスの使い分け"
    Jetbot は速度指令だけで制御できるため汎用の `Articulation` クラスでラップしていますが、Franka は IK やグリッパー制御が必要なため、チュートリアル 4 で学んだ `Franka` クラス（`Articulation` の派生クラス）を使用しています。また、`setup_post_reset` で `reset_to_default_pose()` とステート変数の初期化を行うことで、**RESET** ボタンで最初からやり直せるようにしています。

コードを保存してシミュレーションを確認します：

1. **Ctrl+S** を押して保存し、**File > New From Stage Template > Empty** → **LOAD** を実行します。
2. 以下の一連の動作を確認します：
    - Jetbot がキューブを Franka の近くまで押して運ぶ
    - Jetbot が後退して退避する
    - Franka がキューブを拾い上げて目標位置に配置する

![複数ロボットの連携動作](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/core_api_tutorials_5_2.webp)

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. **複数のロボットとオブジェクト（キューブ）**を同じシーンに配置
2. `Cube`・`GeomPrim`・`RigidPrim` による**押せるオブジェクトの作成**
3. **Articulation クラス**による種類の異なるロボットの制御
4. 移動ロボット（Jetbot）がオブジェクトをマニピュレータ（Franka）まで**押し運ぶ動作**
5. 押す・後退する・拾うを協調させる**ステートマシンロジック**の構築
6. **Franka クラス**による IK ベースのエンドエフェクタ制御とグリッパー操作

## 次のステップ

次のチュートリアル「[複数ロボットシナリオ](06_multiple_tasks.md)」に進み、ロボットシナリオをクラスとして整理し、複数インスタンスを並列実行する方法を学びましょう。
