---
title: 閉ループ構造のリギング
---

# 閉ループ構造のリギング

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- USD レイヤーを使ったアセット編集ワークフロー
- マテリアルとジョイントの調整
- 閉ループアーティキュレーションチェーンの分断方法
- ジョイントドライブとミミックジョイントの設定
- コリジョンメッシュとセルフコリジョンの最適化
- OmniGraph を使ったグリッパー制御の構築

## はじめに

### 前提条件

- [チュートリアル 5: モバイルロボットのリギング](05_rig_mobile_robot.md) を完了していること

### 使用するアセット

このチュートリアルでは、Isaac Sim に同梱されている事前インポート済みの Robotiq 2F-85 グリッパーアセットを使用します：

```
Samples/Rigging/Gripper/Robotiq 2F-85
```

### 所要時間

約 30 分

### 概要

ロボットグリッパーのような機構には、リンクが閉じたループ（閉ループ）を形成する構造が多くあります。しかし、物理シミュレーションのアーティキュレーション（関節連鎖）は**キネマティックツリー**（木構造）で表現する必要があり、ループ構造をそのまま扱うことはできません。

このチュートリアルでは、**Robotiq 2F-85 パラレルグリッパー**を題材に、閉ループ構造を含むロボットを Isaac Sim で正しくリギングする方法を学びます。具体的には以下の流れで進めます：

1. **レイヤーを使ったアセット編集** — 元のファイルを壊さずに設定を行うワークフロー
2. **ジョイントの調整** — ジョイントの向きや制限値の修正、摩擦マテリアルの設定
3. **アーティキュレーションループの分断** — 閉ループを木構造に変換
4. **テスト環境の構築** — グリッパーの動作を確認するためのシーン作成
5. **ジョイントドライブとミミックジョイントの設定** — グリッパーの指を制御するドライブとミミック連動の追加
6. **コリジョンメッシュの最適化** — 把持のための衝突形状の調整
7. **設定の保存** — レイヤーごとに変更を保存
8. **OmniGraph によるグリッパー制御** — Boolean 変数の切り替えでグリッパーを開閉

!!! note "閉ループ構造とは"
    閉ループ構造とは、リンクとジョイントが環状に接続された機構のことです。例えば、パラレルグリッパーの 2 本の指は、それぞれ複数のリンクを介してボディに接続されており、先端で物体を挟むことで閉じたループを形成します。一方、UR10e のようなシリアルロボットアームは、ベースからエンドエフェクタまで一本の鎖状（開ループ）に接続されています。

## ステップ 1：レイヤーを使ったアセット編集

元の USD ファイルを直接編集するのではなく、**レイヤー**を使って非破壊的に編集する方法を学びます。この方法であれば、元のアセットファイルを保持したまま設定変更を行え、アセットの更新や再利用にも対応しやすくなります。

!!! note "USD レイヤーとは"
    USD のレイヤーは、Photoshop のレイヤーに似た仕組みです。ベースとなるファイルの上に編集用のレイヤーを重ねることで、元のファイルを一切変更せずにプロパティの追加・変更ができます。レイヤーの変更が不要になれば、レイヤーを外すだけで元の状態に戻せます。

### 1-1. 作業ディレクトリの準備

サンプルアセットは書き込み禁止のため、まず作業用のフォルダにコピーします：

1. 任意の場所（例：デスクトップ）に作業用フォルダを作成します（例：`Robotiq_2F_85_rigging`）
2. サンプルアセット `Samples/Rigging/Gripper/Robotiq 2F-85` のフォルダ内にある`Robotiq_2F_85_base.usd`ファイルと`Materials`と`parts`ディレクトリを、作成した作業用フォルダにダウンロードします

    ![サンプルアセットのダウンロード](./images/49_sample_assets_download.png)

### 1-2. レイヤーワークフローの概要

このステップで、以下の 3 ファイル構成を作成します：

| ファイル | 役割 | 作成方法 |
|---|---|---|
| `Robotiq_2F_85_base.usd` | ベースとなるアセット（**変更しない**） | サンプルからコピー済み |
| `Robotiq_2F_85_edit.usd` | ジョイント調整やリギング設定を記録するレイヤー | **ユーザーが作成** |
| `Robotiq_2F_85_config.usd` | 上記を束ねて読み込む構成ファイル | **ユーザーが作成** |

### 1-3. 編集用レイヤーの作成

リギング設定を記録するための編集用レイヤーを作成します。ここでは、新しい USD ファイルを作成し、ベースアセットをサブレイヤーとして読み込むことで、元のファイルを変更せずに編集できる環境を構築します。

1. **File > New** で新しいステージを作成します
2. **File > Save As** で、作業用フォルダに `Robotiq_2F_85_edit.usd` として保存します
3. **Layer** タブを開きます（表示されていない場合は **Window > Layer** で表示）
4. Content Browser やファイルマネージャーから `Robotiq_2F_85_base.usd` を **Layer** タブの **Root Layer** にドラッグ＆ドロップします

    ![サブレイヤーの作成](./images/50_create_sub_layer.png)

5. ベースアセットのグリッパーが Stage に表示されることを確認します

これにより、`_edit.usd`（Root Layer）が `_base.usd`（サブレイヤー）の上に重なる構成となり、以降の編集内容は `_edit.usd` に記録され、ベースアセットは変更されません。

!!! note "レイヤーの重なり順序"
    USD のサブレイヤーは**上位のレイヤーが優先**されます。この構成では、Root Layer（`_edit.usd`）の意見（opinion）がサブレイヤー（`_base.usd`）より優先されるため、`_edit.usd` で行った変更が `_base.usd` の値を上書きします。

    一方、上位レイヤーで上書きしていないプロパティについては、下位レイヤーの値がそのまま最終結果に反映されます。つまり、`_base.usd` のメッシュやマテリアルを更新した場合、`_edit.usd` で同じプロパティを変更していなければ、その更新は自動的に反映されます。これが非破壊編集ワークフローの利点です。

