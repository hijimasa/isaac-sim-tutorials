---
title: 把持の合成データ生成
---

# 把持の合成データ生成（Grasping SDG）

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- `isaacsim.replicator.grasping` エクステンションの**コンポーネントとデータフロー**
- **Grasping SDG UI** による把持生成ワークフローの設定と実行
- グリッパーのプロパティ・ジョイント状態・**多段階の把持フェーズ**の定義
- 対象オブジェクトと**把持姿勢サンプリング**（アンチポーダルサンプラー）の設定
- **物理ベースの把持評価**の実行と結果の解釈
- **YAML 設定ファイル**による構成の保存・読み込み・共有

## はじめに

### 前提条件

- 物理シミュレーションの基礎とグリッパーのリギング（ドライブジョイント）の理解
- 公式の Grasp Editor チュートリアルに目を通しておくと、把持定義の考え方の土台になります

!!! tip "libspatialindex が必要"
    把持サンプラーは `libspatialindex` ライブラリを必要とします。関連する警告が出る場合はインストールしてください（Ubuntu の例：`sudo apt-get install libspatialindex-dev`）。

### 所要時間

約 40 分

### 概要

Grasping SDG は、**グリッパーとオブジェクトのペアに対する把持姿勢の探索と評価を自動化**するツールです。生成したデータは、把持計画モデル（グリッパーがどこをどう掴めば成功するか）の学習に使えます。ワークフローは次の 5 段階です：

1. **設定** — グリッパー・対象オブジェクト・探索／評価パラメータの定義
2. **把持姿勢サンプリング** — アルゴリズム（アンチポーダルサンプラーなど）で候補姿勢群を生成
3. **把持実行フェーズ** — 候補ごとに「プリグラスプへ移動 → 指を閉じる → 持ち上げる」のような多段階の動作（Grasp Phases）をシミュレート
4. **物理ベースの評価** — 各フェーズを物理エンジンで実行し、成否や接触力・オブジェクト変位などを記録（現状はグリッパー状態を結果として保存し、そこから評価します）
5. **データログと管理** — 成功した把持とパラメータを記録し、全体を YAML に保存して再現・バッチ処理を可能に

中心となる Python API は **GraspingManager** クラスで、UI はこのパイプラインを直感的に設定・実行するためのものです。UI は **Tools > Replicator > Grasping** で開きます。

このチュートリアルでは、設定済みのグリッパーと把持対象 3 オブジェクト（リジッドボディ＋コライダー付き、初期は重力無効）を含むサンプルステージを使います：**Isaac Sim > Samples > Replicator > Stage > sdg_grasping_xarm.usd**

![Grasping のステージ](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_replicator_tut_gui_grasping_stage.jpg)

## UI の構成

![Grasping UI](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_replicator_tut_gui_grasping_ui_window.jpg)

### Gripper セクション

グリッパーの定義を行います：

- **Path** — グリッパーのルートプリムの USD パス（例：`/World/Robot/gripper_base`）
- **Joints** — グリッパー選択後、関節がリスト表示されます。把持フェーズ中に制御するジョイントの**選択（ドライブジョイントであること）**、各ジョイントの**プリグラスプ位置**（通常は開いた状態）の設定、全ジョイント／ドライブ（非ミミック）ジョイントの表示切り替えができます
- **Grasp Phases** — 1 回の把持を構成する**一連の動作**（例：「Open」「Close」）を定義します。フェーズごとに、対象ジョイントの目標位置、物理ステップの delta time（dt）、実行するシミュレーションステップ数を指定します。フェーズは並べ替え・削除・**個別のデバッグ実行**が可能です。プリグラスプ位置で十分に準備できている場合（完全に開いているなど）、明示的な「Open」フェーズは不要です

### Object セクション

対象オブジェクトの指定と、把持姿勢の生成方法を設定します：

- **Path** — 対象オブジェクトの USD パス
- **Grasp Pose Sampler** — 候補姿勢の生成アルゴリズムの設定。主に**アンチポーダルサンプラー**（`sampler_utils.py` に実装）を使います

