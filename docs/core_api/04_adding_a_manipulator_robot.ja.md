---
title: マニピュレータロボットの追加
---

# マニピュレータロボットの追加

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます:

- `Franka` クラスを使ってマニピュレータロボット（Franka Panda）をシーンに追加する方法
- 逆運動学（IK）によるエンドエフェクタ制御とグリッパー制御の基本 API
- `FrankaPickPlace` クラスを使ったピック＆プレース動作の実行
- ピック＆プレースのステートマシン（状態機械）の理解とカスタマイズ

## はじめに

### 前提条件

- [チュートリアル 2: Hello Robot](02_hello_robot.md) を完了していること

!!! note "このチュートリアルは Standalone Workflow で進めます"
    これまでのチュートリアルは Extension Workflow（`hello_world.py` の編集）で進めてきましたが、このチュートリアルでは **Standalone の Python スクリプト**を使用します。スクリプトは Isaac Sim 同梱の Python 環境（`python.sh` / Windows は `python.bat`）で実行してください。実行方法は [Hello World の「サンプルをスタンドアロンアプリケーションに変換」](01_hello_world.md)で学んだ手順と同様です。

### 所要時間

約 15〜20 分

## Franka ロボットのあるシーンの作成

`Franka` クラスを使って、Franka ロボットと、ロボットがつかむためのキューブをシーンに追加します。`Franka` クラスは `Articulation` を継承しており、逆運動学（IK）やグリッパー制御を含む高レベルな制御メソッドを提供します。

コンストラクタで `create_robot=True` を指定すると、`Franka` クラスが指定パスに Franka ロボットの USD アセットを自動的にスポーンします。

以下のスクリプトを `create_franka_scene.py` などの名前で作成します：

```python linenums="1" hl_lines="13-15 20 28-29 31-40 42-46"
"""地面・Franka ロボット・青いキューブのあるシーンを作成する。"""

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--test", action="store_true")
args, _ = parser.parse_known_args()

from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": False})

import isaacsim.core.experimental.utils.app as app_utils

app_utils.enable_extension("isaacsim.robot.experimental.manipulators.examples")

from isaacsim.core.experimental.objects import Cube, DomeLight, GroundPlane
from isaacsim.core.experimental.prims import GeomPrim, RigidPrim
from isaacsim.core.simulation_manager import SimulationManager
from isaacsim.robot.experimental.manipulators.examples.franka import Franka

DEVICE = "cpu"

GroundPlane("/World/ground_plane")
dome_light = DomeLight("/World/DomeLight")
dome_light.set_intensities(1000)

# Franka ロボットを作成
robot = Franka(robot_path="/World/robot", create_robot=True)

# ロボットがつかむための青いキューブを作成
cube_shape = Cube(
    paths="/World/Cube",
    positions=[0.5, 0.0, 0.0258],
    sizes=1.0,
    scales=[0.0515, 0.0515, 0.0515],
    colors="blue",
)
GeomPrim(paths=cube_shape.paths, apply_collision_apis=True)
RigidPrim(paths=cube_shape.paths)

SimulationManager.setup_simulation(dt=1.0 / 60.0, device=DEVICE)
physics_scene = SimulationManager.get_physics_scenes()[0]
physics_scene.set_enabled_gpu_dynamics(False)
app_utils.play()
app_utils.update_app(steps=20)

step_count = 0
max_test_steps = 60
while simulation_app.is_running():
    simulation_app.update()
    step_count += 1
    if args.test and step_count >= max_test_steps:
        break

app_utils.stop()
simulation_app.close()
```

スクリプトを実行すると、Franka ロボットとキューブが配置されたウィンドウが開き、ウィンドウを閉じるまでシミュレーションが実行されます。

```bash
cd <Isaac Sim インストールディレクトリ>
./python.sh create_franka_scene.py
```

このスクリプトのポイント：

