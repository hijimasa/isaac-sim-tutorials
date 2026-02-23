---
title: URDF インポート
---

# URDF インポート

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- URDF ファイルを Isaac Sim にインポートする方法
- インポート設定（ベースタイプ、密度、コリジョンプロパティ）の構成
- コリジョンメッシュの可視化と確認
- Python スクリプトによるプログラム的なインポート
- ROS 2 ノードからの URDF インポート

## はじめに

### 前提条件

- Isaac Sim のクイックチュートリアルを完了していること
- URDF Importer Extension の基本を理解していること

### 所要時間

約 10〜15 分

### 概要

このチュートリアルでは、URDF（Unified Robot Description Format）ファイルを Isaac Sim にインポートし、USD 形式に変換する方法を学びます。GUI での直接インポート、Python スクリプトによるインポート、ROS 2 ノードからのインポートの3つの方法を解説します。

## GUI での直接インポート

1. `isaacsim.asset.importer.urdf` エクステンションを有効化します。

    ![エクステンション有効化](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_full_tut_gui_import_urdf_enable_extension.png)

2. **File > Import** から URDF ファイルを選択します。

    ![ロボット選択](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_full_tut_gui_import_urdf_select_robot.png)

3. インポート設定（出力先、ベースタイプ、密度、コリジョンプロパティ）を構成し、Import をクリックします。

    ![インポート結果](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_full_tut_viewport_import_urdf_franka.png)

### 主な設定項目

| 設定 | 説明 |
|------|------|
| Static Base / Moveable Base | ロボットのベース固定/移動の設定 |
| Natural Frequency | ジョイント安定性のための固有振動数 |
| Self-Collision | 自己衝突の許可設定 |

## コリジョンメッシュの確認

ビューポートの目のアイコン → **Show by type > Physics > Colliders > All** でコリジョンメッシュを可視化できます。

![コリジョンメッシュ](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_full_tut_viewport_import_urdf_visualize_franka_colliders.png)

## UI 統合例

Robotics Examples タブには、事前設定された例が用意されています：

- Nova Carter URDF
- Franka URDF
- Kaya URDF
- UR10 URDF

![UI 統合例](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_full_ext-isaacsim.asset.importer.urdf-2.3.0_gui_example_import_franka.png)

## Python スクリプトによるインポート

`_urdf.acquire_urdf_interface()` と `ImportConfig()` を使用してプログラム的にインポートできます。

![Python インポート](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isaac_sim_import_urdf.gif)

### モバイルロボットの設定

- Moveable Base を使用
- ホイールには velocity drive、ステアリングには position drive を設定
- Joint Drive Strength でダンピングを調整

### トルク制御ロボット（四足歩行ロボット）

- Moveable Base を有効化
- ジョイントドライブタイプを "None" に設定
- スティフネス/ダンピングパラメータを構成

## ROS 2 ノードからのインポート

Linux 環境では、ROS 2 ノードから直接 URDF をインポートできます：

1. ターミナル 1：Transform Publisher を起動
2. ターミナル 2：ノード名を確認
3. Isaac Sim → **File > Import from ROS 2 URDF Node**

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. GUI による **URDF ファイルの直接インポート**
2. **インポート設定**の構成（ベースタイプ、コリジョン、ドライブ）
3. **コリジョンメッシュ**の可視化
4. **Python スクリプト**によるプログラム的インポート
5. **ROS 2 ノード**からのインポート

## 次のステップ

- [チュートリアル 2: URDF エクスポート](02_export_urdf.md) - USD から URDF への変換方法を学びます。
