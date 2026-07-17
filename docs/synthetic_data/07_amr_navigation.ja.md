---
title: シミュレーション内ランダム化 — AMR ナビゲーション
---

# シミュレーション内ランダム化 — AMR ナビゲーション

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- USD / Isaac Sim API による**シーンランダム化**（アセット姿勢、背景環境の切り替え）
- **特定のシミュレーションイベント**（ロボットが対象に接近したとき）での合成データ収集
- 実行時性能を上げるための**レンダープロダクトの動的な作成・破棄**
- 同一シミュレーションインスタンス内での **Replicator キャプチャグラフの作成・破棄**

## はじめに

### 前提条件

- [チュートリアル 4: シーンベースの合成データセット生成](04_scene_based_sdg.md)を完了していること
- OmniGraph の基本（ナビゲーションの実装が OmniGraph ベースのため）

### 所要時間

約 30〜40 分

### 概要

これまでのチュートリアルは「静的なシーンを作ってキャプチャする」ものでしたが、ここでは**走行中のロボットの視点**からデータを集めます。倉庫を走る AMR（自律移動ロボット）のカメラで撮ったようなデータセットを作りたい場合のアプローチです。

シナリオは次のとおりです：

- **Nova Carter** に OmniGraph のナビゲーションスタック（衝突回避なし）を搭載し、ターゲット Xform（`<..>/targetXform`）へ向けて常に走行させる
- ターゲットはランダム化されたオブジェクト（ドリー＝台車）の位置に置かれる
- ロボットが対象に**接近したら**、SDG パイプラインをトリガーして左右 2 つのカメラセンサーからデータをキャプチャ
- キャプチャ後、対象を再ランダム化してシミュレーションを継続
- `env_interval` フレームごとに**背景環境ごと切り替え**、`num_frames` で終了

左右カメラ（`<..>/stereo_cam_<left/right>_sensor_frame/camera_sensor_<left/right>`）から LdrColor（rgb）アノテータのデータを収集し、既定では `<working_dir>/_out_nav_sdg_demo` に 9 フレーム分書き込みます。

![各環境での収集データ](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isaac_tutorial_replicator_amr_data.png)

## ステップ 1：実行してみる

スタンドアロンで実行します：

```bash
./python.sh standalone_examples/replicator/amr_navigation.py
```

オプション引数：

| 引数 | 既定値 | 意味 |
|---|---|---|
| `--use_temp_rp` | False | **一時レンダープロダクト**を使う（キャプチャ時のみ作成・破棄して性能向上） |
| `--num_frames` | 9 | キャプチャするフレーム数 |
| `--env_interval` | 3 | 背景環境を切り替えるキャプチャ間隔 |

すべての引数を指定した実行例：

```bash
./python.sh standalone_examples/replicator/amr_navigation.py --use_temp_rp --num_frames 9 --env_interval 3
```

Script Editor から実行する場合のコードも公式ページに掲載されています（デモは `NavSDGDemo` クラスの `start` / `clear` / `is_running` で制御します）。

## ステップ 2：NavSDGDemo クラスの構成

デモは `NavSDGDemo` クラスにまとめられています。主な属性：

| 属性 | 役割 |
|---|---|
| `_carter_chassis` / `_carter_nav_target` | Nova Carter とナビゲーショングラフのターゲット Xform の追跡 |
| `_dolly` | ナビゲーションの目標であり、Carter との距離の追跡対象 |
| `_dolly_light` | 毎キャプチャ、ドリーの上に置かれるランダム化ライト |
| `_props` | 毎キャプチャ、ドリーの上に配置して落とすプロップのリスト |
| `_cycled_env_urls` | サイクルする背景環境のパス群 |
| `_timeline` / `_timeline_sub` | タイムラインの制御と、SDG トリガーのフィードバックループとなる tick 購読 |
| `_trigger_distance` | SDG をトリガーする Carter とドリーの距離（**キャプチャごとに再ランダム化**） |
| `_writer` / `_render_products` | ライターと、左右カメラの 2 つのレンダープロダクト |
| `_use_temp_rp` | True ならフレームキャプチャごとにレンダープロダクトを作成・破棄 |

## ステップ 3：ワークフローを理解する

**start 関数** — ナビゲーション向けの物理シーン、Nova Carter、ターゲット Xform 付きナビゲーショングラフ、ドリー、ランダム化ライト、プロップを持つ環境を作り、タイムライン購読（コールバック `_on_timeline_event`）を登録します。

**_on_timeline_event** — タイムラインの tick ごとに Carter とドリーの距離をチェックし、十分近づいたら：

1. シミュレーションを一時停止
2. タイムライン購読を解除
3. SDG をトリガー（Script Editor では非同期、スタンドアロンでは同期で実行）

**ランダム化関数** —

- `_randomize_dolly_pose`：Carter から最低距離を保ちつつドリーをランダムな姿勢で配置し、その位置にナビゲーションターゲットを移動
- `_randomize_dolly_light`：ドリーの上にライトを配置し、色を再ランダム化
- `_randomize_prop_poses`：ドリーの上空にプロップをランダム配置（シミュレーション開始後に落下）

**SDG 実行** — `rep.orchestrator.step` でデータキャプチャとライターの write を起動します。`use_temp_rp=True` の場合はキャプチャ時のみレンダープロダクトを有効化し、False（既定）の場合は毎フレームレンダリング・処理します。

**次フレームの準備（_setup_next_frame）** — フレームカウンタを進め、ドリー・ライト・プロップを再ランダム化し、`env_interval` に達していれば背景環境を切り替えて、タイムラインと購読を再開します。`num_frames` に達したら `rep.orchestrator.wait_until_complete` で書き込み完了を待ってデモをクリアします。

!!! note "このチュートリアルの設計パターン"
    「**タイムライン購読をフィードバックループにして、シミュレーションの状態（距離）を監視し、条件を満たしたらポーズ→キャプチャ→再ランダム化→再開**」という構造は、走行ログ収集型の SDG に広く応用できます。[チュートリアル 3 の例 4](03_getting_started_scripts.md)（高さ条件のキャプチャ）の発展形といえます。

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. OmniGraph ナビゲーションによる **Nova Carter の自律走行**とターゲット追跡
2. **接近イベントをトリガー**にした SDG（ポーズ→キャプチャ→再開のループ）
3. **一時レンダープロダクト**（use_temp_rp）による性能最適化
4. **背景環境のサイクル切り替え**を含むランダム化

## 次のステップ

- [チュートリアル 8: シミュレーション内ランダム化 — UR10 パレタイジング](08_ur10_palletizing.md) - マニピュレーション作業中の SDG を学びます。