| 処理 | 説明 |
|---|---|
| `app_utils.enable_extension()` | `Franka` クラスを提供する拡張機能 `isaacsim.robot.experimental.manipulators.examples` を有効化する |
| `Franka(robot_path=..., create_robot=True)` | Franka の USD アセットのスポーンとラッパー作成を一度に行う |
| `SimulationManager.setup_simulation()` | 物理演算の時間刻み（`dt`）と実行デバイス（CPU/GPU）を設定する |
| `app_utils.play()` / `app_utils.update_app()` | タイムラインを再生し、アプリを指定ステップ数だけ進める |

`Franka` クラスはロボット制御のための以下の主要メソッドを提供します：

| メソッド | 説明 |
|---|---|
| `set_end_effector_pose(position, orientation)` | 逆運動学（IK）でエンドエフェクタを移動する |
| `open_gripper()` / `close_gripper()` | グリッパーを開閉する |
| `get_current_state()` | DOF 位置とエンドエフェクタの姿勢を取得する |
| `get_downward_orientation()` | 下向きのエンドエフェクタ姿勢のクォータニオンを取得する |
| `reset_to_default_pose()` | ロボットをホームポジションにリセットする |

!!! note "逆運動学（IK）とは"
    **逆運動学（Inverse Kinematics）**は、エンドエフェクタ（手先）の目標位置・姿勢から、それを実現する各関節の角度を逆算する計算です。`set_end_effector_pose()` を呼ぶだけで、各関節の角度は `Franka` クラスが内部で自動計算してくれます。

## FrankaPickPlace による完全なピック＆プレース

完全なピック＆プレース動作には `FrankaPickPlace` クラスを使用します。このクラスの `setup_scene()` メソッドは、ピック＆プレースに必要なすべての要素（Franka ロボット、地面、操作対象のキューブ）をスポーンします。

```python linenums="1" hl_lines="19 27-30 35-39 41-53"
"""FrankaPickPlace を使ったピック＆プレース。"""

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--test", action="store_true")
args, _ = parser.parse_known_args()

from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": False})

import isaacsim.core.experimental.utils.app as app_utils

app_utils.enable_extension("isaacsim.robot.experimental.manipulators.examples")

from isaacsim.core.experimental.objects import DomeLight, GroundPlane
from isaacsim.core.simulation_manager import SimulationManager
from isaacsim.robot.experimental.manipulators.examples.franka import FrankaPickPlace

DEVICE = "cpu"

GroundPlane("/World/ground_plane")
dome_light = DomeLight("/World/DomeLight")
dome_light.set_intensities(1000)

# FrankaPickPlace はロボットとキューブをスポーンし、ピック＆プレースの
# ステートマシンを提供する
controller = FrankaPickPlace()
controller.setup_scene()

SimulationManager.setup_simulation(dt=1.0 / 60.0, device=DEVICE)
physics_scene = SimulationManager.get_physics_scenes()[0]
physics_scene.set_enabled_gpu_dynamics(False)
app_utils.play()
# controller.reset() の前にアーティキュレーションの物理テンソルエンティティが
# 有効になるよう、数ステップ実行しておく
app_utils.update_app(steps=20)
controller.reset()

# メインループ: 完了するまで毎物理フレームでピック＆プレースを1ステップ進める
step_count = 0
max_test_steps = sum(controller.events_dt) + 60
while simulation_app.is_running():
    simulation_app.update()
    step_count += 1
    if app_utils.is_playing():
        if not controller.is_done():
            controller.forward()
        else:
            print("Pick-and-place completed")
            app_utils.pause()
            if args.test:
                break
    if args.test and step_count >= max_test_steps:
        raise RuntimeError("Pick-and-place did not complete within the test step budget")

app_utils.stop()
simulation_app.close()
```

スクリプトを実行すると、ロボットがキューブを拾い上げて配置するまでの全フェーズを自動的に実行します。

![Franka によるピック＆プレース動作](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/core_api_tutorials_4_1.webp)

## ピック＆プレースのステートマシンを理解する

`FrankaPickPlace` クラスは、以下のフェーズを持つステートマシン（状態機械）として動作します：

