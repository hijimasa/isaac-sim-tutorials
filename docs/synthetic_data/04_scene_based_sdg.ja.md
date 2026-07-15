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

カメラは 3 視点（トップダウン／パレット注視のランダム視点／フォークリフト運転席からの俯瞰）で、既定では **BasicWriter** が rgb・semantic_segmentation・bounding_box_3d を `<作業ディレクトリ>/_out_scene_based_sdg` に保存します。

![シーンベース SDG](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isaac_tutorial_replicator_offline_data.png)

## ステップ 1：実行してみる

メインスクリプトは `<install_path>/standalone_examples/replicator/scene_based_sdg/scene_based_sdg.py`、ヘルパー関数は `scene_based_sdg_utils.py` にあります。既定の設定はスクリプト内の Python 辞書として保持されているため、**設定ファイルなしでそのまま実行できます**：

```bash
./python.sh standalone_examples/replicator/scene_based_sdg/scene_based_sdg.py
```

既定のパラメータを上書きするには、`--config <path/to/file.json/yaml>` でカスタム設定ファイルを渡します。サンプル設定は `scene_based_sdg/config/*` にあります：

| 設定ファイル | 内容 |
|---|---|
| （なし） | スクリプト内の既定パラメータで実行 |
| `config_basic_writer.yaml` | BasicWriter を明示指定し、環境を Grid（`default_environment.usd`）に変更 |
| `config_default_writer.json` | 既定ライター（BasicWriter）で rgb と instance_segmentation を出力 |
| `config_kitti_writer.yaml` | **KittiWriter** で KITTI 形式のデータセットを出力 |
| `config_coco_writer.yaml` | **CocoWriter** で COCO 形式のデータセットを出力 |

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

環境は USD ステージです。`get_assets_root_path` で Nucleus サーバーのパスを取得し、環境の URL を `open_stage` に渡します。`open_stage` は読み込みの成否を bool で返し、失敗時はアプリケーションを終了します。

### カメラとライターの作成

カメラの作成には Replicator（`rep.create.camera`）と Isaac Sim API（`prims.create_prim`）の 2 通りの方法が示されています。作成したカメラからレンダープロダクトを作り、BasicWriter にアタッチして、選択したアノテータ（rgb・semantic_segmentation・bounding_box_3d）のデータを出力先に書き込みます。

パフォーマンスのため、**レンダープロダクトは SDG 開始まで無効化**して不要なレンダリングを避けます。また、運転席カメラは `rep.get.prim_at_path` で OmniGraph ノードとしてラップし、ランダム化グラフの各ステップでランダム化できるようにしています。

## ステップ 3：ドメインランダマイゼーション

このチュートリアルの中心は、**Isaac Sim API と Replicator API のランダム化の使い分け**です。

### Isaac Sim API によるランダム化（1 回きりの配置）

フォークリフトのスポーンと、その位置に基づくパレットの配置は、通常の Python コードで行います：

```python
# フォークリフトをランダムな姿勢でスポーン
forklift_prim = prims.create_prim(
    prim_path="/World/Forklift",
    position=(random.uniform(-20, -2), random.uniform(-1, 3), 0),
    orientation=euler_angles_to_quat([0, 0, random.uniform(0, math.pi)]),
    usd_path=assets_root_path + config["forklift"]["url"],
    semantic_label=config["forklift"]["class"],
)

# フォークリフトの正面（Y 軸方向）にランダムなオフセットでパレットを配置
forklift_tf = omni.usd.get_world_transform_matrix(forklift_prim)
pallet_offset_tf = Gf.Matrix4d().SetTranslate(Gf.Vec3d(0, random.uniform(-1.2, -1.8), 0))
pallet_pos_gf = (pallet_offset_tf * forklift_tf).ExtractTranslation()
```

### Replicator ランダム化グラフ（毎フレームの再ランダム化）

キャプチャごとに変化させたい要素は、Replicator のランダム化グラフとして**登録**（`rep.randomizer.register`）します。3 つの例が示されています：

**1. 箱の散布とマテリアル** — パレットのバウンディングボックスから散布面（透明な plane）を作り、`scatter_2d` で衝突チェック付きの散布と `rep.randomizer.materials` によるマテリアルのランダム化を行います：

```python
def scatter_boxes():
    cardboxes = rep.create.from_usd(
        assets_root_path + config["cardbox"]["url"], semantics=[("class", config["cardbox"]["class"])], count=5
    )
    with cardboxes:
        rep.randomizer.scatter_2d(scatter_plane, check_for_collisions=True)
        rep.randomizer.materials(cardbox_mats)
    return cardboxes.node

rep.randomizer.register(scatter_boxes)
```

**2. コーンの配置** — フォークリフトの OBB の底面 4 コーナーを計算し、`rep.distribution.sequence` で**定義済み候補位置のリスト**からランダムに選んで配置します。

**3. ライトのランダム化** — フォークリフトとパレットを合わせた AABB の上空（高さ 6〜7）の範囲で、ライトのパラメータと位置をランダム化します。

### トリガーの設定

登録したランダム化は、**毎フレーム**（`rep.trigger.on_frame()`）、**N フレームごと**（interval 指定）、**特定のタイミングで手動**（カスタムイベント）のいずれでもトリガーできます。

### 物理シミュレーション

ランダム化グラフの登録後、データ収集の前に、フォークリフト後方のパレットへ積まれた箱を落とす短い物理シミュレーションを実行します。これにより「きれいに整列した箱」ではなく**物理的に自然な積み上がり**が得られます。

## ステップ 4：実行と後続の学習

最後に、指定フレーム数だけランダム化とフレーム書き込みを実行し、すべてのデータの書き込み完了を待ってからアプリケーションを終了します。

!!! note "生成したデータで学習する（TAO Toolkit）"
    生成した KITTI 形式のデータは、**NVIDIA TAO Toolkit** でそのまま学習に使えます。TAO はセグメンテーション・分類・物体検出の事前学習済みモデルを提供しており、公式チュートリアルでは Detectnet V2 による物体検出が例として挙げられています。TAO は Jupyter ノートブックで学習プロセスをガイドし、spec ファイルの入力パスを合成データのフォルダ構成に合わせて書き換えるだけで、TFRecord への変換と学習が行えます。

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. **SimulationApp** としての Replicator スクリプトの実行と設定ファイルによるパラメータ化
2. **Isaac Sim API**（1 回きりの配置）と **Replicator グラフ**（毎フレームの再ランダム化）の使い分け
3. `scatter_2d`・`sequence`・ライトの**ランダム化グラフ**の登録
4. 物理シミュレーションによる自然な配置と、**KITTI / COCO 形式**での出力

## 次のステップ

- [チュートリアル 5: オブジェクトベースの合成データセット生成](05_object_based_sdg.md) - オブジェクト中心の SDG パイプラインを学びます。
