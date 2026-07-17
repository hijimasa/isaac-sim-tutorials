---
title: ROS 2 Simulation Control
---

# ROS 2 Simulation Control

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- Isaac Sim の **ROS 2 Simulation Control** エクステンションの概要
- ROS 2 の**サービスとアクション**によるシミュレーションの制御（再生・一時停止・停止・ステップ実行）
- ROS 2 インターフェースによる**エンティティ**（プリム）と**ワールド**（USD ファイル）の操作
- シミュレーションのプログラム的なステップ実行

## はじめに

### 前提条件

- [ROS 2 セットアップ](00_setup.md)が完了していること
- Isaac Sim 5.0 以降、ROS 2（Humble 以降）
- **Simulation Interfaces** パッケージをインストールしておくこと：

    ```bash
    # Humble
    sudo apt install ros-humble-simulation-interfaces
    # Jazzy
    sudo apt install ros-jazzy-simulation-interfaces
    ```

    パッケージのソースコードは [simulation_interfaces リポジトリ](https://github.com/ros-simulation/simulation_interfaces)を参照してください。

!!! note "simulation_interfaces のバージョンについて"
    このエクステンションは **simulation_interfaces 1.5.0 以降**を対象としています。インストールされているパッケージにサービスや SimulatorFeatures 定数が存在しない場合、該当サービスは登録をスキップし、GetSimulatorFeatures の応答からもその機能が除外されます（起動時に利用できない型を示す警告がログに出ます）。

    RoboStack Jazzy（Pixi ベースの ROS 2 ワークスペースが使用）は現在 simulation_interfaces 1.2.0 を同梱しており、SpawnEntities が含まれていません。SpawnEntities を追加した 1.5.0 以降が RoboStack Jazzy に反映されるまで、Pixi / Jazzy ワークスペースではこのサービスは利用できません。

### 所要時間

約 30 分（リファレンスとしても使えます）

### 概要

ROS 2 Simulation Control エクステンションは、ROS 標準の **ROS 2 Simulation Interfaces** を使って Isaac Sim の機能を制御します。複数のサービス・アクションを少ないオーバーヘッドで同時に実行できるスケーラブルな設計です。

提供される制御は次の 4 カテゴリです：

| カテゴリ | 内容 |
|---|---|
| **シミュレーション状態制御** | 再生・一時停止・停止・ステップ実行 |
| **エンティティ管理** | エンティティ（プリム）のスポーン・削除・操作 |
| **ワールド管理** | ワールド（USD ファイル）の読み込み・アンロード・照会 |
| **状態の照会** | エンティティ・シミュレーション状態・利用可能リソースの情報取得 |

!!! note "何がうれしいのか"
    これまでのチュートリアルの ROS 2 連携は「シミュレーション**内**のロボットやセンサー」との通信でしたが、このエクステンションでは「シミュレーション**そのもの**」を ROS 2 から操作できます。`simulation_interfaces` は特定のシミュレータに依存しない標準インターフェースなので、**自動テスト**（シーンを読み込み→ロボットをスポーン→N ステップ実行→状態を検証→リセット、をすべて ROS 2 CLI やスクリプトから実行）のようなワークフローを、シミュレータ非依存の形で構築できます。

### エクステンションの有効化

**自動で有効化する場合** — ターミナルから次のコマンドで Isaac Sim を起動します：

```bash
./isaac-sim.sh --/isaac/startup/ros_sim_control_extension=True
```

**手動で有効化する場合** — Isaac Sim を開き、Extension Manager で `isaacsim.ros2.sim_control` を有効化します。

## サービスとアクションの一覧

| サービス | 役割 |
|---|---|
| `/get_simulator_features` | この Isaac Sim 実装がサポートする機能の一覧 |
| `/set_simulation_state` | シミュレーション状態の設定（stopped / playing / paused / quitting） |
| `/get_simulation_state` | 現在のシミュレーション状態の取得 |
| `/get_entities` | シミュレーション内の全エンティティ（プリム）の一覧取得 |
| `/get_entity_info` | 特定エンティティの詳細情報の取得 |
| `/get_entity_state` | 特定エンティティの姿勢・速度・加速度の取得 |
| `/get_entities_states` | 複数エンティティの状態のフィルタ付き一括取得 |
| `/delete_entity` | 特定エンティティの削除 |
| `/get_spawnables` | スポーン可能な USD アセットの一覧取得 |
| `/spawn_entity` | 新しいエンティティの指定位置へのスポーン（**非推奨** — `/spawn_entities` を使用） |
| `/spawn_entities` | 複数エンティティの一括スポーン（Humble は simulation_interfaces >= 1.4.0、Jazzy は >= 1.5.0 が必要） |
| `/get_entity_bounds` | エンティティのワールド座標系 AABB（軸並行バウンディングボックス）の取得 |
| `/reset_simulation` | シミュレーション環境の初期状態へのリセット |
| `/set_entity_state` | 特定エンティティの状態（姿勢・速度）の設定 |
| `/step_simulation` | 指定フレーム数のステップ実行 |
| `/load_world` | ワールド（環境ファイル）の読み込み |
| `/unload_world` | 現在のワールドのアンロード（空のステージを作成） |
| `/get_current_world` | 現在読み込まれているワールドの情報取得 |
| `/get_available_worlds` | 読み込み可能なワールドファイルの一覧取得 |

| アクション | 役割 |
|---|---|
| `/simulate_steps` | 進捗フィードバック付きのステップ実行 |

## シミュレーション状態の制御

### 機能一覧の取得（GetSimulatorFeatures）

simulation_interfaces のうち Isaac Sim がサポートするサービス・アクションの一覧を返します：

```bash
ros2 service call /get_simulator_features simulation_interfaces/srv/GetSimulatorFeatures
```

サポートされる機能（SPAWNING、DELETING、ENTITY_STATE_GETTING など）のリスト、USD 対応を示す `spawn_formats`、実装の詳細を示す `custom_info` が返ります。

### 状態の設定（SetSimulationState）

`SimulationState.msg` の enum（STATE_STOPPED / STATE_PLAYING / STATE_PAUSED / STATE_QUITTING）に対応する数値で、シミュレーション全体の状態を設定します：

```bash
# 再生（1 = playing）
ros2 service call /set_simulation_state simulation_interfaces/srv/SetSimulationState "{state: {state: 1}}"
# 一時停止（2 = paused）
ros2 service call /set_simulation_state simulation_interfaces/srv/SetSimulationState "{state: {state: 2}}"
# 停止（0 = stopped）：一時停止＋リセットに相当
ros2 service call /set_simulation_state simulation_interfaces/srv/SetSimulationState "{state: {state: 0}}"
# 終了（3 = quitting）：Isaac Sim をシャットダウン
ros2 service call /set_simulation_state simulation_interfaces/srv/SetSimulationState "{state: {state: 3}}"
```

### 状態の取得（GetSimulationState）

```bash
ros2 service call /get_simulation_state simulation_interfaces/srv/GetSimulationState
```

0＝停止、1＝再生中、2＝一時停止が返ります。ステップ実行などの操作の前に状態を確認する用途で使います。

### ステップ実行（StepSimulation）

指定した有限のフレーム数だけシミュレーションを進め、PAUSED 状態に戻ります：

```bash
# 1 フレーム進める（内部的には 2 ステップ使用）
ros2 service call /step_simulation simulation_interfaces/srv/StepSimulation "{steps: 1}"
# 10 フレーム進める
ros2 service call /step_simulation simulation_interfaces/srv/StepSimulation "{steps: 10}"
```

!!! warning "ステップ実行は一時停止状態からのみ"
    ステップ実行を行うには、シミュレーションが**一時停止（paused）状態**である必要があります（そうでない場合は RESULT_INCORRECT_STATE が返ります）。サービス呼び出しは全ステップ完了までブロックし、完了後は自動的に一時停止状態に戻ります。

### フィードバック付きステップ実行（SimulateSteps アクション）

サービス版と同じステップ実行を、**1 ステップごとのフィードバック付き**で行う ROS 2 アクションです：

```bash
# 10 フレーム進める
ros2 action send_goal /simulate_steps simulation_interfaces/action/SimulateSteps "{steps: 10}"
# 20 フレーム進める（フィードバック表示付き）
ros2 action send_goal /simulate_steps simulation_interfaces/action/SimulateSteps "{steps: 20}" --feedback
```

各ステップ後に完了数・残数のフィードバックが届き、実行中にキャンセルもできます。

## エンティティの操作

### 一覧の取得（GetEntities）

正規表現（POSIX 拡張）によるフィルタ付きで、エンティティの一覧を取得します。Isaac Sim では **USD のプリムパス全体**がエンティティ名として使われます：

```bash
# すべてのエンティティ
ros2 service call /get_entities simulation_interfaces/srv/GetEntities "{filters: {filter: ''}}"
# パスに 'camera' を含むもの
ros2 service call /get_entities simulation_interfaces/srv/GetEntities "{filters: {filter: 'camera'}}"
# '/World' で始まるもの
ros2 service call /get_entities simulation_interfaces/srv/GetEntities "{filters: {filter: '^/World'}}"
# 'mesh' で終わるもの
ros2 service call /get_entities simulation_interfaces/srv/GetEntities "{filters: {filter: 'mesh$'}}"
```

### 情報・状態の取得（GetEntityInfo / GetEntityState / GetEntitiesStates）

```bash
# エンティティの詳細情報（現在は category が常に OBJECT）
ros2 service call /get_entity_info simulation_interfaces/srv/GetEntityInfo "{entity: '/World/robot'}"
# 単一エンティティの姿勢・速度・加速度（ワールドフレーム基準のみ対応）
ros2 service call /get_entity_state simulation_interfaces/srv/GetEntityState "{entity: '/World/robot'}"
# 複数エンティティの状態を一括取得（GetEntities + GetEntityState の組み合わせ）
ros2 service call /get_entities_states simulation_interfaces/srv/GetEntitiesStates "{filters: {filter: 'robot'}}"
```

!!! note "返ってくる値の注意点"
    - **RigidBodyAPI を持つ**エンティティは姿勢と速度の両方が返ります。持たないエンティティは姿勢のみ（速度はゼロ）です。
    - 加速度は現在の API では提供されないため、**常にゼロ**が報告されます。
    - 多数のエンティティの状態が必要な場合は、GetEntityState を繰り返すより GetEntitiesStates のほうが効率的です。

### スポーン可能アセットの照会（GetSpawnables）

スポーンに使える USD アセットを検索します。既定では Isaac アセットルートパスの `/Isaac/Samples/ROS2/Robots` を検索し、`sources` フィールドで独自の検索パスを追加できます：

```bash
# 既定のスポーン可能アセットをすべて一覧
ros2 service call /get_spawnables simulation_interfaces/srv/GetSpawnables
# ローカルパスを追加して一覧
ros2 service call /get_spawnables simulation_interfaces/srv/GetSpawnables "{sources: ['/home/user/custom_robots']}"
# 複数ソースを指定
ros2 service call /get_spawnables simulation_interfaces/srv/GetSpawnables "{sources: ['/home/user/robots', '/opt/isaac_assets/robots']}"
```

!!! note "GetSpawnables の挙動"
    - 既定の検索パスは `/Isaac/Samples/ROS2/Robots`（深さ 2 まで検索）です。
    - `sources` に追加したパスは再帰的（深さ無制限）に検索されます。
    - 各結果は `uri`（アセットの完全 URI）、`description`（拡張子なしのファイル名）、空の `spawn_bounds` を持つ Spawnable として返ります。
    - アセットルートパスが利用できず `sources` も指定されていない場合は RESULT_OPERATION_FAILED が返ります。
    - **Windows ユーザー（WSL 含む）**：`sources` のパスにはネイティブの Windows パス（例：`C:/Users/foo/robots`）を使ってください。`/mnt/c/Users/foo/robots` のような WSL 形式のパスは Isaac Sim の Windows プロセスからアクセスできず、結果が返りません。

### スポーンと削除（SpawnEntity / DeleteEntity）

!!! warning "SpawnEntity は非推奨"
    SpawnEntity サービスは非推奨（deprecated）です。代わりに `/spawn_entities` サービスを使ってください。SpawnEntities はバッチ処理とエンティティごとのエラー報告に対応しており、単一・複数どちらのワークフローにも適しています。

```bash
# 基本のスポーン（既定位置）
ros2 service call /spawn_entity simulation_interfaces/srv/SpawnEntity "{name: 'MyEntity', allow_renaming: false, uri: '/path/to/model.usd'}"
# 位置・向きを指定してスポーン
ros2 service call /spawn_entity simulation_interfaces/srv/SpawnEntity "{name: 'PositionedEntity', allow_renaming: false, uri: '/path/to/model.usd', initial_pose: {pose: {position: {x: 1.0, y: 2.0, z: 3.0}, orientation: {w: 1.0, x: 0.0, y: 0.0, z: 0.0}}}}"
# 空の Xform を作成（URI なし）
ros2 service call /spawn_entity simulation_interfaces/srv/SpawnEntity "{name: 'EmptyXform', allow_renaming: false, uri: ''}"
# 自動リネームを許可
ros2 service call /spawn_entity simulation_interfaces/srv/SpawnEntity "{name: 'AutoRenamedEntity', allow_renaming: true, uri: '/path/to/model.usd'}"
# ネームスペース指定
ros2 service call /spawn_entity simulation_interfaces/srv/SpawnEntity "{name: 'NamespacedEntity', allow_renaming: false, uri: '/path/to/model.usd', entity_namespace: 'robot1'}"

# 削除
ros2 service call /delete_entity simulation_interfaces/srv/DeleteEntity "{entity: '/World/robot'}"
```

!!! note "スポーンの挙動"
    - URI を指定すると USD ファイルが**参照（Reference）**として読み込まれ、指定しなければ Xform が作成されます。
    - スポーンされたプリムには追跡用の `simulationInterfacesSpawned` 属性が付きます（後述の ResetSimulation が削除対象を特定するために使います）。
    - 名前が重複していて `allow_renaming: false` の場合は NAME_NOT_UNIQUE（101）、名前が空なら NAME_INVALID（102）、USD の解析失敗は RESOURCE_PARSE_ERROR（106）が返ります。
    - 削除は、保護されたプリム（`is_prim_no_delete()` が真）に対しては RESULT_OPERATION_FAILED を返します。

### 一括スポーン（SpawnEntities）

1 回のリクエストで複数のエンティティをスポーンします。`spawn_requests` の各エントリは `SpawnEntity.msg` の形式に従い、それぞれ独立に処理されます。成否はエンティティごとに `results` リストで報告されます：

```bash
# 2 つのエンティティを指定位置にスポーン
ros2 service call /spawn_entities simulation_interfaces/srv/SpawnEntities "{
  spawn_requests: [
    {
      name: 'Robot1', allow_renaming: false,
      entity_resource: {uri: '/path/to/robot.usd'},
      initial_pose: {pose: {position: {x: 0.0, y: 0.0, z: 0.0}, orientation: {w: 1.0, x: 0.0, y: 0.0, z: 0.0}}}
    },
    {
      name: 'Robot2', allow_renaming: true,
      entity_resource: {uri: '/path/to/robot.usd'},
      initial_pose: {pose: {position: {x: 2.0, y: 0.0, z: 0.0}, orientation: {w: 1.0, x: 0.0, y: 0.0, z: 0.0}}}
    }
  ]
}"
```

!!! note "SpawnEntities の挙動"
    - このサービスには ROS 2 Humble では simulation_interfaces >= 1.4.0、Jazzy では >= 1.5.0 が必要です。
    - 各エントリは（SpawnEntity のフラットな `uri` フィールドではなく）`entity_resource.uri` フィールドを使います。
    - エンティティごとの結果は `results` リストで返るので、個々の成否は各 SpawnResult を確認してください。
    - 1 つでもスポーンに失敗すると、集約の `result` フィールドは ENTITIES_SPAWN_FAILED になります。
    - そのほかの SpawnEntity のルール（自動リネーム、`simulationInterfacesSpawned` 属性の付与など）は各エントリに適用されます。

### バウンディングボックスの取得（GetEntityBounds）

エンティティのワールド座標系での軸並行バウンディングボックス（AABB）を計算して返します：

```bash
ros2 service call /get_entity_bounds simulation_interfaces/srv/GetEntityBounds "{entity: '/World/Cube'}"
```

!!! note "GetEntityBounds の挙動"
    - `type=TYPE_BOX` と、AABB の最小コーナー・最大コーナーの 2 点を持つ Bounds メッセージが返ります。
    - バウンディングボックスは USD の既定タイムコードで計算され、default purpose のプリムのみが含まれます。
    - エンティティが存在しない場合は RESULT_NOT_FOUND、計算に失敗した場合は RESULT_OPERATION_FAILED が返ります。

### 状態の設定（SetEntityState）

エンティティの姿勢（と速度）を設定します。現在はワールドフレーム基準の変換のみ受け付けます：

```bash
# 位置と向きのみ設定
ros2 service call /set_entity_state simulation_interfaces/srv/SetEntityState "{
  entity: '/World/Cube',
  state: {
    header: {frame_id: 'world'},
    pose: {
      position: {x: 1.0, y: 2.0, z: 3.0},
      orientation: {w: 1.0, x: 0.0, y: 0.0, z: 0.0}
    },
    twist: {
      linear: {x: 0.0, y: 0.0, z: 0.0},
      angular: {x: 0.0, y: 0.0, z: 0.0}
    }
  }
}"
```

速度の設定は **RigidBodyAPI を持つ**エンティティにのみ適用されます（それ以外では無視されます）。加速度の設定は現在未対応です。

### リセット（ResetSimulation）

```bash
ros2 service call /reset_simulation simulation_interfaces/srv/ResetSimulation
```

タイムラインを停止し、`simulationInterfacesSpawned` 属性を持つプリム（＝このインターフェース経由でスポーンされたもの）をすべて削除してから、タイムラインを再開します。

## ワールドの操作

### 読み込み（LoadWorld）

現在のシーンをクリアして、ワールド（USD ファイル）を読み込み、シミュレーションを停止状態にします：

```bash
# ローカルの USD ファイル
ros2 service call /load_world simulation_interfaces/srv/LoadWorld "{uri: '/path/to/world.usd'}"
# Isaac Sim のサンプル環境
ros2 service call /load_world simulation_interfaces/srv/LoadWorld "{uri: 'https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/6.0/Isaac/Environments/Simple_Room/simple_room.usd'}"
```

対応形式は USD（.usd / .usda / .usdc / .usdz）のみです。**再生中は読み込めません**（停止または一時停止してから呼び出します）。パスが直接見つからない場合は、既定のアセットルートパスを前置して再試行されます。

### アンロードと照会（UnloadWorld / GetCurrentWorld / GetAvailableWorlds）

```bash
# 現在のワールドをアンロードして空のステージを作成（再生中は不可）
ros2 service call /unload_world simulation_interfaces/srv/UnloadWorld
# 現在のワールドの情報（URI・名前・形式）を取得
ros2 service call /get_current_world simulation_interfaces/srv/GetCurrentWorld
# 読み込み可能なワールドの一覧を取得
ros2 service call /get_available_worlds simulation_interfaces/srv/GetAvailableWorlds
# タグでフィルタ（ファイル名に 'warehouse' や 'carter' を含むもの）
ros2 service call /get_available_worlds simulation_interfaces/srv/GetAvailableWorlds "{filter: {tags: ['warehouse', 'carter']}, continue_on_error: true}"
# カスタムパスも検索対象に追加
ros2 service call /get_available_worlds simulation_interfaces/srv/GetAvailableWorlds "{additional_sources: ['/custom/worlds/path'], continue_on_error: true}"
```

GetAvailableWorlds は既定で Isaac Sim の `/Isaac/Environments` と `/Isaac/Samples/ROS2/Scenario` を検索します。`offline_only: true` でローカルファイルシステムのみの検索、TagsFilter は FILTER_MODE_ANY（既定）／FILTER_MODE_ALL に対応します。

!!! note "Windows での additional_sources のパス指定"
    Windows ユーザー（WSL 含む）は、`additional_sources` のパスにネイティブの Windows パス（例：`C:/Users/foo/worlds`）を使ってください。`/mnt/c/Users/foo/worlds` のような WSL 形式のパスは Isaac Sim の Windows プロセスからアクセスできず、結果が返りません。

## 技術的な詳細

このエクステンションは `omni.timeline` インターフェースでシミュレーション状態を制御し、標準的なサービスとして ROS 2 インターフェースを提供します。実装には次が含まれます：

- すべての ROS 2 サービスを単一ノードで扱うシングルトンの **ROS2ServiceManager**
- Isaac Sim のタイムラインとやり取りする **SimulationControl** クラス
- Action Graph インターフェースから独立した、スレッドセーフな ROS 2 spin の実装

さらにシミュレーション制御サービスを追加したい場合は、SimulationControl クラスを拡張して ROS2ServiceManager に追加のサービスを登録します。

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. **ROS 2 Simulation Control エクステンション**の概要と有効化
2. ROS 2 サービスによる**シミュレーション状態制御**（再生・一時停止・停止・ステップ）
3. **エンティティの操作**（スポーン・一括スポーン・削除・状態の取得と設定・バウンディングボックスの取得）
4. **スポーン可能アセットと利用可能ワールドの照会**
5. **ワールドの管理**（読み込み・アンロード・一覧照会）
6. フィードバック付きステップ実行のための **ROS 2 アクション**

これで ROS 2 チュートリアルシリーズは完了です。

## 次のステップ

- [ROS 2 チュートリアル一覧](index.md)に戻る
- 公式の ROS 2 Troubleshooting も参考にしてください
