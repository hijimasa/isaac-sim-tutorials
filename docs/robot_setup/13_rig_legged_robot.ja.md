---
title: 脚ロボットのリギング
---

# 脚ロボットのリギング

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- ロコモーションポリシーに合わせた初期ロボット姿勢の設定
- Joint State API とドライブ API の設定
- ジョイント設定（スティフネス、ダンピング、力制限、アーマチュア）の設定
- 設定の検証スクリプトによる確認

## はじめに

### 前提条件

- [チュートリアル 3: 基本ロボットのアーティキュレーション](03_articulate_robot.md) を完了していること

### 所要時間

約 20〜30 分

### 概要

このチュートリアルでは、H1 ヒューマノイドロボットを例に、ロコモーションポリシーの設定仕様に合わせて脚ロボットをリギングする方法を学びます。初期姿勢の設定、ジョイント設定の構成、設定の検証を行います。

## 初期ロボット姿勢の設定

1. H1 USD ファイルを開きます。

2. Joint State API を作成します。

3. ジョイントを選択・フィルタリングします。

4. Physics Joint State Angular と Angular Drive API を追加します。

    ![初期姿勢](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_rigging_humanoid_1.png)

5. ターゲット位置と速度の属性を設定します。

6. ラジアンから度への変換を行います。

7. Fixed Joint で無限落下を防止します。

    ![シミュレーション](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_rigging_humanoid_2.webp)

## ジョイント設定の構成

1. 環境定義からアクチュエータプロパティを設定します。

2. スティフネスとダンピングの値を設定します。

3. 力制限（Effort Limit）を設定します。

4. アーマチュアと摩擦を設定します。

5. 最大ジョイント速度を設定します。

    ![ジョイント設定](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_rigging_humanoid_3.png)

## ジョイント設定の検証

1. Script Editor で検証スクリプトを実行します。

2. 出力値が仕様と一致することを確認します。

    ![検証結果](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_rigging_humanoid_4.png)

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. **初期ロボット姿勢**の設定
2. **Joint State API** とドライブ API の設定
3. **ジョイント設定**（スティフネス、ダンピング、力制限）の構成
4. **検証スクリプト**による設定確認