!!! tip "Layer タブと Stage パネルの役割分担"
    **Layer** タブはレイヤーの追加や並び替え、**編集ターゲット**（編集内容がどのレイヤーに記録されるか）の切り替えに使うパネルです。プリムを選択して Properties から編集する操作自体は、引き続き **Stage** パネルから行ってください。Layer タブの中でプリムを探そうとすると、レイヤーごとの opinion 一覧が表示されるだけでプリムを直接編集できず、迷子になります。

    後のステップでは作業内容に応じて編集ターゲットを `_edit.usd` ⇔ `_config.usd` と切り替えますが、**「Layer タブで対象レイヤーをアクティブにする → Stage パネルに戻ってプリムを選択する」** という流れは常に変わりません。

### 1-4. 構成ファイルの作成

次に、テストシーンを構築するための構成ファイルを作成します。このファイルでは、編集済みのグリッパーアセットを**ペイロード**としてシーンに配置します。

1. **File > New** で新しいステージを作成します
2. **File > Save As** で、同じ作業用フォルダに `Robotiq_2F_85_config.usd` として保存します
3. Content Browser やファイルマネージャーから `Robotiq_2F_85_edit.usd` を **Stage** パネルの `/World` にドラッグ＆ドロップします
4. Stage パネルに追加されたプリム（青い矢印アイコン）の名前を `Robotiq_2F_85` にリネームします

    !!! tip "プリムのリネーム"
        追加されたプリムの名前はファイル名に基づいて `Robotiq_2F_85_edit` となる場合があります。後のステップで使用するパス（`/World/Robotiq_2F_85/base_link` など）と一致させるため、`Robotiq_2F_85` にリネームしてください。

この構成により、`_config.usd` を開くだけで、ベースアセット＋編集レイヤーの内容がグリッパーとしてシーンに読み込まれます。

!!! note "Payload と Reference の違い"
    Stage にアセットを追加する方法として、**Payload**（ペイロード）と **Reference**（リファレンス）の 2 つがあります。

    | | Payload（ペイロード） | Reference（リファレンス） |
    |---|---|---|
    | **Stage 上のアイコン** | 青い矢印 | オレンジの矢印 |
    | **追加方法** | ドラッグ＆ドロップ | 右クリック > Add > Reference |
    | **遅延読み込み** | 対応（アンロード可能） | 非対応（常に読み込まれる） |
    | **主な用途** | シーンに配置するアセット | 常に必要な依存ファイル |

    **Payload** はシーンが大規模になったとき、必要のないアセットを一時的にアンロードしてメモリとパフォーマンスを節約できる仕組みです。Stage パネルでプリムを右クリックし **Unload** を選択すると、そのアセットをアンロードできます。**Reference** は常に読み込まれるため、アンロードできません。

    今回のようにシーンにアセットを配置する場合は、**Payload**（ドラッグ＆ドロップ）が適しています。

!!! tip "サブレイヤーとの使い分け"
    USD にはサブレイヤー、リファレンス、ペイロードなど複数の合成方法がありますが、このチュートリアルでは以下のように使い分けています：

    - **サブレイヤー**（`_edit.usd` → `_base.usd`）：同じ Prim 階層を共有し、プロパティを上書きする。アセットの**非破壊編集**に適している。
    - **ペイロード**（`_config.usd` → `_edit.usd`）：外部アセットをシーン内の独立した Prim として配置する。**シーン構築**に適している。

!!! tip "レイヤー分離のメリット"
    - **`_edit.usd`**: ロボットのリギング設定（ジョイント、ドライブ、コリジョンなど）のみを格納
    - **`_config.usd`**: テスト用のシーン要素（地面、テスト用オブジェクトなど）を格納

    この分離により、リギングが完成した後は `_edit.usd` を他のシーンでも再利用できます。

## ステップ 2：ジョイントの調整

!!! info "作業ファイル：`Robotiq_2F_85_edit.usd`"
    このステップの変更はすべてグリッパーアセットのリギング設定です。`_edit.usd` を開いた状態で作業してください。

CAD からインポートされたジョイントには、向きが 180 度反転している場合があります。シミュレーションを正しく動作させるために、これらを修正します。

### 2-1. ジョイントの可視化

ジョイントの向きを確認するために、ビューポートでジョイントフレームを可視化します：

1. ビューポート上部の**目のアイコン**をクリックします
2. **Show By Type > Physics > Joints** を有効にします

これにより、各ジョイントの位置と回転軸がビューポート上にギズモとして表示されます。

!!! note "ジョイントギズモの見方"
    ジョイントを可視化すると、各ジョイントの位置に座標軸の矢印が表示されます。回転ジョイント（Revolute Joint）の場合、**回転軸**（通常は特定の軸の矢印）の向きがジョイントの正方向を示します。この正方向は、ジョイントの角度値が正のときにリンクが回転する方向を決定します。

### 2-2. ジョイントの向きの確認

Stage パネルで各ジョイントを選択し、ビューポートに表示されるギズモの軸の向きを確認します。

CAD からインポートされたジョイントでは、回転軸の向きが 180 度反転している場合があります。反転しているジョイントは、回転軸の正方向が期待と逆を向いています。

### 2-3. ジョイントの向きの修正

反転しているジョイントの向きを修正します：

1. Stage パネルで反転しているジョイントを選択します

   例）finger_joint: 指を開く方向に75度回転しようとするのがわかります

     ![修正前のfinger_joint](./images/51_finger_joint_before_fix.png)

2. Properties パネルの **Rotation** セクションで、**Rotation 0** と **Rotation 1** の X 軸に 180 度のオフセットを適用します
3. ギズモの向きが正しくなったことを確認します

   例）finger_joint: 指を閉じる方向に75度回転するようになっています

     ![修正後のfinger_joint](./images/52_finger_joint_after_fix.png)

