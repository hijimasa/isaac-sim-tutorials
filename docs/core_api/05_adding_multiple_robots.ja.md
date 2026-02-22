---
title: 複数ロボットの追加
---

# 複数ロボットの追加

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます:

- 異なる種類のロボットを同じシミュレーションに追加する方法
- サブタスクを活用してタスクを構成する方法
- タスクイベントを使ってロボット間の動作を切り替えるプログラムロジックの構築方法
- 複数のロボットが連携して動作するシミュレーションの実装

## はじめに

### 前提条件

- [チュートリアル 4: マニピュレータロボットの追加](04_adding_a_manipulator_robot.md) を完了していること

### 所要時間

約 15〜20 分

### ソースコードの準備

このチュートリアルでは、引き続き Hello World サンプルの `hello_world.py` を編集していきます。前回のチュートリアルから続けて作業している場合はそのまま進めてください。別の日に作業を再開する場合は、以下の手順でソースコードを開いてください。

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

コードを4段階に分けて段階的に実装していきます。

## ステップ 1: シーンの作成

まず、これまでのチュートリアルで使った Jetbot と Franka の両方をシーンに配置します。前回のチュートリアルで学んだ `PickPlace` タスクを**サブタスク**として再利用することで、Franka とキューブのセットアップを簡潔に記述できます。

```python linenums="1" hl_lines="2-5 9-13 21-22 27-37 39-42"
from isaacsim.examples.interactive.base_sample import BaseSample
from isaacsim.robot.manipulators.examples.franka.tasks import PickPlace
from isaacsim.robot.wheeled_robots.robots import WheeledRobot
from isaacsim.core.utils.nucleus import get_assets_root_path
from isaacsim.core.api.tasks import BaseTask
import numpy as np


class RobotsPlaying(BaseTask):
    def __init__(self, name):
        super().__init__(name=name, offset=None)
        self._jetbot_goal_position = np.array([1.3, 0.3, 0])
        # PickPlace タスクをサブタスクとして再利用する
        # キューブの初期位置と目標位置をカスタマイズ
        self._pick_place_task = PickPlace(
            cube_initial_position=np.array([0.1, 0.3, 0.05]),
            target_position=np.array([0.7, -0.3, 0.0515 / 2.0]),
        )
        return

    def set_up_scene(self, scene):
        super().set_up_scene(scene)
        # サブタスク（今回はPickPlace）の set_up_scene を呼び出し、Franka とキューブを配置
        self._pick_place_task.set_up_scene(scene)
        # Jetbot を追加
        assets_root_path = get_assets_root_path()
        jetbot_asset_path = assets_root_path + "/Isaac/Robots/NVIDIA/Jetbot/jetbot.usd"
        self._jetbot = scene.add(
            WheeledRobot(
                prim_path="/World/Fancy_Jetbot",
                name="fancy_jetbot",
                wheel_dof_names=["left_wheel_joint", "right_wheel_joint"],
                create_robot=True,
                usd_path=jetbot_asset_path,
                position=np.array([0, 0.3, 0]),
            )
        )
        # サブタスクのパラメータから Franka を取得し、位置を変更
        pick_place_params = self._pick_place_task.get_params()
        self._franka = scene.get_object(pick_place_params["robot_name"]["value"])
        self._franka.set_world_pose(position=np.array([1.0, 0, 0]))
        self._franka.set_default_state(position=np.array([1.0, 0, 0]))
        return

    def get_observations(self):
        current_jetbot_position, current_jetbot_orientation = self._jetbot.get_world_pose()
        observations = {
            self._jetbot.name: {
                "position": current_jetbot_position,
                "orientation": current_jetbot_orientation,
                "goal_position": self._jetbot_goal_position,
            }
        }
        return observations

    def get_params(self):
        # ハードコーディングを避けるため、パラメータを動的に取得
        pick_place_params = self._pick_place_task.get_params()
        params_representation = pick_place_params
        params_representation["jetbot_name"] = {"value": self._jetbot.name, "modifiable": False}
        params_representation["franka_name"] = pick_place_params["robot_name"]
        return params_representation

    def post_reset(self):
        self._franka.gripper.set_joint_positions(self._franka.gripper.joint_opened_positions)
        return


class HelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        return

    def setup_scene(self):
        world = self.get_world()
        world.add_task(RobotsPlaying(name="awesome_task"))
        return
```

