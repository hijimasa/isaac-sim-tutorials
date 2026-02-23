---
title: シンプルなロボットの組み立て
---

# シンプルなロボットの組み立て

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- プリミティブ形状を使ったロボットボディと車輪の作成
- Rigid Body と Collider の物理プロパティ設定
- コリジョンメッシュの確認方法
- 摩擦係数・反発係数の設定
- マテリアル（外観）の適用

## はじめに

### 前提条件

- [チュートリアル 1: ステージのセットアップ](01_stage_setup.md) を完了していること

### 所要時間

約 15〜20 分

### 概要

このチュートリアルでは、GUI 操作でプリミティブ形状（キューブ、シリンダー）を使い、二輪ロボットの基本構造を組み立てます。物理プロパティの設定、コリジョンメッシュの確認、マテリアルの適用を学びます。

## オブジェクトの追加

1. ボディ用の Xform を作成し、Cube ジオメトリを追加します。

2. 車輪用の Xform を2つ作成し、それぞれ Cylinder ジオメトリを追加します。

3. 各コンポーネントの位置とスケールを調整します。

    ![ロボットボディ](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_base_ref_gui_simple_objs_body.png)

## 物理プロパティの追加

1. 各オブジェクトに **Rigid Body with Colliders Preset** を適用します。

2. 重力シミュレーションが有効であることを確認します。

    ![物理プロパティ](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_base_ref_gui_simple_objs_physics.webp)

## コリジョンメッシュの確認

1. ビューポートの設定でコリジョンのアウトラインを表示します。

2. すべてのオブジェクトのコリジョン形状を確認します。

    ![コリジョン](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_base_ref_gui_collision.png)

## 摩擦・反発パラメータの追加

1. Physics Material を作成します。

2. 摩擦係数と反発係数を調整します。

3. リジッドボディにマテリアルを割り当てます。

    ![マテリアル](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_base_ref_gui_materials.png)

## 外観マテリアルの設定

1. OmniPBR マテリアルを作成して外観を設定します。

2. ボディと車輪にそれぞれ異なる色を割り当てます。

    ![新規マテリアル](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_base_ref_gui_new_materials.png)

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. **プリミティブ形状**を使ったロボット構造の構築
2. **Rigid Body と Collider** の物理プロパティ設定
3. **コリジョンメッシュ**の可視化と確認
4. **摩擦・反発係数**の設定
5. **外観マテリアル**の適用

## 次のステップ

次のチュートリアル「[基本ロボットのアーティキュレーション](03_articulate_robot.md)」に進み、ジョイントとアーティキュレーションの設定方法を学びましょう。