!!! warning "この Robotiq 2F-85 アセットでの修正対象"
    このアセットでは finger_joint、right_outer_knuckle_joint、right_outer_finger_joint、left_outer_finger_jointの**4 つのジョイント**で向きの修正が必要です。ここで修正しておかないと、ステップ 5 でジョイントドライブを設定した際に、指が期待と逆方向に動いてしまいます。

### 2-4. ジョイント制限の設定

各ジョイントに適切な可動範囲を設定します（デフォルトで正しい可動域が入っているはずです）：

| ジョイント | 下限 | 上限 | 備考 |
|---|---|---|---|
| `left_outer_finger_joint` | 0° | 180° | 外側指リンクの可動範囲 |
| `right_outer_finger_joint` | 0° | 180° | 外側指リンクの可動範囲 |
| `finger_joint` | 0° | 75° | メインの駆動ジョイント |
| `right_outer_knuckle_joint` | 0° | 75° | 右側の外側ナックル |
| その他のジョイント | — | — | 制限なし（デフォルトのまま） |

### 2-5. 指先の摩擦マテリアルの作成

グリッパーの把持性能を向上させるため、指先に摩擦の高いマテリアルを設定します：

1. メニューから **Create > Physics > Physics Material** を選択
2. **Rigid Body Material** を選択し、`fingertip_material` にリネーム
3. 以下のパラメータを設定：

    | パラメータ | 値 | 説明 |
    |---|---|---|
    | Static Friction | `0.8` | 静止摩擦係数（ゴムに近い値） |
    | Dynamic Friction | `0.8` | 動摩擦係数 |
    | Friction Combine Mode | `Max` | 摩擦の合成方法（大きい方を採用） |

    ![摩擦の設定](./images/53_material_setting.png)

4. 作成したマテリアルを `right_inner_finger` と `left_inner_finger` のメッシュに適用

    ![マテリアルの適用](./images/54_finger_material_setting.png)

!!! note "Instanceable プロパティの無効化"
    マテリアルを適用する際、Xform の **Instanceable** プロパティが有効になっているとマテリアルを個別に設定できないことがあります。その場合は Instanceable を無効にしてから、メッシュコンポーネントに直接マテリアルを適用してください。

## ステップ 3：アーティキュレーションループの分断

!!! info "作業ファイル：`Robotiq_2F_85_edit.usd`"
    このステップの変更はグリッパーアセットのリギング設定です。引き続き `_edit.usd` で作業してください。

### 3-1. 問題の理解

この状態でシミュレーションを開始すると、以下のような警告が表示されます：

![ループエラー](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isaac_robotiq_loop_error.png)

これは、アーティキュレーション（関節連鎖）がループを形成しているためです。Isaac Sim のアーティキュレーションは**キネマティックツリー**（木構造）である必要があり、閉ループをそのまま扱うことはできません。

!!! note "なぜループが問題になるのか"
    物理シミュレータのアーティキュレーションソルバーは、ベースリンクからエンドエフェクタまでの**一方向の連鎖**（ツリー構造）を前提に設計されています。ループがあると、ソルバーが関節の拘束を正しく解けなくなります。

### 3-2. 分断するジョイントの選択基準

ループを解消するために、1 つのジョイントをアーティキュレーションから**除外**します。除外されたジョイントは、最大座標ジョイント（Maximal Coordinate Joint）として扱われ、ソルバーの優先度が低くなります。

最適なジョイントを選ぶための基準：

- **アーティキュレーションチェーンの長さを最小化**する位置にあること
- **制限値、抵抗、ドライブが不要**なジョイントであること
- **ロボットの機能への干渉が最小限**であること

### 3-3. ループの分断手順

この Robotiq 2F-85 グリッパーでは、インナーシャフトとボディを接続する `inner_knuckle_joint` が最適な候補です。

![ループの分断](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isaac_robotiq_loop.png)

1. Stage パネルで `left_inner_knuckle_joint` を選択
2. Properties パネルの **Physics** セクションで **Exclude From Articulation** にチェックを入れる
3. 同様に `right_inner_knuckle_joint` にも **Exclude From Articulation** を設定

!!! tip "Exclude From Articulation とは"
    このオプションを有効にすると、該当ジョイントはアーティキュレーションツリーから除外されます。ジョイント自体は物理的に存在し続けますが、アーティキュレーションソルバーではなく通常のジョイントソルバー（Maximal Coordinate）で処理されます。結果として、ループが解消されシミュレーションが正常に動作します。

これでシミュレーションを再度実行すると、ループに関する警告が消えます。

## ステップ 4：テスト環境の構築

!!! info "作業ファイル：`Robotiq_2F_85_config.usd`"
    テスト環境（地面、シリンダー、移動用ジョイントなど）はテストシーン固有の要素です。`_config.usd` を開いた状態で作業してください。

グリッパーの動作を確認するためのテストシーンを構築します。グリッパーを上下・前後に移動できる構造を作り、物体を把持するテストを行います。

### 4-1. テスト環境の構成

以下の要素をシーンに追加します。次節の Python スクリプトを実行することで一括構築できます。

**移動用の足場（グリッパーを上下・前後に動かすための構造）**:

| 要素 | 役割 |
|---|---|
| `Xform`（Rigid Body API 付き） | 中間プリム（Z 軸プリズマティックの基準） |
| `Xform_1`（Rigid Body API 付き） | グリッパーを保持するプリム（X 軸プリズマティックの基準） |
| Fixed Joint | ワールド → `Xform` を固定 |
| Prismatic Joint `Joint_Z`（Z 軸） | `Xform` → `Xform_1`（上下移動） |
| Prismatic Joint `Joint_X`（X 軸） | `Xform_1` → `base_link`（前後移動） |

**プリズマティックジョイントのドライブパラメータ**:

| パラメータ | 値 | 説明 |
|---|---|---|
| Maximum Joint Velocity | `5.0` | 最大ジョイント速度 |
| Joint Limits | `[0, 1]` | 可動範囲（メートル） |
| Damping | `10,000` | ダンピング係数 |
| Stiffness | `10,000` | 剛性係数 |

