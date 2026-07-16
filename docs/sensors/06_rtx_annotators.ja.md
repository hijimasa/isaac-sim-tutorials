---
title: RTX センサーアノテーター
---

# RTX センサーアノテーター

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- `isaacsim.sensors.rtx` が Omniverse Replicator を使ってアノテーターを提供する仕組み
- アノテーターをレンダープロダクトにアタッチしてデータを収集する 2 つの方法（Replicator API / `LidarRtx` クラス）
- 主要なアノテーター（`IsaacCreateRTXLidarScanBuffer` / `IsaacComputeRTXLidarFlatScan` / `IsaacExtractRTXSensorPointCloudNoAccumulator`）の役割と出力
- `GenericModelOutput` バッファからのデータ読み取りと、Object ID を使ったセマンティックセグメンテーション
- Isaac Sim 5.0 で非推奨になったアノテーターと置き換え先

## はじめに

### 前提条件

- [RTX LiDAR センサー](04_rtx_lidar.md) / [RTX Radar センサー](05_rtx_radar.md) の作成方法を理解していること
- Isaac Sim 5.1 が起動できること

### 所要時間

約 15〜20 分

### 概要

`isaacsim.sensors.rtx` 拡張機能は、Omniverse Replicator を使って RTX LiDAR / Radar のデータ収集用**アノテーター**を提供します。アノテーターは、`OmniLidar` や `OmniRadar` などの OmniSensor prim にアタッチされたレンダープロダクトに取り付けます。

このチュートリアルは、次の流れで進みます。

1. **アノテーターをアタッチ**してデータを収集する（Replicator API / `LidarRtx` クラス）
2. **主要なアノテーター**の出力を理解する
3. **`GenericModelOutput` バッファ**からデータを読み取り、Object ID を活用する

## ステップ 1：アノテーターをアタッチしてデータを収集する

### Replicator API を使う方法

Script Editor で実行できる例です。`/lidar` に `OmniLidar` prim を作成し、レンダープロダクトを作成して、`IsaacExtractRTXSensorPointCloudNoAccumulator` アノテーターをアタッチします。

```python
import omni
import omni.replicator.core as rep
from pxr import Gf

# prim パス /lidar に OmniLidar prim を作成
_, sensor = omni.kit.commands.execute(
    "IsaacSensorCreateRtxLidar",
    translation=Gf.Vec3d(0.0, 0.0, 0.0),
    orientation=Gf.Quatd(1.0, 0.0, 0.0, 0.0),
    path="/lidar",
)

# センサー用のレンダープロダクトを作成
render_product = rep.create.render_product(sensor.GetPath(), resolution=(1024, 1024))

# アノテーターを作成
annotator = rep.AnnotatorRegistry.get_annotator("IsaacExtractRTXSensorPointCloudNoAccumulator")

# アノテーターの初期化後、レンダープロダクトにアタッチ
annotator.attach([render_product.path])
```

### LidarRtx クラスを使う方法

`LidarRtx` クラスは、任意のアノテーターを `OmniLidar` prim にアタッチしてデータを収集する単一の API を提供します。次の例は Standalone Python ワークフロー用で、Script Editor では動作しません。

```python
from isaacsim import SimulationApp

kit = SimulationApp()

import numpy as np
import omni
from isaacsim.sensors.rtx import LidarRtx

# 指定した属性で RTX LiDAR を作成
sensor = LidarRtx(
    prim_path="/lidar",
    translation=np.array([0.0, 0.0, 1.0]),
    orientation=np.array([1.0, 0.0, 0.0, 0.0]),
    config_file_name="Example_Rotary",
)

# LidarRtx を初期化（センサー用のレンダープロダクトを作成）
sensor.initialize()

# アノテーターをアタッチ
sensor.attach_annotator("IsaacExtractRTXSensorPointCloudNoAccumulator")

# タイムラインを再生してアノテーターと OmniGraph を初期化し、データ収集を開始
timeline = omni.timeline.get_timeline_interface()
timeline.play()

# シミュレーションフレームごとにアノテーターからデータを収集
while kit.is_running():
    kit.update()
    # センサーにアタッチした各アノテーターが収集したデータを Python dict として出力
    print(sensor.get_current_frame())

timeline.stop()
kit.close()
```

