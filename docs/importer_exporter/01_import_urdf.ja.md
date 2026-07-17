---
title: URDF インポート
---

# URDF インポート

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- URDF ファイルを Isaac Sim にインポートして USD に変換する方法
- インポート設定（Robot Type / Base Type、メッシュ結合、コリジョン）の構成
- コリジョンメッシュの可視化と確認方法
- 組み込みサンプル（Robotics Examples）を使ったインポートの流れ
- Python API（`URDFImporter`）によるプログラム的なインポート
- スタンドアロンスクリプトによる一括変換

## はじめに

### 前提条件

- Isaac Sim のクイックチュートリアル（基本操作）を完了していること

### 所要時間

約 10〜15 分

### 概要

このチュートリアルでは、URDF ファイルを Isaac Sim にインポートし、USD 形式に変換する方法を学びます。具体的には以下の 4 つの方法を順に解説します：

1. **GUI での直接インポート** — メニュー操作だけで URDF を読み込む基本の方法
2. **組み込みサンプルからのインポート** — Robotics Examples に用意された例で流れを体験する
3. **Python API によるインポート** — Script Editor から `URDFImporter` クラスで実行するプログラム的な方法
4. **スタンドアロンスクリプトによるインポート** — ターミナルから一括変換する方法

ROS 2 ノードから URDF（XACRO）を直接インポートする方法は、ROS 2 のインストールが前提となるため[チュートリアル 1a: ROS 2 ノードからの URDF インポート](01a_import_urdf_from_ros2.md)として独立させています。

!!! note "URDF とは / なぜ変換が必要か"
    URDF（Unified Robot Description Format）は、ROS で標準的に使われるロボット記述形式です。XML でロボットのリンク（剛体）とジョイント（関節）の構成、質量、コリジョン形状などを記述します。

    一方、Isaac Sim はシーンやロボットを **USD（Universal Scene Description）** 形式で扱います。そのため URDF のロボットを Isaac Sim で使うには、URDF → USD の**変換（インポート）**が必要です。インポートは一方向の変換であり、元の URDF ファイルが書き換えられることはありません。

    逆方向（USD → URDF）の変換は[チュートリアル 2](02_export_urdf.md)で扱います。

