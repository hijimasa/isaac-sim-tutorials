---
title: マニピュレータロボットの追加
---

# マニピュレータロボットの追加

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます:

- マニピュレータロボット（Franka Panda）をシーンに追加する方法
- `PickPlaceController` を使ったピック＆プレース動作の実装
- `BaseTask` を継承してタスクをモジュール化する方法
- Isaac Sim に用意されている既存のタスククラスの利用方法

## はじめに

### 前提条件

- [チュートリアル 3: コントローラの追加](03_adding_a_controller.md) を完了していること

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

## シーンの作成

これまでのチュートリアルでは車輪型ロボット（Jetbot）を使用してきましたが、ここでは新しいタイプのロボット——**マニピュレータ（ロボットアーム）**をシーンに追加します。

Isaac Sim には Franka Panda ロボット用の専用クラス `Franka` が用意されており、グリッパーやエンドエフェクタへのアクセスなど、マニピュレータに特化した機能を提供します。

```python linenums="1" hl_lines="3-4 18-19 21-28"
from isaacsim.examples.interactive.base_sample import BaseSample
# Franka 関連のタスク・コントローラを含む拡張機能
from isaacsim.robot.manipulators.examples.franka import Franka
from isaacsim.core.api.objects import DynamicCuboid
import numpy as np


class HelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        return

    def setup_scene(self):
        world = self.get_world()
        world.scene.add_default_ground_plane()
        # Franka はグリッパーやエンドエフェクタのインスタンスを持つ
        # ロボット固有クラス
        franka = world.scene.add(
            Franka(prim_path="/World/Fancy_Franka", name="fancy_franka")
        )
        # Franka がつかむためのキューブを追加
        world.scene.add(
            DynamicCuboid(
                prim_path="/World/random_cube",
                name="fancy_cube",
                position=np.array([0.3, 0.3, 0.3]),     # キューブの初期位置
                scale=np.array([0.0515, 0.0515, 0.0515]),# キューブのサイズ
                color=np.array([0, 0, 1.0]),              # 青色
            )
        )
        return
```

コードを保存してシミュレーションを確認します：

1. **Ctrl+S** を押してコードを保存し、Isaac Sim をホットリロードします。
2. **File > New From Stage Template > Empty** でワールドを新規作成してから、**LOAD** ボタンを押します。
3. Franka ロボットと青いキューブがシーンに表示されることを確認します。

## PickAndPlace コントローラの利用

次に、Franka のピック＆プレースコントローラを使って、キューブを拾い上げて別の場所に移動させます。

`PickPlaceController` はステートマシン（状態機械）として動作し、以下の一連の動作を自動的に実行します：

1. キューブの位置まで移動
2. グリッパーを閉じてキューブを把持
3. 目標位置まで移動
4. グリッパーを開いてキューブを配置

??? info "`events_dt` パラメータ（各ステートの実行速度）"
    `PickPlaceController` は内部的に上記の4ステップをさらに細かい **10 個のステート**（移動、下降、閉じ、持ち上げ、移動、下降、開き、持ち上げなど）に分割しています。`events_dt` パラメータは各ステートの実行速度（1 ステップあたりの補間量）を制御するリストです。

    デフォルト値が設定されているため通常は指定不要ですが、複数ロボットを同時に動かす場合や動作速度を調整したい場合に明示的に指定できます。詳しくは [チュートリアル 6](06_multiple_tasks.md) で使用します。

```python linenums="1" hl_lines="4 33-38 40-41 50-56 58-59"
from isaacsim.examples.interactive.base_sample import BaseSample
from isaacsim.robot.manipulators.examples.franka import Franka
from isaacsim.core.api.objects import DynamicCuboid
from isaacsim.robot.manipulators.examples.franka.controllers import PickPlaceController  # ピック＆プレースコントローラ
import numpy as np


class HelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        return

    def setup_scene(self):
        world = self.get_world()
        world.scene.add_default_ground_plane()
        franka = world.scene.add(
            Franka(prim_path="/World/Fancy_Franka", name="fancy_franka")
        )
        world.scene.add(
            DynamicCuboid(
                prim_path="/World/random_cube",
                name="fancy_cube",
                position=np.array([0.3, 0.3, 0.3]),
                scale=np.array([0.0515, 0.0515, 0.0515]),
                color=np.array([0, 0, 1.0]),
            )
        )
        return

    async def setup_post_load(self):
        self._world = self.get_world()
        self._franka = self._world.scene.get_object("fancy_franka")
        self._fancy_cube = self._world.scene.get_object("fancy_cube")
        # PickPlaceController を初期化
        self._controller = PickPlaceController(
            name="pick_place_controller",
            gripper=self._franka.gripper,            # グリッパーのインスタンス
            robot_articulation=self._franka,          # ロボットのアーティキュレーション
        )
        self._world.add_physics_callback("sim_step", callback_fn=self.physics_step)
        # グリッパーを開いた状態に設定
        self._franka.gripper.set_joint_positions(self._franka.gripper.joint_opened_positions)
        # 非同期ワークフロー（Extension Worlflowなど）では async 版の play を使う
        await self._world.play_async()
        return

    # RESET ボタン押下後に呼ばれる
    # ワールド内のリセット処理をここで行う
    async def setup_post_reset(self):
        self._controller.reset()
        self._franka.gripper.set_joint_positions(self._franka.gripper.joint_opened_positions)
        await self._world.play_async()
        return

    def physics_step(self, step_size):
        cube_position, _ = self._fancy_cube.get_world_pose()
        goal_position = np.array([-0.3, -0.3, 0.0515 / 2.0])  # 配置先の目標位置
        current_joint_positions = self._franka.get_joint_positions()
        # コントローラがピック＆プレースの各段階に応じたアクションを計算
        actions = self._controller.forward(
            picking_position=cube_position,
            placing_position=goal_position,
            current_joint_positions=current_joint_positions,
        )
        self._franka.apply_action(actions)
        # ステートマシンが最終状態に到達したらシミュレーションを一時停止
        if self._controller.is_done():
            self._world.pause()
        return
```

