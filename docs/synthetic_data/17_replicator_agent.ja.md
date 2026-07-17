---
title: アクター シミュレーションと合成データ生成（IRA）
---

# アクター シミュレーションと合成データ生成（IRA）

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- `Isaacsim.Replicator.Agent`（IRA）を中心とするフレームワークで人物・ロボットの合成データを生成する仕組み
- 拡張機能の有効化と UI からのデータ生成の流れ
- 設定ファイル（YAML）のトップレベルセクションと**名前付きグループ**の考え方
- **ルーチン・トリガー**によるアクタービヘイビアの制御
- スクリプト（`actor_sdg.py`）と Python API からのデータ生成方法

## はじめに

### 前提条件

- Isaac Sim 6.0.1 がインストール済みで起動できること
- Replicator の基礎（[Replicator の概要](01_replicator_overview.md)）を理解していること
- NavMesh（Navigation Mesh：キャラクターやロボットが歩行可能な領域を表すメッシュ）の作成方法を把握していること

!!! warning "IRA 0.x からの破壊的変更"
    Isaac Sim 6.0 の IRA 1.x は、5.1 以前の IRA 0.x からの**全面的な再設計**です。環境読み込み・アクタースポーン・センサー配置・SDG などのコア機能は引き継がれていますが、**設定スキーマ・ビヘイビアシステム・Python API はすべて変更**されており、0.x の設定ファイルとスクリプトはそのままでは動きません。主な変更点：

    - 外部コマンドファイル（.txt）の生成・保存・読み込みは廃止され、ビヘイビアは **YAML 内のインライン定義（routines / triggers）** になりました（UI の Generate Random Commands / Save Commands ステップも削除）
    - キャラクター・ロボット・センサーは**名前付きグループ**で構成し、複数の集団を 1 つの設定ファイルで独立に設定できます
    - 設定は **Pydantic v2** モデルで読み込み時に検証され、明確なエラーメッセージが出ます
    - アクター設定は **USD スキーマ／プリムとして永続化**され、ステージ上で直接確認・編集できます

    詳細は[公式移行ガイド（Replicator Agent (IRA)）](https://docs.isaacsim.omniverse.nvidia.com/latest/migration_guides/isaac_sim_6_0/ext_isaacsim_replicator_agent_migration_guide.html)を参照してください。

### 所要時間

約 30 分

### 概要

さまざまな環境で人物キャラクターやロボットのようなアニメーションするアクター（エージェント）を検出・追跡することは、小売・製造・物流など多くの産業で大きな価値を持ちます。しかし、実世界データの収集はコストが高くスケールしません。

Isaac Sim 6.0 では、**Omni.Metropolis.Pipeline（OMP）**・**Isaacsim.Replicator.Agent（IRA）**・**Isaacsim.Anim.Robot.Core（IAR）** の 3 つの拡張機能が連携して、3D 環境に人物キャラクターとロボットをセットアップし合成データを生成する仕組みを提供します。このフレームワークは、アクターのビヘイビア・環境・センサーを**設定ファイル 1 つ**で制御します。

- **コードレス** … 設定は YAML ファイルで表現され、コードを書かずに合成データを得られます
- **簡単なセットアップ** … Isaac Sim に同梱。対話的な GUI と、ヘッドレス向けのスクリプトインターフェースの両方を提供
- **高品質データ** … Omniverse の SimReady アセット・物理・レンダリングを活用し、AI 学習に不可欠なリアルな画像と正確なアノテーションを生成
- **シームレスな統合** … Kit 拡張機能として `omni.anim.behavior`・`omni.anim.navigation`・`omni.replicator.core` とネイティブに連携

![IRA の概要](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_4.5_full_ext-isaacsim.replicator.agent-5.0.0_viewport_IRA_overview.png)

## ステップ 1：拡張機能を有効化する

1. Omniverse Extension Manager で **Omni.Metropolis.Pipeline**・**Isaacsim.Anim.Robot.Core**・**Isaacsim.Replicator.Agent.Core / UI** を有効化します。
2. 拡張機能は起動時に Isaac Sim Assets からサンプルアセットを取得します。
3. UI パネルは **Tools > Action and Event Data Generation > Actor SDG** から開けます（画面右側に表示）。

!!! tip
    - 起動時に自動ロードするには、Extension Manager で autoload をチェックします（依存関係のため Isaac Sim の再起動が必要な場合があります）。
    - UI のロードがハングするように見える場合は、`--/persistent/isaac/asset_root/timeout=1.0` フラグ付きで起動してみてください。
    - 想定外のエラーに遭遇した場合は、`./isaac-sim.sh --reset-user` で以前のユーザー設定をクリアして起動してみてください。

## ステップ 2：UI からデータ生成する

コマンド生成のステップが廃止されたため、セットアップから生成までは実質 **2 クリック**です。

1. 拡張機能を有効化して UI パネルを開くと、**最小構成の設定（minimal.yaml）が自動ロード**されます。フォルダアイコンから別の設定ファイルも読み込めます。サンプル設定は `[Isaac Sim App Path]/extscache/isaacsim.replicator.agent.core-[version]/data/sample_configs/` にあります。
2. minimal.yaml にはアクターもカメラも含まれません。より網羅的な例として、同フォルダの **full_pipeline.yaml** を使います（読み込みに時間がかかります）。
3. （任意）設定を編集します。**New** アイコンで新規作成、**Reload** アイコンで UI の変更を破棄して再読み込み、**Save / Save As** アイコンで保存できます。**Verbose save** チェックボックスをオンにすると、変更値だけのコンパクトな出力ではなく、空でない全フィールドを書き出します（全オプションのリファレンスや完全に明示的な設定の共有に便利）。
4. UI 上部の **Set Up Simulation** をクリックすると、設定に従ってシミュレーションアセット（シーン・カメラ・アクター）の読み込みが始まります。シーンにはアクターのスポーンと制御のために **NavMesh** が必要です（サンプル設定のシーンは設定済み。外部シーンは Navigation Mesh のドキュメントを参照）。
5. UI 上部の **Start Data Generation** をクリックすると、Actor SDG Setup パネルの **Simulation Duration** フィールドで指定した**秒数**だけシミュレーションとデータ生成が実行されます。
6. 生成が完了すると、出力データは Replicator パネルの **Output Directory** で指定した場所に保存されます（既定は Linux で `~/IRA_output`、Windows で `%USERPROFILE%\IRA_output`）。

![設定パネル](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_6.0_full_tut_external_actor_sim_getting_started_config_panel.png)

!!! warning "Set Up Simulation はシーンを完全リロードする"
    **Set Up Simulation** をクリックすると、常に現在の設定からシーンを一から再構築します（ベース環境 USD の再オープン、アクター・センサー・プロップレイヤーの再作成）。前回のセットアップ後にステージへ手動で加えた編集は破棄されます。設定を反復する場合は、先に UI か設定ファイルを変更してから Set Up Simulation を押してください。

!!! note "NavMesh の Auto-Bake"
    **Window > Navigation > NavMesh** で Auto-Bake をオフにするとパフォーマンスが向上します。

既定の **IRABasicWriter** と full_pipeline.yaml の場合、出力はカメラ（レンダープロダクト）ごとのサブフォルダに `rgb/`（フレームごとの画像）、`camera_params/`（フレームごとの内部パラメータと姿勢）、`object_detection.json`（バウンディングボックス・スケルトン・アクションデータの統合ファイル）、有効化した追加アノテーターのフォルダ、という構造で書き出されます。

## ステップ 3：設定ファイル（YAML）

設定ファイルはシミュレーションを定義する中心的なデータで、環境からキャラクター・センサー・データ出力まですべてを制御します。トップレベルは次のセクションで構成されます。

| セクション | 主な内容 |
|---|---|
| （ルート） | `version`（1.x.x 必須）、`seed`（32bit uint。省略時はシステム時刻から自動生成）、`simulation_duration`（**秒**単位。0.x の `simulation_length`（フレーム）から変更） |
| **environment** | `base_stage_asset_path`（環境 USD。**必須**。Isaac Sim アセット相対パス・URL・絶対パスに対応）、`prop_asset_paths`（サブレイヤーとして重ねる追加 USD） |
| **character** | `groups` 以下に**名前付きグループ**を定義。グループごとに `num`・`asset_path`・`spawn_areas`・`semantic_labels`・`routines`（インラインビヘイビア）・`triggers`・`colliders`（円柱/箱のコリジョン形状）。`motion_library_path` は character 直下 |
| **robot** | 同じく名前付きグループ。`num` と `config_file_path`（IAR のロボット設定。例：`nova_carter.yaml`）で機種と台数を指定（0.x の `nova_carter_num` / `iw_hub_num` は廃止）。`write_data`、`camera_prim_paths`（データ生成に使う搭載カメラの指定）も可 |
| **sensor** | 名前付きグループごとに配置戦略を指定：**`aim_at_targets`**（高さ・見下ろし角・焦点距離・距離の範囲）または **`maximum_coverage`**（`num: -1` で目標カバレッジに必要な台数を自動計算） |
| **replicator** | **`writers`** 辞書で**複数のライターを同時実行**可能。ライター名をキーに、パラメータを直接指定。ライターごとに `start_frame` / `end_frame`（または `start_time` / `end_time`）と `sensor_prim_list` を指定可能（既定の `start_frame` は 30）。利用可能なライター：`IRABasicWriter`・`CosmosIRAWriter`・`SceneGraphWriter`・`CustomWriter`（`writer_name: "BasicWriter"` で標準 BasicWriter も利用可） |

設定例（0.x からの変換例）：

```yaml
isaacsim.replicator.agent:
  version: 1.6.0
  seed: 123456789
  simulation_duration: 60.0
  environment:
    base_stage_asset_path: "Isaac/Environments/Simple_Warehouse/full_warehouse.usd"
  sensor:
    groups:
      default_cameras:
        num: 4
        aim_at_targets:
          height_range: [2.0, 3.0]
          look_down_angle_range: [0.0, 60.0]
          focal_length_range: [13.0, 23.0]
          distance_range: [6.5, 14.0]
  character:
    groups:
      default_characters:
        num: 8
        asset_path: "Isaac/People/Characters/"
        routines:
          - wander:
              walk:
                speed_range: [1.0, 1.0]
                distance_range: [5.0, 15.0]
              idle:
                - animation: idle
                  time_range: [2.0, 5.0]
  robot:
    groups:
      nova_carters:
        num: 2
        config_file_path: "nova_carter.yaml"
        routines:
          - wander:
              move:
                distance_range: [10.0, 15.0]
              idle:
                time_range: [2.0, 5.0]
  replicator:
    writers:
      IRABasicWriter:
        semantic_filter_predicate: "class:character|robot;id:*"
        rgb: true
        camera_params: true
        start_frame: 30
```

詳細なパラメータリストと例は、公式の **Configuration File Guide** と **Sample Configs**（`[ext-path]/data/sample_configs/` に同梱。安定版のルーチン・トリガー系と実験的なビヘイビアツリー系（`behavior_tree/`）の両方をカバー）を参照してください。

## ステップ 4：アクタービヘイビア（ルーチンとトリガー）

アクターのビヘイビアは OMP・IRA・IAR の連携で実現され、再生中は「**ルーチン・トリガーループ**」で動作します。

- **ルーチン（routines）** … 重み付きビヘイビアのリスト。トリガーが発火していない間、アクターは自身のシードを使って確率的にルーチンからビヘイビアを選び続けます
- **トリガー（triggers）** … イベント駆動／時間駆動の割り込み。発火するとアクターはルーチンを一時停止してトリガーのビヘイビア列を実行します。優先度の高いトリガーは実行中のトリガーを一時停止してキューに入れ（低優先度はスキップ）、すべて完了するとルーチンに戻ります

| 種類 | 内容 |
|---|---|
| キャラクターのビヘイビア | `wander`（ランダム歩行＋アイドル）、`patrol`（3D 点列またはターゲット prim の経路巡回）、`stop`（指定時間の静止） |
| ロボットのビヘイビア | `wander`、`patrol`、`halt`（指定時間の停止） |
| トリガー（共通） | `event_trigger`（名前付きイベントで発火）、`time_trigger`（指定秒数後に発火）、`collision_trigger`（アクターの名前付きコライダーが他のコライダーと重なり始め／終わったときに発火） |

読み込み後、各アクターの設定は USD API スキーマ（人物は SkelRoot 上の **IRACharacterAPI**、アニメーションロボットはルート prim 上の **AnimRobotAPI**）に埋め込まれ、各ビヘイビア・トリガーは個別の USD プリムになります。アクターの `name`・`group`・`seed` はハッシュされて**アクターごとの決定的なシード**となり、環境と設定が同じなら同じ結果を再現します。アニメーションの実装には、人物キャラクターは `omni.anim.behavior`、アニメーションロボットは `isaacsim.anim.robot.core` を利用します。

!!! note "ビヘイビアツリー（実験的機能）"
    IRA 1.3.0 以降では、ルーチン・トリガー方式の代替として、**ビヘイビアツリー**（`omni.behavior.tree.core` / `omni.anim.behavior.tree` でオーサリングし JSON で保存）でキャラクターを制御できます。設定ファイルのキャラクターグループに `behavior_tree` フィールド（＋ノードパラメータを上書きする `overrides`）を指定します。ルーチンの重み付きランダム選択と異なり、順序・分岐・ループを決定的に制御できます。ただし**ビヘイビアツリーのグループではトリガーは未対応**で、1 つのグループはルーチン方式かビヘイビアツリー方式のどちらか一方を使います（1 つの設定ファイル内で両方式のグループの共存は可能）。サンプルは `[Isaac Sim Assets Path]/Samples/BehaviorTree` と拡張機能の `data/sample_configs/behavior_tree/` にあります。

## ステップ 5：スクリプトと API から生成する

### 自動スクリプト（actor_sdg.py）

大規模生成では、スクリプトからの起動が効率的です。IRA はオフライン生成用の自動スクリプト **`actor_sdg.py`**（0.x の `sdg_scheduler.py` の後継）を提供します。

```bash
# Linux
./python.sh tools/actor_sdg/actor_sdg.py -c [config file path]
# Windows
.\python.bat tools\actor_sdg\actor_sdg.py -c [config file path]
```

!!! note
    - Isaac Sim 付属の `python.sh` / `python.bat` を使う必要があります。
    - サンプル設定ファイルは `/tools/actor_sdg` フォルダにあります（例：`-c tools/actor_sdg/sample_config.yaml`）。

### Python API

`isaacsim.replicator.agent.core` を有効化すると、自作スクリプトから Python API（`isaacsim.replicator.agent.core.api`）でシミュレーションのセットアップとデータ生成を実行できます。`IRA.load_config_file(path)` → `IRA.get_config_file()` / `IRA.set_config(config)` → `await IRA.setup_simulation()` → `await IRA.start_data_generation_async(will_wait_until_complete=True)` という流れです（完全な例は公式ページを参照）。

## 用語

| 用語 | 説明 |
|---|---|
| core 拡張機能 | シミュレーション状態を管理。API とモジュールを含み、独立して呼び出せる |
| UI 拡張機能 | IRA の UI。ロード時に core も自動ロードされる |
| 設定ファイル（.yaml） | シード・長さ・アクターグループ・センサー・出力形式などを定義する唯一の情報源 |
| actor / agent | 本ドキュメントでは同義。人物キャラクターとロボット（Nova Carter、iw.hub）。それぞれ `omni.behavior.tree` / `isaacsim.anim.robot` のコントローラで制御される |
| ビヘイビアツリー | 意思決定とアクションを階層的に構成するデータモデル。JSON で定義し設定ファイルから参照。ルーチン・トリガー方式の代替 |

## まとめ

このチュートリアルでは、次の内容を学びました。

- OMP・IRA・IAR が連携して人物・ロボットの合成データをコードレスで生成する仕組み
- UI からの 2 クリックワークフロー（Set Up Simulation → Start Data Generation）と既定の出力先（`~/IRA_output`）
- 設定ファイルのトップレベルセクション（environment / character / robot / sensor / replicator）と名前付きグループ・複数ライター
- ルーチン・トリガーループとビヘイビアの種類、ビヘイビアツリー（実験的機能）
- `actor_sdg.py` と Python API からのデータ生成方法

## 次のステップ

- オブジェクト中心の SDG は [オブジェクト シミュレーションと SDG](18_replicator_object.md) を参照してください。
- シーンの自然言語記述は [VLM シーンキャプショニング](19_replicator_caption.md)、物理イベントは [物理空間イベント生成](20_replicator_incident.md) を参照してください。
