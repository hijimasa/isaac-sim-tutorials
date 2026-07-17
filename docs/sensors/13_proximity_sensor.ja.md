---
title: Proximity センサー
---

# Proximity センサー

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- Proximity センサーが物理コールバックをラップする仕組み
- センサーを prim にアタッチし、コールバックで近接データを取得する方法
- Standalone Python での実行例と出力の読み方

## はじめに

### 前提条件

- [Physics ベースのセンサー](08_physics_sensors.md) の概要を理解していること
- 剛体・コライダーの基礎を理解していること

### 所要時間

約 10 分

### 概要

Proximity センサーは、シーン内の任意の prim にアタッチできる**物理コールバックのラッパー**です。シミュレーション実行中、センサーはアタッチされた prim と他の prim との衝突を毎フレーム記録し、そのデータはコールバック関数から取得できます。

!!! note "使用する拡張機能"
    Proximity センサーは、他の Physics ベースのセンサー（`isaacsim.sensors.physics`）とは異なり、**`isaacsim.sensors.physx`** 拡張機能で提供されます。このため、Isaac Sim 6.0 の公式ドキュメントでは本ページは「PhysX SDK センサー」セクションの配下に移動しました。

!!! warning "Isaac Sim 6.0 での位置づけ"
    Proximity センサー（`isaacsim.sensors.physx.ProximitySensor`）は、非推奨（deprecated）となった
    `isaacsim.sensors.physx` 拡張機能の一部です。衝突検出には
    [Contact センサー](10_contact_sensor.md)や物理接触コールバックを直接使うことを検討してください。
    以下のコードは非推奨の拡張機能を使用していますが、引き続き動作します。

## ステップ：Standalone Python で実行する

次のスクリプトを `python.sh` で実行します。2 つの立方体を作成し、片方に Proximity センサーをアタッチします。シミュレーション開始時に 2 つの立方体は重なり、その後離れます。スクリプト内のコールバック関数が、Proximity センサーの出力を画面に表示します。

```python
import numpy as np
from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": False})

import carb
import omni
from isaacsim.core.api.world import World
from isaacsim.core.experimental.objects import Cube, GroundPlane
from isaacsim.core.utils.extensions import enable_extension
from pxr import Sdf, UsdLux, UsdPhysics

# シーンをセットアップ
world = World()
GroundPlane("/World/GroundPlane")

# 照明を追加
stage = omni.usd.get_context().get_stage()
distantLight = UsdLux.DistantLight.Define(stage, Sdf.Path("/DistantLight"))
distantLight.CreateIntensityAttr(500)

# 物理シミュレーション用にコリジョンと剛体を設定した立方体を追加
cube_1 = Cube("/cube_1", sizes=1.0, positions=np.array([0.4, 0, 5.0]), colors=np.array([1.0, 0, 0]))
UsdPhysics.CollisionAPI.Apply(cube_1.prims[0])
UsdPhysics.RigidBodyAPI.Apply(cube_1.prims[0])

cube_2 = Cube("/cube_2", sizes=1.0, positions=np.array([-0.4, 0, 5.0]), colors=np.array([0, 0, 1.0]))
UsdPhysics.CollisionAPI.Apply(cube_2.prims[0])
UsdPhysics.RigidBodyAPI.Apply(cube_2.prims[0])

# isaacsim.sensors.physx 拡張機能を有効化
enable_extension("isaacsim.sensors.physx")
simulation_app.update()

# cube_1 にセンサーをアタッチ
from isaacsim.sensors.physx import ProximitySensor, clear_sensors, register_sensor

s = ProximitySensor(cube_1.prims[0])
register_sensor(s)


# Proximity センサーのデータを表示するコールバックを追加
def print_proximity_sensor_data_on_update(_):
    data = s.get_data()
    if "/cube_2" in data:
        # /cube_1 が /cube_2 と衝突している
        distance = data["/cube_2"]["distance"]
        duration = data["/cube_2"]["duration"]
        carb.log_warn(f"distance: {distance}, duration: {duration}")


# シミュレーションを再生
world.add_physics_callback("print_sensor_data", print_proximity_sensor_data_on_update)
simulation_app.update()
simulation_app.update()
world.play()

for i in range(100):
    # 固定ステップサイズで実行
    world.step(render=True)
```

Proximity センサーの出力例は次のとおりです（実行ごとに数値のわずかな違いが出ることがあります）。

```text
distance: 0.8995118804137266, duration: 0.03952527046203613
distance: 0.9490971672498862, duration: 0.04244112968444824
distance: 0.9978315307718298, duration: 0.045195579528808594
distance: 1.0952793930211249, duration: 0.00010466575622558594
distance: 1.0952880909233123, duration: 0.004382610321044922
distance: 1.0952874949586842, duration: 0.008539199829101562
distance: 1.095288806188406, duration: 0.012722015380859375
```

立方体が着地すると、シーンは次のようになります。

![Proximity センサーの例](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isaac_proximity_sensor_example.png)

!!! note "データの構造"
    `get_data()` は、衝突相手の prim パスをキーとする辞書を返します。各エントリには `distance`（距離）と `duration`（近接が続いている時間）が含まれます。相手の prim パスがキーに存在するかどうかで、衝突の有無を判定できます。

## まとめ

このチュートリアルでは、次の内容を学びました。

- Proximity センサーが物理コールバックをラップし、非推奨の `isaacsim.sensors.physx` 拡張機能で提供されること
- `ProximitySensor` を prim にアタッチして `register_sensor` で登録する方法
- 物理コールバックと `get_data()` で近接データ（distance / duration）を取得する方法
- 衝突検出の代替として Contact センサーや物理接触コールバックが推奨されること

## 次のステップ

- より詳細な PhysX ベースのセンサー（Generic / Lidar / Lightbeam）については [PhysX SDK センサー](14_physx_sensors.md) を参照してください。