**シーン要素**:

- **シリンダー（把持対象）**: スケール `[0.05, 0.05, 0.2]`、位置 X=0.12、質量 0.10 kg
- **グランドプレーン**: 位置 Z=-0.1
- **Physics Scene**: GPU Dynamics 無効

### 4-2. Python スクリプトによる自動セットアップ

上記の構成は、以下の Python スクリプトを Isaac Sim のメニューバーの `Window` から立ち上げられる Script Editor で実行することで一括構築できます：

```python
from pxr import Usd, UsdGeom, UsdPhysics, PhysxSchema, PhysicsSchemaTools, Gf, Sdf
import omni.usd

stage = omni.usd.get_context().get_stage()

# Xform ノードの作成
xform = UsdGeom.Xform.Define(stage, "/World/Xform")
xform_1 = UsdGeom.Xform.Define(stage, "/World/Xform_1")

# Rigid Body API の適用
for node in [xform, xform_1]:
    UsdPhysics.RigidBodyAPI.Apply(node.GetPrim())

# 固定ジョイントの作成
fixed_joint = UsdPhysics.FixedJoint.Define(
    stage, xform.GetPath().AppendChild("fixed_joint")
)
fixed_joint.CreateBody1Rel().SetTargets([str(xform.GetPath())])

# プリズマティックジョイント 1（Z 軸方向）
prismatic_joint_1 = UsdPhysics.PrismaticJoint.Define(stage, "/World/Joint_Z")
prismatic_joint_1.CreateAxisAttr("Z")
prismatic_joint_1.CreateLowerLimitAttr(0.0)
prismatic_joint_1.CreateUpperLimitAttr(1.0)
prismatic_joint_1.CreateBody0Rel().SetTargets([str(xform.GetPath())])
prismatic_joint_1.CreateBody1Rel().SetTargets([str(xform_1.GetPath())])

# プリズマティックジョイント 2（X 軸方向）
prismatic_joint_2 = UsdPhysics.PrismaticJoint.Define(stage, "/World/Joint_X")
prismatic_joint_2.CreateAxisAttr("X")
prismatic_joint_2.CreateLowerLimitAttr(0.0)
prismatic_joint_2.CreateUpperLimitAttr(1.0)
prismatic_joint_2.CreateBody0Rel().SetTargets([str(xform_1.GetPath())])
prismatic_joint_2.CreateBody1Rel().SetTargets(["/World/Robotiq_2F_85/Robotiq_2F_85/base_link"])

# ジョイントドライブの追加
for joint in [prismatic_joint_1, prismatic_joint_2]:
    drive = UsdPhysics.DriveAPI.Apply(joint.GetPrim(), "linear")
    drive.CreateDampingAttr(10000)
    drive.CreateStiffnessAttr(10000)
    px_joint = PhysxSchema.PhysxJointAPI.Get(stage, str(joint.GetPath()))
    px_joint.CreateMaxJointVelocityAttr().Set(5.0)

# グランドプレーンの追加
PhysicsSchemaTools.addGroundPlane(
    stage, "/World/groundPlane", "Z", 100, Gf.Vec3f(0, 0, -0.1), Gf.Vec3f(1.0)
)

# シリンダー（把持対象）の作成
result, path = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cylinder")
cylinder_prim = stage.GetPrimAtPath(path)
cylinder_prim.GetAttribute("xformOp:scale").Set((0.05, 0.05, 0.2))
cylinder_prim.GetAttribute("xformOp:translate").Set((0.12, 0, 0))

# シリンダーに物理属性を追加
cylinder_body = UsdPhysics.RigidBodyAPI.Apply(cylinder_prim)
UsdPhysics.CollisionAPI.Apply(cylinder_prim)
massAPI = UsdPhysics.MassAPI.Apply(cylinder_body.GetPrim())
massAPI.CreateMassAttr(0.10)

# Physics Scene の作成
scene = UsdPhysics.Scene.Define(stage, Sdf.Path("/physicsScene"))
physxSceneAPI = PhysxSchema.PhysxSceneAPI.Apply(scene.GetPrim())
physxSceneAPI.CreateEnableGPUDynamicsAttr(False)
```

!!! warning "GPU Dynamics が有効だとエラーが発生します"
    Physics Scene の **Enable GPU Dynamics** が有効になっていると、ジョイントドライブの `setDriveTarget()` が使用できず、以下のようなエラーが発生します：

    ```
    PhysX error: PxArticulationJointReducedCoordinate::setDriveTarget(): it is illegal to call this method if PxSceneFlag::eENABLE_DIRECT_GPU_API is enabled!
    ```

    上記の Python スクリプトでは `CreateEnableGPUDynamicsAttr(False)` で無効にしていますが、手動でテスト環境を構築した場合や、前のチュートリアル（[09: Deformable Body](../core_api/09_deformable_body.ja.md)）の設定が残っている場合は、Physics Scene を選択して **Enable GPU Dynamics** がオフになっていることを確認してください。

### 4-3. テスト足場の動作確認

スクリプト実行後、テスト足場（プリズマティックジョイント）が正しく動作することを確認します：

1. メニューから **Tools > Physics > Physics Inspector** を開きます
2. Stage パネルで `Xform`、`Xform_1`、およびグリッパーのプリムを選択します
3. シミュレーションを開始・停止し、Physics Inspector の**リフレッシュ**ボタンをクリックします
4. **Joint_X** の Drive Target スライダーをドラッグして、グリッパーが前後に移動することを確認します
5. 同様に **Joint_Z** で上下移動を確認します

!!! warning "この段階では指が自由に回転します"
    この時点ではグリッパーの指にドライブが設定されていないため、指がラグドールのように自由に回転します。これは正常な動作で、次のステップでジョイントドライブとミミックジョイントを設定して解決します。

