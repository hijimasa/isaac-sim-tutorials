---
title: マニピュレータのセットアップ
---

# マニピュレータのセットアップ

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- URDF ファイルから UR10e ロボットをインポートする方法
- URDF ファイルから Robotiq 2F-140 グリッパーをインポートする方法
- GUI 操作でロボットアームとグリッパーを接続する方法
- Robot Assembler を使った接続方法

## はじめに

### 前提条件

- [チュートリアル 5: モバイルロボットのリギング](05_rig_mobile_robot.md) を完了していること
- Linux 環境（ROS 2 URDF Importer の使用のため）

### 所要時間

約 20〜30 分

### 概要

このチュートリアルでは、UR10e ロボットアームと Robotiq 2F-140 グリッパーを URDF ファイルからインポートし、単一のアーティキュレーションとして接続します。GUI による手動接続と Robot Assembler を使った接続の2つの方法を学びます。

## UR Description パッケージのビルドとインストール

1. UR Description パッケージをクローンします。

2. Python 3.11 またはシステム ROS を使ってビルドします。

## UR10e ロボットのインポート

1. ROS 2 URDF Importer エクステンションを有効にします。

2. URDF Publisher Topic を起動します。

3. UR10e を Isaac Sim にインポートします。

    ![UR10e インポート](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_ur10_importer.png)

## Robotiq 2F-140 グリッパーのインポート

1. XACRO を URDF に変換します。

2. グリッパーを Isaac Sim にインポートします。

    ![Robotiq インポート](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_robotiq_importer.png)

## UR10e と Robotiq 2F-140 の接続

### 方法 1: GUI による手動接続

グリッパーをロボットアームのエンドエフェクタに手動で接続します。

![手動接続](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_connect_gripper_manual.png)

### 方法 2: Robot Assembler による接続

Robot Assembler ツールを使って自動的に接続します。

![Robot Assembler](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_connect_gripper_assembler.png)

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. **URDF** からのロボットアームとグリッパーのインポート
2. **GUI** を使った手動接続
3. **Robot Assembler** を使った自動接続

## 次のステップ

次のチュートリアル「[マニピュレータの設定](07_configure_manipulator.md)」に進み、物理プロパティやジョイントゲインの調整方法を学びましょう。
