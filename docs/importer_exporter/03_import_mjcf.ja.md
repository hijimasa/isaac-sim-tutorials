---
title: MJCF インポート
---

# MJCF インポート

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- MJCF（MuJoCo XML）モデルを Isaac Sim にインポートして USD に変換する方法
- GUI からの対話的なインポート手順
- Python API（`MJCFImporter`）によるプログラム的なインポート手順
- スタンドアロンスクリプトによる一括変換
- インポート後のアーティキュレーション調整の指針と既知の問題

## はじめに

### 前提条件

- Isaac Sim のクイックチュートリアル（基本操作）を完了していること

### 所要時間

約 5〜10 分

### 概要

このチュートリアルでは、MJCF 形式のモデルファイルを Isaac Sim にインポートし、USD 形式に変換する方法を学びます。GUI からの対話的なインポート、Script Editor を使った Python API によるインポート、ターミナルからのスタンドアロンスクリプトによる一括変換の 3 つの方法を解説します。

!!! note "MJCF とは"
    MJCF（MuJoCo XML Format）は、物理シミュレータ **MuJoCo** で使われるモデル記述形式です。URDF と同様に XML でロボットのボディ（剛体）とジョイントを記述しますが、閉ループ構造やアクチュエータ・センサーの定義など、URDF より表現力の高い項目を持ちます。強化学習の研究では MuJoCo 用に作られたモデル資産が多く存在するため、MJCF を直接インポートできると既存資産をそのまま Isaac Sim に持ち込めます。

!!! note "Isaac Sim 6.0 での MJCF インポーターの変更点"
    URDF インポーターと同様に、MJCF インポーターも 6.0 でメジャーアップデートされました。インポートされたアセットには Isaac Sim Robot Schema と Newton 物理エンジン互換のスキーマが適用され、インポートオプションに **Robot Type / Base Type** の選択が追加されています。また、Python からのインポートは Kit コマンド（`MJCFCreateImportConfig` / `MJCFCreateAsset`）に代わって `MJCFImporter` クラスが標準になりました。

## ステップ 1：GUI でのインポート

ここでは、MJCF インポーターエクステンションに同梱されているアリ型モデル（`nv_ant.xml`）をインポートします。

### 1-1. エクステンションの確認

MJCF インポーター（`isaacsim.asset.importer.mjcf`）は通常、Isaac Sim の起動時に自動的にロードされ、**File > Import** メニューから利用できます。もしファイル選択ダイアログのインポート形式に MJCF ファイルが表示されない場合は、**Window > Extensions** を開いて `isaacsim.asset.importer.mjcf` と `isaacsim.asset.importer.mjcf.ui` の両エクステンションを有効化してください。

### 1-2. サンプル MJCF の場所を確認する

`nv_ant.xml` は MJCF インポーターエクステンション自体に同梱されています。場所は次の手順で確認できます：

1. **Window > Extensions** で `isaacsim.asset.importer.mjcf` を検索します。
2. **AUTOLOAD** の横にあるフォルダアイコンをクリックすると、エクステンションのインストール先フォルダが開きます。
3. その中の `/data/mjcf` に `nv_ant.xml` があります。

### 1-3. ファイルを選択してインポートする

