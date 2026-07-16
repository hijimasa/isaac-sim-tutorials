---
title: Articulation Joint センサー
---

# Articulation Joint センサー

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- 関節力の能動成分（active）と受動成分（passive）を読み取る考え方
- `Articulation` / `ArticulationView` の 3 つの関節力 API の違い
- Script Editor から関節力を読み取る方法

## はじめに

### 前提条件

- [Physics ベースのセンサー](08_physics_sensors.md) の概要を理解していること
- Articulation（多関節構造）の基礎知識があること

### 所要時間

約 10 分

### 概要

Articulation センサーを使うと、関節力の**能動成分と受動成分**を読み取れます。関節力の取得には `Articulation` または `ArticulationView` の API を使います。

| API | 返す内容 |
|---|---|
| `get_applied_joint_efforts` | `set_joint_efforts` でユーザーが設定したエフォート |
| `get_measured_joint_forces` | 各関節の 6 次元空間力（関節全体の力）。固定関節から力を取得すれば**力・トルクセンサー**を模倣できる |
| `get_measured_joint_efforts` | 各関節の力の**能動成分**（運動方向への射影） |

!!! note "報告される力は「子リンクへの入力関節力」"
    Articulation ツリーでは、各リンクは 1 つの親リンクを持ちます。`get_measured_joint_forces` と `get_measured_joint_efforts` が報告する関節力は、**子リンクを親リンクに接続する関節が及ぼす力・トルク・エフォート**に相当します。つまり、これらの API はリンクの入力関節力（incoming joint forces）を表します。

## ステップ：Script Editor で関節力を読み取る

**Window > Script Editor** から Script Editor を開き、次のコードを実行します。Ant ロボットを読み込み、各関節の測定力とエフォートを読み取ります。

```python
from isaacsim.core.prims import SingleArticulation
import asyncio
from isaacsim.core.api import World
from isaacsim.core.utils.stage import (
    add_reference_to_stage,
    create_new_stage_async,
    get_current_stage,
)
from isaacsim.storage.native import get_assets_root_path
from pxr import UsdPhysics

async def joint_force():
    World.clear_instance()
    await create_new_stage_async()
    my_world = World(stage_units_in_meters=1.0, backend="torch", device="cpu")
    await my_world.initialize_simulation_context_async()
    await omni.kit.app.get_app().next_update_async()
    assets_root_path = get_assets_root_path()
    asset_path = assets_root_path + "/Isaac/Robots/IsaacSim/Ant/ant.usd"
    add_reference_to_stage(usd_path=asset_path, prim_path="/World/Ant")
    await omni.kit.app.get_app().next_update_async()
    my_world.scene.add_default_ground_plane()
    arti_view = SingleArticulation("/World/Ant/torso")
    my_world.scene.add(arti_view)
    await my_world.reset_async(soft=False)
    stage = get_current_stage()

    sensor_joint_forces = arti_view.get_measured_joint_forces()
    sensor_actuation_efforts = arti_view.get_measured_joint_efforts()
    # Articulation 内の関節名を走査し、関節と関連リンクの情報を取得して、
    # 関節名と対応する子リンクのインデックスのマッピングを作成する。
    joint_link_id = dict()
    for joint_name in arti_view._articulation_view.joint_names:
        joint_path = "/World/Ant/joints/" + joint_name
        joint = UsdPhysics.Joint.Get(stage, joint_path)
        body_1_path = joint.GetBody1Rel().GetTargets()[0]
        body_1_name = stage.GetPrimAtPath(body_1_path).GetName()
        child_link_index = arti_view._articulation_view.get_link_index(body_1_name)
        joint_link_id[joint_name] = child_link_index

    print("joint link IDs", joint_link_id)
    print(sensor_joint_forces[joint_link_id["front_left_leg"]])
    print(sensor_actuation_efforts[joint_link_id["front_left_leg"]])

asyncio.ensure_future(joint_force())
```

!!! tip "力・トルクセンサーの模倣"
    実機の 6 軸力・トルクセンサーを模倣したい場合は、測定したい箇所に**固定関節**を挿入し、その関節に対して `get_measured_joint_forces` を呼び出すと、その関節を通過する 6 次元の力・トルクが取得できます。

## まとめ

このチュートリアルでは、次の内容を学びました。

- Articulation センサーで関節力の能動成分・受動成分を読み取れること
- `get_applied_joint_efforts` / `get_measured_joint_forces` / `get_measured_joint_efforts` の違い
- 報告される力が「子リンクへの入力関節力」であること
- 固定関節を使って力・トルクセンサーを模倣する方法

## 次のステップ

- [Contact センサー](10_contact_sensor.md) で、接触力の検出を学びます。
