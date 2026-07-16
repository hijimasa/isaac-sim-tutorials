---
title: 深度センサー
---

# 深度センサー

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- Isaac Sim が **単一ビュー**からステレオ深度カメラをモデル化する仕組み（`SingleViewDepthSensor`）
- ビューポートで視差マップ（Disparity Map）を確認する方法
- 深度用アノテーター（`DepthSensorDistance` / `DistanceToImagePlane`）で深度画像を出力する方法
- 公式の深度センサーアセットを `SingleViewDepthSensorAsset` で読み込む方法
- 既存アセットを深度センサー対応に更新し、USD として書き出す方法
- 新しいステレオ深度センサーモデルを構築する一般的な流れ

## はじめに

### 前提条件

- [カメラセンサー](01_camera_sensors.ja.md) の内容（`Camera` クラス、レンダープロダクト、レンズ歪みモデル）を理解していること
- Isaac Sim 5.1 が起動できること

### 所要時間

約 15〜20 分

### 概要

Isaac Sim の深度センサーは、**ステレオ深度カメラ**を単一のカメラビューでモデル化します。中心となるのが `isaacsim.sensors.camera.SingleViewDepthSensor` クラスです。このクラスは `Camera` クラスをラップし、**単一の Camera prim からステレオ深度を推定する後処理パイプライン**を設定する API を提供します。

!!! note "対象はステレオ深度カメラ"
    このパイプラインは、あくまで**ステレオ深度カメラ**を近似的にモデル化するためのものです。ToF（Time-of-Flight）センサーや構造化光（Structured Light）センサーのテンプレートとしては使えません。

このチュートリアルは、次の流れで進みます。

1. **単一ビュー後処理パイプライン**で視差マップと深度画像を生成する
2. **深度カメラアセットラッパー**で公式の深度センサーを読み込む
3. **既存アセットの更新**と**新規深度センサーモデルの構築**手順を確認する

## ステップ 1：単一ビュー後処理パイプライン

`SingleViewDepthSensor` クラスと Replicator が提供する新しいアノテーターの使い方は、次の Standalone 例で確認できます。

```bash
./python.sh standalone_examples/api/isaacsim.sensors.camera/camera_stereoscopic_depth.py
```

実行すると、Black Grid 環境に色付きの基本形状が配置されたビューポートが表示されます。

![ステレオ深度の例のビューポート](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_ext-isaacsim.sensors.camera-1.1.2_viewport_camera_stereoscopic_depth.png)

続いて、深度センサーが生成する**視差マップ**を確認します。

1. ビューポートでカメラのレンダープロダクトを選択します。
2. **Render Settings > Post Processing > Depth Sensor** を開き、後処理パイプラインの設定を確認します。
3. **Depth Sensor** のチェックボックスをオンにします。
4. **RGB Depth Output Mode** ドロップダウンから **Disparity** を選択します。

![Depth Sensor の後処理設定](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_ext-isaacsim.sensors.camera-1.1.2_viewport_depth_sensor_settings.png)

ビューポートに視差マップが表示されることを確認します。

![視差マップ](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_ext-isaacsim.sensors.camera-1.1.2_viewport_depth_sensor_disparity.png)

!!! note "後処理設定の適用範囲"
    **Render Settings > Post Processing > Depth Sensor** 以下の設定は、シーン内のすべてのレンダープロダクト（ビューポートを含む）に適用されます。個々のレンダープロダクトを深度センサーとして構成したい場合は、`SingleViewDepthSensor` クラスを使います。

Isaac Sim の UI を閉じ、`--test` を付けてヘッドレスで再実行します。

```bash
./python.sh standalone_examples/api/isaacsim.sensors.camera/camera_stereoscopic_depth.py --test
```

カメラのレンダープロダクトにアタッチされたアノテーターから、次の 2 つの画像が生成されます。1 枚目は `DepthSensorDistance` アノテーターの出力（`depth_sensor_distance.png`）、2 枚目は `DistanceToImagePlane` アノテーターの出力（`distance_to_image_plane.png`）です。

![DepthSensorDistance の出力](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.1_full_ext-isaacsim.sensors.camera-1.3.6_viewport_depth_sensor_distance.png)

![DistanceToImagePlane の出力](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.1_full_ext-isaacsim.sensors.camera-1.3.6_viewport_distance_to_image_plane.png)

!!! warning "最初のフレームで出るエラーについて"
    新しい深度 AOV を使うと、次のようなエラーが表示されることがあります。

    ```text
    [Error] [rtx.postprocessing.plugin] DepthSensor: Texture sizes do not match: ...
    [Error] [rtx.postprocessing.plugin] DepthSensor: Failed to allocate view resources for view 1 device 0
    [Error] [carb.scenerenderer-rtx.plugin] Failed to export AOV 38 to render product. ...
    ```

    これらは深度シミュレーションの**最初のフレームでのみ想定される**エラーで、将来のリリースで修正される予定です。

## ステップ 2：深度カメラアセットラッパー

Isaac Sim は、いくつかの公式深度センサーをサポートしています。これらは `isaacsim.sensors.camera.SingleViewDepthSensorAsset` クラスを使って、ステージ上に参照として自動的に読み込めます。この API はアセット内から単一ビュー深度センサーの特性を指定する `RenderProduct` prim を探し、対応する `Camera` prim を `SingleViewDepthSensor` インスタンスとしてラップします。

この方法で読み込むと、アセット内の各深度センサーの後処理パイプラインを完全に制御でき、API を通じて任意の数のアノテーターをアタッチできます。

