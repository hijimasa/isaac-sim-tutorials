---
title: 物理空間イベント生成（IRI）
---

# 物理空間イベント生成（IRI）

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- `Isaacsim.Replicator.Incident`（IRI）で都市シミュレーションシーンにイベントを生成する仕組み
- **Incident Tagging**（プロパティの + Add メニュー）でアイテムにイベントタグを付ける方法
- Topple（転倒）/ Fire（火災）/ Spill（液漏れ）の 3 イベントの設定
- トリガー（time / carb_event / physical_event）の使い分け
- 標準化された**インシデントレポート（JSON）**の構造と Python API

## はじめに

### 前提条件

- Isaac Sim 6.0.1 が起動できること
- [Replicator の概要](01_replicator_overview.md) を理解していること
- NavMesh の作成方法を把握していること

!!! note "Isaac Sim 6.0 での変更点"
    5.1 まであった **Event Scene Tagger** ウィンドウは廃止され、タグ付けはプリムのプロパティの **+ Add > Incident Tagging** メニューから行います。また、IRA の `response` セクションによるエージェント応答の仕組みは IRA 1.x の再設計に伴い削除され、イベントの記録は標準化された **JSON のインシデントレポート**（既定 `incidents_report.json`）に書き出されるようになりました。

### 所要時間

約 20〜25 分

### 概要

**Isaacsim.Replicator.Incident（IRI）** は、都市シミュレーションシーンにイベントを生成する拡張機能です。現在サポートする自発的イベントは次の 3 種類です。

- **Box toppling（箱の転倒）**
- **Fire and smoke（火災と煙）**
- **Liquid spills（液漏れ）**

### 基本ワークフロー

1. **タグ付け**：イベントに関与させるアイテムを、プロパティのドロップダウンメニュー **+ Add > Incident Tagging** で適切なイベント種別（loose items / spillable items / flammable items）にタグ付けします。
2. **シーン保存**：シーンを閉じて開き直す予定がある場合は、タグ情報を USD ファイルとして保存します。タグ済みサンプルシーンが `[Isaac Sim Assets Path]/Isaac/Samples/Replicator/Incidents/full_warehouse_with_incident_tags.usd` にあります。
3. **イベント設定**：**Event Config File** ウィンドウでシーンに発生させるイベントを定義します。この設定は保存・再読み込みできますが、シーンの USD には保存されないため、Event Config File パネルの保存・読み込み機能で別途管理します。設定後、**Set Up Events** でイベントをトリガーするデーモンを読み込みます。
4. **実行**：Play でプレビュー、または **Record Events** で SDG データを生成します。イベントアイテムには実行中にセマンティックラベルが付与され、Replicator の SDG 収集を支援します。イベントの詳細は、別途 **JSON のインシデントレポート**（既定では出力ディレクトリの `incidents_report.json`）に記録されます。

!!! note "ビューポートカメラ"
    イベント中にビューポートカメラは自動調整されません。イベントを見るには手動でシーン内のイベント位置を探し、カメラを移動する必要があります。

!!! warning "火災イベントとマルチティックレンダリング"
    火災イベントで炎のエフェクトが正しくレンダリングされない場合は、マルチティックレンダリングを無効化してください。最も簡単なのは起動時のコマンドラインでの上書きです：Linux は `./isaac-sim.sh --/rtx/hydra/supportMultiTickRate=false`、Windows は `.\isaac-sim.bat --/rtx/hydra/supportMultiTickRate=false`。

## ステップ 1：IRI スタンドアロン UI の例（棚から箱を落とす）

倉庫シーン `[Isaac Sim Assets Path]/Environments/Simple_Warehouse/full_warehouse.usd` から始めます。

1. 倉庫シーンを開き、NavMesh がベイクされていることを確認します（この例では転倒方向の決定に NavMesh を使います）。
2. 棚の箱を選択し、**IncidentTagging > LooseItem > Navmesh** で loose items としてタグ付けします。転倒時、箱は最も近い NavMesh 点（＝歩行可能エリア）に向かって落ちます。
3. （任意）進捗を保存します。
4. **Event Config File** ウィンドウを開き、デフォルトの Spill / Fire イベントを削除して topple イベント設定を確認します。topple アイテムは `$random_loose_item$`（シーン内の loose item をランダム選択）、トリガーは時間ベースで 3 秒です。
5. **Set Up Events** で topple デーモンを読み込み、Play して **Record Events** でデータ収集、**Stop Record** で停止します。指定した出力ディレクトリにインシデントレポート（既定のファイル名 `incidents_report.json`）が書き出されます。

