---
title: RTX LiDAR センサー
---

# RTX LiDAR センサー

![倉庫内の RTX LiDAR](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_full_ref_viewport_rtx_lidar_warehouse.png)

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- RTX LiDAR が `OmniLidar` prim としてレンダリングされる仕組み
- `IsaacSensorCreateRtxLidar` コマンド（低レベル）と `LidarRtx` クラス（高レベル）で RTX LiDAR を作成する方法
- Replicator アノテーターで LiDAR データを収集する方法
- RTX LiDAR アセットライブラリから実機モデルを読み込む方法
- 旧来の JSON 設定ファイルを `OmniLidar` USD に変換する方法

## はじめに

### 前提条件

- [RTX センサー](03_rtx_sensors.md) の概要（RTX Sensor SDK、Motion BVH）を理解していること
- Isaac Sim 5.1 が RTX 対応 GPU で起動できること

### 所要時間

約 15〜20 分

### 概要

RTX LiDAR センサーは、RTX ハードウェア上で**レンダリング時に GPU でシミュレート**されます。その結果は `GenericModelOutput` AOV にコピーされて利用されます。

RTX LiDAR は、`OmniSensorGenericLidarCoreAPI` スキーマを適用した **`OmniLidar` prim** としてレンダリングされます。`OmniLidar` prim にレンダープロダクトをアタッチし、そのレンダープロダクトに `GenericModelOutput` AOV を設定すると、RTXSensor レンダラーが LiDAR のレンダリング結果を AOV へ書き込みます。

!!! warning "Camera prim ベースの LiDAR は非推奨"
    Isaac Sim 4.5 以前では、RTX センサーは Camera prim ベースでした（`sensorModelPluginName` / `sensorModelConfig` 属性で設定）。Camera prim を RTX LiDAR として使う方式は **Isaac Sim 5.0 で非推奨**となりました。既存の JSON 設定は、後述の手順で `OmniLidar` prim を含む USD に変換できます。

このチュートリアルは、次の流れで進みます。

1. **コマンド**または **`LidarRtx` クラス**で RTX LiDAR を作成する
2. **アノテーター**でデータを収集する
3. **アセットライブラリ**から実機モデルを読み込む
4. **JSON → USD 変換**ツールを使う

## ステップ 1：RTX LiDAR を作成する

`isaacsim.sensors.rtx` 拡張機能は、RTX LiDAR を作成する 2 つの API を提供します。さらに低レベルな API は `omni.replicator.core` 拡張機能が提供し、`OmniLidar` prim の一括作成やレンダープロダクトのアタッチが行えます。

### コマンドで作成する

低レベルの `IsaacSensorCreateRtxLidar` コマンドは、既知の LiDAR USD/USDA アセット、適切なスキーマを適用した汎用 `OmniLidar` prim、または非推奨ワークフロー用の Camera prim への参照をステージ上に作成します。

```python
import omni
from pxr import Gf

# OmniLidar prim に適用する属性を指定
sensor_attributes = {'omni:sensor:Core:scanRateBaseHz': 20}

_, sensor = omni.kit.commands.execute(
    "IsaacSensorCreateRtxLidar",
    translation=Gf.Vec3d(0, 0, 0),
    orientation=Gf.Quatd(1, 0, 0, 0,),
    path="/lidar",
    parent=None,
    config="Example_Rotary",
    visiblity=False,
    variant=None,
    force_camera_prim=False,
    **sensor_attributes,
)
```

![コマンドで RTX LiDAR を作成](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_ext-isaacsim.sensors.rtx-15.1.1_gui_rtx_lidar_create_command.png)

上の例は、`Example_Rotary.usda` への参照を `OmniLidar` prim として `/lidar` に作成し、指定した位置・姿勢に配置します。prim はステージ上で不可視に設定され、`scanRateBaseHz` はデフォルトの 10 Hz から 20 Hz に変更されます。

!!! note "主なパラメータ"
    - `force_camera_prim=True` にすると、代わりに `sensorModelConfig` を設定した不可視の Camera prim を作成します（非推奨ワークフロー用）。
    - `config=None` にすると、`OmniSensorGenericLidarCoreAPI` スキーマを適用した汎用 `OmniLidar` prim を作成します。追加のキーワード引数は prim の属性として設定されます。
    - エミッター状態の属性を指定する場合は、属性名にエミッター状態カウントの接頭辞を付けます（例：`OmniSensorGenericLidarCoreEmitterStateAPI:s001:elevationDeg`）。

### LidarRtx クラスで作成する

高レベルの `LidarRtx` クラスは、RTX LiDAR を作成・設定する Python インターフェースを提供します。`IsaacSensorCreateRtxLidar` コマンドに引数を渡すのに加え、生成された `OmniLidar` prim を自動的にラップしてレンダープロダクトをアタッチします。アノテーターやライターをアタッチする API、`get_data` メソッドで毎フレームの結果を辞書として読み取る API も備えています。

