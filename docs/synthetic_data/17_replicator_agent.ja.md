---
title: アクター シミュレーションと合成データ生成（IRA）
---

# アクター シミュレーションと合成データ生成（IRA）

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- `Isaacsim.Replicator.Agent`（IRA）拡張機能で人物・ロボットの合成データを生成する仕組み
- IRA の有効化とクイックスタートの流れ
- 設定ファイル（YAML）の各セクションの意味
- UI とスクリプトからのデータ生成方法

## はじめに

### 前提条件

- Isaac Sim 5.1 がインストール済みで起動できること
- Replicator の基礎（[Replicator の概要](01_replicator_overview.md)）を理解していること
- NavMesh（Navigation Mesh：キャラクターやロボットが歩行可能な領域を表すメッシュ）の作成方法を把握していること

### 所要時間

約 20〜30 分

### 概要

さまざまな環境で人を検出・追跡することは、多くの産業で大きな価値を持ちます（小売の客動線分析、倉庫/工場のレイアウト最適化、人とロボットの協調作業の安全性検証など）。しかし、実世界データの収集はコストが高くスケールしません。

**Isaacsim.Replicator.Agent（IRA）** 拡張機能は、多様な 3D 環境で**人物キャラクターとロボット**の合成データを生成します。設定ファイルとコマンドファイルを通じて、環境・カメラパラメータ・キャラクター・ロボットのモーションを制御でき、2D/3D の各種アノテーション（RGB カメラ、ステレオカメラなど）を出力します。IRA では、人物キャラクターとロボットをまとめて **agent（アクター）** と呼びます。

![IRA の概要](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_full_ext-isaacsim.replicator.agent-5.0.0_viewport_IRA_overview.png)

!!! note "ベータ機能"
    Isaacsim.Replicator.Agent はベータ版です。IRA は `omni.anim.graph` / `omni.anim.navigation` / `omni.replicator.core` を利用する Kit 拡張機能で、Omniverse エコシステムと互換性があります。

## ステップ 1：IRA を有効化する

1. Omniverse Extension Manager で `isaacsim.replicator.agent.core` と `isaacsim.replicator.agent.ui` を有効化します。
2. 拡張機能は起動時に Isaac Sim Assets からサンプルアセットを取得します。
3. UI パネルは **Tools > Action and Event Data Generation > Actor SDG** から開けます（画面右側に表示）。

![IRA UI の場所](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_full_ext-isaacsim.replicator.agent-5.0.0_viewport_IRA_UI_location.png)

!!! tip
    - 起動時に自動ロードするには、Extension Manager で autoload をチェックします（依存関係のため Isaac Sim の再起動が必要な場合があります）。
    - UI のロードがハングするように見える場合は、`--/persistent/isaac/asset_root/timeout=1.0` フラグ付きで起動してみてください。

## ステップ 2：クイックスタート

1. IRA 拡張機能を有効化し、UI パネルを開きます。
2. 設定ファイルを読み込むか、拡張機能付属のデフォルト設定ファイルを使います（`[Isaac Sim App Path]/extscache/isaacsim.replicator.agent.core-[version]/config/default_config.yaml`。起動時に自動ロードされます）。
3. UI 上部の **Set Up Simulation** をクリックしてシミュレーションアセットを読み込みます（時間がかかります）。
4. Character パネルの **Generate Random Commands** でコマンドを生成し、ディスクアイコンで保存します。
5. UI 上部の **Start Data Generation** でシミュレーションとデータ生成を開始します（SDG Setup パネルの Simulation Length に従って進行）。
6. 出力データは Replicator パネルの Output Directory から確認できます。

![Set Up Simulation](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_ext-isaacsim.replicator.agent-0.7.1_gui_IRA_getting_started_set_up_simulation.png)

## ステップ 3：設定ファイル（YAML）

設定ファイルはシミュレーションを定義する中心的なデータで、次のセクションを持ちます。構造は固定ですが、各プロパティ・セクションの順序は変えられます。一部のセクション（character / robot / response / incident）はオプションです。

```yaml
isaacsim.replicator.agent:
version: 0.7.1
global:
    seed: 123456
    simulation_length: 300
scene:
    asset_path: [Isaac Sim Assets Path]/Isaac/Environments/Simple_Warehouse/full_warehouse.usd
sensor:
    camera_num: 5
character:  # オプション
    asset_path: [Isaac Sim Assets Path]/Isaac/People/Characters/
    command_file: default_command.txt
    filters:
        - "male"
        - "medical"
    num: 10
    spawn_area:
        - "Walkable"
    navigation_area:
        - "Walkable"
robot:  # オプション
    command_file: default_robot_command.txt
    nova_carter_num: 0
    iw_hub: 0
    write_data: false
response:  # オプション
    response_list: []
incident:  # オプション
    incident_list: []
replicator:
    writer: IRABasicWriter
    parameters:
        output_dir:
        rgb: true
        object_info_bounding_box_2d_tight: true
        object_info_bounding_box_2d_loose: true
        object_info_bounding_box_3d: true
```

### 各セクションの意味

