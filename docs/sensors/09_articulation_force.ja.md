---
title: Articulation Joint センサー
---

# Articulation Joint センサー

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- 関節力の能動成分（active）と受動成分（passive）を読み取る考え方
- `Articulation` クラス（`isaacsim.core.experimental.prims`）の 2 つの関節力 API の違い
- Script Editor から関節力を読み取る方法

## はじめに

### 前提条件

- [Physics ベースのセンサー](08_physics_sensors.md) の概要を理解していること
- Articulation（多関節構造）の基礎知識があること

### 所要時間

約 10 分

### 概要

Articulation センサーを使うと、関節力の**能動成分と受動成分**を読み取れます。関節力の取得には `isaacsim.core.experimental.prims` 拡張機能の `Articulation` クラスの API を使います。

| API | 返す内容 |
|---|---|
| `get_link_incoming_joint_force()` | 各リンクの入力関節の 6 次元の力とトルク（それぞれ shape `(N, L, 3)`）。関節全体の空間力を表し、固定関節から力を取得すれば**力・トルクセンサー**を模倣できる |
| `get_dof_projected_joint_forces()` | 各 DOF の関節力の**能動成分**（運動方向への射影）。駆動関節の測定エフォートの読み取りに便利 |

!!! note "報告される力は「子リンクへの入力関節力」"
    Articulation ツリーでは、各リンクは 1 つの親リンクを持ちます。`get_link_incoming_joint_force` と `get_dof_projected_joint_forces` が報告する関節力は、**子リンクを親リンクに接続する関節が及ぼす力・トルク・エフォート**に相当します。つまり、これらの API はリンクの入力関節力（incoming joint forces）を表します。

!!! note "Isaac Sim 6.0 での API 変更"
    Isaac Sim 6.0 では、従来の `SingleArticulation` / `ArticulationView`（`isaacsim.core.prims`）の
    `get_measured_joint_forces` / `get_measured_joint_efforts` に代わり、
    `isaacsim.core.experimental.prims.Articulation` の上記 API を使う形に公式チュートリアルが更新されました。

## ステップ：Script Editor で関節力を読み取る

**Window > Script Editor** から Script Editor を開き、次のコードを実行します。Ant ロボットを読み込み、各関節の測定力とエフォートを読み取ります。

```python
import asyncio

import omni
import omni.timeline
from isaacsim.core.experimental.objects import GroundPlane
from isaacsim.core.experimental.prims import Articulation
from isaacsim.core.experimental.utils.stage import (
    add_reference_to_stage,
    create_new_stage_async,
)
from isaacsim.storage.native import get_assets_root_path
from pxr import UsdPhysics


async def joint_force():
    await create_new_stage_async()
    await omni.kit.app.get_app().next_update_async()

    # 物理シーンをセットアップする
    stage = omni.usd.get_context().get_stage()
    UsdPhysics.Scene.Define(stage, "/World/PhysicsScene")

    # Ant ロボットを読み込み、地面を追加する
    assets_root_path = get_assets_root_path()
    asset_path = assets_root_path + "/Isaac/Robots/IsaacSim/Ant/ant.usd"
    add_reference_to_stage(usd_path=asset_path, path="/World/Ant")
    GroundPlane("/World/GroundPlane")
    await omni.kit.app.get_app().next_update_async()

    # Articulation をラップする
    arti = Articulation("/World/Ant/torso")

    # 物理テンソル API を利用可能にするためシミュレーションを開始する
    timeline = omni.timeline.get_timeline_interface()
    timeline.play()
    await omni.kit.app.get_app().next_update_async()

    # 6 次元の関節力（リンクごとの力とトルク）を読み取る
    forces, torques = arti.get_link_incoming_joint_force()
    # DOF に射影された関節力（DOF ごとの能動成分）を読み取る
    projected_forces = arti.get_dof_projected_joint_forces()

    # 確認用に numpy に変換する
    forces_np = forces.numpy()
    torques_np = torques.numpy()
    projected_np = projected_forces.numpy()

    # 組み込み API で関節名とリンクインデックスの対応を取得する
    print("Joint names:", arti.joint_names)
    print("Link names:", arti.link_names)

    # front_left_leg のリンクインデックスと関節インデックスを取得する
    link_idx = int(arti.get_link_indices("front_left_leg").numpy()[0])
    joint_idx = int(arti.get_joint_indices("front_left_leg").numpy()[0])

    print("front_left_leg link forces:", forces_np[0, link_idx])
    print("front_left_leg link torques:", torques_np[0, link_idx])
    print("front_left_leg projected force:", projected_np[0, joint_idx])

    timeline.stop()


asyncio.ensure_future(joint_force())
```

!!! tip "力・トルクセンサーの模倣"
    実機の 6 軸力・トルクセンサーを模倣したい場合は、測定したい箇所に**固定関節**を挿入し、その関節に対して `get_link_incoming_joint_force` を呼び出すと、その関節を通過する 6 次元の力・トルクが取得できます。

## まとめ

このチュートリアルでは、次の内容を学びました。

- Articulation センサーで関節力の能動成分・受動成分を読み取れること
- `get_link_incoming_joint_force` / `get_dof_projected_joint_forces` の違い
- 報告される力が「子リンクへの入力関節力」であること
- 固定関節を使って力・トルクセンサーを模倣する方法

`Articulation` クラスの詳細は [isaacsim.core.experimental.prims の API ドキュメント](https://docs.isaacsim.omniverse.nvidia.com/latest/py/source/extensions/isaacsim.core.experimental.prims/docs/index.html)を参照してください。

## 次のステップ

- [Contact センサー](10_contact_sensor.md) で、接触力の検出を学びます。
