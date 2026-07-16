---
title: 物理空間イベント生成（IRI）
---

# 物理空間イベント生成（IRI）

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- `Isaacsim.Replicator.Incident`（IRI）で都市シミュレーションシーンにイベントを生成する仕組み
- Event Scene Tagger でアイテムにイベントタグを付ける方法
- Topple（転倒）/ Fire（火災）/ Spill（液漏れ）の 3 イベントの設定
- IRI スタンドアロンと IRA 統合の 2 つのワークフロー
- イベントに対するエージェントの応答（Agent Response）の設定

## はじめに

### 前提条件

- Isaac Sim 5.1 が起動できること
- [アクター シミュレーションと SDG（IRA）](17_replicator_agent.md) を理解していること
- NavMesh の作成方法を把握していること

### 所要時間

約 20〜25 分

### 概要

**Isaacsim.Replicator.Incident（IRI）** は、都市シミュレーションシーンにイベントを生成する拡張機能です。[IRA](17_replicator_agent.md) と統合すると、シーン内のアクターにイベントとイベント応答を指定できます。現在サポートする自発的イベントは次の 3 種類です。

- **Box toppling（箱の転倒）**
- **Fire and smoke（火災と煙）**
- **Liquid spills（液漏れ）**

### 基本ワークフロー

1. **タグ付け**：イベントに関与させるアイテムを **Event Scene Tagger**（**Tools > Action and Event Data Generation > Event Scene Tagger**）で適切なイベント種別にタグ付けします（loose items / spillable items / flammable items）。
2. **シーン保存**：タグ情報を保存します（IRA で使う場合は必須）。タグ済みサンプルシーンが `[Isaac Sim Assets Path]/Isaac/Samples/Replicator/Incidents/full_warehouse_with_incident_tags.usd` にあります。
3. **イベント設定**：
    - **(3a) IRI スタンドアロン** … **Event Config File** ウィンドウでイベント設定ファイルを作成し、**Set Up Events** でイベントをトリガーするデーモンを読み込みます。
    - **(3b) IRA 統合** … **Actor SDG** ウィンドウの Events パネルで同じイベントをトリガーします。Response パネルでエージェント応答も指定できます。
4. **実行**：Play でプレビュー、または **Record Events**（スタンドアロン）/ **Start Data Generation**（IRA 統合）で SDG データを生成します。

!!! note "ビューポートカメラ"
    イベント中にビューポートカメラは自動調整されません。イベントを見るには手動でシーン内のイベント位置を探し、カメラを移動する必要があります。イベントアイテムには実行中にセマンティックラベルが付与され、別途イベントログ（YAML）も生成されます。

## ステップ 1：IRI スタンドアロン UI の例（棚から箱を落とす）

倉庫シーン `[Isaac Sim Assets Path]/Environments/Simple_Warehouse/full_warehouse.usd` から始めます。

![Topple イベントのウォークスルー](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_ext-isaacsim.replicator.incident-0.1.13_gui_ToppleEventFUllWalkthrough.webp)

1. 倉庫シーンを開き、NavMesh がベイクされていることを確認します（この例では転倒方向の決定に NavMesh を使います）。
2. **Event Scene Tagger** を開きます。
3. 棚の箱を選択し、**Tag Loose Items: Navmesh** で loose items としてタグ付けします。転倒時、箱は最も近い NavMesh 点（＝歩行可能エリア）に向かって落ちます。
4. （任意）進捗を保存します（IRA で使うなら必須）。
5. **Event Config File** ウィンドウを開き、デフォルトの Spill / Fire イベントを削除して topple イベント設定を確認します。topple アイテムは `$random_loose_item$`（シーン内の loose item をランダム選択）、トリガーは時間ベースで 3 秒です。
6. **Set Up Events** で topple デーモンを読み込み、Play して **Record Events** でデータ収集、**Stop Record** で停止します。指定した出力ディレクトリにイベントレポートが生成されます。

## ステップ 2：IRA 統合

1. スタンドアロン例のステップ 1・2 を実行します。
2. **Actor SDG** ウィンドウを開き、保存したシーンのパスを scene asset path に入力します。
3. スタンドアロンと同様に、ただし **Actor SDG の Events パネル**で topple イベントを追加します。
4. **Save As** でシーン構成を保存します。
5. **Set Up Simulation** でアクターとデーモンを読み込みます。Play でプレビュー、または **Start Data Generation** で IRA の SDG ライターと共に記録します。
6. （任意）**Response** パネルでイベントへのエージェント応答を追加します。例：topple イベントに `physical_event` 応答（イベント名と同名）を追加し、commands に次を入力すると、選択エージェントが転倒アイテムへ移動して周囲を見回します。

