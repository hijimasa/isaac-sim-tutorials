---
title: オブジェクトベースの合成データセット生成
---

# オブジェクトベースの合成データセット生成

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- **コリジョンウォールで囲んだ作業エリア**の中に、ラベル付きアセットとディストラクタを浮遊させるオブジェクト中心 SDG のセットアップ
- リジッドボディ・コライダーの**プログラム的な付与**と、物理シーンのカスタム設定
- **カスタムランダマイザ**（バウンス・カメラ姿勢・速度）と Replicator ランダマイザの併用
- **PathTracing とモーションブラー**によるキャプチャ
- レンダープロダクトのオン／オフによる**パフォーマンス最適化**
- **PoseWriter** による DOPE / CenterPose 形式の出力

## はじめに

### 前提条件

- [チュートリアル 4: シーンベースの合成データセット生成](04_scene_based_sdg.md)を完了していること
- USD / Isaac Sim API によるステージ操作、リジッドボディダイナミクスの基本

### 所要時間

約 40〜50 分

### 概要

「オブジェクトベース」の SDG は、シーンの現実感よりも**対象オブジェクトの見え方の多様性**を重視するアプローチです。姿勢推定（DOPE、CenterPose）や物体検出モデルの学習データに向いています。

スクリプトは、**見えないコリジョンウォールで閉じたエリア**にラベル付きアセットとディストラクタ（学習対象ではない妨害オブジェクト）をスポーンし、複数のカメラ視点からシーンをキャプチャします。カメラ姿勢のランダム化、オブジェクトへのランダム速度の適用、カスタムイベントによるシーンのランダム化を組み合わせ、ランダマイザは Replicator ベースとカスタム Isaac Sim / USD API ベースの両方を特定のタイミングでトリガーします。

![オブジェクトベース SDG](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isaac_tutorial_replicator_object_based_sdg.jpg)

## ステップ 1：実行してみる

メインスクリプトは `<install_path>/standalone_examples/replicator/object_based_sdg/object_based_sdg.py`、ヘルパーは `object_based_sdg_utils.py` です：

```bash
./python.sh standalone_examples/replicator/object_based_sdg/object_based_sdg.py
```

カスタム設定ファイルは `--config` で渡します（サンプルは `object_based_sdg/config/*`。`object_based_sdg_config.yaml` は **BasicWriter** でラベル付きアセットとメッシュディストラクタを拡張した例、`object_based_sdg_dope_config.yaml` と `object_based_sdg_centerpose_config.yaml` はそれぞれ **PoseWriter の DOPE / CenterPose** 形式の出力例です）：

```bash
./python.sh standalone_examples/replicator/object_based_sdg/object_based_sdg.py \
    --config standalone_examples/replicator/object_based_sdg/config/object_based_sdg_dope_config.yaml
```

## ステップ 2：設定パラメータを理解する

主な設定パラメータ：

| パラメータ | 説明 |
|---|---|
| `launch_config` | レンダラーやヘッドレスモードなどの起動設定 |
| `env_url` | 読み込む環境の URL。空なら空のステージを新規作成 |
| `working_area_size` | オブジェクトを配置するエリアのサイズ（幅・奥行き・高さ）。周囲は見えないコリジョンウォールで囲まれる |
| `num_frames` / `num_cameras` | キャプチャフレーム数とカメラ数（総エントリ数は num_frames × num_cameras） |
| `disable_render_products_between_captures` | True ならキャプチャ間でレンダープロダクトを無効化してリソースを節約 |
| `simulation_duration_between_captures` | キャプチャ間に実行するシミュレーション時間 |
| `camera_properties_kwargs` | カメラプロパティ（`focal_length`、`focus_distance`、`f_stop`、`clipping_range`。6.0 でスネークケース表記に変更） |
| `writer_type` / `writer_kwargs` | 使用するライター（PoseWriter、BasicWriter など）とその初期化パラメータ |
| `labeled_assets_and_properties` | **学習対象**のラベル付きアセットのリスト（プロパティ付き） |
| `shape_distractors_types` / `_num` | 形状ディストラクタの種類（capsule / cone / cylinder / sphere / cube）と数 |
| `mesh_distractors_urls` / `_num` | メッシュディストラクタの URL リストと数 |

!!! note "ディストラクタとは"
    ディストラクタは、**学習対象ではない**が、シーンを雑然とさせてモデルの頑健性を高めるためのオブジェクトです。ラベルは付けず、遮蔽や背景ノイズの役割を果たします。

## ステップ 3：ヘルパー関数とカスタムランダマイザ