## ステップ 5：ジョイントドライブとミミックジョイントの設定

!!! info "作業ファイル：`Robotiq_2F_85_edit.usd`"
    ドライブとミミックジョイントはグリッパーアセットのリギング設定です。`_edit.usd` を開いた状態で作業してください。

グリッパーの指を制御するためのジョイントドライブとミミックジョイントを設定します。Robotiq 2F-85 は 1 つのモーターで両方の指を同期駆動する構造のため、**メイン駆動ジョイント（`finger_joint`）にのみドライブを設定し、反対側（`right_outer_knuckle_joint`）はミミックジョイントで連動させます**。

### 5-1. メイン駆動ジョイントへのドライブ追加

`finger_joint` に Angular Drive を追加し、力制御で動作するように設定します。

1. Stage パネルで `finger_joint` を選択
2. Properties パネルで **Add > Physics > Angular Drive** をクリック
3. 以下のパラメータを設定：

    | パラメータ | 値 | 説明 |
    |---|---|---|
    | Stiffness | `0.0` | 位置制御を無効化 |
    | Damping | `5,000` | 速度制御のダンピング |
    | Max Force | `180.0` | 最大把持力（ニュートン、データシートに基づく値） |
    | Max Actuator Velocity | `130` deg/s | 最大関節速度（データシートに基づく値） |

!!! note "Stiffness = 0 の意味（力制御）"
    `Stiffness = 0` に設定すると位置制御が無効になり、`Damping` のみで速度制御を行います。これにより、グリッパーが物体を把持する際に、一定のトルクで物体を挟み込む動作が実現できます。位置制御（Stiffness > 0）にすると、物体に接触しても目標位置に到達しようとして過大な力が発生する可能性があります。

!!! note "`right_outer_knuckle_joint` にはドライブを追加しません"
    反対側の指は次節（5-2）でミミックジョイントとして設定します。ミミックジョイントは参照ジョイントのドライブ特性を自動的に継承するため、個別のドライブは不要です（むしろ追加するとドライブ同士が干渉します）。

### 5-2. ミミックジョイントによる左右指の連動

`right_outer_knuckle_joint` をミミックジョイントとして設定し、`finger_joint` の動きに連動させます。

1. Stage パネルで `right_outer_knuckle_joint` を選択
2. Properties パネルで **Add > Physics > Mimic Joint** をクリック
3. 以下のパラメータを設定：

    | パラメータ | 値 | 説明 |
    |---|---|---|
    | Gearing | `-1.0` | 参照ジョイントの動きに対する係数 |
    | Reference Joint | `finger_joint` | 連動元のジョイント |

!!! note "ミミックジョイントとは"
    ミミックジョイントは、参照ジョイントの動きに連動して自動的に動くジョイントです。Gearing は参照ジョイントの位置に対する係数で、`-1.0` を指定すると参照ジョイントが +75° 回転したときに -75° 回転します。Robotiq 2F-85 の左右指のジョイントは内部的に逆方向の軸として定義されているため、`-1.0` で正しく対称な動きになります。

### 5-3. 指の平行性を維持するスプリング

Robotiq 2F-85 グリッパーには、指先を平行に保つためのスプリング機構があります。これを再現するために、外側の指ジョイントに弱い剛性を持つ Angular Drive を設定します：

1. Stage パネルで `left_outer_finger_joint` を選択
2. Properties パネルで **Add > Physics > Angular Drive** をクリック
3. 以下のパラメータを設定：

    | パラメータ | 値 | 説明 |
    |---|---|---|
    | Stiffness | `0.05` | 弱い剛性で平行を維持 |
    | Damping | `0.0` | ダンピングなし |
    | Target Position | `0.0` | 平行な状態を目標位置とする |

4. `right_outer_finger_joint` にも同じ設定を適用します

この設定により、グリッパーが閉じる際に指先が平行を保ちながら動き、物体に接触するまで抵抗なく閉じることができます。

!!! warning "Drive の Stiffness を使うこと"
    ジョイント自体の **Stiffness 属性ではなく**、必ず **Angular Drive の Stiffness** に設定してください。アーティキュレーション内のジョイントでは、ジョイント自体の Stiffness 属性は無視されるため、Drive 経由でのみ剛性を効かせることができます。

    ```
    [omni.physx.plugin] Stiffness attribute is unsupported for articulation joints and will be ignored
    ```

    上記のような警告が出た場合は、ジョイント自体に Stiffness を設定してしまっています。

!!! warning "この設定を忘れると指のリンクが折れて裏返ります"
    外側の指ジョイントに Drive の Stiffness を設定しないと、シミュレーション開始直後に指のリンク（`outer_finger`）が内側に折れて裏返ったような姿勢になり、グリッパーが正常に閉じなくなります。Drive の Stiffness が「指を平行な姿勢に戻すばね」として機能しているためです。

### 5-4. グリッパー単体の動作確認

!!! info "ここからは作業ファイルを `Robotiq_2F_85_config.usd` に切り替えます"
    5-4 以降は動作検証のステップです。`_config.usd` ではテスト足場（プリズマティックジョイント）でグリッパーが固定されているため、シミュレーションを実行しても本体が落下せず、開閉動作の確認がしやすくなります。Layer タブで `_config.usd` を編集ターゲットに切り替えた後、**Stage パネルに戻って `finger_joint` などのプリムを選択して操作してください**（次節以降の変更は `_config.usd` に入っても構いませんが、ドライブ値の最終調整は `_edit.usd` に戻してから記録します）。

ここまでの設定でグリッパー単体が正しく動作するか確認します。`Stiffness = 0`（力制御）に設定したため、`Target Position` は無視され、**`Target Velocity` で駆動方向を指定**します。Physics Inspector の Drive Target スライダーは `Target Position` のみを扱い `Target Velocity` を変更できないため、ここでは `finger_joint` の Angular Drive を直接書き換えて動作を確認します：

