---
title: 複数タスクの実行
---

# 複数タスクの実行

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます:

- `offset` パラメータを使ってタスクのアセットを空間的に配置する方法
- `find_unique_string_name()` でプリムパスやオブジェクト名の衝突を回避する方法
- `_task_objects` と `_move_task_objects_to_their_frame()` を使ったオフセット管理
- 同じタスクを複数インスタンス化して並列実行する方法

## はじめに

### 前提条件

- [チュートリアル 5: 複数ロボットの追加](05_adding_multiple_robots.md) を完了していること

### 所要時間

約 15〜20 分

### ソースコードの準備

このチュートリアルでは、引き続き Hello World サンプルの `hello_world.py` を編集していきます。前回のチュートリアルから続けて作業している場合はそのまま進めてください。別の日に作業を再開する場合は、以下の手順でソースコードを開いてください。

1. **Windows > Examples > Robotics Examples** をアクティブにして、Robotics Examples タブを開きます。
2. **Robotics Examples > General > Hello World** をクリックします。
3. **Open Source Code** ボタンをクリックし、Visual Studio Code で `hello_world.py` を開きます。

詳しい手順は [Hello World の「サンプルを開く」セクション](01_hello_world.md)を参照してください。

!!! warning "注意"
    **STOP** → **PLAY** の操作ではワールドが正しくリセットされない場合があります。シミュレーションをやり直す場合は、**RESET** ボタンを使用してください。

## タスクのパラメータ化

前回のチュートリアルでは `RobotsPlaying` タスクを1つだけ使いましたが、同じタスクを複数配置するには、各タスクのアセットが重ならないように**位置をオフセット**する必要があります。

`BaseTask` は `offset` パラメータをサポートしており、タスク内のすべてのアセットを指定した分だけ平行移動できます。ここでは以下のポイントが重要です：

| 機能 | 説明 |
|---|---|
| `offset` パラメータ | タスクのコンストラクタに渡し、`self._offset` として利用可能 |
| `find_unique_string_name()` | 名前やパスの衝突を避けるためにユニークな名前を生成 |
| `self._task_objects` | タスクが管理するオブジェクトを登録する辞書 |
| `_move_task_objects_to_their_frame()` | 登録されたオブジェクトにオフセットを適用 |

