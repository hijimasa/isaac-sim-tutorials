---
title: ROS 2 Python カスタム OmniGraph ノード
---

# ROS 2 Python カスタム OmniGraph ノード

## 学習目標

これは発展的（オプション）なチュートリアルです。以下の内容を習得できます：

- Isaac Sim 内での ROS 2 **rclpy** Python インターフェースの使用
- トピック（`std_msgs/msg/Int32`）を購読し、受信した数値の**フィボナッチ数**を計算して出力する、基本的な**カスタム OmniGraph Python ノード**の作成（[Isaac Sim VS Code Edition](https://marketplace.visualstudio.com/items?itemName=NVIDIA.isaacsim-vscode-edition) を使用）

## はじめに

### 前提条件

- [ROS 2 セットアップ](00_setup.md)が完了していること（ROS 2 のインストール、ROS 2 エクステンションの有効化、Isaac Sim ROS 2 ワークスペースのビルド、環境変数の設定）
- 公式の Custom Python Nodes チュートリアル（OmniGraph のカスタム Python ノードの書き方）を完了していること

### 所要時間

約 30〜40 分

### 概要

[チュートリアル 22](22_generic_pub_sub.md) の汎用ノードでも大抵のメッセージは扱えますが、「**受信したデータに独自の処理を加えてからグラフに流したい**」場合は、カスタム OmniGraph ノードの出番です。このチュートリアルでは、ROS 2 の購読・計算・グラフへの出力を 1 つのノードにまとめた例として、`/number` トピックの整数を受信してフィボナッチ数を計算するノードを作ります。

## ステップ 1：エクステンションのテンプレートを作成する

1. Isaac Sim VS Code Edition（VS Code 拡張機能）で **Template > Extension** を開き、新しい Isaac Sim エクステンションを作成するウィザードを起動します。次のフィールドを設定します：

| フィールド | 値 |
|---|---|
| **Ext. name** | `custom.python.ros2_node` |
| **Ext. path** | エクステンションを作成するパス |
| **Ext. title** | ROS 2 Python Custom OmniGraph Node |
| **Ready-to-use extension** | チェック（すぐ使える Python エクステンションを生成） |
| **Omnigraph node** | チェック（OmniGraph 用のファイル／フォルダを生成） |

![VS Code エクステンションテンプレート](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/tutorial_ros2_custom_omnigraph_node_python_vscode_extension_template.png)

2. エクステンション設定ファイル（`custom.python.ros2_node/config/extension.toml`）を編集し、`[dependencies]` の下に Isaac Sim の ROS 2 ブリッジを依存として追加します：

```toml
"isaacsim.ros2.bridge" = {}
```

## ステップ 2：ノードの入出力を定義する（.ogn ファイル）

OmniGraph 定義ファイル（`custom.python.ros2_node/custom/python/ros2_node/ogn/python/nodes` フォルダの `OgnCustomPythonRos2NodePy.ogn`）を次の内容にします。この定義は、2 つの入力（実行トリガーと購読するトピック名）と 2 つの出力（実行トリガーと計算したフィボナッチ数）を持つノードを表します：

```json
{
    "CustomPythonRos2NodePy": {
        "version": 1,
        "language": "python",
        "icon": "icons/icon.svg",
        "uiName": "Custom Python ROS 2 Node",
        "description": [
            "This node subscribes to a ROS 2 topic (with message type 'std_msgs/msg/Int32') and computes and outputs the Fibonacci number"
        ],
        "categoryDefinitions": "config/CategoryDefinition.json",
        "categories": ["extension:Category"],
        "inputs": {
            "execIn": {
                "type": "execution",
                "description": "Input execution trigger"
            },
            "topic": {
                "type": "string",
                "uiName": "Subscription topic",
                "description": "Topic to subscribe to",
                "default": "/number"
            }
        },
        "outputs": {
            "execOut": {
                "type": "execution",
                "description": "Output execution trigger"
            },
            "fibonacci": {
                "type": "uint64",
                "uiName": "Fibonacci",
                "description": "Computed Fibonacci number"
            }
        }
    }
}
```

!!! tip ".ogn ファイルの文法"
    `.ogn` ファイルの文法の詳細は公式の OGN Reference Guide を、入出力に使える属性データ型は OmniGraph の Attribute Data Types を参照してください。

## ステップ 3：ノードの処理を実装する（Python ファイル）

同じフォルダの `OgnCustomPythonRos2NodePy.py` を次の内容にします。構成は 2 クラスです：

- **`OgnCustomPythonRos2NodePyInternalState`** — ROS との通信を担うノードごとの内部状態クラス。ROS 2 ノードと購読を作成し、受信メッセージを処理します。`BaseResetNode` を継承しており、タイムライン停止時にカスタムのリセット処理（購読とノードの破棄）を行います。
- **`OgnCustomPythonRos2NodePy`** — OmniGraph ノード本体。入力値と内部状態に基づいて出力を計算・設定します。

```python
import rclpy
import std_msgs.msg

import omni.graph.core
from isaacsim.core.nodes import BaseResetNode

from custom.python.ros2_node.ogn.OgnCustomPythonRos2NodePyDatabase import OgnCustomPythonRos2NodePyDatabase


class OgnCustomPythonRos2NodePyInternalState(BaseResetNode):
    """ノードごとの状態情報を保持するためのクラス。

    タイムライン停止時にカスタムリセットを行うため BaseResetNode を継承する。"""

    def __init__(self):
        """ノードごとの状態情報を初期化する"""
        self._data = None
        self._ros2_node = None
        self._subscription = None
        # カスタムリセット用のタイムラインイベントを設定するため親クラスを呼ぶ
        super().__init__(initialize=False)

    @property
    def data(self):
        """受信データを取得し、読み取り後にクリアする"""
        tmp = self._data
        self._data = None
        return tmp

    def _callback(self, msg):
        """購読がメッセージを受信したときに呼ばれる関数"""
        self._data = msg.data

    def initialize(self, node_name, topic_name):
        """ROS 2 ノードと購読を初期化する"""
        try:
            rclpy.init()
        except:
            pass
        # ROS 2 ノードを作成
        if not self._ros2_node:
            self._ros2_node = rclpy.create_node(node_name=node_name)
        # ROS 2 購読を作成
        if not self._subscription:
            self._subscription = self._ros2_node.create_subscription(
                msg_type=std_msgs.msg.Int32, topic=topic_name, callback=self._callback, qos_profile=10
            )
        self.initialized = True

    def spin_once(self, timeout_sec=0.01):
        """ROS 2 の処理を回し、トピックからの受信メッセージがあれば取り込む"""
        rclpy.spin_once(self._ros2_node, timeout_sec=timeout_sec)

    def custom_reset(self):
        """タイムライン停止時に ROS 2 の購読とノードを破棄する"""
        if self._ros2_node:
            self._ros2_node.destroy_subscription(self._subscription)
            self._ros2_node.destroy_node()

        self._data = None
        self._ros2_node = None
        self._subscription = None
        self.initialized = False

        rclpy.try_shutdown()


class OgnCustomPythonRos2NodePy:
    """OmniGraph ノードクラス"""

    @staticmethod
    def fibonacci(n):
        """与えられた数のフィボナッチ数列の値を反復計算する"""
        if n <= 0:
            return 0
        elif n == 1:
            return 1
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b

    @staticmethod
    def internal_state():
        """ノードごとの状態情報を取得する"""
        return OgnCustomPythonRos2NodePyInternalState()

    @staticmethod
    def compute(db) -> bool:
        """入力と内部状態に基づいて出力を計算する"""
        state = db.per_instance_state

        try:
            # 状態（ROS 2 ノードと購読）が初期化済みか確認
            if not state.initialized:
                state.initialize(node_name="custom_python_ros2_node", topic_name=db.inputs.topic)
            # spin して受信メッセージを取り込む
            state.spin_once()

            # 受信データを取得
            number = state.data
            if number is not None:
                # 受信した数のフィボナッチ数を計算
                value = OgnCustomPythonRos2NodePy.fibonacci(number)
                # uint64 のオーバーフローを確認
                if value > 2**64:
                    db.log_warn(f"Fibonacci number {number} exceeds uint64's storage capacity")
                    return False
                # 値を出力し、出力実行をトリガーする
                db.outputs.fibonacci = value
                db.outputs.execOut = omni.graph.core.ExecutionAttributeState.ENABLED
        except Exception as e:
            db.log_error(f"Computation error: {e}")
            return False
        return True

    @staticmethod
    def release(node):
        """ノードごとの状態情報を解放する"""
        try:
            state = OgnCustomPythonRos2NodePyDatabase.per_instance_internal_state(node)
        except Exception as e:
            return
        # 状態をリセット
        state.reset()
        state.initialized = False
```

## ステップ 4：カスタムノードを動かす

!!! warning "先にエクステンションを有効化すること"
    OmniGraph ノードが利用可能になるには、まずカスタムエクステンションを有効化する必要があります。**Window > Extensions** で `custom.python.ros2_node` を検索して有効化してください。

1. 新しいステージで Action Graph を作成し、次のノードを追加・接続します：

| ノード | 役割 |
|---|---|
| **On Playback Tick** | 毎フレーム実行 |
| **Custom Python ROS 2 Node** | 作成したカスタムノード |
| **To String** | カスタムノードの出力を文字列に変換 |
| **Print Text** | 出力をビューポートまたはターミナルに表示。Property パネルで **To Screen** にチェックを入れるとビューポートに表示される |

![カスタムノードのグラフ](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/tutorial_ros2_custom_omnigraph_node_python_node_graph.png)

2. シミュレーションを **Play** します。
3. 新しい ROS 2 ターミナルから `/number` トピックに数値を配信します：

    ```bash
    ros2 topic pub -1 /number std_msgs/msg/Int32 "{data: 10}"
    ```

4. メッセージが受信されると、ビューポート左上にフィボナッチ数が表示されます（新しい値を受信しないと表示は徐々にフェードします）。

    ![結果の表示](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/tutorial_ros2_custom_omnigraph_node_python_results_display.png)

5. 別の数値を配信して、Isaac Sim 側の表示が変わることを確認します。

!!! tip "コンソールに表示するには"
    Isaac Sim のコンソールで値を確認したい場合は、Print Text ノードの **To Screen** のチェックを外し、**Log Level** を Warning に設定してください。

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. エクステンション内での**カスタム OmniGraph Python ノード**の作成（.ogn 定義＋ Python 実装）
2. カスタムノード内で **rclpy** の ROS 2 ノードを作ってトピックを購読し、フィボナッチ計算の結果で下流ノードをトリガーする実装パターン（内部状態クラス、`spin_once`、タイムライン停止時の `custom_reset`）

## 次のステップ

- [チュートリアル 27: ROS 2 カスタム C++ OmniGraph ノード](27_custom_cpp_node.md) - 同様のカスタムノードを C++ で作成します。
