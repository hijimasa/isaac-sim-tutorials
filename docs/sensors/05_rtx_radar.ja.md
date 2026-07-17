---
title: RTX Radar センサー
---

# RTX Radar センサー

![倉庫内の RTX Radar](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isaacsim_sensors_rtx_radar_node_overview_warehouse.png)

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- RTX Radar が `OmniRadar` prim としてレンダリングされる仕組み
- `isaacsim.sensors.experimental.rtx` の `Radar` クラスで RTX Radar を作成する方法
- `RadarSensor` クラスで Radar データを収集する方法
- Radar の戻り値がマテリアルプロパティに依存すること

## はじめに

### 前提条件

- [RTX センサー](03_rtx_sensors.md) の概要（特に Radar には Motion BVH が必須）を理解していること
- Isaac Sim 6.0 が RTX 対応 GPU で起動できること

### 所要時間

約 10 分

### 概要

RTX Radar センサーは、RTX ハードウェア上で**レンダリング時に GPU でシミュレート**されます。その結果は `GenericModelOutput` AOV にコピーされて利用されます。

RTX Radar は、`OmniSensorGenericRadarWpmDmatAPI` スキーマを適用した **`OmniRadar` prim** としてレンダリングされます。`OmniRadar` prim にレンダープロダクトをアタッチし、`GenericModelOutput` AOV を設定すると、RTXSensor レンダラーが Radar のレンダリング結果を AOV へ書き込みます。

!!! warning "RTX Radar には Motion BVH が必須"
    RTX Radar のドップラー効果（したがって Radar 全体）を正しくモデル化するには、**Motion BVH を有効にする**必要があります。Motion BVH はパフォーマンス上の理由からデフォルトで無効なので、RTX Radar を使う前に明示的に有効化してください。起動時のコマンドライン引数（`--/renderer/raytracingMotion/enabled=true` など）または `SimulationApp` の `enable_motion_bvh=True`、`carb.settings` での設定が使えます。詳細は [RTX センサー](03_rtx_sensors.md) の Motion BVH の節を参照してください。

