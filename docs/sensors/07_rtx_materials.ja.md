---
title: RTX センサー用の非可視マテリアル
---

# RTX センサー用の非可視マテリアル

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- 「非可視マテリアル（non-visual materials）」とは何か、なぜ RTX センサーで重要なのか
- USD 属性として非可視マテリアルを指定する方法（UI / Python）
- マテリアル ID がどのように計算され、アノテーターに公開されるか
- Non-Visual Material ID Debug View でマテリアル ID を可視化する方法
- 旧来の CSV マッピング方式（非推奨）とセンサーマテリアル種別

## はじめに

### 前提条件

- [RTX LiDAR センサー](04_rtx_lidar.md) / [RTX Radar センサー](05_rtx_radar.md) と [RTX センサーアノテーター](06_rtx_annotators.md) を理解していること
- Isaac Sim 5.1 が起動できること

### 所要時間

約 10〜15 分

### 概要

`omni.sensors.nv.materials` 拡張機能は、RTX センサーの**非可視スペクトル**で見えるマテリアルのレンダリングをサポートします。これらは **非可視マテリアル** と呼ばれます。

非可視マテリアルは **USD 属性**としてレンダリングされ、USD ファイルで指定できます。Isaac Sim は `isaacsim.sensors.rtx` 拡張機能に、これらの属性を Material prim に設定するのを簡単にする API を含んでいます。レンダラーは、指定された属性の組み合わせから各非可視マテリアルの**マテリアル ID** を計算します。このマテリアル ID は `GenericModelOutput` AOV から提供され、複数のアノテーターで公開されます（[RTX センサーアノテーター](06_rtx_annotators.md) を参照）。

## ステップ 1：非可視マテリアル属性を指定する

有効な非可視マテリアル属性の名前と値は、Omniverse Kit のドキュメントで規定されています。

### ユーザーインターフェースから指定する

**Stage** ウィンドウでマテリアルを右クリックし、**Add > Attribute** を選択すると、カスタムの非可視属性を指定するウィンドウが開きます。

![属性の追加ウィンドウ](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isaacsim_sensors_rtx_materials_new_attribute.png)

追加した属性は、マテリアルのプロパティに表示され、値を設定できるようになります。

![追加された非可視マテリアル属性](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isaacsim_sensors_rtx_materials_new_nva_property.png)

### Python から指定する

`isaacsim.sensors.rtx` には、Material prim に非可視マテリアル属性を設定する Python API がいくつか含まれています。次の Standalone 例が、これらの API の使い方を示します。

```bash
./python.sh standalone_examples/api/isaacsim.sensors.rtx/specify_non_visual_materials.py
```

実行すると、次のように各立方体が可視スペクトルで異なる色に表示されます。

![非可視マテリアルの例（デフォルトビュー）](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.1_full_tut_viewport_specify_non_visual_materials_base.png)

## ステップ 2：マテリアル ID を可視化する

ビューポートで **RTX - Real-Time > Debug View > Non-Visual Material ID** を選択すると、Non-Visual Material ID Debug View に切り替わります。

![Debug View メニュー](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.1_full_tut_viewport_specify_non_visual_materials_debug_view_menu.png)

Debug View では、各非可視マテリアルのマテリアル ID が色として表示され、シーン内のマテリアルを識別できます。

![Non-Visual Material ID Debug View](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.1_full_tut_viewport_specify_non_visual_materials_debug_view.png)

各立方体の色がデフォルトビューと変わり、立方体に適用された可視マテリアルの非可視マテリアル属性の組み合わせから計算されたマテリアル ID を反映していることが確認できます。

## ステップ 3：可視マテリアルへのマッピング（非推奨）

!!! warning "CSV マッピングは Isaac Sim 5.1 で非推奨"
    CSV 仕様による可視マテリアルから RTX センサー非可視マテリアルへのマッピングは、**Isaac Sim 5.1 で非推奨**になりました。デフォルトでは、非可視マテリアルは USD 属性で指定・レンダリングされます（ステップ 1・2 を参照）。ここでは参考として旧方式を紹介します。

