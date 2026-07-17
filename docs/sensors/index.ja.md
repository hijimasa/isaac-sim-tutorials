---
title: センサーチュートリアル
---

# センサーチュートリアル

<span class="badge badge-beginner">Beginner</span>

Isaac Sim の RTX センサー・Physics ベースのセンサー・PhysX SDK センサーの使い方チュートリアルです。

## 概要

Isaac Sim のセンサーは、大きく次の 3 系統に分かれます。

- **カメラ／深度センサー** … USD の Camera prim をベースに、画像・深度・キャリブレーションを扱います。
- **RTX センサー** … RTX レンダラーで物理ベースにレンダリングし、非可視マテリアル（透明・反射など）と相互作用します（LiDAR / Radar / Acoustic）。
- **Physics ベース／PhysX SDK センサー** … CPU 物理やレイキャストで、接触・IMU・距離などの ground truth を取得します。

!!! note "Isaac Sim 6.0 での API 再編"
    Isaac Sim 6.0 では、センサー系拡張機能が大きく再編されました。`isaacsim.sensors.camera` / `isaacsim.sensors.rtx` は `isaacsim.sensors.experimental.rtx` に、`isaacsim.sensors.physics` は `isaacsim.sensors.experimental.physics` に置き換えられています（旧拡張機能は非推奨）。各チュートリアルは新 API に対応済みです。

## チュートリアル

### カメラ・深度

- [カメラセンサー](01_camera_sensors.md) — カメラの作成、画像取得、OpenCV 歪みモデル、カメラリグ
- [深度センサー](02_depth_sensors.md) — ステレオ深度、視差マップ、深度アノテーター

### RTX センサー

- [RTX センサー](03_rtx_sensors.md) — RTX Sensor SDK、Motion BVH、重要設定、GMO 補助出力の概要
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

### PhysX SDK センサー

- [PhysX SDK センサー](14_physx_sensors.md) — 概要
- [Proximity センサー](13_proximity_sensor.md) — 近接検出
- [PhysX SDK Generic センサー](15_physx_generic.md) — カスタムレイパターン
- [PhysX SDK Lidar](16_physx_lidar.md) — レイキャストによる LiDAR 模擬
- [PhysX SDK Lightbeam センサー](17_physx_lightbeam.md) — ライトカーテン

!!! note "6.0 で追加された公式トピック（本サイト補足）"
    Isaac Sim 6.0 の公式ドキュメントには、このほか [構造化光カメラ](https://docs.isaacsim.omniverse.nvidia.com/latest/sensors/isaacsim_sensors_camera_structured_light.html)、[RTX Acoustic センサー](https://docs.isaacsim.omniverse.nvidia.com/latest/sensors/isaacsim_sensors_rtx_acoustic.html)、[マルチティックレンダリング](https://docs.isaacsim.omniverse.nvidia.com/latest/sensors/isaacsim_sensors_multitick_rendering.html)、[カスタム RTX センサープロファイル](https://docs.isaacsim.omniverse.nvidia.com/latest/sensors/isaacsim_sensors_rtx_custom.html)、[Joint State センサー](https://docs.isaacsim.omniverse.nvidia.com/latest/sensors/isaacsim_sensors_physics_joint_state.html)、[Physics Raycast センサー](https://docs.isaacsim.omniverse.nvidia.com/latest/sensors/isaacsim_sensors_physics_raycast.html) のページが追加されています。