1. シミュレーションを開始（再生ボタン）
2. Stage パネルで `finger_joint` を選択
3. Properties パネルの **Angular Drive** セクションを開く
4. **Target Velocity** の値を直接変更して開閉動作を確認：
    - 正の値（例：`+1.0`）にすると指が閉じる
    - 負の値（例：`-1.0`）にすると指が開く
    - ミミック設定により、左右の指が同期して動くことを確認
5. 確認後はシミュレーションを停止し、Target Velocity を `0.0` に戻す

!!! tip "Physics Inspector で位置制御の確認だけ行いたい場合"
    Physics Inspector の Drive Target スライダーは `Target Position` のみを操作するため、力制御（`Stiffness = 0`）の本構成では指は動きません。スライダーで動作確認したい場合は一時的に `Stiffness` に小さな値（例：`100`）を入れる必要がありますが、本チュートリアルの最終構成は速度制御なので、**Angular Drive の `Target Velocity` を直接変更する手順を推奨します**。

### 5-5. 物理ステップの最適化

重い物体（最大ペイロード 2.5 kg）を把持する場合、接触の安定性を確保するためにタイムステップを増やす必要があります：

- Physics Scene の **Steps Per Second** を最低 **80** 以上に設定

!!! tip "ステップ数とパフォーマンスのトレードオフ"
    ステップ数を増やすとシミュレーションの精度が上がりますが、計算コストも増加します。グリッパーの把持が不安定な場合にのみステップ数を増やし、安定している場合はデフォルト値（60）のままで問題ありません。

### 5-6. 把持力の調整テスト

実際の把持動作と把持力を調整するためのテストです。**Max Force = 180 N** はデータシート上の最大値ですが、テストでは小さな値（例：`5.0` N）から始めて、把持の挙動を観察しながら調整します。

1. シリンダーのスケール X を `0.08` に変更（やや太いシリンダー）
2. シリンダーの位置 X を `0.13` に移動
3. `finger_joint` の Angular Drive の **Max Force** を `5.0` に一時的に下げる
4. シミュレーションを実行し、シリンダーが安定して平行把持されることを確認
5. 把持が安定したら、想定する把持物の重量に応じて Max Force を調整（最大ペイロード 2.5 kg 把持なら `180.0` 程度に戻す）

!!! note "なぜ Max Force を一時的に下げるのか"
    最大値（180 N）のままだと、薄いシリンダーや軽い物体に対して過大な把持力がかかり、シリンダーが弾き飛ばされる・物理計算が不安定になるなどの挙動が起きやすくなります。テスト時は小さな値から始めて、把持の挙動を確認しながら適切な値を見つけるのがコツです。

## ステップ 6：コリジョンメッシュとセルフコリジョン

!!! info "作業ファイルを `Robotiq_2F_85_edit.usd` に戻します"

### 6-1. コリジョンメッシュの確認

まず、現在のコリジョン形状を確認します：

1. ビューポート上部の**目のアイコン**をクリック
2. **Show By Type > Physics > Colliders > All** を選択
3. コリジョンが有効なオブジェクトの周りに輪郭線が表示されることを確認

### 6-2. コリジョン近似タイプの調整

指先の接触精度を向上させるために、コリジョン近似タイプを変更します：

1. ビューポートでオブジェクトのコンポーネントを選択
2. Properties パネルの **Physics** セクションを開く
3. **Collider Approximation** のタイプを変更：

| タイプ | 説明 | 用途 |
|---|---|---|
| **Convex Hull** | 凸包による近似 | バランスの取れたパフォーマンスと精度 |
| **Convex Decomposition** | 凸分解による近似 | 複雑な指先の輪郭に最適 |
| **Triangle Mesh** | メッシュそのもの | 最も正確だが計算コストが高い |

!!! tip "指先には Convex Decomposition を推奨"
    指先のメッシュは複雑な形状をしているため、Convex Hull では正確な接触が得られない場合があります。**Convex Decomposition** を使用すると、形状の凹凸をより正確に再現できます。

!!! note "Physics セクションが表示されない場合"
    Properties パネルに Physics セクションが表示されない場合は、Stage ツリーで親または子の Xform を確認してください。コライダーが別の階層のプリムに設定されている場合があります。

!!! warning "Collider Approximation を変更できない場合"
    Collider Approximation のドロップダウンが操作できない、または変更が反映されない場合は、対象メッシュの**親 Xform に `Instanceable` プロパティが設定されていないか**確認してください。`Instanceable` が有効になっていると、子要素のコリジョン近似タイプを個別に変更できません。

    Stage パネルで親 Xform を選択し、Properties パネルで **Instanceable** のチェックを外してから、再度コリジョン近似タイプを変更してください（ステップ 2-5 のマテリアル適用時と同じ対応です）。

### 6-3. セルフコリジョンの有効化

デフォルトでは、同じアーティキュレーション内のリンク同士は衝突しません。グリッパーの指同士が貫通しないように、セルフコリジョンを有効にします：

1. Stage パネルで `/World/Robotiq_2F_85`（アーティキュレーションルートのプリム）を選択
2. Properties パネルの **Articulation Root** セクションで **Self Collision Enabled** にチェックを入れる

これにより、グリッパーの指同士が物理的に干渉するようになり、指が互いを貫通する問題が解消されます。

## ステップ 7：設定の保存

!!! info "作業ファイル：`Robotiq_2F_85_edit.usd` と `Robotiq_2F_85_config.usd`"
    このステップでは両方のファイルを保存します。

テストと検証が完了したら、各ファイルを保存します。

### 7-1. 変更内容の確認と保存

各ステップで正しいファイルで作業していれば、変更は自動的に適切なファイルに記録されているはずです。**Layer** タブを開き、以下を確認してください：

- **`Robotiq_2F_85_edit.usd`**: ジョイント調整、ドライブ、ミミックジョイント、コリジョン設定など、グリッパーのリギングに関する変更が含まれていること
- **`Robotiq_2F_85_config.usd`**: テスト用の Xform、プリズマティックジョイント、グランドプレーン、シリンダーなど、テストシーン固有の要素が含まれていること

