---
title: シーンベースの合成データセット生成
---

# シーンベースの合成データセット生成

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- **外部設定ファイル**（YAML / JSON）によるシミュレーション・シナリオパラメータの調整
- カスタム環境の読み込みと **Isaac Sim API によるアセットのスポーン**
- ランダム化された**物理シミュレーション**の実行
- 各種 **Replicator ランダム化グラフ**の登録（scatter_2d、シーケンス配置、ライト）
- Replicator API による**カメラとレンダープロダクト**の作成、**ライター**でのディスク保存

## はじめに

### 前提条件

- [チュートリアル 3: Getting Started スクリプト](03_getting_started_scripts.md)を完了していること
- omni.replicator の[アノテータ](https://docs.omniverse.nvidia.com/extensions/latest/ext_replicator/annotators_details.html)と[ライター](https://docs.omniverse.nvidia.com/extensions/latest/ext_replicator/writer_examples.html)、[ランダマイザ](https://docs.omniverse.nvidia.com/extensions/latest/ext_replicator/randomizer_details.html)の基本
- スタンドアロンアプリケーションとしてのシミュレーション実行（[ROS 2 チュートリアル 17](../ros/17_standalone_python.md) でも扱いました）

### 所要時間

約 30〜40 分

### 概要

「シーンベース」の SDG は、**現実的なシーン全体**（このチュートリアルでは倉庫）の中にオブジェクトを配置して、学習用データセットをオフライン（ディスク）に生成するアプローチです。シナリオは次のとおりです：

- 倉庫環境内の指定エリアに**フォークリフトをランダム配置**
- フォークリフトの位置を基準に、正面のランダムな距離に**パレット**を配置
- Replicator の `scatter_2d`（`check_for_collisions=True`）で、パレット上に**箱を衝突なしで散布**（毎キャプチャフレームで再散布）
- フォークリフトの OBB（有向バウンディングボックス）の底面コーナーのいずれかに**トラフィックコーン**をランダム配置
- SDG 開始前に短い物理シミュレーションを実行し、フォークリフト後方のパレットに**箱を落下**させて自然な積み上がりを作る

カメラは 3 視点（トップダウン／パレット注視のランダム視点／フォークリフト運転席からの俯瞰）で、データは**バックエンドを設定できる** Replicator ライターで収集します。既定では **BasicWriter ＋ DiskBackend** の組み合わせで、rgb・bounding_box_2d_tight・semantic_segmentation・distance_to_image_plane・bounding_box_3d・occlusion の各アノテータのデータを `<作業ディレクトリ>/_out_scene_based_sdg` に保存します。

![シーンベース SDG](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isaac_tutorial_replicator_offline_data.png)

## ステップ 1：実行してみる

メインスクリプトは `<install_path>/standalone_examples/replicator/scene_based_sdg/scene_based_sdg.py`、ヘルパー関数は `scene_based_sdg_utils.py` にあります。既定の設定はスクリプト内の Python 辞書として保持されているため、**設定ファイルなしでそのまま実行できます**：

```bash
./python.sh standalone_examples/replicator/scene_based_sdg/scene_based_sdg.py
```

既定のパラメータを上書きするには、`--config <path/to/file.json/yaml>` でカスタム設定ファイルを渡します。サンプル設定は `scene_based_sdg/config/*` にあります：

| 設定ファイル | 内容 |
|---|---|
| （なし） | スクリプト内の既定パラメータで実行（レンダラーは `RealTimePathTracing`、`rt_subframes: 32`、`num_frames: 10`） |
| `config_basic_writer.yaml` | BasicWriter＋`backend_type: DiskBackend` を明示指定し、環境を Grid（`default_environment.usd`）に変更 |
| `config_default_writer.json` | 既定ライター（BasicWriter）＋DiskBackend で rgb と instance_segmentation を出力 |
| `config_kitti_writer.yaml` | **KittiWriter** で KITTI 形式のデータセットを出力（`backend_type: null`） |
| `config_coco_writer.yaml` | **CocoWriter** で COCO 形式のデータセットを出力（`backend_type: null`） |

!!! note "backend_type / backend_params 設定キー"
    Isaac Sim 6.0 では、出力先を **バックエンド**（`DiskBackend` など）として設定する方式になり、設定ファイルに `backend_type` と `backend_params`（`output_dir` など）を指定します。BasicWriter のような組み込みライターはバックエンド経由で書き込み、KittiWriter / CocoWriter のように独自に出力を管理するライターでは `backend_type: null` として `writer_config` 内の `output_dir` を使います。

```bash
./python.sh standalone_examples/replicator/scene_based_sdg/scene_based_sdg.py \
    --config standalone_examples/replicator/scene_based_sdg/config/config_kitti_writer.yaml
```

!!! note "KITTI / COCO 形式で出力できることの意味"
    KittiWriter / CocoWriter を使うと、既存の学習パイプライン（KITTI・COCO 形式を前提とするツール群）に**変換なしでそのまま**接続できます。まとめの節で触れる TAO Toolkit での学習も KITTI 形式の出力を前提としています。

## ステップ 2：スクリプトの構成を理解する

### SimulationApp としての実行

GUI の Script Editor で実行する通常の omni.replicator の例と異なり、このスクリプトは Isaac Sim をスタンドアロンアプリケーションとして起動します。**`SimulationApp` オブジェクトは、他の依存モジュール（`omni.replicator.core` など）の import より先に作成する**必要があります（Omniverse 関連の import は SimulationApp 作成後に行います）。

### 環境の読み込み

環境は USD ステージです。`get_assets_root_path` で Nucleus サーバーのパスを取得し、環境の URL を `open_stage` に渡します。読み込みの成否は `stage_opened, _ = open_stage(...)` のように戻り値のタプルから確認し、失敗時はアプリケーションを終了します。読み込み後は `rep.set_global_seed(42)` と `np.random.default_rng(42)` で**シード付きのランダム化**を初期化します。

### カメラとライターの作成

カメラは `rep.functional.create.camera` で作成し、`rep.functional.create.scope` で作った `/SDG/Cameras` スコープの下に整理して配置します（DriverCam / PalletCam / TopCam の 3 台）。作成したカメラからレンダープロダクトを作り、ヘルパー関数 `setup_writer(config)` がバックエンド設定（`backend_type` / `backend_params`）に対応したライターを初期化してアタッチします。

パフォーマンスのため、**レンダープロダクトは SDG 開始まで無効化**（`hydra_texture.set_updates_enabled(False)`）して不要なレンダリングを避けます。

## ステップ 3：ドメインランダマイゼーション

このチュートリアルの中心は、**Isaac Sim API と Replicator API のランダム化の使い分け**です。

### Isaac Sim API によるランダム化（1 回きりの配置）

フォークリフトのスポーンと、その位置に基づくパレットの配置は、シード付きの `np.random.Generator`（`rng`）を使った通常の Python コードで行います。プリムの作成・参照・ラベル付け・配置には `isaacsim.core.experimental` 系のユーティリティ（`define_prim`、`add_reference_to_stage`、`add_labels`、`XformPrim`）を使います：

```python
# フォークリフトをランダムな姿勢でスポーン
forklift_path = "/SDG/Forklift"
forklift_prim = define_prim(forklift_path)
add_reference_to_stage(assets_root_path + config["forklift"]["url"], forklift_path)
add_labels(forklift_prim, labels=[config["forklift"]["class"]], taxonomy="class")
XformPrim(
    forklift_path,
    positions=(rng.uniform(-20, -2), rng.uniform(-1, 3), 0),
    orientations=euler_angles_to_quaternion([0, 0, rng.uniform(0, math.pi)]).numpy(),
    reset_xform_op_properties=True,
)

# フォークリフトの正面（Y 軸方向）にランダムなオフセットでパレットを配置
forklift_tf = omni.usd.get_world_transform_matrix(forklift_prim)
pallet_offset_tf = Gf.Matrix4d().SetTranslate(Gf.Vec3d(0, rng.uniform(-1.8, -1.2), 0))
pallet_pos = (pallet_offset_tf * forklift_tf).ExtractTranslation()
```

### 毎フレームの再ランダム化（functional API とグラフランダマイザ）

キャプチャごとに変化させたい要素は、**functional API の直接呼び出し**と、**カスタムイベントでトリガーするグラフランダマイザ**の 2 通りで実現します：

**1. 箱の散布** — パレットのバウンディングボックスから散布面（透明な plane）を作り、SDG ループ内で `rep.functional.randomizer.scatter_2d` を**直接呼び出して**衝突チェック付きの散布を行います：

```python
rep.functional.randomizer.scatter_2d(
    prims=cardboxes, surface_prims=scatter_plane, check_for_collisions=True, rng=rng
)
```

**2. 箱のマテリアル** — 箱のメッシュに対する `rep.randomizer.materials` のグラフを `rep.trigger.on_custom_event` で登録し、ループ内で `rep.utils.send_og_event(event_name="randomize_cardboxes_materials")` によりトリガーします。

**3. コーンの配置** — フォークリフトの OBB（`compute_obb` / `get_obb_corners`）の底面コーナーから候補位置リストを計算し、定義済み候補からランダムに選んで配置します。

**4. ライトのランダム化** — フォークリフトとパレットを合わせた AABB（Axis-Aligned Bounding Box：座標軸に平行なバウンディングボックス。向きを持つ OBB と異なり回転しません）の上空（高さ 6〜7）の範囲で、スフィアライトの色・強度・位置・スケールをランダム化するグラフを登録し、カスタムイベント（`randomize_lights`）でトリガーします。

**5. カメラの姿勢** — ヘルパー関数でパレット／トップビュー／運転席カメラのランダム化範囲（bounds）を計算し、SDG ループ内で `rep.functional.modify.pose` によりカメラ位置をランダム化して対象を注視させます。

### 物理シミュレーション

ランダム化グラフの登録後、データ収集の前に、フォークリフト後方のパレットへ積まれた箱を落とす短い物理シミュレーションを実行します。これにより「きれいに整列した箱」ではなく**物理的に自然な積み上がり**が得られます。シミュレーションには **SimulationManager** と experimental の **GeomPrim / RigidPrim** クラス（`isaacsim.core.experimental.prims`）を使います。

## ステップ 4：実行と後続の学習

最後に、指定フレーム数だけランダム化とフレーム書き込みを実行し（SDG ループ）、`rep.orchestrator.wait_until_complete()` ですべてのデータの書き込み完了を待ってから、ライターのデタッチとレンダープロダクトの破棄を行います。GUI 実行時は `close_app_after_run: false` を設定すると、データ生成後もアプリケーションを開いたままにできます（headless 時は無視されます）。

!!! note "生成したデータで学習する（TAO Toolkit）"
    生成した KITTI 形式のデータは、**NVIDIA TAO Toolkit** でそのまま学習に使えます。TAO はセグメンテーション・分類・物体検出の事前学習済みモデルを提供しており、公式チュートリアルでは Detectnet V2 による物体検出が例として挙げられています。TAO は Jupyter ノートブックで学習プロセスをガイドし、spec ファイルの入力パスを合成データのフォルダ構成に合わせて書き換えるだけで、TFRecord への変換と学習が行えます。

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. **SimulationApp** としての Replicator スクリプトの実行と設定ファイル（バックエンド設定を含む）によるパラメータ化
2. **Isaac Sim API**（シード付きの 1 回きりの配置）と **rep.functional API／グラフランダマイザ**（毎フレームの再ランダム化）の使い分け
3. `rep.functional.randomizer.scatter_2d` の直接呼び出しと、カスタムイベントでトリガーする**マテリアル・ライトのランダム化グラフ**の登録
4. **SimulationManager** と experimental プリムクラスによる物理シミュレーション、**KITTI / COCO 形式**での出力

## 次のステップ

- [チュートリアル 5: オブジェクトベースの合成データセット生成](05_object_based_sdg.md) - オブジェクト中心の SDG パイプラインを学びます。
