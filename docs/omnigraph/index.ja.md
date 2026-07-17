---
title: OmniGraph チュートリアル
---

# OmniGraph チュートリアル

<span class="badge badge-advanced">Advanced</span>

OmniGraph を使ったグラフの作成・編集・拡張のチュートリアルです。

## 概要

**OmniGraph** は Omniverse のビジュアルプログラミングフレームワークです。複数システムの機能をつなぐグラフフレームワークであり、独自ノード（入力を受け取って処理し、出力を返す、グラフを構成する最小の処理単位）を組み込める計算フレームワークでもあります。Isaac Sim では、Replicator・ROS 2 ブリッジ・センサーアクセス・コントローラ・外部入出力デバイス・UI など、多くの機能の中心エンジンとして使われています。

エディタは **Window > Graph Editors > Action Graph** から開けます。

## チュートリアル

- [Isaac Sim OmniGraph チュートリアル](01_omnigraph_tutorial.md) — アクショングラフで JetBot を制御する
- [OmniGraph の Python スクリプティング](02_omnigraph_scripting.md) — Python API でグラフを構築・編集・実行する
- [カスタム Python ノード](03_custom_python_nodes.md) — `.ogn` と Python で独自ノードを作る
- [カスタム C++ ノード](04_custom_cpp_nodes.md) — C++ でノードを実装する
- [よく使う OmniGraph ショートカット](05_shortcuts.md) — コントローラグラフを数クリックで生成する

!!! note "本サイト補足：カスタム IPC ノード（Isaac Sim 6.0 新設）"
    Isaac Sim 6.0 の公式ドキュメントには、プロセス間通信（IPC）を行うカスタム OmniGraph ノードの構築ページが新設されています。本サイトには対応ページがまだないため、必要な場合は公式の [Building Custom IPC OmniGraph Nodes](https://docs.isaacsim.omniverse.nvidia.com/latest/omnigraph/omnigraph_custom_ipc_nodes.html) を参照してください。
