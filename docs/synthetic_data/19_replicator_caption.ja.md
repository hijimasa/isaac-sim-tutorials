---
title: VLM シーンキャプショニング（IRC）
---

# VLM シーンキャプショニング（IRC）

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- `Isaacsim.Replicator.Caption.Core`（IRC）が VLM 向けの画像・キャプションペアを生成する仕組み
- シーングラフ（Scene Graph）とサポートツリー（Support Tree）の概念
- UI パネルからキャプションを生成する方法
- IRA / IRO に IRC を組み込んで各フレームのキャプションを生成する方法

## はじめに

### 前提条件

- Isaac Sim 5.1 が起動できること
- [Replicator の概要](01_replicator_overview.md) を理解していること
- LLM/VLM とキャプションデータセットの基礎を理解していること

### 所要時間

約 20 分

### 概要

VLM（Vision-Language Model）は、視覚コンテンツとテキスト記述の複雑な関係を学ぶために、**画像・キャプションのペア**データセットに依存します。NVIDIA Omniverse の 3D ground truth を活用すると、シーン全体の記述・オブジェクト間の関係・空間推論（相対位置や相互作用）まで含む、詳細で正確・スケーラブルなアノテーションが可能になります。3D メタデータにより、「何が見えるか」だけでなく「要素がどう配置され相互作用するか」も記述できます。

**Isaacsim.Replicator.Caption.Core（IRC）** の主な機能は次のとおりです。

- Omniverse に読み込んだシーンの画像・キャプションペアを生成する
- [IRO](18_replicator_object.md) や [IRA](17_replicator_agent.md) に組み込み、実行時に各フレームのキャプションを生成する
- キャプション出力と共にシーングラフをエクスポートし、カスタム後処理を可能にする

![IRC のデモ](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_ext-isaacsim.replicator.caption-5.0.0_gui_IRC_demo.png)

## ワークフローとシーングラフ

![IRC のワークフロー](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_ext-isaacsim.replicator.caption-5.0.0_gui_IRC_workflow.png)

**シーングラフ** はキャプション生成の中間出力で、視覚シーンの構造化表現です。ノードがオブジェクト、エッジがオブジェクト間の空間関係を表します。たとえば「木の下のベンチに座る人」の画像なら、`person`・`bench`・`tree` のノードと、`sitting on`・`under` のエッジを含みます。この空間的な焦点により、詳細な空間推論やシーン分析に有用です。

!!! note "サポートツリー（Support Tree）"
    シーン内のオブジェクトの空間関係を表す木構造です。ルートは床（0 レベル）、その直接の子は床の上のオブジェクト（1 レベル）、2 レベルは 1 レベルのオブジェクトに支えられたオブジェクト……と続きます。

## ステップ 1：IRC を有効化する

1. Omniverse Extension Manager で `isaacsim.replicator.caption.core` を有効化します。
2. UI パネルは **Tools > Action and Event Data Generation > VLM Scene Captioning** から開けます（画面右側）。

![IRC の開始](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_ext-isaacsim.replicator.caption-5.0.0_gui_IRC_start_1.png)

IRC は次の 3 通りで実行できます：**UI パネル** / **IRA 拡張機能** / **IRO 拡張機能**。

## ステップ 2：UI パネルから生成する

1. **Caption Settings** パネルのファイルセレクタで、キャプションを付ける USD ファイルを選びます（デモ用に `[Isaac Sim Assets Path]/Samples/Replicator/Captioning/test_caption.usda` があります）。
2. **Load Scene** でシーンを読み込みます（スクリプト実行の確認が出たら Yes）。
3. **Model Settings** パネルの API key フィールドに LLM モデルの認証情報を入力し、**Accept** します。
4. **Caption Settings** でキャプションレベル（**Brief Caption**＝短い / **Full Caption**＝詳細）を選び、**Input Camera Prim Path** にカメラの prim パス、**Output Path** に出力先を入力して **Generate Scene Graph** をクリックします。

シーングラフ・キャプション・対応画像が出力ディレクトリに生成されます。

!!! note "デフォルトモデルとローカルホスティング"
    デフォルトのサービス URL・モデル名は NVIDIA がトライアルとして無償ホストしています。到達不能な場合は別モデル（`meta/llama3-8b-instruct`、`meta/llama3-70b-instruct`、`meta/llama-3.1-405b-instruct` など）を選べます。LLM API リファレンスの NVIDIA NIM をローカルにホストすることも可能です。

## ステップ 3：設定ファイル（IRA / IRO 用）

IRA / IRO 下で実行する際の IRC 設定ファイルの例です。

