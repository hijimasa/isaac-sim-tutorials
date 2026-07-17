---
title: 複数ロボットシナリオ
---

# 複数ロボットシナリオ

!!! note "旧タイトル「複数タスクの実行」について"
    Isaac Sim 6.0 で公式チュートリアルが「Multiple Tasks」から「Multiple Robot Scenarios」に改題され、内容も Task クラスベースから Python クラスによるシナリオ管理へと刷新されました。本ページもそれに合わせて更新しています。

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます:

- ロボットシナリオを再利用可能な Python クラスとして整理する方法
- `offset` パラメータを使って複数のシナリオをワールド内に空間配置する方法
- ループで複数のシナリオを並列実行する方法
- シナリオパラメータへのランダム化の追加
- 複数ロボットインスタンスを管理する際のベストプラクティス

## はじめに

### 前提条件

- [チュートリアル 5: 複数ロボットの追加](05_adding_multiple_robots.md) を完了していること

### 所要時間

約 15〜20 分

### ソースコードの準備

このチュートリアルでは、前回に引き続き Hello World サンプルの `hello_world.py` を編集していきます。前回のチュートリアルから続けて作業している場合はそのまま進めてください。別の日に作業を再開する場合は、以下の手順でソースコードを開いてください。

1. **Windows > Examples > Robotics Examples** をアクティブにして、Robotics Examples タブを開きます。
2. **Robotics Examples > General > Hello World** をクリックします。
3. **Open Source Code** ボタンをクリックし、Visual Studio Code で `hello_world.py` を開きます。

詳しい手順は [Hello World の「サンプルを開く」セクション](01_hello_world.md)を参照してください。

!!! warning "注意"
    **STOP** → **PLAY** の操作ではワールドが正しくリセットされない場合があります。シミュレーションをやり直す場合は、**RESET** ボタンを使用してください。

## クラスによるロボットシナリオの整理

複数のロボットに同じようなタスクを実行させる場合、ロボットのセットアップと制御ロジックを**再利用可能なクラス**にカプセル化しておくと便利です。このアプローチにより、異なるパラメータ（位置オフセットなど）を持つ複数のインスタンスを簡単に作成できます。

前回のチュートリアルで作った「Jetbot がキューブを Franka まで押し、Franka が拾い上げる」一連の流れを、`RobotScenario` クラスとして整理します：

| メソッド | 役割 |
|---|---|
| `setup_scene()` | このシナリオのロボットとキューブを（`offset` を加味して）作成する |
| `initialize()` | シーンロード後にアーティキュレーションハンドルを作成する |
| `step()` | シナリオのロジックを 1 ステップ実行する（ステートマシン） |
| `reset()` | シナリオの状態をリセットする |

