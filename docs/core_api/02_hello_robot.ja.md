---
title: Hello Robot
---

# Hello Robot

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます:

- Nucleus サーバーからロボットアセットをシーンに読み込む方法
- `Articulation` クラスを使用してロボットプリムをラップし、高レベル API でアクセスする方法
- `set_dof_velocity_targets()` でジョイントに速度指令を送ってロボットを動かす方法
- `SimulationManager` の物理演算コールバックを使ってシミュレーション中に継続的にアクションを適用する方法
- ジョイント名やインデックスを指定して特定のジョイントだけを制御する方法

## はじめに

### 前提条件

- [チュートリアル 1: Hello World](01_hello_world.md) を完了していること
- `/Isaac` フォルダを含む Omniverse Nucleus サーバーが設定済みであること

!!! note "Nucleus サーバーとは"
    **Nucleus** は Omniverse のアセット配信・共有サーバーです。Isaac Sim が使用するロボットや環境などの公式アセット（`/Isaac` フォルダ以下）は、Nucleus 経由で読み込まれます。標準的なインストール手順で Isaac Sim をセットアップしていれば追加の設定は不要で、アセットのパス（例：`.../Isaac/Robots/...`）を指定するだけで利用できます。

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

ロボットアセットは Omniverse Nucleus サーバーに格納されています。`get_assets_root_path()` でアセットのルートパスを取得し、`stage_utils.add_reference_to_stage()` でアセットを USD Stage に読み込みます。

ただし、`add_reference_to_stage()` だけではロボットの 3D モデルと物理プロパティが Stage 上に配置されるだけで、関節の位置取得や速度指令といった**ロボットとしての制御**はできません。制御するには低レベルな USD API や PhysX API を直接操作する必要があります。

そこで、読み込んだロボットのプリムを `Articulation` クラスでラップします。`Articulation` クラスは既存のプリムを**参照するだけ**で、プリムのコピーや変換は行いません。同じ `/World/Fancy_Robot` プリムに対して、`get_dof_positions()` や `set_dof_velocity_targets()` などの高レベル API を提供する Python オブジェクトを作成します。

| 処理 | 役割 |
|---|---|
| `stage_utils.add_reference_to_stage()` | USD Stage 上にロボットのプリムを作成する |
| `Articulation(path)` | 既存のプリムを参照し、関節制御の高レベル API を提供する Python ラッパーを作成する |

まず必要なパッケージをインポートします：

```python linenums="1"
import carb
import isaacsim.core.experimental.utils.stage as stage_utils
from isaacsim.core.experimental.prims import Articulation
from isaacsim.examples.base.base_sample_experimental import BaseSample
from isaacsim.storage.native import get_assets_root_path
```

`setup_scene` で Jetbot をステージに追加します：

```python linenums="1"
        # Jetbot ロボットをステージに追加
        asset_path = assets_root_path + "/Isaac/Robots/NVIDIA/Jetbot/jetbot.usd"
        stage_utils.add_reference_to_stage(usd_path=asset_path, path="/World/Fancy_Robot")
```

`setup_post_load` で `Articulation` クラスでラップします：

```python linenums="1"
        # 制御のために Jetbot を Articulation クラスでラップ
        self._jetbot = Articulation("/World/Fancy_Robot")
```

コード全体は以下の通りです：

```python linenums="1" hl_lines="2-6 28-32 34-43"
# -- Isaac パッケージのインポートここから -- #
import carb
import isaacsim.core.experimental.utils.stage as stage_utils
from isaacsim.core.experimental.prims import Articulation
from isaacsim.examples.base.base_sample_experimental import BaseSample
from isaacsim.storage.native import get_assets_root_path

# -- Isaac パッケージのインポートここまで -- #


class HelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()

    def setup_scene(self):
        # 地面を追加
        ground_plane = stage_utils.add_reference_to_stage(
            usd_path=get_assets_root_path() + "/Isaac/Environments/Grid/default_environment.usd",
            path="/World/ground",
        )

        # Nucleus サーバーからアセットのルートパスを取得
        assets_root_path = get_assets_root_path()
        if assets_root_path is None:
            carb.log_error("Could not find nucleus server with /Isaac folder")
            return

        # -- Jetbot の追加ここから -- #
        # Jetbot ロボットをステージに追加
        asset_path = assets_root_path + "/Isaac/Robots/NVIDIA/Jetbot/jetbot.usd"
        stage_utils.add_reference_to_stage(usd_path=asset_path, path="/World/Fancy_Robot")
        # -- Jetbot の追加ここまで -- #

    async def setup_post_load(self):
        # -- アーティキュレーションここから -- #
        # 制御のために Jetbot を Articulation クラスでラップ
        self._jetbot = Articulation("/World/Fancy_Robot")
        # -- アーティキュレーションここまで -- #

        # Jetbot の情報を出力
        print("Number of DOFs: " + str(self._jetbot.num_dofs))
        print("DOF names: " + str(self._jetbot.dof_names))
        print("Joint Positions: " + str(self._jetbot.get_dof_positions().numpy()))
```