確認後、両方のレイヤーで **Save Layer** をクリックして保存します。

!!! tip "変更が間違ったファイルに入ってしまった場合"
    Layer タブで変更が記録されたプリムを確認できます。間違ったファイルに変更が入っている場合は、Layer タブでプリムを正しいレイヤーにドラッグして移動できます。

## ステップ 8：OmniGraph によるグリッパー制御

!!! info "作業ファイル：`Robotiq_2F_85_config.usd`"
    OmniGraph によるグリッパー制御はテストシーン固有の要素です。`_config.usd` を開いた状態で作業してください。

Physics Inspector のスライダーでグリッパーを操作するのは手間がかかります。OmniGraph を使って、Boolean 変数の切り替えだけでグリッパーの開閉を制御する仕組みを構築します。

### 8-1. Action Graph の作成

1. メニューから **Window > Graph Editors > Action Graph** を開く
2. **New Action Graph** アイコンをクリック
3. 作成された Action Graph を `Gripper_Controller` にリネーム

### 8-2. グラフの構成

グリッパー制御グラフは以下のロジックで動作します（次の節で詳細を説明しています）：

1. **Boolean 変数**（開/閉の指示）と **Float 変数**（速度の絶対値）を用意する
2. Boolean 変数に応じて、Float 変数の符号を切り替える（閉じる場合は負、開く場合は正など）
3. 切り替えた値を `finger_joint` の `targetVelocity` に書き込む
4. ミミックジョイントにより、`finger_joint` の動きに連動して右側の指も同期して動く

#### 8-2-1. 変数の追加

このチュートリアルでは、これまで扱っていなかった**変数（Variables）**を使います。Action Graph の変数は、グラフ内のノード間で共有でき、外部から値を変更することでグラフの挙動を制御できます。

1. Action Graph エディターの **Variables** パネル（左側）にある **[+ Add]** ボタンをクリックします
2. 新しい変数が追加されるので、**変数名** をクリックして `close` にリネームします
3. **型**（デフォルトは `Bool`）が `Bool` であることを確認します（必要に応じてドロップダウンから変更）

    ![close 変数の追加](./images/55_add_close_variable.png)

4. 同様にもう 1 つ変数を追加し、名前を `speed` 、型を `Float` に変更します

    ![speed 変数の追加](./images/56_add_speed_variable.png)

!!! tip "変数の型を変更する方法"
    変数の型はリストの **Type** 列のドロップダウンから変更できます。`Bool`、`Int`、`Float`、`String` などの基本型のほか、`Vector3f` など複数要素の型も選択可能です。

#### 8-2-2. ノードの配置と接続

以下の完成形を見本に、Action Graph を構築します：

![Gripper Controller の完成形](./images/57_gripper_controller_action_graph.png)

必要なノードと配置：

1. **On Variable Change** — グラフ実行のトリガー（変数変更時に発火）
2. **Read Variable Node**（`close` 用）— Boolean 変数 `close` を取得
3. **Read Variable Node**（`speed` 用）— Float 変数 `speed` を取得
4. **Boolean Not** — Boolean 変数 `close` の値を反転
5. **To Float** — `close` の値を Float 値に変換（True=1.0、False=0.0）
6. **To Float** — `close` の反転した値を Float 値に変換
7. **Constant Float** — 定数 `-1.0` を出力（開く方向の符号反転に使用）
8. **Multiply** — float 変換した `close` と `speed` を乗算（**閉じる方向**の速度。close=true のとき `+speed`、false のとき `0`）
9. **Multiply** — float 変換した `close` の反転値と `Constant Float` を乗算（close=false のとき `-1.0`、true のとき `0`）
10. **Multiply** — 上記 9 番の結果と `speed` を乗算（**開く方向**の速度。close=false のとき `-speed`、true のとき `0`）
11. **Add** — 開く方向の速度と閉じる方向の速度を加算（どちらか一方が 0 になるため、結果として有効な値が選択される）
12. **Write Prim Attribute** — `finger_joint` の `targetVelocity` に値を書き込む

#### 8-2-3. 各ノードの設定

##### On Variable Change

- **Variable Name** に `close`を選択
- これによって`close`変数変更時に発火します

##### Constant Float

- **Value** に `-1.0` を入力
- この値は閉じる方向に動かすときの符号反転に使用します

##### Write Prim Attribute

ジョイントの目標速度に書き込むノードです。以下のパラメータを設定：

| パラメータ | 値 |
|---|---|
| **Prim** | `/World/Robotiq_2F_85/Robotiq_2F_85/finger_joint` |
| **Attribute Name** | `drive:angular:physics:targetVelocity` |
| **Attribute Type** | `float` |

!!! tip "Prim の指定方法"
    Prim フィールドの右側にあるアイコンから Stage パネルでプリムを選択するか、直接パスを入力できます。プリムパスは `_config.usd` 内のグリッパー配置によって異なる場合があります。Stage パネルで `finger_joint` を選択して正確なパスを確認してください。

#### 8-2-4. 接続のフロー

このグラフは「**開く方向の速度**」「**閉じる方向の速度**」の 2 系統を計算し、それらを足し合わせて最終的な目標速度を作ります。`close` が False のとき開く方向のみが有効値になり、True のとき閉じる方向のみが有効値になります（もう一方は 0 になる）。

**開く方向の経路**（`close = false` のときに `-speed` を出力）：

1. `close` 変数 → **Boolean Not** の Value In
2. **Boolean Not** の Value Out → **To Float**（上側）の Value
3. **To Float**（上側）の Float → **Multiply**（上段）の A
4. **Constant Float** の Value → **Multiply**（上段）の B
5. **Multiply**（上段）の Product → **Multiply**（中段）の A
6. `speed` 変数 → **Multiply**（中段）の B
7. **Multiply**（中段）の Product → **Add** の A

