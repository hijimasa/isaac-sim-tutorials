---
title: RTX センサーの配置とキャリブレーション（ISP）
---

# RTX センサーの配置とキャリブレーション（ISP）

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- `isaacsim.sensors.rtx.placement`（ISP）でカメラ配置を最適化する仕組み
- Camera Placement ツールで被覆要件に基づき最適なカメラ位置を自動決定する方法
- Camera Calibration ツールでカメラのキャリブレーションデータ（位置・向き・FOV ポリゴン）を生成する方法

## はじめに

### 前提条件

- Isaac Sim 5.1 が起動できること
- ステージ単位がメートル、Z 軸が上向きであること
- 有効な NavMesh がベイクされていること

### 所要時間

約 20〜25 分

### 概要

倉庫・小売店・病院などの屋内/閉鎖空間では、カメラ配置の最適化が、被覆範囲を確保しつつ配置コストを最小化する重要な技術です。**`isaacsim.sensors.rtx.placement`（ISP）** は、シーンレイアウトと被覆要件に基づいて**最適なカメラ位置を自動決定**します。生成カメラの詳細メタデータや、各カメラの FOV 被覆を可視化したステージレイアウトも提供し、カメラの方向・位置・FOV ポリゴン情報を `.json` に保存できます。

この拡張機能は 2 つの UI ウィンドウに分かれています。

- **Camera Placement** … 被覆要件とシーン制約に基づき、最適な姿勢でカメラを自動配置します。
- **Camera Calibration** … 位置・向き・FOV 情報を含むキャリブレーションデータを抽出・管理します。

## パート 1：Camera Placement ツール

**Tools > Sensors > Camera Placement** からアクセスします。

### 主な入力フィールド

| フィールド | 説明 |
|---|---|
| **Camera Placement Output Path** | 生成データ（`camera_info_payload.json`）の保存先。カメラパス・位置・注視点を含む |
| **Total Camera Number** | 配置するカメラの総数（`-1` で必要最小数を自動計算） |
| **Camera Height Range** | 地面からのカメラ高さの許容範囲 |
| **Camera Distance Range** | 任意の点 P からカメラを配置できる距離範囲（任意の P に対し、この範囲内の距離のカメラ C が存在することを保証） |
| **Camera Look Down Angle Range** | カメラの下向き傾き角の範囲（0°＝水平、90°＝真下） |
| **Patch Size** | 被覆推定のためステージを分割するパッチのサイズ（小さいほど詳細だが計算時間増） |
| **Ground Height** | ステージの地面の高さ |

**その他の調整パラメータ**：`Border Checking Index`（境界への近さ）、`Camera On Navmesh`（NavMesh 上のみに配置するか）、`Minimum Coverage Increase`（有効とみなす最小追加被覆）、`Limit FOV by Distance`、`Coverage Density`（各パッチを最低何台で被覆するか）、`Target Coverage Ratio`（被覆すべき全体割合）。

**ボタン**：`Place Cameras`（自動配置開始）、`Show Selected Camera Coverage`（選択カメラの被覆を色分け表示。Coverage Density が N なら N 色）、`Hide Coverage`。

### チュートリアル（フルウェアハウス）

!!! note "前提"
    ステージ単位はメートル、Z 軸が上、有効な NavMesh が必要です。`omni.anim.navigation.bundle` 拡張機能を有効化し、**Window > Navigation > Navmesh** の Bake で NavMesh をベイクしてください。

1. `isaacsim.sensors.rtx.placement` を有効化し、Camera Placement パネルを開きます。
2. Isaac Sim Full Warehouse を開き、NavMesh がベイク済みか確認します。
3. **Camera Placement Output Path** にキャッシュフォルダを設定し、**Total Camera Number** を設定します（`-1` で自動）。
4. （任意）Camera Range / Stage Processing パラメータを調整します（この例はデフォルト）。
5. **Fine-tune**：`Coverage Density` を 2（各パッチを 2 台で被覆）、`Target Coverage Ratio` を 0.99（99% 被覆）に設定します。

![配置パラメータの調整](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_full_ext-isaacsim.sensor.rtx.placement-5.0.0_gui_camera_placement_tuning_setting.png)

6. **Place Cameras** で自動配置を開始します（時間がかかります。完了後、各方向のカメラ数がコンソールに warning として出力されます）。
7. **被覆確認**：トップビューカメラに切り替え、**Show By Type > Navmesh** で NavMesh を表示。`World/Cameras` 以下の全カメラ prim を選択し、**Show Selected Camera Coverage** で被覆を可視化します（この例では 1 回被覆＝赤、2 回被覆＝緑）。

