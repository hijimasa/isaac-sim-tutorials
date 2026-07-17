---
title: RTX センサー用の非可視マテリアル
---

# RTX センサー用の非可視マテリアル

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- 「非可視マテリアル（non-visual materials）」とは何か、なぜ RTX センサーで重要なのか
- USD 属性として非可視マテリアルを指定する方法（UI / Python の `NonVisualMaterial` クラス）
- マテリアル ID がどのように計算され、アノテーターに公開されるか
- Non-Visual Material ID Debug View でマテリアル ID を可視化する方法
- 旧来の CSV マッピング方式が削除されたこと

## はじめに

### 前提条件

- [RTX LiDAR センサー](04_rtx_lidar.md) / [RTX Radar センサー](05_rtx_radar.md) と [RTX センサーアノテーター](06_rtx_annotators.md) を理解していること
- Isaac Sim 6.0 が起動できること

### 所要時間

約 10〜15 分

### 概要

`omni.sensors.nv.materials` 拡張機能は、RTX センサーの**非可視スペクトル**で見えるマテリアルのレンダリングをサポートします。これらは **非可視マテリアル** と呼ばれます。

非可視マテリアルは **USD 属性**としてレンダリングされ、USD ファイルで指定できます。Isaac Sim には、これらの属性を Material prim に簡単に設定できる **`isaacsim.core.experimental.materials.NonVisualMaterial`** クラスが含まれています。レンダラーは、指定された属性の組み合わせから各非可視マテリアルの**マテリアル ID** を計算します。このマテリアル ID は `GenericModelOutput` AOV から提供され、複数のアノテーターで公開されます（[RTX センサーアノテーター](06_rtx_annotators.md) を参照）。

## ステップ 1：非可視マテリアル属性を指定する

有効な非可視マテリアル属性の名前と値は、Omniverse Kit のドキュメントで規定されています。

### ユーザーインターフェースから指定する

**Stage** ウィンドウでマテリアルを右クリックし、**Add > Attribute** を選択すると、カスタムの非可視属性を指定するウィンドウが開きます。

![属性の追加ウィンドウ](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isaacsim_sensors_rtx_materials_new_attribute.png)

追加した属性は、マテリアルのプロパティに表示され、値を設定できるようになります。

![追加された非可視マテリアル属性](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isaacsim_sensors_rtx_materials_new_nva_property.png)

### Python から指定する

`isaacsim.core.experimental.materials.NonVisualMaterial` クラスは、Material prim に非可視マテリアル属性を設定する Python API を提供します。次の Standalone 例が、この API の使い方を示します（詳細はソースコードを参照してください）。

```bash
./python.sh standalone_examples/api/isaacsim.sensors.experimental.rtx/apply_nonvisual_materials.py
```

実行すると、次のように各立方体が可視スペクトルで異なる色に表示されます。

![非可視マテリアルの例（デフォルトビュー）](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_5.1_full_tut_viewport_apply_nonvisual_materials_base.png)

## ステップ 2：マテリアル ID を可視化する

ビューポートで **RTX - Real-Time > Debug View > Non-Visual Material ID** を選択すると、Non-Visual Material ID Debug View に切り替わります。

![Debug View メニュー](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_5.1_full_tut_viewport_apply_nonvisual_materials_debug_view_menu.png)

Debug View では、各非可視マテリアルのマテリアル ID が色として表示され、シーン内のマテリアルを識別できます。

![Non-Visual Material ID Debug View](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_5.1_full_tut_viewport_apply_nonvisual_materials_debug_view.png)

各立方体の色がデフォルトビューと変わり、立方体に適用された可視マテリアルの非可視マテリアル属性の組み合わせから計算されたマテリアル ID を反映していることが確認できます。

!!! note "属性変更後はステージの再読み込みが必要"
    Material prim の非可視マテリアル属性を変更した場合、変更を反映するにはステージを保存して再読み込みする必要があります。

## 旧方式：CSV による可視マテリアルのマッピング（削除済み）

!!! warning "CSV マッピングは削除されました"
    CSV 仕様（`RtxSensorMaterialMap.csv` と carb 設定 `rtx.materialDb.rtSensorNameToIdMap` / `rtx.materialDb.rtSensorMaterialLogs` を組み合わせるワークフロー）による可視マテリアルから RTX センサー非可視マテリアルへのマッピングは、Isaac Sim 5.1 で非推奨となり、**現在はサポートされていません**。これらの設定と CSV ファイルは無視されます。非可視マテリアルは、上記の手順どおり **USD 属性**（`omni:simready:nonvisual:*`）で指定してください。移行の詳細は公式の [RTX Sensors 移行ガイド](https://docs.isaacsim.omniverse.nvidia.com/latest/migration_guides/isaac_sim_6_0/sensors_rtx_to_experimental_rtx.html) を参照してください。

## まとめ

このチュートリアルでは、次の内容を学びました。

- 非可視マテリアルは RTX センサーの非可視スペクトルでの応答を定義し、USD 属性として指定すること
- UI（Add > Attribute）または Python の `NonVisualMaterial` クラスで非可視マテリアル属性を設定する方法
- マテリアル ID が属性の組み合わせから計算され、Debug View で色として可視化できること（属性変更後はステージ再読み込みが必要）
- 旧来の CSV マッピング方式は削除され、USD 属性方式に一本化されたこと

## 次のステップ

- 物理ベースのセンサー（接触・IMU など）については [Physics ベースのセンサー](08_physics_sensors.md) を参照してください。