```text
GoToResponse
LookAround 10
```

## ステップ 3：シーンタグ付けの詳細

**Event Scene Tagger** で、アイテムを loose items / spillable items / flammable items にタグ付けします。

### Loose Items（転倒アイテム）

転倒時、タグ種別に応じた方向に力が加わります。

- **Random Direction** … ランダムな方向に力を加える。
- **NavMesh Direction** … 最も近い NavMesh エッジの方向に力を加える（棚やテーブル上のアイテムに有用）。
- **Closest Waypoint Direction** … 最も近い Waypoint 上の最近点の方向に力を加える。Waypoint は任意の位置に配置・リサイズできる箱で、歩行経路や通路を表します（**Add Waypoint Prim** で追加、scene パネルで不可視化可能）。
- **Untag Loose Items** … 選択アイテム（およびネストされたアイテム）の loose タグを解除。

### Flammable Items（可燃アイテム）

火災イベントの対象になるアイテムです。燃料源として、階層下に可視メッシュが必要です。

### Spillable Items（液漏れアイテム）

液漏れイベントの対象になるアイテムです。液漏れは、アイテムの下にある **spillable area** タグの prim 上に平らな液面を生成することで表現されます。**Spillable Area Floor** ボタンで床を spillable area としてタグ付けします（該当 prim が無い場合は高さ 0.0 の地面に生成）。

## ステップ 4：イベント設定（IRI スクリプト）

IRI はイベント設定を YAML スクリプトに保存し、直接編集できます。3 つのイベント（topple / fire / spill）を時間トリガーで定義する例です。

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

## ステップ 5：各イベント種別

### Topple Event（転倒）

![Topple イベント](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_ext-isaacsim.replicator.incident-0.1.0_viewport_topple_event.png)

- `name` … イベント名
- `topple_item.item` … 転倒させるアイテム（特定の prim パス、または `$random_loose_item$`）
- `topple_item.topple_nearby_radius` … この半径内の他の loose item も転倒
- `trigger` … トリガー（時間ベースなど）

転倒したアイテムにはセマンティックラベル `incident_toppled_item` が付与されます。

### Fire Event（火災）

![Fire イベント](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_ext-isaacsim.replicator.incident-0.1.0_viewport_pyro_event.png)

- `flammable_item.item` … 発火させるアイテム（特定 prim パス、または `$random_flammable_item$`）

可燃アイテムには `incident_flaming_item` が付与されます。炎自体を出力するにはカスタム Replicator ライターが必要です。

### Spill Event（液漏れ）

![Spill イベント](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_ext-isaacsim.replicator.incident-0.1.0_viewport_spill_event.png)

- `leakable_item.item` … 液漏れさせるアイテム（特定 prim パス、または `$random_leakable_item$`）
- `leakable_item.target_size` … 液漏れエリアのサイズ
- `leakable_item.leak_duration` … 液漏れの継続時間

液漏れアイテムには `incident_leaking_item`、液体自体には `incident_liquid_spill` が付与されます。

## SDG 収集とエージェント応答

**SDG 収集**：イベントアイテムのセマンティックラベルに基づき、Replicator の SDG ライターが処理します。追加情報は出力ディレクトリのイベントログ（YAML）に収集されます。IRA の設定では `semantic_filter_predicate` に `incident_*` ラベルを含めます。

![セマンティックラベル](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_ext-isaacsim.replicator.incident-0.1.0_viewport_semantic_label.png)

**エージェント応答**：IRA 設定ファイルの `response` セクションで定義します。各応答は `name`・`priority`・`pick_agent`（例：`nearest`）・`commands`・`trigger`（`type: physical_event`、`event_name` で対象イベントを指定）を持ちます。

```yaml
response:
    response_list:
    - CommandResponse:
        name: check out topple
        priority: 1
        pick_agent: nearest
        resume: true
        commands:
            - GoToResponse
            - LookAround 1
        trigger:
            type: physical_event
            event_name: my topple event
```

## まとめ

このチュートリアルでは、次の内容を学びました。

- IRI が topple / fire / spill の 3 イベントをシーンに生成すること
- Event Scene Tagger でアイテムをタグ付けし、方向（random / navmesh / waypoint）を指定すること
- IRI スタンドアロンと IRA 統合の 2 ワークフロー
- 各イベントの YAML 設定とセマンティックラベル、エージェント応答の定義

## 次のステップ

- カメラ配置の最適化は [RTX センサーの配置とキャリブレーション](21_sensors_rtx_placement.md) を参照してください。