## ステップ 2：シーンタグ付けの詳細

プリムをステージウィンドウまたはビューポートで右クリックし、**+ Add > Incident Tagging** から loose items / spillable items / flammable items を選択してタグ付けします（このメニューは Property タブの **+ Add** ボタンからも使えます）。タグ情報を残すには **File > Save** でシーンを USD として保存します。

!!! tip "タグの可視化と解除"
    - タグ付け済みアイテムは、ビューポート上部の目のアイコンから **Show By Type > Incident Scene Tags** を有効にすると種別ごとに可視化できます。
    - タグの解除は、Property パネルの **Raw Usd Properties** セクションで `isaacsim_replicator_incident_attr:` で始まるプロパティを削除して行います。

### Loose Items（転倒アイテム）

転倒時、タグ種別に応じた方向に力が加わります。

- **Random Direction** … ランダムな方向に力を加える。
- **NavMesh Direction** … 最も近い NavMesh エッジの方向に力を加える（棚やテーブル上のアイテムに有用）。
- **Closest Waypoint Direction** … 最も近い Waypoint 上の最近点の方向に力を加える。Waypoint は任意の位置に配置・リサイズできる箱で、歩行経路や通路を表します。Waypoint の追加は、プロパティのドロップダウンメニューから **Create > Incident/Topple > Topple Destination** を選択します（リサイズ・複製して複雑な経路も作成可能）。

### Flammable Items（可燃アイテム）

火災イベントの対象になるアイテムです。燃料源として、階層下に可視メッシュが必要です。

### Spillable Items（液漏れアイテム）

液漏れイベントの対象になるアイテムです。液漏れは、アイテムの下にある **spillable area** タグの prim 上に平らな液面を生成することで表現されます（該当 prim が無い場合は高さ 0.0 の地面に生成）。

## ステップ 3：イベント設定（YAML）

IRI はイベント設定を YAML スクリプトに保存し、直接編集できます。このファイルは USD シーンの一部ではないため、Event Config File パネルの保存・読み込み機能で別途管理します。3 つのイベント（topple / fire / spill）を時間トリガーで定義する例です。

```yaml
isaacsim.replicator.incident:
version: 0.1.0
global:
    report_dir:
    seed: 654321
event:
    event_list:
    - ToppleEvent:
        name: my topple event
        topple_item:
            item: $random_loose_item$
            topple_nearby_radius: 1.5
        trigger:
            type: time
            time: 3
    - FireEvent:
        name: my fire event
        flammable_item:
            item: $random_flammable_item$
        trigger:
            type: time
            time: 6
    - SpillEvent:
        name: my spill event
        leakable_item:
            item: $random_leakable_item$
            target_size: 1.5
            leak_duration: 5.0
        trigger:
            type: time
            time: 9
```

### トリガーの種類

イベントを開始するトリガーを各イベントに設定します。現在サポートされるトリガーは次の 3 種類です。

| 種類 | 内容 | 例 |
|---|---|---|
| `time` | 指定時刻（秒）にイベント開始 | `trigger: {type: time, time: 1.5}` |
| `carb_event` | 指定した carb イベントの発生時に開始。**他の拡張機能と IRI イベントを統合する主要な手段** | `trigger: {type: carb_event, event_name: my_extension_custom_event}` |
| `physical_event` | 他の IRI イベントの開始をトリガーにする（`incident_name` で対象イベント名を指定） | `trigger: {type: physical_event, incident_name: MyFireEvent}` |

## ステップ 4：各イベント種別

### Topple Event（転倒）

![Topple イベント](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_5.0_full_ext-isaacsim.replicator.incident-0.1.0_viewport_topple_event.png)

- `name` … イベント名
- `topple_item.item` … 転倒させるアイテム（特定の prim パス、または `$random_loose_item$`）
- `topple_item.topple_nearby_radius` … この半径内の他の loose item も転倒
- `trigger` … トリガー（時間ベースなど）

転倒したアイテムにはセマンティックラベル `incident_toppled_item` が付与されます。

