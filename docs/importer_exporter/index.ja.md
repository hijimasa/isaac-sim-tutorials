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
    URDF ファイルを Isaac Sim にインポートする方法を学びます。GUI での直接インポート、Python スクリプトによるプログラム的インポート、ROS 2 ノードからのインポートの3つの方法を解説します。

!!! example "[チュートリアル 2: URDF エクスポート](02_export_urdf.md)"
    USD to URDF Exporter を使用して、USD 形式のロボットファイルを URDF 形式に変換する方法を学びます。コリジョンオブジェクトのマッピングやエクスポーターの制限事項についても解説します。

!!! example "[チュートリアル 3: MJCF インポート](03_import_mjcf.md)"
    MJCF（MuJoCo XML）形式のモデルファイルを Isaac Sim にインポートし、USD 形式に変換する方法を学びます。GUI と Python スクリプトの両方の方法を解説します。

!!! example "[チュートリアル 4: ShapeNet インポーター](04_shapenet_importer.md)"
    ShapeNet データベースからの3Dモデルインポートについて紹介します。専用エクステンションは非推奨のため、標準 OBJ インポート手順を使用します。