1. **File > Import** でファイル選択ダイアログを開き、`nv_ant.xml` を選択します。
2. ファイルを選択すると、ダイアログ右側に **Options** ペインが表示されます。必要に応じて変更します（既定のままでも構いません）。主な項目は **USD Output**（保存先）、**Robot Type** / **Base Type**（ロボットスキーマと固定方法）、**Import Scene**（MJCF のシミュレーション設定も取り込むか）、**Merge Mesh**、**Collision From Visuals** / **Collision Type**、**Allow Self-Collision** です。各オプションの詳細は公式の [MJCF Importer Extension](https://docs.isaacsim.omniverse.nvidia.com/latest/importer_exporter/ext_isaacsim_asset_importer_mjcf.html) ドキュメントの Import Options を参照してください。

    ![MJCF インポートオプション](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_6.0_full_ext-isaacsim.asset.importer.mjcf-3.0.0_user_interface.png)

3. **Import** ボタンをクリックすると、URDF のときと同様に**変換後の USD の保存先を確認するダイアログ**が表示されます。**Yes** をクリックするとロボットがステージに追加されます。

!!! warning "確認ダイアログが他のウィンドウの背後に隠れることがある"
    [URDF インポート](01_import_urdf.md)と同様に、この確認ダイアログが他のウィンドウの背後に隠れて、アプリがフリーズしたように見えることがあります。Import ボタンを押した後に操作できなくなった場合は、手前のウィンドウを移動して隠れているダイアログに応答してください。

    ![インポートされたアリ型ロボット](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_6.0_full_ext-isaacsim.asset.importer.mjcf-3.0.0_user_interface_ant.png)

## ステップ 2：Python API によるインポート

GUI と同じことを Python スクリプトでも実行できます。Isaac Sim 6.0 では `MJCFImporter` / `MJCFImporterConfig` クラスを使います。

1. **Window > Script Editor** で Script Editor を開きます。
2. 以下のコードを Script Editor にコピーします：

```python
import isaacsim.core.experimental.utils.stage as stage_utils
import omni.usd
from isaacsim.asset.importer.mjcf import MJCFImporter, MJCFImporterConfig
from pxr import Gf, PhysicsSchemaTools, Sdf, UsdLux, UsdPhysics

# 新しいステージを作成
omni.usd.get_context().new_stage()

# エクステンションのインストール先パスを取得
ext_manager = omni.kit.app.get_app().get_extension_manager()
ext_id = ext_manager.get_enabled_extension_id("isaacsim.asset.importer.mjcf")
extension_path = ext_manager.get_extension_path(ext_id)

# インポート設定を作成
import_config = MJCFImporterConfig(mjcf_path=extension_path + "/data/mjcf/nv_ant.xml")

# MJCF をインポート
importer = MJCFImporter(import_config)
output_usd_path = importer.import_mjcf()

# 変換された USD を現在のステージとして開く
result, stage = stage_utils.open_stage(output_usd_path)

# 物理シーンを作成
scene = UsdPhysics.Scene.Define(stage, Sdf.Path("/physicsScene"))

# 重力を設定
scene.CreateGravityDirectionAttr().Set(Gf.Vec3f(0.0, 0.0, -1.0))
scene.CreateGravityMagnitudeAttr().Set(9.81)

# ライトを追加
distantLight = UsdLux.DistantLight.Define(stage, Sdf.Path("/DistantLight"))
distantLight.CreateIntensityAttr(500)
```

3. **Run**（Ctrl + Enter）をクリックすると、アリ型ロボットがインポートされます。

### コードのポイント

| クラス／メソッド | 説明 |
|---|---|
| `MJCFImporterConfig` | インポート設定。`mjcf_path`（入力）のほか、`usd_path`（出力先）、`fix_base`（`None` = Source / `True` = Fixed / `False` = Mobile）、`merge_mesh`、`robot_type` などを指定できる |
| `MJCFImporter` | 設定を受け取ってインポートを実行するクラス |
| `importer.import_mjcf()` | 変換を実行し、生成された USD ファイルのパスを返す |
| `stage_utils.open_stage()` | 生成された USD を現在のステージとして開く（`isaacsim.core.experimental.utils.stage`） |

!!! note "旧 API（MJCFCreateImportConfig / MJCFCreateAsset コマンド）からの移行"
    Isaac Sim 5.x までのチュートリアルで使われていた `omni.kit.commands.execute("MJCFCreateImportConfig")` / `MJCFCreateAsset` の Kit コマンドベースの方法に代わって、6.0 では上記の `MJCFImporter` クラスが標準の方法になりました。なお、旧サンプルにあった重力値 `981.0`（ステージ距離単位がセンチメートルであることを前提とした値）も、現在の公式サンプルではメートル単位の `9.81` に修正されています。

!!! note "地面がないので落下します"
    このサンプルコードは物理シーンと重力を設定しますが、**地面（Ground Plane）は作成しません**。そのままシミュレーションを再生するとロボットは落下し続けます。動作を確認したい場合は、メニューの **Create > Physics > Ground Plane** で地面を追加してから再生してください。

## ステップ 3：スタンドアロンスクリプトによるインポート

Isaac Sim の GUI を開かずに、ターミナルから MJCF を USD に一括変換することもできます。Isaac Sim のインストールルートで次を実行します：

```bash
./python.sh standalone_examples/api/isaacsim.asset.importer.mjcf/mjcf_import.py --mjcf /path/to/nv_ant.xml --usd-path /path/to/output --merge-mesh
```

主な引数は次のとおりです（すべての引数はスクリプトの `--help` で確認できます）：

| 引数 | 説明 |
|---|---|
| `--mjcf` | MJCF ファイル（`.xml`）またはディレクトリのパス。ディレクトリを渡すと中の MJCF をまとめて変換する |
| `--usd-path` | 変換した USD の出力先ディレクトリ |
| `--robot-type` | ロボットスキーマの Robot Type（Default / End Effector / Manipulator / Humanoid / Wheeled / Holonomic / Quadruped / Mobile Manipulators / Aerial。既定は Default） |
| `--import-scene` | MJCF のシミュレーション設定もあわせて取り込む（既定：True） |
| `--merge-mesh` | メッシュを結合して最適化する |
| `--collision-from-visuals` / `--collision-type` | ビジュアルメッシュからのコリジョン生成とその形状の種類 |
| `--allow-self-collision` | 自己衝突を許可する |
| `--fix-base` / `--no-fix-base` | ベース固定の 3 択指定（省略時は MJCF の記述のまま） |
| `--link-density` | 質量未定義のリンクに適用する密度（kg/m³） |
| `--override-gain-type` / `--override-bias-type` | MuJoCo アクチュエータの gain / bias タイプの上書き（例：`"fixed"` / `"affine"`） |
| `--override-gain-prm` / `--override-bias-prm` | MuJoCo アクチュエータの gain / bias パラメータ配列の上書き（最大 10 要素） |
| `--test` | 同梱の `nv_ant.xml` を一時ディレクトリに変換して動作確認する |

## インポート後の調整

ロボットはステージにインポートされた時点でシミュレーションに使用できます。インポート後のアセットには、センサーの追加、マテリアルの変更、ジョイントドライブや各種設定の更新といった変更を加えることで、より安定したシミュレーションを実現できます。

ロボットはシミュレーション内では**アーティキュレーション**として扱われます。アーティキュレーションのチューニングについては、公式の Articulation Stability Guide のほか、[ロボットセットアップ チュートリアル 11: ジョイントドライブゲインの調整](../robot_setup/11_joint_tuning.md)も参考にしてください。

## 既知の問題：多自由度ジョイントの変換

USD では、ジョイントは 2 つの剛体間の**運動学的拘束**として定義され、ジョイントを作成すると自由度（DOF）はそのジョイントの軸のみに制限されます（例：回転ジョイントは 1 DOF）。

一方 MuJoCo では、ジョイントは**自由度そのもの**として定義され、複数のジョイントを組み合わせて多自由度を表現できます（例：X 軸回転＋ Y 軸回転で 2 自由度の関節）。これを USD でそのまま表現すると、同じ 2 ボディ間に複数のジョイントが定義されて運動学的ループとなり、過拘束になってしまいます。

このため MJCF インポーターは、同じボディペア間の多自由度ジョイントを、**PhysX バリアントでは単一の D6 ジョイントに自動変換**します。一方、physics および mujoco / newton バリアントでは元の 1 自由度ずつのジョイントが保持されます。この違いにより、**mujoco 用と physx 用のアセットは相互にそのまま流用できません**。

すべての自由度を保持してこの変換を避けたい場合は、MJCF を編集して親子ボディの間に**質量ゼロのダミーリンク**を挿入し、多自由度ジョイントを中間エッジごとの 1 自由度ジョイントに分割してください（例：ボディ A-B 間の 2 つの回転ジョイント → A-ダミー間の回転ジョイント＋ダミー-B 間の回転ジョイント）。

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. **GUI** による MJCF ファイルのインポート（アリ型ロボットの例）
2. **Python API**（`MJCFImporter` / `MJCFImporterConfig`）によるインポートと物理シーンのセットアップ
3. **スタンドアロンスクリプト**（`mjcf_import.py`）による一括変換
4. インポート後の**アーティキュレーション調整**の指針と**多自由度ジョイント**に関する既知の問題

### さらに学ぶには

インポートオプションの詳細については、公式の [MJCF Importer Extension](https://docs.isaacsim.omniverse.nvidia.com/latest/importer_exporter/ext_isaacsim_asset_importer_mjcf.html) ドキュメントを参照してください。ジョイントゲインの調整には Gain Tuner エクステンションも利用できます。

## 次のステップ

- [チュートリアル 4: 一般 3D モデルのインポート](04_general_3d_model_importer.md) - OBJ / FBX などの一般的な 3D モデルのインポートと物理プロパティの設定方法を学びます。