!!! info "サブタスクのパターン"
    `RobotsPlaying` タスクは、内部で `PickPlace` タスクの `set_up_scene` を呼び出しています。このように既存タスクをサブタスクとして組み込むことで、同じ処理を再実装する必要がなくなります。

!!! note "`set_world_pose` と `set_default_state` の違い"
    Franka の位置変更に2つのメソッドを使っている理由は、それぞれの役割が異なるためです。

    | メソッド | 役割 |
    |---|---|
    | `set_world_pose()` | **現在のフレーム**でのロボットの位置を即座に変更する |
    | `set_default_state()` | **リセット時に復帰する位置**を登録する |

    `set_default_state()` を省略すると、RESET ボタンを押したときに Franka が PickPlace タスク内部で設定された元の位置（原点付近）に戻ってしまい、Jetbot と重なる問題が発生します。

コードを保存してシミュレーションを確認します：

1. **Ctrl+S** を押して保存し、**File > New From Stage Template > Empty** → **LOAD** を実行します。
2. Jetbot と Franka の両方がシーンに表示されることを確認します。

## ステップ 2: Jetbot を動かす

次に、Jetbot にコントローラを追加して、キューブを Franka の方向に押して運ぶ動作を実装します。チュートリアル 3 で使用した `WheelBasePoseController` を再利用します。

```python linenums="1" hl_lines="6-7 79-89 95-96 98-104"
from isaacsim.examples.interactive.base_sample import BaseSample
from isaacsim.robot.manipulators.examples.franka.tasks import PickPlace
from isaacsim.robot.wheeled_robots.robots import WheeledRobot
from isaacsim.core.utils.nucleus import get_assets_root_path
from isaacsim.core.api.tasks import BaseTask
from isaacsim.robot.wheeled_robots.controllers.wheel_base_pose_controller import WheelBasePoseController
from isaacsim.robot.wheeled_robots.controllers.differential_controller import DifferentialController
import numpy as np


class RobotsPlaying(BaseTask):
    def __init__(self, name):
        super().__init__(name=name, offset=None)
        self._jetbot_goal_position = np.array([1.3, 0.3, 0])
        self._pick_place_task = PickPlace(
            cube_initial_position=np.array([0.1, 0.3, 0.05]),
            target_position=np.array([0.7, -0.3, 0.0515 / 2.0]),
        )
        return

    def set_up_scene(self, scene):
        super().set_up_scene(scene)
        self._pick_place_task.set_up_scene(scene)
        assets_root_path = get_assets_root_path()
        jetbot_asset_path = assets_root_path + "/Isaac/Robots/NVIDIA/Jetbot/jetbot.usd"
        self._jetbot = scene.add(
            WheeledRobot(
                prim_path="/World/Fancy_Jetbot",
                name="fancy_jetbot",
                wheel_dof_names=["left_wheel_joint", "right_wheel_joint"],
                create_robot=True,
                usd_path=jetbot_asset_path,
                position=np.array([0, 0.3, 0]),
            )
        )
        pick_place_params = self._pick_place_task.get_params()
        self._franka = scene.get_object(pick_place_params["robot_name"]["value"])
        self._franka.set_world_pose(position=np.array([1.0, 0, 0]))
        self._franka.set_default_state(position=np.array([1.0, 0, 0]))
        return

    def get_observations(self):
        current_jetbot_position, current_jetbot_orientation = self._jetbot.get_world_pose()
        observations = {
            self._jetbot.name: {
                "position": current_jetbot_position,
                "orientation": current_jetbot_orientation,
                "goal_position": self._jetbot_goal_position,
            }
        }
        return observations

    def get_params(self):
        pick_place_params = self._pick_place_task.get_params()
        params_representation = pick_place_params
        params_representation["jetbot_name"] = {"value": self._jetbot.name, "modifiable": False}
        params_representation["franka_name"] = pick_place_params["robot_name"]
        return params_representation

    def post_reset(self):
        self._franka.gripper.set_joint_positions(self._franka.gripper.joint_opened_positions)
        return


class HelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        return

    def setup_scene(self):
        world = self.get_world()
        world.add_task(RobotsPlaying(name="awesome_task"))
        return

    async def setup_post_load(self):
        self._world = self.get_world()
        task_params = self._world.get_task("awesome_task").get_params()
        self._jetbot = self._world.scene.get_object(task_params["jetbot_name"]["value"])
        self._cube_name = task_params["cube_name"]["value"]
        # Jetbot 用のコントローラを初期化
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
        self._jetbot_controller.reset()
        await self._world.play_async()
        return

    def physics_step(self, step_size):
        current_observations = self._world.get_observations()
        # Jetbot を目標位置に向かって移動させる
        self._jetbot.apply_wheel_actions(
            self._jetbot_controller.forward(
                start_position=current_observations[self._jetbot.name]["position"],
                start_orientation=current_observations[self._jetbot.name]["orientation"],
                goal_position=current_observations[self._jetbot.name]["goal_position"],
            )
        )
        return
```

