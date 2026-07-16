---
title: カスタム Replicator ランダマイゼーションノード
---

# カスタム Replicator ランダマイゼーションノード

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- カスタムのシーンランダム化 **Python スクリプト**の作成
- スクリプトの **OmniGraph ノード化**と、既存の SDG パイプライングラフへの手動追加
- **`@ReplicatorWrapper`** によるノードの **ReplicatorItem 化**と、Replicator API 経由での自動追加

## はじめに

### 前提条件

- [ROS 2 チュートリアル 26: カスタム Python OmniGraph ノード](../ros/26_custom_python_node.md)などで OmniGraph ノードの作り方（.ogn＋Python）を経験していること
- Replicator のランダム化 API の基本

### 所要時間

約 30〜40 分

### 概要

Replicator 組み込みのランダマイザ（`rep.randomizer.*`、`rep.distribution.*`）で足りない分布や配置ロジックが必要になったら、**自作のランダム化を OmniGraph ノードとして Replicator に統合**できます。このチュートリアルでは「球の表面上」「球の内部」「2 つの球の間」に一様分布するランダムな 3D 点を生成する 3 つのランダマイザを例に、**素の Python 関数 → OmniGraph ノード → ReplicatorItem** と段階的に統合レベルを上げていきます。

![Python でのランダム化結果](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_replicator_tut_gui_custom_og_randomizer_python.jpg)

## ステップ 1：Python 関数として書く

まず、球の半径（または 2 つの半径）を入力に、球面上／球内／2 球間のランダムな 3D 点を返す関数を用意します。これらの点をプリムの位置に使い、新しいステージにプリムを生成して回転・位置をランダム化するスクリプトを Script Editor で実行します。

この段階では Replicator とは無関係の、通常の USD API ベースのランダム化です（[チュートリアル 3 の例 3](03_getting_started_scripts.md)と同じ立ち位置）。

## ステップ 2：OmniGraph ノードにする

次に、各ランダム化関数を OmniGraph ノード化します。ノード定義（`OgnSampleInSphere.ogn`、`OgnSampleOnSphere.ogn`、`OgnSampleBetweenSpheres.ogn`）とノード実装（対応する `.py`）を作成します。

作成後、ランダマイザはグラフエディタのノードとして利用可能になります。

!!! note "このチュートリアルのノードは組み込み済み"
    チュートリアルで使う 3 ノードは、組み込みの `isaacsim.replicator.examples` エクステンションに既に含まれており、既定で利用できます。OmniGraph チュートリアルの手順で自作したノードは `omni.new.extension`（既定名の場合）経由で利用でき、見つからない場合は **Window > Extensions > THIRD PARTY** でエクステンションを有効化してください。

### SDG パイプライングラフへの手動追加

基本の SDG グラフ（作成したキューブの回転を毎フレームランダム化するもの）を Script Editor で作ると、`/Replicator/SDGPipeline` にグラフが生成されます。このグラフを開いて、カスタムノードを手動で追加できます。動作確認は UI の **Tools > Replicator > Preview**（または **Step**）で行います。

![SDG パイプラインへの手動追加](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_replicator_tut_gui_custom_og_randomizer_pipeline.jpg)

## ステップ 3：ReplicatorItem として統合する

手動追加を避けるには、ノードを **`@ReplicatorWrapper` デコレータ**で **ReplicatorItem** としてカプセル化します。こうすると、Replicator API から呼ぶだけで**ノードが SDG パイプライングラフに自動挿入**されます。つまり自作ランダマイザを `rep.randomizer.*` と同じ流儀で使えるようになります。

!!! warning "ノードパスの指定"
    ReplicatorWrapper 内の `create_node` はノードパスとして `"isaacsim.replicator.examples.OgnSampleInSphere"` を使っています。自作ノードが組み込みの `isaacsim.replicator.examples` エクステンションに含まれない場合は、このパスを自分のエクステンションのものに置き換えてください。

スニペットを Script Editor で実行すると、カスタムノードが自動的に SDG パイプライングラフへ追加されます。ランダム化のトリガーは同じく **Tools > Replicator > Preview**（または **Step**）です。

![ReplicatorItem による自動追加](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_replicator_tut_gui_custom_og_randomizer_replicator.jpg)

## まとめ

このチュートリアルでは、カスタムランダム化の 3 段階の統合レベルを扱いました：

| 段階 | 形態 | 特徴 |
|---|---|---|
| 1 | Python 関数 | 手軽。ただし SDG グラフとは独立で、トリガー制御は自前 |
| 2 | OmniGraph ノード | グラフエディタで扱える。SDG パイプラインへは手動追加 |
| 3 | ReplicatorItem（@ReplicatorWrapper） | Replicator API から組み込みランダマイザと同様に使える |

## 次のステップ

- [チュートリアル 12: モジュラービヘイビアスクリプティング](12_modular_scripting.md) - スクリプトコンポーネントとしてランダム化を部品化する方法を学びます。
