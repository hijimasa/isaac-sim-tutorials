---
title: Robot Schema の適用
---

# Robot Schema の適用

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- **Robot Schema** が何であり、なぜ必要なのか
- 主要な API（**RobotAPI / LinkAPI / JointAPI / SiteAPI** など）の役割
- 手動でリギングしたロボットに Robot Schema を適用する方法（GUI と Python の両方）
- 専用レイヤーに分離して非破壊的に適用するベストプラクティス
- Gain Tuner などの Asset Editor 系ツールでロボットが認識されることの確認方法

## はじめに

### 前提条件

- [チュートリアル 5: モバイルロボットのリギング](05_rig_mobile_robot.md) を完了していること
- リギング済みの USD アセット（例：`SMV_Forklift_B01_01`）が手元にあること

### 所要時間

約 20 分

### 概要

[チュートリアル 5](05_rig_mobile_robot.md) では、フォークリフトに **Articulation Root** を適用してアーティキュレーションとして駆動できる状態まで仕上げました。これだけでも物理シミュレーション自体は動作しますが、Isaac Sim の高度なツール群——たとえば **Gain Tuner**（[チュートリアル 11](11_joint_tuning.md)）、**Grasp Editor**、**Robot Description Editor（XRDF Editor）**、**Robot Wizard**、そして Isaac Sim 6.0 で追加された **Robot Inspector** や **Robot Poser** など——は、対象アセットを「ロボット」として認識するために **Robot Schema** という追加スキーマが適用されていることを要求します。

このチュートリアルでは、手動リギングしたロボットに Robot Schema を適用し、後続のツールチェーンで使えるようにする方法を学びます。具体的には以下の流れで進めます：

1. **Robot Schema とは何か** を理解する
2. **専用レイヤーの作成** — 非破壊的に Robot Schema を追加
3. **Python による一括適用** — 公式推奨の方法
4. **GUI による補足的な適用** — 個別プリムへの追加・微修正
5. **適用結果の確認** — Properties パネルと Gain Tuner で動作確認

!!! note "URDF / MJCF インポート経由のロボットでは不要"
    [URDF インポーター](06_setup_manipulator.md) や MJCF インポーターを使ってロボットを読み込んだ場合、これら 2 つのインポーターは **Robot Schema を自動的に適用**します。後続の[チュートリアル 6 / 7](06_setup_manipulator.md) で扱う UR10e はその例です。本チュートリアルは、**URDF を経由せず手動でリギングしたロボット**（チュートリアル 5 の成果物など）を扱う場合に必要となります。

## ステップ 1：Robot Schema とは

