---
title: Hello World
---

# Hello World

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます:

- Core API で定義される World と Scene の作成方法
- Stage に剛体(rigid body)を追加し、NVIDIA Isaac Sim で Python を使用してシミュレーションする方法
- Extension Workflow と Standalone Workflow の違い

## はじめに

### 前提条件

- このチュートリアルには、Python および非同期プログラミングの中級レベルの知識が必要です。
- チュートリアルを開始する前に、[Visual Studio Code](https://code.visualstudio.com/download) をダウンロードしてインストールしてください。
- チュートリアルを開始する前に、[クイックチュートリアル](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/introduction/quickstart_index.html#isaac-sim-intro-quickstart-series)を確認してください。

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

1. **LOAD** ボタンをクリックしてワールドを読み込みます。<br>
   ![LOADボタン](images/06_load_button.png)

2. 読み込んだワールドを消して最初の状態に戻すには、**File > New From Stage Template > Empty** をクリックして新しいステージを作成し、保存確認で **Don't Save** をクリックします。<br>
   ![新規ステージ作成](images/07_new_empty_world.png)
   ![保存しないを選択](images/08_close_options.png)

3. **LOAD** ボタンをクリックしてワールドを再度読み込みます。

4. **Open Source Code** ボタンをクリックし、`hello_world.py` を開いて **Ctrl+S** を押してホットリロードします。ワークスペースから Hello World のウィンドウが消えます（拡張機能が再起動されたため）。<br>
   ![ソースコードを開くボタン](images/04_open_source_code.png)

5. Robotics Examples メニューを再度開き、**LOAD** ボタンをクリックします。

それでは、この Hello World サンプルに追記する形で進めていきましょう。

## コード概要

ここからは、`hello_world.py` のコードを段階的に拡張していきます。まず、サンプルの基本構造を確認しましょう。

この例は `BaseSample` を継承しています。`BaseSample` は、ロボティクス拡張アプリケーションの基本設定を行うボイラープレートクラスで、以下の機能を提供します：

1. ボタン操作でアセットと共にワールドを読み込む
2. 新しいステージ作成時にワールドをクリアする
3. ワールド内のオブジェクトをデフォルト状態にリセットする
4. ホットリロードを処理する

**World** は、シミュレータとモジュール化された方法で対話するための中核クラスです。コールバックの追加、物理演算のステップ実行、シーンのリセットなど、多くのイベントを管理します。

**Scene** は World が内部に持つインスタンスで、USD Stage 内のシミュレーションアセットを管理します。アセットの追加・操作・検査・リセットのための簡易 API を提供します。

```python linenums="1" hl_lines="1 12-14"
from isaacsim.examples.interactive.base_sample import BaseSample # ロボティクス拡張アプリのボイラープレート

class HelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        return

    # シーンにアセットを初回配置するための関数
    # ホットリロード後は呼ばれず、空のステージからワールドを読み込む場合のみ呼ばれる
    def setup_scene(self):
        # World は BaseSample で定義されており、__init__ 以外のどこからでもアクセス可能
        world = self.get_world()
        world.scene.add_default_ground_plane() # デフォルトの地面をシーンに追加
        return
```

## シングルトン・ワールド

World はシングルトンです。つまり、NVIDIA Isaac Sim の実行中に存在できる World は1つだけです。

前のセクションでは `self.get_world()` を使って World を取得しましたが、`World.instance()` でも同じインスタンスを取得できます。両者は同一のオブジェクトを返しますが、使い分けの目安は以下の通りです：

| 取得方法 | 使いどころ |
|---|---|
| `self.get_world()` | `BaseSample` を継承したクラス内（通常のチュートリアル開発） |
| `World.instance()` | `BaseSample` を継承していない別のファイルや拡張機能からアクセスする場合 |

以下のコードは、`World.instance()` を使ったアクセス方法を示しています。`BaseSample` を継承していないクラスや別の拡張機能からでも、この方法で現在の World にアクセスできます。

```python linenums="1" hl_lines="2 9"
from isaacsim.examples.interactive.base_sample import BaseSample
from isaacsim.core.api import World # World クラスを直接インポート

class HelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        return

    def setup_scene(self):
        world = World.instance() # シングルトンインスタンスを取得
        world.scene.add_default_ground_plane()
        return
```

## シーンへの追加

Python API を使用して、シーンに剛体として立方体を追加します。

```python linenums="1" hl_lines="3 13-20"
from isaacsim.examples.interactive.base_sample import BaseSample
import numpy as np
from isaacsim.core.api.objects import DynamicCuboid # 動的な立方体を作成するクラス

class HelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        return

    def setup_scene(self):
        world = self.get_world()
        world.scene.add_default_ground_plane()
        fancy_cube = world.scene.add(
            DynamicCuboid(
                prim_path="/World/random_cube", # USD Stage 上のパス
                name="fancy_cube",              # 後からオブジェクトを取得するための一意な名前
                position=np.array([0, 0, 1.0]), # 位置（デフォルト単位: メートル）
                scale=np.array([0.5015, 0.5015, 0.5015]), # スケール（numpy 配列）
                color=np.array([0, 0, 1.0]),    # RGB（0〜1の範囲）
            ))
        return
```

コードを保存してシミュレーションを確認します：

1. **Ctrl+S** を押してコードを保存し、Isaac Sim をホットリロードします。
2. Hello World サンプル拡張機能のウィンドウを再度開きます。
3. **File > New From Stage Template > Empty** でワールドを新規作成してから、**LOAD** ボタンを押します。`setup_scene` で変更を加えた場合はこの操作が必要です。
4. **PLAY** ボタンを押して動的キューブのシミュレーションを開始し、落下する様子を確認します。

![動的キューブの落下シミュレーション](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/core_api_tutorials_1_1.webp)

!!! note "注釈"
    コードを編集するたびに、**Ctrl+S** を押して保存し、Isaac Sim をホットリロードしてください。

## オブジェクトのプロパティの確認

次に、キューブのワールド座標と速度を出力してみます。

ここで新しいメソッド `setup_post_load` が登場します。`setup_scene` との違いは以下の通りです：

| メソッド | 呼ばれるタイミング | 用途 |
|---|---|---|
| `setup_scene` | 空のステージから初回ロード時のみ | アセットの配置 |
| `setup_post_load` | **LOAD** ボタン押下後に毎回 | 物理ハンドルが有効になった後の初期化処理 |

`setup_post_load` は物理シミュレーションの1ステップ後に呼ばれるため、オブジェクトの座標・速度などの物理プロパティを取得できます。

```python linenums="1" hl_lines="23-33"
from isaacsim.examples.interactive.base_sample import BaseSample
import numpy as np
from isaacsim.core.api.objects import DynamicCuboid

class HelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        return

    def setup_scene(self):
        world = self.get_world()
        world.scene.add_default_ground_plane()
        fancy_cube = world.scene.add(
            DynamicCuboid(
                prim_path="/World/random_cube",
                name="fancy_cube",
                position=np.array([0, 0, 1.0]),
                scale=np.array([0.5015, 0.5015, 0.5015]),
                color=np.array([0, 0, 1.0]),
            ))
        return

    # LOAD ボタン押下後に毎回呼ばれる（setup_scene の後、物理ステップ1回分の後）
    # 物理ハンドルが有効になっているため、物理プロパティの取得が可能
    async def setup_post_load(self):
        self._world = self.get_world()
        self._cube = self._world.scene.get_object("fancy_cube") # 名前でオブジェクトを取得
        position, orientation = self._cube.get_world_pose()
        linear_velocity = self._cube.get_linear_velocity()
        # ターミナルに出力される
        print("Cube position is : " + str(position))
        print("Cube's orientation is : " + str(orientation))
        print("Cube's linear velocity is : " + str(linear_velocity))
        return
```

## シミュレーション中のオブジェクトプロパティの継続的検査

物理演算ステップが実行されるたびに、キューブの姿勢と速度を出力します。

[Workflow](#workflow) で述べたように、**Extension Workflow** ではアプリケーションは非同期で実行されており、物理演算のステップタイミングを直接制御できません。ただし、**物理演算コールバック**を登録することで、各物理ステップの前に任意の処理を実行できます。

```python linenums="1" hl_lines="26 29-37"
from isaacsim.examples.interactive.base_sample import BaseSample
import numpy as np
from isaacsim.core.api.objects import DynamicCuboid

class HelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        return

    def setup_scene(self):
        world = self.get_world()
        world.scene.add_default_ground_plane()
        fancy_cube = world.scene.add(
            DynamicCuboid(
                prim_path="/World/random_cube",
                name="fancy_cube",
                position=np.array([0, 0, 1.0]),
                scale=np.array([0.5015, 0.5015, 0.5015]),
                color=np.array([0, 0, 1.0]),
            ))
        return

    async def setup_post_load(self):
        self._world = self.get_world()
        self._cube = self._world.scene.get_object("fancy_cube")
        self._world.add_physics_callback("sim_step", callback_fn=self.print_cube_info) # コールバック名は一意にする
        return

    # 各物理ステップの前に呼ばれるコールバック関数
    # 引数 step_size は必須（物理ステップの時間幅）
    def print_cube_info(self, step_size):
        position, orientation = self._cube.get_world_pose()
        linear_velocity = self._cube.get_linear_velocity()
        # ターミナルに出力される
        print("Cube position is : " + str(position))
        print("Cube's orientation is : " + str(orientation))
        print("Cube's linear velocity is : " + str(linear_velocity))
```

## ワールドのリセット

シミュレーション中にオブジェクトを初期状態に戻したい場合は、**RESET** ボタンを使用します。リセット後に再度初期化が必要な処理は `setup_pre_reset` および `setup_post_reset` コールバックで行えます。

!!! tip "ヒント"
    `world.reset()` を呼ぶと、すべてのオブジェクトが `setup_scene` で設定した初期状態に戻ります。Standalone Workflow では、アセット追加後に `world.reset()` を呼ぶことで物理ハンドルが正しく初期化されます。

## サンプルをスタンドアロンアプリケーションに変換

!!! note "注釈"
    Windows では `python.sh` の代わりに `python.bat` を使用してください。

[Workflow](#workflow) で述べたように、**Standalone Workflow** では Python から Isaac Sim を直接起動し、物理演算とレンダリングのタイミングを完全に制御できます。

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

```python linenums="1" hl_lines="1-4 20-22 30-32 34"
# Isaac Sim を他のインポートより先に起動する（Standalone の必須手順）
# Standalone アプリケーションの最初の2行は必ずこの形式にする
from isaacsim import SimulationApp
simulation_app = SimulationApp({"headless": False}) # headless=True でGUI無しでも実行可能

from isaacsim.core.api import World
from isaacsim.core.api.objects import DynamicCuboid
import numpy as np

world = World()
world.scene.add_default_ground_plane()
fancy_cube = world.scene.add(
    DynamicCuboid(
        prim_path="/World/random_cube",
        name="fancy_cube",
        position=np.array([0, 0, 1.0]),
        scale=np.array([0.5015, 0.5015, 0.5015]),
        color=np.array([0, 0, 1.0]),
    ))
# アセット追加後にリセットを呼ぶことで、物理ハンドルが正しく初期化される
# アーティキュレーション等のプロパティ取得前に必ず実行すること
world.reset()
for i in range(500):
    position, orientation = fancy_cube.get_world_pose()
    linear_velocity = fancy_cube.get_linear_velocity()
    # ターミナルに出力される
    print("Cube position is : " + str(position))
    print("Cube's orientation is : " + str(orientation))
    print("Cube's linear velocity is : " + str(linear_velocity))
    # Standalone では物理演算とレンダリングのタイミングを制御できる
    # Extension と異なり、すべて同期的に実行される
    world.step(render=True) # 物理演算1ステップ + レンダリング1ステップを実行

simulation_app.close() # Isaac Sim を終了
```

Isaac Sim のインストールディレクトリに移動し、以下のコマンドでスクリプトを実行します：

```bash
cd <Isaac Sim インストールディレクトリ>
./python.sh ./exts/isaacsim.examples.interactive/isaacsim/examples/interactive/user_examples/my_application.py
```

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. **World** および **Scene** クラスの概要
2. Python による Scene へのコンテンツ追加
3. `setup_post_load` による初期化と物理プロパティの取得
4. 物理演算コールバックの追加
5. Standalone アプリケーションへの変換

## 次のステップ

次のチュートリアル「[Hello Robot](02_hello_robot.md)」に進み、シミュレーションにロボットを追加する方法を学びましょう。

!!! note "注釈"
    次のチュートリアルでは主に Extension Workflow を使用して開発を進めます。ただし、本チュートリアルで扱った内容を踏まえれば、他の Workflow への変換も同様の手順で行えます。