!!! warning "タイムラインとタイムスタンプに関する注意"
    - RTX センサーアノテーターは、データ収集にシミュレーションのタイムラインを使います。**タイムラインが再生されていない**（一時停止・停止中）と、アノテーターはデータを収集しません。
    - RTX センサーが生成する `GenericModelOutput` AOV には内部タイムスタンプが含まれ、ログに `App Ready` が表示された時点から**単調増加**します。これはアニメーションタイムライン（`omni.timeline`）とは独立しているため、タイムラインを一時停止・再開するとポイントクラウド内のタイムスタンプが不連続になることがあります。
    - このため、これらのアノテーターでデータを収集するときは、`omni.replicator.core.orchestrator.step()` ではなく `omni.kit.app.get_app().update()` / `next_update_async()` を使ってシミュレーションをステップする必要があります（Isaac Sim の API は前者を使用します）。

## ステップ 2：主要なアノテーター

各アノテーターは特定の OmniGraph ノードに対応しており、入出力はそのノードと同じです。

!!! note "5.0 でのアノテーター整理"
    Isaac Sim 5.0 では、新しい `OmniLidar` / `OmniRadar` prim と非推奨の Camera prim ベースワークフローの両方を扱えるよう、いくつかの既存アノテーターがよりシンプルなものに置き換えられました。詳細は後述の「非推奨アノテーター」を参照してください。

    アノテーターは `OmniLidar` prim の `GenericModelOutput` AOV がデバイス上で提供されることに依存します。`--/app/sensors/nv/lidar/outputBufferOnGPU` や `--/app/sensors/nv/radar/outputBufferOnGPU` を `false` に設定すると、正しく動作しません。

### IsaacCreateRTXLidarScanBuffer

`OmniLidar` prim からのフレームを 1 つのスキャンに**累積**し、累積スキャンデータを出力します。デフォルトでは 3D 直交座標のポイントクラウドを出力し、初期化時に対応する入力フラグを `True` にすると追加データも出力できます。

```python
import omni.replicator.core as rep
annotator = rep.AnnotatorRegistry.get_annotator("IsaacCreateRTXLidarScanBuffer")
# 必要な出力を指定して初期化（レンダープロダクトへのアタッチ前に行う）
annotator.initialize(outputTimestamp=True, outputMaterialId=True)
```

`LidarRtx` クラス経由の場合は、フラグをキーワード引数で渡します。

```python
sensor.attach_annotator("IsaacCreateRTXLidarScanBuffer", outputTimestamp=True, outputMaterialId=True)
```

出力はバッファへのポインタとして提供されます。各バッファのデータ型は次のとおりです。

| 出力 | 型 | 説明 | 提供条件 |
|---|---|---|---|
| `data` | float3 | 3D 直交座標のポイントクラウド | 常に提供 |
| `azimuth` | float | 各戻り値の方位角（度） | `outputAzimuth=true` |
| `elevation` | float | 各戻り値の仰角（度） | `outputElevation=true` |
| `distance` | float | 各戻り値の距離（ワールド単位、既定はメートル） | `outputDistance=true` |
| `intensity` | float | 各戻り値の強度（正規化済み） | `outputIntensity=true` |
| `timestamp` | uint64 | 各戻り値のタイムスタンプ（シミュレーション開始からのナノ秒） | `outputTimestamp=true` |
| `emitterId` | uint32 | 戻り値を発したエミッターの ID | `outputEmitterId=true` かつ `auxOutputType` が `BASIC` 以上 |
| `materialId` | uint32 | 戻り値を生成したオブジェクトのマテリアル ID | `outputMaterialId=true` かつ `auxOutputType` が `EXTRA` 以上 |
| `objectId` | uint8 | 戻り値を生成したオブジェクトの ID（安定した 128 ビット整数） | `outputObjectId=true`、`auxOutputType` が `EXTRA` 以上、かつ `--/rtx-transient/stableIds/enabled=true` |
| `normal` | float3 | 戻り値を生成した面の法線 | `outputNormal=true`、`auxOutputType` が `FULL`、かつ `--/app/sensors/nv/lidar/publishNormals=true` |
| `velocity` | float3 | 戻り値を生成したオブジェクトの速度 | `outputVelocity=true` かつ `auxOutputType` が `FULL` |

!!! warning "法線出力とパフォーマンス"
    `--/app/sensors/nv/lidar/publishNormals=true` で法線出力を有効にすると VRAM 使用量が増え、パフォーマンスに悪影響を与えることがあります。

### IsaacComputeRTXLidarFlatScan

累積された **2D** RTX LiDAR スキャンから深度と方位角のデータを抽出します。RTX Radar には対応していません。3D LiDAR（仰角が 0 でないエミッターを持つもの）にアタッチした場合、データを返しません。

