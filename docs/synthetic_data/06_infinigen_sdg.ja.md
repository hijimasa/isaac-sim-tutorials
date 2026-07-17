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

1. [Infinigen GitHub リポジトリ](https://github.com/princeton-vl/infinigen/blob/main/docs/Installation.md)の手順で Infinigen をインストールします。
2. [Hello Room](https://github.com/princeton-vl/infinigen/blob/main/docs/HelloRoom.md) の手順に従って室内シーンを生成します。シードを変えながらループする例（Linux）では、10 個のユニークなダイニングルームを生成し、`outputs/indoors/dining_room_$i` に保存します。
3. export コマンドで USD 形式（`-f usdc`、`--omniverse` で Omniverse 互換）に変換し、`outputs/omniverse/dining_room_$i` に出力します。

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
| `debug_mode` | true にすると天井などを非表示にして、開発・デバッグ時にシーンを見やすくする |

!!! note "gravity_disabled_chance"
    アセットごとに「重力を無効にして浮遊させる確率」を指定できます。これにより、同じ設定から**落下して積もるアセット**（物理有効）と**空中に浮くアセット**（コライダーのみ）が混在するシーンが作れます。

## ステップ 4：パイプラインの流れ

実装は次の流れで進みます：

1. **環境の読み込み** — `get_usd_paths` で設定のフォルダ／ファイルから USD を収集し、サイクルしながら 1 つずつ読み込みます。
2. **シーンのセットアップ** — `setup_env` が環境にコライダーを付与（debug_mode なら上部の壁を非表示）。`get_matching_prim_location` でダイニングテーブル（作業エリア）の位置を取得し、ラベル付きアセットとディストラクタをスポーンして物理プロパティを付与、`randomize_poses` で姿勢をランダム化します。
3. **カメラとレンダープロダクト** — USD API でカメラプリムを定義し、`rep.create.render_product` でレンダープロダクトを作成。`disable_render_products` が true ならキャプチャ間は無効化します。
4. **ライターのセットアップ** — `setup_writer` が設定に基づいてライターを初期化し、レンダープロダクトにアタッチします。**複数のライターを同時に使い、異なる形式のデータセットを 1 回の実行で生成**できます。
5. **ドメインランダマイゼーション** — アセット姿勢、シーンライト、ドームライト、形状ディストラクタの色をランダム化。ランダマイザは登録後、**Replicator のトリガーで特定の間隔ごとに手動トリガー**されます。
6. **物理シミュレーションとキャプチャ** — 初期の重なりを解消する短いシミュレーション → **浮遊状態のキャプチャ** → 落下・静止までの長いシミュレーション → **静止状態のキャプチャ**。カメラは毎キャプチャ、ランダムなターゲットアセットを注視する位置にランダム配置されます。
7. 1 環境分のキャプチャが終わると次の環境を読み込み、`capture_counter` が総数に達するまで繰り返します。

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. **Infinigen** でのフォトリアル室内環境の生成と USD エクスポート
2. 環境の**サイクル読み込み**とコライダー付与による SDG 対応
3. **auto_label / manual_label** によるラベル付きアセットの構成と重力無効確率
4. **複数ライター**の同時使用と、浮遊／静止の 2 シナリオのキャプチャ

## 次のステップ

- [チュートリアル 7: シミュレーション内ランダム化 — AMR ナビゲーション](07_amr_navigation.md) - 走行するロボットの視点からの SDG を学びます。