コードを保存して **PLAY** を押すと、Jetbot がキューブを押しながら Franka の方向に移動します。

## ステップ 3: タスクイベントの追加

現状では Jetbot がキューブを届けた後も動き続けてしまいます。タスクイベント（`_task_event`）を導入して、以下の3つのフェーズを切り替えるロジックを追加します：

| イベント | 動作 |
|---|---|
| `0` | Jetbot がキューブを Franka の近くまで押す |
| `1` | Jetbot が後退して Franka に作業スペースを譲る |
| `2` | Jetbot が停止する（Franka の作業準備完了） |

```python linenums="1" hl_lines="8 16 51-52 65-73 76 80-81 103-115"
from isaacsim.examples.interactive.base_sample import BaseSample
from isaacsim.robot.manipulators.examples.franka.tasks import PickPlace
from isaacsim.robot.wheeled_robots.robots import WheeledRobot
from isaacsim.core.utils.nucleus import get_assets_root_path
from isaacsim.core.api.tasks import BaseTask
from isaacsim.robot.wheeled_robots.controllers.wheel_base_pose_controller import WheelBasePoseController
from isaacsim.robot.wheeled_robots.controllers.differential_controller import DifferentialController
from isaacsim.core.utils.types import ArticulationAction
import numpy as np


class RobotsPlaying(BaseTask):
    def __init__(self, name):
        super().__init__(name=name, offset=None)
        self._jetbot_goal_position = np.array([1.3, 0.3, 0])
        self._task_event = 0  # タスクイベント: どのフェーズにいるかを管理
        self._pick_place_task = PickPlace(
            cube_initial_position=np.array([0.1, 0.3, 0.05]),
            target_position=np.array([0.7, -0.3, 0.0515 / 2.0]),
        )
        return

    def set_up_scene(self, scene):
        super().set_up_scene(scene)
        self._pick_place_task.set_up_scene(scene)
        assets_root_path = get_assets_root_path()
        jetbot_asset_path = assets_root_path + "/Isaac/Robots/NVIDIA/Jetbot/jetbot.usd"
        self._jetbot = scene.add(
            WheeledRobot(
                prim_path="/World/Fancy_Jetbot",
                name="fancy_jetbot",
                wheel_dof_names=["left_wheel_joint", "right_wheel_joint"],
                create_robot=True,
                usd_path=jetbot_asset_path,
                position=np.array([0, 0.3, 0]),
            )
        )
        pick_place_params = self._pick_place_task.get_params()
        self._franka = scene.get_object(pick_place_params["robot_name"]["value"])
        self._franka.set_world_pose(position=np.array([1.0, 0, 0]))
        self._franka.set_default_state(position=np.array([1.0, 0, 0]))
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
        return observations

    def get_params(self):
        pick_place_params = self._pick_place_task.get_params()
        params_representation = pick_place_params
        params_representation["jetbot_name"] = {"value": self._jetbot.name, "modifiable": False}
        params_representation["franka_name"] = pick_place_params["robot_name"]
        return params_representation

    def pre_step(self, control_index, simulation_time):
        if self._task_event == 0:
            # Jetbot が目標位置に到達したかチェック
            current_jetbot_position, _ = self._jetbot.get_world_pose()
            if np.mean(np.abs(current_jetbot_position[:2] - self._jetbot_goal_position[:2])) < 0.04:
                self._task_event += 1
                self._cube_arrive_step_index = control_index
        elif self._task_event == 1:
            # Jetbot が 200 ステップ後退したら次のフェーズへ
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
        world.add_task(RobotsPlaying(name="awesome_task"))
        return

    async def setup_post_load(self):
        self._world = self.get_world()
        task_params = self._world.get_task("awesome_task").get_params()
        self._jetbot = self._world.scene.get_object(task_params["jetbot_name"]["value"])
        self._cube_name = task_params["cube_name"]["value"]
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
        self._jetbot_controller.reset()
        await self._world.play_async()
        return

    def physics_step(self, step_size):
        current_observations = self._world.get_observations()
        if current_observations["task_event"] == 0:
            # フェーズ 0: Jetbot がキューブを押して運ぶ
            self._jetbot.apply_wheel_actions(
                self._jetbot_controller.forward(
                    start_position=current_observations[self._jetbot.name]["position"],
                    start_orientation=current_observations[self._jetbot.name]["orientation"],
                    goal_position=current_observations[self._jetbot.name]["goal_position"],
                )
            )
        elif current_observations["task_event"] == 1:
            # フェーズ 1: Jetbot が後退する
            self._jetbot.apply_wheel_actions(ArticulationAction(joint_velocities=[-8, -8]))
        elif current_observations["task_event"] == 2:
            # フェーズ 2: Jetbot を停止する
            # 注意: 目標速度は変更しない限り維持されるため、明示的にゼロを設定する
            self._jetbot.apply_wheel_actions(ArticulationAction(joint_velocities=[0.0, 0.0]))
        return
```