### IsaacExtractRTXSensorPointCloudNoAccumulator

`GenericModelOutput` バッファのポイントクラウドデータを、毎フレーム直交座標ベクトルのバッファに抽出します（`IsaacCreateRTXLidarScanBuffer` ノードに `enablePerFrameOutput=true` を設定したもの）。累積を行わないため、フレームごとの生データが必要な場合に使います。

## ステップ 3：GenericModelOutput バッファからのデータ読み取り

`isaacsim.sensors.rtx.generic_model_output` Python モジュールは、`GenericModelOutput` アノテーターが生成したバッファを検査する API を提供します。読み取りの例は次の Standalone 例を参照してください。

```bash
./python.sh standalone_examples/api/isaacsim.sensors.rtx/inspect_lidar_metadata.py
```

### Object ID を使ったセマンティックセグメンテーション

`GenericModelOutput` 構造体には `objId` フィールドがあり、`IsaacCreateRTXLidarScanBuffer` ノードもオプションで `objectId` を出力します。いずれも `--/rtx-transient/stableIds/enabled=true` を設定した場合にのみ値が入ります。

このデータは 128 ビット符号なし整数の列（実質ストライド 16）として解釈され、シーン内の一意な prim パスに対応する**安定した一意の ID** です。i 番目の整数が、i 番目の戻り値を生成した prim に対応します。これを使えば、Object ID を prim パスにマッピングし、prim からセマンティックラベルを取得することでシーンをセマンティックセグメンテーションできます。

`LidarRtx` クラスには、Object ID を prim パスとして解決する 2 つのユーティリティがあります。

- `LidarRtx.decode_stable_id_mapping` … `StableIdMap` AOV の出力を「128 ビット整数 → prim パス」の Python dict として解決します。
- `LidarRtx.get_object_ids` … `GenericModelOutput` / `IsaacCreateRTXLidarScanBuffer` の Object ID 配列を 128 ビット整数として解決します。

使用例は `standalone_examples/api/isaacsim.sensors.rtx/resolve_object_ids_from_gmo.py` を参照してください。

## 非推奨アノテーター

Isaac Sim 5.0 で、いくつかのアノテーターが削除・置き換えられました。新しいアノテーターの出力は、非推奨アノテーターと必ずしも同一ではありません。

| 非推奨（4.5）アノテーター | 置き換え先 | 備考 |
|---|---|---|
| `IsaacComputeRTXLidarFlatScanSimulationTime` | `IsaacComputeRTXLidarFlatScan` | 同一データ。タイムスタンプは `IsaacReadSimulationTime` を併用 |
| `IsaacComputeRTXLidarFlatScanSystemTime` | `IsaacComputeRTXLidarFlatScan` | 同一データ。タイムスタンプは `IsaacReadSystemTime` を併用 |
| `RtxSensorCpuIsaacComputeRTXLidarPointCloud` | `IsaacExtractRTXSensorPointCloudNoAccumulator` | azimuth/elevation/range を除き同一（直交座標から計算可能）。GPU/CPU 出力は設定で自動選択 |
| `RtxSensorGpuIsaacComputeRTXLidarPointCloud` | `IsaacExtractRTXSensorPointCloudNoAccumulator` | 同上 |
| `RtxSensorCpuIsaacComputeRTXRadarPointCloud` | `IsaacExtractRTXSensorPointCloudNoAccumulator` | 同上 |
| `RtxSensorGpuIsaacComputeRTXRadarPointCloud` | `IsaacExtractRTXSensorPointCloudNoAccumulator` | 同上 |
| `IsaacReadRTXLidarData` | `isaacsim.sensors.rtx.read_gmo_data` ユーティリティ | 「GenericModelOutput バッファからのデータ読み取り」を参照 |

## まとめ

このチュートリアルでは、次の内容を学びました。

- アノテーターを Replicator API または `LidarRtx` クラスでアタッチしてデータを収集する方法
- `IsaacCreateRTXLidarScanBuffer`（累積）と `IsaacExtractRTXSensorPointCloudNoAccumulator`（毎フレーム）の違いと出力
- タイムラインとタイムスタンプに関する注意点、`GenericModelOutput` バッファの読み取り
- Object ID を使ったセマンティックセグメンテーションの考え方

## 次のステップ

- LiDAR / Radar の戻り値を左右するマテリアルについては [RTX センサー用の非可視マテリアル](07_rtx_materials.md) を参照してください。
