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
| 手動収集 | キーボード／ゲームパッドのテレオペ |
| 自動収集 | ランダム加速度、ランダム経路追従 |

![MobilityGen のロボット](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_replicator_tut_gui_mobility_gen_robots.png)

## ステップ 1：占有マップを作成する

環境の占有マップが必要です。ここでは倉庫シーンを使います。

1. Content ブラウザから **Isaac Sim/Environments/Simple_Warehouse/warehouse_multiple_shelves.usd** を読み込みます。
2. **Tools > Robotics > Occupancy Map** を開き、次のように設定します（テキストボックスへの入力は ctrl＋左クリックで入力モードになります）：
    - **Origin**：X: 2.0, Y: 0.0, Z: 0.0
    - **Upper Bound**：X: 10.0, Y: 20.0, **Z: 2.0**（ロボットが 2 m の高架下を通れる想定）
    - **Lower Bound**：X: -14.0, Y: -18.0, **Z: 0.1**（5 cm の段差は乗り越えられる想定）
3. **Calculate** → **Visualize Image** をクリックします。
4. Visualization ウィンドウで **Rotate Image** を 180、**Coordinate Type** を **ROS Occupancy Map Parameters File YAML** にして **Regenerate Image** をクリックします。
5. 生成された YAML テキストをコピーし、`~/MobilityGenData/maps/warehouse_multiple_shelves/map.yaml` というファイルを作って貼り付けます（Windows では `~` を任意のディレクトリに読み替え）。
6. YAML 内の `image: warehouse_multiple_shelves.png` の行を **`image: map.png`** に書き換えて保存します。
7. Visualization ウィンドウの **Save Image** で、同じフォルダに `map.png` という名前で画像を保存します。

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

記録した軌跡（ロボットの姿勢など）をリプレイして、センサーデータをレンダリングします。Isaac Sim ディレクトリ内から `replay_directory.py` スクリプトを実行します：

```bash
./python.sh standalone_examples/replicator/mobility_gen/replay_directory.py --render_interval 40 --enable isaacsim.replicator.mobility_gen.examples
```

| 引数 | 意味 |
|---|---|
| `--input` / `--output` | 入力の記録パス／レンダリング済みデータの出力パス |
| `--rgb_enabled` | RGB 画像のレンダリング |
| `--segmentation_enabled` | セマンティックセグメンテーションのレンダリング |
| `--depth_enabled` | 深度画像のレンダリング |
| `--instance_id_segmentation_enabled` | インスタンスセグメンテーションのレンダリング |
| `--normals_enabled` | 法線画像のレンダリング |
| `--render_rt_subframes` | RT レンダリングのサブフレーム数（品質と速度のトレードオフ） |
| `--render_interval` | レンダリング 1 回あたりの物理ステップ数 |

完了すると `~/MobilityGenData/replays` にレンダリング済みのセンサーデータが生成されます。セグメンテーションマスクなどはファイルブラウザだけでは確認しづらいため、オープンソースの [MobilityGen GitHub リポジトリ](https://github.com/NVlabs/MobilityGen/tree/dev-external-occupancy-map-generation/examples)の例、特に [Gradio 可視化スクリプト](https://github.com/NVlabs/MobilityGen/blob/main/examples/04_visualize_gradio.py)での確認がお勧めです（Python でデータを読むヘルパーは `reader.py`）。

![Gradio での可視化](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_replicator_tut_gui_mobility_gen_gradio_gui.png)

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
3. `ROBOT.register()` デコレータでクラスを登録すると、MobilityGen から発見可能になります。

Isaac Sim の再起動後、MobilityGen UI に新しいロボットが表示されます。

!!! warning "robots.py のバックアップを取ること"
    ロボットの登録は Isaac Sim のビルドファイルの編集を伴うため、自作の `robots.py` は**外部にコピーを保管**してください（アップデートで失われないように）。

共通クラスパラメータには、`physics_dt`、スポーン高さの `z_offset`、三人称カメラの取り付け設定（`chase_camera_*`）、経路計画・衝突判定用の footprint 半径（`occupancy_map_radius` / `occupancy_map_collision_radius`）、前面カメラの設定（`front_camera_*`）、テレオペのゲイン（`keyboard_*` / `gamepad_*`）、ランダムシナリオの速度・加速度パラメータ（`random_action_*`）、経路追従のパラメータ（`path_following_*`）などがあります。

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
