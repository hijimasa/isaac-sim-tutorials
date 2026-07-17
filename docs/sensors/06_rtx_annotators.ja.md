---
title: RTX センサーアノテーター
---

# RTX センサーアノテーター

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- `isaacsim.sensors.experimental.rtx` と `isaacsim.sensors.rtx.nodes` が Omniverse Replicator を使ってアノテーターを提供する仕組み
- 推奨手段である `LidarSensor` / `RadarSensor` クラスでデータを収集する方法
- 現行アノテーター `IsaacExtractRTXSensorPointCloud` と `draw-point-cloud` ライターの使い方
- `GenericModelOutput` バッファからのデータ読み取りと、Object ID を使ったセマンティックセグメンテーション
- Isaac Sim 6.0 で非推奨になったアノテーターと置き換え先

## はじめに

### 前提条件

- [RTX LiDAR センサー](04_rtx_lidar.md) / [RTX Radar センサー](05_rtx_radar.md) の作成方法を理解していること
- Isaac Sim 6.0 が起動できること

### 所要時間

約 15〜20 分

### 概要

`isaacsim.sensors.experimental.rtx` と `isaacsim.sensors.rtx.nodes` 拡張機能は、Omniverse Replicator を使って RTX LiDAR / Radar のデータ収集用**アノテーター**（レンダープロダクトから特定の種類のデータを抽出する Replicator の構成部品。[深度センサーのページ](02_depth_sensors.md)の note も参照）を提供します。

!!! note "6.0 でのアノテーター再編"
    Isaac Sim 6.0 では、旧 `isaacsim.sensors.rtx` 拡張機能に同梱されていたアノテーター（`IsaacCreateRTXLidarScanBuffer` など）は**非推奨**となり、引き続き有効な `isaacsim.sensors.rtx.nodes` 拡張機能の `IsaacExtractRTXSensorPointCloud` に置き換えられました。ほとんどのユーザーは、これを内部で利用する `LidarSensor` / `RadarSensor` クラス経由で間接的に使うことになります。

このチュートリアルは、次の流れで進みます。

1. **`LidarSensor` / `RadarSensor`** でデータを収集する（推奨）
2. **現行アノテーター**（`IsaacExtractRTXSensorPointCloud`）とデバッグ描画ライターを使う
3. **`GenericModelOutput` バッファ**からデータを読み取り、Object ID を活用する

## ステップ 1：LidarSensor / RadarSensor でデータを収集する

推奨されるのは、アノテーターとレンダープロダクトを自動的に管理する **`LidarSensor`** / **`RadarSensor`** クラスを使う方法です。次の例は Standalone Python ワークフロー用で、Script Editor では動作しません。

```python
from isaacsim import SimulationApp

kit = SimulationApp()

import numpy as np
import omni
from isaacsim.sensors.experimental.rtx import Lidar, LidarSensor, parse_generic_model_output_data

# RTX LiDAR を作成
lidar = Lidar.create(
    path="/World/lidar",
    config="Example_Rotary",
    translations=np.array([0.0, 0.0, 1.0]),
    orientations=np.array([1.0, 0.0, 0.0, 0.0]),
)

# アノテーターのアタッチとデータ取得を担う LidarSensor を作成
sensor = LidarSensor(lidar, annotators=["generic-model-output"])

# タイムラインを再生してデータ収集を開始
timeline = omni.timeline.get_timeline_interface()
timeline.play()

# シミュレーションフレームごとにセンサーからデータを収集
for _ in range(100):
    kit.update()
    data, info = sensor.get_data("generic-model-output")
    if data is not None:
        gmo = parse_generic_model_output_data(data)
        print(f"Points: {gmo.numElements}")

timeline.stop()
kit.close()
```

!!! warning "タイムラインとタイムスタンプに関する注意"
    - RTX センサーアノテーターは、データ収集にシミュレーションのタイムラインを使います。**タイムラインが再生されていない**（一時停止・停止中）と、アノテーターはデータを収集しません。
    - **マルチティックレンダリングが有効（デフォルト）** の場合、`GenericModelOutput` AOV の内部タイムスタンプはセンサーがティックするたびに進み、`omni.timeline` の Play / Pause / Stop に従います。`omni.kit.app.get_app().update()` / `next_update_async()`、`omni.replicator.core.orchestrator.step()` / `step_async()` のいずれでシミュレーションを進めても、期待どおりのタイムスタンプが得られます。
    - **マルチティックレンダリングが無効**の場合、タイムスタンプはログに `App Ready` が表示された時点から単調増加し、タイムラインとは独立します。一時停止・再開でポイントクラウド内のタイムスタンプが不連続になることがあり、この場合は `orchestrator.step()` ではなく `omni.kit.app.get_app().update()` / `next_update_async()` でステップする必要があります。
    - OmniSensor prim にアタッチしたライターを確実にトリガーするには、`omni.replicator.core.orchestrator.step()` / `step_async()` の使用が推奨されます。

