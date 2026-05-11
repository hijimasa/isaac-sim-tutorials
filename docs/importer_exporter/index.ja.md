---
title: インポート・エクスポートチュートリアル
---

# インポート・エクスポートチュートリアル

## 概要

このチュートリアルシリーズでは、Isaac Sim でのアセットのインポートとエクスポートの方法を学びます。URDF（ROS 標準のロボット記述形式）や MJCF（MuJoCo の物理シミュレーション形式）のインポート、USD から URDF への変換、さらに外部3Dモデルデータベースからのインポートまでを段階的に解説します。

これらのスキルは、既存のロボットモデルを Isaac Sim のシミュレーション環境に統合したり、Isaac Sim で作成したモデルを他のツールで使用する際に不可欠です。

![URDF インポート](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_full_tut_viewport_import_urdf_franka.png)

## チュートリアル

!!! example "[チュートリアル 1: URDF インポート](01_import_urdf.md)"
    URDF ファイルを Isaac Sim にインポートする方法を学びます。GUI からの直接インポートと Python スクリプトによるプログラム的インポートを、インポート設定（ベース固定、自己衝突、Natural Frequency など）の意味とともに解説します。

!!! example "[チュートリアル 1a: ROS 2 ノードからの URDF インポート](01a_import_urdf_from_ros2.md)"
    ROS 2 がインストールされた環境で、`robot_state_publisher` が公開する `/robot_description` トピックから直接 URDF を取り込む方法を学びます。ROS 2 のインストールが前提となるため、独立したチュートリアルとして分けています。

!!! example "[チュートリアル 2: URDF エクスポート](02_export_urdf.md)"
    USD to URDF Exporter を使用して、USD 形式のロボットファイルを URDF 形式に変換する方法を学びます。コリジョンオブジェクトのマッピングやエクスポーターの制限事項についても解説します。

!!! example "[チュートリアル 3: MJCF インポート](03_import_mjcf.md)"
    MJCF（MuJoCo XML）形式のモデルファイルを Isaac Sim にインポートし、USD 形式に変換する方法を学びます。GUI と Python スクリプトの両方の方法を解説します。
