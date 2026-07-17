---
title: RTX センサー
---

# RTX センサー

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- RTX センサーが Omniverse RTX レンダラーの **RTX Sensor SDK** を使って環境を検知する仕組み
- `isaacsim.sensors.experimental.rtx` 拡張機能に含まれる RTX センサーの種類
- RTX センサーの動作に影響する**重要な設定**（キャリブレーション用フラグ）
- **Motion BVH** の役割と、有効化が必要になる条件・方法
- **GenericModelOutput（GMO）** の補助出力レベル（`aux_output_level`）の仕組み

## はじめに

### 前提条件

- Isaac Sim 6.0 が起動できること
- RTX レンダラーが動作する GPU 環境であること

### 所要時間

約 10〜15 分

### 概要

Isaac Sim の **RTX センサー**は、Omniverse RTX レンダラーの **RTX Sensor SDK** を使って環境を検知します。可視・非可視スペクトルの両方でマテリアルと相互作用できるのが特徴です。

- **RTX ベースの LiDAR** は、透明・反射面での光の相互作用による戻り値をモデル化できます。
- **RTX ベースの Radar** は、電波スペクトルでのマテリアルの放射率・反射率を考慮した戻り値をモデル化できます。

RTX センサーを支えるユーティリティは `isaacsim.sensors.experimental.rtx` 拡張機能にまとめられています。

