---
title: RTX LiDAR センサー
---

# RTX LiDAR センサー

![倉庫内の RTX LiDAR](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_4.5_full_ref_viewport_rtx_lidar_warehouse.png)

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- RTX LiDAR が `OmniLidar` prim としてレンダリングされる仕組み
- `isaacsim.sensors.experimental.rtx` の `Lidar` クラス（オーサリング）で RTX LiDAR を作成する方法
- `tick_rate` / `aux_output_level` / `accumulate_outputs` の各パラメータの意味
- `LidarSensor` クラス（ランタイム）で LiDAR データを収集する方法
- RTX LiDAR アセットライブラリから実機モデルを読み込む方法
- 出力の可視化と ROS 2 連携の入り口

## はじめに

### 前提条件

- [RTX センサー](03_rtx_sensors.md) の概要（RTX Sensor SDK、Motion BVH、GMO 補助出力レベル）を理解していること
- Isaac Sim 6.0 が RTX 対応 GPU で起動できること

### 所要時間

約 15〜20 分

### 概要

RTX LiDAR センサーは、RTX ハードウェア上で**レンダリング時に GPU でシミュレート**されます。その結果は `GenericModelOutput` AOV にコピーされて利用されます。

RTX LiDAR は、`OmniSensorGenericLidarCoreAPI` スキーマを適用した **`OmniLidar` prim** としてレンダリングされます。`OmniLidar` prim にレンダープロダクトをアタッチし、そのレンダープロダクトに `GenericModelOutput` AOV を設定すると、RTXSensor レンダラーが LiDAR のレンダリング結果を AOV へ書き込みます。`OmniSensorGenericLidarCoreAPI` スキーマは `omni.usd.schema.omni_sensors` 拡張機能で定義されています。