## ステップ 2：現行アノテーターとデバッグ描画

### IsaacExtractRTXSensorPointCloud

`IsaacExtractRTXSensorPointCloud` アノテーターは、`GenericModelOutput` バッファのポイントクラウドデータを毎フレーム直交座標（x, y, z）バッファに抽出します。`isaacsim.sensors.rtx.nodes` 拡張機能が提供し、**`OmniLidar`（RTX LiDAR）と `OmniRadar`（RTX Radar）の両方**で動作します。GMO バッファが球面座標を含む場合は直交座標への変換を行い、センサー→ワールドの変換行列も出力します。

ビューポートでの可視化には、同じく `isaacsim.sensors.rtx.nodes` の **`RtxSensorDebugDrawPointCloud`** Replicator ライターが使えます。

### draw-point-cloud ライター

`isaacsim.sensors.rtx.nodes` が有効な場合、`LidarSensor` / `RadarSensor` / `AcousticSensor` で `"draw-point-cloud"` という名前のライターが利用できます。`writers=["draw-point-cloud"]` を渡すとデバッグ描画ライターがアタッチされます。次のスニペットは Script Editor（**Window > Script Editor**）で実行できます。

```python
import omni.kit.app
from isaacsim.sensors.experimental.rtx import Lidar, LidarSensor

# "draw-point-cloud" ライターは isaacsim.sensors.rtx.nodes が登録する。
# センサーを作る前に拡張機能を有効化しておくこと。
omni.kit.app.get_app().get_extension_manager().set_extension_enabled_immediate(
    "isaacsim.sensors.rtx.nodes", True
)

# センサーがラップする OmniLidar prim を作成
Lidar.create("/World/lidar", config="Example_Rotary")
sensor = LidarSensor("/World/lidar", annotators=[], writers=["draw-point-cloud"])
```

### RTX Radar で使う

アノテーターは `OmniRadar` prim でも同様に動作します。RTX Radar には Motion BVH の有効化が必要な点に注意してください。

```python
import carb
import numpy as np
import omni.kit.app
import omni.replicator.core as rep
from isaacsim.sensors.experimental.rtx import Radar

# RTX Radar には Motion BVH の有効化が必要
settings = carb.settings.get_settings()
settings.set("/renderer/raytracingMotion/enabled", True)
settings.set("/renderer/raytracingMotion/enableHydraEngineMasking", True)
settings.set("/renderer/raytracingMotion/enabledForHydraEngines", "0,1,2,3,4")

# デバッグ描画ライターは isaacsim.sensors.rtx.nodes が登録する
omni.kit.app.get_app().get_extension_manager().set_extension_enabled_immediate(
    "isaacsim.sensors.rtx.nodes", True
)

radar = Radar(path="/Radar", tick_rate=20, translations=np.array([0, 0, 1.0]))

render_product = rep.create.render_product(radar.paths[0], resolution=(1, 1))
writer = rep.writers.get("RtxSensorDebugDrawPointCloud")
writer.initialize(size=0.2, color=[1.0, 0.3, 0.1, 1.0])  # オレンジ色・大きめの点
writer.attach([render_product.path])
```

### 補助データ

`LidarSensor` / `RadarSensor` クラスを使う場合、補助データ（強度・エミッター ID・マテリアル ID など）は `parse_generic_model_output_data` を介して `GenericModelOutput` バッファから直接取得できます。どの補助フィールドに値が入るかは、センサー prim の `_replicator:rendervar:GenericModelOutput:channels` 属性（コンストラクタの `aux_output_level`）で制御します。

```python
import numpy as np
from isaacsim.sensors.experimental.rtx import Lidar, LidarSensor

# emitterId などの補助フィールドを有効にするには aux_output_level を BASIC 以上にする
lidar = Lidar.create(
    path="/World/lidar",
    config="Example_Rotary",
    aux_output_level="BASIC",
    translations=np.array([0.0, 0.0, 1.0]),
    orientations=np.array([1.0, 0.0, 0.0, 0.0]),
)

# generic-model-output アノテーター付きの LidarSensor を作成。
# 補助フィールドは aux_output_level に応じて GMO バッファに含まれる。
sensor = LidarSensor(lidar, annotators=["generic-model-output"])
```

## ステップ 3：GenericModelOutput バッファからのデータ読み取り

