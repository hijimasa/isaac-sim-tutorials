---
title: オブジェクト シミュレーションと合成データ生成（IRO）
---

# オブジェクト シミュレーションと合成データ生成（IRO）

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- `isaacsim.replicator.object`（IRO）拡張機能がコード変更なしで物体検出用の合成データを生成する仕組み
- エンドツーエンドのパイプラインと、UI / Docker / 埋め込みインターフェースからの実行方法
- 記述ファイル（YAML）の中心概念（Mutable / Harmonizer / Setting）
- テーブルにオブジェクトを落とすシーンの記述ファイルを作成する手順

## はじめに

### 前提条件

- Isaac Sim 5.1 が起動できること
- [Replicator の概要](01_replicator_overview.md) を理解していること
- YAML の基本を理解していること

### 所要時間

約 25〜30 分

### 概要

**isaacsim.replicator.object（IRO）** は、**コード変更が不要**な拡張機能で、小売の物体検出からロボティクスまで幅広いタスクのモデル訓練用合成データを生成します。可変（mutable）なシーンを記述した YAML 記述ファイル（またはそれらを積み重ねた階層）を入力とし、RGB・2D/3D バウンディングボックス・セグメンテーションマスクなどのグラフィックスコンテンツと記述ファイルを出力します。

![IRO の概要](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_replicator_ext-isaacsim.replicator.object-0.4.2_viewport_overview.png)

!!! note "IRO の価値"
    合成データによる深層学習は需要が高い一方、3D ソフトの習得（UI パネルへの習熟など）には時間がかかります。IRO は、Maya や 3ds Max の経験がないデータサイエンティストでも、**マクロ**を使ってドメインランダム化されたシーンを抽象的・直感的・コンパクトに記述できることを目指しています。ドメインランダム化では、詳細な 3D コンテンツより「シーンをどうランダム化するかのルール」と「ルール間の関係」が重要になります。

## エンドツーエンドのパイプライン

1. **グラフィックスリソースの取得** … IRO は USD 形式の 3D モデルを必要とします。OBJ など一般的な形式は asset converter で USD に変換できます。
2. **記述ファイルの作成** … 後述の手順で YAML を記述します。
3. **合成データの生成** … UI / Docker / 埋め込みインターフェースで実行します。
4. **CV モデルの訓練・デプロイ** … IRO で作成した画像で物体検出モデルを訓練する例は TAO 6.0 のノートブックにあります。

## ステップ 1：UI から実行する

1. **Windows > Extension Manager** で `isaacsim.replicator.object` を検索し、緑のカプセルアイコンで有効化します。
2. 有効化されると、右上に **Object Detection SDG** パネルが表示され、**Tools > Action and Event Data Generation** に Object Detection SDG と Distribution Visualizer が追加されます。
3. パネル右側のフォルダアイコン（または VS Code アイコン）で拡張機能のルートフォルダを開きます。`PATH_TO_EXTENSION/isaacsim/replicator/object/configs` に多数の YAML 記述ファイルがあります（まずは `demo_kaleidoscope.yaml` がおすすめ）。
4. `global.yaml` の `output_path` を、出力を保存するローカルフォルダに更新します。
5. Simulate ボタン下のドロップダウンから `demo_kaleidoscope` を選び、**Simulate** をクリックして開始します。進捗はプログレスバーで表示されます。

!!! warning "プレースホルダの置換"
    一部の例にはプレースホルダがあり、有効なパスに置換する必要があります。例：`global.yaml` / `minimum.yaml` の `PATH_TO_OUTPUT`、`demo_bottle.yaml` の `PATH_TO_LABEL_IMAGES`（JPEG 画像フォルダ）、`demo_table.yaml` 等の `PATH_TO_BOXES`（箱などの USD フォルダ）など。USD ごとにサイズが異なるため、正しく表示されない場合は scale を調整します。

## ステップ 2：Docker から実行する

Isaac Sim の Docker コンテナで実行できます。`global.yaml` の `output_path` を `/tmp` 以下に設定します。