```python linenums="1" hl_lines="11-23 25-56 58-62 71-95 139-170"
import isaacsim.core.experimental.utils.stage as stage_utils
import numpy as np
from isaacsim.core.experimental.objects import Cube, DomeLight, GroundPlane
from isaacsim.core.experimental.prims import Articulation, GeomPrim, RigidPrim, XformPrim
from isaacsim.core.simulation_manager import SimulationEvent, SimulationManager
from isaacsim.examples.base.base_sample_experimental import BaseSample
from isaacsim.robot.experimental.manipulators.examples.franka import Franka
from isaacsim.storage.native import get_assets_root_path


class RobotScenario:
    """Jetbot + Franka + キューブのシナリオをオフセット付きでカプセル化する。"""

    def __init__(self, name: str, offset: np.ndarray = np.array([0.0, 0.0, 0.0])):
        self.name = name
        self.offset = offset
        self.state = 0
        self.step_counter = 0
        self.pick_phase = 0
        self.jetbot = None
        self.franka = None
        self.cube = None
        self.cube_goal = np.array([1.2, 0.0, 0.0]) + offset

    def setup_scene(self):
        """このシナリオのロボットとキューブを作成する。"""
        assets_root_path = get_assets_root_path()
        base_path = f"/World/{self.name}"

        # Jetbot を追加
        stage_utils.add_reference_to_stage(
            usd_path=assets_root_path + "/Isaac/Robots/NVIDIA/Jetbot/jetbot.usd",
            path=f"{base_path}/Jetbot",
        )
        jetbot_xform = XformPrim(f"{base_path}/Jetbot")
        jetbot_xform.reset_xform_op_properties()
        jetbot_xform.set_world_poses(positions=self.offset.tolist())

        # Jetbot の前方にキューブを追加
        cube_pos = self.offset + np.array([0.15, 0.0, 0.025])
        cube_shape = Cube(
            paths=f"{base_path}/Cube",
            positions=cube_pos.tolist(),
            sizes=1.0,
            scales=[0.05, 0.05, 0.05],
            colors="red",
        )
        GeomPrim(paths=cube_shape.paths, apply_collision_apis=True)
        RigidPrim(paths=cube_shape.paths)

        # Franka を追加
        franka_pos = self.offset + np.array([0.8, -0.3, 0.0])
        self.franka = Franka(robot_path=f"{base_path}/Franka", create_robot=True)
        franka_xform = XformPrim(f"{base_path}/Franka")
        franka_xform.reset_xform_op_properties()
        franka_xform.set_world_poses(positions=franka_pos.tolist())

    def initialize(self):
        """シーンロード後にアーティキュレーションハンドルを初期化する。"""
        base_path = f"/World/{self.name}"
        self.jetbot = Articulation(f"{base_path}/Jetbot")
        self.cube = RigidPrim(f"{base_path}/Cube")

    def reset(self):
        """シナリオの状態をリセットする。"""
        self.state = 0
        self.step_counter = 0
        self.pick_phase = 0
        self.franka.reset_to_default_pose()

    def step(self):
        """シナリオのロジックを1ステップ実行する。"""
        if self.state == 0:
            # Jetbot がキューブを押す
            cube_pos = self.cube.get_world_poses()[0].numpy()[0]
            if np.linalg.norm(cube_pos[:2] - self.cube_goal[:2]) > 0.05:
                self.jetbot.set_dof_velocity_targets([10.0, 10.0])
            else:
                self.jetbot.set_dof_velocity_targets([0.0, 0.0])
                self.state = 1
                self.step_counter = 0

        elif self.state == 1:
            # Jetbot が後退する
            self.jetbot.set_dof_velocity_targets([-8.0, -8.0])
            self.step_counter += 1
            if self.step_counter > 100:
                self.jetbot.set_dof_velocity_targets([0.0, 0.0])
                self.state = 2
                self.step_counter = 0
                self.franka.open_gripper()

        elif self.state == 2:
            # Franka のピック＆プレース
            self._franka_pick_place()

    def _franka_pick_place(self):
        """Franka のピック＆プレースのステートマシンを実行する。"""
        cube_pos = self.cube.get_world_poses()[0].numpy()[0]
        down_orient = self.franka.get_downward_orientation()
        self.step_counter += 1

        if self.pick_phase == 0:
            self.franka.set_end_effector_pose(np.array([cube_pos[0], cube_pos[1], cube_pos[2] + 0.2]), down_orient)
            if self.step_counter > 120:
                self.pick_phase = 1
                self.step_counter = 0
        elif self.pick_phase == 1:
            self.franka.set_end_effector_pose(np.array([cube_pos[0], cube_pos[1], cube_pos[2] + 0.1]), down_orient)
            if self.step_counter > 100:
                self.pick_phase = 2
                self.step_counter = 0
        elif self.pick_phase == 2:
            self.franka.close_gripper()
            if self.step_counter > 100:
                self.pick_phase = 3
                self.step_counter = 0
        elif self.pick_phase == 3:
            _, current_position, _ = self.franka.get_current_state()
            target = current_position + np.array([0.1, 0.0, 0.08])
            self.franka.set_end_effector_pose(position=target, orientation=down_orient)
            if self.step_counter > 150:
                self.step_counter = 0
                self.pick_phase = 4
        elif self.pick_phase == 4:
            _, current_position, _ = self.franka.get_current_state()
            target = current_position + np.array([0.1, 0.0, 0.01])
            self.franka.set_end_effector_pose(position=target, orientation=down_orient)
            if self.step_counter > 150:
                self.step_counter = 0
                self.pick_phase = 5
        elif self.pick_phase == 5:
            self.franka.open_gripper()
            if self.step_counter > 150:
                self.step_counter = 0
                self.state = 6  # 完了


class HelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        self._physics_callback_id = None
        self._scenarios = []

    def setup_scene(self):
        GroundPlane("/World/ground_plane")
        dome_light = DomeLight("/World/DomeLight")
        dome_light.set_intensities(1000)

        # 単一のシナリオを作成
        self._scenario = RobotScenario(name="scenario_0", offset=np.array([0.0, 0.0, 0.0]))
        self._scenario.setup_scene()

    async def setup_post_load(self):
        self._scenario.initialize()

        self._physics_callback_id = SimulationManager.register_callback(
            self.physics_step, event=SimulationEvent.PHYSICS_POST_STEP
        )

    def physics_step(self, dt, context):
        self._scenario.step()

    async def setup_post_reset(self):
        self._scenario.reset()

    def physics_cleanup(self):
        if self._physics_callback_id is not None:
            SimulationManager.deregister_callback(self._physics_callback_id)
            self._physics_callback_id = None
```