`isaacsim.sensors.experimental.rtx.generic_model_output` Python モジュールは、`GenericModelOutput` アノテーターが生成したバッファを検査する API を提供します。`isaacsim.sensors.experimental.rtx` の **`parse_generic_model_output_data`** ユーティリティ関数を使うと、アノテーター出力を簡単にパースできます。

!!! note "旧 API からの移行"
    Isaac Sim 4.5 の `OgnIsaacReadRTXLidarData` ノードは 5.0 で削除され、`parse_generic_model_output_data` / `parse_object_ids` / `parse_stable_id_map_data` ユーティリティ（`isaacsim.sensors.experimental.rtx` から再エクスポート）に置き換えられました。旧 `isaacsim.sensors.rtx.get_gmo_data` に相当する処理も `parse_generic_model_output_data` で行います。

読み取りの例は次の Standalone 例を参照してください。

```bash
# LiDAR の GMO を調べる
./python.sh standalone_examples/api/isaacsim.sensors.experimental.rtx/inspect_lidar_gmo.py --aux-data-level FULL

# Radar の GMO を調べる
./python.sh standalone_examples/api/isaacsim.sensors.experimental.rtx/inspect_radar_gmo.py
```

### Object ID を使ったセマンティックセグメンテーション

`GenericModelOutput` 構造体には、戻り値ごとのオブジェクト識別子を格納する `objId` フィールドがあります。データは `np.uint8` の numpy 配列として提供され、`--/rtx-transient/stableIds/enabled=true` を設定した場合にのみ値が入ります。

このデータは 128 ビット符号なし整数の列（実質ストライド 16）として解釈され、シーン内の一意な prim パスに対応する**安定した一意の ID** です。i 番目の整数が、i 番目の戻り値を生成した prim に対応します。これを使えば、Object ID を prim パスにマッピングし、prim からセマンティックラベルを取得することでシーンをセマンティックセグメンテーションできます。

`isaacsim.sensors.experimental.rtx` には、Object ID を prim パスとして解決する 2 つのユーティリティ関数があります。

- `parse_stable_id_map_data` … `StableIdMap` AOV（`OmniLidar` / `OmniRadar` prim から生成可能）の出力を「安定 ID → prim パス」の Python dict として解決します。
- `parse_generic_model_output_data` … `GenericModelOutput` バッファの `objId` フィールド（128 ビットのオブジェクト ID）へのアクセスを提供します。

使用例は `standalone_examples/api/isaacsim.sensors.experimental.rtx/resolve_lidar_object_ids.py` を参照してください。

!!! note "マップに載らない Object ID がある"
    すべての Object ID にマップエントリがあるわけではありません。レンダラーは、インスタンスごとのベース安定 ID に上位 32 ビットのインデックス（メッシュならサブメッシュインデックス、プロシージャルジオメトリなら三角形ごとのプリミティブインデックス）を組み合わせて 128 ビット ID を構成します。`StableIdMap` にはインスタンス単位（USD prim パスを持つもののみ）と、複数サブセットを持つ場合の GeomSubset 単位のエントリしか登録されません。そのため、プロシージャルジオメトリへのヒットなどではマップエントリのない ID が返り、`map[id]` の直接参照は `KeyError` になります。同梱の例のように `map.get(id, "<unknown>")` を使って安全に処理してください。

## 非推奨アノテーター

Isaac Sim 6.0 では、次のアノテーターが非推奨の `isaacsim.sensors.rtx` 拡張機能に同梱されており、将来のリリースで削除されます：**`IsaacCreateRTXLidarScanBuffer`**、**`IsaacComputeRTXLidarFlatScan`**、**`IsaacExtractRTXSensorPointCloudNoAccumulator`**。

代わりに、有効な `isaacsim.sensors.rtx.nodes` 拡張機能の `IsaacExtractRTXSensorPointCloud` を使ってください。ほとんどのユーザーは `LidarSensor` / `RadarSensor` 経由で間接的に利用します。

### IsaacCreateRTXLidarScanBuffer（非推奨）

`OmniLidar` prim からのフレームを 1 つのスキャンに**累積**し、累積スキャンデータを出力します（`OmniRadar` には非対応）。デフォルトでは 3D 直交座標のポイントクラウドを出力し、初期化時に対応する入力フラグを `True` にすると追加データも出力できます。

```python
import omni.replicator.core as rep
annotator = rep.AnnotatorRegistry.get_annotator("IsaacCreateRTXLidarScanBuffer")
# 必要な出力を指定して初期化（レンダープロダクトへのアタッチ前に行う）
annotator.initialize(outputTimestamp=True, outputMaterialId=True)
```