可視スペクトルでレンダリングされるセンサーマテリアルは 21 種類あり、現時点でこれ以上追加することはできません。これらのプロパティは同名の JSON ファイル（`./data/material_files/` フォルダ内）に格納されています。

| Index | センサーマテリアル種別 | | Index | センサーマテリアル種別 |
|---|---|---|---|---|
| 0 | Default | | 11 | RetroMarkings |
| 1 | AsphaltStandard | | 12 | RetroSign |
| 2 | AsphaltWeathered | | 13 | RubberStandard |
| 3 | VegetationGrass | | 14 | SoilClay |
| 4 | WaterStandard | | 15 | ConcreteRough |
| 5 | GlassStandard | | 16 | ConcreteSmooth |
| 6 | FiberGlass | | 17 | OakTreeBark |
| 7 | MetalAlloy | | 18 | FabricStandard |
| 8 | MetalAluminum | | 19 | PlexiGlassStandard |
| 9 | MetalAluminumOxidized | | 20 | MetalSilver |
| 10 | PlasticStandard | | 31 | INVALID |

### センサーマテリアルマッピングの使い方（旧方式）

旧システムでは、Isaac Sim がマテリアル ID を上表のセンサーマテリアル種別にマッピングする方法を知っている必要があります。これはコマンドラインで次の carb 設定を行うことで実現します。

```bash
--/rtx/materialDb/rtSensorNameToIdMap="DefaultMaterial:0;AsphaltStandardMaterial:1;AsphaltWeatheredMaterial:2;...;MetalSilverMaterial:20"
```

`rtSensorNameToIdMap` を設定したら、`kit/rendering-data/runtime/RtxSensorMaterialMap.csv` を編集し、正確なマテリアル名トークンをセンサーマテリアル種別にマッピングします。この CSV は、マテリアル prim の部分名とセンサーマテリアル種別のペアを含みます。CSV は 1 つだけで、すべてのコンテンツのマッピングを制御し、Isaac Sim 起動時に読み込まれます（実行中の変更は再起動まで反映されません）。

例として、`/Root/SM_floor29/SM_floor02/SM_floor02` prim に `/Root/SM_floor29/Looks/MI_Floor_02b` というマテリアルが割り当てられている場合、この床を RTX センサーに対して粗いコンクリートとして見せるには、次のエントリを追加します。

```text
mi_floor_02b,ConcreteRoughMaterial
```

![マテリアルマッピングの例](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isaacsim_sensors_rtx_material_map.png)

!!! note "CSV 記述の注意点"
    - メッシュにアタッチされたマテリアル prim 名で、最初の `/Looks/` の直後に現れる最初のトークンが使われます。ステージ上の大文字小文字にかかわらず、CSV では**常に小文字**で記述します。
    - 上表のセンサーマテリアル種別に `Material` の語が連結される点にも注意してください（例：`ConcreteRough` → `ConcreteRoughMaterial`）。

### デバッグ

次の carb パラメータが役立ちます。

```text
[settings]
rtx.materialDb.rtSensorMaterialLogs=true
```

`true` にすると、シーン内でセンサーマテリアルにマッピングされて**いない**すべてのマテリアルの一覧が、Isaac Sim 起動時にターミナルとログに出力されます。

## まとめ

このチュートリアルでは、次の内容を学びました。

- 非可視マテリアルは RTX センサーの非可視スペクトルでの応答を定義し、USD 属性として指定すること
- UI（Add > Attribute）または Python API で非可視マテリアル属性を設定する方法
- マテリアル ID が属性の組み合わせから計算され、Debug View で色として可視化できること
- 旧来の CSV マッピング方式（非推奨）と 21 種類のセンサーマテリアル種別

## 次のステップ

- 物理ベースのセンサー（接触・IMU など）については [Physics ベースのセンサー](08_physics_sensors.md) を参照してください。
