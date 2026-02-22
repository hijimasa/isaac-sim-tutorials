---
title: コントローラの追加
---

# コントローラの追加

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます:

- `BaseController` を継承してカスタムコントローラを作成する方法
- ユニサイクルモデル（差動駆動の運動学モデル）を使ったロボット制御の基礎
- Isaac Sim に用意されている既存のコントローラを利用する方法

## はじめに

### 前提条件

- [チュートリアル 2: Hello Robot](02_hello_robot.md) を完了していること

### 所要時間

約 10 分

### ソースコードの準備

このチュートリアルでは、引き続き Hello World サンプルの `hello_world.py` を編集していきます。前回のチュートリアルから続けて作業している場合はそのまま進めてください。別の日に作業を再開する場合は、以下の手順でソースコードを開いてください。

1. **Windows > Examples > Robotics Examples** をアクティブにして、Robotics Examples タブを開きます。
2. **Robotics Examples > General > Hello World** をクリックします。
3. **Open Source Code** ボタンをクリックし、Visual Studio Code で `hello_world.py` を開きます。

詳しい手順は [Hello World の「サンプルを開く」セクション](01_hello_world.md)を参照してください。

## カスタムコントローラの作成

前回のチュートリアルでは、各車輪に直接速度を指定してロボットを動かしました。しかし実際のロボット制御では、「前進速度」や「旋回速度」といった高レベルなコマンドで操作したい場面がほとんどです。

この変換を行うのが**コントローラ**です。Isaac Sim のコントローラは `BaseController` を継承して作成します。実装する必要があるのは `forward` メソッドのみで、このメソッドは `ArticulationAction` を返す必要があります。

### ユニサイクルモデル

差動駆動ロボット（Jetbot のような2輪ロボット）では、前進速度 $v$ と旋回角速度 $\omega$ から各車輪の速度を計算する**ユニサイクルモデル**がよく使われます。

計算式は以下の通りです：

| 変数 | 説明 |
|---|---|
| $v$ | 前進速度（`command[0]`） |
| $\omega$ | 旋回角速度（`command[1]`） |
| $r$ | 車輪の半径（`wheel_radius`） |
| $L$ | 左右車輪間の距離＝トレッド（`wheel_base`）[^1] |

[^1]: 厳密には左右の車輪間距離は「トレッド（tread）」と呼ばれますが、Isaac Sim の API ではパラメータ名として `wheel_base` が使用されています。

$$
v_{\text{left}} = \frac{2v - \omega L}{2r}, \quad v_{\text{right}} = \frac{2v + \omega L}{2r}
$$

### コード全体

以下のコードでは、`CoolController` クラスでユニサイクルモデルを実装し、前進速度 0.20 m/s と旋回角速度 π/4 rad/s を指定して Jetbot を円弧状に走行させます。

```python linenums="1" hl_lines="5 8-22 52-53 56-58"
from isaacsim.examples.interactive.base_sample import BaseSample
from isaacsim.core.utils.nucleus import get_assets_root_path
from isaacsim.robot.wheeled_robots.robots import WheeledRobot
from isaacsim.core.utils.types import ArticulationAction
from isaacsim.core.api.controllers import BaseController  # コントローラの基底クラス
import numpy as np


class CoolController(BaseController):
    def __init__(self):
        super().__init__(name="my_cool_controller")
        # ユニサイクルモデルに基づくオープンループコントローラ
        self._wheel_radius = 0.03    # 車輪の半径 [m]
        self._wheel_base = 0.1125    # 左右車輪間の距離（トレッド） [m]
        return

    def forward(self, command):
        # command[0]: 前進速度, command[1]: 旋回角速度（ヨー方向のみ）
        joint_velocities = [0.0, 0.0]
        joint_velocities[0] = ((2 * command[0]) - (command[1] * self._wheel_base)) / (2 * self._wheel_radius)
        joint_velocities[1] = ((2 * command[0]) + (command[1] * self._wheel_base)) / (2 * self._wheel_radius)
        # コントローラは ArticulationAction を返す必要がある
        return ArticulationAction(joint_velocities=joint_velocities)


class HelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        return

    def setup_scene(self):
        world = self.get_world()
        world.scene.add_default_ground_plane()
        assets_root_path = get_assets_root_path()
        jetbot_asset_path = assets_root_path + "/Isaac/Robots/NVIDIA/Jetbot/jetbot.usd"
        world.scene.add(
            WheeledRobot(
                prim_path="/World/Fancy_Robot",
                name="fancy_robot",
                wheel_dof_names=["left_wheel_joint", "right_wheel_joint"],
                create_robot=True,
                usd_path=jetbot_asset_path,
            )
        )
        return

    async def setup_post_load(self):
        self._world = self.get_world()
        self._jetbot = self._world.scene.get_object("fancy_robot")
        self._world.add_physics_callback("sending_actions", callback_fn=self.send_robot_actions)
        # ロード・初回リセット後にコントローラを初期化
        self._my_controller = CoolController()
        return

    def send_robot_actions(self, step_size):
        # コントローラが計算したアクションをロボットに適用
        self._jetbot.apply_action(
            self._my_controller.forward(command=[0.20, np.pi / 4])
        )
        return
```

コードを保存してシミュレーションを確認します：

