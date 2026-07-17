---
title: MobilityGen によるデータ生成
---

# MobilityGen によるデータ生成

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- **MobilityGen** 用の占有マップの作成
- キーボード操縦（テレオペ）による**軌跡の記録**
- 記録した軌跡の**リプレイとセンサーデータのレンダリング**
- 自動シナリオ（ランダム経路追従など）による**プロシージャルなデータ生成**
- **カスタムロボット**の追加方法

## はじめに

### 前提条件

- 占有マップの作成経験（[ROS 2 チュートリアル 18](../ros/18_navigation.md) で経験済みです）

### 所要時間

約 30〜40 分

### 概要

**MobilityGen** は、Isaac Sim 上で**モバイルロボットのデータを生成・収集**するためのツールセットです。特徴は「**記録とレンダリングの分離**」で、軽い状態でロボットの軌跡（姿勢など）だけを記録し、後からその軌跡をリプレイして高品質なセンサーデータ（RGB・セグメンテーション・深度など）をレンダリングします。

対応するロボットと収集方法：

| 分類 | 対応 |
|---|---|
| 差動二輪 | Jetbot、Carter |
| 四足 | Spot |
| ヒューマノイド | H1 |
| センサー構成（前面カメラ 1 台） | JetbotRobot、CarterRobot、H1Robot、SpotRobot |
| センサー構成（USD ベースのマルチセンサーリグ。現状はマルチカメラのみ） | JetbotMultiSensorRobot、CarterMultiSensorRobot、H1MultiSensorRobot、SpotMultiSensorRobot |
| 手動収集 | キーボード／ゲームパッドのテレオペ |
| 自動収集 | ランダム加速度、ランダム経路追従 |

![MobilityGen のロボット](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_5.0_replicator_tut_gui_mobility_gen_robots.png)

!!! warning "マルチ GPU レンダリングを無効化して起動すること"
    MobilityGen を使うときは、必ずマルチ GPU レンダリングを無効にして Isaac Sim をターミナルから起動してください。複数 GPU を搭載したマシンでは、有効のままだと MobilityGen の起動時に CUDA エラーやクラッシュが発生することがあります。

    ```bash
    ./isaac-sim.sh --/renderer/multiGpu/enabled=false
    ```

!!! note "拡張機能の名称変更"
    Isaac Sim 6.0 では、MobilityGen のコア拡張機能は `isaacsim.replicator.mobility_gen` から **`isaacsim.replicator.experimental.mobility_gen`** に移行しました（旧名称は非推奨）。

## ステップ 1：占有マップを作成する

環境の占有マップが必要です。ここでは倉庫シーンを使います。

1. Content ブラウザから **Isaac Sim/Environments/Simple_Warehouse/warehouse_multiple_shelves.usd** を読み込みます。
2. **Tools > Robotics > Occupancy Map** を開き、次のように設定します（テキストボックスへの入力は ctrl＋左クリックで入力モードになります）：
    - **Origin**：X: 2.0, Y: 0.0, Z: 0.0
    - **Upper Bound**：X: 10.0, Y: 20.0, **Z: 2.0**（ロボットが 2 m の高架下を通れる想定）
    - **Lower Bound**：X: -14.0, Y: -18.0, **Z: 0.1**（高さ 10 cm 未満の床面の凹凸や段差は占有マップに含めず、乗り越えられる想定）
3. **Calculate** → **Visualize Image** をクリックします。
4. Visualization ウィンドウの **Image File Name** フィールドに `map` と入力し、**Update YAML** をクリックします。
5. **Save YAML** をクリックし、ツリーエクスプローラで `~/MobilityGenData/maps/warehouse_multiple_shelves` フォルダを開いて、ファイル名 `map.yaml` で保存します（Windows では `~` を任意のディレクトリに読み替え）。
6. Visualization ウィンドウに戻り、**Save Image** で同じフォルダに `map.png` という名前で画像を保存します。

!!! note "境界（Upper / Lower Bound）の意味"
    占有マップの上限・下限座標は、ロボットにナビゲートさせたい範囲のバウンディングボックスを `warehouse_multiple_shelves.usd` シーン内に定義するものです。上記の値はメインフロアをカバーするよう事前に選ばれています。別のシーンを使う場合は、そのシーンに合わせて調整してください。

`~/MobilityGenData/maps/warehouse_multiple_shelves/` に `map.yaml` と `map.png` があれば完了です。

## ステップ 2：軌跡を記録する