!!! warning "`isaacsim.sensors.rtx` は 6.0 で非推奨"
    Isaac Sim 6.0 では、従来の `isaacsim.sensors.rtx` 拡張機能は **非推奨（deprecated）** となり、`isaacsim.sensors.experimental.rtx` に置き換えられました。新しい拡張機能は、prim を作成する**オーサリングクラス**（`Lidar` / `Radar` / `Acoustic`）と、アノテーターを取り付けてデータを読み出す**ランタイムクラス**（`LidarSensor` / `RadarSensor` / `AcousticSensor`）に分かれています。OmniGraph ノード・アノテーター・デバッグ描画は、引き続き有効な `isaacsim.sensors.rtx.nodes` 拡張機能が提供します。詳細は公式の [RTX Sensors 移行ガイド](https://docs.isaacsim.omniverse.nvidia.com/latest/migration_guides/isaac_sim_6_0/sensors_rtx_to_experimental_rtx.html) を参照してください。

RTX センサーを使い始める基本的な流れは次のとおりです。

1. **センサーをシーンに追加** … メニューの **Create > Isaac > Sensors** から RTX Lidar / RTX Radar を作成するか、各センサーページで説明する Python API を使います。
2. **データを収集** … センサーにアノテーターをアタッチして、点群データ・スキャンバッファ・生の GenericModelOutput データを取り出します。
3. **出力を可視化** … Debug Draw 拡張機能で点群を可視化するか、ビューポートのデバッグビューを設定します。
4. **ROS 2 と連携** … RTX LiDAR の ROS 2 チュートリアルに従って、センサーデータを PointCloud2 / LaserScan メッセージとして配信します。

このセクションで扱うセンサーとトピックは次のとおりです。

| センサー / トピック | 説明 |
|---|---|
| [RTX LiDAR センサー](04_rtx_lidar.md) | 光の相互作用を物理ベースでモデル化する LiDAR |
| [RTX Radar センサー](05_rtx_radar.md) | 電波スペクトルで動作する Radar |
| [RTX センサーアノテーター](06_rtx_annotators.md) | RTX センサーの出力データを取得するアノテーター |
| [RTX センサー用の非可視マテリアル](07_rtx_materials.md) | 非可視スペクトルでのマテリアル応答を定義する |

!!! note "6.0 で追加されたセンサー・トピック（本サイト補足）"
    Isaac Sim 6.0 では、超音波センサーをモデル化する **RTX Acoustic センサー**（旧 Ultrasonic プラグインの後継。[公式ページ](https://docs.isaacsim.omniverse.nvidia.com/latest/sensors/isaacsim_sensors_rtx_acoustic.html)）、カメラ・RTX センサーを物理時間で駆動する **Multi-Tick Rendering**（[公式ページ](https://docs.isaacsim.omniverse.nvidia.com/latest/sensors/isaacsim_sensors_multitick_rendering.html)）、**カスタム RTX センサープロファイルの作成**（[公式ページ](https://docs.isaacsim.omniverse.nvidia.com/latest/sensors/isaacsim_sensors_rtx_custom.html)）が追加されています。

RTX センサーは `omni.sensors` 拡張機能スイート上に構築されています。モデル化の仕組みや自作方法については、Omniverse の Common / Lidar / Radar / Acoustic / Materials 各拡張機能のドキュメントも参照してください。

## 重要な設定

次の設定は、RTX センサーの動作とパフォーマンスに影響します。

| 設定 | デフォルト | 説明 |
|---|---|---|
| `--/app/sensors/nv/lidar/outputBufferOnGPU` | `false` | LiDAR の戻り値バッファを GPU 上に保持して後処理する。アノテーターを正しく動作させるには `false` のままにする必要がある |
| `--/app/sensors/nv/radar/outputBufferOnGPU` | `false` | Radar の戻り値バッファを GPU 上に保持して後処理する。アノテーターを正しく動作させるには `false` のままにする必要がある |
| `--/app/sensors/nv/lidar/publishNormals` | `false` | ヒット法線の出力を有効化する。VRAM 使用量が増える |
| `--/rtx/materialDb/nonVisualMaterialCSV/enabled` | `false` | USD 属性による非可視マテリアルを有効化する |
| `--/rtx/materialDb/nonVisualMaterialSemantics/prefix` | `omni:simready:nonvisual` | 非可視マテリアルの USD 属性プレフィックスを指定する |
| `--/rtx/rtxsensor/useHydraTimeAlways` | `true` | RTX センサーモデルで Hydra 時間（`omni.timeline`）を使う。マルチティックレンダリング無効時のみ適用 |
| `--/rtx-transient/stableIds/enabled` | `false` | セマンティックセグメンテーション用の安定 128 ビットオブジェクト ID を有効化する |
| `--/renderer/raytracingMotion/enabled` | `false` | モーション補正・ドップラー効果用の Motion BVH を有効化する |

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

## 補助出力レベルと GenericModelOutput RenderVar

RTX の LiDAR / Radar / Acoustic センサーは、**GenericModelOutput（GMO）** という AOV を出力します。各 GMO フレームに含まれる補助データの量は、センサー prim の `_replicator:rendervar:GenericModelOutput:channels` 属性で制御します。

!!! note "GMO とは"
    **GenericModelOutput（GMO）** は、RTX センサーが出力する共通のデータ構造です。ヒット位置・距離・強度などの基本データに加え、補助出力レベルに応じて速度・法線などの追加フィールドが含まれます。詳細は [RTX センサーアノテーター](06_rtx_annotators.md) を参照してください。

`isaacsim.sensors.experimental.rtx` の `Lidar` / `Radar` / `Acoustic` クラスのコンストラクタパラメータ **`aux_output_level`** は、この属性をセンサー prim に書き込む便利機能です（`Lidar(..., aux_output_level="FULL")` など）。UI から設定する場合は、Stage ウィンドウで prim を選択し、**Property** タブの **Array Properties** ウィジェットで `_replicator:rendervar:GenericModelOutput:channels` の行を **Edit** して値（`BASIC` など）を設定します。

有効な値はセンサーの種類ごとに異なります。

| センサー | 有効な値 |
|---|---|
| Lidar | `NONE`（デフォルト）、`BASIC`、`EXTRA`、`FULL` |
| Radar | `NONE`（デフォルト）、`BASIC` |
| Acoustic | `NONE`（デフォルト）、`BASIC` |

!!! note "旧属性からの移行"
    以前のリリースでは、同じ目的でセンサー種別ごとの USD 属性（LiDAR の `omni:sensor:Core:auxOutputType`、Radar の `omni:sensor:WpmDmat:auxOutputType`）を使っていましたが、これらはスキーマから**削除**されました。Isaac Sim 6.0 に同梱される USD アセットは更新済みです。旧属性を含むカスタム USD シーンは移行が必要で、旧属性は新しいスキーマでは黙って無視されます。

!!! warning "既知の問題：GMO channels は「最後にアタッチした側」が勝つ"
    `_replicator:rendervar:GenericModelOutput:channels` 属性は、現状レンダープロダクトのアタッチイベントごとに実質グローバルに扱われます。同じステージ上の 2 つの RTX センサーが異なる値を設定した場合、**最後にレンダープロダクトがアタッチされたセンサーの値**がすべての GMO RenderVar に適用されます。回避策として、(1) ステージ上のすべての RTX センサーを同じ `aux_output_level` に揃える、(2) 使いたい値を持つセンサーを最後にアタッチする、(3) 要件が競合するセンサーをステージや `SimulationApp` インスタンスで分離する、のいずれかを推奨します。この問題は将来のリリースで修正予定です。なお、Camera prim は GMO AOV を出力しないため影響を受けません。

## トラブルシューティング

- **アノテーターの出力が空になる** … シミュレーションのタイムラインが再生中であることを確認してください（RTX センサーアノテーターはタイムラインに依存します）。また、`outputBufferOnGPU` 系の設定がデフォルトの `false` のままであることを確認してください。
- **蓄積スキャンに複数フレームの戻り値が混ざる** … LiDAR の回転レートがフレームレートより遅い場合に起こる想定内の動作です。フレームごとの出力の利用を検討してください。蓄積出力を使う場合は `omni:sensor:Core:accumulateOutputs` が `true` で、`omni:sensor:tickRate` が `omni:sensor:Core:scanRateBaseHz` と等しいことを確認してください。
- **ドップラー効果が出ない** … Motion BVH を有効にしてください。
- **パフォーマンス** … RTX センサーは NVIDIA RTX GPU（レイトレーシング対応）が必要です。センサー数・解像度は VRAM 容量に、シミュレーション速度はレイトレーシングコア数に依存します。

## まとめ

このチュートリアルでは、次の内容を学びました。

- RTX センサーは RTX Sensor SDK を使い、可視・非可視スペクトルでマテリアルと相互作用すること
- 6.0 では API が `isaacsim.sensors.experimental.rtx`（オーサリング＋ランタイムクラス）に再編され、LiDAR / Radar / Acoustic / アノテーター / 非可視マテリアルが含まれること
- アノテーターを使うには `outputBufferOnGPU` を `false` のままにするなど、重要な設定があること
- Motion BVH がモーション関連の効果（LiDAR のモーション補正、Radar のドップラー効果）に必要であり、パフォーマンスとのトレードオフで既定では無効なこと
- GMO の補助出力レベルは `aux_output_level`（`_replicator:rendervar:GenericModelOutput:channels` 属性）で制御すること

## 次のステップ

- [RTX LiDAR センサー](04_rtx_lidar.md) で、具体的な LiDAR の設定とデータ取得を学びます。
