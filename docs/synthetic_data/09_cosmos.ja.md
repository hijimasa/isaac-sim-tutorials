---
title: Cosmos 合成データ生成
---

# Cosmos 合成データ生成

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- **CosmosWriter** による、同期したマルチモーダルデータ（RGB・深度・セグメンテーション・エッジ）の生成
- クリップ単位のキャプチャ構成と **Cosmos Transfer** の制御ブランチとの対応
- セグメンテーションモードやエッジ検出しきい値などの**高度な設定**

## はじめに

### 前提条件

- omni.replicator とそのライターの基本
- [チュートリアル 3: Getting Started スクリプト](03_getting_started_scripts.md)の基本的な理解

### 所要時間

約 30 分

### 概要

!!! note "NVIDIA Cosmos と Cosmos Transfer とは"
    [NVIDIA Cosmos](https://www.nvidia.com/en-us/ai/cosmos/) はフィジカル AI 向けの世界基盤モデル（WFM）プラットフォームです。その中の **Cosmos Transfer** は、低解像度の制御信号（深度・セグメンテーション・エッジなど）から Multi-ControlNet アーキテクチャで**高品質な映像シミュレーションを生成**するモデルです。

    つまりこのチュートリアルのワークフローは、「Isaac Sim で**構造的に正しい**グラウンドトゥルースを生成 → Cosmos Transfer で**見た目のリアリティ**を注入」という 2 段構えで、フォトリアルな学習データを大量に得るためのものです。

このチュートリアルでは、倉庫環境を自律走行する Carter Nova ロボットの前面カメラから、CosmosWriter で同期マルチモーダルデータをキャプチャします。

CosmosWriter の主なユースケースは次のとおりです：

- **Sim-to-Real 転移** — Cosmos Transfer により、シミュレーション映像をマテリアル・照明・環境条件の異なるフォトリアルなシーンに変換
- **ドメイン適応** — 1 つのシミュレーションから、シーンスタイル・マテリアル・照明のバリエーションを持つ多様な学習データを生成（高価なシミュレーションの再実行や実データ収集が不要）
- **データオーグメンテーション** — ロボットの動作・オブジェクト位置・シーン構造を保ったまま、視覚的バリエーションを増やして限られたデータセットを拡張

ロボティクスでの sim-to-real 変換の実例は [Cosmos Cookbook Robotics Gallery](https://nvidia-cosmos.github.io/cosmos-cookbook/gallery/robotics_inference.html) を参照してください。合成キッチンシーンを、キャビネットのスタイルやロボットのマテリアル、照明条件を変えたフォトリアル環境に変換する例が紹介されています。

![Cosmos 倉庫キャプチャ](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_5.1_replicator_tut_viewport_cosmos_warehouse.webp)

## CosmosWriter が生成するデータ

ロボットのカメラから **5 つの同期モダリティ**を出力します：

| モダリティ | 内容 | Cosmos Transfer の制御ブランチ |
|---|---|---|
| RGB | カラー画像 | `vis`（バイラテラルブラー適用） |
| Depth | カメラからの距離 | `depth`（3D 構造の理解） |
| Segmentation | インスタンスマスク | `seg`（オブジェクト識別） |
| Shaded Segmentation | リアルな陰影付きインスタンスマスク | — |
| Edges | Canny エッジ検出 | `edge`（しきい値調整可能） |

各制御ブランチには重み（0.0〜1.0）を設定でき、**制御信号への忠実さと生成の自由度**のバランスを調整します。

## ステップ 1：実行してみる

スタンドアロンで実行します（Windows では `python.bat`）：

```bash
./python.sh standalone_examples/replicator/cosmos_writer_warehouse.py
```

!!! note "スクリプトの場所の変更"
    Isaac Sim 6.0 でサンプルの場所が `standalone_examples/api/isaacsim.replicator.examples/` から `standalone_examples/replicator/` に移動しました。

Script Editor 版のコードも公式ページに掲載されています。スクリプトは倉庫環境を読み込み、ナビゲーション付きの Carter Nova を追加してターゲットを設定し、SDG パイプラインを実行します。

## ステップ 2：キャプチャパラメータとパイプライン

主なキャプチャパラメータ：

| パラメータ | 例 | 意味 |
|---|---|---|
| `NUM_CLIPS` | 2 | 生成する動画クリップの数 |
| `NUM_FRAMES_PER_CLIP` | 10 | クリップあたりのフレーム数 |
| `CAPTURE_INTERVAL` | 2 | 何シミュレーションステップごとにキャプチャするか |
| `START_DELAY` | 0.1 | キャプチャ開始前の遅延（開始タイミングの調整用） |

`run_sdg_pipeline` 関数がキャプチャプロセス全体を統括します。ポイントは：

- レンダープロダクトはロボットの前面カメラから **1280×720** で作成
- `pause_timeline=False` により、**キャプチャ中もロボットは移動し続ける**（ナビゲーションの進行が映像として残る）
- キャプチャの合間にシミュレーションを進めて走行を進行させる

出力は**クリップ単位**に整理され、各クリップが Cosmos Transfer への入力となる連続フレーム列になります。各モダリティは PNG シーケンスに加えて **MP4 動画**（`rgb.mp4`、`depth.mp4`、`segmentation.mp4`、`shaded_seg.mp4`、`edges.mp4`）としても出力され、MP4 はそのまま Cosmos Transfer の制御入力として渡せます（PNG はフレーム単位の確認やカスタム処理用）。

## ステップ 3：高度な設定

**セグメンテーションモード** — CosmosWriter は 2 つのモードをサポートします：

- **Instance ID モード**（既定）：インスタンスごとに ID を割り当て
- **Semantic Segmentation モード**：セマンティックラベルベース（セマンティックアノテーションが必要）

**カスタムセグメンテーション色** — 特定のセマンティックラベルに固定色を割り当てられます。データセット間でクラスの色/ID を一貫させたい場合（Cosmos Transfer にクラスの対応関係を保持させたい場合）に使います。

**エッジ検出のチューニング** — Canny エッジ検出のヒステリシスしきい値（low / high）を調整できます。低いしきい値はノイズを含む多くのエッジを検出し、高いしきい値は強いエッジだけのクリーンな出力になります（典型的な値の範囲は 10〜200）。

## ステップ 4：Cosmos Transfer でデータを使う

生成したデータは Cosmos Transfer の制御ブランチにマッピングして使います。単一制御（例：edge のみ）とマルチモーダル制御（複数ブランチの重み付き併用）の設定例が公式ページに掲載されています。生成した MP4 は [Cosmos Transfer1](https://docs.nvidia.com/cosmos/latest/transfer1/index.html) または [Transfer2.5](https://docs.nvidia.com/cosmos/latest/transfer2.5/index.html) にそのまま渡せます。

[Cosmos Cookbook Robotics Gallery](https://nvidia-cosmos.github.io/cosmos-cookbook/gallery/robotics_inference.html) には、このワークフローの実例として次が紹介されています：

- **エッジのみの制御** — ロボットの動作を正確に保ったまま、シミュレーション映像を多様なキッチンスタイル（白・赤・木目のキャビネット）やロボットのマテリアル（プラスチック・金属・ゴールド）に変換
- **マルチ制御** — 深度・エッジ・セグメンテーションの制御を組み合わせた精密なシーン操作

!!! note "運用上の注意点"
    - **制御の重み**：高いほど制御信号に忠実、低いほど生成の自由度が増します。合計が 1.0 を超えると自動的に正規化されます。
    - **プロンプト**：カメラ制御の指示は避け、単一シーンの豊かな描写に集中させます。
    - **セーフティ**：人の顔は Cosmos Guardrail により自動的にぼかされます。

## まとめ

このチュートリアルでは、倉庫を走行するロボットから **CosmosWriter** で同期マルチモーダルデータ（RGB・深度・セグメンテーション・エッジ）を生成し、**Cosmos Transfer** で高品質な映像シミュレーションを作るためのグラウンドトゥルースとして使う方法を扱いました。

## 次のステップ

- [チュートリアル 10: データオーグメンテーション](10_augmentation.md) - アノテータ／ライターへの拡張処理の適用を学びます。
