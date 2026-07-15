---
title: ランダム化スニペット集
---

# ランダム化スニペット集

## 学習目標

このページでは、**USD / Isaac Sim API を使ったランダム化のスニペット集**を紹介します。組み込みの Replicator ランダマイザでは足りない・適用できないシナリオ向けのコード例です。

## はじめに

### 前提条件

- USD の基本と Script Editor でのコード実行
- サブフレームなどの Replicator の基本概念（[チュートリアル 3](03_getting_started_scripts.md)参照）

### 概要

各スニペットは Replicator のサンプルスニペットと同じ構成・関数名になるよう設計されており、`write_data=True` を設定するとデータをディスクに書き出すこともできます。**完全なコードは[公式ページ](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/replicator_tutorials/tutorial_replicator_isaac_randomizers.html)からコピーして Script Editor で実行**してください。このページでは各スニペットが「何をするものか・どんなときに使うか」を整理します。

## スニペット 1：光源のランダム化

キューブと球のある環境をセットアップし、指定した数のライトをスポーンして、選択した属性（色・強度・位置など）を指定フレーム数にわたってランダム化します。

![光源のランダム化](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isaac_tutorial_replicator_randomization_lights.gif)

**使いどころ**：Replicator の組み込みライトランダマイザより細かく、USD 属性レベルでライトを制御したい場合。

## スニペット 2：テクスチャのランダム化

環境にキューブと球をスポーンし、テクスチャを指定フレーム数ランダム化した後、**元のマテリアルを再割り当て**します。新しいマテリアルの作成とプリムへの割り当て方法も含まれています。

![テクスチャのランダム化](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isaac_tutorial_replicator_randomization_textures.gif)

**使いどころ**：ランダム化後に元の見た目へ戻す必要がある場合（[チュートリアル 8](08_ur10_palletizing.md) のマテリアルキャッシュと同じ発想）。

## スニペット 3：逐次的（連鎖）ランダム化

**前のランダム化の結果を次のランダム化の入力に使う**、より複雑な例です。フォークリフト・パレット・ビン・ドームライトをセットアップし、毎フレーム：

1. ドームライトのテクスチャをサイクル
2. パレットをランダムな位置に移動
3. **ビンをパレットの上に完全に載るように**移動（パレットの位置に依存）
4. カメラを球面上のほぼ等間隔な点を巡るカスタムサンプラーで移動し、**ビンを注視**させる

![連鎖ランダム化](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isaac_tutorial_replicator_randomization_chained_persp.gif)

**使いどころ**：「A の位置が決まってから B を A の上に置く」のような**依存関係のあるランダム化**。グラフベースの Replicator ランダマイザでは表現しにくい部分です。

## スニペット 4：物理ベースのランダム体積充填

複数の面へのオブジェクトの**積み上げ**をランダム化します。選択エリアにパレットをランダムにスポーンし、その上に物理シミュレーションされる箱をスポーンします。工夫が詰まっています：

- パレットの周囲に**一時的なコリジョンボックス**を作り、箱の落下中のこぼれ落ちを防止
- 落下後、箱をさまざまな方向に動かし、最後に**パレット中心へ引き寄せて**安定した積み上がりに
- 滑らかに安定位置へ移動できるよう、シミュレーション中は箱の**摩擦を一時的に低減**
- 最後にコリジョンエリアを除去（以降は箱が床に落ちることも可能に）

![体積充填](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isaac_tutorial_replicator_randomization_volume_fill.gif)

**使いどころ**：倉庫シーンなどで「自然に積まれた荷物」を大量生成したい場合。

## スニペット 5：SimReady アセットの SDG 例

[SimReady Assets](https://developer.nvidia.com/omniverse/simready-assets)（物理的に正確なプロパティ・挙動・データ接続を持つ、シミュレーション最適化済みの 3D アセット）を使ってシーンをランダム化する例です。テーブル・皿・皿の上のアイテムでシーンを作り、しばらくシミュレーションしてからキャプチャ画像を保存します。

```bash
./python.sh standalone_examples/api/isaacsim.replicator.examples/simready_assets_sdg.py
```

!!! warning "実行の前提"
    この例は**非同期モードでのみ**動作し、検索リクエストを処理するために **SimReady Explorer ウィンドウが有効**になっている必要があります。

![SimReady アセットの SDG](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_replicator_tut_viewport_randomization_simready_assets.jpg)

## まとめ

| スニペット | キーとなるテクニック |
|---|---|
| 光源のランダム化 | USD 属性レベルのライト制御 |
| テクスチャのランダム化 | マテリアルのキャッシュと復元 |
| 逐次的ランダム化 | 依存関係のある連鎖ランダム化、球面カメラサンプラー |
| 物理ベースの体積充填 | 一時コリジョン壁、摩擦の一時低減、中心への引き寄せ |
| SimReady アセット | 物理的に正確なアセットの検索とスポーン |

## 次のステップ

- [チュートリアル 14: 便利なスニペット集](14_isaac_snippets.md) - データアクセスとキャプチャ制御のスニペット集です。
