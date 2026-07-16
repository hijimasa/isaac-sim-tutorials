---
title: PhysX SDK Generic センサー
---

# PhysX SDK Generic センサー

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- Generic センサーがカスタムのレイパターンで ground truth 深度を測定する仕組み
- スキャンパターンを定義するパラメータ（streaming / sampling_rate / batch_size / sensor_pattern / origin_offsets）
- ストリーミングモードと繰り返しモードの違い
- バッチデータを順次送信してスキャンを継続する方法

## はじめに

### 前提条件

- [PhysX SDK センサー](14_physx_sensors.md) の概要を理解していること
- NumPy の基本操作を理解していること

### 所要時間

約 15〜20 分

### 概要

PhysX SDK Generic センサーは、PhysX SDK のレイキャストを使って 2 つの prim 間の深度を測定します。Isaac Sim で PhysX SDK ベースのセンサーを構築し、ground truth 深度を測定する方法のデモンストレーションとなっています。**任意のスキャンパターン**を自分で定義できるのが最大の特徴です。

## ステップ 1：サンプルを実行する

1. **Windows > Examples > Robotics Examples** で Robotics Examples タブを有効にします。
2. **Robotics Examples > Sensors > Custom Pattern Range Sensor** をクリックします。
3. **Load Sensor** → **Load Scene** → **Set Sensor Pattern** の順にボタンを押します。
4. **Open Source Code** でソースコードを確認できます（Python API でセンサーを作成・追加・制御する例）。
5. **PLAY** で開始します。

![Generic センサーの例](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_full_tut_viewport_generic_sensor.webp)

パターンを可視化するには、レイが壁に当たって刻まれた像を保存します。出力ディレクトリを指定して **Save Pattern Image** を押し、保存された画像を開いてジグザグパターンを確認します。

![スキャンパターン](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isaac_tutorial_advanced_generic_sensor_pattern.png)

## ステップ 2：スキャンパターンをカスタマイズする

スキャンパターンをカスタマイズするには、次のパラメータを指定・変更します。

| パラメータ | 説明 |
|---|---|
| `streaming` | データを継続的にストリーミングする場合は `True`、最初に 1 度だけバッチ送信して繰り返す場合は `False` |
| `sampling_rate` | 1 秒あたりのスキャン数 |
| `batch_size` | 1 バッチに含まれるスキャン数。数フレームを描画しても枯渇しない十分な大きさが必要 |
| `sensor_pattern` | Nx2 の NumPy 配列（N は batch_size）。各列は各レイの `[azimuth, zenith]` 角度 |
| `origin_offsets` | （省略可）Nx3 の NumPy 配列。各行は各レイの原点からのオフセット `[x, y, z]` |

!!! note "batch_size の考え方"
    たとえば 2400 スキャン/秒、描画レートが 120 fps の場合、各フレームは 20 スキャンを描画します。batch_size を 12000 にすると、枯渇するまでに 120 fps で 600 フレーム（5 秒）描画できます。batch_size が `sampling_rate / fps` に満たない場合、センサーはフレームあたり batch_size 分しかスキャンできず、意図より遅くなります。

    - **azimuth**（方位角）… x 軸から測ったレイの水平角
    - **zenith**（天頂角）… z 軸から測ったレイの垂直角

## ステップ 3：スキャンパターンの例

### ストリーミング生成パターン

例では、上下 1 往復ごとに水平方向へ 10 回スイープし、ジグザグを作ります。