```bash
docker run --gpus device=0 --entrypoint /bin/bash -v LOCAL_PATH:/tmp --network host -it ISAAC_SIM_DOCKER_CONTAINER_URL

# 例：demo_kaleidoscope でシミュレーション起動
bash isaac-sim.sh --no-window --enable isaacsim.replicator.object --allow-root \
  --/log/file=/tmp/isaacsim.replicator.object.log --/log/level=warn --/windowless=True \
  --/config/file=PATH_TO_EXTENSION/isaacsim/replicator/object/configs/demo_kaleidoscope.yaml
```

ログ `/tmp/isaacsim.replicator.object.log` を `METROPERF` でフィルタすると拡張機能のメッセージを確認できます。

!!! note
    Docker 内の初回実行で何も生成されない場合は、もう一度実行してください。

## ステップ 3：埋め込みインターフェースで素早く試す

ディスクへの書き出しが不要なときは、埋め込みインターフェースが記述ファイルのプロトタイピングに便利です。記述ファイルを選び、Object Detection SDG パネルの **Initialize Scene Randomization** で読み込むと、ランダム化シンボルが作成・接続されます。以降、**Randomize Scene** をクリックするたびにシーンがランダム化されます。物理的にプレビューするには左側の三角の Play ボタンを押します。

![埋め込みインターフェース](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_replicator_ext-isaacsim.replicator.object-0.4.2_viewport_ui_embedded_interface.webp)

## 出力

シミュレーション後、出力は `output_path` に保存され、内容は出力スイッチ設定で決まります。例として `demo_bottle` は RGB 画像とセグメンテーションを出力します。

![bottle の RGB](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_replicator_ext-isaacsim.replicator.object-0.4.2_viewport_bottle_image.jpg)
![bottle のセグメンテーション](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_replicator_ext-isaacsim.replicator.object-0.4.2_viewport_bottle_segmentation.png)

2D バウンディングボックスは次の形式です（4 つの正の数が `x_min, x_max, y_min, y_max`。`-1` はオクルージョン率の位置で、ボトルは透明なため `-1`）。

```text
bottle_0 0 -1.0 0 1028 333 1362 2159 0 0 0 0 0 0 0
bottle_1 0 -1.0 0 1895 112 2277 1694 0 0 0 0 0 0 0
bottle_2 0 -1.0 0 1281 462 1854 2159 0 0 0 0 0 0 0
```

## 概念：Mutable / Harmonizer / Setting

記述ファイルは、メインキー `isaacsim.replicator.object` を持つ YAML です。キーと値のペアはそれぞれ **Mutable**・**Harmonizer**・**Setting** のいずれかです。

- **Setting** … シーンの構成方法とデータ出力方法を記述します（出力フレーム数、2D BBox の有無、物理の重力・摩擦など）。
- **Mutable** … シーンに配置するオブジェクト。毎フレームランダム化されます。
- **Harmonizer** … Mutable のランダム化の仕方を制約します。他の Mutable のランダム化状態を把握して、それに応じてランダム化したい場合に定義します。

**シミュレーションワークフロー**：起動時に初期化ステージ、その後は毎フレームのシミュレーションステージが実行されます。初期化では記述ファイルがパースされ、実際の値の解決が必要な各 Mutable Attribute に対して**シンボル**が作成されます。シンボルが解決されると、依存するシンボルも再帰的に解決されます。未解決の harmonized な属性に出会うとパーサは `AWAITING_HARMONIZATION` 状態になり、Harmonizer が情報を集めてランダム化し、結果を伝播します。解決後、値で USD シーンを更新し、重力が有効なら物理を解決（重なりや落下）し、グラフィックスを取得します。各フレームの状態は保存され、後で復元・検査できます。

## ステップ 4：記述ファイルを作成する

テーブルの上にランダムなオブジェクトを落とすシーンを作ります。ドームライト用 HDRI（`PATH_TO_HDRI`）、テーブル USD（`PATH_TO_TABLE`）、散布するオブジェクトの USD フォルダ（`PATH_TO_OBJECTS`）があるとします。まずビューポートにアセットをドラッグして配置範囲を把握し、オブジェクトの妥当な位置範囲（例：`(-13, 100, -70)` 〜 `(13, 100, 70)`）を決めます。

