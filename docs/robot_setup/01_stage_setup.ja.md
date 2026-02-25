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

1. メニューバーの**Edit > Preferences** を開き、Stage の設定を確認します。

    - **Up Axis**: Z（デフォルト）<br>
      Isaac SimのデフォルトはZ軸です。アセット作成時に異なる上軸を持つプログラムを使用した場合、アセットが回転した状態でインポートされます。
    - **Stage Units**: メートル（デフォルト）<br>
      2022.1以前のIsaac Simではステージ単位がセンチメートルでしたが、現在はデフォルトでメートルです。ただしOmniverse Kitのデフォルト単位は依然としてセンチメートルです。USD単位が100倍ずれているように見える場合はこの点を留意してください。
    - **Rotation Order**: ZYX（デフォルト）<br>
      デフォルトではZ軸→Y軸→X軸の順で回転が実行されます。
    ![Preferences](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_base_ref_gui_preferences.png)

## Physics Scene の作成

1. メニューバーの**Create > Physics > Physics Scene** を選択します。

2. Properties パネルで以下を確認・設定します：

    - **Gravity**: デフォルトの重力設定を確認
    - **Enable GPU Dynamics**: 効率化のためオフに設定
    - **Broadphase Type**: MBP に設定

    ![Physics Properties](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_base_ref_gui_physics_properties.png)

## グラウンドプレーンの追加

1. メニューバーの**Create > Physics > Ground Plane** を選択します。

2. ビューポート上部の![Eye icon](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_base_ref_gui_eyecon.png)をクリックして表示されるメニューからGrid の表示を有効にして、地面の位置を視覚的に確認します。

    ![Gridの表示方法](images/01_show_grid.png)

## ライティングの追加
新しい Stage には、デフォルトで**defaultLight**が事前配置されています。これがなければ何も見えません。この**defaultLight**はステージ内の**Environment** Xformの子要素であり、右上の**Stage**タブのコンテキストツリーで確認できます。

追加のスポットライトを作成するには：

1. 光の反射を確認するため、まだ存在しない場合は地面平面を追加します。メニューバーの**Create > Physics > Ground Plane**から追加できます。
2. メニューバーの**Create > Light > Sphere Light**を選択します。
3. ステージ上でライトを配置します。
    - 右上の**Stage**タブで、コンテキストツリー内の新規作成したライトを選択します。
    - 下部の**Property**タブ、**Transform**セクションで**Translate**ツールを使用し、グラウンドプレーン上空の位置（例：(0, 0, 1)）に移動させます。
    - **Property**タブの**Transform**セクションで、**Orient**ツールを使用し回転を(0, 60, 0)に設定します。
4. ライトの色・明るさ・範囲プロパティを変更：
    - **Property**タブ内の**Main > Color**でカラーバーをクリックし任意の色を選択。例：薄緑色 (RGB: 0.5, 1.0, 0.5)。
    - 同じく**Property**タブ内で、**Main > Intensity**を**1e6**に、**Main > Radius**を**0.05**に変更します。
    - **Shaping**セクションで、コーン角度を45度、コーンソフトネスを0.05に変更します。
5. 新規スポットライトを視認しやすくするため、**defaultLight**の強度を下げます。そのライトの**Property**タブを開き、**Main > Intensity**を**300**に設定します。

    ![Lighting](images/02_lighting.png)

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. **ステージプロパティ**の確認と設定
2. **Physics Scene** の作成と物理エンジン設定
3. **グラウンドプレーン**の追加
4. **ライティング**の追加と調整

## 次のステップ

次のチュートリアル「[シンプルなロボットの組み立て](02_assemble_robot.md)」に進み、プリミティブ形状を使ったロボットの構築方法を学びましょう。