```python
def _test_streaming_data(self):
    # カスタムパターン生成
    # 数フレーム描画しても枯渇しない十分な大きさのバッチで送る。
    batch_size = int(1e6)  # 処理する各バッチのサイズ
    half_batch = int(batch_size / 2)
    # 各レイは azimuth（x 軸からの水平角）と zenith（z 軸からの垂直角）で指定
    frequency = 10
    N_pts = int(batch_size / frequency / 2)
    # azimuth はバッチごとに frequency 回、上下限の間をジグザグ
    azimuth = np.tile(
        np.append(np.linspace(-np.pi / 4, np.pi / 4, N_pts), np.linspace(np.pi / 4, -np.pi / 4, N_pts)), frequency
    )
    # zenith はバッチごとに 1 往復
    zenith = np.append(
        np.linspace(-np.pi / 4, np.pi / 4, half_batch), np.linspace(np.pi / 4, -np.pi / 4, half_batch)
    )
    # カスタムパターンは [azimuth, zenith] 角度の配列として送る
    self.sensor_pattern = np.stack((azimuth, zenith))
```

origin offset は省略可能です。例では小さなランダムオフセットを追加しています。

```python
    # 各レイは原点にオフセットを持てる
    self.origin_offsets = 5 * np.random.random((batch_size, 3))
    # self.origin_offsets = np.zeros((batch_size, 3))   # オフセットなし
```

### ファイルからパターンを読み込む

プログラムで生成できない場合や生成方法を開示したくない場合は、ファイルからデータをインポートできます。

```python
## ファイルからデータをインポート
sensor_pattern = np.loadtxt("filename.csv", delimiter=",")
batch_size = np.shape(sensor_pattern)[0]
sensor_pattern = np.deg2rad(sensor_pattern).T.copy()   ## 必ず .copy() を使う
```

### 繰り返しパターン

繰り返しを分かりやすく見せるため、上向きにスキャンする組と下向きにスキャンする組の 2 モードに分けます。正しく実行できれば、追加データを取り込まずに繰り返されることを確認できます。

![繰り返しパターン](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isaac_tutorial_advanced_generic_repeat.gif)

非ストリーミングモードにするには `self._streaming = False` に設定します。すると次のコードでパターンが生成されます。

```python
def _test_repeating_data(self):
    batch_size = int(1e6)
    half_batch = int(batch_size / 2)
    frequency = 10
    N_pts = int(batch_size / frequency / 2)
    azimuth = np.tile(
        np.append(np.linspace(-np.pi / 4, np.pi / 4, N_pts), np.linspace(np.pi / 4, -np.pi / 4, N_pts)), frequency
    )
    zenith = np.append(-0.5 * np.ones(half_batch), 0.5 * np.ones(half_batch))
    sensor_pattern = np.stack((azimuth, zenith))
    origin_offsets = 0.05 * np.random.random((batch_size, 3))
```

## ステップ 4：スキャンパターンを順次送信する

センサーが各バッチを処理し、データが枯渇しそうになると `send_next_batch()` が `True` になります。そのタイミングで `set_next_batch_rays(prim_path, sensor_pattern)`（オフセットがあれば `set_next_batch_offsets(prim_path, sensor_pattern)` も）で次のバッチを送信します。

```python
def _on_editor_step(self, step):
    if not self._timeline.is_playing():
        return

    if self._timeline.is_playing():
        if self._generic:
            if self._pattern_set:
                # send_next_batch は、データが枯渇して補充が必要になると True を返す
                if self._sensor.send_next_batch(self._genericPath):
                    # 次のバッチを set_next_batch_rays() で設定
                    self._sensor.set_next_batch_rays(self._genericPath, self.sensor_pattern)
                    # （省略可）各レイのオフセットがあれば追加
                    self._sensor.set_next_batch_offsets(self._genericPath, self.origin_offsets)
```

## まとめ

このチュートリアルでは、次の内容を学びました。

- Generic センサーが任意のレイパターンで ground truth 深度を測定できること
- `sensor_pattern`（`[azimuth, zenith]`）や `batch_size` などのパラメータの意味
- ストリーミングモードと繰り返しモード、ファイルからのパターン読み込み
- `send_next_batch()` を使ってバッチを順次送信する方法

## 次のステップ

- [PhysX SDK Lidar](16_physx_lidar.md) で、回転式 LiDAR の模擬を学びます。
