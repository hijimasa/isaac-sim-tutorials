---
title: Hello Robot
---

# Hello Robot

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます:

- Nucleus サーバーからロボットアセットをシーンに読み込む方法
- `Robot` クラスを使用してロボットプリムをラップし、高レベル API でアクセスする方法
- アーティキュレーション（関節構造）のジョイントに速度指令を送ってロボットを動かす方法
- 物理演算コールバックを使ってシミュレーション中に継続的にアクションを適用する方法
- `WheeledRobot` クラスを使って車輪型ロボットをより簡潔に制御する方法

## はじめに

### 前提条件

- [チュートリアル 1: Hello World](01_hello_world.md) を完了していること
- `/Isaac` フォルダを含む Omniverse Nucleus サーバーが設定済みであること

### 所要時間

約 10〜15 分

## ロボットをシーンに追加する

前回のチュートリアルでは立方体をシーンに追加しましたが、今回はロボットを追加します。ここでは NVIDIA の **Jetbot**（2輪の差動駆動ロボット）を使用します。

ロボットアセットは Omniverse Nucleus サーバーに格納されています。`get_assets_root_path()` でアセットのルートパスを取得し、`add_reference_to_stage()` でアセットを USD Stage に読み込みます。

読み込んだロボットを `Robot` クラスでラップし、`world.scene.add()` で Scene に登録することで、高レベル API（位置取得・関節制御など）が利用可能になります。

```python linenums="1" hl_lines="2-4 17-30 33-37"
from isaacsim.examples.interactive.base_sample import BaseSample
from isaacsim.core.utils.nucleus import get_assets_root_path  # Nucleus アセットパス取得
from isaacsim.core.utils.stage import add_reference_to_stage   # USD Stage へのアセット追加
from isaacsim.core.api.robots import Robot                     # ロボット高レベル API クラス
import carb


class HelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        return

    def setup_scene(self):
        world = self.get_world()
        world.scene.add_default_ground_plane()

        # Nucleus サーバーから /Isaac フォルダのルートパスを取得
        assets_root_path = get_assets_root_path()
        if assets_root_path is None:
            # carb でターミナルに警告・エラー・情報を出力できる
            carb.log_error("Could not find nucleus server with /Isaac folder")

        asset_path = assets_root_path + "/Isaac/Robots/NVIDIA/Jetbot/jetbot.usd"
        # USD ファイルへの参照として新しい XFormPrim を作成する
        # メモリのポインタと同様の仕組み
        add_reference_to_stage(usd_path=asset_path, prim_path="/World/Fancy_Robot")

        # Jetbot のプリムルートを Robot クラスでラップし、Scene に追加する
        # これにより高レベル API で属性の取得・設定や物理ハンドルの初期化が可能になる
        # 注意: この呼び出しは Stage 上に Jetbot を新規作成するわけではない
        #       add_reference_to_stage で既に作成済み
        jetbot_robot = world.scene.add(
            Robot(prim_path="/World/Fancy_Robot", name="fancy_robot")
        )

        # リセット前はアーティキュレーション情報にアクセスできない（物理ハンドル未初期化のため）
        # setup_post_load は初回リセット後に呼ばれるので、そこでアクセスする
        print("Num of degrees of freedom before first reset: " + str(jetbot_robot.num_dof))  # None と出力される
        return

    async def setup_post_load(self):
        self._world = self.get_world()
        self._jetbot = self._world.scene.get_object("fancy_robot")
        # 初回リセット後はアーティキュレーション情報にアクセス可能
        print("Num of degrees of freedom after first reset: " + str(self._jetbot.num_dof))  # 2 と出力される
        print("Joint Positions after first reset: " + str(self._jetbot.get_joint_positions()))
        return
```

コードを保存してシミュレーションを確認します：

1. **Ctrl+S** を押してコードを保存し、Isaac Sim をホットリロードします。
2. Hello World サンプル拡張機能のウィンドウを再度開きます。
3. **File > New From Stage Template > Empty** でワールドを新規作成してから、**LOAD** ボタンを押します。
4. ターミナルの出力を確認します。

![Jetbot をシーンに追加した様子](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/core_api_tutorials_2_1.webp)