!!! note "Isaac Sim 6.0 での URDF インポーターの変更点"
    Isaac Sim 6.0 の URDF インポーターはメジャーアップデートされ、インポートされたアセットには [Isaac Sim Robot Schema](https://docs.isaacsim.omniverse.nvidia.com/latest/omniverse_usd/robot_schema.html) と Newton 物理エンジン互換のスキーマが適用されるようになりました。あわせてインポートオプションも再編され、**Robot Type / Base Type** の選択が追加された一方、旧バージョンにあったジョイントドライブ（Natural Frequency など）のインポート時設定は廃止され、ゲイン調整はインポート後に行う方式になっています。

## ステップ 1：GUI での直接インポート

ここでは、URDF インポーターエクステンションに同梱されている UR10 の URDF（`ur10.urdf`）をインポートします。

### 1-1. エクステンションの有効化

URDF インポーター（`isaacsim.asset.importer.urdf`）は通常、Isaac Sim の起動時に自動的にロードされます。もし読み込まれていない場合は、**Window > Extensions** を開いて `isaacsim.asset.importer.urdf` を検索し、有効化してください。

### 1-2. サンプル URDF の場所を確認する

今回使う `ur10.urdf` は、URDF インポーターエクステンション自体に同梱されています。ファイルの場所は次の手順で確認できます：

1. **Window > Extensions** で `isaacsim.asset.importer.urdf` を検索します。
2. **AUTOLOAD** の横にあるフォルダアイコンをクリックすると、エクステンションのインストール先フォルダが開きます。
3. その中の `/data/urdf/robots/ur10/urdf` に `ur10.urdf` があります。このパスをコピーしておきます。

### 1-3. ファイルを選択する

**File > Import** を開き、ファイル選択ダイアログのナビゲーションバーに先ほどコピーしたパスを貼り付けて、`ur10.urdf` を選択します。

![ロボット選択](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_6.0_full_ext-isaacsim.asset.importer.urdf-3.0.0_gui_0.png)

### 1-4. インポート設定を構成する

URDF ファイルを選択すると、ファイル選択ダイアログの右側に **Options** ペイン（インポート設定）が表示されます。UR10 の場合は以下のように設定します：

| 設定項目 | 今回の設定 | 説明 |
|---|---|---|
| **USD Output** | 既定のまま | 変換後の USD ファイルの保存先。既定では URDF と同じディレクトリになる。フォルダアイコンから変更可能 |
| **Robot Type** | 既定（`Default`）のまま | ロボットスキーマの `isaac:robotType` 属性を設定する。Default / End Effector / Manipulator / Humanoid / Wheeled / Holonomic / Quadruped / Mobile Manipulators / Aerial から選択 |
| **Base Type** | 既定（`Source`）のまま | ルートリンクの固定方法。**Source**（URDF の記述に従う・既定）／ **Fixed**（ワールドへの固定ジョイントを追加＝固定ベース）／ **Mobile**（固定ジョイントを除去＝移動ベース）の 3 択 |
| **Merge Mesh** | オン | 剛体ごとにメッシュを 1 つに結合する。USD のプリム数が減り、パフォーマンスが向上する |
| **Allow Self-Collision** | オン | ロボット自身のリンク同士の衝突判定を有効にするか |

上記以外の項目（Collision From Visuals、Collision Type、ROS Package List、Debug Mode など）は既定のままで構いません。各オプションの詳細は公式の [URDF Importer Extension](https://docs.isaacsim.omniverse.nvidia.com/latest/importer_exporter/ext_isaacsim_asset_importer_urdf.html) ドキュメントを参照してください。

![インポートオプション](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_6.0_full_ext-isaacsim.asset.importer.urdf-3.0.0_gui_1.png)

!!! warning "出力先ディレクトリの書き込み権限"
    インポート時の出力先ディレクトリには**書き込み権限が必要**です。既定の出力先は URDF ファイルと同じディレクトリになるため、エクステンション同梱のサンプルのように読み取り専用の場所にある URDF をインポートする場合は、**USD Output** を書き込み可能な場所に変更してください。

!!! note "ジョイントドライブの設定は「インポート後」に行う"
    Isaac Sim 5.x までの URDF インポーターには、インポート時にジョイントドライブを設定する **Joints & Drives** セクション（Stiffness / Natural Frequency の指定）がありましたが、**6.0 で廃止されました**。6.0 では URDF の記述から各ジョイントのドライブが自動構成され、ゲインの調整はインポート後に Property パネルや **Gain Tuner** エクステンションで行います。

    Isaac Sim のジョイントドライブは PD 制御（Stiffness / Damping）で駆動されます。値を大きくするほどジョイントは目標値に素早く追従し、動作中の振動（オシレーション）が抑えられます。一方、値を上げすぎるとシミュレーションが**数値的に不安定**になり、ジョイントや剛体が意図せず飛散・振動発散する場合があります。その場合は Physics Scene のシミュレーションタイムステップを小さくするか、値を下げて調整してください。詳しくは[ロボットセットアップ チュートリアル 11: ジョイントドライブゲインの調整](../robot_setup/11_joint_tuning.md)で解説しています。

### 1-5. インポートを実行する

**Import** ボタンをクリックすると、**URDF Confirm Path** ダイアログが表示され、変換後の USD ファイルの保存先が確認できます。**Yes** をクリックするとインポートが実行され、ロボットがステージに追加されます。

![URDF Confirm Path ダイアログ](images/01_urdf_confirm_path.png)

同じ場所に一度インポートしたことがある場合は、続けて **URDF Confirm Overwrite** ダイアログが表示されます。上書きしてよければ **Yes** をクリックします。

![URDF Confirm Overwrite ダイアログ](images/01_urdf_confirm_overwrite.png)

!!! warning "確認ダイアログが他のウィンドウの背後に隠れることがある"
    環境によっては、この確認ダイアログが**ファイル選択ウィンドウや Extensions ウィンドウの背後に隠れて表示される**ことがあります。その間はメインウィンドウ全体がクリックに反応しなくなるため、フリーズしたように見えます。Import ボタンを押した後に操作できなくなった場合は、手前のウィンドウをドラッグで移動（または閉じる）して、隠れているダイアログの **Yes / No** に応答してください。

![インポート結果](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_6.0_full_ext-isaacsim.asset.importer.urdf-3.0.0_gui_2.png)

!!! note "モバイルロボット（車輪型）をインポートする場合"
    車輪で移動するロボットの場合は、次の点を確認・調整します：

    - **Base Type** を **Mobile**（または URDF 側でベースが固定されていなければ **Source**）にする
    - インポート後、速度制御するジョイント（車輪）のドライブを **Velocity**、位置制御するジョイント（ステアリング）を **Position** に設定する
    - ドライブの強さはジョイントの **Damping** で調整する（Velocity ドライブでは Stiffness は常に 0 にします）

!!! note "トルク制御ロボット（四足歩行ロボットなど）をインポートする場合"
    脚をトルクで直接制御するロボットの場合は、次のようにします：

    - **Base Type** を **Mobile**（または **Source**）にする
    - インポート後、トルク制御するジョイント（脚）のドライブタイプを **None**、それ以外のジョイントを **Position** または **Velocity** に設定する
    - **None** ドライブのジョイントでは Stiffness / Damping は効果を持たないため、0 に設定します

## ステップ 2：コリジョンメッシュの可視化

すべてのリジッドボディがコリジョンプロパティを持つとは限らず、また、コリジョンメッシュは見た目用のビジュアルメッシュより簡略化された形状であることが一般的です。意図した通りにコリジョンが設定されているかは、インポート後に目視で確認しておくと安心です。

ビューポートでコリジョンメッシュを可視化する手順：

1. ビューポート左上の**目のアイコン**をクリックします。
2. **Show By Type** にカーソルを合わせます。
3. **Physics** にカーソルを合わせます。
4. **Colliders** にカーソルを合わせます。
5. **All** を選択します（None / Selected / All の 3 択です）。

コリジョンメッシュがワイヤーフレーム（ピンク〜緑色の線）で重ねて表示されます。

!!! note "ワイヤーフレームが表示されない場合"
    環境やアセットによっては、**All** を選択してもワイヤーフレームがすぐに反映されないことがあります。その場合は、ビューポートのカメラを動かす、対象のプリムに近づく、あるいは一度シミュレーションを再生するなどして表示が更新されるか確認してください。

![コリジョンメッシュ](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_6.0_full_ext-isaacsim.asset.importer.urdf-3.0.0_gui_3.png)

## ステップ 3：組み込みサンプルからのインポート

!!! warning "本サイト補足：この節は 5.1.0 時点の内容に基づきます"
    この「組み込みサンプル」の節は Isaac Sim 6.0 の公式チュートリアルからは削除されました。本節は 5.1.0 時点の内容と検証をもとにした本サイト独自の解説です。お使いのバージョンによっては、例の構成や表記が異なる場合があります。

Isaac Sim には、インポートから駆動設定・シミュレーションまでの一連の流れを体験できるサンプルが組み込まれています。

**Window > Examples > Robotics Examples** を有効にすると、画面下部のドックに **Robotics Examples** タブが表示されます。サイドバーの **IMPORT ROBOTS** セクションには 4 つの例が用意されています：

- Carter URDF（モバイルロボット。公式ドキュメントでは Nova Carter URDF と表記されていますが、実際の UI 上の表記は Carter URDF です）
- Franka URDF（マニピュレータ）
- Kaya URDF（モバイルロボット）
- UR10 URDF（マニピュレータ）

!!! note "マテリアルの読み込みを待つ"
    これらのサンプルではマテリアルの読み込みに時間がかかることがあります。UI 右下のプログレス表示で進行状況を確認できます。

![Robotics Examples](./images/01_robotics_examples_window.png)

それぞれインポート設定とインポート後のセットアップ内容は異なりますが、使い方は共通です：

1. **Robotics Examples** タブで **IMPORT ROBOTS > （ロボット名） URDF** をクリックすると、右側に例のパネルが開きます。
2. **Command Panel** の **Load Robot** 行にある **LOAD** ボタン — URDF をステージにインポートし、地面・ライト・物理シーンを追加します。
3. **Configure Drives** 行にある **CONFIGURE** ボタン — 各ジョイントドライブの Stiffness / Damping を設定します。
4. パネル右上の**鉛筆アイコン（Open Source Code）** — この一連の処理を Python API でどう実装しているか、ソースコードを確認できます。
5. 左側ツールバーの **PLAY** ボタン — シミュレーションを開始します。
6. **Move to Pose** 行にある **MOVE** ボタン — ロボットをホーム（休止）姿勢へ動かします。

## ステップ 4：Python API によるインポート

Import ウィンドウで行っていた操作は、Python スクリプトでも実行できます。Isaac Sim 6.0 では、`URDFImporter` / `URDFImporterConfig` クラスを使う新しい API が導入されました。

1. **Window > Script Editor** で Script Editor を開きます。
2. 以下のコードを Script Editor にコピーします：

```python
import os

import isaacsim.core.experimental.utils.stage as stage_utils
import omni
from isaacsim.asset.importer.urdf import URDFImporter, URDFImporterConfig

# エクステンションのインストール先パスを取得
ext_manager = omni.kit.app.get_app().get_extension_manager()
ext_id = ext_manager.get_enabled_extension_id("isaacsim.asset.importer.urdf")
extension_path = ext_manager.get_extension_path(ext_id)

# URDF をインポート
importer = URDFImporter(
    URDFImporterConfig(
        urdf_path=os.path.normpath(os.path.join(extension_path, "data", "urdf", "robots", "ur10", "urdf", "ur10.urdf")),
        usd_path=os.path.normpath(os.path.join(extension_path, "data", "urdf", "robots", "ur10", "urdf", "ur10.usd")),
        merge_mesh=True,             # メッシュを結合（GUI の Merge Mesh に相当）
        allow_self_collision=True,   # 自己衝突を許可（GUI の Allow Self-Collision に相当）
    )
)
output_path = importer.import_urdf()

# 変換された USD を開く
print(output_path)
result, stage = stage_utils.open_stage(output_path)
```

3. **Run**（Ctrl + Enter）をクリックすると、UR10 が変換されてステージに読み込まれます。

### コードのポイント

| クラス／メソッド | 説明 |
|---|---|
| `URDFImporterConfig` | インポート設定。`urdf_path`（入力）と `usd_path`（出力）のほか、`merge_mesh`、`allow_self_collision`、`fix_base`（`None` = Source / `True` = Fixed / `False` = Mobile）、`robot_type` などを指定できる |
| `URDFImporter` | 設定を受け取ってインポートを実行するクラス |
| `importer.import_urdf()` | 変換を実行し、生成された USD ファイルのパスを返す |
| `stage_utils.open_stage()` | 生成された USD を現在のステージとして開く（`isaacsim.core.experimental.utils.stage`） |

!!! warning "サンプルの出力先は書き込み可能な場所に"
    上のコードはエクステンション同梱フォルダに `ur10.usd` を出力します。インストール環境によってはこのフォルダが読み取り専用のことがあるため、その場合は `usd_path` を自分の作業ディレクトリなど書き込み可能な場所に変更してください。

!!! note "旧 API（URDFParseFile / URDFImportRobot コマンド）からの移行"
    Isaac Sim 5.x までのチュートリアルで使われていた `omni.kit.commands.execute("URDFParseFile", ...)` / `URDFImportRobot` / `URDFParseAndImportFile` の Kit コマンドベースの方法に代わって、6.0 では上記の `URDFImporter` クラスが標準の方法になりました。

## ステップ 5：スタンドアロンスクリプトによるインポート

Isaac Sim の GUI を開かずに、ターミナルから URDF を USD に一括変換することもできます。Isaac Sim のインストールルートで次を実行します：

```bash
./python.sh standalone_examples/api/isaacsim.asset.importer.urdf/urdf_import.py --urdf /path/to/ur10.urdf --usd-path /path/to/output --merge-mesh
```

主な引数は次のとおりです（すべての引数はスクリプトの `--help` で確認できます）：

| 引数 | 説明 |
|---|---|
| `--urdf` | URDF ファイル（`.urdf`）またはディレクトリのパス。ディレクトリを渡すと中の URDF をまとめて変換する |
| `--usd-path` | 変換した USD の出力先ディレクトリ |
| `--robot-type` | ロボットスキーマの Robot Type（Default / End Effector / Manipulator / Humanoid / Wheeled / Holonomic / Quadruped / Mobile Manipulators / Aerial。既定は Default） |
| `--merge-mesh` | メッシュを結合して最適化する |
| `--merge-fixed-joints` | 可能な範囲で固定ジョイントをマージしてモデルを最適化する |
| `--collision-from-visuals` | ビジュアルメッシュからコリジョン形状を生成する |
| `--collision-type` | コリジョン形状の種類（`"Convex Hull"`、`"Convex Decomposition"`、`"Bounding Sphere"`、`"Bounding Cube"`） |
| `--allow-self-collision` | 自己衝突を許可する |
| `--fix-base` / `--no-fix-base` | ベース固定の 3 択指定。`--fix-base` でワールドへの固定ジョイントを追加、`--no-fix-base` で既存の固定ジョイントを除去、省略時は URDF の記述のまま（GUI の Base Type に対応） |
| `--link-density` | 質量未定義のリンクに適用する密度（kg/m³） |
| `--joint-drive-type` / `--joint-target-type` | 全ジョイントに適用するドライブ種別（force / acceleration）とターゲット種別（none / position / velocity） |
| `--override-joint-stiffness` / `--override-joint-damping` | 全ジョイントに適用する Stiffness / Damping の上書き値 |
| `--ros-package` | `package://` URL を解決するための `名前:パス` のマッピング（複数指定可） |
| `--test` | 同梱の `carter.urdf` を一時ディレクトリに変換して動作確認する |

## インポート後の調整

ロボットはステージにインポートされた時点でシミュレーションに使用できますが、インポート後のアセットには次のような変更を加えられます：

- センサー（カメラ、IMU、LiDAR など）の追加
- マテリアルの変更
- ジョイントドライブや各種設定の更新によるシミュレーションの安定化

ロボットはシミュレーション内では**アーティキュレーション**として扱われます。アーティキュレーションのチューニングについては、公式の Articulation Stability Guide のほか、[ロボットセットアップ チュートリアル 11: ジョイントドライブゲインの調整](../robot_setup/11_joint_tuning.md)も参考にしてください。

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. GUI による **URDF ファイルの直接インポート**と設定項目（Robot Type / Base Type / Merge Mesh など）の意味
2. **コリジョンメッシュ**の可視化と確認
3. **組み込みサンプル**（Robotics Examples）によるインポートの流れ
4. **Python API**（`URDFImporter` / `URDFImporterConfig`）によるインポート
5. **スタンドアロンスクリプト**（`urdf_import.py`）による一括変換

### さらに学ぶには

インポート設定の全項目については、公式の [URDF Importer Extension](https://docs.isaacsim.omniverse.nvidia.com/latest/importer_exporter/ext_isaacsim_asset_importer_urdf.html) ドキュメントを参照してください。

## 次のステップ

- [チュートリアル 1a: ROS 2 ノードからの URDF インポート](01a_import_urdf_from_ros2.md) - ROS 2 の `robot_state_publisher` から URDF（XACRO）を直接インポートする方法を学びます。
- [チュートリアル 2: URDF エクスポート](02_export_urdf.md) - 逆方向、つまり USD から URDF への変換方法を学びます。