![ドラッグ＆ドロップで確認](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_replicator_ext-isaacsim.replicator.object-0.4.2_viewport_drag_and_drop.webp)

```yaml
isaacsim.replicator.object:
  # 最小限
  version: 0.4.x
  num_frames: 3
  seed: 0
  output_path: PATH_TO_OUTPUT
  screen_height: 2160
  screen_width: 3840

  # 物理パラメータ
  gravity: 10000
  friction: 0.3
  simulation_time: 10
  linear_damping: 4

  # ライト
  bright_light:
    type: light
    subtype: dome
    intensity: 1000
    transform_operators:
    - rotateX: 270
    texture_path: PATH_TO_HDRI

  # カメラ（$[/...] はマクロによる参照）
  focal_length: 14.228393962367306
  horizontal_aperture: 20.955
  camera_parameters:
    screen_width: $[/screen_width]
    screen_height: $[/screen_height]
    focal_length: $[/focal_length]
    horizontal_aperture: $[/horizontal_aperture]
    near_clip: 0.001
    far_clip: 100000
  default_camera:
    type: camera
    camera_parameters: $[/camera_parameters]
    transform_operators:
    - translate: [0, 50, 0]
    - rotateY:
        distribution_type: range
        start: -180
        end: 180
    - rotateX: -30
    - translate_local: [0, 0, 400]

  # 落とす箱（10 個）
  box:
    count: 10
    type: geometry
    subtype: mesh
    physics: rigidbody  # 重力・衝突などに反応
    tracked: true       # true なら BBox・セグメンテーション等を出力に記録
    usd_path:
      distribution_type: folder
      value: PATH_TO_OBJECTS
      suffix: usd
    transform_operators:
    - translate:  # 計画した範囲
        distribution_type: range
        start: [-13, 100, -70]
        end: [13, 100, 70]
    - rotateXYZ:
        distribution_type: range
        start: [-180, -180, -180]
        end: [180, 180, 180]
    - scale: [0.2, 0.2, 0.2]

  # テーブル
  table:
    type: geometry
    subtype: mesh
    physics: collision  # 剛体は衝突するが自身は動かない
    usd_path: PATH_TO_TABLE
    transform_operators:
    - rotateX: -90
```

**Simulate** を押すと RGB 画像とセグメンテーションマスクが生成されます。

![生成された RGB](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_replicator_ext-isaacsim.replicator.object-0.4.2_viewport_step_by_step_rgb.jpg)

!!! warning
    記述の YAML フォーマット（インデントなど）が正しいか確認してください。`mapping values are not allowed here` エラーはフォーマットの問題であることが多いです。

## シーン編集とカタログ

**シーン編集**：埋め込みインターフェースで作成したシーンでは、立方体を作成して translate と size を変え（回転は不可）、その空間範囲に含まれる prim の可視性を切り替えられます（**Toggle Visibility of selected region** ボタン。事前に立方体を選択しておく必要があります）。

![可視性の切り替え](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_replicator_ext-isaacsim.replicator.object-0.4.2_viewport_toggle_visibility.webp)

**カタログ**：記述ファイルで使える要素は、Setting / Mutable / Camera / Geometry / Light / Mutable Attribute / Transformation / Harmonizer / Macro / Distribution Visualizer / Randomization Dependency のカタログにまとめられています。型が期待される箇所には、後で評価されるマクロ文字列（例：`$[index]`）も使えます。

!!! note "使用している 3rd-party ライブラリ"
    py3dbp（改変, MIT）、PyYaml（MIT）、trimesh（MIT）、regex（Apache）。

## まとめ

このチュートリアルでは、次の内容を学びました。

- IRO がコード変更なしで物体検出用の合成データを生成すること
- UI / Docker / 埋め込みインターフェースからの実行方法と出力形式
- 記述ファイルの中心概念（Mutable / Harmonizer / Setting）とシミュレーションワークフロー
- テーブルにオブジェクトを落とすシーンの記述ファイルの書き方

## 次のステップ

- シーンの自然言語記述は [VLM シーンキャプショニング](19_replicator_caption.md) を参照してください。
