---
title: 便利なスニペット集
---

# 便利なスニペット集

## 学習目標

このページでは、Isaac Sim Replicator の**データアクセスとキャプチャ制御のスニペット集**を紹介します。いずれもスタンドアロンアプリケーションとして、または Script Editor から実行できます。

## はじめに

### 前提条件

- [チュートリアル 3: Getting Started スクリプト](03_getting_started_scripts.md)を完了していること

### 概要

**完全なコードは[公式ページ](https://docs.isaacsim.omniverse.nvidia.com/latest/replicator_tutorials/tutorial_replicator_isaac_snippets.html)を参照**してください。このページでは各スニペットの目的・使いどころ・スタンドアロン版の実行コマンドを整理します。

## スニペット 1：複数カメラからのアノテータ／カスタムライターデータ

シーン内の複数のカメラから、アノテータまたはカスタムライターでデータにアクセスする例です。

```bash
./python.sh standalone_examples/api/isaacsim.replicator.examples/multi_camera.py
```

## スニペット 2：特定のシミュレーション時点でのデータアクセス

シミュレーションシーンの**特定のイベント時**に、複数カメラから合成データ（RGB・セマンティックセグメンテーション）を取得する例です（[チュートリアル 3 の例 4](03_getting_started_scripts.md) の発展形）。

```bash
./python.sh standalone_examples/api/isaacsim.replicator.examples/simulation_get_data.py
```

## スニペット 3：カスタムイベントによるランダム化と書き込み

シミュレーション中のさまざまなタイミングで、**カスタムイベント**を使ってランダム化とデータ書き込みをトリガーする例です。

```bash
./python.sh standalone_examples/api/isaacsim.replicator.examples/custom_event_and_write.py
```

## スニペット 4：モーションブラー

**RTX Real-Time** と **RTX Interactive（Path Tracing）**の両レンダリングモードでモーションブラーをキャプチャする例です。

- Real-Time モードでは組み込みのモーションブラー後処理パラメータを使用
- Path Tracing モードでは複数のサブフレーム（`/omni/replicator/pathTracedMotionBlurSubSamples`）をレンダリングして合成

アニメーションアセットと物理アセットの同期した動きを使っており、**キーフレームアニメーションは任意の delta time で補間できる**のに対し、**物理アセットは任意の delta time でモーションサンプルを得るためにカスタム物理 FPS が必要**という違いも扱います。目標物理 FPS の計算・変更・復元の方法が含まれます。

```bash
./python.sh standalone_examples/api/isaacsim.replicator.examples/motion_blur.py
```

## スニペット 5：カスタム FPS での購読とイベント

各種イベント（ステージ・物理・レンダー/アプリ）の購読、カスタム更新レートの設定、関連設定の調整の例です。

```bash
./python.sh standalone_examples/api/isaacsim.replicator.examples/subscribers_and_events.py
```

## スニペット 6：カスタム FPS でのライター／アノテータデータアクセス

**カスタム FPS** でライターをトリガーし、アノテータデータにアクセスする例です。データが不要な間はプロダクトのレンダリングを無効化します。

```bash
./python.sh standalone_examples/api/isaacsim.replicator.examples/custom_fps_writer_annotator.py
```

!!! warning "既知の問題：Replicator グラフ作成後のタイムライン FPS 変更"
    現在、Replicator グラフの作成**後**にタイムライン（ステージ）の FPS を変更すると、グラフがリセットされてしまいます。回避策として、**タイムライン（ステージ）のパラメータは Replicator グラフを作成する前に設定**してください。

## スニペット 7：Cosmos Writer の簡易例

落下するボックスのシンプルなシーンで、**CosmosWriter** による同期マルチモーダルデータ（RGB・セグメンテーション・深度・エッジの画像と動画）をキャプチャする例です。詳細は[チュートリアル 9: Cosmos 合成データ生成](09_cosmos.md)を参照してください。

```bash
./python.sh standalone_examples/api/isaacsim.replicator.examples/cosmos_writer_simple.py
```

## スニペット 8：デフォーマブルを使った合成データ生成

**デフォーマブル（変形体）物理**を使った SDG の例です。デフォーマブルなアセット（バナナやマーカーなど）をクレートに落下させ、各アセットの最下点の頂点がトリガー高さを横切ったタイミングで RGB とセマンティックセグメンテーションをキャプチャします。`VolumeDeformableMaterial`・`DeformablePrim` と、トリガー検出のためのデフォーマブル Tensor API（`get_nodal_positions` など）を使用し、キャプチャごとのマテリアル色のランダム化もオプションで行えます。

```bash
./python.sh standalone_examples/api/isaacsim.replicator.examples/sdg_deformables.py
```

## まとめ

| スニペット | 使いどころ |
|---|---|
| 複数カメラのデータアクセス | マルチビューのデータセット構築 |
| 特定時点でのデータアクセス | イベントトリガー型キャプチャ |
| カスタムイベント | ランダム化と書き込みの分離制御 |
| モーションブラー | Real-Time / Path Tracing 両対応のブラー表現と物理 FPS の調整 |
| カスタム FPS の購読／データアクセス | キャプチャレートとシミュレーションレートの分離 |
| Cosmos Writer 簡易例 | マルチモーダル出力の最小構成 |
| デフォーマブル SDG | 変形体物理と頂点位置ベースのトリガーキャプチャ |

これで Replicator チュートリアル群（カスタマイズ編）は完了です。

## 次のステップ

- [チュートリアル 15: 把持の合成データ生成](15_grasping_sdg.md) - グリッパーによる把持データの生成を学びます。