**閉じる方向の経路**（`close = true` のときに `+speed` を出力）：

1. `close` 変数 → **To Float**（下側）の Value
2. **To Float**（下側）の Float → **Multiply**（下段）の A
3. `speed` 変数 → **Multiply**（下段）の B
4. **Multiply**（下段）の Product → **Add** の B

**実行フローと書き込み**：

1. **Add** の Sum → **Write Prim Attribute** の Values
2. **On Variable Change** の Changed → **Write Prim Attribute** の Exec In

#### 8-2-5. 動作の仕組み

このグラフの計算結果は次のようになります：

| `close` の値 | 開く方向の出力 | 閉じる方向の出力 | Add の結果（targetVelocity） |
|---|---|---|---|
| `false`（開く） | `1.0 × (-1.0) × speed = -speed` | `0.0 × speed = 0` | `-speed` |
| `true`（閉じる） | `0.0 × (-1.0) × speed = 0` | `1.0 × speed = +speed` | `+speed` |

つまり、`close = true` のときに正の速度（閉じる方向）、`close = false` のときに負の速度（開く方向）が `finger_joint` の `targetVelocity` に書き込まれます。ステップ 2-3 でジョイントの向きを揃えたため、正の速度がグリッパーを閉じる動きに対応します。

!!! tip "OmniGraph の詳細"
    OmniGraph の基本的な使い方は、[チュートリアル 5: モバイルロボットのリギング](05_rig_mobile_robot.md) で学んだ内容を参考にしてください。グリッパー制御では、差分制御（Differential Controller）ではなくジョイントドライブのターゲット値を直接設定する形になります。

!!! note "なぜ targetPosition ではなく targetVelocity なのか"
    ステップ 5-1 で `finger_joint` のドライブを **力制御**（Stiffness=0、Damping のみ）に設定しました。この設定では位置目標（`targetPosition`）は無視され、速度目標（`targetVelocity`）と Damping によって駆動力が決まります。そのため、ここでは `targetVelocity` を書き換えることでグリッパーを開閉制御します。

### 8-3. 動作確認

1. `speed` 変数の値を設定します（例：`100.0`）
    - Action Graph エディターの **Variables** パネルで `speed` を選択し、**Default Value** に値を入力
2. シミュレーションを開始（タイムラインの Play ボタン）
3. **Variables** パネルで `close` のチェックボックス（Default Value）を切り替えてグリッパーの開閉を確認します
    - **True**（チェックあり）: グリッパーが閉じる方向に移動
    - **False**（チェックなし）: グリッパーが開く方向に移動

![動作確認](images/58_play_closed_loop_rigging.webp)

!!! tip "speed の値の調整"
    `speed` の値が大きすぎると指が勢いよく動きすぎて把持が安定しない場合があります。`50` 〜 `150` 程度から始めて、把持の挙動を見ながら調整してください。

## トラブルシューティング

| 症状 | 原因 | 解決方法 |
|---|---|---|
| セルフコリジョンが機能しない | Articulation Root の設定漏れ | アーティキュレーションルートで **Self Collision Enabled** がチェックされていることを確認 |
| シミュレーション開始時に外側指のリンクが折れて裏返る | 外側指ジョイントの Drive Stiffness 未設定 | `left/right_outer_finger_joint` に **Angular Drive** を追加し Stiffness を `0.05` に設定（ジョイント自体の Stiffness 属性ではない点に注意） |
| 重い物体の把持が不安定 | タイムステップ不足 | Physics Scene の **Steps Per Second** を 80 以上に増加 |
| コリジョンメッシュに隙間がある | 近似タイプが不適切 | 指先メッシュの近似を **Convex Decomposition** に変更 |
| Collider Approximation を変更できない | 親 Xform の Instanceable が有効 | 親 Xform で **Instanceable** のチェックを外す |
| アーティキュレーションループの警告 | Exclude From Articulation 未設定 | `left/right_inner_knuckle_joint` に **Exclude From Articulation** を設定 |
| `setDriveTarget()` 関連のエラーが出る | Physics Scene の GPU Dynamics が有効 | **Enable GPU Dynamics** をオフ。前チュートリアル（Deformable Body）の設定が残っていないか確認 |
| `Stiffness attribute is unsupported for articulation joints` 警告 | ジョイント自体の Stiffness 属性に値を設定 | 該当ジョイントの Angular Drive を追加し、Drive 側の Stiffness で剛性を指定 |
| ジョイントが動かない／グリッパーが固まる | アーティキュレーションのロック（ミミック制約と関節制限の矛盾、過剰な Exclude From Articulation など） | `right_outer_knuckle_joint` の Drive を削除し Mimic Joint のみが設定されているか確認、`Exclude From Articulation` が `inner_knuckle_joint` 以外に付いていないか確認 |

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. **レイヤーベースの編集ワークフロー** — `_base.usd`、`_edit.usd`、`_config.usd` の 3 層構成による非破壊的な設定変更
2. **Payload と Reference の使い分け** — シーン構築での合成方法の選択
3. **ジョイントの可視化と向きの修正** — ギズモを使った確認と Rotation オフセットによる修正
4. **閉ループの分断** — `Exclude From Articulation` を使ってキネマティックツリーに変換
5. **ジョイントドライブの設定** — Stiffness、Damping、Max Force のバランス調整による力制御の実現
6. **ミミックジョイント** — 1 つの入力で複数のジョイントを同期制御
7. **コリジョンメッシュの最適化** — Convex Decomposition による正確な接触判定
8. **セルフコリジョン** — アーティキュレーション内のリンク同士の衝突を有効化
9. **OmniGraph によるグリッパー制御** — Variables を活用した Action Graph での開閉制御

## 次のステップ

次のチュートリアル「[ジョイントドライブゲインの調整](11_joint_tuning.md)」に進み、ジョイントドライブパラメータの最適化方法を学びましょう。