!!! note "シナリオごとに一意なプリムパスを使う"
    `RobotScenario` はシナリオ名から `/World/scenario_0/Jetbot` のような**一意のプリムパス**を組み立てます。これにより、複数のシナリオを追加してもプリムパスが衝突しません。

**Ctrl+S** で保存し、**File > New From Stage Template > Empty** → **LOAD** を実行すると、1組の Jetbot + Franka がキューブの受け渡しを行います。

![ロボットシナリオの実行](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/core_api_tutorials_6_1.webp)

## 複数シナリオへのスケーリング

シナリオをクラス化したので、あとはループで複数のインスタンスを作成するだけで並列実行できます。以下の変更を加えます。

シナリオ数を設定します：

```python linenums="1"
        self._num_scenarios = 3  # 並列実行するシナリオ数
```

シナリオを作成します：

```python linenums="1"
        # Y 軸方向にオフセットして複数のシナリオを作成
        for i in range(self._num_scenarios):
            offset = np.array([0.0, (i - 1) * 2.0, 0.0])  # Y 軸方向に等間隔で配置
            scenario = RobotScenario(name=f"scenario_{i}", offset=offset, randomize=False)
            scenario.setup_scene()
            self._scenarios.append(scenario)
```

シナリオを初期化します：

```python linenums="1"
        # すべてのシナリオを初期化
        for scenario in self._scenarios:
            scenario.initialize()
```

すべてのシナリオをステップ実行します：

```python linenums="1"
        # すべてのシナリオをステップ実行
        for scenario in self._scenarios:
            scenario.step()
```

すべてのシナリオをリセットします：

```python linenums="1"
        # すべてのシナリオをリセット
        for scenario in self._scenarios:
            scenario.reset()
```

クリーンアップします：

```python linenums="1"
        self._scenarios = []
```

コード全体は以下の通りです（`RobotScenario` クラスには次のセクションで使う `randomize` パラメータも追加しています）：