### 物理ハンドルに関する重要なポイント

`setup_scene` と `setup_post_load` で表示される `num_dof`（自由度の数）が異なることに注目してください。

| タイミング | `num_dof` の値 | 理由 |
|---|---|---|
| `setup_scene`（リセット前） | `None` | 物理ハンドルが未初期化 |
| `setup_post_load`（リセット後） | `2` | 物理ハンドルが初期化済み（左右の車輪） |

!!! warning "注意"
    アーティキュレーション（関節構造）のプロパティ（自由度、ジョイント位置など）は、最初のリセットが行われるまでアクセスできません。これらの情報を取得する処理は、必ず `setup_post_load` 以降で行ってください。

## ロボットを動かす

次に、Jetbot の車輪に速度指令を送って動かします。

ロボットの動作制御には **ArticulationController**（アーティキュレーションコントローラ）を使用します。これは暗黙的な PD コントローラとして動作し、PD ゲインの設定、アクションの適用、制御モードの切り替えなどを行えます。

`ArticulationAction` には以下の3つのパラメータを指定できます：

| パラメータ | 説明 |
|---|---|
| `joint_positions` | 各ジョイントの目標位置 |
| `joint_velocities` | 各ジョイントの目標速度 |
| `joint_efforts` | 各ジョイントに適用するトルク/力 |

いずれも `numpy` 配列、`list`、または `None`（その自由度には指令を送らない）を指定できます。

```python linenums="1" hl_lines="2 30-33 36-37 39-47"
from isaacsim.examples.interactive.base_sample import BaseSample
from isaacsim.core.utils.types import ArticulationAction  # ジョイント指令のデータ型
from isaacsim.core.utils.nucleus import get_assets_root_path
from isaacsim.core.utils.stage import add_reference_to_stage
from isaacsim.core.api.robots import Robot
import numpy as np
import carb


class HelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        return

    def setup_scene(self):
        world = self.get_world()
        world.scene.add_default_ground_plane()
        assets_root_path = get_assets_root_path()
        if assets_root_path is None:
            carb.log_error("Could not find nucleus server with /Isaac folder")
        asset_path = assets_root_path + "/Isaac/Robots/NVIDIA/Jetbot/jetbot.usd"
        add_reference_to_stage(usd_path=asset_path, prim_path="/World/Fancy_Robot")
        jetbot_robot = world.scene.add(
            Robot(prim_path="/World/Fancy_Robot", name="fancy_robot")
        )
        return

    async def setup_post_load(self):
        self._world = self.get_world()
        self._jetbot = self._world.scene.get_object("fancy_robot")
        # アーティキュレーションコントローラを取得（初回リセット後のみ呼び出し可能）
        # PD ゲインの設定やアクションの適用に使用する
        self._jetbot_articulation_controller = self._jetbot.get_articulation_controller()
        # 物理演算コールバックを追加し、毎ステップごとにアクションを適用する
        self._world.add_physics_callback("sending_actions", callback_fn=self.send_robot_actions)
        return

    # 物理演算コールバック: 各ステップで呼ばれ、ロボットにアクションを送信する
    def send_robot_actions(self, step_size):
        # apply_action は ArticulationAction を受け取り、各ジョイントに指令を送る
        # joint_positions, joint_efforts, joint_velocities を指定可能
        # None を指定した自由度にはこのステップでは指令を送らない
        # 同じ処理は self._jetbot.apply_action(...) からも呼び出せる
        self._jetbot_articulation_controller.apply_action(
            ArticulationAction(
                joint_positions=None,
                joint_efforts=None,
                joint_velocities=5 * np.random.rand(2,)  # 左右の車輪にランダムな速度を指定
            )
        )
        return
```

コードを保存してシミュレーションを確認します：

1. **Ctrl+S** を押してコードを保存し、Isaac Sim をホットリロードします。
2. **File > New From Stage Template > Empty** でワールドを新規作成してから、**LOAD** ボタンを押します。
3. **PLAY** ボタンを押して、Jetbot がランダムに動き回る様子を確認します。

![Jetbot がランダムに動き回る様子](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/core_api_tutorials_2_2.webp)