!!! info "参照（Reference）について"
    `add_reference_to_stage()` は USD ファイルを**参照（Reference）**として Stage に追加します。元のファイルへのリンクを保持するため、参照先のアセットが更新された場合も、ステージを開き直す（再読み込みする）タイミングでその変更が反映されます。USD の内容を Stage に直接コピーする方法もありますが、ロボットアセットの読み込みでは参照方式が一般的です。

コードを保存してシミュレーションを確認します：

1. **Ctrl+S** を押してコードを保存し、Isaac Sim をホットリロードします。
2. Hello World サンプル拡張機能のウィンドウを再度開きます。
3. **File > New From Stage Template > Empty** でワールドを新規作成してから、**LOAD** ボタンを押します。
4. Jetbot がシーンに表示され、ターミナルに自由度（DOF）数やジョイント名が出力されることを確認します。

シーンはロードされましたが、ロボットはまだ動きません。次のセクションでロボットを動かす方法を説明します。

### 物理ハンドルに関する重要なポイント

`Articulation` クラスの作成とプロパティ取得を `setup_scene` ではなく `setup_post_load` で行っていることに注目してください。

!!! warning "注意"
    アーティキュレーション（関節構造）のプロパティ（自由度、ジョイント位置など）は、物理ハンドルが初期化されるまでアクセスできません。`setup_post_load` は物理ステップ 1 回分が完了した後に呼ばれるため、これらの情報に安全にアクセスできます。アーティキュレーションを扱う処理は、必ず `setup_post_load` 以降で行ってください。

## ロボットを動かす

次に、Jetbot の車輪のジョイントにランダムな速度指令を送って動かします。

ジョイントへの速度指令には `Articulation` クラスの `set_dof_velocity_targets()` を使用します。これは物理エンジンに組み込まれた**暗黙的な PD コントローラ**への目標速度の設定です。

??? info "暗黙的な PD コントローラとは（クリックで展開）"
    実際のロボットでは、モータに「目標位置」や「目標速度」を指定すると、モータドライバ内の制御器が目標値と現在値の差に応じて電流（トルク）を計算し、関節を動かします。

    Isaac Sim の物理エンジン（PhysX）でも同様の仕組みが内部に組み込まれています。目標位置や目標速度を指定すると、PhysX が内部で **PD 制御（比例-微分制御）** を行い、目標に追従するために必要な力を自動計算します。

    $$
    F = K_p \cdot (x_{\text{target}} - x_{\text{current}}) + K_d \cdot (\dot{x}_{\text{target}} - \dot{x}_{\text{current}})
    $$

    この PD コントローラはユーザーが明示的に実装するのではなく、物理エンジンに**暗黙的に**組み込まれているため、「暗黙的な PD コントローラ」と呼ばれます。

毎物理ステップで速度指令を送るために、チュートリアル 1 で学んだ `SimulationManager` の物理演算コールバックを使用します。

`SimulationManager` をインポートします：

```python linenums="1"
from isaacsim.core.simulation_manager import SimulationManager
```

コールバックを登録します：

```python linenums="1"
        # 毎物理ステップでアクションを送るための物理演算コールバックを登録
        from isaacsim.core.simulation_manager.impl.isaac_events import IsaacEvents

        self._physics_callback_id = SimulationManager.register_callback(
            self.send_robot_actions, IsaacEvents.POST_PHYSICS_STEP
        )
```

指令を送る関数を定義します：