1. **Ctrl+S** を押してコードを保存し、Isaac Sim をホットリロードします。
2. **File > New From Stage Template > Empty** でワールドを新規作成してから、**LOAD** ボタンを押します。
3. **PLAY** ボタンを押して、Jetbot が円弧を描いて走行する様子を確認します。

![カスタムコントローラによる円弧走行](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/core_api_tutorials_3_1.webp)

!!! warning "注意"
    **STOP** → **PLAY** の操作ではワールドが正しくリセットされない場合があります。シミュレーションをやり直す場合は、**RESET** ボタンを使用してください。

### カスタムコントローラのポイント

- `BaseController` を継承し、`forward` メソッドを実装する
- `forward` メソッドは必ず `ArticulationAction` を返す
- コントローラ内でロボット固有のパラメータ（車輪半径、車輪間距離など）を管理する
- 高レベルなコマンド（前進速度、旋回速度）を低レベルなジョイント指令に変換する役割を担う

## 既存のコントローラを利用する

Isaac Sim には、よく使われるロボットの制御パターンに対応した**既存のコントローラ**が用意されています。これらを活用することで、運動学の計算を自前で実装する必要がなくなります。

ここでは以下の2つのコントローラを組み合わせて使用します：

| コントローラ | 種類 | 説明 |
|---|---|---|
| `WheelBasePoseController` | 汎用コントローラ | 目標位置に向かってロボットを誘導する。複数のロボットタイプで利用可能 |
| `DifferentialController` | ロボット固有コントローラ | 差動駆動ロボット用。前進・旋回速度から車輪速度を計算する |

`WheelBasePoseController` は内部で `DifferentialController` を使い、目標位置への経路を計算します。前のセクションで自作したコントローラと異なり、**ロボットの現在位置と目標位置**を指定するだけで自動的にロボットを誘導してくれます。

```python linenums="1" hl_lines="5-8 44-48 51-55"
from isaacsim.examples.interactive.base_sample import BaseSample
from isaacsim.core.utils.nucleus import get_assets_root_path
from isaacsim.robot.wheeled_robots.robots import WheeledRobot
# 複数のロボットタイプで使える汎用コントローラ
from isaacsim.robot.wheeled_robots.controllers.wheel_base_pose_controller import WheelBasePoseController
# 差動駆動ロボット固有のコントローラ
from isaacsim.robot.wheeled_robots.controllers.differential_controller import DifferentialController
import numpy as np


class HelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        return

    def setup_scene(self):
        world = self.get_world()
        world.scene.add_default_ground_plane()
        assets_root_path = get_assets_root_path()
        jetbot_asset_path = assets_root_path + "/Isaac/Robots/NVIDIA/Jetbot/jetbot.usd"
        world.scene.add(
            WheeledRobot(
                prim_path="/World/Fancy_Robot",
                name="fancy_robot",
                wheel_dof_names=["left_wheel_joint", "right_wheel_joint"],
                create_robot=True,
                usd_path=jetbot_asset_path,
            )
        )
        return

    async def setup_post_load(self):
        self._world = self.get_world()
        self._jetbot = self._world.scene.get_object("fancy_robot")
        self._world.add_physics_callback("sending_actions", callback_fn=self.send_robot_actions)
        # WheelBasePoseController に DifferentialController を渡して初期化
        self._my_controller = WheelBasePoseController(
            name="cool_controller",
            open_loop_wheel_controller=DifferentialController(
                name="simple_control",
                wheel_radius=0.03,      # 車輪の半径 [m]
                wheel_base=0.1125       # 左右車輪間の距離（トレッド） [m]
            ),
            is_holonomic=False  # Jetbot は非ホロノミック（横移動不可）
        )
        return

    def send_robot_actions(self, step_size):
        # ロボットの現在位置と姿勢を取得
        position, orientation = self._jetbot.get_world_pose()
        # 現在位置・姿勢と目標位置を渡すだけで、コントローラが経路を計算してくれる
        self._jetbot.apply_action(
            self._my_controller.forward(
                start_position=position,
                start_orientation=orientation,
                goal_position=np.array([0.8, 0.8])  # 目標位置 [x, y]
            )
        )
        return
```

コードを保存してシミュレーションを確認します：

1. **Ctrl+S** を押してコードを保存し、Isaac Sim をホットリロードします。
2. **File > New From Stage Template > Empty** でワールドを新規作成してから、**LOAD** ボタンを押します。
3. **PLAY** ボタンを押して、Jetbot が目標位置 (0.8, 0.8) に向かって自律的に移動する様子を確認します。

![既存コントローラによる目標位置への移動](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/core_api_tutorials_3_2.webp)

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. **BaseController** を継承したカスタムコントローラの作成
2. **ユニサイクルモデル**による差動駆動ロボットの運動学
3. **WheelBasePoseController** と **DifferentialController** を使った目標位置への自律移動

## 次のステップ

次のチュートリアル「[マニピュレータロボットの追加](04_adding_a_manipulator_robot.md)」に進み、マニピュレータロボットをシミュレーションに追加する方法を学びましょう。

!!! note "注釈"
    以降のチュートリアルでも主に Extension Workflow を使用して開発を進めます。Standalone Workflow への変換方法は [Hello World](01_hello_world.md#_11) で学んだ手順と同様です。