毎ステップで左右の車輪にランダムな速度（0〜5 の範囲）を適用しているため、Jetbot は不規則に動きます。

## 練習問題

以下の練習問題に挑戦して、ロボット制御の理解を深めましょう。

!!! question "練習問題"
    1. **後退させる** — Jetbot を後ろ向きに移動させてみましょう。
    2. **右に旋回させる** — Jetbot を右方向に旋回させてみましょう。
    3. **5秒後に停止させる** — シミュレーション開始から5秒後に Jetbot を停止させてみましょう。

??? tip "ヒント（クリックで展開）"
    - **後退**: 車輪の速度を負の値にします。
    - **右旋回**: 左右の車輪に異なる速度を設定します（左の車輪を速く、右を遅く）。
    - **時間制限**: `step_size` を毎ステップ累積して経過時間を計算し、条件分岐で停止させます。

## WheeledRobot クラスを使う

ここまでは汎用的な `Robot` クラスを使用していました。Isaac Sim には、特定のロボットタイプに特化したクラスも用意されています。車輪型ロボットの場合は `WheeledRobot` クラスを使うことで、より簡潔にコードを記述できます。

`Robot` クラスと `WheeledRobot` クラスの違いを見てみましょう：

| 特徴 | `Robot` クラス | `WheeledRobot` クラス |
|---|---|---|
| アセット読み込み | `add_reference_to_stage` + `Robot()` の2段階 | `WheeledRobot()` で一括（`create_robot=True`） |
| 車輪のジョイント | インデックスで指定 | ジョイント名で指定可能 |
| アクション適用 | `get_articulation_controller().apply_action()` | `apply_wheel_actions()` で直接指定 |

```python linenums="1" hl_lines="3 15-23 30-31"
from isaacsim.examples.interactive.base_sample import BaseSample
from isaacsim.core.utils.nucleus import get_assets_root_path
from isaacsim.robot.wheeled_robots.robots import WheeledRobot  # 車輪型ロボット専用クラス
from isaacsim.core.utils.types import ArticulationAction
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
        # WheeledRobot はアセットの読み込みと Robot ラッパーの作成を一度に行う
        self._jetbot = world.scene.add(
            WheeledRobot(
                prim_path="/World/Fancy_Robot",
                name="fancy_robot",
                wheel_dof_names=["left_wheel_joint", "right_wheel_joint"],  # 車輪のジョイント名
                create_robot=True,       # USD アセットの読み込みも同時に行う
                usd_path=jetbot_asset_path,
            )
        )
        return

    async def setup_post_load(self):
        self._world = self.get_world()
        self._jetbot = self._world.scene.get_object("fancy_robot")
        self._world.add_physics_callback("sending_actions", callback_fn=self.send_robot_actions)
        return

    def send_robot_actions(self, step_size):
        # apply_wheel_actions で車輪に直接アクションを適用できる
        self._jetbot.apply_wheel_actions(
            ArticulationAction(
                joint_positions=None,
                joint_efforts=None,
                joint_velocities=5 * np.random.rand(2,)  # 左右の車輪にランダムな速度を指定
            )
        )
        return
```

`WheeledRobot` を使った場合のポイント：

- `add_reference_to_stage` の呼び出しが不要（`create_robot=True` でアセット読み込みも含まれる）
- `wheel_dof_names` で車輪のジョイント名を明示的に指定できる
- `apply_wheel_actions()` で車輪に特化したアクション適用が可能

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. **Nucleus サーバー**からロボットアセットを読み込みシーンに追加する方法
2. **Robot クラス**でロボットプリムをラップし、高レベル API でアクセスする方法
3. **ArticulationController** と **ArticulationAction** によるジョイント制御
4. **物理演算コールバック**を使ったシミュレーション中の継続的なアクション適用
5. **WheeledRobot クラス**を使った車輪型ロボットの簡潔な制御

## 次のステップ

次のチュートリアル「Adding a Controller」に進み、ロボットにコントローラを追加してより高度な動作を実現する方法を学びましょう。

!!! note "注釈"
    以降のチュートリアルでも主に Extension Workflow を使用して開発を進めます。Standalone Workflow への変換方法は [Hello World](01_hello_world.md) で学んだ手順と同様です。