コードを保存してシミュレーションを確認します：

1. **Ctrl+S** を押して保存し、**File > New From Stage Template > Empty** → **LOAD** を実行します。
2. **PLAY** ボタンを押して、Franka がキューブを拾い上げて目標位置に配置する様子を確認します。
3. 動作が完了するとシミュレーションが自動的に一時停止します。

![Franka によるピック＆プレース動作](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/core_api_tutorials_4_1.webp)

## タスクとは？

ここまでのコードでは、シーンの作成（`setup_scene`）、コントローラの初期化（`setup_post_load`）、物理ステップの処理（`physics_step`）がすべて `HelloWorld` クラスに混在しています。

**Task** は、シーン内の特定の作業（タスク）をモジュール化するための仕組みです。`BaseTask` を継承してタスククラスを定義すると、以下の処理を独立して管理できます：

| メソッド | 説明 |
|---|---|
| `set_up_scene` | タスクに必要なアセットをシーンに配置 |
| `get_observations` | タスクの解決に必要な観測情報を返す |
| `pre_step(control_index, simulation_time)` | 各物理ステップの前に実行される処理（タスク達成判定など） |
| `post_reset` | リセット後の初期化処理 |

`pre_step` の引数 `control_index` は物理ステップごとに自動でインクリメントされるインデックス（0, 1, 2, ...）、`simulation_time` はシミュレーション開始からの経過時間（秒）です。いずれも World が自動的に渡すため、ユーザーが手動で管理する必要はありません。

タスクをモジュール化することで、同じタスクを異なるロボットやシーンで再利用できるようになります。

### 既存の PickPlace タスクを利用する

まずは Isaac Sim に用意されている既存のタスクを使って、タスクの基本的な使い方を学びましょう。Franka の場合、`PickPlace` タスクを使うことで、前のセクションと同等の処理をより整理されたコードで実現できます。

既存タスクの特徴：

- `get_params()` でタスクのパラメータ（ロボット名、キューブ名など）を動的に取得可能
- `set_params()` でシミュレーション中にパラメータを変更可能
- `world.get_observations()` でタスクが提供する観測情報を一括取得可能

```python linenums="1" hl_lines="2-3 11 17-20 22-23"
from isaacsim.examples.interactive.base_sample import BaseSample
from isaacsim.robot.manipulators.examples.franka.tasks import PickPlace        # 既存のタスク
from isaacsim.robot.manipulators.examples.franka.controllers import PickPlaceController


class HelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        return

    def setup_scene(self):
        world = self.get_world()
        # 既存の PickPlace タスクを追加
        world.add_task(PickPlace(name="awesome_task"))
        return

    async def setup_post_load(self):
        self._world = self.get_world()
        # タスクからパラメータを動的に取得
        # {"task_param_name": {"value": [value], "modifiable": [True/False]}}
        task_params = self._world.get_task("awesome_task").get_params()
        self._franka = self._world.scene.get_object(task_params["robot_name"]["value"])
        self._cube_name = task_params["cube_name"]["value"]
        self._controller = PickPlaceController(
            name="pick_place_controller",
            gripper=self._franka.gripper,
            robot_articulation=self._franka,
        )
        self._world.add_physics_callback("sim_step", callback_fn=self.physics_step)
        await self._world.play_async()
        return

    async def setup_post_reset(self):
        self._controller.reset()
        await self._world.play_async()
        return

    def physics_step(self, step_size):
        current_observations = self._world.get_observations()
        actions = self._controller.forward(
            picking_position=current_observations[self._cube_name]["position"],
            placing_position=current_observations[self._cube_name]["target_position"],
            current_joint_positions=current_observations[self._franka.name]["joint_positions"],
        )
        self._franka.apply_action(actions)
        if self._controller.is_done():
            self._world.pause()
        return
```

前のセクションのコードと比較すると、`setup_scene` がシンプルになっていることがわかります。シーンの構築（Franka やキューブの配置）はタスク内部で自動的に行われるため、`HelloWorld` クラスではタスクの追加とコントローラの実行に集中できます。

## カスタムタスクの作成

