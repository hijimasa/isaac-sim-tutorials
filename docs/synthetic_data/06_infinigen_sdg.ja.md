---
title: Infinigen を使った環境ベースの生成
---

# Infinigen を使った環境ベースの合成データセット生成

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- **Infinigen** でプロシージャル生成した環境を背景シーンとして読み込む
- 環境を SDG と物理シミュレーション用に準備する（コライダー付与）
- 物理有効の**ラベル付きアセット**とシーンの多様性のための**ディストラクタ**の配置
- キャプチャと分離して手動トリガーする **Replicator ランダマイザ**とカスタム USD / Isaac Sim API ランダマイザの併用
- **複数のライターとカメラ**による、異なる視点・異なる種類のデータの同時保存
- 設定ファイルによるパイプラインのカスタマイズ

## はじめに

### 前提条件

- [チュートリアル 4](04_scene_based_sdg.md)・[チュートリアル 5](05_object_based_sdg.md)を完了していること
- [Infinigen](https://infinigen.org/) によるプロシージャル環境生成の基本

### 所要時間

約 40〜50 分（Infinigen での環境生成時間を除く）

### 概要

!!! note "Infinigen とは"
    Infinigen はプリンストン大学発のオープンソースツールで、**部屋の間取りから家具まで完全にプロシージャルに**フォトリアルな室内環境を生成できます。生成した環境は USD 形式にエクスポートして Isaac Sim に読み込めるため、「背景環境そのものを大量にランダム化する」という、SDG の多様性をもう一段引き上げるアプローチが可能になります。

このチュートリアルでは、Infinigen で生成したダイニングルーム環境を背景として、テーブル（作業エリア）にラベル付きアセットとディストラクタを配置し、**浮遊状態**と**物理シミュレーション後の静止状態**の 2 シナリオでキャプチャします。1 つの環境でのキャプチャが終わると次の環境を読み込み、目標のキャプチャ数まで繰り返します。

![Infinigen 環境の例](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_4.5_replicator_tut_viewport_infinigen_rooms.jpg)

![収集データの例](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_4.5_replicator_tut_viewport_infinigen_assets.jpg)

## ステップ 1：Infinigen 環境を生成する

1. [Infinigen GitHub リポジトリ](https://github.com/princeton-vl/infinigen/blob/main/docs/source/Installation.md)の手順で Infinigen をインストールします。
2. [Hello Room](https://github.com/princeton-vl/infinigen/blob/main/docs/source/HelloRoom.md) の手順に従って室内シーンを生成します。シードを変えながらループする例（Linux）では、Infinigen 生成用と Omniverse エクスポート用の出力フォルダを `mkdir -p` で作成しつつ、10 個のユニークなダイニングルームを生成して `outputs/indoors/dining_room_$i` に保存します（`infinigen_examples.generate_indoors` コマンド）。
3. `infinigen.tools.export` コマンドで USD 形式（`-f usdc`、`--omniverse` で Omniverse 互換）に変換し、`outputs/omniverse/dining_room_$i` に出力します。

!!! warning "Infinigen のシーン生成は Linux のみでテスト済み"
    Infinigen は Isaac Sim の外部で保守されている外部ライブラリであり、シーン生成ステップは **Linux 上でのみテスト**されています。最新のプラットフォーム対応状況は Infinigen のプラットフォームサポート表を参照してください。

## ステップ 2：実行してみる

メインスクリプトは `<install_path>/standalone_examples/replicator/infinigen/infinigen_sdg.py`、ヘルパーは `infinigen_sdg_utils.py` です：

```bash
./python.sh standalone_examples/replicator/infinigen/infinigen_sdg.py
```

複数ライターなどのカスタム設定は `--config` で渡します（サンプルは `infinigen/config` ディレクトリ）。

## ステップ 3：設定パラメータを理解する

| カテゴリ | 主なパラメータ |
|---|---|
| `environments` | `folders`（Infinigen 環境のディレクトリ群）／`files`（個別の USD ファイル） |
| `capture` | `total_captures`（総キャプチャ数）、`num_floating_captures_per_env`（物理シミュレーション**前**＝浮遊状態のキャプチャ数）、`num_dropped_captures_per_env`（**後**＝静止状態のキャプチャ数）、`num_cameras`、`resolution`、`disable_render_products`、`rt_subframes`、`path_tracing`、`camera_look_at_target_offset`、`camera_distance_to_target_range`、`num_scene_lights` |
| `writers` | 使用するライターのリスト（`type`：BasicWriter、DataVisualizationWriter など、`kwargs`：各ライター固有の引数）。**複数指定可** |
| `labeled_assets` | `auto_label`（ファイル名から正規表現 `regex_replace_pattern` / `regex_replace_repl` でラベルを自動生成）／`manual_label`（URL・ラベル・数・`gravity_disabled_chance` を個別指定） |
| `distractors` | `shape_distractors`（プリミティブ形状）／`mesh_distractors`（メッシュ）の数・種類・重力無効確率 |
| `physics` | `gpu_collision_stack_size`：PhysX の GPU コリジョンスタックサイズ（バイト）。PhysX 既定の 64 MB では、コライダーの多い Infinigen シーンには不足するため、**既定で 300 MB**（314572800）に設定。`collisionStackSize` のバッファオーバーフローエラーが出る場合はエラーメッセージの推奨値以上に増やす。必要に応じて `gpu_found_lost_pairs_capacity` など他の GPU メモリ設定も指定可能 |
| `debug_mode` | true にすると天井などを非表示にして、開発・デバッグ時にシーンを見やすくする |

!!! note "gravity_disabled_chance"
    アセットごとに「重力を無効にして浮遊させる確率」を指定できます。これにより、同じ設定から**落下して積もるアセット**（物理有効）と**空中に浮くアセット**（コライダーのみ）が混在するシーンが作れます。

## ステップ 4：パイプラインの流れ

実装は次の流れで進みます：

1. **アセットの読み込み（最初に 1 回）** — `load_auto_labeled_assets`（ファイル名から正規表現でラベルを自動生成。例：`002_banana` → `banana`）と `load_manual_labeled_assets`（明示的なラベル指定）でラベル付きアセットを読み込み、物理プロパティを付与します。どちらも**浮遊用**（重力無効）と**落下用**（重力有効）のリストを別々に返します。
2. **PhysX GPU メモリの設定** — SDG ループの前に `configure_physics_scene` で PhysX シーンの `gpuCollisionStackSize`（既定 300 MB）などを設定し、コライダーの多い Infinigen シーンでの `PxGpuDynamicsMemoryConfig::collisionStackSize` バッファオーバーフローを防ぎます（`/PhysicsScene` プリムは環境をまたいで永続するため設定は 1 回で済みます）。
3. **環境の読み込み** — `get_usd_paths` で設定のフォルダ／ファイルから USD を収集し（`.thumbs` フォルダはスキップ）、`cycle` でサイクルしながら 1 つずつ読み込みます。
4. **シーンのセットアップ** — 環境にコライダーを付与（debug_mode なら上部の壁を非表示）。ダイニングテーブル（作業エリア）の位置を取得し、`randomize_poses`（`location_range` / `rotation_range` / `scale_range` を明示指定）でアセットの姿勢をランダム化します。
5. **カメラとレンダープロダクト** — `rep.functional.create.scope` で `/Cameras` スコープを作り、`rep.functional.create.camera`（`clipping_range` 指定可）でカメラを作成して `rep.create.render_product` でレンダープロダクトを作成。`disable_render_products` が true なら作成時に無効化し、キャプチャ時のみ有効化します。
6. **ライターのセットアップ** — `setup_writer` が設定に基づいてライター（BasicWriter、DataVisualizationWriter、PoseWriter、カスタムライターなど）を初期化し、レンダープロダクトにアタッチします。**複数のライターを同時に使い、異なる形式のデータセットを 1 回の実行で生成**できます。
7. **ドメインランダマイゼーション** — シーンライト（USD API で作成したスフィアライト）の位置・強度・色を `randomize_lights` でランダム化。ドームライトと形状ディストラクタの色は**グラフランダマイザ**として一度登録し、`rep.utils.send_og_event` の OmniGraph イベントで環境ごとにトリガーします。
8. **物理シミュレーションとキャプチャ** — 初期の重なりを解消する短いシミュレーション → **浮遊状態のキャプチャ**（カメラの極角 0〜75° の多様な視点）→ 落下・静止までの長いシミュレーション（約 200 フレーム、レンダリングなしで効率化）→ **静止状態のキャプチャ**（極角 0〜45° の上方寄り視点）。`path_tracing: true` ならキャプチャ時のみ PathTracing に切り替えます。
9. 1 環境分のキャプチャが終わると次の環境を読み込み、`capture_counter` が総数に達するまで繰り返します。完了後はデータの書き込みを待ち、ライターのデタッチとレンダープロダクトの破棄を行います。

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. **Infinigen** でのフォトリアル室内環境の生成と USD エクスポート
2. 環境の**サイクル読み込み**とコライダー付与による SDG 対応
3. **auto_label / manual_label** によるラベル付きアセットの構成と重力無効確率
4. **複数ライター**の同時使用と、浮遊／静止の 2 シナリオのキャプチャ

## 次のステップ

- [チュートリアル 7: シミュレーション内ランダム化 — AMR ナビゲーション](07_amr_navigation.md) - 走行するロボットの視点からの SDG を学びます。