| フェーズ | 動作 | デフォルトのステップ数 |
|---|---|---|
| 0 | キューブ上方の x, y 位置へ移動 | 60 |
| 1 | キューブへ下降 | 40 |
| 2 | グリッパーを閉じて把持 | 20 |
| 3 | キューブを持ち上げる | 40 |
| 4 | キューブを目標位置へ移動 | 80 |
| 5 | グリッパーを開いて解放 | 20 |
| 6 | 上方へ退避 | 20 |

各フェーズの所要ステップ数はコンストラクタに `events_dt` を渡してカスタマイズできます。また、`setup_scene()` の引数でキューブの初期位置・サイズ・目標位置を変更できます：

```python linenums="1"
# 各フェーズのステップ数をカスタマイズ
controller = FrankaPickPlace(events_dt=[80, 60, 30, 60, 100, 30, 30])
# キューブの位置・サイズ・目標位置をカスタマイズ
controller.setup_scene(
    cube_initial_position=[0.4, 0.2, 0.0258], cube_size=[0.05, 0.05, 0.05], target_position=[-0.4, 0.2, 0.12]
)
```

コード全体は以下の通りです：

```python linenums="1" hl_lines="27-34"
"""FrankaPickPlace を使ったピック＆プレース。"""

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--test", action="store_true")
args, _ = parser.parse_known_args()

from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": False})

import isaacsim.core.experimental.utils.app as app_utils

app_utils.enable_extension("isaacsim.robot.experimental.manipulators.examples")

from isaacsim.core.experimental.objects import DomeLight, GroundPlane
from isaacsim.core.simulation_manager import SimulationManager
from isaacsim.robot.experimental.manipulators.examples.franka import FrankaPickPlace

DEVICE = "cpu"

GroundPlane("/World/ground_plane")
dome_light = DomeLight("/World/DomeLight")
dome_light.set_intensities(1000)

# -- カスタムセットアップここから -- #
# 各フェーズのステップ数をカスタマイズ
controller = FrankaPickPlace(events_dt=[80, 60, 30, 60, 100, 30, 30])
# キューブの位置・サイズ・目標位置をカスタマイズ
controller.setup_scene(
    cube_initial_position=[0.4, 0.2, 0.0258], cube_size=[0.05, 0.05, 0.05], target_position=[-0.4, 0.2, 0.12]
)
# -- カスタムセットアップここまで -- #

SimulationManager.setup_simulation(dt=1.0 / 60.0, device=DEVICE)
physics_scene = SimulationManager.get_physics_scenes()[0]
physics_scene.set_enabled_gpu_dynamics(False)
app_utils.play()
# controller.reset() の前にアーティキュレーションの物理テンソルエンティティが
# 有効になるよう、数ステップ実行しておく
app_utils.update_app(steps=20)
controller.reset()

# メインループ: 完了するまで毎物理フレームでピック＆プレースを1ステップ進める
step_count = 0
max_test_steps = sum(controller.events_dt) + 60
while simulation_app.is_running():
    simulation_app.update()
    step_count += 1
    if app_utils.is_playing():
        if not controller.is_done():
            controller.forward()
        else:
            print("Pick-and-place completed")
            app_utils.pause()
            if args.test:
                break
    if args.test and step_count >= max_test_steps:
        raise RuntimeError("Pick-and-place did not complete within the test step budget")

app_utils.stop()
simulation_app.close()
```

!!! tip "参考: さらに詳しいサンプル"
    `--device`、`--ik-method`、`--test` オプションを備えた完全なスタンドアロンのピック＆プレースサンプルは、Isaac Sim 付属の `standalone_examples/api/isaacsim.robot.experimental.manipulators/franka/pick_place.py` を参照してください。

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. `create_robot=True` を指定した **Franka クラス**によるマニピュレータロボットの追加
2. **逆運動学（IK）とグリッパー制御**のための主要メソッド
3. `FrankaPickPlace.setup_scene()` による**ピック＆プレースシーンの一括スポーン**
4. `forward()` メソッドによる**ピック＆プレース動作の実行**
5. ピック＆プレースの**ステートマシンの理解とカスタマイズ**

## 次のステップ

次のチュートリアル「[複数ロボットの追加](05_adding_multiple_robots.md)」に進み、複数のロボットが連携するシミュレーションの構築方法を学びましょう。