既存タスクの使い方がわかったところで、次は `BaseTask` を継承して独自のタスクを作成してみましょう。カスタムタスクを作ることで、タスク達成の判定やビジュアルフィードバックなど、独自のロジックを追加できます。

以下のコードでは `FrankaPlaying` タスクを定義し、キューブが目標位置に到達したら色を緑に変える機能を追加しています。

```python linenums="1" hl_lines="5 8-62 69 78-81"
from isaacsim.examples.interactive.base_sample import BaseSample
from isaacsim.robot.manipulators.examples.franka import Franka
from isaacsim.core.api.objects import DynamicCuboid
from isaacsim.robot.manipulators.examples.franka.controllers import PickPlaceController
from isaacsim.core.api.tasks import BaseTask  # タスクの基底クラス
import numpy as np


class FrankaPlaying(BaseTask):
    # ここでは BaseTask の一部のメソッドのみオーバーライドしている
    # calculate_metrics, is_done など他にもオーバーライド可能なメソッドがある
    def __init__(self, name):
        super().__init__(name=name, offset=None)
        self._goal_position = np.array([-0.3, -0.3, 0.0515 / 2.0])
        self._task_achieved = False
        return

    # タスクに必要なアセットをシーンに配置する
    def set_up_scene(self, scene):
        super().set_up_scene(scene)
        scene.add_default_ground_plane()
        self._cube = scene.add(
            DynamicCuboid(
                prim_path="/World/random_cube",
                name="fancy_cube",
                position=np.array([0.3, 0.3, 0.3]),
                scale=np.array([0.0515, 0.0515, 0.0515]),
                color=np.array([0, 0, 1.0]),
            )
        )
        self._franka = scene.add(
            Franka(prim_path="/World/Fancy_Franka", name="fancy_franka")
        )
        return

    # タスクの解決に必要な観測情報を返す
    def get_observations(self):
        cube_position, _ = self._cube.get_world_pose()
        current_joint_positions = self._franka.get_joint_positions()
        observations = {
            self._franka.name: {
                "joint_positions": current_joint_positions,
            },
            self._cube.name: {
                "position": cube_position,
                "goal_position": self._goal_position,
            },
        }
        return observations

    # 各物理ステップの前に呼ばれる
    # タスク達成の判定やビジュアルのフィードバックを行う
    def pre_step(self, control_index, simulation_time):
        cube_position, _ = self._cube.get_world_pose()
        if not self._task_achieved and np.mean(np.abs(self._goal_position - cube_position)) < 0.02:
            # キューブが目標位置に到達したら色を緑に変更
            self._cube.get_applied_visual_material().set_color(color=np.array([0, 1.0, 0]))
            self._task_achieved = True
        return

    # リセット後に呼ばれる
    # グリッパーを開いた状態にし、キューブの色を青に戻す
    def post_reset(self):
        self._franka.gripper.set_joint_positions(self._franka.gripper.joint_opened_positions)
        self._cube.get_applied_visual_material().set_color(color=np.array([0, 0, 1.0]))
        self._task_achieved = False
        return


class HelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        return

    def setup_scene(self):
        world = self.get_world()
        # タスクをワールドに追加する
        world.add_task(FrankaPlaying(name="my_first_task"))
        return

    async def setup_post_load(self):
        self._world = self.get_world()
        # ワールドが初回リセット時にタスクの set_up_scene を呼び出し済み
        # なのでタスク内のオブジェクトを取得できる
        self._franka = self._world.scene.get_object("fancy_franka")
        self._controller = PickPlaceController(
            name="pick_place_controller",
            gripper=self._franka.gripper,
            robot_articulation=self._franka,
        )
        self._world.add_physics_callback("sim_step", callback_fn=self.physics_step)
        await self._world.play_async()
        return

    async def setup_post_reset(self):
        self._controller.reset()
        await self._world.play_async()
        return

    def physics_step(self, step_size):
        # タスクからすべての観測情報を取得
        current_observations = self._world.get_observations()
        actions = self._controller.forward(
            picking_position=current_observations["fancy_cube"]["position"],
            placing_position=current_observations["fancy_cube"]["goal_position"],
            current_joint_positions=current_observations["fancy_franka"]["joint_positions"],
        )
        self._franka.apply_action(actions)
        if self._controller.is_done():
            self._world.pause()
        return
```

カスタムタスクでは、既存タスクにはない独自の機能（`pre_step` でのキューブの色変更など）を追加できます。一方、シーン構築や観測情報の定義を自前で実装する必要があります。

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. **Franka Panda** マニピュレータロボットのシーンへの追加
2. **PickPlaceController** を使ったピック＆プレース動作の実装
3. 既存の **PickPlace** タスクを使ったタスクの基本的な利用方法
4. **BaseTask** を継承したカスタムタスクの作成と独自ロジックの追加

## 次のステップ

次のチュートリアル「[複数ロボットの追加](05_adding_multiple_robots.md)」に進み、複数のロボットが連携するシミュレーションの構築方法を学びましょう。

!!! note "注釈"
    以降のチュートリアルでも主に Extension Workflow を使用して開発を進めます。Standalone Workflow への変換方法は [Hello World](01_hello_world.md#_11) で学んだ手順と同様です。