```python linenums="1" hl_lines="14 19 26-31 152-154 161-168 171-175 182-186 189-193 200-201"
import isaacsim.core.experimental.utils.stage as stage_utils
import numpy as np
from isaacsim.core.experimental.objects import Cube, DomeLight, GroundPlane
from isaacsim.core.experimental.prims import Articulation, GeomPrim, RigidPrim, XformPrim
from isaacsim.core.simulation_manager import SimulationEvent, SimulationManager
from isaacsim.examples.base.base_sample_experimental import BaseSample
from isaacsim.robot.experimental.manipulators.examples.franka import Franka
from isaacsim.storage.native import get_assets_root_path


class RobotScenario:
    """Jetbot + Franka + キューブのシナリオをオフセット付きでカプセル化する。"""

    def __init__(self, name: str, offset: np.ndarray = np.array([0.0, 0.0, 0.0]), randomize: bool = False):
        self.name = name
        self.offset = offset
        self.state = 0
        self.step_counter = 0
        self.randomize = randomize
        self.pick_phase = 0
        self.jetbot = None
        self.franka = None
        self.cube = None
        self.cube_goal = np.array([1.2, 0.0, 0.0]) + offset

        # 有効ならキューブの目標位置をランダム化する
        if self.randomize:
            random_x = np.random.uniform(1.0, 1.6)
            self.cube_goal = np.array([random_x, 0.0, 0.0]) + offset
        else:
            self.cube_goal = np.array([1.2, 0.0, 0.0]) + offset

    def setup_scene(self):
        """このシナリオのロボットとキューブを作成する。"""
        assets_root_path = get_assets_root_path()
        base_path = f"/World/{self.name}"

        # Jetbot を追加
        stage_utils.add_reference_to_stage(
            usd_path=assets_root_path + "/Isaac/Robots/NVIDIA/Jetbot/jetbot.usd",
            path=f"{base_path}/Jetbot",
        )
        jetbot_xform = XformPrim(f"{base_path}/Jetbot")
        jetbot_xform.reset_xform_op_properties()
        jetbot_xform.set_world_poses(positions=self.offset.tolist())

        # Jetbot の前方にキューブを追加
        cube_pos = self.offset + np.array([0.15, 0.0, 0.025])
        cube_shape = Cube(
            paths=f"{base_path}/Cube",
            positions=cube_pos.tolist(),
            sizes=1.0,
            scales=[0.05, 0.05, 0.05],
            colors="red",
        )
        GeomPrim(paths=cube_shape.paths, apply_collision_apis=True)
        RigidPrim(paths=cube_shape.paths)

        # Franka を追加
        franka_pos = self.offset + np.array([0.8, -0.3, 0.0])
        self.franka = Franka(robot_path=f"{base_path}/Franka", create_robot=True)
        franka_xform = XformPrim(f"{base_path}/Franka")
        franka_xform.reset_xform_op_properties()
        franka_xform.set_world_poses(positions=franka_pos.tolist())

    def initialize(self):
        """シーンロード後にアーティキュレーションハンドルを初期化する。"""
        base_path = f"/World/{self.name}"
        self.jetbot = Articulation(f"{base_path}/Jetbot")
        self.cube = RigidPrim(f"{base_path}/Cube")

    def reset(self):
        """シナリオの状態をリセットする。"""
        self.state = 0
        self.step_counter = 0
        self.pick_phase = 0
        self.franka.reset_to_default_pose()

    def step(self):
        """シナリオのロジックを1ステップ実行する。"""
        if self.state == 0:
            # Jetbot がキューブを押す
            cube_pos = self.cube.get_world_poses()[0].numpy()[0]
            if np.linalg.norm(cube_pos[:2] - self.cube_goal[:2]) > 0.05:
                self.jetbot.set_dof_velocity_targets([10.0, 10.0])
            else:
                self.jetbot.set_dof_velocity_targets([0.0, 0.0])
                self.state = 1
                self.step_counter = 0

        elif self.state == 1:
            # Jetbot が後退する
            self.jetbot.set_dof_velocity_targets([-8.0, -8.0])
            self.step_counter += 1
            if self.step_counter > 100:
                self.jetbot.set_dof_velocity_targets([0.0, 0.0])
                self.state = 2
                self.step_counter = 0
                self.franka.open_gripper()

        elif self.state == 2:
            # Franka のピック＆プレース
            self._franka_pick_place()

    def _franka_pick_place(self):
        """Franka のピック＆プレースのステートマシンを実行する。"""
        cube_pos = self.cube.get_world_poses()[0].numpy()[0]
        down_orient = self.franka.get_downward_orientation()
        self.step_counter += 1

        if self.pick_phase == 0:
            self.franka.set_end_effector_pose(np.array([cube_pos[0], cube_pos[1], cube_pos[2] + 0.2]), down_orient)
            if self.step_counter > 120:
                self.pick_phase = 1
                self.step_counter = 0
        elif self.pick_phase == 1:
            self.franka.set_end_effector_pose(np.array([cube_pos[0], cube_pos[1], cube_pos[2] + 0.1]), down_orient)
            if self.step_counter > 100:
                self.pick_phase = 2
                self.step_counter = 0
        elif self.pick_phase == 2:
            self.franka.close_gripper()
            if self.step_counter > 100:
                self.pick_phase = 3
                self.step_counter = 0
        elif self.pick_phase == 3:
            _, current_position, _ = self.franka.get_current_state()
            target = current_position + np.array([0.1, 0.0, 0.08])
            self.franka.set_end_effector_pose(position=target, orientation=down_orient)
            if self.step_counter > 150:
                self.step_counter = 0
                self.pick_phase = 4
        elif self.pick_phase == 4:
            _, current_position, _ = self.franka.get_current_state()
            target = current_position + np.array([0.1, 0.0, 0.01])
            self.franka.set_end_effector_pose(position=target, orientation=down_orient)
            if self.step_counter > 150:
                self.step_counter = 0
                self.pick_phase = 5
        elif self.pick_phase == 5:
            self.franka.open_gripper()
            if self.step_counter > 150:
                self.step_counter = 0
                self.state = 6  # 完了


class HelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        self._physics_callback_id = None
        self._scenarios = []
        # -- シナリオ数の設定ここから -- #
        self._num_scenarios = 3  # 並列実行するシナリオ数
        # -- シナリオ数の設定ここまで -- #

    def setup_scene(self):
        GroundPlane("/World/ground_plane")
        dome_light = DomeLight("/World/DomeLight")
        dome_light.set_intensities(1000)

        # -- シナリオ作成ここから -- #
        # Y 軸方向にオフセットして複数のシナリオを作成
        for i in range(self._num_scenarios):
            offset = np.array([0.0, (i - 1) * 2.0, 0.0])  # Y 軸方向に等間隔で配置
            scenario = RobotScenario(name=f"scenario_{i}", offset=offset, randomize=False)
            scenario.setup_scene()
            self._scenarios.append(scenario)
        # -- シナリオ作成ここまで -- #

    async def setup_post_load(self):
        # -- シナリオ初期化ここから -- #
        # すべてのシナリオを初期化
        for scenario in self._scenarios:
            scenario.initialize()
        # -- シナリオ初期化ここまで -- #

        self._physics_callback_id = SimulationManager.register_callback(
            self.physics_step, event=SimulationEvent.PHYSICS_POST_STEP
        )

    def physics_step(self, dt, context):
        # -- シナリオのステップ実行ここから -- #
        # すべてのシナリオをステップ実行
        for scenario in self._scenarios:
            scenario.step()
        # -- シナリオのステップ実行ここまで -- #

    async def setup_post_reset(self):
        # -- シナリオのリセットここから -- #
        # すべてのシナリオをリセット
        for scenario in self._scenarios:
            scenario.reset()
        # -- シナリオのリセットここまで -- #

    def physics_cleanup(self):
        if self._physics_callback_id is not None:
            SimulationManager.deregister_callback(self._physics_callback_id)
            self._physics_callback_id = None
        # -- 全シナリオの削除ここから -- #
        self._scenarios = []
        # -- 全シナリオの削除ここまで -- #
```