| セクション | 主な内容 |
|---|---|
| **global** | `seed`（乱数シード。空なら現在時刻）、`simulation_length`（フレーム数。30 FPS 前提。例：300 フレーム = カメラあたり 10 秒） |
| **scene** | `asset_path`（環境 USD へのパス。キャラクターやカメラを含んでもよい） |
| **sensor** | `camera_num`（データ取得するカメラ数。`-1` で `/World/Cameras` 以下の全カメラ）または `camera_list`（prim パスのリスト。両者は排他） |
| **character** | `num`（人数）、`asset_path`（キャラクターアセットフォルダ）、`command_file`、`filters`（`filter.json` によるフィルタ）、`spawn_area` / `navigation_area`（NavMesh エリア） |
| **robot** | `nova_carter_num` / `iw_hub`（台数）、`command_file`、`write_data`（各ロボットの先頭 2 カメラ出力の有無） |
| **response** | アクターが実行する応答のリスト |
| **incident** | 発生させるインシデントのリスト（`isaacsim.replicator.incident` の incident セクションと同構造。[イベント生成](20_replicator_incident.md) 参照） |
| **replicator** | `writer`（使用ライター）と `parameters`（ライターの initialize 引数） |

!!! warning "カメラ数と VRAM"
    - データ生成のカメラ数はシステムの VRAM に制限されます。`Cannot create cuda external memory for resource` 等が出たら `camera_num` を減らします。
    - `Too many open files` 等が出る場合は、ファイルディスクリプタの上限を引き上げます（例：`HARD_LIMIT=\`ulimit -Hn\`; ulimit -Sn $HARD_LIMIT`）。
    - `spawn_area` と `navigation_area` が異なる場合、アクターの最初のコマンドは navigation_area への移動になります。

### 最小構成

最小限必要なのは拡張機能ヘッダとバージョンだけです。他のフィールドは未指定ならデフォルト値が自動生成されます。

```yaml
isaacsim.replicator.agent:
version: 0.7.1
```

!!! note "バージョン整合"
    設定ファイルの version は拡張機能のマイナーバージョンと一致する必要があります（例：`0.1.12` は `0.1.11` と動作するが `0.0.12` は不可）。

## ステップ 4：データ生成

### UI から生成する

UI ではシミュレーションと生成設定のすべての属性を細かく制御できます。設定ファイルの全フィールドは UI から直接編集でき、UI の各フィールドは設定ファイルの対応フィールドを持ちます。

- UI で変更すると Save File ボタンに「\*」が付きます。**保存するまで設定ファイルには書き込まれません**（未保存は青、無効入力は赤で表示）。未保存の変更がある場合、Set Up Simulation / Start Data Generation はディスク上のファイルではなく UI 表示の情報に従います。
- アセット（シーン・キャラクター・カメラ）は **Set Up Simulation** をクリックするまで読み込まれません。

!!! note "NavMesh が必須"
    シミュレーションのセットアップ前に、アクターを正しくスポーン・制御するためステージに **NavMesh** が必要です。**Window > Navigation > NavMesh** で Auto-Bake をオフにするとパフォーマンスが向上します。

![NavMesh の Auto-Bake をオフ](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_full_ext-isaacsim.replicator.agent-5.0.0_viewport_disable_navmesh_autobake.png)

- アクターのコマンドを編集します。**Generate Random Commands** でランダムコマンドを生成し、**Save Commands** で保存します（**コマンドは保存しないと反映されません**）。
- 準備ができたら **Start Data Generation** で開始します。`simulation_length` 分のデータが生成されると自動停止します。途中終了は **Stop Data Generation** です。

!!! warning
    Stop Data Generation の後、Replicator の停止に時間がかかることがあります。停止完了前にすぐ Start Data Generation すると固まる場合があるため、停止完了を待ってください。

### スクリプトから生成する

大規模生成では、スクリプトからの起動が効率的です。IRA はオフライン生成用の自動スクリプト `sdg_scheduler.py` を提供します。

```bash
# Linux
./python.sh tools/actor_sdg/sdg_scheduler.py -c [config file path]
# Windows
.\python.bat tools\actor_sdg\sdg_scheduler.py -c [config file path]
```

!!! note
    - Isaac Sim 付属の `python.sh` / `python.bat` を使う必要があります。
    - サンプル設定ファイルは `/tools/actor_sdg` フォルダにあります（例：`-c tools/actor_sdg/default_config.yaml`）。
    - `--save_usd` フラグを付けると、Set Up Simulation 後の USD を出力ディレクトリに書き出します（アクター・センサー位置の復元に便利）。

## 用語

| 用語 | 説明 |
|---|---|
| core 拡張機能 | シミュレーション状態を管理。API とモジュールを含み、独立して呼び出せる |
| UI 拡張機能 | IRA の UI。ロード時に core も自動ロードされる |
| 設定ファイル（.yaml） | シード・長さ・アクター数・出力形式などを定義 |
| コマンドファイル（.txt） | 各行が「アクター名＋コマンド名＋パラメータ」。`omni.anim.people` / `isaacsim.anim.robot` 経由でアクターを制御 |
| actor / agent | 本ドキュメントでは同義。人物キャラクターとロボット（Nova Carter、iw.hub） |

## まとめ

このチュートリアルでは、次の内容を学びました。

- IRA が人物・ロボットの合成データを GPU 加速で生成する仕組み
- 設定ファイルの各セクション（global / scene / sensor / character / robot / response / incident / replicator）の意味
- UI とスクリプト（`sdg_scheduler.py`）からのデータ生成方法
- NavMesh と VRAM に関する注意点

## 次のステップ

- オブジェクト中心の SDG は [オブジェクト シミュレーションと SDG](18_replicator_object.md) を参照してください。
- シーンの自然言語記述は [VLM シーンキャプショニング](19_replicator_caption.md)、物理イベントは [物理空間イベント生成](20_replicator_incident.md) を参照してください。
