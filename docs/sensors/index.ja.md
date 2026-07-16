---
title: センサーチュートリアル
---

# センサーチュートリアル

<span class="badge badge-beginner">Beginner</span>

Isaac Sim の RTX センサー・Physics ベースのセンサー・PhysX SDK センサーの使い方チュートリアルです。

## 概要

Isaac Sim のセンサーは、大きく次の 3 系統に分かれます。

- **カメラ／深度センサー** … USD の Camera prim をベースに、画像・深度・キャリブレーションを扱います。
- **RTX センサー** … RTX レンダラーで物理ベースにレンダリングし、非可視マテリアル（透明・反射など）と相互作用します（LiDAR / Radar）。
- **Physics ベース／PhysX SDK センサー** … CPU 物理やレイキャストで、接触・IMU・距離などの ground truth を取得します。

## チュートリアル

### カメラ・深度

- [カメラセンサー](01_camera_sensors.md) — カメラの作成、画像取得、OpenCV 歪みモデル、カメラリグ
- [深度センサー](02_depth_sensors.md) — ステレオ深度、視差マップ、深度アノテーター

### RTX センサー

- [RTX センサー](03_rtx_sensors.md) — RTX Sensor SDK と Motion BVH の概要
- [RTX LiDAR センサー](04_rtx_lidar.md) — OmniLidar の作成、データ収集、アセットライブラリ
- [RTX Radar センサー](05_rtx_radar.md) — OmniRadar の作成、ドップラー効果
- [RTX センサーアノテーター](06_rtx_annotators.md) — 点群データの収集、GenericModelOutput、Object ID
- [RTX センサー用の非可視マテリアル](07_rtx_materials.md) — 非可視マテリアル属性、マテリアル ID

### Physics ベースのセンサー

- [Physics ベースのセンサー](08_physics_sensors.md) — 概要
- [Articulation Joint センサー](09_articulation_force.md) — 関節力・トルクの読み取り
- [Contact センサー](10_contact_sensor.md) — 接触力の検出
- [Effort センサー](11_effort_sensor.md) — 関節エフォートの追跡
- [IMU センサー](12_imu_sensor.md) — 加速度・角速度の取得
- [Proximity センサー](13_proximity_sensor.md) — 近接検出

### PhysX SDK センサー

- [PhysX SDK センサー](14_physx_sensors.md) — 概要
- [PhysX SDK Generic センサー](15_physx_generic.md) — カスタムレイパターン
- [PhysX SDK Lidar](16_physx_lidar.md) — レイキャストによる LiDAR 模擬
- [PhysX SDK Lightbeam センサー](17_physx_lightbeam.md) — ライトカーテン