!!! note "旧 API からの移行"
    Isaac Sim 6.0 では、旧 `isaacsim.sensors.rtx` の `LidarRtx` クラスと `IsaacSensorCreateRtxLidar` コマンドは非推奨（deprecated）となり、`isaacsim.sensors.experimental.rtx` の `Lidar`（オーサリング）＋ `LidarSensor`（ランタイム）に置き換えられました。また、Camera prim を JSON コンフィグで RTX LiDAR 化する方式（Isaac Sim 5.0 で非推奨）は**削除**されています。詳細は公式の [RTX Sensors 移行ガイド](https://docs.isaacsim.omniverse.nvidia.com/latest/migration_guides/isaac_sim_6_0/sensors_rtx_to_experimental_rtx.html) を参照してください。

!!! warning "マルチ GPU 環境での既知の問題"
    複数 GPU（MGPU）のシステムでは、一部の RTX LiDAR アセットがログに CUDA error 700 を伴う致命的なクラッシュを引き起こすことがあります。この問題が発生した場合は、`./isaac-sim.sh --/renderer/multiGpu/enabled=false` で単一 GPU レンダリングに切り替えてください。Standalone Python では `SimulationApp` コンストラクタに `multi_gpu=False` を渡します。

このチュートリアルは、次の流れで進みます。

1. **`Lidar` クラス**で RTX LiDAR を作成し、主要パラメータを理解する
2. **`LidarSensor`** でデータを収集する
3. **出力を可視化**する（Debug Draw / デバッグビュー / RViz2）
4. **アセットライブラリ**から実機モデルを読み込む

## ステップ 1：RTX LiDAR を作成する

`isaacsim.sensors.experimental.rtx` 拡張機能は、RTX LiDAR を作成する Python API を提供します。さらに低レベルな API は `omni.replicator.core` 拡張機能が提供し、`OmniLidar` prim の一括作成やレンダープロダクトのアタッチが行えます。

### 1-1. Lidar クラスで作成する

`Lidar` クラスは、`OmniLidar` prim を作成・ラップする高レベルの Python インターフェースです。既知の設定名や USD ファイルから新規作成するには `Lidar.create()` を、ステージ上の既存 `OmniLidar` prim をラップするには `Lidar(path)` を使います。次のスニペットは Script Editor（**Window > Script Editor**）で実行できます。

```python
import numpy as np
from isaacsim.sensors.experimental.rtx import Lidar

# 既知のセンサー設定から RTX LiDAR を作成
lidar = Lidar.create(
    path="/World/lidar",
    config="Example_Rotary",
    translations=np.array([0.0, 0.0, 1.0]),
    orientations=np.array([1.0, 0.0, 0.0, 0.0]),
    attributes={"omni:sensor:Core:scanRateBaseHz": 20},
)
```

![RTX LiDAR を作成](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_5.0_full_ext-isaacsim.sensors.rtx-15.1.1_gui_rtx_lidar_create_lidar_rtx.png)

上の例は、`Example_Rotary.usda` への参照を `OmniLidar` prim として `/World/lidar` に作成し、指定した位置・姿勢に配置します。`scanRateBaseHz` 属性は `attributes` 辞書を介してデフォルトの 10 Hz から 20 Hz に変更されます。

!!! note "Lidar.create() の主なパラメータ"
    - `config`（`SUPPORTED_LIDAR_CONFIGS` に登録された設定名）と `usd_path`（`OmniLidar` USD アセットへの直接パス）は**排他**で、どちらか一方を指定します。
    - `Lidar.create()` / `Lidar(...)` のどちらも `schemas`（追加で適用する USD スキーマのリスト）と `attributes`（prim 属性の辞書）を受け付けます。
    - 位置・姿勢は複数形の配列（`positions=[[...]]` / `translations=[[...]]` / `orientations=[[...]]` / `scales=[[...]]`）で渡します。センサー 1 台につき `N=1` のみサポートされます。
    - 設定可能な属性は `omni.usd.schema.omni_sensors` の `OmniSensorGenericLidarCoreAPI` / `OmniSensorGenericLidarCoreEmitterStateAPI` スキーマを参照してください。

### 1-2. tick_rate（レンダリング頻度）

`tick_rate` パラメータ（Hz）はセンサーがレンダリングする頻度を制御します。デフォルトの `0` は **autotrigger モード**で、シミュレーションフレームごとにレンダリングします。0 以外の値を設定すると、シミュレーションのステップレートとは独立に指定周波数でレンダリングされます（prim の `omni:sensor:tickRate` 属性に対応）。

```python
from isaacsim.sensors.experimental.rtx import Lidar

# シミュレーションのフレームレートに関係なく 10 Hz でレンダリング
lidar = Lidar.create("/World/Lidar", config="Example_Rotary", tick_rate=10.0)
```

!!! warning "tick_rate は scanRateBaseHz と等しくすること"
    `OmniLidar` prim では、スキャンの蓄積とマルチティックレンダリングを正しく動作させるため、`tick_rate`（`omni:sensor:tickRate`）を `omni:sensor:Core:scanRateBaseHz` と**等しく**する必要があります。値が食い違うと、LiDAR はフルスキャンに蓄積されず毎フレーム部分スキャンを出力するようになり、LaserScan の配信などフルスキャン前提のパイプラインが静かに壊れます。

### 1-3. aux_output_level（補助出力レベル）

RTX LiDAR は、`aux_output_level` コンストラクタパラメータで補助データの出力量を制御します。有効な値は `"NONE"`（デフォルト）、`"BASIC"`、`"EXTRA"`、`"FULL"` です。

```python
from isaacsim.sensors.experimental.rtx import Lidar

lidar = Lidar.create("/World/Lidar", config="Example_Rotary", aux_output_level="BASIC")
```

属性の流れと旧 `omni:sensor:Core:auxOutputType` 属性からの移行、複数センサー混在時の既知の問題については [RTX センサー](03_rtx_sensors.md) を、レベルごとのフィールド一覧は [RTX センサーアノテーター](06_rtx_annotators.md) を参照してください。

### 1-4. accumulate_outputs（スキャンの蓄積）

`accumulate_outputs` パラメータ（デフォルト `True`）は prim の `omni:sensor:Core:accumulateOutputs` 属性を制御します。`True` の場合、フルスキャンが完成するまで複数フレームにわたってデータを蓄積します。回転式 LiDAR では 360 度回転、ソリッドステート LiDAR では全方位角スイープがフルスキャンに相当します。

```python
from isaacsim.sensors.experimental.rtx import Lidar

# 蓄積を無効にして、フレームごとの部分スキャンを取得する
lidar = Lidar.create("/World/Lidar", config="Example_Rotary", accumulate_outputs=False)
```

## ステップ 2：RTX LiDAR からデータを収集する

RTX LiDAR からデータを収集する推奨方法は、ランタイムクラス **`LidarSensor`** を使うことです。`LidarSensor` は `Lidar` オーサリングオブジェクトをラップし、Replicator アノテーターを管理します。

```python
from isaacsim.sensors.experimental.rtx import Lidar, LidarSensor, parse_generic_model_output_data

lidar = Lidar.create("/World/Lidar", config="Example_Rotary")
sensor = LidarSensor(lidar, annotators=["generic-model-output"])

data, info = sensor.get_data("generic-model-output")
gmo = parse_generic_model_output_data(data)
```

Isaac Sim には、レンダープロダクトに直接アタッチできる低レベルの [RTX センサーアノテーター](06_rtx_annotators.md) も用意されています。`GenericModelOutput` アノテーターの使い方の詳細は、同ページの GMO バッファの読み取りを参照してください。

## ステップ 3：RTX LiDAR の出力を可視化する

RTX LiDAR の点群データを可視化する方法は複数あります。

### Debug Draw

**Debug Draw 拡張機能**は、点群をビューポートに直接描画する高効率な可視化手段です。描画したジオメトリはフレームをまたいで保持され、物理シーンとは相互作用しません。Standalone 例 `create_lidar_basic.py` が Debug Draw による可視化を実演しています。

```bash
# Debug Draw による可視化付きの基本的な LiDAR 作成
./python.sh standalone_examples/api/isaacsim.sensors.experimental.rtx/create_lidar_basic.py
```

### ビューポートのデバッグビュー

ビューポートの **RTX - Real-Time > Debug View > Non-Visual Material ID** を選択すると、非可視マテリアル ID を可視化できます。RTX センサーからマテリアルがどう見えるかを確認でき、マテリアル設定のデバッグに便利です。詳細は [RTX センサー用の非可視マテリアル](07_rtx_materials.md) を参照してください。

### RViz2

ROS 2 を使う場合は、点群データを RViz2 で可視化できます（次節参照）。

## ステップ 4：ROS 2 連携

Isaac Sim は、RTX LiDAR データを標準メッセージ型（`sensor_msgs/PointCloud2`＝3D 点群、`sensor_msgs/LaserScan`＝2D スキャン）として ROS 2 に配信することを完全サポートしています。

クイックスタートの手順は次のとおりです。

1. 上記の方法で RTX LiDAR センサーを作成します。
2. **Tools > Robotics > ROS 2 OmniGraphs > RTX Lidar** を開きます。
3. グラフパス・LiDAR prim・フレーム ID・配信するデータ型を設定します。
4. **Play** を押すと配信が始まります。

OmniGraph によるブリッジノードの追加、複数センサーの RViz2 可視化、PointCloud2 への強度・オブジェクト ID の付与などの詳細は、[RTX LiDAR の ROS 2 チュートリアル](../ros/08_rtx_lidar.md) を参照してください。

## ステップ 5：RTX LiDAR アセットライブラリ

Isaac Sim には実機の RTX LiDAR モデルライブラリが含まれており、`Lidar.create()` の `config` / `variant` パラメータで指定して読み込めます。`config` には次のいずれかを指定できます。

- LiDAR モデル USD ファイルの正確な名前（拡張子なし。例：`HESAI_XT32_SD10`）
- ベンダー名を省いたもの（例：`XT32_SD10`）

省略可能な `variant` で、モデルの特定バリアントを選択できます。`variant` は 2 つの形式を受け付けます。

- **フラットな文字列** … `sensor` という単一のバリアントセットを持つ USD（Ouster OS ファミリーなど大半の設定）用。
- **`dict[str, str]`**（`{バリアントセット名: バリアント名, ...}`） … 複数のバリアントセットを持つ USD（`Product` と `Profile` を使う SICK ファミリーなど）用。辞書の挿入順に適用されるため、外側のバリアントセットを先に書きます。

サポートされる設定とバリアントの形式は `isaacsim.sensors.experimental.rtx.SUPPORTED_LIDAR_CONFIGS` で公開されており、これをイテレートすると利用可能な（config, variant）の組み合わせを列挙できます。

次の例は、SICK picoScan100 を `picoScan150Pro` プロダクト・`Profile11_15Hz_1p0deg` プロファイルで読み込みます。

```python
from isaacsim.sensors.experimental.rtx import Lidar

# SICK picoScan100 の USD は 2 つのバリアントセット（"Product" と "Profile"）を
# 持つため、variant は各バリアントセットと選択値の辞書で渡す。
# 単一の "sensor" バリアントセットを持つ設定（例：Ouster OS1）では
# フラットな文字列（例：variant="OS1_REV6_32ch20hz1024res"）を渡す。
lidar = Lidar.create(
    path="/World/lidar",
    config="picoScan100",
    variant={"Product": "picoScan150Pro", "Profile": "Profile11_15Hz_1p0deg"},
)
```

### センサーマテリアル

RTX LiDAR のマテリアルシステムでは、USD ステージ上の部分的なマテリアル prim 名にセンサーマテリアル種別を割り当てられます。LiDAR の戻り値の挙動は、マテリアルのプロパティ（放射率・反射率など）に依存します。詳細は [RTX センサー用の非可視マテリアル](07_rtx_materials.md) を参照してください。

## Standalone 例

RTX LiDAR の作成・データ収集の例は次のとおりです。

```bash
# Debug Draw による可視化付きの基本的な LiDAR 作成
./python.sh standalone_examples/api/isaacsim.sensors.experimental.rtx/create_lidar_basic.py

# ベンダー設定（Ouster / SICK / HESAI）とバリアントを使った LiDAR
./python.sh standalone_examples/api/isaacsim.sensors.experimental.rtx/create_lidar_with_config_and_variants.py

# 補助出力レベル別に GenericModelOutput（GMO）データを調べる
./python.sh standalone_examples/api/isaacsim.sensors.experimental.rtx/inspect_lidar_gmo.py --aux-data-level FULL

# セマンティックセグメンテーション用にオブジェクト ID を USD prim パスへ解決する
./python.sh standalone_examples/api/isaacsim.sensors.experimental.rtx/resolve_lidar_object_ids.py

# 車輪型ロボットと Lidar + LidarSensor の統合
./python.sh standalone_examples/api/isaacsim.sensors.experimental.rtx/lidar_robot_integration.py

# ROS 2 連携
./python.sh standalone_examples/api/isaacsim.ros2.bridge/rtx_lidar.py
```

## まとめ

このチュートリアルでは、次の内容を学びました。

- RTX LiDAR は `OmniLidar` prim としてレンダリングされ、結果は `GenericModelOutput` AOV に書き込まれること
- `Lidar.create()` で RTX LiDAR を作成し、`tick_rate` / `aux_output_level` / `accumulate_outputs` で挙動を制御する方法
- `LidarSensor` でデータを収集し、Debug Draw やデバッグビューで可視化する方法
- アセットライブラリから実機モデルを `config` / `variant` で読み込む方法

## 次のステップ

- [RTX Radar センサー](05_rtx_radar.md) で、電波スペクトルのセンサーを扱います。
- データ取得の詳細は [RTX センサーアノテーター](06_rtx_annotators.md) を参照してください。