```yaml
isaacsim.replicator.caption.core:
   version: 0.0.9
   camera_prim_path: /World/Cameras/Camera
   scene_path: USD_FILE
   caption_configs:
      save_full_scene_graph: true
      save_pruned_scene_graph: true
      attach_label_to_usd: false
      use_ai_label: false
      visualize_caption: true
      max_object_capacity: 100
      export_edges: true
      global_caption: true
      qa_caption: false
      brief_caption: true
      pruning_ratio: 1.0
      verbose: true
      random_seed: 0
      caption_only: false
      export_world: true
   output_path: OUTPUT_PATH
```

### 主な caption_configs

| キー | 説明 |
|---|---|
| `save_full_scene_graph` / `save_pruned_scene_graph` | 完全 / 剪定済みシーングラフを保存 |
| `pruning_ratio` | シーングラフを最小全域木（MST）に剪定した後、保持する MST エッジの割合（既定 1.0 = MST 生成後は剪定しない） |
| `attach_label_to_usd` | セマンティックラベルの無い prim に、prim パスの basename から自動ラベルを付与（アノテーターに捕捉されないと キャプション対象にならない） |
| `use_ai_label` | データベースの AI 生成ラベルを使用 |
| `visualize_caption` | 出力画像上にシーングラフを可視化 |
| `max_object_capacity` | シーングラフに含める最大オブジェクト数（2D BBox サイズの大きい順に選択） |
| `export_edges` | エッジ（空間関係）を出力 |
| `export_world` | prim の 3D ワールド座標を出力（未指定時は他座標はカメラ空間） |
| `global_caption` / `qa_caption` / `brief_caption` | 全体キャプション / QA キャプション / 簡易キャプションを生成 |

!!! warning "NIM API キー"
    IRA / IRO 下でキャプションを生成するには NIM AI が必要です。`export NIM_API_KEY=<API_KEY>` を環境変数（`~/.bashrc` など）に設定します。API キーには有効期間と無料クレジット上限があります。**シーングラフのみ**が必要でキャプション不要なら、AI 認証情報は不要です。

## ステップ 4：IRA / IRO に組み込む

### IRA で使う

IRA の設定ファイルで IRC の `SceneGraphWriter` を使うと、各フレームのキャプションを出力できます。

```yaml
isaacsim.replicator.agent:
   version: 0.0.9
   agent_configs:
      ...
   replicator:
      writer: SceneGraphWriter
      parameters:
         output_dir: OUTPUT_PATH
         caption_config:  # IRC の caption_configs と同じ
            pruning_ratio: 1.0
            global_caption: true
            brief_caption: true
            export_edges: true
            visualize_caption: true
            save_pruned_scene_graph: true
            ...
         caption_interval: 1000    # caption_interval フレームごとにキャプション生成
         scene_graph_interval: 1   # scene_graph_interval フレームごとにシーングラフ生成
         skip_frames: 0
         writer_interval: 1
         export_point_cloud: false
         export_depth: false
```

出力は `<output_dir>/<Camera Prim Name>/` 以下に、剪定/完全シーングラフ・可視化画像・キャプションとして保存されます。

### IRO で使う

IRO の設定ファイルで IRC の `CombinedIROSceneGraphWriter` を使います。

```yaml
isaacsim.replicator.object:
   version: 0.4.x
   camera_parameters: ...
   caption_configs:
      save_full_scene_graph: true
      save_pruned_scene_graph: true
      visualize_caption: true
      global_caption: true
      qa_caption: true
      brief_caption: true
      caption_writer: CombinedIROSceneGraphWriter
      ...
   output_switches:
      caption: True
      ...
```

`caption_writer` には次のいずれかを指定します。

- **`CombinedIROSceneGraphWriter`** … IRO 出力とキャプションを結合して出力
- **`IROSceneGraphWriter`** … キャプションのみを出力し、IRO の他出力（2D 検出ラベルなど）を抑制（画像・distance_to_image_plane・pointcloud は生成可能）

## まとめ

このチュートリアルでは、次の内容を学びました。

- IRC が Omniverse の 3D ground truth から VLM 向けの画像・キャプションペアを生成すること
- シーングラフ（ノード＝オブジェクト、エッジ＝空間関係）とサポートツリーの概念
- UI パネルからキャプションを生成する手順
- IRA（`SceneGraphWriter`）/ IRO（`CombinedIROSceneGraphWriter`）に組み込む方法

## 次のステップ

- 物理イベントの生成は [物理空間イベント生成](20_replicator_incident.md) を参照してください。
