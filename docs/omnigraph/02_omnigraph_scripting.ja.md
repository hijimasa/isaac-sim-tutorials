---
title: OmniGraph の Python スクリプティング
---

# OmniGraph の Python スクリプティング

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- `og.Controller.edit` を使って Python だけでアクショングラフを構築する方法
- グラフの属性値の取得・設定、ノードの追加・接続を行う方法
- グラフの評価タイミング（毎フレーム / オンデマンド）を制御する方法

## はじめに

### 前提条件

- [Isaac Sim OmniGraph チュートリアル](01_omnigraph_tutorial.md)（GUI 版）と Omniverse Script Editor を理解していること
- [Core API チュートリアル](../core_api/index.md) の Hello World で、Python 拡張機能ワークフローと Standalone ワークフローに慣れていること

### 所要時間

約 20 分

### 概要

OmniGraph はビジュアルスクリプティングツールですが、Python スクリプティングインターフェースも備えています。このチュートリアルでは、Python API だけでアクショングラフを構築・編集・実行する例を紹介します。

## ステップ 1：グラフを作成する

毎フレーム「Hello World」をコンソールに出力するシンプルなアクショングラフを作ります。**Window > Script Editor** を開き、次のコードを貼り付けます。

```python
import omni.graph.core as og

keys = og.Controller.Keys
(graph_handle, list_of_nodes, _, _) = og.Controller.edit(
    {"graph_path": "/action_graph", "evaluator_name": "execution"},
    {
        keys.CREATE_NODES: [
            ("tick", "omni.graph.action.OnTick"),
            ("print", "omni.graph.ui_nodes.PrintText")
        ],
        keys.SET_VALUES: [
            ("print.inputs:text", "Hello World"),
            ("print.inputs:logLevel", "Warning")  # ターミナルで出力を見えるよう Warning に設定
        ],
        keys.CONNECT: [
            ("tick.outputs:tick", "print.inputs:execIn")
        ],
    },
)
```

!!! note "evaluator_name とは"
    **evaluator** は、グラフをどの方式で評価（実行）するかを決める仕組みです。`evaluator_name` に `"execution"` を指定すると、実行ピンの接続に従ってイベント駆動で動く**アクショングラフ**として作成されます（GUI の **New Action Graph** で作るグラフと同じ種類です）。

- **Run** を押すと、Stage ツリーに新しい prim `/action_graph` が作成されます。
- prim を展開すると `tick` と `print` ノードがグラフの下に表示されます。これらは他の prim と同様に扱えます。
- **Play** を押すと、毎フレーム「Hello World」がコンソールに出力されます。
- **Window > Graph Editors > Action Graph** でグラフエディタを開き、**Edit Action Graph** アイコンをクリックすると、線で接続された 2 つのノードが確認できます。

## ステップ 2：グラフを編集する

グラフを作成したら、専用の API でグラフの要素を操作できます。

### 属性値の取得と設定

Script Editor の別タブに次のスニペットを貼り付けて実行します。

```python
import omni.graph.core as og

# 属性から既存の値を取得
existing_text = og.Controller.attribute("/action_graph/print.inputs:text").get()
print("Existing Text: ", existing_text)

# 新しい値を設定
og.Controller.attribute("/action_graph/print.inputs:text").set("New Texts to print")
```

これで「Print Text」ノードの値が「Hello World」から「New Texts to print」に変わります。ただし、この変更は最初のグラフ tick まで反映されません。したがって **Run** を押した時点ではまだ tick されておらず、現在の値「Existing Text: Hello World」が 1 度だけ出力されます。**Play** でシミュレーションを開始すると、tick ごとに更新後のテキスト「New Texts to print」が出力されます。

### ノードと接続を追加する

3 つ目のタブで、既存グラフにノードと接続を追加します。

```python
import omni.graph.core as og

og.Controller.create_node("/action_graph/new_node_name", "omni.graph.nodes.ConstantString")
og.Controller.attribute("/action_graph/new_node_name.inputs:value").set("This is a new node")
og.Controller.connect("/action_graph/new_node_name.inputs:value", "/action_graph/print.inputs:text")
```

`new_node_name` という新しいノードが作成され、「Print Text」ノードに接続されます。グラフエディタを開いていれば、ノードが 2 つから 3 つに増えて接続されているのが確認できます。

## ステップ 3：グラフの実行タイミングを制御する

デフォルトでは、グラフは毎フレーム評価されます。**オンデマンド**（呼び出したときだけ実行）に変更することもできます。これには `pipeline_stage` パラメータを使います。多くの場合、グラフ作成時に設定します。

1. Stage ツリーで前のグラフを選択し、**Delete** キーで削除します。
2. Script Editor の新しいタブに次のコードを貼り付けます。

```python
import omni.graph.core as og

keys = og.Controller.Keys
(demand_graph_handle, _, _, _) = og.Controller.edit(
    {
        "graph_path": "/ondemand_graph",
        "evaluator_name": "execution",
        "pipeline_stage": og.GraphPipelineStage.GRAPH_PIPELINE_STAGE_ONDEMAND
    },
    {
        keys.CREATE_NODES: [
            ("tick", "omni.graph.action.OnTick"),
            ("print", "omni.graph.ui_nodes.PrintText")
        ],
        keys.SET_VALUES: [
            ("print.inputs:text", "On Demand Graph"),
            ("print.inputs:logLevel", "Warning")
        ],
        keys.CONNECT: [
            ("tick.outputs:tick", "print.inputs:execIn")
        ],
    },
)
```

3. **Run** を押すと `/ondemand_graph` が作成されます。
4. **Play** で開始しても、明示的に評価を呼んでいないため、このグラフからは何も出力されません。
5. グラフを手動でトリガーするには、別タブで `demand_graph_handle.evaluate()` を実行します。シミュレーションが実行中であることを確認して **Run** を押すと、「On Demand Graph」が 1 度だけ出力されます。

!!! note "既存グラフのパイプラインステージ変更"
    既存のグラフに対しては `demand_graph_handle.change_pipeline_stage(og.GraphPipelineStage.GRAPH_PIPELINE_STAGE_ONDEMAND)` でも設定できます。物理コールバックやレンダリングコールバックにグラフをアタッチする詳しい例は `standalone_examples/api/isaacsim.core.experimental.api/omnigraph_triggers.py` を参照してください。

## まとめ

このチュートリアルでは、次の内容を学びました。

- `og.Controller.edit` を使い、`CREATE_NODES` / `SET_VALUES` / `CONNECT` でグラフを構築する方法
- `og.Controller.attribute(...).get()/set()` や `create_node` / `connect` でグラフを編集する方法
- `pipeline_stage` でオンデマンド実行を設定し、`evaluate()` で手動トリガーする方法

## 次のステップ

- [カスタム Python ノード](03_custom_python_nodes.md) で、独自の OmniGraph ノードを作る方法を学びます。
