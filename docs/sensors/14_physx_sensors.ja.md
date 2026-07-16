---
title: PhysX SDK センサー
---

# PhysX SDK センサー

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- PhysX SDK センサーが PhysX SDK のレイキャストを使って距離を測定する仕組み
- `isaacsim.sensors.physx` 拡張機能が提供するセンサーの種類
- Physics ベースのセンサーや RTX センサーとの違い

## はじめに

### 前提条件

- Isaac Sim 5.1 が起動できること
- コライダー（Collision）と剛体の基礎を理解していること

### 所要時間

約 5 分

### 概要

Isaac Sim の **PhysX SDK センサー**は、PhysX SDK が提供する**レイキャスト**を使い、シミュレーション内のオブジェクト間の距離を測定します。これらのセンサーは PhysX SDK からの**正確な測定値**を出力します。デフォルトでは、センサーが出力できる最大レートは**レンダーレート**です。

PhysX SDK センサーは `isaacsim.sensors.physx` 拡張機能にまとめられており、次のセンサーをサポートします。

| センサー | 説明 |
|---|---|
| [PhysX SDK Generic センサー](15_physx_generic.md) | カスタムのレイパターンで ground truth 深度を測定する |
| [PhysX SDK Lidar](16_physx_lidar.md) | レイキャストで LiDAR を模擬する |
| [PhysX SDK Lightbeam センサー](17_physx_lightbeam.md) | ライトカーテン状の光線遮断を検出する |

!!! note "3 種類のセンサー系統の違い"
    - **RTX センサー** … RTX レンダラーで物理ベースにレンダリングし、非可視マテリアル（透明・反射など）と相互作用します。
    - **Physics ベースのセンサー**（`isaacsim.sensors.physics`）… CPU 物理から質量・速度などのプロパティを読み取ります（Contact / IMU など）。
    - **PhysX SDK センサー**（`isaacsim.sensors.physx`）… PhysX のレイキャストで距離を測定します。非可視マテリアルとは相互作用せず、常に ground truth を返します。

## まとめ

PhysX SDK センサーは、PhysX のレイキャストに基づく ground truth の距離センサーです。次の各ページで、Generic / Lidar / Lightbeam それぞれの使い方を学びます。

## 次のステップ

- [PhysX SDK Generic センサー](15_physx_generic.md) から順に学びます。
