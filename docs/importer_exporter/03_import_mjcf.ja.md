---
title: MJCF インポート
---

# MJCF インポート

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- MJCF（MuJoCo）モデルファイルを Isaac Sim にインポートする方法
- GUI および Python スクリプトによるインポート方法
- インポート後のロボットのアーティキュレーション設定

## はじめに

### 前提条件

- Isaac Sim のクイックチュートリアルを完了していること

### 所要時間

約 5〜10 分

### 概要

このチュートリアルでは、MJCF（MuJoCo XML）形式のモデルファイルを Isaac Sim にインポートし、USD 形式に変換する方法を学びます。GUI からの対話的なインポートと Python スクリプトによるプログラム的なインポートの2つの方法を解説します。

## GUI でのインポート

1. **Window > Extensions** から MJCF Importer エクステンションを有効化します。

    ![MJCF インポートダイアログ](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_base_ext-isaacsim.asset.importer.mjcf-2.3.0_gui_0.png)

2. **File > Import** でファイル選択ダイアログを開きます。

3. エクステンションのアセットフォルダ（`/data/mjcf`）から `nv_humanoid.xml` などのファイルを選択します。

4. インポート設定を構成し、Import をクリックします。

    ![インポートされたヒューマノイド](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_base_ext-isaacsim.asset.importer.mjcf-2.3.0_gui_humanoid.png)

## Python スクリプトによるインポート

Script Editor（**Window > Script Editor**）を使ったプログラム的なインポートも可能です：

1. `MJCFCreateImportConfig` コマンドでインポート設定を作成
2. `fix_base()` や `make_default_prim()` などのオプションを設定
3. `MJCFCreateAsset` コマンドでアセットを作成
4. 物理シーンの初期化（重力設定）
5. ライティングの追加

### 主な設定オプション

| オプション | 説明 |
|-----------|------|
| `fix_base` | ロボットのベースを固定するかどうか |
| `make_default_prim` | デフォルトプリムとして設定するかどうか |

## インポート後の設定

- インポートされたロボットはシミュレーション内のアーティキュレーションとして変換されます
- インポート後にセンサー、マテリアル、ジョイント設定を変更可能
- アーティキュレーションの安定性はスタビリティガイドを参照して調整できます

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. **GUI** による MJCF ファイルのインポート
2. **Python スクリプト**によるプログラム的インポート
3. インポート後の**アーティキュレーション設定**

## 次のステップ

- [チュートリアル 4: ShapeNet インポーター](04_shapenet_importer.md) - ShapeNet データベースからの3Dモデルインポート方法を学びます。
