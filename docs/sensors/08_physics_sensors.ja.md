---
title: Physics ベースのセンサー
---

# Physics ベースのセンサー

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- Physics ベースのセンサーが RTX センサーと何が違うのか
- `isaacsim.sensors.physics` 拡張機能が提供するセンサーの種類
- 出力レートやノイズに関する基本的な考え方

## はじめに

### 前提条件

- Isaac Sim 5.1 が起動できること
- 剛体（Rigid Body）や Articulation といった物理シミュレーションの基礎を理解していること

### 所要時間

約 5 分

### 概要

Isaac Sim の **Physics ベースのセンサー**は、CPU の物理シミュレーションに基づき、レンダリングが完了した後に実行されます。prim の物理プロパティ（質量や速度など）にアクセスでき、物理エンジンから**正確な測定値**を出力します。センサーの読み値は後処理で加工できます。

!!! note "出力レートとノイズ"
    - デフォルトでは、センサーが出力できる最大レートは**物理レート**です。それを超えるレートでデータを生成するには、補間オプションを指定する必要があります。
    - シミュレータからの ground truth の読み値にはすでに多少のノイズが含まれていることがあります。よりリアルにするために、後処理でさらにノイズを加えることもできます。

Physics ベースのセンサーは `isaacsim.sensors.physics` 拡張機能にまとめられています。Isaac Sim は次の ground truth センサーをサポートします。

| センサー | 説明 |
|---|---|
| [Articulation Joint センサー](09_articulation_force.md) | 関節にかかる力・トルクを読み取る |
| [Contact センサー](10_contact_sensor.md) | 接触力を検出する（接触セル/圧力センサー相当） |
| [Effort センサー](11_effort_sensor.md) | 個々の関節に加わるトルク・力を追跡する |
| [IMU センサー](12_imu_sensor.md) | 加速度・角速度を出力する |
| [Proximity センサー](13_proximity_sensor.md) | 近接（衝突）を検出する |

!!! note "Proximity センサーの拡張機能"
    Proximity センサーは他の Physics ベースのセンサーとは異なり、`isaacsim.sensors.physx` 拡張機能で提供されます。

## まとめ

Physics ベースのセンサーは、CPU 物理シミュレーションに基づく ground truth センサーであり、正確な物理量を出力します。次の各ページで、それぞれのセンサーの作成方法とデータ取得方法を学びます。

## 次のステップ

- [Articulation Joint センサー](09_articulation_force.md) から順に、各センサーの使い方を学びます。