```python linenums="1" hl_lines="10-12 14 25-26 30-34 47-52 54 101"
from isaacsim.examples.interactive.base_sample import BaseSample
from isaacsim.robot.manipulators.examples.franka.tasks import PickPlace
from isaacsim.robot.manipulators.examples.franka.controllers import PickPlaceController
from isaacsim.robot.wheeled_robots.robots import WheeledRobot
from isaacsim.core.utils.nucleus import get_assets_root_path
from isaacsim.robot.wheeled_robots.controllers.wheel_base_pose_controller import WheelBasePoseController
from isaacsim.robot.wheeled_robots.controllers.differential_controller import DifferentialController
from isaacsim.core.api.tasks import BaseTask
from isaacsim.core.utils.types import ArticulationAction
from isaacsim.core.utils.string import find_unique_string_name  # ユニーク名生成
from isaacsim.core.utils.prims import is_prim_path_valid         # プリムパスの存在チェック
from isaacsim.core.api.objects.cuboid import VisualCuboid
import numpy as np


class RobotsPlaying(BaseTask):
    def __init__(self, name, offset=None):
        super().__init__(name=name, offset=offset)
        self._task_event = 0
        # offset を加算して、タスクごとに異なる目標位置を設定
        self._jetbot_goal_position = np.array([1.3, 0.3, 0]) + self._offset
        self._pick_place_task = PickPlace(
            cube_initial_position=np.array([0.1, 0.3, 0.05]),
            target_position=np.array([0.7, -0.3, 0.0515 / 2.0]),
            offset=offset,  # サブタスクにも同じオフセットを伝播
        )
        return

    def set_up_scene(self, scene):
        super().set_up_scene(scene)
        self._pick_place_task.set_up_scene(scene)
        # ユニークな名前を生成して、複数インスタンスでの名前衝突を回避
        jetbot_name = find_unique_string_name(
            initial_name="fancy_jetbot", is_unique_fn=lambda x: not self.scene.object_exists(x)
        )
        jetbot_prim_path = find_unique_string_name(
            initial_name="/World/Fancy_Jetbot", is_unique_fn=lambda x: not is_prim_path_valid(x)
        )
        assets_root_path = get_assets_root_path()
        jetbot_asset_path = assets_root_path + "/Isaac/Robots/NVIDIA/Jetbot/jetbot.usd"
        self._jetbot = scene.add(
            WheeledRobot(
                prim_path=jetbot_prim_path,
                name=jetbot_name,
                wheel_dof_names=["left_wheel_joint", "right_wheel_joint"],
                create_robot=True,
                usd_path=jetbot_asset_path,
                position=np.array([0, 0.3, 0]),
            )
        )
        # ── (A) Jetbot を _task_objects に登録（後でオフセットを適用するため）──
        self._task_objects[self._jetbot.name] = self._jetbot

        # ── (B) サブタスクが作成した Franka の位置を追加調整 ──
        # PickPlace サブタスクが Franka を配置済みだが、Jetbot と離すために X+1.0 ずらす
        pick_place_params = self._pick_place_task.get_params()
        self._franka = scene.get_object(pick_place_params["robot_name"]["value"])
        current_position, _ = self._franka.get_world_pose()
        self._franka.set_world_pose(position=current_position + np.array([1.0, 0, 0]))
        self._franka.set_default_state(position=current_position + np.array([1.0, 0, 0]))

        # ── (C) _task_objects に登録されたオブジェクトにオフセットを一括適用 ──
        self._move_task_objects_to_their_frame()
        return

    def get_observations(self):
        current_jetbot_position, current_jetbot_orientation = self._jetbot.get_world_pose()
        observations = {
            "task_event": self._task_event,
            self._jetbot.name: {
                "position": current_jetbot_position,
                "orientation": current_jetbot_orientation,
                "goal_position": self._jetbot_goal_position,
            }
        }
        observations.update(self._pick_place_task.get_observations())
        return observations

    def get_params(self):
        pick_place_params = self._pick_place_task.get_params()
        params_representation = pick_place_params
        params_representation["jetbot_name"] = {"value": self._jetbot.name, "modifiable": False}
        params_representation["franka_name"] = pick_place_params["robot_name"]
        return params_representation

    def pre_step(self, control_index, simulation_time):
        if self._task_event == 0:
            current_jetbot_position, _ = self._jetbot.get_world_pose()
            if np.mean(np.abs(current_jetbot_position[:2] - self._jetbot_goal_position[:2])) < 0.04:
                self._task_event += 1
                self._cube_arrive_step_index = control_index
        elif self._task_event == 1:
            if control_index - self._cube_arrive_step_index == 200:
                self._task_event += 1
        return

    def post_reset(self):
        self._franka.gripper.set_joint_positions(self._franka.gripper.joint_opened_positions)
        self._task_event = 0
        return


class HelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        return

    def setup_scene(self):
        world = self.get_world()
        # offset を指定してタスクを配置
        world.add_task(RobotsPlaying(name="awesome_task", offset=np.array([0, -1.0, 0])))
        # 原点付近に目印のキューブを配置（位置のずれを確認するため）
        VisualCuboid(
            prim_path="/new_cube_1",
            name="visual_cube",
            position=np.array([1.0, 0, 0.05]),
            scale=np.array([0.1, 0.1, 0.1]),
        )
        return

    async def setup_post_load(self):
        self._world = self.get_world()
        task_params = self._world.get_task("awesome_task").get_params()
        self._franka = self._world.scene.get_object(task_params["franka_name"]["value"])
        self._jetbot = self._world.scene.get_object(task_params["jetbot_name"]["value"])
        self._cube_name = task_params["cube_name"]["value"]
        self._franka_controller = PickPlaceController(
            name="pick_place_controller",
            gripper=self._franka.gripper,
            robot_articulation=self._franka,
        )
        self._jetbot_controller = WheelBasePoseController(
            name="cool_controller",
            open_loop_wheel_controller=DifferentialController(
                name="simple_control",
                wheel_radius=0.03,
                wheel_base=0.1125,
            ),
        )
        self._world.add_physics_callback("sim_step", callback_fn=self.physics_step)
        await self._world.play_async()
        return

    async def setup_post_reset(self):
        self._franka_controller.reset()
        self._jetbot_controller.reset()
        await self._world.play_async()
        return

    def physics_step(self, step_size):
        current_observations = self._world.get_observations()
        if current_observations["task_event"] == 0:
            self._jetbot.apply_wheel_actions(
                self._jetbot_controller.forward(
                    start_position=current_observations[self._jetbot.name]["position"],
                    start_orientation=current_observations[self._jetbot.name]["orientation"],
                    goal_position=current_observations[self._jetbot.name]["goal_position"],
                )
            )
        elif current_observations["task_event"] == 1:
            self._jetbot.apply_wheel_actions(ArticulationAction(joint_velocities=[-8.0, -8.0]))
        elif current_observations["task_event"] == 2:
            self._jetbot.apply_wheel_actions(ArticulationAction(joint_velocities=[0.0, 0.0]))
            actions = self._franka_controller.forward(
                picking_position=current_observations[self._cube_name]["position"],
                placing_position=current_observations[self._cube_name]["target_position"],
                current_joint_positions=current_observations[self._franka.name]["joint_positions"],
            )
            self._franka.apply_action(actions)
        if self._franka_controller.is_done():
            self._world.pause()
        return
```