```python linenums="1"
    def send_robot_actions(self, dt, context):
        # 車輪のジョイントにランダムな目標速度を適用する
        # Jetbot は 2 つの DOF を持つ: left_wheel_joint と right_wheel_joint
        random_velocities = 5 * np.random.rand(1, 2)  # 形状: (1, num_dofs)
        self._jetbot.set_dof_velocity_targets(random_velocities)
```

コード全体は以下の通りです：

```python linenums="1" hl_lines="6-9 17 40-47 49-56 58-62"
import carb
import isaacsim.core.experimental.utils.stage as stage_utils
import numpy as np
from isaacsim.core.experimental.prims import Articulation

# -- SimulationManager のインポートここから -- #
from isaacsim.core.simulation_manager import SimulationManager

# -- SimulationManager のインポートここまで -- #
from isaacsim.examples.base.base_sample_experimental import BaseSample
from isaacsim.storage.native import get_assets_root_path


class HelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        self._physics_callback_id = None

    def setup_scene(self):
        # 地面を追加
        ground_plane = stage_utils.add_reference_to_stage(
            usd_path=get_assets_root_path() + "/Isaac/Environments/Grid/default_environment.usd",
            path="/World/ground",
        )

        # Nucleus サーバーからアセットのルートパスを取得
        assets_root_path = get_assets_root_path()
        if assets_root_path is None:
            carb.log_error("Could not find nucleus server with /Isaac folder")
            return

        # Jetbot ロボットをステージに追加
        asset_path = assets_root_path + "/Isaac/Robots/NVIDIA/Jetbot/jetbot.usd"
        stage_utils.add_reference_to_stage(usd_path=asset_path, path="/World/Fancy_Robot")

    async def setup_post_load(self):
        # 制御のために Jetbot を Articulation クラスでラップ
        self._jetbot = Articulation("/World/Fancy_Robot")

        # -- コールバック登録ここから -- #
        # 毎物理ステップでアクションを送るための物理演算コールバックを登録
        from isaacsim.core.simulation_manager.impl.isaac_events import IsaacEvents

        self._physics_callback_id = SimulationManager.register_callback(
            self.send_robot_actions, IsaacEvents.POST_PHYSICS_STEP
        )
        # -- コールバック登録ここまで -- #

    # -- アクション送信ここから -- #
    def send_robot_actions(self, dt, context):
        # 車輪のジョイントにランダムな目標速度を適用する
        # Jetbot は 2 つの DOF を持つ: left_wheel_joint と right_wheel_joint
        random_velocities = 5 * np.random.rand(1, 2)  # 形状: (1, num_dofs)
        self._jetbot.set_dof_velocity_targets(random_velocities)

    # -- アクション送信ここまで -- #

    def physics_cleanup(self):
        # 拡張機能のアンロード時にコールバックをクリーンアップ
        if self._physics_callback_id is not None:
            SimulationManager.deregister_callback(self._physics_callback_id)
            self._physics_callback_id = None
```

!!! note "速度指令の配列形状"
    experimental API はバッチ処理を前提としているため、`set_dof_velocity_targets()` に渡す配列の形状は `(オブジェクト数, DOF 数)` になります。Jetbot 1 台の場合は `(1, 2)` の配列（左右の車輪）を渡します。

コードを保存してシミュレーションを確認します：

1. **Ctrl+S** を押してコードを保存し、Isaac Sim をホットリロードします。
2. **File > New From Stage Template > Empty** でワールドを新規作成してから、**LOAD** ボタンを押します。
3. Jetbot がランダムな速度で動き回る様子を確認します。

![Jetbot がランダムに動き回る様子](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/core_api_tutorials_2_2.webp)

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
    コールバックの引数 `dt` を毎ステップ累積して経過時間を計算し、条件分岐で停止させます。

## 特定のジョイントを制御する

ジョイントは名前またはインデックスを指定して個別に制御することもできます。車輪ジョイントのインデックスを取得し、特定のジョイントにだけ速度を適用する方法を見てみましょう。

車輪ジョイントのインデックスを取得します：

```python linenums="1"
        # 利用可能な DOF 名を出力
        print("Available DOFs:", self._jetbot.dof_names)

        # 特定の車輪ジョイントのインデックスを取得
        self._wheel_indices = self._jetbot.get_dof_indices(["left_wheel_joint", "right_wheel_joint"]).numpy()
        print("Wheel indices:", self._wheel_indices)
```

インデックスを指定して車輪速度を設定します：

