---
title: RTX Radar センサー
---

# RTX Radar センサー

![倉庫内の RTX Radar](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isaacsim_sensors_rtx_radar_node_overview_warehouse.png)

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- RTX Radar が `OmniRadar` prim としてレンダリングされる仕組み
- `IsaacSensorCreateRtxRadar` コマンドで RTX Radar を作成する方法
- アノテーターで Radar の結果を可視化する方法
- Radar の戻り値がマテリアルプロパティに依存すること

## はじめに

### 前提条件

- [RTX センサー](03_rtx_sensors.md) の概要（特に Radar には Motion BVH が必須）を理解していること
- Isaac Sim 5.1 が RTX 対応 GPU で起動できること

### 所要時間

約 10 分

### 概要

RTX Radar センサーは、RTX ハードウェア上で**レンダリング時に GPU でシミュレート**されます。その結果は `GenericModelOutput` AOV にコピーされて利用されます。

RTX Radar は、`OmniSensorGenericRadarWpmDmatAPI` スキーマを適用した **`OmniRadar` prim** としてレンダリングされます。`OmniRadar` prim にレンダープロダクトをアタッチし、`GenericModelOutput` AOV を設定すると、RTXSensor レンダラーが Radar のレンダリング結果を AOV へ書き込みます。

!!! warning "ドップラー効果には Motion BVH が必須"
    RTX Radar のドップラー効果（したがって Radar 全体）を正しくモデル化するには、**Motion BVH を有効にする**必要があります。有効化の方法は [RTX センサー](03_rtx_sensors.md#motion-bvh) を参照してください。

!!! note "Camera prim ベースの Radar は非推奨"
    Isaac Sim 4.5 以前では、Radar は Camera prim ベースでした（`sensorModelPluginName` を `omni.sensors.nv.radar.wpm_dmatapprox.plugin` に設定）。この方式は **Isaac Sim 5.0 で非推奨**となりました。

## ステップ 1：RTX Radar を作成する

`isaacsim.sensors.rtx` 拡張機能は、RTX Radar を作成する 1 つの API を提供します。さらに低レベルな API は `omni.replicator.core` 拡張機能が提供します。

`IsaacSensorCreateRtxRadar` コマンドは、適切なスキーマを適用した汎用 `OmniRadar` prim、または非推奨ワークフロー用の Camera prim を作成します。

```python
import omni
from pxr import Gf

# OmniRadar prim に適用する属性を指定
sensor_attributes = {'omni:sensor:tickRate': 10}

_, sensor = omni.kit.commands.execute(
    "IsaacSensorCreateRtxRadar",
    translation=Gf.Vec3d(0, 0, 0),
    orientation=Gf.Quatd(1, 0, 0, 0,),
    path="/radar",
    parent=None,
    visibility=False,
    variant=None,
    force_camera_prim=False,
    **sensor_attributes,
)
```

![コマンドで RTX Radar を作成](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_ext-isaacsim.sensors.rtx-15.1.1_gui_rtx_radar_create_command.png)

上の例は、`OmniRadar` prim を `/radar` に作成し、指定した位置・姿勢に配置します。prim はステージ上で不可視に設定され、`tickRate` 属性はデフォルトの 20 Hz から 10 Hz に設定されます。設定できる属性は `omni.usd.schema.omni_sensors` 拡張機能の `OmniSensorGenericRadarWpmDmatAPI` スキーマを参照してください。

!!! note
    `force_camera_prim=True` にすると、代わりに不可視の Camera prim を作成します（非推奨ワークフロー用）。

## ステップ 2：データを収集する

`OmniRadar` prim にアノテーターをアタッチすると、Radar の結果を可視化できます。利用可能なアノテーターの詳細は [RTX センサーアノテーター](06_rtx_annotators.md) を参照してください。

## ステップ 3：センサーマテリアル

RTX Radar のマテリアルシステムでは、USD ステージ上の部分的なマテリアル prim 名にセンサーマテリアル種別を割り当てられます。Radar の戻り値の挙動は、マテリアルのプロパティ（放射率・反射率など）に依存します。詳細は [RTX センサー用の非可視マテリアル](07_rtx_materials.md) を参照してください。

## Standalone 例

RTX Radar を作成する例は次のとおりです。

```bash
./python.sh standalone_examples/api/isaacsim.util.debug_draw/rtx_radar.py
```

## まとめ

このチュートリアルでは、次の内容を学びました。

- RTX Radar は `OmniRadar` prim としてレンダリングされ、結果は `GenericModelOutput` AOV に書き込まれること
- `IsaacSensorCreateRtxRadar` コマンドで RTX Radar を作成する方法
- ドップラー効果には Motion BVH が必須であること
- Radar の戻り値がマテリアルの放射率・反射率に依存すること

## 次のステップ

- [RTX センサーアノテーター](06_rtx_annotators.md) で、RTX センサーの出力データの取得方法を学びます。
