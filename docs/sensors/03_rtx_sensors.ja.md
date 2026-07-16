---
title: RTX センサー
---

# RTX センサー

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- RTX センサーが Omniverse RTX レンダラーの **RTX Sensor SDK** を使って環境を検知する仕組み
- `isaacsim.sensors.rtx` 拡張機能に含まれる RTX センサーの種類
- **Motion BVH** の役割と、有効化が必要になる条件・方法

## はじめに

### 前提条件

- Isaac Sim 5.1 が起動できること
- RTX レンダラーが動作する GPU 環境であること

### 所要時間

約 5〜10 分

### 概要

Isaac Sim の **RTX センサー**は、Omniverse RTX レンダラーの **RTX Sensor SDK** を使って環境を検知します。可視・非可視スペクトルの両方でマテリアルと相互作用できるのが特徴です。

- **RTX ベースの LiDAR** は、透明・反射面での光の相互作用による戻り値をモデル化できます。
- **RTX ベースの Radar** は、電波スペクトルでのマテリアルの放射率・反射率を考慮した戻り値をモデル化できます。

RTX センサーを支えるユーティリティは `isaacsim.sensors.rtx` 拡張機能にまとめられており、次のセンサーが含まれます。

| センサー | 説明 |
|---|---|
| [RTX LiDAR センサー](04_rtx_lidar.md) | 光の相互作用を物理ベースでモデル化する LiDAR |
| [RTX Radar センサー](05_rtx_radar.md) | 電波スペクトルで動作する Radar |
| [RTX センサーアノテーター](06_rtx_annotators.md) | RTX センサーの出力データを取得するアノテーター |
| [RTX センサー用の非可視マテリアル](07_rtx_materials.md) | 非可視スペクトルでのマテリアル応答を定義する |

RTX センサーは `omni.sensors` 拡張機能スイート上に構築されています。モデル化の仕組みや自作方法については、Omniverse の Common / Lidar / Radar / Materials 各拡張機能のドキュメントも参照してください。

## Motion BVH

RTX センサーは、動きに関連するセンサー効果（センサー露光中のオブジェクトの動きや、データ収集中のセンサー自身の動きなど）を正確にモデル化するために **Motion BVH** を使用します。

パフォーマンス上の理由から、Isaac Sim では Motion BVH は**デフォルトで無効**になっています。次の RTX センサー機能が Motion BVH の影響を受けます。

- **RTX LiDAR** … LiDAR のモーション補正を正しく動作させるには、Motion BVH を有効にする必要があります。
- **RTX Radar** … ドップラー効果（したがって RTX Radar 全体）を正しくモデル化するには、Motion BVH を有効にする必要があります。

!!! warning "パフォーマンスへの影響"
    Motion BVH を有効にすると、すべてのセンサーで VRAM 使用量が増え、レンダリング時間が大幅に増加することがあります。**必要ないときは無効のまま**にしておいてください。

### Motion BVH を有効にする方法

Motion BVH を有効にする方法は 2 つあります。

**1. Standalone Python ワークフロー**

`SimulationApp` のコンストラクタで `enable_motion_bvh` を `True` に指定します。

```python
from isaacsim import SimulationApp

simulation_app = SimulationApp({"enable_motion_bvh": True})
```

**2. すべてのワークフロー（コマンドライン）**

起動時に次の設定を指定します。

```bash
--/renderer/raytracingMotion/enabled=true \
--/renderer/raytracingMotion/enableHydraEngineMasking=true \
--/renderer/raytracingMotion/enabledForHydraEngines='0,1,2,3,4'
```

## まとめ

このチュートリアルでは、次の内容を学びました。

- RTX センサーは RTX Sensor SDK を使い、可視・非可視スペクトルでマテリアルと相互作用すること
- `isaacsim.sensors.rtx` に LiDAR / Radar / アノテーター / 非可視マテリアルが含まれること
- Motion BVH がモーション関連の効果（LiDAR のモーション補正、Radar のドップラー効果）に必要であり、パフォーマンスとのトレードオフで既定では無効なこと

## 次のステップ

- [RTX LiDAR センサー](04_rtx_lidar.md) で、具体的な LiDAR の設定とデータ取得を学びます。