```python linenums="1"
        # 特定の DOF インデックスに目標速度を適用
        wheel_velocities = np.array([[10.0, 10.0]])  # 両輪同速 = 前進
        self._jetbot.set_dof_velocity_targets(wheel_velocities, dof_indices=self._wheel_indices)
```

コード全体は以下の通りです：

```python linenums="1" hl_lines="31-38 48-52"
import carb
import isaacsim.core.experimental.utils.stage as stage_utils
import numpy as np
from isaacsim.core.experimental.prims import Articulation
from isaacsim.core.simulation_manager import SimulationManager
from isaacsim.examples.base.base_sample_experimental import BaseSample
from isaacsim.storage.native import get_assets_root_path


class HelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        self._physics_callback_id = None

    def setup_scene(self):
        # 地面を追加
        ground_plane = stage_utils.add_reference_to_stage(
            usd_path=get_assets_root_path() + "/Isaac/Environments/Grid/default_environment.usd",
            path="/World/ground",
        )

        # Jetbot ロボットをステージに追加
        assets_root_path = get_assets_root_path()
        asset_path = assets_root_path + "/Isaac/Robots/NVIDIA/Jetbot/jetbot.usd"
        stage_utils.add_reference_to_stage(usd_path=asset_path, path="/World/Fancy_Robot")

    async def setup_post_load(self):
        # Jetbot を Articulation クラスでラップ
        self._jetbot = Articulation("/World/Fancy_Robot")

        # -- インデックス取得ここから -- #
        # 利用可能な DOF 名を出力
        print("Available DOFs:", self._jetbot.dof_names)

        # 特定の車輪ジョイントのインデックスを取得
        self._wheel_indices = self._jetbot.get_dof_indices(["left_wheel_joint", "right_wheel_joint"]).numpy()
        print("Wheel indices:", self._wheel_indices)
        # -- インデックス取得ここまで -- #

        # 物理演算コールバックを登録
        from isaacsim.core.simulation_manager.impl.isaac_events import IsaacEvents

        self._physics_callback_id = SimulationManager.register_callback(
            self.send_robot_actions, IsaacEvents.POST_PHYSICS_STEP
        )

    def send_robot_actions(self, dt, context):
        # -- 車輪速度の設定ここから -- #
        # 特定の DOF インデックスに目標速度を適用
        wheel_velocities = np.array([[10.0, 10.0]])  # 両輪同速 = 前進
        self._jetbot.set_dof_velocity_targets(wheel_velocities, dof_indices=self._wheel_indices)
        # -- 車輪速度の設定ここまで -- #

    def physics_cleanup(self):
        if self._physics_callback_id is not None:
            SimulationManager.deregister_callback(self._physics_callback_id)
            self._physics_callback_id = None
```

Jetbot のように全ジョイントが制御対象の場合はインデックス指定は必須ではありませんが、多数のジョイントを持つロボット（マニピュレータなど）で一部のジョイントだけを制御したい場合に、この方法が役立ちます。

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. `stage_utils.add_reference_to_stage()` による**ロボットのステージへの追加**
2. **Articulation クラス**でロボットプリムをラップし、高レベル API でアクセスする方法
3. `set_dof_velocity_targets()` による**速度制御**
4. **SimulationManager** を使った物理演算コールバックの登録
5. ジョイント名・インデックスによる**特定ジョイントの制御**

## 次のステップ

次のチュートリアル「[コントローラの追加](03_adding_a_controller.md)」に進み、ロボットにコントローラを追加してより高度な動作を実現する方法を学びましょう。

!!! note "公式チュートリアルでの次のステップ"
    「コントローラの追加」は Isaac Sim 6.0 の公式ドキュメントからは削除されたページで、本サイトでは 5.1.0 時点の内容をもとにした独自解説として保持しています。公式のチュートリアルシリーズでは、次は「[マニピュレータロボットの追加](04_adding_a_manipulator_robot.md)」に進みます。

!!! tip "さらに学ぶには"
    Isaac Sim には車輪型ロボットやマニピュレータ向けの拡張機能（`isaacsim.robot.experimental.wheeled_robots`、`isaacsim.robot.experimental.manipulators.examples` など）も用意されています。`standalone_examples/api/isaacsim.robot.experimental.manipulators/franka` や `standalone_examples/api/isaacsim.robot.experimental.manipulators/universal_robots/` にあるスタンドアロンサンプルも参考にしてください。