!!! note "アセットの属性は暫定的"
    公式アセットの Camera prim に対する属性指定は暫定的なもので、将来のアセット更新やリリースで変更される可能性があります。

例として、Intel RealSense D455 深度カメラアセットを読み込み、深度センサーにアノテーターをアタッチするには、Script Editor で次のスニペットを実行します。

```python
from isaacsim.sensors.camera import SingleViewDepthSensorAsset
from isaacsim.storage.native import get_assets_root_path

# RealSense D455 をステージに追加
asset_path = get_assets_root_path() + "/Isaac/Sensors/Intel/RealSense/rsd455.usd"
realsense_d455 = SingleViewDepthSensorAsset(prim_path="/World/realsense_d455", asset_path=asset_path)

# アセット内のすべての深度センサー prim を初期化し、
# それぞれの HydraTexture にアタッチしたレンダープロダクトを作成する
realsense_d455.initialize()

# アセット内で利用可能なすべての深度センサーの prim パスを表示
print(realsense_d455.get_all_depth_sensor_paths())

# camera prim パスを指定して特定の深度センサーを取得
depth_sensor = realsense_d455.get_child_depth_sensor("/World/realsense_d455/RSD455/Camera_Pseudo_Depth")

# 深度センサーにアノテーターをアタッチ
depth_sensor.attach_annotator("DepthSensorDistance")
```

**Stage** ウィンドウに RealSense D455 深度カメラアセットが読み込まれたことが表示されます。

![深度センサーアセットの Stage ウィンドウ](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_ext-isaacsim.sensors.camera-1.3.0_gui_depth_sensor_asset_stage.png)

**Layer** ウィンドウには、`HydraTexture` と `DepthSensorDistance` の RenderVar がアタッチされた `RenderProduct` prim が作成されたことが表示されます。

![深度センサーアセットの Layer ウィンドウ](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_ext-isaacsim.sensors.camera-1.3.0_gui_depth_sensor_asset_layer.png)

## ステップ 3：深度センサーモデルを構築する

### 既存アセットを深度センサー対応に更新する

`SingleViewDepthSensorAsset` クラスには、既存アセットを深度センサー対応に更新する便利な API があります。次の例は、新しい Camera prim を深度センサーとして更新し、他のステージで参照として読み込める USD ファイルとして書き出す方法を示します。

```bash
./python.sh standalone_examples/api/isaacsim.sensors.camera/camera_add_depth_sensor.py
```

実行すると、ローカルディレクトリに `example_camera_with_depth_sensor.usd` アセットが作成されます。Isaac Sim で開くと、Stage ウィンドウで Camera prim に関連付けられた新しいレンダープロダクト prim が作成され、`omni:rtx:post:depthSensor:baselineMM` 属性にカスタム値が設定されていることを確認できます。

![更新後アセットの Stage ウィンドウ](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_ext-isaacsim.sensors.camera-1.3.0_gui_new_depth_sensor_asset_stage.png)

新しいステージを開き、Script Editor で次のスニペットを実行すると、このアセットを参照として読み込めます。

```python
from isaacsim.sensors.camera import SingleViewDepthSensorAsset

asset_path = "example_camera_with_depth_sensor.usd"
example_depth_sensor = SingleViewDepthSensorAsset(prim_path="/example_depth_sensor", asset_path=asset_path)
example_depth_sensor.initialize()
```

![更新後アセットの Layer ウィンドウ](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_ext-isaacsim.sensors.camera-1.3.0_gui_new_depth_sensor_asset_layer.png)

### 新しい深度センサーアセットを作成する

前述のとおり、単一ビュー後処理パイプラインは**ステレオ深度カメラ**をモデル化するためのものです（ToF や構造化光センサーには使えません）。新しいステレオ深度センサーモデルを構築する一般的な流れは、次のとおりです。

1. サポートされている [インポーター/エクスポーター](../importer_exporter/index.md) のいずれかを使い、既存の深度センサーモデルを USD にインポートします。
2. モデルの適切な位置に Camera prim を追加してアセットを保存します。
3. USD でテスト環境を構築し、実機のテストリグを正確に再現するようにオブジェクトと深度センサーを配置します。
4. OpenCV で実機カメラをキャリブレーションする場合は、[カメラセンサー](01_camera_sensors.md) のレンズ歪みモデルの要領で OpenCV レンズ歪みスキーマを Camera prim に適用します。
5. レンダリング画像と実機画像を比較しながら、各 Camera prim の内部・外部パラメータをキャリブレーションします。
6. キャリブレーションが済んだら、深度センサースキーマをレンダープロダクトに適用し、属性を設定して深度画像をレンダリングします。実機の深度画像と比較し、許容誤差に収まるまで属性を調整して繰り返します。

## まとめ

このチュートリアルでは、次の内容を学びました。

- Isaac Sim はステレオ深度カメラを**単一ビュー**の後処理パイプラインでモデル化すること（`SingleViewDepthSensor`）
- ビューポートで視差マップを確認し、`DepthSensorDistance` / `DistanceToImagePlane` アノテーターで深度画像を出力する方法
- `SingleViewDepthSensorAsset` で公式アセットを読み込み、既存アセットを深度センサー対応に更新する方法
- 新しいステレオ深度センサーモデルを構築するワークフロー

## 次のステップ

- RTX ベースの LiDAR / Radar については [RTX センサー](03_rtx_sensors.md) を参照してください。