`set_up_scene` 内では、オフセットの適用対象が **2 種類** あることに注意してください：

| 対象 | オフセットの適用方法 | 説明 |
|---|---|---|
| サブタスク内のオブジェクト（Franka, キューブ） | `PickPlace` に `offset` を渡す **(コンストラクタで実行済み)** | サブタスク自身が `_task_objects` と `_move_task_objects_to_their_frame()` でオフセットを適用 |
| 自タスクのオブジェクト（Jetbot） | `_task_objects` に登録 → `_move_task_objects_to_their_frame()` **(A, C)** | 自分で追加したオブジェクトは自分で登録・適用する |

**(B)** の Franka の位置調整はオフセットとは別の処理で、Jetbot と Franka が重ならないよう X 方向に追加で 1.0 ずらしています。これはサブタスク側でオフセット適用済みの位置に対する追加の調整です。

コードを保存してシミュレーションを確認します：

1. **Ctrl+S** を押して保存し、**File > New From Stage Template > Empty** → **LOAD** を実行します。
2. **PLAY** を押すと、Y 軸方向に -1.0 オフセットされた位置でロボットが動作します。
3. 原点付近の白いキューブと比較して、タスクのアセットがオフセットされていることを確認できます。

## 複数タスクの並列実行

`offset` によるパラメータ化ができたので、同じタスクを複数インスタンス化して並列に実行します。ここでは3つの `RobotsPlaying` タスクを Y 軸方向に並べて配置します。

複数タスクを扱う際の重要なポイント：

- **タスクイベントのキー名を一意にする** — 複数タスクの観測情報が混ざらないよう、タスク名をプレフィックスとして付ける（`self.name + "_event"`）
- **コントローラをリストで管理する** — 各タスクに対応するコントローラをリストに格納
- **`world_cleanup()`** — ホットリロード時にリストを初期化する