コードを保存して **PLAY** を押すと、Jetbot がキューブを運んだ後、後退して停止する様子を確認できます。

## ステップ 4: Franka によるピック＆プレース

最後に、Franka のコントローラを追加して、Jetbot が退いた後に Franka がキューブを拾い上げて目標位置に配置する動作を実装します。

```python linenums="1" hl_lines="8 55-56 88-92 99-100 115-121 123-124"
from isaacsim.examples.interactive.base_sample import BaseSample
from isaacsim.robot.manipulators.examples.franka.tasks import PickPlace
from isaacsim.robot.wheeled_robots.robots import WheeledRobot
from isaacsim.core.utils.nucleus import get_assets_root_path
from isaacsim.core.api.tasks import BaseTask
from isaacsim.robot.wheeled_robots.controllers.wheel_base_pose_controller import WheelBasePoseController
from isaacsim.robot.wheeled_robots.controllers.differential_controller import DifferentialController
from isaacsim.robot.manipulators.examples.franka.controllers import PickPlaceController
from isaacsim.core.utils.types import ArticulationAction
import numpy as np


class RobotsPlaying(BaseTask):
    def __init__(self, name):
        super().__init__(name=name, offset=None)
        self._jetbot_goal_position = np.array([1.3, 0.3, 0])
        self._task_event = 0
        self._pick_place_task = PickPlace(
            cube_initial_position=np.array([0.1, 0.3, 0.05]),
            target_position=np.array([0.7, -0.3, 0.0515 / 2.0]),
        )
        return

    def set_up_scene(self, scene):
        super().set_up_scene(scene)
        self._pick_place_task.set_up_scene(scene)
        assets_root_path = get_assets_root_path()
        jetbot_asset_path = assets_root_path + "/Isaac/Robots/NVIDIA/Jetbot/jetbot.usd"
        self._jetbot = scene.add(
            WheeledRobot(
                prim_path="/World/Fancy_Jetbot",
                name="fancy_jetbot",
                wheel_dof_names=["left_wheel_joint", "right_wheel_joint"],
                create_robot=True,
                usd_path=jetbot_asset_path,
                position=np.array([0, 0.3, 0]),
            )
        )
        pick_place_params = self._pick_place_task.get_params()
        self._franka = scene.get_object(pick_place_params["robot_name"]["value"])
        self._franka.set_world_pose(position=np.array([1.0, 0, 0]))
        self._franka.set_default_state(position=np.array([1.0, 0, 0]))
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
        # サブタスクの観測情報も統合する
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
        world.add_task(RobotsPlaying(name="awesome_task"))
        return

    async def setup_post_load(self):
        self._world = self.get_world()
        task_params = self._world.get_task("awesome_task").get_params()
        self._franka = self._world.scene.get_object(task_params["franka_name"]["value"])
        self._jetbot = self._world.scene.get_object(task_params["jetbot_name"]["value"])
        self._cube_name = task_params["cube_name"]["value"]
        # Franka 用のコントローラを追加
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
            self._jetbot.apply_wheel_actions(ArticulationAction(joint_velocities=[-8, -8]))
        elif current_observations["task_event"] == 2:
            self._jetbot.apply_wheel_actions(ArticulationAction(joint_velocities=[0.0, 0.0]))
            # Franka がキューブを拾い上げて配置する
            actions = self._franka_controller.forward(
                picking_position=current_observations[self._cube_name]["position"],
                placing_position=current_observations[self._cube_name]["target_position"],
                current_joint_positions=current_observations[self._franka.name]["joint_positions"],
            )
            self._franka.apply_action(actions)
        # Franka のピック＆プレースが完了したらシミュレーションを一時停止
        if self._franka_controller.is_done():
            self._world.pause()
        return
```

