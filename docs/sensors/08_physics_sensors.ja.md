---
title: Physics ベースのセンサー
---

# Physics ベースのセンサー

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- Physics ベースのセンサーが RTX センサーと何が違うのか
- `isaacsim.sensors.experimental.physics` 拡張機能が提供するセンサーの種類
- 出力レートやノイズに関する基本的な考え方

## はじめに

### 前提条件

- Isaac Sim 6.0 が起動できること
- 剛体（Rigid Body）や Articulation といった物理シミュレーションの基礎を理解していること

### 所要時間

約 5 分

### 概要

Isaac Sim の **Physics ベースのセンサー**は、CPU の物理シミュレーションに基づき、レンダリングが完了した後に実行されます。prim の物理プロパティ（質量や速度など）にアクセスでき、物理エンジンから**正確な測定値**を出力します。センサーの読み値は後処理で加工できます。

!!! note "出力レートとノイズ"
    - デフォルトでは、センサーが出力できる最大レートは**物理レート**です。それを超えるレートでデータを生成するには、補間オプションを指定する必要があります。
    - シミュレータからの ground truth の読み値にはすでに多少のノイズが含まれていることがあります。よりリアルにするために、後処理でさらにノイズを加えることもできます。

Physics ベースのセンサーは `isaacsim.sensors.experimental.physics` 拡張機能にまとめられています。

!!! warning "`isaacsim.sensors.physics` は 6.0 で非推奨"
    Isaac Sim 6.0 では、従来の `isaacsim.sensors.physics` 拡張機能は **非推奨（deprecated）** となり、`isaacsim.sensors.experimental.physics` に置き換えられました。新しい拡張機能は同等のセンサークラス（`ContactSensor`、`IMUSensor`、`EffortSensor` など）を同じコア機能で提供します。移行手順の詳細は公式の [Physics Sensors 移行ガイド](https://docs.isaacsim.omniverse.nvidia.com/latest/migration_guides/isaac_sim_6_0/sensors_physics_to_experimental_physics.html) を参照してください。なお、例・OmniGraph ノード・UI は `isaacsim.sensors.physics.examples` / `.nodes` / `.ui` 拡張機能が引き続き提供します。

Isaac Sim は次の ground truth センサーをサポートします。

| センサー | 説明 |
|---|---|
| [Articulation Joint センサー](09_articulation_force.md) | 関節にかかる力・トルクを読み取る |
| [Contact センサー](10_contact_sensor.md) | 接触力を検出する（接触セル/圧力センサー相当） |
| [Effort センサー](11_effort_sensor.md) | 個々の関節に加わるトルク・力を追跡する |
| [IMU センサー](12_imu_sensor.md) | 加速度・角速度を出力する |
| Joint State センサー | 関節の位置・速度・エフォートをまとめて読み取る（6.0 で追加。[公式ページ](https://docs.isaacsim.omniverse.nvidia.com/latest/sensors/isaacsim_sensors_physics_joint_state.html)） |
| Physics Raycast センサー | レイキャストによる距離計測（6.0 で追加。PhysX Lidar / Generic / Lightbeam の後継。[公式ページ](https://docs.isaacsim.omniverse.nvidia.com/latest/sensors/isaacsim_sensors_physics_raycast.html)） |

!!! note "Proximity センサーの位置づけ"
    [Proximity センサー](13_proximity_sensor.md) は `isaacsim.sensors.physx` 拡張機能で提供され、Isaac Sim 6.0 の公式ドキュメントでは **PhysX SDK センサー**のカテゴリに分類されています。

## まとめ

Physics ベースのセンサーは、CPU 物理シミュレーションに基づく ground truth センサーであり、正確な物理量を出力します。6.0 では API が `isaacsim.sensors.experimental.physics` に移行し、Joint State センサーと Physics Raycast センサーが追加されました。次の各ページで、それぞれのセンサーの作成方法とデータ取得方法を学びます。

## 次のステップ

- [Articulation Joint センサー](09_articulation_force.md) から順に、各センサーの使い方を学びます。
