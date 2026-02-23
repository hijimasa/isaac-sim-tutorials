---
title: マニピュレータの設定
---

# マニピュレータの設定

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- アーティキュレーションのソルバー設定の調整
- 物理マテリアル（摩擦係数）の設定
- ジョイントの力制限の設定
- Physics Inspector を使ったアーティキュレーションの検査
- Gain Tuner を使ったジョイントゲインの調整

## はじめに

### 前提条件

- [チュートリアル 6: マニピュレータのセットアップ](06_setup_manipulator.md) を完了していること

### 所要時間

約 15〜20 分

### 概要

このチュートリアルでは、UR10e ロボットと Robotiq 2F-140 グリッパーの物理プロパティ、ジョイント力制限、ドライブゲインを設定して、マニピュレーションタスクの安定性と精度を向上させます。

## アーティキュレーションの調整

1. `ur/root_joint` prim を選択し、アーティキュレーションを有効にします。

2. **Solver Position Iterations Count** を増加します。

3. **Solver Velocity Iterations Count** を増加します。

4. **Sleep Threshold** を減少させます。

5. **Stabilization Threshold** を減少させます。

    ![アーティキュレーションプロパティ](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_articulation_properties.png)

## 物理マテリアルの追加

1. Physics Material（Rigid Body Material）を作成します。

2. 静摩擦係数と動摩擦係数を設定します。

3. グリッパーの指先にマテリアルを適用します。

## ジョイント力制限の設定

1. `finger_joint` prim を選択します。

2. **Max Force** の値を設定します。

## アーティキュレーションの検査

1. **Physics Inspector** を開きます。

2. アーティキュレーションをリフレッシュしてジョイントの位置をテストします。

    ![Physics Inspector](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_physics_inspector.png)

## Gain Tuner によるゲイン調整

1. **Gain Tuner** ツールにアクセスします。

2. ロボットアーティキュレーションを選択してジョイントゲインを調整します。

    ![Gain Tuner](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_gain_tuner_ur10e.png)

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. **アーティキュレーション**のソルバー設定調整
2. **物理マテリアル**（摩擦係数）の設定
3. **ジョイント力制限**の設定
4. **Physics Inspector** によるアーティキュレーション検査
5. **Gain Tuner** によるジョイントゲイン調整

## 次のステップ

次のチュートリアル「[ロボット設定ファイルの生成](08_generate_robot_config.md)」に進み、キネマティクスソルバー用の設定ファイルを生成する方法を学びましょう。
