---
title: Replicator の概要
---

# Replicator の概要

## 学習目標

このページでは、Isaac Sim での合成データ生成（SDG）を支える **Replicator** のツール群の全体像を把握します：

- **Semantics Schema Editor** — セマンティックラベルの付与
- **Synthetic Data Visualizer** — センサー出力のビューポート内可視化
- **Synthetic Data Recorder** — GUI からのデータ記録
- **Replicator YAML** — 設定ファイルベースの SDG ワークフロー
- **Getting Started Scripts** — スクリプトベースの典型的ワークフロー

## はじめに

### 前提条件

- Isaac Sim の基本操作に慣れていること

### 所要時間

約 10 分

### 概要

Isaac Sim Replicator は、合成データ生成（SDG: Synthetic Data Generation）のためのさまざまなツールとワークフローを提供します。中核機能の多くは [omni.replicator](https://docs.omniverse.nvidia.com/extensions/latest/ext_replicator.html) エクステンションが提供しています。SDG 関連の UI パネルをまとめて表示するには、公式ドキュメントの **Synthetic Data Generation Layout** が利用できます。

!!! note "合成データ生成（SDG）とは"
    機械学習モデル（物体検出・セグメンテーションなど）の学習には、大量の**ラベル付きデータ**が必要です。実世界で画像を集めて人手でラベル付けするのは高コストですが、シミュレータなら**レンダリングと同時に正確なラベル（アノテーション）を自動生成**できます。さらに、照明・配置・テクスチャなどをランダム化（**ドメインランダマイゼーション**）することで、実世界への汎化性能を高めたデータセットを大量に作れます。これが Replicator の役割です。

!!! note "アノテータとライター：Replicator の 2 つの基本部品"
    このセクション全体で繰り返し登場する用語です。

    - **アノテータ（annotator）** … RGB・深度・セマンティックセグメンテーション・バウンディングボックスなど、**特定の種類のデータを生成・抽出する**モジュールです。カメラのレンダープロダクト（レンダリング出力の単位）に接続して使います。
    - **ライター（writer）** … アノテータの出力を受け取り、**指定した形式（PNG・JSON・KITTI 形式など）でディスクへ書き出す**部品です。既定の **BasicWriter** のほか、用途別ライターやカスタムライターを利用できます。

## Semantics Schema Editor

[Semantics Schema Editor](https://docs.omniverse.nvidia.com/extensions/latest/ext_replicator/semantics_schema_editor.html) は、ステージ上のプリムの**セマンティックラベル**を表示・追加・編集・削除できる GUI エクステンションです。

セマンティックセグメンテーションやバウンディングボックスのようなアノテータが合成データにセマンティック情報を含めるには、プリムへのセマンティックラベル付けが**必須**です。エディタは **Tools > Replicator > Semantics Schema Editor** から開けます。

![Semantics Schema Editor](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_4.5_replicator_tut_gui_semantics_editor_window.jpg)

プログラムからラベルを付ける場合は、[チュートリアル 3](03_getting_started_scripts.md) で登場する `add_labels()` のようなスニペットを使います。

## Synthetic Data Visualizer

[Synthetic Data Visualizer](https://docs.omniverse.nvidia.com/extensions/latest/ext_replicator/visualization.html) は、センサー出力（セグメンテーション、深度、バウンディングボックスなど）を**ビューポートウィンドウ内で直接可視化**できるツールです。ビューポートのアイコンから、表示したい出力形式を選択します。

![Synthetic Data Visualizer](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_4.5_replicator_tut_gui_data_visualizer_sensors.jpg)

!!! note
    Cross Correspondence の可視化には、公式のアノテータ詳細ページの Cross Correspondence 節で説明されている 2 カメラの特殊なセットアップが必要です。

## Synthetic Data Recorder

**Synthetic Data Recorder** は、エディタから直接合成データを記録できる GUI ツールです。omni.replicator の上に構築されており、既定のライターとして **BasicWriter** を使用します。テスト目的で合成データの記録を素早く反復するのに便利です。**Tools > Replicator > Synthetic Data Recorder** から開けます。

![Synthetic Data Recorder](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_4.5_replicator_tut_gui_sd_recorder_editor.jpg)

詳しい使い方は[チュートリアル 2: Synthetic Data Recorder](02_recorder.md) で解説します。

## Replicator YAML

[Replicator YAML](https://docs.omniverse.nvidia.com/extensions/latest/ext_replicator/yaml_workflow.html) は、Replicator API の上に構築された**設定ファイルベース**のワークフローです。ランダマイゼーションとデータキャプチャのパイプラインを設定ファイルとして定義でき、この設定は Replicator API を通じて OmniGraph（ノードを繋いで処理を定義する Omniverse の実行グラフ機構。詳細は OmniGraph セクションを参照）のワークフローに変換されて SDG を実行します。**Tools > Replicator > Replicator YAML** からアクセスできます。

## Getting Started Scripts

**Getting Started Scripts** は、典型的な Isaac Sim Replicator ワークフローの出発点となるサンプル集です。アノテータやライターからのデータアクセス、データキャプチャとは独立にトリガーされる Replicator ランダマイザ＋カスタム USD / Isaac Sim API ランダマイザの併用といった基本トピックをカバーします。

詳しくは[チュートリアル 3: Getting Started スクリプト](03_getting_started_scripts.md)で解説します。

## まとめ

このページでは、Replicator の主要ツールの役割を整理しました：

| ツール | 用途 | 使い方 |
|---|---|---|
| Semantics Schema Editor | ラベル付け（SDG の前提） | GUI |
| Synthetic Data Visualizer | アノテータ出力の確認 | GUI（ビューポート） |
| Synthetic Data Recorder | データ記録の素早い反復 | GUI |
| Replicator YAML | 設定ファイル駆動の SDG | 設定ファイル |
| Getting Started Scripts | 本格的な SDG パイプラインの出発点 | Python |

## 次のステップ

- [チュートリアル 2: Synthetic Data Recorder](02_recorder.md) - GUI だけで合成データを記録してみます。