```python linenums="1" hl_lines="14 21 64 97-105 108-111 113-128 134-138 141-162 164-170"
from isaacsim.examples.interactive.base_sample import BaseSample
from isaacsim.core.utils.nucleus import get_assets_root_path
from isaacsim.robot.manipulators.examples.franka.tasks import PickPlace
from isaacsim.robot.manipulators.examples.franka.controllers import PickPlaceController
from isaacsim.robot.wheeled_robots.robots import WheeledRobot
from isaacsim.robot.wheeled_robots.controllers.wheel_base_pose_controller import WheelBasePoseController
from isaacsim.robot.wheeled_robots.controllers.differential_controller import DifferentialController
from isaacsim.core.api.tasks import BaseTask
from isaacsim.core.utils.types import ArticulationAction
from isaacsim.core.utils.string import find_unique_string_name
from isaacsim.core.utils.prims import is_prim_path_valid
import numpy as np


class RobotsPlaying(BaseTask):
    def __init__(self, name, offset=None):
        super().__init__(name=name, offset=offset)
        self._task_event = 0
        self._jetbot_goal_position = np.array([np.random.uniform(1.2, 1.6), 0.3, 0]) + self._offset
        self._pick_place_task = PickPlace(
            cube_initial_position=np.array([0.1, 0.3, 0.05]),
            target_position=np.array([0.7, -0.3, 0.0515 / 2.0]),
            offset=offset,
        )
        return

    def set_up_scene(self, scene):
        super().set_up_scene(scene)
        self._pick_place_task.set_up_scene(scene)
        jetbot_name = find_unique_string_name(
            initial_name="fancy_jetbot", is_unique_fn=lambda x: not self.scene.object_exists(x)
        )
        jetbot_prim_path = find_unique_string_name(
            initial_name="/World/Fancy_Jetbot", is_unique_fn=lambda x: not is_prim_path_valid(x)
        )
        assets_root_path = get_assets_root_path()
        jetbot_asset_path = assets_root_path + "/Isaac/Robots/NVIDIA/Jetbot/jetbot.usd"
        self._jetbot = scene.add(
            WheeledRobot(
                prim_path=jetbot_prim_path,
                name=jetbot_name,
                wheel_dof_names=["left_wheel_joint", "right_wheel_joint"],
                create_robot=True,
                usd_path=jetbot_asset_path,
                position=np.array([0, 0.3, 0]),
            )
        )
        # (A) Jetbot を _task_objects に登録
        self._task_objects[self._jetbot.name] = self._jetbot
        # (B) サブタスクが作成した Franka を Jetbot と離すために X+1.0 追加調整
        pick_place_params = self._pick_place_task.get_params()
        self._franka = scene.get_object(pick_place_params["robot_name"]["value"])
        current_position, _ = self._franka.get_world_pose()
        self._franka.set_world_pose(position=current_position + np.array([1.0, 0, 0]))
        self._franka.set_default_state(position=current_position + np.array([1.0, 0, 0]))
        # (C) _task_objects に登録されたオブジェクトにオフセットを一括適用
        self._move_task_objects_to_their_frame()
        return

    def get_observations(self):
        current_jetbot_position, current_jetbot_orientation = self._jetbot.get_world_pose()
        observations = {
            # タスク名をプレフィックスにして、複数タスクでキーが衝突しないようにする
            self.name + "_event": self._task_event,
            self._jetbot.name: {
                "position": current_jetbot_position,
                "orientation": current_jetbot_orientation,
                "goal_position": self._jetbot_goal_position,
            }
        }
        observations.update(self._pick_place_task.get_observations())
        return observations

    def get_params(self):
        pick_place_params = self._pick_place_task.get_params()
        params_representation = pick_place_params
        params_representation["jetbot_name"] = {"value": self._jetbot.name, "modifiable": False}
        params_representation["franka_name"] = pick_place_params["robot_name"]
        return params_representation

    def pre_step(self, control_index, simulation_time):
        if self._task_event == 0:
            current_jetbot_position, _ = self._jetbot.get_world_pose()
            if np.mean(np.abs(current_jetbot_position[:2] - self._jetbot_goal_position[:2])) < 0.04:
                self._task_event += 1
                self._cube_arrive_step_index = control_index
        elif self._task_event == 1:
            if control_index - self._cube_arrive_step_index == 200:
                self._task_event += 1
        return

    def post_reset(self):
        self._franka.gripper.set_joint_positions(self._franka.gripper.joint_opened_positions)
        self._task_event = 0
        return


class HelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        # 各タスクのコントローラやオブジェクトをリストで管理
        self._tasks = []
        self._num_of_tasks = 3
        self._franka_controllers = []
        self._jetbot_controllers = []
        self._jetbots = []
        self._frankas = []
        self._cube_names = []
        return

    def setup_scene(self):
        world = self.get_world()
        # 3つのタスクを Y 軸方向にオフセットして配置
        for i in range(self._num_of_tasks):
            world.add_task(RobotsPlaying(name="my_awesome_task_" + str(i), offset=np.array([0, (i * 2) - 3, 0])))
        return

    async def setup_post_load(self):
        self._world = self.get_world()
        for i in range(self._num_of_tasks):
            self._tasks.append(self._world.get_task(name="my_awesome_task_" + str(i)))
            task_params = self._tasks[i].get_params()
            self._frankas.append(self._world.scene.get_object(task_params["franka_name"]["value"]))
            self._jetbots.append(self._world.scene.get_object(task_params["jetbot_name"]["value"]))
            self._cube_names.append(task_params["cube_name"]["value"])
            self._franka_controllers.append(
                PickPlaceController(
                    name="pick_place_controller",
                    gripper=self._frankas[i].gripper,
                    robot_articulation=self._frankas[i],
                    events_dt=[0.008, 0.002, 0.5, 0.1, 0.05, 0.05, 0.0025, 1, 0.008, 0.08],
                )
            )
            self._jetbot_controllers.append(
                WheelBasePoseController(
                    name="cool_controller",
                    open_loop_wheel_controller=DifferentialController(
                        name="simple_control",
                        wheel_radius=0.03,
                        wheel_base=0.1125,
                    ),
                )
            )
        self._world.add_physics_callback("sim_step", callback_fn=self.physics_step)
        await self._world.play_async()
        return

    async def setup_post_reset(self):
        for i in range(len(self._tasks)):
            self._franka_controllers[i].reset()
            self._jetbot_controllers[i].reset()
        await self._world.play_async()
        return

    def physics_step(self, step_size):
        current_observations = self._world.get_observations()
        # すべてのタスクをループで処理
        for i in range(len(self._tasks)):
            if current_observations[self._tasks[i].name + "_event"] == 0:
                self._jetbots[i].apply_wheel_actions(
                    self._jetbot_controllers[i].forward(
                        start_position=current_observations[self._jetbots[i].name]["position"],
                        start_orientation=current_observations[self._jetbots[i].name]["orientation"],
                        goal_position=current_observations[self._jetbots[i].name]["goal_position"],
                    )
                )
            elif current_observations[self._tasks[i].name + "_event"] == 1:
                self._jetbots[i].apply_wheel_actions(ArticulationAction(joint_velocities=[-8.0, -8.0]))
            elif current_observations[self._tasks[i].name + "_event"] == 2:
                self._jetbots[i].apply_wheel_actions(ArticulationAction(joint_velocities=[0.0, 0.0]))
                actions = self._franka_controllers[i].forward(
                    picking_position=current_observations[self._cube_names[i]]["position"],
                    placing_position=current_observations[self._cube_names[i]]["target_position"],
                    current_joint_positions=current_observations[self._frankas[i].name]["joint_positions"],
                )
                self._frankas[i].apply_action(actions)
        return

    def world_cleanup(self):
        # ホットリロード時にリストを初期化する
        self._tasks = []
        self._franka_controllers = []
        self._jetbot_controllers = []
        self._jetbots = []
        self._frankas = []
        self._cube_names = []
        return
```

