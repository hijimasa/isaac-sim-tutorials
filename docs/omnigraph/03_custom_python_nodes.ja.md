---
title: カスタム Python ノード
---

# カスタム Python ノード

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- OmniGraph ノードが `.ogn` ファイルと関数ファイル（Python/C++）の 2 つで定義されること
- `.ogn`（JSON）でノードの入出力・パラメータを定義する方法
- Python で `compute` 関数を実装する方法
- 作成したカスタムノードを Isaac Sim に組み込む方法

## はじめに

### 前提条件

- [Isaac Sim OmniGraph チュートリアル](01_omnigraph_tutorial.md) と [Python スクリプティング](02_omnigraph_scripting.md) を理解していること
- JSON と Python の基本を理解していること

### 所要時間

約 15〜20 分

### 概要

Isaac Sim には多数のデフォルトノードが用意されています（Omnigraph Node Library や API ドキュメントで確認できます）。それでは不十分な場合、独自のノードを作成して Isaac Sim に統合できます。

ノードは 2 つのファイルで定義されます。

- **`.ogn` ファイル** … ノードの構造（入力・出力・パラメータ）を定義する JSON ファイル
- **関数ファイル** … ノードの動作を定義する Python または C++ ファイル

このチュートリアルでは Python ノードに焦点を当てます。

!!! note "ファイル名の接頭辞"
    すべての OmniGraph ノードファイルは接頭辞 `Ogn` で始まります。これはパーサーが期待する規約です。

## ステップ 1：ノード定義（.ogn）を書く

`.ogn` ファイルは、ノードの入力・出力・パラメータを定義する JSON です。シンプルなノード定義の例です。

```json
{
 "NodeName": {
     "version": 1,
     "categories": "examples",
     "description": ["Minimum Example"],
     "language": "python",
     "metadata": {
         "uiName": "minimum example"
     },
     "inputs": {
         "execIn": {
             "description": "the trigger input that starts the node",
             "type": "execution"
         },
         "value_input": {
             "type": "double",
             "description": "a number",
             "default": 0.0
         }
     },
     "outputs": {
         "output_bool": {
             "type": "bool",
             "description": "let output be a boolean"
         }
     }
   }
}
```

!!! note "`execIn` 入力について"
    `execIn` は、ノードをトリガーするための特別な入力です。このトリガーは **Action Graph** でのみ意味を持ちます。Action Graph では、物理 tick やステージイベント（ステージの開閉など）で明示的にノードを実行する必要があります。一方 **Push Graph** では、ノードは毎フレーム自動的に実行されるため `execIn` 入力は不要です。

## ステップ 2：関数定義を書く

入力の数が 0 より大きいかどうかで真偽値を出力する、最小限の Python ノードの例です。

```python
class OgnNodeName:
    @staticmethod
    def compute(db):
        db.outputs.out = bool(db.inputs.value_input > 0.0)
        return True
```

!!! note "実装上の注意"
    - クラス名は `.ogn` ファイル内のノード名と一致させ、ファイル名もクラス名と一致させる必要があります。
    - `compute` 関数が `execIn` 入力によってトリガーされる処理です。引数は 1 つで、ノードの入出力を含むデータベース（`db`）を受け取ります。成功時は `True`、失敗時は `False` を返します。
    - このノードは内部状態を持たないため、通過するデータは次の tick で失われます。tick 間でデータを保存したい場合は「internal state」を使います。

## ステップ 3：カスタムノードを使う

作成したノードを使うには、次の 2 通りの方法があります。

- 既存ノードの `.py` / `.ogn` ファイルを含むディレクトリを持つ拡張機能に、自作の `.py` / `.ogn` ファイルを挿入する（独自の拡張機能を作らずに済みます）。
- 独自の拡張機能を作成し、そこにファイルを挿入する。

## Isaac Sim のノードを例として活用する

既存の OmniGraph ノードのコードを調べて、ノードの構造の例として活用したり、自分用に改変したりできます。特定のノードのバックエンド `.py` / `.ogn` ファイルを探すには、エディタウィンドウでノードにマウスを重ねます。ツールチップに拡張機能名が括弧で表示されるので、`exts/isaacsim.<ext_name>/isaacsim/<ext_name>/ogn/python/nodes/` にあるフォルダに移動します。

!!! warning
    すべてのノードが Python で書かれているわけではなく、C++ バックエンドのものもあります。そのため、リスト上のすべてのノードに対応する `.py` / `.ogn` が見つかるとは限りません。また、`Ogn<node_name>Database.py` のリストがあるフォルダは、ノードの Python 記述を含むディレクトリでは**ありません**。

## まとめ

このチュートリアルでは、次の内容を学びました。

- OmniGraph ノードが `.ogn`（構造）と関数ファイル（動作）で定義されること
- `.ogn` で入出力・パラメータを定義し、`execIn` が Action Graph でのトリガーになること
- `compute(db)` 関数で `db.inputs` / `db.outputs` を扱う方法
- カスタムノードを既存拡張機能または独自拡張機能に組み込む方法

## 次のステップ

- C++ ノードについては [カスタム C++ ノード](04_custom_cpp_nodes.md) を参照してください。
