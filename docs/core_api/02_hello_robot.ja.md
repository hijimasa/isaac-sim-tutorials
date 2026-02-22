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

### ソースコードの準備

このチュートリアルでは、引き続き Hello World サンプルの `hello_world.py` を編集していきます。前回のチュートリアルから続けて作業している場合はそのまま進めてください。別の日に作業を再開する場合は、以下の手順でソースコードを開いてください。

1. **Windows > Examples > Robotics Examples** をアクティブにして、Robotics Examples タブを開きます。
2. **Robotics Examples > General > Hello World** をクリックします。
3. **Open Source Code** ボタンをクリックし、Visual Studio Code で `hello_world.py` を開きます。

詳しい手順は [Hello World の「サンプルを開く」セクション](01_hello_world.md#hello-world_1)を参照してください。

## ロボットをシーンに追加する

前回のチュートリアルでは立方体をシーンに追加しましたが、今回はロボットを追加します。ここでは NVIDIA の **Jetbot**（2輪の差動駆動ロボット）を使用します。

??? info "GUI でロボットを追加する方法（クリックで展開）"
    Python コードを書かなくても、Isaac Sim Assets ブラウザからドラッグ＆ドロップでロボットをシーンに追加できます。

    1. **Window > Browsers > Isaac Sim Assets** をクリックして、Isaac Sim Assets ウィンドウを有効にします。<br>
       ![Isaac Sim Assets ウィンドウを有効にする](images/09_isaac_sim_assets_browser.png)

        !!! warning "初回起動時の注意"
            Isaac Sim Assets ウィンドウを初めて開く際、アセットデータのダウンロードが行われるため、表示されるまでに時間がかかることがあります。ネットワーク環境によっては数分以上かかる場合があります。

    2. 検索バーに「Jetbot」と入力し、表示された Jetbot アセットをビューポートにドラッグ＆ドロップします。<br>
       ![Jetbot をドラッグ＆ドロップ](images/10_drag_and_drop_jetbot.webp)

    この方法は素早くロボットを配置したい場合に便利ですが、Python API を使った方法を覚えることで、プログラムから動的にロボットを追加・制御できるようになります。以降ではPython APIを使った方法を解説します。

### Python API によるロボットの追加

ロボットアセットは Omniverse Nucleus サーバーに格納されています。`get_assets_root_path()` でアセットのルートパスを取得し、`add_reference_to_stage()` でアセットを USD Stage に読み込みます。

ただし、`add_reference_to_stage()` だけではロボットの 3D モデルと物理プロパティが Stage 上に配置されるだけで、関節の位置取得や速度指令といった**ロボットとしての制御**はできません。制御するには低レベルな USD API や PhysX API を直接操作する必要があります。

そこで、読み込んだロボットのプリムを `Robot` クラスでラップし、`world.scene.add()` で Scene に登録します。`Robot` クラスは既存のプリムを**参照するだけ**で、プリムのコピーや変換は行いません。同じ `/World/Fancy_Robot` プリムに対して、`get_joint_positions()` や `apply_action()` などの高レベル API を提供する Python オブジェクトを作成します。

| 処理 | 役割 |
|---|---|
| `add_reference_to_stage()` | USD Stage 上にロボットのプリムを作成する |
| `Robot(prim_path=...)` | 既存のプリムを参照し、高レベル API を提供する Python ラッパーを作成する |
| `world.scene.add()` | ラッパーを Scene に登録し、World のライフサイクル（reset/step）と連携させる |

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

!!! info "参照（Reference）について"
    `add_reference_to_stage()` は USD ファイルを**参照（Reference）**として Stage に追加します。元のファイルへのリンクを保持するため、アセットの変更が自動的に反映されます。USD の内容を Stage に直接コピーする方法もありますが、ロボットアセットの読み込みでは参照方式が一般的です。

コードを保存してシミュレーションを確認します：

1. **Ctrl+S** を押してコードを保存し、Isaac Sim をホットリロードします。
2. Hello World サンプル拡張機能のウィンドウを再度開きます。
3. **File > New From Stage Template > Empty** でワールドを新規作成してから、**LOAD** ボタンを押します。
4. ターミナルの出力を確認します。

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

ロボットの動作制御には **ArticulationController**（アーティキュレーションコントローラ）を使用します。これは**暗黙的な PD コントローラ**として動作し、PD ゲインの設定、アクションの適用、制御モードの切り替えなどを行えます。

??? info "暗黙的な PD コントローラとは（クリックで展開）"
    実際のロボットでは、モータに「目標位置」や「目標速度」を指定すると、モータドライバ内の制御器が目標値と現在値の差に応じて電流（トルク）を計算し、関節を動かします。

    Isaac Sim の物理エンジン（PhysX）でも同様の仕組みが内部に組み込まれています。`joint_positions` や `joint_velocities` で目標値を指定すると、PhysX が内部で **PD 制御（比例-微分制御）** を行い、目標に追従するために必要な力を自動計算します。

    $$
    F = K_p \cdot (x_{\text{target}} - x_{\text{current}}) + K_d \cdot (\dot{x}_{\text{target}} - \dot{x}_{\text{current}})
    $$

    この PD コントローラはユーザーが明示的に実装するのではなく、物理エンジンに**暗黙的に**組み込まれているため、「暗黙的な PD コントローラ」と呼ばれます。$K_p$（比例ゲイン）と $K_d$（微分ゲイン）は `ArticulationController` を通じて調整できます。

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

!!! note "2つの `apply_action` の使い分け"
    コード中のコメントにある通り、同じ処理は `self._jetbot.apply_action(...)` でも呼び出せます。それぞれの特徴は以下の通りです：

    | 呼び出し方 | 特徴 |
    |---|---|
    | `robot.get_articulation_controller().apply_action()` | PD ゲインの変更や制御モードの切り替えなど、ArticulationController の詳細な設定にアクセスできる |
    | `robot.apply_action()` | 簡潔に書ける。内部で ArticulationController を呼び出しているため動作は同じ |

    PD ゲインの調整が不要な場合は `robot.apply_action()` で十分です。次のチュートリアルからはこちらの簡潔な書き方を使用します。

コードを保存してシミュレーションを確認します：

1. **Ctrl+S** を押してコードを保存し、Isaac Sim をホットリロードします。
2. **File > New From Stage Template > Empty** でワールドを新規作成してから、**LOAD** ボタンを押します。
3. **PLAY** ボタンを押して、Jetbot がランダムに動き回る様子を確認します。

![Jetbot がランダムに動き回る様子](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/core_api_tutorials_2_2.webp)

毎ステップで左右の車輪にランダムな速度（0〜5 の範囲）を適用しているため、Jetbot は不規則に動きます。

## 練習問題

以下の練習問題に挑戦して、ロボット制御の理解を深めましょう。

**問題 1: 後退させる** — Jetbot を後ろ向きに移動させてみましょう。

??? tip "ヒント（クリックで展開）"
    車輪の速度を負の値にします。

**問題 2: 右に旋回させる** — Jetbot を右方向に旋回させてみましょう。

??? tip "ヒント（クリックで展開）"
    左右の車輪に異なる速度を設定します（左の車輪を速く、右を遅く）。

**問題 3: 5秒後に停止させる** — シミュレーション開始から5秒後に Jetbot を停止させてみましょう。

??? tip "ヒント（クリックで展開）"
    `step_size` を毎ステップ累積して経過時間を計算し、条件分岐で停止させます。

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

次のチュートリアル「[コントローラの追加](03_adding_a_controller.md)」に進み、ロボットにコントローラを追加してより高度な動作を実現する方法を学びましょう。

!!! note "注釈"
    以降のチュートリアルでも主に Extension Workflow を使用して開発を進めます。Standalone Workflow への変換方法は [Hello World](01_hello_world.md#_11) で学んだ手順と同様です。