!!! note "`events_dt` の明示的な指定"
    [チュートリアル 4](04_adding_a_manipulator_robot.md) で説明した通り、`events_dt` は `PickPlaceController` の各ステートの実行速度を制御するリストです。複数の Franka が同時に動作する場合、デフォルト値ではタイミングが合わず動作が不安定になることがあるため、ここでは明示的に値を指定して各ロボットの動作速度を揃えています。

コードを保存してシミュレーションを確認します：

1. **Ctrl+S** を押して保存し、**File > New From Stage Template > Empty** → **LOAD** を実行します。
2. **PLAY** ボタンを押して、3組の Jetbot + Franka が並んで同時に動作する様子を確認します。

![複数タスクの並列実行](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/core_api_tutorials_6_2.webp)

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. `offset` パラメータによるタスクの**空間配置**
2. `find_unique_string_name()` による**名前衝突の回避**
3. `_task_objects` と `_move_task_objects_to_their_frame()` による**オフセット管理**
4. リストを使ったコントローラとタスクの**並列管理**
5. `world_cleanup()` による**ホットリロード対応**

!!! tip "発展"
    異なる種類のタスクを組み合わせて実行する例は、Isaac Sim に付属のスタンドアロンサンプル `standalone_examples/api/isaacsim.robot.manipulators/universal_robots/multiple_tasks.py` を参照してください。

## 次のステップ

次のチュートリアル「[属性の追加](07_adding_props.md)」に進み、GUI 操作でオブジェクトに物理属性を設定する方法を学びましょう。

!!! note "注釈"
    以降のチュートリアルでも主に Extension Workflow を使用して開発を進めます。Standalone Workflow への変換方法は [Hello World](01_hello_world.md) で学んだ手順と同様です。
