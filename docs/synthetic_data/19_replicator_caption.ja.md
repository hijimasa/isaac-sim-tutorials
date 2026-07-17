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

- Isaac Sim 6.0.1 が起動できること
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

![IRC のデモ](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_5.0_full_ext-isaacsim.replicator.caption-5.0.0_gui_IRC_demo.png)

## ワークフローとシーングラフ

![IRC のワークフロー](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_5.0_full_ext-isaacsim.replicator.caption-5.0.0_gui_IRC_workflow.png)

**シーングラフ** はキャプション生成の中間出力で、視覚シーンの構造化表現です。ノードがオブジェクト、エッジがオブジェクト間の空間関係を表します。たとえば「木の下のベンチに座る人」の画像なら、`person`・`bench`・`tree` のノードと、`sitting on`・`under` のエッジを含みます。この空間的な焦点により、詳細な空間推論やシーン分析に有用です。

!!! note "サポートツリー（Support Tree）"
    シーン内のオブジェクトの空間関係を表す木構造です。ルートは床（0 レベル）、その直接の子は床の上のオブジェクト（1 レベル）、2 レベルは 1 レベルのオブジェクトに支えられたオブジェクト……と続きます。

## ステップ 1：IRC を有効化する

1. Omniverse Extension Manager で `isaacsim.replicator.caption.core` を有効化します。
2. UI パネルは **Tools > Action and Event Data Generation > VLM Scene Captioning** から開けます（画面右側）。

![IRC の開始](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_5.0_full_ext-isaacsim.replicator.caption-5.0.0_gui_IRC_start_1.png)

IRC は次の 3 通りで実行できます：**UI パネル** / **IRA 拡張機能** / **IRO 拡張機能**。

## ステップ 2：UI パネルから生成する

1. **Caption Settings** パネルのファイルセレクタで、キャプションを付ける USD ファイルを選びます（デモ用に `[Isaac Sim Assets Path]/Samples/Replicator/Captioning/test_caption.usda` があります）。
2. **Load Scene** でシーンを読み込みます（スクリプト実行の確認が出たら Yes）。
3. **Model Settings** パネルの API key フィールドに LLM モデルの認証情報を入力し、**Accept** します。
4. **Caption Settings** でキャプションレベル（**Brief Caption**＝短い / **Full Caption**＝詳細）を選び、**Input Camera Prim Path** にカメラの prim パス、**Output Path** に出力先を入力して **Generate Scene Graph** をクリックします。

シーングラフ・キャプション・対応画像が出力ディレクトリに生成されます。

!!! note "デフォルトモデルとローカルホスティング"
    デフォルトのサービス URL・モデル名は NVIDIA がトライアルとして無償ホストしています。到達不能な場合は、NVIDIA NIM API リファレンスページに掲載されているモデルから選び、Model Settings パネルの **Model Name** フィールドにモデル識別子を入力します。NVIDIA NIM を入手してローカルにホストすることも可能です。

!!! tip "ROI（関心領域）のキャプション生成"
    特定の領域のキャプションを生成するには、カメラのドロップダウンから対象カメラを選択し、ROI がビュー平面の大部分を占めるようにカメラを配置してから、**Generate Scene Graph** をクリックします。

## Python API（CaptionAPI）

IRC は、モデル設定とキャプション生成をプログラムから行うための Python API（**CaptionAPI**）を提供します。モデルの API キーは環境変数 `NVIDIA_API_KEY` から読み込みます（NVIDIA NIM API キーのページで生成し、`export NVIDIA_API_KEY=<API_KEY>` を実行しておきます）。

```python
import os
from isaacsim.replicator.caption.core.api import CaptionAPI

CaptionAPI.set_model_params(
    url="https://integrate.api.nvidia.com/v1",
    name="meta/llama-3.1-8b-instruct",
    key=os.environ["NVIDIA_API_KEY"],
)

# 設定ファイルの読み込み（任意）
CaptionAPI.load_config_file("/path/to/irc_config.yaml")

# キャプションの非同期生成
import asyncio
task = asyncio.ensure_future(CaptionAPI.get_captions())
task.add_done_callback(lambda future: print(f"Generated captions: {future.result()}"))
```

## ステップ 3：設定ファイル（IRA / IRO 用）

IRA / IRO 下で実行する際の IRC 設定ファイルの例です。

```yaml
isaacsim.replicator.caption.core:
   version: 0.6.6
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

!!! warning "NVIDIA NIM API キー"
    IRA / IRO 下でキャプションを生成するには NVIDIA NIM AI が必要です。Linux/Mac では `~/.bashrc` などに `export NVIDIA_API_KEY=<API_KEY>`、Windows ではコマンドプロンプトで `set NVIDIA_API_KEY=<API_KEY>` を設定します。API キーには有効期間と無料クレジット上限があります。**シーングラフのみ**が必要でキャプション不要なら、AI 認証情報は不要です。

## ステップ 4：IRA / IRO に組み込む

### IRA で使う

IRA（1.x）の設定ファイルで、`replicator.writers` に IRC の `SceneGraphWriter` を指定すると、各フレームのキャプションを出力できます。キャプション関連パラメータはライターのパラメータとして直接記述します。

```yaml
isaacsim.replicator.agent:
   version: 1.6.0
   simulation_duration: 5
   environment:
      base_stage_asset_path: "Isaac/Samples/Replicator/Captioning/test_caption.usda"
   sensor:
      groups:
         ceiling_cameras:
            num: 2
            aim_at_targets:
               distance_range: [5, 10]
               height_range: [7, 10]
               focal_length_range: [10, 15]
               look_down_angle_range: [30, 45]
   character:
      groups:
         warehouse_workers:
            asset_path: "Isaac/People/Characters/"
            num: 5
            routines:
               - wander:
                    weight: 1
                    repeat: 1
                    walk:
                       speed_range: [0.8, 1.5]
                       distance_range: [5.0, 10.0]
                    idle:
                       - animation: idle
                         weight: 1
                         time_range: [2.0, 5.0]
   replicator:
      writers:
         SceneGraphWriter:
            semantic_filter_predicate: "class:*"
            rgb: true
            camera_params: true
            pruning_ratio: 1.0
            global_caption: true
            qa_caption: false
            brief_caption: true
            visualize_caption: true
            max_object_capacity: 100
            export_edges: true
            save_full_scene_graph: true
            save_pruned_scene_graph: true
            caption_only: false
            scene_graph_interval: 10   # scene_graph_interval フレームごとにシーングラフ生成
            caption_interval: 10       # caption_interval フレームごとにキャプション生成
```

出力は `<output_dir>/<Camera Prim Name>/` 以下に、剪定済みシーングラフ（`caption_pruned_json/scene_graph_pruned_<frame id>.json`）とキャプション（`caption/scene_graph_caption_<frame id>.json`）として保存されます。

### IRO で使う

IRO の設定ファイルで IRC の `CombinedIROSceneGraphWriter` を使います。

```yaml
isaacsim.replicator.object:
   version: 0.x.y
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
