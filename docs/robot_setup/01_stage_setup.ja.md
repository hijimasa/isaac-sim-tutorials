---
title: ステージのセットアップ
---

# ステージのセットアップ

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- ステージプロパティ（軸方向、単位、回転順序）の確認と設定
- Physics Scene の作成と重力・ブロードフェーズの設定
- グラウンドプレーンの追加
- ライティングの追加と調整

## はじめに

### 前提条件

- Isaac Sim がインストールされ、起動できること

### 所要時間

約 10〜15 分

### 概要

このチュートリアルでは、物理シミュレーションを行うための仮想環境のセットアップ方法を学びます。ステージプロパティの確認、Physics Scene の作成、グラウンドプレーンとライティングの追加を GUI 操作で行います。

## ステージプロパティの設定

1. **Edit > Preferences** を開き、Stage の設定を確認します。

    - **Up Axis**: Z（デフォルト）
    - **Stage Units**: メートル（デフォルト）
    - **Rotation Order**: XYZ

    ![Preferences](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_base_ref_gui_preferences.png)

## Physics Scene の作成

1. **Create > Physics > Physics Scene** を選択します。

2. Properties パネルで以下を確認・設定します：

    - **Gravity**: デフォルトの重力設定を確認
    - **Enable GPU Dynamics**: 効率化のためオフに設定
    - **Broadphase Type**: MBP に設定

    ![Physics Properties](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_base_ref_gui_physics_properties.png)

## グラウンドプレーンの追加

1. **Create > Physics > Ground Plane** を選択します。

2. Grid の表示を有効にして、地面の位置を視覚的に確認します。

    ![Eye icon](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_base_ref_gui_eyecon.png)

## ライティングの追加

1. **Create > Light > Sphere Light** を選択してスフィアライトを追加します。

2. Properties パネルで以下を調整します：

    - **Position**: シーンを照らす適切な位置に配置
    - **Intensity**: 明るさを調整
    - **Color**: ライトの色を設定
    - **Radius**: ライトの影響範囲を設定

    ![Lighting](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_base_ref_gui_lighting.png)

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. **ステージプロパティ**の確認と設定
2. **Physics Scene** の作成と物理エンジン設定
3. **グラウンドプレーン**の追加
4. **ライティング**の追加と調整

## 次のステップ

次のチュートリアル「[シンプルなロボットの組み立て](02_assemble_robot.md)」に進み、プリミティブ形状を使ったロボットの構築方法を学びましょう。