### Fire Event（火災）

![Fire イベント](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_5.0_full_ext-isaacsim.replicator.incident-0.1.0_viewport_pyro_event.png)

- `flammable_item.item` … 発火させるアイテム（特定 prim パス、または `$random_flammable_item$`）

可燃アイテムには `incident_flaming_item` が付与されます。炎自体を出力するにはカスタム Replicator ライターが必要です。YAML のトリガーで指定する開始時刻は秒単位ですが、インシデントレポートの JSON では `trigger_data` にトリガー情報、`simulation_data` に火災固有のデータ（フレーム単位の `start_time` と、炎エミッタ prim の `fire_prim`）が記録されます。

### Spill Event（液漏れ）

![Spill イベント](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_5.0_full_ext-isaacsim.replicator.incident-0.1.0_viewport_spill_event.png)

- `leakable_item.item` … 液漏れさせるアイテム（特定 prim パス、または `$random_leakable_item$`）
- `leakable_item.target_size` … 液漏れエリアのサイズ
- `leakable_item.leak_duration` … 液漏れの継続時間

液漏れアイテムには `incident_leaking_item`、液体自体には `incident_liquid_spill` が付与されます。

## SDG 収集とインシデントレポート（JSON）

**SDG 収集**：イベントアイテムのセマンティックラベルに基づき、Replicator の SDG ライターが処理します。`semantic_filter_predicate` に `incident_*` ラベルを含めます。

![セマンティックラベル](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_5.0_full_ext-isaacsim.replicator.incident-0.1.0_viewport_semantic_label.png)

**インシデントレポート**：イベント記録時に書き出される構造化メタデータは **JSON** です（`isaacsim.replicator.incident.core` の `IncidentReport.start_recording` を使用。既定のファイル名 `incidents_report.json`、`file_name` 引数で変更可能）。Event Config File で保存・読み込みするイベント設定の YAML とは別物です。

トップレベルのキーはイベント名で、各イベントのエントリには次のセクションが含まれ得ます（いずれもオプション）。

| セクション | 内容 |
|---|---|
| `event_data` | 設定・セットアップ由来のイベント固有フィールド |
| `trigger_data` | トリガー経由で起動された場合に存在。`type`・`priority`・`time`（**秒**単位）などを持つ `trigger` オブジェクトを含む |
| `simulation_data` | シミュレーションタイムラインのメタデータ。**フレーム番号（整数）**単位（秒ではないので注意） |

イベント種別ごとの `simulation_data`：Topple と Spill は `start_time` / `end_time`（フレーム。Topple の `end_time` はアイテムが静止したとみなされた時点、Spill は `trigger_time + leak_duration` 相当まで）、Fire は `start_time`（着火フレーム）と `fire_prim`（FlowEmitterBox エミッタ prim の USD パス）のみで `end_time` はありません。パーサは `simulation_data` のキーをイベント種別固有として扱い、欠けているセクションを許容する実装にしてください。

## Python API

`isaacsim.replicator.incident.core` を有効化すると、自作スクリプトから各インシデントをセットアップできます。`get_instance().get_incident_manager()` でインシデントマネージャを取得し、`omni.metropolis.pipeline.triggers` の `TriggersManager` でトリガーを作成、`ApplyLooseItemTagCommand` / `ApplyFlammableItemTagCommand` / `ApplyLeakableItemTagCommand` / `ApplySpillableAreaTagCommand` の各 Kit コマンドでプリムにタグを付け、`create_topple_event_manager()` / `create_pyro_event_manager()` / `create_spill_event_manager()` からイベントを生成します（完全な例は公式ページを参照）。

## まとめ

このチュートリアルでは、次の内容を学びました。

- IRI が topple / fire / spill の 3 イベントをシーンに生成すること
- プロパティの **+ Add > Incident Tagging** でアイテムをタグ付けし、方向（random / navmesh / waypoint）を指定すること
- イベント設定 YAML と 3 種類のトリガー（time / carb_event / physical_event）
- セマンティックラベルによる SDG 収集と、標準化されたインシデントレポート（`incidents_report.json`）の構造
- Python API によるプログラムからのイベントセットアップ

## 次のステップ

- カメラ配置の最適化は [RTX センサーの配置とキャリブレーション](21_sensors_rtx_placement.md) を参照してください。