!!! note "旧 API からの移行"
    Isaac Sim 6.0 では、旧 `isaacsim.sensors.rtx` の `IsaacSensorCreateRtxRadar` コマンドは非推奨（deprecated）となり、`isaacsim.sensors.experimental.rtx` の `Radar`（オーサリング）＋ `RadarSensor`（ランタイム）に置き換えられました。Camera prim ベースの Radar 方式は削除されています。詳細は公式の [RTX Sensors 移行ガイド](https://docs.isaacsim.omniverse.nvidia.com/latest/migration_guides/isaac_sim_6_0/sensors_rtx_to_experimental_rtx.html) を参照してください。

## ステップ 1：RTX Radar を作成する

`isaacsim.sensors.experimental.rtx` 拡張機能は、RTX Radar を作成する `Radar` クラスを提供します。さらに低レベルな API（`OmniRadar` prim の一括作成やレンダープロダクトのアタッチ）は `omni.replicator.core` 拡張機能が提供します。

`Radar` クラスは、適切なスキーマを適用した `OmniRadar` prim を作成（または既存 prim をラップ）します。次のスニペットは Script Editor（**Window > Script Editor**）で実行できます。

```python
import carb
import isaacsim.core.experimental.utils.stage as stage_utils
import numpy as np
from isaacsim.sensors.experimental.rtx import Radar

# RTX Radar のドップラー速度推定には Motion BVH の有効化が必要
settings = carb.settings.get_settings()
settings.set("/renderer/raytracingMotion/enabled", True)
settings.set("/renderer/raytracingMotion/enableHydraEngineMasking", True)
settings.set("/renderer/raytracingMotion/enabledForHydraEngines", "0,1,2,3,4")

# Radar の親となる /World Xform をステージに用意する
stage_utils.define_prim("/World", "Xform")

# カスタム tick rate で RTX Radar を作成
radar = Radar(
    path="/World/radar",
    tick_rate=10,
    translations=np.array([0.0, 0.0, 0.0]),
    orientations=np.array([1.0, 0.0, 0.0, 0.0]),
)
```

![RTX Radar を作成](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_5.0_full_ext-isaacsim.sensors.rtx-15.1.1_gui_rtx_radar_create_command.png)

上の例は、`OmniRadar` prim を `/World/radar` に作成し、`omni:sensor:tickRate` 属性を 10 Hz に設定します。設定できる属性は `omni.usd.schema.omni_sensors` 拡張機能の `OmniSensorGenericRadarWpmDmatAPI` スキーマを参照してください。

!!! note "Radar.create() の主なパラメータ"
    - `Radar.create()` は `config`（`SUPPORTED_RADAR_CONFIGS` に登録された設定名）または `usd_path` を受け付けます（排他）。
    - `attributes` で prim 属性を上書きでき、位置・姿勢は複数形の配列（`positions=[[...]]` / `translations=[[...]]` / `orientations=[[...]]` / `scales=[[...]]`、`N=1`）で渡します。
    - 追加の USD スキーマ（`schemas=[...]`）は `Radar(...)` コンストラクタが受け付けます。`Radar.create()` は現状 `schemas` を転送しないため、必要な場合は `Radar(...)` を直接使ってください。

### tick_rate（レンダリング頻度）

`tick_rate` パラメータ（Hz）はセンサーがレンダリングする頻度を制御します。デフォルトの `0` は autotrigger モードで、シミュレーションフレームごとにレンダリングします（prim の `omni:sensor:tickRate` 属性に対応）。

!!! warning "Isaac Sim 6.0 GA の既知の問題"
    Isaac Sim 6.0 GA では、RTX Radar は `omni:sensor:tickRate` 属性に関係なく autotrigger で動作します。将来のリリースで修正される予定です。

### aux_output_level（補助出力レベル）

RTX Radar は、`aux_output_level` コンストラクタパラメータで補助データの出力量を制御します。有効な値は `"NONE"`（デフォルト）と `"BASIC"` です。`"BASIC"` を設定すると、GMO 出力で**視線方向速度（`rv_ms`）**が有効になります。

```python
import carb
from isaacsim.sensors.experimental.rtx import Radar

# RTX Radar には Motion BVH の有効化が必要
settings = carb.settings.get_settings()
settings.set("/renderer/raytracingMotion/enabled", True)
settings.set("/renderer/raytracingMotion/enableHydraEngineMasking", True)
settings.set("/renderer/raytracingMotion/enabledForHydraEngines", "0,1,2,3,4")

radar = Radar(path="/Radar", aux_output_level="BASIC")
```

属性の流れと旧 `omni:sensor:WpmDmat:auxOutputType` 属性（削除済み）からの移行、複数センサー混在時の既知の問題については [RTX センサー](03_rtx_sensors.md) を参照してください。

## ステップ 2：データを収集する

RTX Radar からデータを収集する推奨方法は、`LidarSensor` と同様に、`Radar` オーサリングオブジェクトをラップして Replicator アノテーターを管理するランタイムクラス **`RadarSensor`** を使うことです。

```python
import carb
from isaacsim.sensors.experimental.rtx import Radar, RadarSensor, parse_generic_model_output_data

# RTX Radar には Motion BVH の有効化が必要
settings = carb.settings.get_settings()
settings.set("/renderer/raytracingMotion/enabled", True)
settings.set("/renderer/raytracingMotion/enableHydraEngineMasking", True)
settings.set("/renderer/raytracingMotion/enabledForHydraEngines", "0,1,2,3,4")

radar = Radar(path="/Radar")
sensor = RadarSensor(radar, annotators=["generic-model-output"])

data, info = sensor.get_data("generic-model-output")
gmo = parse_generic_model_output_data(data)
```

利用可能な低レベルアノテーターの一覧は [RTX センサーアノテーター](06_rtx_annotators.md) を参照してください。

### 出力の可視化

**Debug Draw 拡張機能**を使うと、RTX Radar の点群出力をビューポートで可視化できます。Standalone 例 `create_radar_basic.py` が実演しています。

```bash
./python.sh standalone_examples/api/isaacsim.sensors.experimental.rtx/create_radar_basic.py
```

## ステップ 3：センサーマテリアル

RTX Radar のマテリアルシステムでは、USD ステージ上の部分的なマテリアル prim 名にセンサーマテリアル種別を割り当てられます。Radar の戻り値の挙動は、マテリアルのプロパティ（放射率・反射率など）に依存します。詳細は [RTX センサー用の非可視マテリアル](07_rtx_materials.md) を参照してください。

## Standalone 例

RTX Radar の作成・データ収集の例は次のとおりです。

```bash
# Debug Draw による可視化付きの基本的な Radar 作成
./python.sh standalone_examples/api/isaacsim.sensors.experimental.rtx/create_radar_basic.py

# Radar の GenericModelOutput（GMO）データを調べる
./python.sh standalone_examples/api/isaacsim.sensors.experimental.rtx/inspect_radar_gmo.py
```

ROS 2 への PointCloud2 配信については、公式の [RTX Radar Sensors チュートリアル](https://docs.isaacsim.omniverse.nvidia.com/latest/ros2_tutorials/tutorial_ros2_rtx_radar.html) を参照してください（6.0 では `OgnROS2RtxRadarHelper` ノードが追加されています）。

## まとめ

このチュートリアルでは、次の内容を学びました。

- RTX Radar は `OmniRadar` prim としてレンダリングされ、結果は `GenericModelOutput` AOV に書き込まれること
- `Radar` クラスで RTX Radar を作成し、`RadarSensor` でデータを収集する方法
- ドップラー効果（したがって Radar 全体）には Motion BVH が必須であること
- `aux_output_level="BASIC"` で視線方向速度（`rv_ms`）が有効になること
- Radar の戻り値がマテリアルの放射率・反射率に依存すること

## 次のステップ

- [RTX センサーアノテーター](06_rtx_annotators.md) で、RTX センサーの出力データの取得方法を学びます。