!!! note "アンチポーダル把持とは"
    オブジェクトの**反対側の 2 点で挟む**把持で、平行グリッパーで安定しやすい基本形です。サンプラーの主なパラメータ：

    | パラメータ | 意味 |
    |---|---|
    | Number of orientations per grasp axis | 主把持軸まわりの回転バリエーション数 |
    | Gripper standoff distance | 接近時の TCP（または指先）とオブジェクト表面の距離。早すぎる衝突の防止に重要 |
    | Maximum gripper aperture | グリッパーの最大開き幅（広すぎる把持候補の除外） |
    | Alignment axes | オブジェクトの特徴や把持線に合わせるグリッパーのローカル軸 |
    | Gripper approach direction | 接近方向のベクトル |
    | Lateral perturbation (sigma) | 把持軸に対して横方向への接触点のランダムなずらし |
    | Random seed | 再現可能なサンプリングのためのシード |

- **Grasp Poses** — 生成した候補姿勢の管理（生成数の指定・クリア・ビューポートでの可視化とサイクル確認）
- **Trimesh** — サンプラーが内部で使う三角形メッシュのデバッグ可視化

![生成された把持姿勢](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_replicator_tut_viewport_grasping_poses.jpg)

!!! tip
    グリッパーの開き幅やスタンドオフ距離の値を決めるには、Measure Tool が便利です。

### Workflow セクション

設定を使って実際の評価を回します。システムはまずグリッパーの初期姿勢を保存し、評価対象の各把持姿勢について定義済みの把持フェーズを物理シミュレーションで順に実行し、結果を記録します。

- **Number of Grasps Samples** — 評価する姿勢数（`-1` で全候補）
- **Output Path** — 評価結果（YAML など構造化形式）の保存先
- **Overwrite Results** — 既存結果の上書き可否（無効なら連番で新規作成）
- **Start Workflow** — 評価の開始

### Simulation セクション

- **Render each simulation step** — フェーズ内の物理ステップごとにビューポートを更新するか。**無効にすると大規模データセットの評価が大幅に高速化**します
- **Simulate using timeline** — メインのタイムラインを進める方式か、物理シーンを直接ステップする方式かの選択。直接ステップは高速評価向き、タイムライン方式は実際のロボットアプリケーションの動作に近い挙動です
- **Isolated physics scene** — 専用の Physics Scene プリムを指定すると、メインステージの他の物理設定・動的オブジェクトから隔離して評価でき、一貫性・再現性が向上します

### Config セクション

セットアップ全体を YAML に保存・読み込みできます。**Config Includes** で保存対象（Gripper Path / Joint Pregrasp States / Grasp Phases / Object Path / Sampler Parameters / 生成済み Grasp Poses）を選択でき、モジュール的な構成管理が可能です。

## コード例（GraspingManager API）

UI で設定できる一連の手順（ステージを開く → GraspingManager のセットアップ（設定ファイルの読み込み可）→ 把持姿勢の生成 → 物理シミュレーションでの評価 → 結果の保存）は、**GraspingManager API** でプログラム的にも実行できます。バッチ処理や大きなワークフローへの統合に向いています。

```bash
./python.sh standalone_examples/api/isaacsim.replicator.grasping/grasping_workflow_sdg.py
```

Script Editor 版のコードも公式ページに掲載されています。

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. Grasping SDG の**5 段階ワークフロー**（設定→サンプリング→フェーズ実行→物理評価→ログ）
2. **UI の 5 セクション**（Gripper / Object / Workflow / Simulation / Config）の設定項目
3. **アンチポーダルサンプラー**のパラメータの意味
4. **YAML 設定**による再現性の確保と **GraspingManager API** によるバッチ実行

## 次のステップ

- [チュートリアル 16: MobilityGen によるデータ生成](16_mobility_gen.md) - モバイルロボットのデータ収集ツールを学びます。