コードを保存してシミュレーションを確認します：

1. **Ctrl+S** を押して保存し、**File > New From Stage Template > Empty** → **LOAD** を実行します。
2. 3組の Jetbot + Franka が並んで同時に動作する様子を確認します。

![複数シナリオの並列実行](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/core_api_tutorials_6_2.webp)

## ランダム化の追加

シミュレーションをより変化に富んだものにするため、シナリオのパラメータに**ランダム化**を追加できます。`RobotScenario` はコンストラクタの `randomize` パラメータが有効な場合、キューブの目標位置をランダムにサンプリングします。`setup_scene` でシナリオを作成する際に `randomize=True` を指定してください：

```python linenums="1"
for i in range(self._num_scenarios):
    offset = np.array([0.0, (i - 1) * 2.0, 0.0])  # Y 軸方向に等間隔で配置
    scenario = RobotScenario(name=f"scenario_{i}", offset=offset, randomize=True)
    scenario.setup_scene()
    self._scenarios.append(scenario)
```

これにより、各シナリオの Jetbot がキューブを押す距離が変わり、シナリオごとに異なる進行を確認できます。

## スケーリングのベストプラクティス

大規模なマルチロボットシミュレーションを作成する際は、以下の点に注意してください：

- **一意のパスを使う**: 各シナリオはプリムパスの衝突を避けるため、一意の USD プリムパスを使用します。`RobotScenario` クラスはシナリオ名から `/World/scenario_0/Jetbot` のような一意のパスを作成しています。
- **状態を独立に管理する**: 各シナリオインスタンスが自身のステート変数を保持することで、シナリオごとに独立して進行できます。
- **適切にクリーンアップする**: `physics_cleanup` メソッドで、シミュレーション停止時にコールバックの解除とシナリオリストのクリアを確実に行います。
- **パフォーマンスを考慮する**: シナリオ数が多い場合は、物理ステップの頻度を下げる、または GPU アクセラレーションによるシミュレーションを使うことでパフォーマンスを改善できます。

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. ロボットシナリオの**再利用可能な Python クラスへの整理**
2. `offset` パラメータによる複数シナリオの**空間配置**
3. ループによる**複数シナリオの並列実行**
4. シナリオパラメータへの**ランダム化**の追加
5. 複数ロボットインスタンス管理の**ベストプラクティス**

## 次のステップ

次のチュートリアル「[属性の追加](07_adding_props.md)」に進み、GUI 操作でオブジェクトに物理属性を設定する方法を学びましょう。

!!! note "注釈"
    以降のチュートリアルでも主に Extension Workflow を使用して開発を進めます。Standalone Workflow への変換方法は [Hello World](01_hello_world.md) で学んだ手順と同様です。
