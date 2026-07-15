---
title: Instanceable Assets
---

# Instanceable Assets（インスタンス化可能なアセット）

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- アセットをインスタンス化可能（instanceable）にするための**階層構造の要件**
- **URDF / MJCF インポーター**でインスタンス化可能なアセットを直接作成する方法
- **既存の USD アセット**をインスタンス化可能に変換するユーティリティスクリプトの使い方

## はじめに

### 前提条件

- [チュートリアル 2: Cloner 入門](02_cloner.md)を完了していること
- [URDF インポート](../importer_exporter/01_import_urdf.md)・[MJCF インポート](../importer_exporter/03_import_mjcf.md)の基本を理解していること

### 所要時間

約 10〜15 分

### 概要

強化学習では、同じロボットのクローンを大量に配置した大規模なシーンで学習を行うのが一般的です。ロボットを増やすほど、ロボットとメッシュのアセット一式ぶんのメモリ消費も増えていきます。

このメモリ消費を抑えるために、USD の [Scenegraph Instancing](https://graphics.pixar.com/usd/dev/api/_usd__page__scenegraph_instancing.html)（シーングラフインスタンシング）機能を利用して、同じロボットの各コピーが共有するメッシュを **instanceable** としてマークできます。こうすると各コピーは**単一のメッシュ実体を参照**するようになり、同じメッシュがシーン内に何個も複製されるのを防いで、シミュレーション全体のメモリ使用量を削減できます。

!!! note "インスタンシングの直感的なイメージ"
    通常の複製が「ロボットの 3D データを 1000 部コピーする」のに対し、インスタンシングは「3D データは 1 部だけ持ち、1000 個の置き場所からそれを参照する」イメージです。見た目や物理挙動は変わりませんが、メッシュデータがメモリ上に 1 つしか存在しなくなります。その代わり、**インスタンス化されたプリムの子孫のプロパティは個別に変更できなくなる**という制約が生まれます。ロボットのメッシュ形状は環境ごとに変わらないので、この制約は通常問題になりません。

## ステップ 1：階層構造の要件を理解する

USD では、インスタンス化されたプリムの**子孫のプロパティを変更することが禁止**されています。ロボットアセットの場合、メッシュのプロパティはシミュレーション中に環境間で異なることがないため、通常は**メッシュプリムだけ**をインスタンス化の対象にします（各リンクの Transform はロボットごとに異なる動きをするため、インスタンス化できません）。

instanceable フラグを機能させるには、アセットのツリー構造を特定の形にしておく必要があります。具体的には、インスタンス化したいメッシュ（またはプリミティブジオメトリ）プリムには、**親となる Xform プリム**が必要です。この親 Xform に、メッシュの定義を持つマスター USD ファイルへの参照（Reference）が追加されます。

たとえば、次の構造はインスタンス化**できません**：

```
World
  |_ Robot
       |_ Collisions
               |_ Sphere
               |_ Box
```

次のように、各メッシュに親 Xform を挟んだ構造に変更する必要があります：

```
World
  |_ Robot
       |_ Collisions
               |_ Sphere_Xform
               |      |_ Sphere
               |_ Box_Xform
                      |_ Box
```

元の `Sphere` や `Box` プリムに Reference が設定されていた場合、それらは `Sphere_Xform` / `Box_Xform` 側に移動する必要があります。

## ステップ 2：URDF / MJCF インポーターで作成する

[URDF インポーター](../importer_exporter/01_import_urdf.md)と [MJCF インポーター](../importer_exporter/03_import_mjcf.md)は、どちらも**インスタンス化可能なアセットとして直接インポートする**オプションをサポートしています。このオプションを選ぶと、インポートされたアセットは上記の階層要件に従った **2 つの USD ファイル**に分割されます：メッシュデータ用の USD と、それを参照するロボット定義本体（マスターステージ）です。

手順：

1. インポート設定で **Create Instanceable Asset** オプションにチェックを入れます。
2. **Instanceable USD Path** テキストボックスに、メッシュデータの保存先ファイルパスを指定します。既定値は `./instanceable_meshes.usd` で、カレントディレクトリに `instanceable_meshes.usd` が生成されます。
3. インポートを実行します。

インポート後、ステージ（マスターステージ）にはロボットの定義が表示されます。Stage パネルでロボットの階層を展開すると、メッシュを子孫に持つ親プリムが **Instanceable** としてマークされ、Instanceable USD Path で指定した USD ファイル内のプリムを参照していることが確認できます。また、子孫のメッシュの属性は変更できなくなっています。

インスタンス化したアセットを新しいステージに追加するときは、**マスター USD ファイルを追加するだけ**で構いません（メッシュ USD は自動的に参照されます）。

## ステップ 3：既存のアセットを変換する

既存の（インスタンス化されていない）アセットは、階層要件の制約があるため、そのままではインスタンス化できるとは限りません。ここでは変換を簡単にするユーティリティスクリプトを 2 つ紹介します。いずれも **Window > Script Editor** から実行します。

### 3-1. メッシュに親 Xform を挿入する（create_parent_xforms）

まず、すべてのメッシュプリムが親 Xform を持つように階層を修正します。次のユーティリティは、ステージ内のすべてのメッシュプリムに対して、新しい Xform プリムを親として自動挿入します：

```python
import omni.usd
import omni.client

from pxr import UsdGeom, Sdf

def create_parent_xforms(asset_usd_path, source_prim_path, save_as_path=None):
    """ source_prim_path 以下の各 Mesh/Geometry プリムに UsdGeom.Xform の親プリムを追加する。
        Mesh/Geometry プリムにマテリアル割り当てがあれば、新しい親プリムに移動する。

        Args:
            asset_usd_path (str): アセットの USD ファイルパス
            source_prim_path (str): ルートプリムの USD パス
            save_as_path (str): 変更後の USD の保存先。None なら同じファイルに上書き保存。
    """
    omni.usd.get_context().open_stage(asset_usd_path)
    stage = omni.usd.get_context().get_stage()

    prims = [stage.GetPrimAtPath(source_prim_path)]
    edits = Sdf.BatchNamespaceEdit()
    while len(prims) > 0:
        prim = prims.pop(0)
        print(prim)
        if prim.GetTypeName() in ["Mesh", "Capsule", "Sphere", "Box"]:
            new_xform = UsdGeom.Xform.Define(stage, str(prim.GetPath()) + "_xform")
            print(prim, new_xform)
            edits.Add(Sdf.NamespaceEdit.Reparent(prim.GetPath(), new_xform.GetPath(), 0))
            continue

        children_prims = prim.GetChildren()
        prims = prims + children_prims

    stage.GetRootLayer().Apply(edits)

    if save_as_path is None:
        omni.usd.get_context().save_stage()
    else:
        omni.usd.get_context().save_as_stage(save_as_path)
```

引数は次のとおりです：

| 引数 | 説明 |
|---|---|
| `asset_usd_path` | 既存の USD アセットのファイルパス |
| `source_prim_path` | アセットのルートプリムの USD パス |
| `save_as_path` | 変更後のアセットの保存先。未指定なら元ファイルを上書き |

```python
create_parent_xforms(
    asset_usd_path=ASSET_USD_PATH,
    source_prim_path=SOURCE_PRIM_PATH,
    save_as_path=SAVE_AS_PATH
)
```

!!! warning "メッシュ上の USD Relationship は失われる"
    この変換では、参照されるメッシュ上の [USD Relationship](https://graphics.pixar.com/usd/dev/api/class_usd_relationship.html) はすべて削除されます。Relationship のターゲットが元のプリム内を指しており、新しいステージからは無効になる可能性があるためです。メッシュに設定されがちな Relationship の例としては、ビジュアルマテリアル、物理マテリアル、コリジョンフィルタのペアなどがあります。これらの Relationship は、メッシュ本体ではなく**親の Xform 側に設定する**ことをお勧めします。

### 3-2. 一括変換する（convert_asset_instanceable）

上記の処理を含む一括変換ユーティリティです。`create_xforms=True` を指定すると親 Xform の挿入から行い、参照用の新しい USD ファイル（`<アセット名>_meshes.usd`）を生成した上で、アセットツリーを走査してメッシュ／プリミティブプリムの親を instanceable としてマークし、メッシュ USD への参照を挿入します：

```python
def convert_asset_instanceable(asset_usd_path, source_prim_path, save_as_path=None, create_xforms=True):
    """ すべての mesh/geometry プリムをインスタンス化可能にする。
        オプションで、mesh/geometry プリムの親として UsdGeom.Xform プリムを追加できる。
        アセット USD ファイルのコピーを作成し、参照用に使用する。
        mesh/geometry プリムの親プリムがコピーした USD ファイルを参照するようにアセットを更新する。

        Args:
            asset_usd_path (str): アセットの USD ファイルパス
            source_prim_path (str): ルートプリムの USD パス
            save_as_path (str): 変更後の USD の保存先。None なら同じファイルに上書き保存。
            create_xforms (bool): mesh/geometry プリムに親 Xform を追加するかどうか。
    """

    if create_xforms:
        create_parent_xforms(asset_usd_path, source_prim_path, save_as_path)
        asset_usd_path = save_as_path

    instance_usd_path = ".".join(asset_usd_path.split(".")[:-1]) + "_meshes.usd"
    omni.client.copy(asset_usd_path, instance_usd_path)
    omni.usd.get_context().open_stage(asset_usd_path)
    stage = omni.usd.get_context().get_stage()

    prims = [stage.GetPrimAtPath(source_prim_path)]
    while len(prims) > 0:
        prim = prims.pop(0)
        if prim:
            if prim.GetTypeName() in ["Mesh", "Capsule", "Sphere", "Box"]:
                parent_prim = prim.GetParent()
                if parent_prim and not parent_prim.IsInstance():
                    parent_prim.GetReferences().AddReference(assetPath=instance_usd_path, primPath=str(parent_prim.GetPath()))
                    parent_prim.SetInstanceable(True)
                    continue

            children_prims = prim.GetChildren()
            prims = prims + children_prims

    if save_as_path is None:
        omni.usd.get_context().save_stage()
    else:
        omni.usd.get_context().save_as_stage(save_as_path)
```

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. インスタンス化可能なアセットに必要な**階層構造の要件**（メッシュの親に Xform）
2. **URDF / MJCF インポーター**の Create Instanceable Asset オプションによる作成
3. **既存アセットの変換**ユーティリティ（`create_parent_xforms` / `convert_asset_instanceable`）

これで Isaac Lab チュートリアルシリーズは完了です。

## 次のステップ

- [Isaac Lab チュートリアル一覧](index.md)に戻る
- 学習そのものに進む場合は [Isaac Lab 公式ドキュメント](https://isaac-sim.github.io/IsaacLab)へ
