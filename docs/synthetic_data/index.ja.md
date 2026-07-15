---
title: 合成データ生成チュートリアル
---

# 合成データ生成チュートリアル

<span class="badge badge-intermediate">Intermediate</span>

Replicator を中心とした合成データ生成（SDG: Synthetic Data Generation）のチュートリアルです。

## 概要

機械学習モデルの学習に必要な**ラベル付きデータを、シミュレーションから自動生成**するのが合成データ生成です。Isaac Sim では **Replicator**（omni.replicator）がその中核を担い、レンダリングと同時に正確なアノテーション（バウンディングボックス、セグメンテーション、深度など）を出力し、ドメインランダマイゼーション（照明・配置・テクスチャのランダム化）によって汎化性能の高いデータセットを作れます。

このシリーズでは、GUI ツールでの記録から、スクリプトベースの本格的な SDG パイプラインまでを段階的に学びます。

## チュートリアル

### 基礎と入門

!!! example "[チュートリアル 1: Replicator の概要](01_replicator_overview.md)"
    セマンティックラベル付け、可視化、レコーダー、YAML ワークフローなど、Replicator のツール群の全体像を把握します。

!!! example "[チュートリアル 2: Synthetic Data Recorder](02_recorder.md)"
    GUI だけで合成データを記録します。カスタムライターや Data Visualization ライター、ランダマイズカメラとの組み合わせも扱います。

!!! example "[チュートリアル 3: Getting Started スクリプト](03_getting_started_scripts.md)"
    スクリプトベースの SDG の基本設定（capture on play、step、RTSubframes、DLSS）と、BasicWriter・カスタムライター・2 方式のランダム化・条件付きキャプチャの 4 つの実例を学びます。

### SDG チュートリアル

!!! example "[チュートリアル 4: シーンベースの合成データセット生成](04_scene_based_sdg.md)"
    倉庫シーンでフォークリフト・パレット・箱をランダム化し、KITTI / COCO 形式のデータセットをオフライン生成します。

!!! example "[チュートリアル 5: オブジェクトベースの合成データセット生成](05_object_based_sdg.md)"
    コリジョンウォールで囲んだ空間に対象物とディストラクタを浮遊させ、姿勢推定向けデータ（DOPE / CenterPose）を生成します。

!!! example "[チュートリアル 6: Infinigen を使った環境ベースの生成](06_infinigen_sdg.md)"
    プロシージャル生成した室内環境を背景に、複数ライターで多様なデータセットを生成します。

!!! example "[チュートリアル 7: シミュレーション内ランダム化 — AMR ナビゲーション](07_amr_navigation.md)"
    走行する Nova Carter の接近をトリガーにキャプチャし、背景環境もサイクルさせます。

!!! example "[チュートリアル 8: シミュレーション内ランダム化 — UR10 パレタイジング](08_ur10_palletizing.md)"
    パレタイジング作業のイベントで、シミュレーションに干渉せずデータを収集します。

!!! example "[チュートリアル 9: Cosmos 合成データ生成](09_cosmos.md)"
    CosmosWriter で Cosmos Transfer 向けの同期マルチモーダルデータを生成します。

### カスタマイズのツールとテクニック

!!! example "[チュートリアル 10: データオーグメンテーション](10_augmentation.md)"
    warp（GPU）／NumPy（CPU）カーネルでアノテータ・ライターのデータを加工します。

!!! example "[チュートリアル 11: カスタム Replicator ランダマイゼーションノード](11_custom_og_randomizer.md)"
    自作ランダム化を OmniGraph ノード化し、ReplicatorItem として SDG パイプラインに統合します。

!!! example "[チュートリアル 12: モジュラービヘイビアスクリプティング](12_modular_scripting.md)"
    プリムに添付できる部品化されたランダマイザ（ビヘイビアスクリプト）の使い方と自作方法を学びます。

!!! example "[チュートリアル 13: ランダム化スニペット集](13_isaac_randomizers.md)"
    ライト・テクスチャ・連鎖ランダム化・物理充填・SimReady アセットのコード集です。

!!! example "[チュートリアル 14: 便利なスニペット集](14_isaac_snippets.md)"
    複数カメラ・イベント駆動・モーションブラー・カスタム FPS などのデータアクセス集です。

### その他のデータ生成ツール

!!! example "[チュートリアル 15: 把持の合成データ生成](15_grasping_sdg.md)"
    アンチポーダルサンプラーと物理評価で把持データセットを自動生成します。

!!! example "[チュートリアル 16: MobilityGen によるデータ生成](16_mobility_gen.md)"
    軌跡の記録とレンダリングを分離した、モバイルロボットのデータ収集ツールです。

### アクション・イベントデータ生成（準備中）

- Actor / Object シミュレーションと SDG、VLM シーンキャプショニング、物理空間イベント生成、RTX センサーの配置とキャリブレーション
