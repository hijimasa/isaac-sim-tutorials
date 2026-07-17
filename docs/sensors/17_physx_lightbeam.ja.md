---
title: PhysX SDK Lightbeam センサー
---

# PhysX SDK Lightbeam センサー

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- Lightbeam センサーが光線の遮断を検出する仕組み
- 複数の光線でライトカーテンを構成する考え方
- サンプルの実行方法と読み取れるデータ

## はじめに

### 前提条件

- [PhysX SDK センサー](14_physx_sensors.md) の概要を理解していること
- コライダー（Collision）の基礎を理解していること

### 所要時間

約 10 分

### 概要

PhysX SDK Lightbeam センサーは、PhysX SDK のレイキャストを使って、オブジェクトが**光線（light beam）を遮ったか**どうかを判定します。光線の本数と高さを指定することで、安全用途のライトカーテン（light "curtain"）状の Lightbeam センサー群を構成できます。

!!! warning "Isaac Sim 6.0 での非推奨化"
    PhysX SDK Lightbeam センサー（`isaacsim.sensors.physx`）は Isaac Sim 6.0 で非推奨（deprecated）となりました。
    後継は **Physics Raycast センサー**（`isaacsim.sensors.experimental.physics.RaycastSensor`）で、
    ビームカーテンとして構成すると同じ機能を実現できます。移行の詳細は後述の
    「Physics Raycast センサーへの移行」を参照してください。

## ステップ：サンプルを実行する

1. **Windows > Examples > Robotics Examples** で Robotics Examples タブを有効にします。
2. **Robotics Examples > Sensors > Lightbeam** をクリックします。
3. 各光線ごとに空のデータが表示されるウィンドウを確認します。Play を押すとデータが埋まります。各ビームについて、**ヒットしたかどうか**・**ヒットの線形深度**・**xyz の正確なヒット位置**が表示されます。
4. **PLAY** で開始します。
5. **SHIFT + 左クリック**で立方体やセンサーをドラッグすると、読み値が変化します。

![Lightbeam センサーの例](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_4.5_full_tut_viewport_lightbeam_sensor.gif)

!!! tip "安全ライトカーテンとしての利用"
    複数の光線を縦に並べてライトカーテンを作ると、その面を横切る物体を検出できます。工場の安全柵のように、危険領域への侵入検知をシミュレートするのに適しています。

## Physics Raycast センサーへの移行

PhysX SDK Lightbeam センサーは非推奨です。同じ機能を実現するには、**Physics Raycast センサー**（`isaacsim.sensors.experimental.physics.RaycastSensor`）をビームカーテンとして構成します。

### 概念の対応関係

| PhysX SDK Lightbeam センサー | Physics Raycast センサー |
|---|---|
| `numRays` | `rayOrigins` / `rayDirections` 配列の長さ。ビームごとに 1 エントリ作成する |
| `curtainLength` / `curtainAxis` | `rayOrigins`。カーテン軸に沿ってレイの原点を分散させる。たとえば高さ `h`、ビーム数 `N` の垂直カーテンでは `origins[i] = [0, 0, -h/2 + h * i / (N-1)]` |
| `forwardAxis` | `rayDirections`。すべての方向ベクトルを前方軸に設定する。たとえば X 軸方向に発射するカーテンでは `[1, 0, 0]` |
| `minRange` / `maxRange` | `minRange` / `maxRange`。意味は同じ |
| ビームごとのヒット・深度・位置データ | `RaycastSensor.get_sensor_reading()` がレイごとの深度・ヒット位置・ヒット法線を返す |

### 対話型サンプル

Physics Raycast センサーのサンプルには、平行な垂直レイによるビームカーテン構成が含まれます。

- **GUI**: **Robotics Examples > Sensors > Physics Raycast Sensor** を開き、**Load Scene** をクリックします。
- **ソースコード**: `source/extensions/isaacsim.sensors.physics.examples/isaacsim/sensors/physics/examples/raycast_sensor.py`

Python API の使い方や OmniGraph ワークフローを含む詳細は、[Physics Raycast センサーの公式ドキュメント](https://docs.isaacsim.omniverse.nvidia.com/latest/sensors/isaacsim_sensors_physics_raycast.html)と[公式移行ガイド](https://docs.isaacsim.omniverse.nvidia.com/latest/migration_guides/isaac_sim_6_0/sensors_physx_lightbeam_to_physics_raycast.html)を参照してください。

## まとめ

このチュートリアルでは、次の内容を学びました。

- Lightbeam センサーが PhysX レイキャストで光線の遮断を検出すること
- 光線の本数と高さを指定してライトカーテンを構成できること
- サンプルで各ビームのヒット有無・深度・ヒット位置を確認できること
- Isaac Sim 6.0 での後継が Physics Raycast センサー（ビームカーテン構成）であること

## 次のステップ

- センサーセクションの一覧は [センサーチュートリアル](index.md) に戻って確認できます。
- 実機ロボットへのセンサー統合は [ROS 2 チュートリアル](../ros/index.md) も参考になります。