**Robot Schema** は、OpenUSD の [Physics Schema](https://openusd.org/release/api/physics_8h_source.html) を補完する形で NVIDIA が定義した、**ロボットを記述するための拡張スキーマ**です。Physics Schema が「剛体・ジョイント・アーティキュレーション」といった**物理の枠組み**を定義するのに対し、Robot Schema は「どのプリムがロボットの中核（Robot）で、どれがリンク／ジョイント／参照点なのか」という**意味づけ**を与えます。

### 1-1. なぜ Physics Schema だけでは足りないのか

Physics Schema は USD のオープン標準であり、汎用的に使えますが、**「これはロボットだ」と宣言する仕組みは持っていません**。たとえば：

- アーティキュレーションを 1 つのロボットとして列挙する
- 名前空間（`/robot1`、`/robot2` のような区別）を ROS や OmniGraph に伝える
- DOF のレポート順序、加速度／ジャーク制限などのロボット固有メタデータを記述する
- グリッパーの吸着点（Attachment Point）や工具の参照点（Reference Point）を定義する

これらは Physics Schema の範囲外です。**Robot Schema はこの不足を埋め**、Asset Editor 系の各種ツールがロボット構造を一貫して扱える共通基盤を提供します。

### 1-2. 4 つの主要 API

Robot Schema は 5 つの適用型 API スキーマ（IsaacRobotAPI / IsaacLinkAPI / IsaacJointAPI / IsaacSiteAPI / IsaacAttachmentPointAPI）と 2 つの型付きスキーマ（IsaacNamedPose / IsaacSurfaceGripper）から構成されています。本チュートリアルでは特に重要な 4 つを扱います：

| API スキーマ | 適用先 | 役割 | 主な属性／リレーション |
|---|---|---|---|
| **IsaacRobotAPI** | ロボットのルートプリム | 「これがロボット本体」と宣言。各種ツールはここを起点にロボットを認識する | `isaac:description`、`isaac:namespace`、`isaac:robotType`、`isaac:license`、`isaac:source`、`isaac:version`、`isaac:changelog`、`robotLinks`（リレーション）、`robotJoints`（リレーション）、`namedPoses`（リレーション） |
| **IsaacLinkAPI** | 各リンク（剛体）プリム | リンクとしての意味づけ。表示名のオーバーライドなど | `nameOverride` |
| **IsaacJointAPI** | 各ジョイントプリム | ジョイントとしての意味づけ。DOF の並び順情報など | `nameOverride`、`isaac:physics:DofOffsetOpOrder`（Token 配列） |
| **IsaacSiteAPI** | エンドエフェクタや工具取付点などの参照プリム | ツール取付点・センサー位置・エンドエフェクタフレームなどの「ロボット上の意味のある点（サイト）」を表現する | `isaac:Description`、`isaac:forwardAxis` |

このほかに、グリッパーの吸着点を表す `IsaacAttachmentPointAPI`、サーフェスグリッパー全体を表す `IsaacSurfaceGripper` プリム型、名前付きジョイント姿勢を保存する `IsaacNamedPose` プリム型（Robot Poser が使用）があります。これらは必要に応じて適用します。

!!! note "Isaac Sim 6.0 でのスキーマ変更"
    - **`IsaacSiteAPI` は旧 `IsaacReferencePointAPI` の後継**です。旧スキーマが適用されたロボットも動作しますが、非推奨（deprecated）警告が出力されます。
    - IsaacJointAPI の DOF オフセットは、旧来の軸ごとの属性（`isaac:physics:Tr_X:DoFOffset` など）から **`isaac:physics:DofOffsetOpOrder` Token 配列**に変更されました。単一 DOF のジョイント（Revolute / Prismatic）や固定ジョイントではこの属性は不要です。
    - 既存アセットの移行には、`usd.schema.isaac.robot_schema.utils` の **`UpdateDeprecatedSchemas(robot_prim)`**（ReferencePoint → Site、旧 DOF オフセット属性の移行を一括実行）が使えます。

### 1-3. ツールはどう Robot Schema を使うのか

具体例として、Gain Tuner の動作を見てみましょう。Gain Tuner はステージ全体を走査し、**`IsaacRobotAPI` が適用されたプリムだけ**をドロップダウンメニューに列挙します（`isaacsim.robot_setup.gain_tuner` 拡張の実装）。Robot Schema が適用されていなければ、たとえ Articulation Root が有効でも Gain Tuner からは「ロボットが見えない」状態になります。

同様の仕組みで、Grasp Editor は `IsaacAttachmentPointAPI` を、Robot Description Editor（XRDF Editor）は `IsaacJointAPI` の DOF 並び順情報を、Isaac Sim 6.0 の **Robot Inspector**（`isaacsim.robot.schema.ui`）や **Robot Poser** は `IsaacRobotAPI` のリンク／ジョイントリストと `IsaacNamedPose` を、それぞれ参照します。

## ステップ 2：レイヤー構成の準備

Isaac Sim の[アセット構造ガイドライン](https://docs.isaacsim.omniverse.nvidia.com/latest/robot_setup/asset_structure.html) では、**Robot Schema を専用レイヤーに分離して保存する**ことが推奨されています。これにより：

- ベースアセット（メッシュやリギング）に手を加えずに Robot Schema を追加できる
- スキーマの将来の更新があってもベースを再生成せずに対応できる
- 不要になればレイヤーを切り離すだけで元に戻せる

### 2-1. レイヤー構成の方針

USD はファイルを**レイヤー**として重ね合わせる仕組みを持っており、ベースアセットを変更せずに別ファイルからプロパティを上書き・追加できます。Robot Schema もこの仕組みを使って専用レイヤーに分離するのが推奨です：

| ファイル | 役割 |
|---|---|
| `<robot>.usd` | ベースのリギング済みアセット（チュートリアル 5 の成果物） |
| `configuration/<robot>_robot_schema.usda` | **Robot Schema の適用結果のみ** を格納するレイヤー（このチュートリアルで作成） |

`configuration/` サブディレクトリ配下に `*_robot_schema.usda` という名前で配置するのは Isaac Sim 公式推奨の命名規則です。

!!! note "USD レイヤーの考え方"
    USD のレイヤーは、Photoshop のレイヤーに似た仕組みです。**ベースとなるファイルの上にもう一つのレイヤーを重ねる**ことで、元のファイルを一切変更せずにプロパティの追加・変更ができます。本チュートリアルでは、ベースアセット（リギング済みフォークリフト）の上に Robot Schema レイヤーを重ねる構成を作ります。

    後段のステップ 3 で実行する Python スクリプトが、このレイヤー構造を自動的に作成します。

### 2-2. 作業ディレクトリの確認

チュートリアル 5 で作成した USD ファイル（例：`forklift.usd`）が保存されているフォルダを開きます。同じフォルダの中に `configuration/` サブフォルダがなければ作成しておきます。

```
my_forklift/
├── forklift.usd                              ← ベースアセット
└── configuration/                            ← 新規作成
    └── forklift_robot_schema.usda            ← このチュートリアルで作成
```

## ステップ 3：Python による Robot Schema の一括適用

ロボットのリンク数・ジョイント数が多い場合、Python による一括適用が圧倒的に効率的です。Isaac Sim 公式ドキュメントが提供しているスクリプトをそのまま使います。

### 3-1. ベースアセットを開く

1. Isaac Sim を起動し、チュートリアル 5 で作成した `forklift.usd` を開きます
2. ステージのデフォルトプリムが正しく設定されていることを確認します（`/SMV_Forklift_B01_01` など、ロボットのルート Xform）

!!! note "デフォルトプリムの確認方法"
    Stage パネルでロボットのルート Xform を選択し、**Properties** パネルの **Metadata** セクションで `defaultPrim` が設定されているか確認します。設定されていない場合は、ルート Xform を右クリックし **Set as Default Prim** を選択してください。

### 3-2. Script Editor を開く

1. メニューから **Window > Script Editor** を選択します

### 3-3. 一括適用スクリプトの実行

以下のスクリプトを Script Editor に貼り付け、**Run**（▶ ボタン）をクリックします：

```python
import omni.usd
import pxr
import usd.schema.isaac.robot_schema as rs
from pxr import Sdf, Usd, UsdGeom

stage = omni.usd.get_context().get_stage()

# Create a configuration/ sublayer in the same directory as the base asset
robot_asset_path = "/".join(stage.GetRootLayer().identifier.split("/")[:-1])
robot_asset = ".".join(stage.GetRootLayer().identifier.split("/")[-1].split(".")[:-1])
schema_asset = f"configuration/{robot_asset}_robot_schema.usda"
edit_layer = Sdf.Layer.FindOrOpen(f"{robot_asset_path}/{schema_asset}")
if not edit_layer:
    edit_layer = Sdf.Layer.CreateNew(f"{robot_asset_path}/{schema_asset}")

# Add sublayer to the stage (relative path), only if not already present
if schema_asset not in stage.GetRootLayer().subLayerPaths:
    stage.GetRootLayer().subLayerPaths.append(schema_asset)

# Make all edits in the edit layer
with pxr.Usd.EditContext(stage, edit_layer):
    default_prim = stage.GetDefaultPrim()

    # Apply the Robot API to the default prim.
    # This auto-populates the Links and Joints lists from the physics articulation.
    rs.ApplyRobotAPI(default_prim)

# Save the Robot Schema layer and the stage
edit_layer.Save()
stage.Save()

print(f"Robot Schema saved to {schema_asset}")
```

このスクリプトは以下を行います：

1. ベースアセットと同じディレクトリに `configuration/<アセット名>_robot_schema.usda` という新規レイヤーを作成し、サブレイヤーとしてアタッチ（すでにアタッチ済みであればスキップ）
2. デフォルトプリムに **RobotAPI** を適用
3. `ApplyRobotAPI` が物理アーティキュレーションを自動走査し、発見した**剛体には LinkAPI**、**ジョイントには JointAPI** を適用したうえで、`robotLinks` / `robotJoints` リレーションに順序付きで自動登録
4. すべての変更を Robot Schema レイヤーに書き込んで保存

!!! note "Isaac Sim 6.0 での変更点"
    以前は `Usd.PrimRange` で全プリムを走査して `ApplyLinkAPI` / `ApplyJointAPI` を手動で呼び出す必要がありましたが、Isaac Sim 6.0 では **`ApplyRobotAPI` がリンク／ジョイントの検出・適用・リスト登録まで自動で行います**。自動登録（auto-population）には物理情報（アーティキュレーション）がステージ上でオーサリングされている必要があります。物理を別レイヤーに分離しているアセットでは、適用作業の間だけ物理レイヤーをサブレイヤーとして追加し、保存前に取り外してください。

### 3-4. 実行結果の確認

Script Editor の出力に `Robot Schema saved to configuration/<...>_robot_schema.usda` と表示されれば成功です。

ファイルマネージャーで `configuration/` フォルダを開き、新しい `*_robot_schema.usda` ファイルが作成されていることを確認します。

!!! tip "スクリプトの再実行・ロボット構造の更新"
    ロボットの構造が後から変わった場合（リンクやジョイントの追加など）は、ルートプリムに **RobotAPI を再適用**して自動登録をやり直すか、`usd.schema.isaac.robot_schema.utils` の **`RecalculateRobotSchema`**（既存の並び順を保持したまま、新規リンク／ジョイントを追記し、無効なターゲットを削除）を使ってください。GUI では、ルートプリム選択時の Properties パネルにある **Re-Calculate Robot Tree** ボタンでも同じ処理を実行できます。

## ステップ 4：GUI による適用（補足）

GUI でも Robot Schema を適用できます。少数のプリムだけ追加で API を当てたい場合や、属性を個別に編集したい場合に便利です。

### 4-1. RobotAPI の適用

1. Stage パネルでロボットのルート Xform（例：`/SMV_Forklift_B01_01`）を選択します
2. Properties パネルの **+ Add** ボタンをクリック
3. 表示されたメニューから **Isaac > Robot Schema > Robot API** を選択
4. Properties パネルに紫色の **Robot** セクションが追加されたことを確認

GUI からの適用でも Python と同様に、物理アーティキュレーションが自動走査され、発見された剛体・ジョイントに **IsaacLinkAPI / IsaacJointAPI** が適用されて `robotLinks` / `robotJoints` リストに自動登録されます。

!!! warning "適用先レイヤーに注意"
    アセットが[アセット構造ガイドライン](https://docs.isaacsim.omniverse.nvidia.com/latest/robot_setup/asset_structure.html)に従っている場合、Robot Schema は**ベースレイヤーまたは専用の Robot Schema レイヤー**に適用してください（インターフェースレイヤーに直接オーサリングしない）。自動登録には物理情報が必要なため、適用作業の間だけ物理レイヤーをサブレイヤーとして追加し、保存前に取り外します。

### 4-2. 属性の編集

追加された Robot セクションでは、以下を設定できます：

| 属性 | 例 | 用途 |
|---|---|---|
| **Description** | `Custom forklift mobile robot rig` | ロボットの説明文 |
| **Namespace** | `forklift` | ROS / OmniGraph の名前空間 |
| **Robot Type** | `mobile_robot` | ロボット種別（任意の Token） |
| **Robot Links**（リレーション） | 各リンクのプリムパス | ロボットを構成するリンクの順序付きリスト |
| **Robot Joints**（リレーション） | 各ジョイントのプリムパス | DOF を持つジョイントの順序付きリスト |

!!! note "Robot Links / Robot Joints の意味"
    これらのリレーションは「ステート報告に含めたいリンク／ジョイントの順序」を指定するものです。リレーションに登録されていないリンクやジョイントもアーティキュレーションには含まれますが、ROS のジョイントステートメッセージなどには出力されません。

### 4-3. LinkAPI / JointAPI の個別適用

- リンクに対して：剛体プリムを選択 → **+ Add > Edit API Schema > IsaacLinkAPI**
- ジョイントに対して：ジョイントプリムを選択 → **+ Add > Edit API Schema > IsaacJointAPI**

ステップ 3 のスクリプトを実行済みであれば、すべてのリンクとジョイントに自動で適用されているため、この手順は通常不要です。

## ステップ 5：適用結果の確認

### 5-1. Properties パネルでの確認

1. Stage パネルでロボットのルートプリムを選択
2. Properties パネルをスクロールし、**紫色の Robot セクション**が表示されることを確認
3. 各リンク／ジョイントを選択し、それぞれ **Link** / **Joint** セクションが表示されることを確認

!!! tip "セクションが表示されない場合"
    Properties パネルの上部にある検索欄に `Robot` と入力するか、フィルタを **All** に切り替えてください。Raw USD Properties 表示にすると `apiSchemas = ["IsaacRobotAPI", ...]` のように直接確認できます。

### 5-2. Gain Tuner での認識確認

Robot Schema が正しく適用されていれば、Gain Tuner からロボットが認識されるはずです：

1. メニューから **Tools > Robotics > Asset Editors > Gain Tuner** を開く
2. **Select Robot** ドロップダウンを開く
3. リストにあなたのロボット（例：`/SMV_Forklift_B01_01`）が表示されていることを確認

ドロップダウンに表示されなければ、ステップ 3 のスクリプト実行時にエラーが出ていなかったか、ステージを保存後にリロードしたかを確認してください。

### 5-3. Python によるプログラム的な確認

Script Editor で以下を実行することでも確認できます：

```python
import omni.usd
import usd.schema.isaac.robot_schema as rs

stage = omni.usd.get_context().get_stage()
default_prim = stage.GetDefaultPrim()

print("Applied schemas:", default_prim.GetAppliedSchemas())
print("Has RobotAPI:", default_prim.HasAPI(rs.Classes.ROBOT_API.value))

# Inspect the targets of robotLinks / robotJoints
for rel_name in [rs.Relations.ROBOT_LINKS.name, rs.Relations.ROBOT_JOINTS.name]:
    rel = default_prim.GetRelationship(rel_name)
    targets = rel.GetTargets()
    print(f"{rel_name} target count: {len(targets)}")
```

`Has RobotAPI: True` と表示され、リンク・ジョイントが想定通りの数で登録されていれば成功です。

## ステップ 6（オプション）：Reference Point の追加

ロボットアームのエンドエフェクタや、フォークリフトのフォーク先端など、**ロボット上の意味のある参照点**には `IsaacReferencePointAPI` を適用しておくと、後続のツール（Pick & Place チュートリアル、Grasp Editor など）から参照しやすくなります。

!!! warning "参照点プリムは事前に作成しておく必要があります"
    `IsaacReferencePointAPI` は**既存のプリムに API を追加する仕組み**であり、プリムを新規生成してくれるわけではありません。対象パスにプリムが存在しないまま API を適用すると、以下のような実行時エラーになります：

    ```
    RuntimeError: Accessed invalid null prim
      ... in ApplyReferencePointAPI
    ```

    そのため、まず**参照点となる Xform プリムを作成**し、適切な位置に配置してから API を適用します。

### 6-1. GUI で適用する例

1. Stage パネルで親プリム（例：`/SMV_Forklift_B01_01/lift`）を右クリック
2. **Create > Xform** を選択し、新しい Xform を作成
3. 作成された Xform を `fork_tip` にリネーム
4. Properties パネルの **Transform** で、参照点として配置したい位置・姿勢を設定（例：フォーク先端の座標）
5. `fork_tip` を選択した状態で **+ Add > Edit API Schema > IsaacReferencePointAPI** を選択
6. **Description** に `Fork tip for object insertion` などの説明を入力
7. **Forward Axis** に基準軸（`X`、`Y`、`Z` のいずれか）を設定

### 6-2. Python で適用する例

参照点プリムが存在しない場合に新規作成し、適切な位置に配置してから API を適用する完全な例です：

```python
from pxr import Usd, UsdGeom, Gf
import omni.usd
import usd.schema.isaac.robot_schema as rs

stage = omni.usd.get_context().get_stage()

# Create the reference point prim if it does not exist
ref_path = "/SMV_Forklift_B01_01/lift/fork_tip"
ref_prim = stage.GetPrimAtPath(ref_path)
if not ref_prim.IsValid():
    ref_xform = UsdGeom.Xform.Define(stage, ref_path)
    # Set the local transform (adjust to the actual fork tip position in your asset)
    ref_xform.AddTranslateOp().Set(Gf.Vec3d(0.0, 0.0, 0.5))
    ref_prim = ref_xform.GetPrim()

# Apply ReferencePointAPI
rs.ApplyReferencePointAPI(ref_prim)

# Set attributes
ref_prim.GetAttribute("isaac:Description").Set("Fork tip for object insertion")
ref_prim.GetAttribute("isaac:forwardAxis").Set("Z")

print(f"ReferencePointAPI applied to {ref_path}")
```

!!! tip "既存プリムをそのまま参照点にする場合"
    すでに目的の場所に Xform やリンクがある場合は、新規作成せずにそのプリムに直接 `ApplyReferencePointAPI` を適用するだけで構いません。その場合は、上記スクリプトの `if not ref_prim.IsValid():` ブロック全体を削除してください。

    リンク（剛体）に Reference Point API を追加することも可能で、その場合は LinkAPI と ReferencePointAPI の両方が同じプリムに適用された状態になります。

## トラブルシューティング

| 症状 | 原因 | 解決方法 |
|---|---|---|
| Gain Tuner にロボットが表示されない | RobotAPI 未適用 | ステップ 3 のスクリプトを実行、または GUI で **IsaacRobotAPI** をルートプリムに適用 |
| `usd.schema.isaac.robot_schema` の import エラー | `isaacsim.robot.schema` 拡張が無効 | **Window > Extensions** で `isaacsim.robot.schema` を検索して有効化 |
| `default_prim` が `None` | デフォルトプリム未設定 | ルート Xform を右クリックし **Set as Default Prim** |
| `robotLinks` / `robotJoints` が空 | スクリプト実行時に Default Prim 配下に剛体／ジョイントがない | プリム階層を確認、または `default_prim` を正しいルートに変更 |
| 再実行時にリレーションが重複 | `AddTarget` の重複登録 | `configuration/*_robot_schema.usda` を削除してから再実行 |
| Properties パネルに Robot セクションが出ない | 拡張機能の読み込み失敗 / プリム選択ミス | Isaac Sim を再起動、ステージを再読み込み、ルートプリムを再選択 |
| `RuntimeError: Accessed invalid null prim` が `ApplyReferencePointAPI` などで発生 | 対象パスにプリムが存在しない | `stage.GetPrimAtPath(...)` の戻り値で `prim.IsValid()` を確認。存在しない場合は `UsdGeom.Xform.Define` などで先にプリムを作成してから API を適用（ステップ 6-2 参照） |

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. **Robot Schema の概念** — Physics Schema を補完してロボットの意味づけを行う拡張スキーマ
2. **4 つの主要 API**（RobotAPI / LinkAPI / JointAPI / ReferencePointAPI）の役割と属性
3. **専用レイヤー（`configuration/<robot>_robot_schema.usda`）への分離**による非破壊的な適用
4. **Python による一括適用** — 全リンク・ジョイントへの自動適用
5. **GUI による補足適用** — 個別プリムへの追加と属性編集
6. **適用結果の確認** — Properties パネルと Gain Tuner ドロップダウンでの動作確認
7. **Reference Point の追加** — エンドエフェクタなど意味のある参照点の登録

これにより、手動リギングしたロボットも URDF インポート経由のロボットと同等に、Gain Tuner や Grasp Editor などの Asset Editor 系ツールから扱えるようになります。

!!! tip "公式ドキュメント"
    Robot Schema のより詳細な仕様（Surface Gripper、AttachmentPointAPI、ロボットの組み合わせ表現など）は、Isaac Sim 公式ドキュメントの [Robot Schema](https://docs.isaacsim.omniverse.nvidia.com/latest/omniverse_usd/robot_schema.html) を参照してください。

## 次のステップ

次のチュートリアル「[マニピュレータのセットアップ](06_setup_manipulator.md)」に進み、URDF からロボットアームをインポートする中級編に入りましょう。URDF インポート経由では Robot Schema が自動適用されるため、本チュートリアルで学んだ概念がそのまま活きてきます。
