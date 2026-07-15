---
title: Synthetic Data Recorder
---

# Synthetic Data Recorder

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- **Synthetic Data Recorder** の UI 構成（Writer フレーム／Control フレーム）と使い方
- **カスタムライター**の登録と GUI からの利用
- アノテーションを画像に重ねて出力する **Data Visualization ライター**
- Replicator の**ランダマイズカメラ**を組み合わせた記録
- 記録ループの内部動作（`orchestrator.step`）

## はじめに

### 前提条件

- [チュートリアル 1: Replicator の概要](01_replicator_overview.md)を読んでいること
- アノテータが正しく動作するには、アセットに**セマンティックラベル**が付いている必要があります（このチュートリアルのサンプルステージはラベル付け済みです）

### 所要時間

約 20〜30 分

### 概要

Synthetic Data Recorder は、**コードを書かずに** GUI から合成データを記録できるエクステンションです。既定では **BasicWriter** を使って主要なアノテータのデータを記録でき、[カスタムライター](https://docs.omniverse.nvidia.com/extensions/latest/ext_replicator/custom_writer.html)を使えば任意の形式での記録も可能です。

UI ウィンドウはメニューの **Tools > Replicator > Synthetic Data Recorder** から開きます。

このチュートリアルでは次のサンプルステージを使います：

```text
https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/5.1
/Isaac/Samples/Replicator/Stage/full_warehouse_worker_and_anim_cameras.usd
```

Content ブラウザの **Isaac Sim > Samples > Replicator > Stage > full_warehouse_worker_and_anim_cameras.usd** から開くか、上の URL をパスフィールドに貼り付けて読み込みます。

![サンプルステージ](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_replicator_tut_gui_sd_recorder_stage.jpg)

このステージには**セマンティックアノテーションと複数のカメラが設定済み**で、一部のカメラはシミュレーション実行中にシーン内を動くアニメーション付きです。

## ステップ 1：UI の構成を理解する

レコーダーは大きく 2 つの部分に分かれています：

| フレーム | 内容 |
|---|---|
| **Writer フレーム** | センサー・データ・出力のパラメータ（Render Products / Parameters / Output / Config） |
| **Control フレーム** | 記録の開始・停止・一時停止と、記録フレーム数などのパラメータ |

![レコーダーウィンドウ](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_replicator_tut_gui_sd_recorder_window.jpg)

### Writer フレーム

**Render Products** — **Add New Render Product** ボタンでレンダープロダクト（記録対象のカメラ＋解像度の組）のリストを作ります。既定では、アクティブなビューポートカメラがカメラパスとして追加されます。Stage でカメラを選択した状態なら、選択したカメラが追加されます。同じカメラパスを異なる解像度で複数登録することもでき、各エントリの値は入力フィールドで手動編集できます。

![Render Products](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_replicator_tut_gui_sd_recorder_rp.jpg)

**Parameters** — 既定の組み込みライター（**BasicWriter**）とカスタムライターを選択できます。既定ライターのパラメータ（主にアノテータ）はチェックボックスで選びます。カスタムライターのパラメータは事前にわからないため、必要なパラメータをすべて含む **JSON ファイル**として用意し、**Parameters Path** にパスを入力します。

![Writer パラメータ](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_replicator_tut_gui_sd_recorder_writer_params.jpg)

**Output** — データの保存先ディレクトリと、今回の記録のフォルダ名を指定します。フォルダ名が衝突する場合は自動的に連番が付きます。**Use S3** を有効にして必要事項を入力すれば S3 バケットへの書き込みにも対応します（AWS 認証情報の設定が必要。S3 書き込み時はフォルダの連番命名は使えず Timestamp 固定になります）。

**Config** — GUI のライター設定状態を JSON 設定ファイルとして保存・読み込みできます。既定では、最後に使った設定状態が読み込まれます。

![Output と Config](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_replicator_tut_gui_sd_recorder_out_conf.jpg)

### Control フレーム

| 項目 | 動作 |
|---|---|
| **Start** | 選択したパラメータでライターを作成し、記録を開始 |
| **Stop** | 記録を停止してライターをクリア |
| **Pause / Resume** | ライターをクリアせずに一時停止／再開 |
| **Number of Frames** | 記録するフレーム数。到達すると自動停止。`0` なら Stop を押すまで無限に記録 |
| **RTSubframes** | 1 フレームごとに追加でレンダリングするサブフレーム数 |
| **Control Timeline** | レコーダーと連動してタイムラインも開始・停止・一時停止・再開する |
| **Verbose** | 詳細ログ（開始・停止・記録フレーム数などのイベント）を出力 |

![Control フレーム](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_replicator_tut_gui_sd_recorder_control.jpg)

!!! note "RTSubframes はいつ増やすか"
    ランダム化したマテリアルの読み込みが間に合わない場合や、オブジェクトのテレポートによる残像（ゴースト）などの時間方向のレンダリングアーティファクトがある場合は、**RTSubframes** を増やします。1 フレームにつき複数のサブフレームをレンダリングするため品質が向上しますが、フレームあたりのレンダリング時間は長くなります。暗い照明条件での品質改善にも有効です。

ここまでの設定で **Start** を押せば、倉庫シーンの合成データ（既定では RGB など選択したアノテータ）が出力ディレクトリに記録されます。

## ステップ 2：カスタムライターを使う

独自のデータ形式に対応するには、カスタムライターを登録して GUI から読み込みます。ここでは `MyCustomWriter` というカスタムライターを **Script Editor** で登録し、レコーダーから使えるようにします：

```python
import numpy as np
from omni.replicator.core import AnnotatorRegistry, BackendDispatch, Writer, WriterRegistry

class MyCustomWriter(Writer):
    def __init__(
        self,
        output_dir,
        rgb = True,
        normals = False,
    ):
        self.version = "0.0.1"
        self.backend = BackendDispatch({"paths": {"out_dir": output_dir}})
        self.annotators = []
        if rgb:
            self.annotators.append(AnnotatorRegistry.get_annotator("rgb"))
        if normals:
            self.annotators.append(AnnotatorRegistry.get_annotator("normals"))
        self._frame_id = 0

    def write(self, data: dict):
        for annotator in data.keys():
            # レンダープロダクトが複数ある場合、データはサブフォルダに保存される
            annotator_split = annotator.split("-")
            render_product_path = ""
            multi_render_prod = 0
            if len(annotator_split) > 1:
                multi_render_prod = 1
                render_product_name = annotator_split[-1]
                render_product_path = f"{render_product_name}/"

            # rgb
            if annotator.startswith("rgb"):
                if multi_render_prod:
                    render_product_path += "rgb/"
                filename = f"{render_product_path}rgb_{self._frame_id}.png"
                print(f"[{self._frame_id}] Writing {self.backend.output_dir}/{filename} ..")
                self.backend.write_image(filename, data[annotator])

            # 法線
            if annotator.startswith("normals"):
                if multi_render_prod:
                    render_product_path += "normals/"
                filename = f"{render_product_path}normals_{self._frame_id}.png"
                print(f"[{self._frame_id}] Writing {self.backend.output_dir}/{filename} ..")
                colored_data = ((data[annotator] * 0.5 + 0.5) * 255).astype(np.uint8)
                self.backend.write_image(filename, colored_data)

        self._frame_id += 1

    def on_final_frame(self):
        self._frame_id = 0

WriterRegistry.register(MyCustomWriter)
```

パラメータは JSON ファイル（`my_params.json`）として用意し、Parameters Path に指定します：

```json
{
    "rgb": true,
    "normals": true
}
```

![カスタムライターの設定](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_replicator_tut_gui_sd_recorder_custom_writer.jpg)

## ステップ 3：Data Visualization ライター

**Data Visualization ライター**は、アノテーションデータを**レンダリング画像の上に重ねて描画**するカスタムライターです。データセットの中身を目視確認したいときに便利です。実装は `/isaacsim.replicator.writers/python/scripts/writers/data_visualization_writer.py` にあり、`from isaacsim.replicator.writers import DataVisualizationWriter` で import できます。

Parameters フレームでこのカスタムライターを選択し、パラメータを JSON（例：`my_data_visualization_params.json`）で渡します：

```json
{
    "bounding_box_2d_tight": true,
    "bounding_box_2d_tight_params": {
        "background": "rgb",
        "outline": "green",
        "fill": null
    },
    "bounding_box_2d_loose": true,
    "bounding_box_2d_loose_params": {
        "background": "normals",
        "outline": "red",
        "fill": null
    },
    "bounding_box_3d": true,
    "bounding_box_3d_params": {
        "background": "rgb",
        "fill": "blue",
        "width": 2
    }
}
```

出力されるデータの例：

![Data Visualization ライターの出力](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_replicator_tut_gui_sd_recorder_datavis_writer.jpg)

対応アノテータは bounding_box_2d_tight / bounding_box_2d_loose / bounding_box_3d、背景は rgb / normals です。その他のパラメータはクラスの docstring を参照してください。

## ステップ 4：Replicator のランダマイズカメラと組み合わせる

Replicator のランダム化を記録に活用するには、レコーダーを開始する**前に** Script Editor でランダマイズカメラを作成しておきます。この例では、フレームごとに位置がランダム化され、常に段ボール箱を注視するカメラを Replicator API で作ります：

```python
import omni.replicator.core as rep

camera = rep.create.camera()
with rep.trigger.on_frame():
    with camera:
        rep.modify.pose(
            position=rep.distribution.uniform((-5, 5, 1), (-1, 15, 5)),
            look_at="/Root/Warehouse/SM_CardBoxA_3",
        )
```

このカメラをレンダープロダクトとしてレコーダーに追加すると、記録の各フレームでカメラが指定パラメータでランダム化されます。

![ランダマイズカメラ](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_replicator_tut_gui_sd_recorder_rep_cam.jpg)

## 記録ループの内部動作

レコーダーの実装は `/isaacsim.replicator.synthetic_recorder/isaacsim/replicator/synthetic_recorder/synthetic_recorder.py` にあり、記録処理には `orchestrator.step(rt_subframes, pause_timeline, delta_time)` 関数を使っています。この関数は、レンダラーの「処理中のフレーム（frames in flight）」を待つことで、記録フレームとステージの同期を保証します。UI との統合には非同期版の `step_async` が使われます：

```python
while self._current_frame < num_frames:
    timeline = omni.timeline.get_timeline_interface()

    if self.control_timeline and not timeline.is_playing():
        timeline.play()
        timeline.commit()

    await rep.orchestrator.step_async(rt_subframes=self.rt_subframes, delta_time=None, pause_timeline=False)

    self._current_frame += 1
```

この記録ループは、シミュレーションやアニメーションのような**動的なシーン**ではタイムラインを進めながら、**静的なキャプチャ**ではタイムラインを進めずに動作させることができ、視点のランダム化・照明条件の調整・オブジェクトの再配置といったシナリオの記録に対応できます。

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. Synthetic Data Recorder の **Writer / Control フレーム**の全パラメータ
2. **カスタムライター**の登録と JSON パラメータでの利用
3. **Data Visualization ライター**によるアノテーションの重畳出力
4. **ランダマイズカメラ**との組み合わせ
5. `orchestrator.step` による記録ループの内部動作

## 次のステップ

- [チュートリアル 3: Getting Started スクリプト](03_getting_started_scripts.md) - スクリプトベースの SDG ワークフローの基礎を学びます。
