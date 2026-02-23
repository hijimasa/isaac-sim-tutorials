---
title: ロボット設定ファイルの生成
---

# ロボット設定ファイルの生成

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- USD to URDF Exporter を使った URDF ファイルの生成
- Lula Robot Description Editor を使ったロボット記述ファイルの生成
- コリジョンスフィアの生成と編集
- XRDF ファイルのエクスポート

## はじめに

### 前提条件

- [チュートリアル 7: マニピュレータの設定](07_configure_manipulator.md) を完了していること

### 所要時間

約 15〜20 分

### 概要

このチュートリアルでは、UR10e ロボットと 2F-140 グリッパーのロボット設定ファイルを、Lula Robot Description Editor と USD to URDF Exporter を使って生成します。これらのファイルはキネマティクスソルバーに必要な情報を提供します。

## ロボット URDF の生成

1. Isaac Sim USD to URDF Exporter エクステンションを有効にします。

2. URDF ファイルをエクスポートします。

    ![URDF エクスポート](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_export_urdf.png)

## Lula ロボット記述ファイルとコリジョンスフィアの生成

1. Isaac Sim Lula エクステンションを有効にします。

2. ロボットアセットを Lula 用に準備します。

3. Lula Robot Description Editor でジョイントを設定します。

    ![Lula Robot Description Editor](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_lula_robot_description_editor.png)

4. コリジョンスフィアを生成します。

    ![コリジョンスフィア](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_lula_link_sphere_editor_add_spheres.png)

5. Lula ロボット記述ファイルをエクスポートします。

    ![エクスポート](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_lula_export_robot_description_file.png)

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. **USD to URDF Exporter** による URDF ファイルの生成
2. **Lula Robot Description Editor** によるロボット記述ファイルの生成
3. **コリジョンスフィア**の生成と編集
4. 設定ファイルの**エクスポート**

## 次のステップ

次のチュートリアル「[ピック＆プレースの例](09_pick_and_place.md)」に進み、キネマティクスソルバーと RMPFlow を使ったマニピュレーションタスクを実行する方法を学びましょう。