スクリプトは、一般的な操作に **`rep.functional` API を直接使用**します：Transform の設定は `rep.functional.modify.pose`、アセットやカメラの作成は `rep.functional.create.reference` / `rep.functional.create.camera`、物理プロパティの付与は `rep.functional.physics.apply_rigid_body` / `apply_collider` です（独自の Transform ヘルパー関数は不要になりました）。ユーティリティモジュールには、**ランダムな位置・回転・スケール値の生成**や**球面上のランダム姿勢の生成**、**コライダーのみの付与**（静的オブジェクト用）などのヘルパー関数が残っています。セマンティックラベル関連は `isaacsim.core.experimental.utils.semantics` の `add_labels` / `remove_all_labels` / `upgrade_prim_semantics_to_labels` を使います。

カスタムランダマイザの代表例：

- **バウンスランダマイザ**（Isaac Sim / USD ベース）— 底面コリジョンボックスの上の「バウンスエリア」に重なったオブジェクトを毎物理ステップ検出し、ほぼ上向きのランダム速度を与えて浮遊させ続けます。
- **カメラランダム化** — ランダムに選んだラベル付きアセットを、ランダムな距離＋中心を外すオフセットで注視します。カメラのコライダーを有効にした場合は、数フレームのシミュレーションで重なったオブジェクトを押し出します。
- **ターゲットへの速度付与** — 作業エリア中心に向かうランダムな大きさの速度を与え、オブジェクトが散らばりきらず、ときどき中心に集まってシーンが雑然とするようにします。
- **球状ライトのランダム化**（Replicator ベース）— 色・色温度・強度・位置・スケールを、カスタムイベント（`rep.utils.send_og_event(event_name="randomize_lights")`）で手動トリガー。
- **形状ディストラクタの色**（Replicator ベース）— プリムパスからグラフノードを作り、組み込みの `rep.randomizer.color` でランダム化。こちらもカスタムイベントでトリガーします。

## ステップ 4：SDG ループとモーションブラー

メインのキャプチャループは、指定フレーム数だけシミュレーションを回しながら、**カスタムのフレーム間隔で**ランダム化（カメラ姿勢、中心への速度付与、ライト、色、背景ドームなど）とキャプチャをトリガーします。

**モーションブラー**のキャプチャでは、レンダーモードを **PathTracing** に設定し、動きの継続時間と合成するサブフレーム数（パストレースサンプル数）を選んでキャプチャします：

![モーションブラー](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isaac_tutorial_replicator_object_based_sdg_motion_blur.jpg)

!!! note "パフォーマンス最適化"
    キャプチャ間に多くのシミュレーションフレームを回す場合は、`disable_render_products_between_captures: True` で**キャプチャ時以外のレンダリングと処理を止める**のが効果的です。`set_render_products_updates` の `include_viewport=True` はビューポート（UI）のレンダリングも無効化します。ライブ表示は失われますが、ヘッドレスサーバーでの実行では特に有効です。

## ステップ 5：PoseWriter と出力形式

既定のライターは **PoseWriter** です（実装は `isaacsim.replicator.writers` エクステンションの `pose_writer.py`）：

| パラメータ | 説明 |
|---|---|
| `output_dir` | 出力ディレクトリ |
| `format` | 出力形式（`dope`、`centerpose` など）。None なら利用可能な全データを書き出す既定形式 |
| `use_subfolders` | True ならカメラ名ごとのサブフォルダに出力 |
| `write_debug_images` | True ならデバッグ画像（バウンディングボックスのオーバーレイなど）も出力 |
| `skip_empty_frames` | True なら空のフレームをスキップ |

## 実例：SyntheticaDETR

このパイプラインの実用例が **SyntheticaDETR** です。RT-DETR をベースに、**Isaac Sim Replicator で生成した合成データのみ**で学習された屋内物体検出ネットワークで、YCBV データセットの BOP リーダーボードで最高性能を記録しています。

- データ生成では、オブジェクトを天井から落として物理シミュレーションで安定配置させ、RGB とグラウンドトゥルース（セグメンテーション・深度・バウンディングボックス）のペアをキャプチャします。
- 3D アセットが手元にない実物体は、iPad/iPhone の **AR Code** アプリ（LiDAR＋多視点画像）で USD 形式のアセットとして取り込んで利用できます。
- モデルは [NGC カタログ](https://catalog.ngc.nvidia.com/orgs/nvidia/teams/isaac/models/synthetica_detr)で公開されており、ROS で動かす場合は Isaac ROS RT-DETR チュートリアルを参照してください。

![SyntheticaDETR のデータ生成](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isaac_tutorial_replicator_object_based_sdg_drop_table.jpg)

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. コリジョンウォールで囲んだ**オブジェクト中心の SDG シナリオ**の構成と設定パラメータ
2. **カスタムランダマイザ**（バウンス・カメラ・速度）と **Replicator ランダマイザ**（ライト・色）の併用
3. **PathTracing＋モーションブラー**のキャプチャとレンダープロダクト制御による最適化
4. **PoseWriter** による DOPE / CenterPose 形式の出力と、SyntheticaDETR という実用例

## 次のステップ

- [チュートリアル 6: Infinigen を使った環境ベースの生成](06_infinigen_sdg.md) - プロシージャル生成環境での SDG を学びます。