![被覆の可視化](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_full_ext-isaacsim.sensor.rtx.placement-5.0.0_gui_camera_placement_coverage_visualization.png)

8. （任意）USD を保存して、以降の SDG ワークフローにカメラ配置を残します。

## パート 2：Camera Calibration ツール

**Tools > Sensors > Camera Calibration** からアクセスします。配置済みカメラのキャリブレーションデータを生成します。

### 主な入力フィールド

| フィールド | 説明 |
|---|---|
| **Place Info** | シーンの場所（都市・建物・部屋）。`city=[名]/building=[名]/room=[名]` 形式で `calibration.json` に保存 |
| **Scene Root Prim Path** | シーンのルート prim。トップビューカメラはこの中心を注視 |
| **Floor & Ceiling Height** | 床・天井の高さ（天井高でトップビューのクリッピング範囲を調整。既定 -1） |
| **Top View Camera** | `Create` でトップビューカメラ（`Calibration_Top_Camera`）を生成。回転 [0,0,0]・正射投影・地面に垂直である必要あり |
| **Raycast Density** | レイキャスト密度（N なら N×N レイ。FOV 輪郭の詳細度。既定 100） |
| **Minimum FOV Polygon Edge Length** | ポリゴン輪郭の最小エッジ長（既定 0＝簡略化なし） |
| **Minimum Area of FOV Polygon Hole to Ignore** | 無視する FOV ポリゴンの穴の最小面積（既定 0） |
| **Output Folder Path** | 出力先 |

**ボタン**：`Create Dot Prims`（各カメラのキャリブレーションドット生成）、`Generate Calibration File`（`calibration.json` 生成。事前に Create Dot Prims が必要）、`Generate Top View Image`（トップビュー画像と `imageMetadata.json` を出力）。

### チュートリアル

!!! note "前提"
    ステージ単位はメートル、有効な NavMesh が必要です。カメラは `/World/Cameras` 以下に置き、歩行可能エリアを見られることが理想です。

1. `isaacsim.sensors.rtx.placement` を有効化し、Camera Calibration パネルを開きます。
2. **トップビューカメラの作成**：**Scene Root Prim Path** を `/Root` に設定。倉庫の天井をクリップするため **Ceiling Height** を 6 に設定（床が高さ 0 なので Floor Height は変更不要）。

    ![天井高の設定](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_full_ext-isaacsim.replicator.agent.camera_calibration-5.0.0_gui_set_ceiling_height.png)

3. **Create** をクリックし、生成されたトップビューカメラにビューポートを切り替えてフロアプランを覆っているか確認します（カメラアイコン > Cameras > Calibration_Top_Camera）。

    ![ビューポートの切り替え](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_full_ext-isaacsim.replicator.agent.camera_calibration-5.0.0_viewport_switch_viewport.png)

4. **属性の設定**：**Place Info**（例：`city=Santa Clara/building=Isaac Sim Warehouse/room=Warehouse`）、Raycast Density など（この例はデフォルト）、必要なら Create Camera View Images / Create FOV Polygon Images / Show FOV Polygon をチェック、**Output Folder Path** を設定します。
5. **Create Dot Prims** で各カメラのキャリブレーションドットを生成します（`/World/Calibration_Dots/[Camera Name]/` に各カメラ 6 個。射影行列の計算に使用）。
6. **Generate Calibration File** で `calibration.json` を生成します。対象カメラを選択するとステージで FOV を可視化できます。
7. **Generate Top View Image** で FOV ポリゴン付きトップビュー画像を出力します（`Create FOV Polygon Images` チェック時は `[Output]/Debug/fieldOfViewPolygon` に各カメラの画像）。

    ![FOV ポリゴン](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_full_ext-isaacsim.replicator.agent.camera_calibration-5.0.0_viewport_fov_polygon.png)

## まとめ

このチュートリアルでは、次の内容を学びました。

- ISP がシーンレイアウトと被覆要件からカメラ配置を最適化すること
- Camera Placement ツールで Coverage Density / Target Coverage Ratio を設定し、被覆を色分け可視化する方法
- Camera Calibration ツールでトップビューカメラを作成し、`calibration.json` と FOV ポリゴンを生成する方法

## 次のステップ

- 合成データ生成の一覧は [合成データ生成](index.md) を参照してください。
- センサー自体の詳細は [センサーチュートリアル](../sensors/index.md) を参照してください。
