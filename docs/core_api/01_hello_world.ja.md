---
title: Hello World
---

# Hello World

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます:

- Core API（experimental）を使って USD ステージを操作する方法
- Stage に剛体(rigid body)を追加し、NVIDIA Isaac Sim で Python を使用してシミュレーションする方法
- Extension Workflow と Standalone Workflow の違い

!!! note "USD の基本用語：ステージとプリム"
    Isaac Sim のシーンは **USD（Universal Scene Description）** という形式で管理されます。チュートリアル全体で頻出する次の 2 つの用語を最初に押さえておきましょう。

    - **ステージ（Stage）** … シーン全体を表す入れ物です。エディタの Stage パネルに表示されるツリーが、現在のステージの中身です。
    - **プリム（Prim）** … ステージ上に配置される個々のオブジェクト（ツリーのノード）です。ロボット・立方体・ライト・カメラなどはすべてプリムで、`/World/fancy_cube` のような**パス**で一意に識別されます。

## はじめに

### 前提条件

- このチュートリアルには、Python および非同期プログラミングの中級レベルの知識が必要です。
- チュートリアルを開始する前に、[Visual Studio Code](https://code.visualstudio.com/download) をダウンロードしてインストールしてください。
- チュートリアルを開始する前に、[クイックチュートリアル](https://docs.isaacsim.omniverse.nvidia.com/latest/introduction/quickstart_index.html#isaac-sim-intro-quickstart-series)を確認してください。

!!! note "Isaac Sim 6.0 での Core API の刷新"
    Isaac Sim 6.0 では、従来の `isaacsim.core.api`（World / Scene ベースの API）が**非推奨（deprecated）**となり、Core API チュートリアルは `isaacsim.core.experimental.*` と `isaacsim.core.simulation_manager` を使う内容に刷新されました。本ページも刷新後の内容に対応しています。

### Workflow

Isaac Sim はより大規模なソリューションの構成要素であり、単独でも使用可能です。そのため、同じ目的を達成するために複数の方法が存在します。これらの異なる方法を「Workflow」と呼びます。

??? info "3つの Workflow の詳細（クリックで展開）"

    | Workflow | 主な特徴 | 推奨用途 |
    |---|---|---|
    | **GUI** | 視覚的で直感的なツール | ワールド構築、ロボット組み立て、センサー取り付け、OmniGraphs によるビジュアルプログラミング |
    | **Extension** | 非同期実行、ホットリロード、適応型物理演算ステップ | Python スニペットのテスト、インタラクティブ GUI 構築、リアルタイム応答が必要なアプリケーション |
    | **Standalone** | 物理演算・レンダリングのタイミング制御、ヘッドレス実行 | 強化学習の大規模トレーニング、体系的なワールド生成 |

    - **GUI Workflow**: コードを書かずに、GUIの操作だけでシミュレーション環境を構築できます。
    - **Extension Workflow**: Isaac Sim 内で Python スクリプトを拡張機能として実行します。ホットリロード（コード保存で即反映）が使えるため、開発効率が高いです。
    - **Standalone Workflow**: Isaac Sim を Python スクリプトから直接起動します。物理演算やレンダリングのタイミングを完全に制御できます。

以降のチュートリアルでは主に **Extension Workflow** を用いて説明しますが、Extension Workflow で生成する物体や各種設定は GUI からも行えますし、スクリプトを書き換えることで Standalone Workflow に置き換えることも可能です。

### Hello World サンプルを開く

まず、Hello World サンプルを開きます。

1. **Windows > Examples > Robotics Examples** をアクティブにして、Robotics Examples タブを開きます。<br>
   ![Robotics Examplesタブの場所](images/01_robotics_example_place.png)

2. **Robotics Examples > General > Hello World** をクリックします。<br>
   ![Hello Worldの場所](images/02_hello_world_place.png)

3. ワークスペースに Hello World サンプル拡張機能のウィンドウが表示されていることを確認してください。<br>
   ![Hello Worldウィンドウ](images/03_hello_world_window.png)

4. **Open Source Code** ボタンをクリックし、Visual Studio Code で編集可能なソースコードを起動します。<br>
   ![ソースコードを開くボタン](images/04_open_source_code.png)

5. **Open Folder** ボタンをクリックし、サンプルファイルを含むディレクトリを開きます。<br>
   ![フォルダを開くボタン](images/05_open_folder.png)

このフォルダには以下の3つのファイルが含まれています：

- `hello_world.py` — アプリケーションのロジック部分
- `hello_world_extension.py` — アプリケーションの UI 要素
- `__init__.py`

### サンプルの動作確認

試しに Hello World サンプルをロードしてみましょう。

1. **File > New From Stage Template > Empty** をクリックして新しいステージを作成し、保存確認で **Don't Save** をクリックします。<br>
   ![新規ステージ作成](images/07_new_empty_world.png)
   ![保存しないを選択](images/08_close_options.png)

2. **LOAD** ボタンをクリックしてワールドを読み込みます。<br>
   ![LOADボタン](images/06_load_button.png)

3. **Open Source Code** ボタンをクリックし、`hello_world.py` を開いて **Ctrl+S** を押してホットリロードします。ワークスペースから Hello World のウィンドウが消えます（拡張機能が再起動されたため）。<br>
   ![ソースコードを開くボタン](images/04_open_source_code.png)

4. Robotics Examples メニューを再度開き、**LOAD** ボタンをクリックします。

それでは、この Hello World サンプルに追記する形で進めていきましょう。

## コード概要

ここからは、`hello_world.py` のコードを段階的に拡張していきます。まず、サンプルの基本構造を確認しましょう。

この例は `BaseSample` を継承しています。`BaseSample` は、ロボティクス拡張アプリケーションの基本設定を行うボイラープレートクラスで、以下の機能を提供します：

1. ボタン操作でアセットをステージに読み込む
2. 新しいステージ作成時にステージをクリアする
3. オブジェクトをデフォルト状態にリセットする
4. ホットリロードを処理する

まずは必要なパッケージをインポートします：

```python linenums="1"
import isaacsim.core.experimental.utils.stage as stage_utils
from isaacsim.examples.base.base_sample_experimental import BaseSample
from isaacsim.storage.native import get_assets_root_path
```

`setup_scene` では、`stage_utils.add_reference_to_stage()` を使って地面のアセットをステージに直接追加します：

```python linenums="1"
    # シーンにアセットを初回配置するための関数
    def setup_scene(self):
        # 地面をステージに直接追加する
        ground_plane = stage_utils.add_reference_to_stage(
            usd_path=get_assets_root_path() + "/Isaac/Environments/Grid/default_environment.usd",
            path="/World/ground",
        )
```

コード全体は以下の通りです：

```python linenums="1" hl_lines="2-4 14-20"
# -- Isaac Sim パッケージのインポート -- #
import isaacsim.core.experimental.utils.stage as stage_utils
from isaacsim.examples.base.base_sample_experimental import BaseSample
from isaacsim.storage.native import get_assets_root_path

# -- インポートここまで -- #


class HelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()

    # -- シーンのセットアップ -- #
    # シーンにアセットを初回配置するための関数
    def setup_scene(self):
        # 地面をステージに直接追加する
        ground_plane = stage_utils.add_reference_to_stage(
            usd_path=get_assets_root_path() + "/Isaac/Environments/Grid/default_environment.usd",
            path="/World/ground",
        )

    # -- シーンのセットアップここまで -- #
```

## 重要な概念

Core API（experimental）を使う上で押さえておきたい 3 つの概念があります：

| 概念 | 説明 |
|---|---|
| **Stage ユーティリティ** | `stage_utils` モジュールは、参照の追加・プリムの作成・ステージ階層の管理など、USD ステージを直接操作する関数を提供します |
| **プリムクラス** | `RigidPrim`、`GeomPrim`、`Articulation` などのプリムラッパークラスにより、物理機能を持つ USD プリムを直接制御できます |
| **SimulationManager** | コールバックやシミュレーションイベントを扱うクラスで、各種シミュレーションイベントに対するコールバックの登録・解除メソッドを提供します |

## シーンへの追加

Python API を使用して、シーンに剛体として立方体を追加します。Core API では、**まずジオメトリ（形状）を作成し、それにコリジョンと剛体のプロパティを適用する**という流れになります。

必要なパッケージをインポートします：

```python linenums="1"
import isaacsim.core.experimental.utils.stage as stage_utils
import numpy as np
from isaacsim.core.experimental.materials import PreviewSurfaceMaterial
from isaacsim.core.experimental.objects import Cube
from isaacsim.core.experimental.prims import GeomPrim, RigidPrim
from isaacsim.examples.base.base_sample_experimental import BaseSample
from isaacsim.storage.native import get_assets_root_path
```

立方体を追加する処理は以下の通りです：

```python linenums="1"
        # 立方体用の青いビジュアルマテリアルを作成
        visual_material = PreviewSurfaceMaterial("/World/Materials/blue")
        visual_material.set_input_values("diffuseColor", [0.0, 0.0, 1.0])

        # 立方体のジオメトリを作成
        self._cube_shape = Cube(
            paths="/World/fancy_cube",
            positions=np.array([[0.0, 0.0, 1.0]]),  # 地面から 1m 上の初期位置
            sizes=[1.0],
            scales=np.array([[0.5015, 0.5015, 0.5015]]),  # 立方体のスケール
            reset_xform_op_properties=True,
        )

        # コリジョン API を適用して物理的な衝突判定を有効化
        GeomPrim(paths=self._cube_shape.paths, apply_collision_apis=True)

        # 剛体にする（物理に反応する動的オブジェクト）
        self._cube = RigidPrim(paths=self._cube_shape.paths)

        # 青いマテリアルを適用
        self._cube_shape.apply_visual_materials(visual_material)
```

コード全体は以下の通りです：

```python linenums="1" hl_lines="2-8 24-45"
# -- Isaac Sim パッケージのインポート -- #
import isaacsim.core.experimental.utils.stage as stage_utils
import numpy as np
from isaacsim.core.experimental.materials import PreviewSurfaceMaterial
from isaacsim.core.experimental.objects import Cube
from isaacsim.core.experimental.prims import GeomPrim, RigidPrim
from isaacsim.examples.base.base_sample_experimental import BaseSample
from isaacsim.storage.native import get_assets_root_path

# -- インポートここまで -- #


class HelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()

    def setup_scene(self):
        # 地面を追加
        ground_plane = stage_utils.add_reference_to_stage(
            usd_path=get_assets_root_path() + "/Isaac/Environments/Grid/default_environment.usd",
            path="/World/ground",
        )

        # -- 立方体の作成とマテリアル適用 -- #
        # 立方体用の青いビジュアルマテリアルを作成
        visual_material = PreviewSurfaceMaterial("/World/Materials/blue")
        visual_material.set_input_values("diffuseColor", [0.0, 0.0, 1.0])

        # 立方体のジオメトリを作成
        self._cube_shape = Cube(
            paths="/World/fancy_cube",
            positions=np.array([[0.0, 0.0, 1.0]]),  # 地面から 1m 上の初期位置
            sizes=[1.0],
            scales=np.array([[0.5015, 0.5015, 0.5015]]),  # 立方体のスケール
            reset_xform_op_properties=True,
        )

        # コリジョン API を適用して物理的な衝突判定を有効化
        GeomPrim(paths=self._cube_shape.paths, apply_collision_apis=True)

        # 剛体にする（物理に反応する動的オブジェクト）
        self._cube = RigidPrim(paths=self._cube_shape.paths)

        # 青いマテリアルを適用
        self._cube_shape.apply_visual_materials(visual_material)
        # -- 立方体の作成とマテリアル適用ここまで -- #
```

コードを保存してシミュレーションを確認します：

1. **Ctrl+S** を押してコードを保存し、Isaac Sim をホットリロードします。
2. Hello World サンプル拡張機能のウィンドウを再度開きます。
3. **LOAD** ボタンをクリックします。
4. シミュレーションが自動的に開始され、動的キューブが落下する様子を確認します。

![動的キューブの落下シミュレーション](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/core_api_tutorials_1_1.webp)

!!! note "注釈"
    コードを編集するたびに、**Ctrl+S** を押して保存し、Isaac Sim をホットリロードしてください。

### プリムクラスの理解

experimental API では、物理が有効なオブジェクトをレイヤー構造で作成します：

| クラス | 役割 |
|---|---|
| `Cube`（その他の形状クラス） | USD ステージ上にビジュアルジオメトリを作成する |
| `GeomPrim` | ジオメトリをラップし、物理的な衝突判定のためのコリジョン API を適用できる |
| `RigidPrim` | 剛体ダイナミクスを追加し、重力や力に反応するオブジェクトにする |

このモジュール化されたアプローチにより、細かい制御が可能です。たとえば、静的なコライダー（`RigidPrim` なしの `GeomPrim`）や、完全に動的なオブジェクト（両方を適用）を作り分けられます。

## オブジェクトのプロパティの確認

次に、キューブのワールド座標と速度を出力してみます。

ここで新しいメソッド `setup_post_load` が登場します。`setup_scene` との違いは以下の通りです：

| メソッド | 呼ばれるタイミング | 用途 |
|---|---|---|
| `setup_scene` | 空のステージから初回ロード時のみ | アセットの配置 |
| `setup_post_load` | **LOAD** ボタン押下後に毎回 | 物理ハンドルが有効になった後の初期化処理 |

`setup_post_load` は `setup_scene` と物理ステップ 1 回分が完了した後に呼ばれるため、オブジェクトの座標・速度などの物理プロパティを取得できます。

!!! note "物理ハンドルとは"
    **物理ハンドル**は、物理エンジン（PhysX）側で生成される、シミュレーション対象を読み書きするための内部参照です。ステージにプリムを置いただけでは物理エンジン側の実体はまだ存在せず、物理ステップの開始時に初期化されます。物理ハンドルが有効になって初めて、座標・速度・関節角度（アーティキュレーション：関節構造のプロパティ）などへアクセスできます。

プロパティの取得部分は以下のように書きます：

```python linenums="1"
        # RigidPrim のメソッドでキューブのプロパティを取得
        positions, orientations = self._cube.get_world_poses()
        # get_velocities() は (linear_velocities, angular_velocities) のタプルを返す
        linear_velocities, angular_velocities = self._cube.get_velocities()

        # warp 配列から numpy に変換して出力
        # 注意: experimental API はバッチ化された結果を返す（単一オブジェクトでも）
        print("Cube position is : " + str(positions.numpy()[0]))
        print("Cube's orientation is : " + str(orientations.numpy()[0]))
        print("Cube's linear velocity is : " + str(linear_velocities.numpy()[0]))
```

!!! note "warp 配列とバッチ化された結果"
    experimental API は、結果を **warp 配列**（GPU 対応の配列型）としてバッチ形式で返します。`.numpy()` で numpy 配列に変換し、単一オブジェクトを扱う場合は `[0]` で最初（かつ唯一）の要素を取り出してください。

コード全体は以下の通りです：

```python linenums="1" hl_lines="39-53"
import isaacsim.core.experimental.utils.stage as stage_utils
import numpy as np
from isaacsim.core.experimental.materials import PreviewSurfaceMaterial
from isaacsim.core.experimental.objects import Cube
from isaacsim.core.experimental.prims import GeomPrim, RigidPrim
from isaacsim.examples.base.base_sample_experimental import BaseSample
from isaacsim.storage.native import get_assets_root_path


class HelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()

    def setup_scene(self):
        # 地面を追加
        ground_plane = stage_utils.add_reference_to_stage(
            usd_path=get_assets_root_path() + "/Isaac/Environments/Grid/default_environment.usd",
            path="/World/ground",
        )

        # 立方体用の青いビジュアルマテリアルを作成
        visual_material = PreviewSurfaceMaterial("/World/Materials/blue")
        visual_material.set_input_values("diffuseColor", [0.0, 0.0, 1.0])

        # 立方体のジオメトリを作成
        self._cube_shape = Cube(
            paths="/World/fancy_cube",
            positions=np.array([[0.0, 0.0, 1.0]]),
            sizes=[1.0],
            scales=np.array([[0.5015, 0.5015, 0.5015]]),
            reset_xform_op_properties=True,
        )

        # コリジョンと剛体を適用
        GeomPrim(paths=self._cube_shape.paths, apply_collision_apis=True)
        self._cube = RigidPrim(paths=self._cube_shape.paths)
        self._cube_shape.apply_visual_materials(visual_material)

    # LOAD ボタン押下後に呼ばれる
    # setup_scene と物理ステップ1回分が完了した後に1回だけ呼ばれ、
    # 物理プロパティの取得に必要な物理ハンドルが有効になっている
    async def setup_post_load(self):
        # -- プロパティの取得ここから -- #
        # RigidPrim のメソッドでキューブのプロパティを取得
        positions, orientations = self._cube.get_world_poses()
        # get_velocities() は (linear_velocities, angular_velocities) のタプルを返す
        linear_velocities, angular_velocities = self._cube.get_velocities()

        # warp 配列から numpy に変換して出力
        # 注意: experimental API はバッチ化された結果を返す（単一オブジェクトでも）
        print("Cube position is : " + str(positions.numpy()[0]))
        print("Cube's orientation is : " + str(orientations.numpy()[0]))
        print("Cube's linear velocity is : " + str(linear_velocities.numpy()[0]))
        # -- プロパティの取得ここまで -- #
```

## シミュレーション中のオブジェクトプロパティの継続的検査

物理演算ステップが実行されるたびに、キューブの姿勢と速度を出力します。

[Workflow](#workflow) で述べたように、**Extension Workflow** ではアプリケーションは非同期で実行されており、物理演算のステップタイミングを直接制御できません。ただし、**物理演算コールバック**を登録することで、特定のイベントの前後に任意の処理を実行できます。コールバックの登録には `SimulationManager` を使用します。

まず `SimulationManager` をインポートします：

```python linenums="1"
from isaacsim.core.simulation_manager import SimulationManager
```

`SimulationManager` を使って物理演算コールバックを登録します：

```python linenums="1"
        # SimulationManager を使って物理演算コールバックを登録
        from isaacsim.core.simulation_manager.impl.isaac_events import IsaacEvents

        self._physics_callback_id = SimulationManager.register_callback(
            self.print_cube_info, IsaacEvents.POST_PHYSICS_STEP
        )
```

クリーンアップ時にはコールバックを解除します：

```python linenums="1"
        # 拡張機能のアンロード時にコールバックをクリーンアップ
        if self._physics_callback_id is not None:
            SimulationManager.deregister_callback(self._physics_callback_id)
            self._physics_callback_id = None
```

コード全体は以下の通りです：

```python linenums="1" hl_lines="7-10 18 46-52 55-63 65-71"
import isaacsim.core.experimental.utils.stage as stage_utils
import numpy as np
from isaacsim.core.experimental.materials import PreviewSurfaceMaterial
from isaacsim.core.experimental.objects import Cube
from isaacsim.core.experimental.prims import GeomPrim, RigidPrim

# -- SimulationManager の読み込みここから -- #
from isaacsim.core.simulation_manager import SimulationManager

# -- SimulationManager の読み込みここまで -- #
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

        # 立方体用の青いビジュアルマテリアルを作成
        visual_material = PreviewSurfaceMaterial("/World/Materials/blue")
        visual_material.set_input_values("diffuseColor", [0.0, 0.0, 1.0])

        # 立方体のジオメトリを作成
        self._cube_shape = Cube(
            paths="/World/fancy_cube",
            positions=np.array([[0.0, 0.0, 1.0]]),
            sizes=[1.0],
            scales=np.array([[0.5015, 0.5015, 0.5015]]),
            reset_xform_op_properties=True,
        )

        # コリジョンと剛体を適用
        GeomPrim(paths=self._cube_shape.paths, apply_collision_apis=True)
        self._cube = RigidPrim(paths=self._cube_shape.paths)
        self._cube_shape.apply_visual_materials(visual_material)

    async def setup_post_load(self):
        # -- コールバック登録ここから -- #
        # SimulationManager を使って物理演算コールバックを登録
        from isaacsim.core.simulation_manager.impl.isaac_events import IsaacEvents

        self._physics_callback_id = SimulationManager.register_callback(
            self.print_cube_info, IsaacEvents.POST_PHYSICS_STEP
        )
        # -- コールバック登録ここまで -- #

    # 物理演算コールバック関数 - 各物理ステップの後に呼ばれる
    # dt（デルタタイム）と context を引数に取る
    def print_cube_info(self, dt, context):
        positions, orientations = self._cube.get_world_poses()
        linear_velocities, angular_velocities = self._cube.get_velocities()

        print("Cube position is : " + str(positions.numpy()[0]))
        print("Cube's orientation is : " + str(orientations.numpy()[0]))
        print("Cube's linear velocity is : " + str(linear_velocities.numpy()[0]))

    def physics_cleanup(self):
        # -- コールバック解除ここから -- #
        # 拡張機能のアンロード時にコールバックをクリーンアップ
        if self._physics_callback_id is not None:
            SimulationManager.deregister_callback(self._physics_callback_id)
            self._physics_callback_id = None
        # -- コールバック解除ここまで -- #
```

!!! note "コールバックの登録と解除はセットで"
    `SimulationManager.register_callback()` は登録 ID を返します。拡張機能のアンロード時やシミュレーションの停止時にコールバックが残ったままにならないよう、`physics_cleanup` で `deregister_callback()` を呼んで解除するのが定型パターンです。

## ワールドのリセット

シミュレーション中にオブジェクトを初期状態に戻したい場合は、**RESET** ボタンを使用します。リセット後に再度初期化が必要な処理は `setup_pre_reset` および `setup_post_reset` コールバックで行えます。

## サンプルをスタンドアロンアプリケーションに変換

!!! note "注釈"
    Windows では `python.sh` の代わりに `python.bat` を使用してください。

[Workflow](#workflow) で述べたように、**Standalone Workflow** では Python から Isaac Sim を直接起動します。

Standalone スクリプトは Isaac Sim 同梱の Python インタプリタ（`python.sh`）で実行する必要があります。このインタプリタは Isaac Sim のインストールディレクトリ直下にあります。

スクリプトの配置場所は任意ですが、Hello World サンプルと同じ `user_examples` ディレクトリに置くのが分かりやすいです：

```
<Isaac Sim インストールディレクトリ>/
├── python.sh                    # Isaac Sim 同梱の Python インタプリタ
└── exts/
    └── isaacsim.examples.interactive/
        └── isaacsim/examples/interactive/
            └── user_examples/
                └── my_application.py   # ← ここに作成
```

!!! tip "ヒント"
    `python.sh`（Windows では `python.bat`）は Isaac Sim に必要なすべての依存関係を含む専用の Python 環境です。システムにインストールされた Python で実行するとモジュールが見つからずエラーになります。

新しい `my_application.py` ファイルを上記のディレクトリに作成し、以下のコードを記述します：

```python linenums="1" hl_lines="1-5 41-43 46-48 58 60"
# Isaac Sim を他のインポートより先に起動する（Standalone の必須手順）
# Standalone アプリケーションの最初の2行は必ずこの形式にする
from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": False})  # headless=True でGUI無しでも実行可能

# ここから Isaac Sim のモジュールをインポートできる
import isaacsim.core.experimental.utils.stage as stage_utils
import numpy as np
import omni.timeline
from isaacsim.core.experimental.materials import PreviewSurfaceMaterial
from isaacsim.core.experimental.objects import Cube
from isaacsim.core.experimental.prims import GeomPrim, RigidPrim
from isaacsim.core.simulation_manager import SimulationManager
from isaacsim.storage.native import get_assets_root_path

# 地面を追加
ground_plane = stage_utils.add_reference_to_stage(
    usd_path=get_assets_root_path() + "/Isaac/Environments/Grid/default_environment.usd",
    path="/World/ground",
)

# 立方体用の青いビジュアルマテリアルを作成
visual_material = PreviewSurfaceMaterial("/World/Materials/blue")
visual_material.set_input_values("diffuseColor", [0.0, 0.0, 1.0])

# 立方体のジオメトリを作成
cube_shape = Cube(
    paths="/World/fancy_cube",
    positions=np.array([[0.0, 0.0, 1.0]]),
    sizes=[1.0],
    scales=np.array([[0.5, 0.5, 0.5]]),
    reset_xform_op_properties=True,
)

# コリジョンと剛体を適用
GeomPrim(paths=cube_shape.paths, apply_collision_apis=True)
cube = RigidPrim(paths=cube_shape.paths)
cube_shape.apply_visual_materials(visual_material)

# タイムライン（物理シミュレーション）を開始
omni.timeline.get_timeline_interface().play()
simulation_app.update()

# シミュレーションループを実行
for i in range(50):
    # 物理シミュレーションが実行中の場合のみプロパティを取得
    if SimulationManager.is_simulating():
        positions, orientations = cube.get_world_poses()
        linear_velocities, angular_velocities = cube.get_velocities()

        # ターミナルに出力される
        print("Cube position is : " + str(positions.numpy()[0]))
        print("Cube's orientation is : " + str(orientations.numpy()[0]))
        print("Cube's linear velocity is : " + str(linear_velocities.numpy()[0]))

    # アプリを1ステップ進める（物理演算＋レンダリング）
    simulation_app.update()

simulation_app.close()  # Isaac Sim を終了
```

Isaac Sim のインストールディレクトリに移動し、以下のコマンドでスクリプトを実行します：

```bash
cd <Isaac Sim インストールディレクトリ>
./python.sh ./exts/isaacsim.examples.interactive/isaacsim/examples/interactive/user_examples/my_application.py
```

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. ステージを直接操作する **Core API**（experimental）の概要
2. `stage_utils` による**ステージへのアセット追加**
3. `Cube`・`GeomPrim`・`RigidPrim` による**動的オブジェクトの作成**
4. **SimulationManager** による物理演算コールバックの登録
5. プリムラッパーのメソッドによる**物理プロパティの取得**
6. Standalone アプリケーションへの変換

## 次のステップ

次のチュートリアル「[Hello Robot](02_hello_robot.md)」に進み、シミュレーションにロボットを追加する方法を学びましょう。

!!! note "注釈"
    次のチュートリアルでは主に Extension Workflow を使用して開発を進めます。ただし、本チュートリアルで扱った内容を踏まえれば、他の Workflow への変換も同様の手順で行えます。