出力はバッファへのポインタとして提供されます。各バッファのデータ型と提供条件は次のとおりです。必要な属性や carb 設定が不足していると、アノテーターは警告を表示してそのデータを出力しません。

| 出力 | 型 | 説明 | 提供条件 |
|---|---|---|---|
| `data` | float3 | 3D 直交座標のポイントクラウド | 常に提供 |
| `azimuth` | float | 各戻り値の方位角（度） | `outputAzimuth=true` |
| `elevation` | float | 各戻り値の仰角（度） | `outputElevation=true` |
| `distance` | float | 各戻り値の距離（ワールド単位、既定はメートル） | `outputDistance=true` |
| `intensity` | float | 各戻り値の強度（正規化済み） | `outputIntensity=true` |
| `timestamp` | uint64 | 各戻り値のタイムスタンプ（シミュレーション開始からのナノ秒） | `outputTimestamp=true` |
| `emitterId` | uint32 | 戻り値を発したエミッターの ID | `outputEmitterId=true` かつ `aux_output_level` が `BASIC` 以上 |
| `channelId` | uint32 | 戻り値が生成されたチャネルの ID | `outputChannelId=true` かつ `aux_output_level` が `BASIC` 以上 |
| `materialId` | uint32 | 戻り値を生成したオブジェクトのマテリアル ID | `outputMaterialId=true` かつ `aux_output_level` が `EXTRA` 以上 |
| `tickId` | uint32 | 戻り値が生成されたティックの ID | `outputTickId=true` かつ `aux_output_level` が `BASIC` 以上 |
| `hitNormal` | float3 | 戻り値を生成した面の法線 | `outputHitNormal=true`、`aux_output_level` が `FULL`、かつ `--/app/sensors/nv/lidar/publishNormals=true` |
| `velocity` | float3 | 戻り値を生成したオブジェクトの速度 | `outputVelocity=true` かつ `aux_output_level` が `FULL` |
| `objectId` | uint8 | 戻り値を生成したオブジェクトの ID（安定した 128 ビット整数） | `outputObjectId=true`、`aux_output_level` が `EXTRA` 以上、かつ `--/rtx-transient/stableIds/enabled=true` |
| `echoId` | uint8 | マルチエコー LiDAR 設定でどのエコーかを示す | `outputEchoId=true` かつ `aux_output_level` が `BASIC` 以上 |
| `tickState` | uint8 | 戻り値が生成されたティックの状態 | `outputTickState=true` かつ `aux_output_level` が `BASIC` 以上 |

!!! note
    `aux_output_level` は `isaacsim.sensors.experimental.rtx.Lidar` のコンストラクタパラメータで、prim の `_replicator:rendervar:GenericModelOutput:channels` 属性を設定します。属性の流れと UI からの設定方法は [RTX センサー](03_rtx_sensors.md) を参照してください。

!!! warning "法線出力とパフォーマンス"
    `--/app/sensors/nv/lidar/publishNormals=true` で法線出力を有効にすると VRAM 使用量が増え、パフォーマンスに悪影響を与えることがあります。

### IsaacComputeRTXLidarFlatScan（非推奨）

累積された **2D** RTX LiDAR スキャンから深度と方位角のデータを抽出します。仰角 0 のエミッターのみを持つ 2D LiDAR 専用で、`OmniRadar`（RTX Radar）や 3D LiDAR には対応していません。

### IsaacExtractRTXSensorPointCloudNoAccumulator（非推奨）

`GenericModelOutput` バッファから毎フレームポイントクラウドを抽出します（`OmniLidar` / `OmniRadar` 対応）。`isaacsim.sensors.rtx.nodes` の `IsaacExtractRTXSensorPointCloud` に置き換えられました。

## まとめ

このチュートリアルでは、次の内容を学びました。

- `LidarSensor` / `RadarSensor` クラスでアノテーターとレンダープロダクトを自動管理してデータを収集する方法
- 現行アノテーター `IsaacExtractRTXSensorPointCloud` と `draw-point-cloud` ライター（`isaacsim.sensors.rtx.nodes`）の使い方
- マルチティックレンダリングの有無によるタイムスタンプ挙動の違い
- `parse_generic_model_output_data` / `parse_stable_id_map_data` による GMO バッファの読み取りと Object ID の解決
- 6.0 で非推奨になったアノテーター（`IsaacCreateRTXLidarScanBuffer` など）と置き換え先

## 次のステップ

- LiDAR / Radar の戻り値を左右するマテリアルについては [RTX センサー用の非可視マテリアル](07_rtx_materials.md) を参照してください。
