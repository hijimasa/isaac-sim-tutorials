---
title: カメラへのノイズ付加
---

# カメラへのノイズ付加

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- センサー画像への **Augmentation（拡張処理）** の追加の概要
- **ノイズを加えた画像データ**を ROS 2 にパブリッシュする方法

## はじめに

### 前提条件

- [チュートリアル 5: ROS 2 カメラ](05_camera.md)を完了していること
- ROS 2 ブリッジが有効であること
- [omni.replicator](https://docs.omniverse.nvidia.com/extensions/latest/ext_replicator.html) の概念（アノテータ、ライター）に触れたことがあること
- スタンドアロンワークフローで ROS 2 メッセージングを使うため、[セットアップページ](00_setup.md)の「（オプション）内部 ROS 2 ライブラリを使う」の手順（スタンドアロンスクリプト用の環境変数設定）を完了しておくこと。ネイティブ ROS 2 を source して実行する場合はそのままで構いません

### 所要時間

約 15〜20 分

### 概要

実機のカメラ画像には必ずノイズが乗ります。グラウンドトゥルースそのままの「きれいすぎる」シミュレーション画像で開発した認識アルゴリズムは、実機に持っていくと性能が落ちることがあります（Sim-to-Real ギャップ）。このチュートリアルでは、Replicator の **Augmentation** 機能を使って、ROS 2 に配信するカメラ画像へガウシアンノイズを加える方法を、サンプルスクリプトを通して学びます。

このチュートリアルは、これまでの GUI ベースの手順と異なり、**スタンドアロン Python スクリプト**（Isaac Sim を Python スクリプトから起動する方式）を使います。

## サンプルを実行する

1. 1 つ目のターミナルで ROS 2 ワークスペースを source しておきます。
2. 別のターミナル（ROS 2 環境を source 済み、かつ Isaac Sim の内部ライブラリ用環境変数を設定済み）で、Isaac Sim のインストールディレクトリからサンプルスクリプトを実行します：

    ```bash
    ./python.sh standalone_examples/api/isaacsim.ros2.bridge/camera_noise.py
    ```

3. シーンの読み込みが終わると、ビューポートが倉庫のシーンを反時計回りにスキャンし始めることを確認します。
4. ROS 環境を source した新しいターミナルで `rviz2` を実行して空の RViz ウィンドウを開きます。
5. 左下の **Add** をクリックし、ポップアップの **By display type** タブから **Image** を選んで **OK** をクリックします。
6. RViz 画面のどこかに Image ウィンドウが追加され、Display ウィンドウに **Image** のメニュー項目が現れます。Image ウィンドウを使いやすい場所にドッキングします。
7. Display メニューの Image を展開し、**Image Topic** を `/rgb_augmented` に変更します。Isaac Sim の映像に少しノイズが乗ったバージョンが RViz の Image ウィンドウに表示されることを確認します。

![ノイズ付きカメラ画像](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_5.0_ros_tut_gui_ros2_camera_noise.gif)

## コード解説

### レンダープロダクトへのカメラ設定

最初のステップは、データ取得に使うレンダープロダクトにカメラを設定することです。ビューポートにカメラを設定する API もありますが、レンダープロダクトのプリムを直接操作する低レベル API もあり、どちらでも結果は同じです。ここでは既にレンダープロダクトのパスを扱っているため、`set_camera_prim_path` を使っています：

```python
# レンダープロダクトを取得し、カメラプリムを直接設定する
render_product_path = get_active_viewport().get_render_product_path()
set_camera_prim_path(render_product_path, CAMERA_STAGE_PATH)
```

### ノイズ関数（Augmentation）の定義

センサーパイプライン内の Augmentation は、次のいずれの方法でも定義できます：

- C++ OmniGraph ノード
- Python OmniGraph ノード
- [omni.warp](https://docs.omniverse.nvidia.com/extensions/latest/ext_warp.html) カーネル（GPU）
- numpy カーネル（CPU）

サンプルでは warp（GPU）版と numpy（CPU）版の基本的なノイズ関数が示されています（簡潔さのため、色値の範囲外チェックは省略されています）：

```python
import warp as wp

# GPU ノイズカーネル（説明用）。入力は RGBA、出力は RGB
@wp.kernel
def image_gaussian_noise_warp(
    data_in: wp.array3d(dtype=wp.uint8), data_out: wp.array3d(dtype=wp.uint8), seed: int, sigma: float = 0.5
):
    i, j = wp.tid()
    dim_i = data_out.shape[0]
    dim_j = data_out.shape[1]
    pixel_id = i * dim_i + j
    state_r = wp.rand_init(seed, pixel_id + (dim_i * dim_j * 0))
    state_g = wp.rand_init(seed, pixel_id + (dim_i * dim_j * 1))
    state_b = wp.rand_init(seed, pixel_id + (dim_i * dim_j * 2))

    data_out[i, j, 0] = wp.uint8(float(data_in[i, j, 0]) + (255.0 * sigma * wp.randn(state_r)))
    data_out[i, j, 1] = wp.uint8(float(data_in[i, j, 1]) + (255.0 * sigma * wp.randn(state_g)))
    data_out[i, j, 2] = wp.uint8(float(data_in[i, j, 2]) + (255.0 * sigma * wp.randn(state_b)))
```

```python
import numpy as np

# CPU ノイズカーネル
def image_gaussian_noise_np(data_in: np.ndarray, seed: int, sigma: float = 25.0):
    np.random.seed(seed)
    return data_in + sigma * np.random.randn(*data_in.shape)
```

### アノテータの登録

どちらの関数も `rep.Augmentation.from_function()` で Augmentation として登録できます。標準の `rgb` アノテータの出力にノイズ処理を合成した、新しいアノテータ `rgb_gaussian_noise` を登録します：

```python
import omni.replicator.core as rep

# rgba にノイズを加えて rgb で出力する拡張アノテータを登録する
# CPU 版を使う場合は image_gaussian_noise_warp を image_gaussian_noise_np に、
# device を "cpu" に変更する
rep.annotators.register(
    name="rgb_gaussian_noise",
    annotator=rep.annotators.augment_compose(
        source_annotator=rep.annotators.get("rgb", device="cuda"),
        augmentations=[
            rep.annotators.Augmentation.from_function(
                image_gaussian_noise_warp, sigma=0.1, seed=1234, data_out_shape=(-1, -1, 3)
            ),
        ],
    ),
)
```

!!! note "seed 引数について"
    `seed` は Replicator Augmentation の事前定義済みオプション引数で、Python 関数と warp カーネルのどちらでも使えます。`None` または負の値にすると、Replicator のグローバルシードとノード識別子から再現可能な一意のシードが生成されます。warp カーネルでは、この seed が乱数生成器の初期化に使われ、カーネル呼び出しごとに新しい整数シードが生成されます。

### ROS 2 パブリッシャ（ライター）の登録と接続

次に、新しい `rgb_gaussian_noise` アノテータを使う ROS 2 画像パブリッシャのライターを登録します：

```python
# 拡張画像を使う新しいライターを作成する
rep.writers.register_node_writer(
    name="CustomROS2PublishImage",
    node_type_id="isaacsim.ros2.bridge.ROS2PublishImage",
    annotators=[
        "rgb_gaussian_noise",
        omni.syntheticdata.SyntheticData.NodeConnectionTemplate(
            "IsaacReadSimulationTime", attributes_mapping={"outputs:simulationTime": "inputs:timeStamp"}
        ),
    ],
    category="custom",
)

# Replicator のテレメトリ追跡にライターを登録する
(
    rep.WriterRegistry._default_writers.append("CustomROS2PublishImage")
    if "CustomROS2PublishImage" not in rep.WriterRegistry._default_writers
    else None
)
```

最後に、このライターを初期化してレンダープロダクトにアタッチすると、データのキャプチャと ROS への配信が始まります：

```python
# ライターを作成してレンダープロダクトにアタッチする
writer = rep.writers.get("CustomROS2PublishImage")
writer.initialize(topicName="rgb_augmented", frameId="sim_camera")
writer.attach([render_product_path])
```

## まとめ

このチュートリアルでは、ROS センサーパイプラインへの **Augmentation の追加**の基礎と、RGB センサー出力への**ノイズ付加**を扱いました。

## 次のステップ

- [チュートリアル 7: カメラデータのパブリッシュ](07_camera_publishing.md) - Python スクリプティングでカメラのデータを配信する方法を学びます。
