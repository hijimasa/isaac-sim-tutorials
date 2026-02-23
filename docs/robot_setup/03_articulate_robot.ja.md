---
title: 基本ロボットのアーティキュレーション
---

# 基本ロボットのアーティキュレーション

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- リボリュートジョイントの追加と回転軸の設定
- ジョイントドライブ（角速度制御）の設定
- アーティキュレーションルートの追加
- ActionGraph を使った速度コントローラの実装

## はじめに

### 前提条件

- [チュートリアル 2: シンプルなロボットの組み立て](02_assemble_robot.md) を完了していること

### 所要時間

約 15〜20 分

### 概要

このチュートリアルでは、前回組み立てたロボットのボディと車輪をジョイントで接続し、アーティキュレーションを設定して動くロボットに仕上げます。速度コントローラを追加してシミュレーション中にロボットを制御する方法も学びます。

## ジョイントの追加

1. ジョイントを整理するための Scope を作成します。

2. ボディと車輪のオブジェクトを選択し、リボリュートジョイントを追加します。

3. 回転軸を設定し、ジョイントを Scope 内に整理します。

    ![ジョイント設定](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_base_ref_gui_rigging_mockrobot_joints.png)

## ジョイントドライブの追加

1. 角速度制御用のドライブプロパティを適用します。

2. ダンピングとターゲット速度のパラメータを設定します。

    ![ジョイントドライブ](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_base_ref_gui_rigging_mockrobot_joint_drives.webp)

## アーティキュレーションの追加

1. mock_robot にアーティキュレーションルートを設定します。

2. シミュレーションの性能と物理的正確性が向上することを確認します。

    ![インタラクション](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_base_ref_gui_rigging_mockrobot_interaction.webp)

## コントローラの追加

1. ActionGraph スコープを作成します。

2. Joint Velocity コントローラを実装して、シミュレーション中にロボットの動きを制御します。

    ![コントローラ](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_base_ref_gui_rigging_mockrobot_controller.png)

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. **リボリュートジョイント**の追加と回転軸設定
2. **ジョイントドライブ**（角速度制御）の設定
3. **アーティキュレーションルート**の追加
4. **ActionGraph** を使った速度コントローラの実装

## 次のステップ

次のチュートリアル「[カメラとセンサーの追加](04_camera_sensors.md)」に進み、ロボットにカメラセンサーを取り付ける方法を学びましょう。