```python
import numpy as np
import omni
from isaacsim.sensors.rtx import LidarRtx

sensor_attributes = {'omni:sensor:Core:scanRateBaseHz': 20}

# 指定した属性で RTX LiDAR を作成
sensor = LidarRtx(
    prim_path="/lidar",
    translation=np.array([0.0, 0.0, 1.0]),
    orientation=np.array([1.0, 0.0, 0.0, 0.0]),
    config_file_name="Example_Rotary",
    **sensor_attributes,
)
```

![LidarRtx クラスで RTX LiDAR を作成](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_ext-isaacsim.sensors.rtx-15.1.1_gui_rtx_lidar_create_lidar_rtx.png)

## ステップ 2：RTX LiDAR からデータを収集する

RTX LiDAR からデータを収集する推奨方法は、**Replicator アノテーター**を使うことです。Isaac Sim は複数の [RTX センサーアノテーター](06_rtx_annotators.md) を提供しています。`LidarRtx` クラスは、これらのアノテーターや `GenericModelOutput` アノテーターを、ラップしている `OmniLidar` prim にアタッチする API を提供します。

## ステップ 3：RTX LiDAR アセットライブラリ

Isaac Sim には実機の RTX LiDAR モデルライブラリが含まれており、`IsaacSensorCreateRtxLidar` の `config` / `variant` パラメータ、または `LidarRtx` の `config_file_name` パラメータで指定して読み込めます。`config` には次のいずれかを指定できます。

- LiDAR モデル USD ファイルの正確な名前（拡張子なし。例：`HESAI_XT32_SD10`）
- 上記のアンダースコアをスペースに置換したもの（例：`HESAI XT32 SD10`）
- ベンダー名を省いたもの（例：`XT32_SD10`）
- ベンダー名を省き、アンダースコアをスペースに置換したもの（例：`XT32 SD10`。Create メニューの表示名と一致）

省略可能な `variant` で、モデルの特定バリアントを選択できます。次の例は SICK picoScan150 を `Normal_11` バリアントで読み込みます。

```python
import omni
from pxr import Gf

_, sensor = omni.kit.commands.execute(
    "IsaacSensorCreateRtxLidar",
    path="/lidar",
    config="picoScan150",
    variant="Normal_11",
)
```

## ステップ 4：センサーマテリアルと JSON → USD 変換

### センサーマテリアル

RTX LiDAR のマテリアルシステムでは、USD ステージ上の部分的なマテリアル prim 名にセンサーマテリアル種別を割り当てられます。LiDAR の戻り値の挙動は、マテリアルのプロパティ（放射率・反射率など）に依存します。詳細は [RTX センサー用の非可視マテリアル](07_rtx_materials.md) を参照してください。

### JSON ファイルを OmniLidar USD に変換する

Isaac Sim には、旧来の JSON LiDAR 設定ファイルを `OmniLidar` prim を含む USD に自動変換するユーティリティが付属しています。

```bash
./python.sh tools/isaacsim.sensors.rtx/convert_lidar_json_to_usda.py
```

`-h` / `--help` フラグで使い方が表示されます。このツールは複数の JSON ファイルを対応する USD に変換し、同一 LiDAR モデルのバリアント設定を USD バリアントセットを使って 1 つの USD にまとめることもできます。

## Standalone 例

RTX LiDAR の作成・データ収集の例は次のとおりです。

```bash
./python.sh standalone_examples/api/isaacsim.ros2.bridge/rtx_lidar.py
./python.sh standalone_examples/api/isaacsim.sensors.rtx/inspect_lidar_metadata.py
./python.sh standalone_examples/api/isaacsim.sensors.rtx/resolve_object_ids_from_gmo.py
./python.sh standalone_examples/api/isaacsim.sensors.rtx/rotating_lidar_rtx.py
./python.sh standalone_examples/api/isaacsim.util.debug_draw/rtx_lidar.py --config Example_Rotary
./python.sh standalone_examples/api/isaacsim.util.debug_draw/rtx_lidar.py --config Example_Solid_State
```

## まとめ

このチュートリアルでは、次の内容を学びました。

- RTX LiDAR は `OmniLidar` prim としてレンダリングされ、結果は `GenericModelOutput` AOV に書き込まれること
- `IsaacSensorCreateRtxLidar` コマンドと `LidarRtx` クラスで RTX LiDAR を作成する方法
- アノテーターでデータを収集し、アセットライブラリから実機モデルを読み込む方法
- 旧 JSON 設定を `OmniLidar` USD に変換する方法

## 次のステップ

- [RTX Radar センサー](05_rtx_radar.md) で、電波スペクトルのセンサーを扱います。
- データ取得の詳細は [RTX センサーアノテーター](06_rtx_annotators.md) を参照してください。
