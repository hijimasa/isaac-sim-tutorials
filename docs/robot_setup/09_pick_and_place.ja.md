---
title: ピック＆プレースの例
---

# ピック＆プレースの例

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- グリッパーの制御方法
- Lula キネマティクスソルバーを使ったターゲット追従
- RMPFlow によるモーション制御の設定
- ピック＆プレースタスクの実装

## はじめに

### 前提条件

- [チュートリアル 8: ロボット設定ファイルの生成](08_generate_robot_config.md) を完了していること

### 所要時間

約 20〜30 分

### 概要

このチュートリアルでは、UR10e ロボットと 2F-140 グリッパーを使ってピック＆プレースタスクを実行します。Lula キネマティクスソルバーによるターゲット追従と RMPFlow によるモーション制御を組み合わせて、オブジェクトのマニピュレーションを行います。

## グリッパー制御の例

グリッパーの開閉を制御する基本的な方法を学びます。

![グリッパー制御](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_ur10e_gripper_control.webp)

## Lula キネマティクスソルバーによるターゲット追従

Lula キネマティクスソルバーを使ってターゲットに追従する方法を学びます。

![ターゲット追従](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_ur10e_follow_target.webp)

## RMPFlow の設定

RMPFlow によるモーション制御を設定します。

## RMPFlow によるターゲット追従

RMPFlow を使ったターゲット追従の例です。

![RMPFlow ターゲット追従](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_ur10e_follow_target_rmp.webp)

## 基本的なピック＆プレースタスク

RMPFlow を使った基本的なピック＆プレースタスクを実装します。

![ピック＆プレース](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_ur10e_pick_place_rmp.webp)

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. **グリッパー制御**の基本
2. **Lula キネマティクスソルバー**によるターゲット追従
3. **RMPFlow** によるモーション制御
4. **ピック＆プレースタスク**の実装

## 次のステップ

次のチュートリアル「[閉ループ構造のリギング](10_closed_loop_structures.md)」に進み、高度なロボットリギング技法を学びましょう。