!!! note "`pre_step` の `control_index` の活用"
    `pre_step(control_index, simulation_time)` の `control_index` は物理ステップごとに自動インクリメントされるインデックスです（[チュートリアル 4](04_adding_a_manipulator_robot.md) 参照）。このコードでは、Jetbot が目標に到達した時点の `control_index` を `_cube_arrive_step_index` に記録し、そこから 200 ステップ経過したかどうかで後退フェーズの終了を判定しています。

コードを保存してシミュレーションを確認します：

1. **Ctrl+S** を押して保存し、**File > New From Stage Template > Empty** → **LOAD** を実行します。
2. **PLAY** ボタンを押して、以下の一連の動作を確認します：
    - Jetbot がキューブを Franka の近くまで押して運ぶ
    - Jetbot が後退して退避する
    - Franka がキューブを拾い上げて目標位置に配置する
    - 動作完了後にシミュレーションが一時停止する

![複数ロボットの連携動作](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/core_api_tutorials_6_2.webp)

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. **Jetbot** と **Franka** の2種類のロボットを同じシーンに配置
2. 既存の `PickPlace` タスクを**サブタスク**として再利用するパターン
3. **タスクイベント**を使ったフェーズ管理によるロボット間の動作切り替え
4. `observations.update()` によるサブタスクの観測情報の統合

## 次のステップ

次のチュートリアル「[複数タスクの実行](06_multiple_tasks.md)」に進み、同じタスクの複数インスタンスを空間的に配置して並列実行する方法を学びましょう。

!!! note "注釈"
    以降のチュートリアルでも主に Extension Workflow を使用して開発を進めます。Standalone Workflow への変換方法は [Hello World](01_hello_world.md#_11) で学んだ手順と同様です。