1. **Window > Extensions** で **MobilityGen UI** を検索して有効化します。2 つのウィンドウ（MobilityGen UI と、占有マップ・可視化表示用）が開きます（重なっている場合はドラッグして並べてください）。
2. シナリオを構築します：
    - **Stage** に倉庫の USD の URL（`.../Isaac/Environments/Simple_Warehouse/warehouse_multiple_shelves.usd`）を貼り付け
    - **Occupancy Map** にステップ 1 の `map.yaml` のパスを入力
    - **Robot** ドロップダウンで **H1Robot** を選択
    - **Scenario** ドロップダウンで **KeyboardTeleoperationScenario** を選択
    - **Build** をクリック
3. 数秒後にシーンと占有マップが表示されます。キーボード（**W**：前進、**A**：左旋回、**S**：後退、**D**：右旋回）でロボットを試運転します。
4. **Start recording** で記録を開始し、ロボットを動かして、**Stop recording** で停止します。

データは既定で `~/MobilityGenData/recordings` に記録されます。

## ステップ 3：リプレイとレンダリング

記録した軌跡（ロボットの姿勢とジョイント状態）をヘッドレスでリプレイして、物理シミュレーションを再実行することなくセンサー画像（RGB・深度・セグメンテーション・法線）をレンダリングします。Isaac Sim のルートディレクトリから `replay_directory.py` スクリプトを実行します：

```bash
./python.sh \
  standalone_examples/replicator/mobility_gen/replay_directory.py \
  --input ~/MobilityGenData/recordings \
  --output ~/MobilityGenData/replays \
  --render_interval 40
```

!!! warning "Isaac Sim 5.x の記録は変換が必要"
    Isaac Sim 5.x で作成した記録は 6.0 とディスク上のフォーマットが異なり（`state/common/*.npy` → `*.npz`）、リプレイ前に変換が必要です。変換スクリプトは `./python.sh standalone_examples/replicator/mobility_gen/migrate_recordings.py ~/MobilityGenData/recordings --recursive` です。詳細は[公式移行ガイド（MobilityGen Recordings）](https://docs.isaacsim.omniverse.nvidia.com/latest/migration_guides/isaac_sim_6_0/mobility_gen_recordings_migration.html)を参照してください。

| 引数 | 意味 |
|---|---|
| `--input` / `--output` | 入力の記録ディレクトリ（複数の記録をサブディレクトリとして含む）／レンダリング済みデータの出力ディレクトリ |
| `--render_interval` | N 物理ステップごとに 1 回レンダリング（40 でおよそ 1 秒に 1 回。フルフレームレートなら 1） |
| `--rgb_enabled` | RGB 画像のレンダリング（既定：True） |
| `--depth_enabled` | 深度画像のレンダリング（既定：True） |
| `--segmentation_enabled` | セマンティックセグメンテーションのレンダリング（既定：True） |
| `--normals_enabled` | 法線画像のレンダリング（既定：False） |
| `--instance_id_segmentation_enabled` | インスタンスセグメンテーションのレンダリング（既定：False） |
| `--render_rt_subframes` | RT レンダリングのサブフレーム数（品質と速度のトレードオフ。既定：1） |

無効化には `--no-rgb_enabled` のような否定形フラグを使います。完了すると `~/MobilityGenData/replays` にレンダリング済みのセンサーデータが生成されます。セグメンテーションマスクなどはファイルブラウザだけでは確認しづらいため、オープンソースの [MobilityGen GitHub リポジトリ](https://github.com/NVlabs/MobilityGen/tree/dev-external-occupancy-map-generation/examples)の例、特に [Gradio 可視化スクリプト](https://github.com/NVlabs/MobilityGen/blob/main/examples/04_visualize_gradio.py)での確認がお勧めです（Gradio をインストールした Python から `python examples/04_visualize_gradio.py --input_dir ~/MobilityGenData/replays` で実行。Python でデータを読むヘルパーは `reader.py`）。

![Gradio での可視化](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_5.0_replicator_tut_gui_mobility_gen_gradio_gui.png)

### センサーキャリブレーションの上書き（sensor_overrides.usda）

Isaac Sim 上でロボットのセンサー（カメラの内部パラメータ・歪み係数・投影タイプ・センサー変換など）を変更すると、MobilityGen はその編集内容をロボットアセットの完全なコピーではなく、**軽量な USD 差分**として永続化します。`isaacsim.replicator.experimental.mobility_gen` のヘルパー（`sensor_overrides.py`）が：

- 変更した属性だけを、各記録ディレクトリ内の **`sensor_overrides.usda`** に保存します
- リプレイ／レンダリング時に同ファイルを読み込み、ロボット prim サブツリーにマージして、**キャプチャ時のキャリブレーションと一致**したカメラでレンダリングします

`sensor_overrides.usda` はオプションです。この機能より前の記録などファイルが無い場合、リプレイ時に上書きは適用されません。

## Tips

### プロシージャルなデータ生成

手動テレオペの代わりに自動シナリオを使えば、放置でデータを集められます：

1. ステップ 1 と同様に占有マップを作成します。
2. ステップ 2 の Scenario で **RandomPathFollowingScenario** を選択します。ビルドすると自動で走行・リセットを繰り返します。**Start recording は必要**ですが、シナリオがリセットされるたびに新しい記録が自動で作られます。
3. ステップ 3 と同様にレンダリングします。

他のシナリオ（**RandomAccelerationScenario** など）も同じ流れです。

### カスタムロボットの追加

MobilityGen Examples エクステンションの `robots.py`（`<isaac sim path>/exts/isaacsim.replicator.mobility_gen.examples/isaacsim/replicator/mobility_gen/examples/robots.py`）を編集して、新しいロボットを追加できます：

1. `MobilityGenRobot` クラス（車輪型なら `WheeledMobilityGenRobot`）を継承したクラスを作成します。既存実装のカスタマイズから始めるのがお勧めです。
2. 抽象メソッドを実装します：`build()`（ロボットをステージに追加）、`write_action()`（並進・角速度の指令を受けて制御）。`physics_dt` などの共通クラスパラメータも上書きします。
3. `ROBOTS.register()` デコレータでクラスを登録すると、MobilityGen から発見可能になります。

Isaac Sim の再起動後、MobilityGen UI に新しいロボットが表示されます。

!!! warning "robots.py のバックアップを取ること"
    ロボットの登録は Isaac Sim のビルドファイルの編集を伴うため、自作の `robots.py` は**外部にコピーを保管**してください（アップデートで失われないように）。

共通クラスパラメータには、`physics_dt`、スポーン高さの `z_offset`、三人称カメラの取り付け設定（`chase_camera_*`）、経路計画・衝突判定用の footprint 半径（`occupancy_map_radius` / `occupancy_map_collision_radius`）、前面カメラの設定（`front_camera_*`）、テレオペのゲイン（`keyboard_*` / `gamepad_*`）、ランダムシナリオの速度・加速度パラメータ（`random_action_*`）、経路追従のパラメータ（`path_following_*`）などがあります。

### NuRec アセット（3D 再構築シーン）の利用

MobilityGen は USD 環境で動作するため、NVIDIA **NuRec** パイプラインで作られた 3D 再構築シーンもそのまま使えます。NVIDIA PhysicalAI-Robotics NuRec データセットには、MobilityGen のステージとして直接使える屋内シーンが用意されています。

- NuRec シーンは **Particle USD**（パーティクルベース）と **Volume USD**（ボリュームベース）の 2 形式で公開されており、どちらもステージとして使えます。多くのシーンには**計算済みの占有マップ**が付属し、手動でのマップ生成を省略できます（無い場合は通常どおり占有マップを生成）。
- MobilityGen ウィンドウの **Stage** に NuRec シーンの USD パス、**Occupancy Map** に対応する `map.yaml` を設定し、あとは通常のフロー（記録 → `replay_directory.py` でリプレイ・レンダリング）と同じです。

!!! warning "再構築シーンでの出力の制限"
    再構築環境では **RGB レンダリングは完全対応**ですが、**深度**は再構築ジオメトリの欠損やノイズにより精度が保証されず、**セマンティックセグメンテーションは非対応**です。リプレイ時にスキップするには `--no-depth_enabled --no-segmentation_enabled` を渡します。占有マップの品質は USD ステージのコリジョンジオメトリに依存するため、記録前に可視化を確認して範囲を調整してください。

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. MobilityGen 用の**占有マップの作成**
2. H1 のキーボードテレオペによる**軌跡の記録**
3. 記録した軌跡からの**センサーデータのレンダリング**（記録とレンダリングの分離）
4. **自動シナリオ**によるプロシージャル生成と**カスタムロボット**の追加

これで合成データ生成チュートリアルシリーズは完了です。

## 次のステップ

- [合成データ生成チュートリアル一覧](index.md)に戻る
- 別のロボット（Spot など）や別のシナリオ（Random Path Following）での記録を試してみてください
