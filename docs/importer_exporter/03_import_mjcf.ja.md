---
title: MJCF インポート
---

# MJCF インポート

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- MJCF（MuJoCo XML）モデルを Isaac Sim にインポートして USD に変換する方法
- GUI からの対話的なインポート手順
- Python スクリプトによるプログラム的なインポート手順
- インポート後のアーティキュレーション調整の指針

## はじめに

### 前提条件

- Isaac Sim のクイックチュートリアル（基本操作）を完了していること

### 所要時間

約 5〜10 分

### 概要

このチュートリアルでは、MJCF 形式のモデルファイルを Isaac Sim にインポートし、USD 形式に変換する方法を学びます。GUI からの対話的なインポートと、Script Editor を使った Python によるインポートの 2 つの方法を解説します。

!!! note "MJCF とは"
    MJCF（MuJoCo XML Format）は、物理シミュレータ **MuJoCo** で使われるモデル記述形式です。URDF と同様に XML でロボットのボディ（剛体）とジョイントを記述しますが、閉ループ構造やアクチュエータ・センサーの定義など、URDF より表現力の高い項目を持ちます。強化学習の研究では MuJoCo 用に作られたモデル資産が多く存在するため、MJCF を直接インポートできると既存資産をそのまま Isaac Sim に持ち込めます。

## ステップ 1：GUI でのインポート

ここでは、MJCF インポーターエクステンションに同梱されているヒューマノイドのモデル（`nv_humanoid.xml`）をインポートします。

### 1-1. エクステンションの確認

MJCF インポーター（`isaacsim.asset.importer.mjcf`）は通常、Isaac Sim の起動時に自動的にロードされ、**File > Import** メニューから利用できます。もしファイル選択ダイアログのインポート形式に MJCF ファイルが表示されない場合は、**Window > Extensions** を開いて `isaacsim.asset.importer.mjcf` を有効化してください。

### 1-2. サンプル MJCF の場所を確認する

`nv_humanoid.xml` は MJCF インポーターエクステンション自体に同梱されています。場所は次の手順で確認できます：

1. **Window > Extensions** で `isaacsim.asset.importer.mjcf` を検索します。
2. **AUTOLOAD** の横にあるフォルダアイコンをクリックすると、エクステンションのインストール先フォルダが開きます。
3. その中の `/data/mjcf` に `nv_humanoid.xml` があります。

### 1-3. ファイルを選択してインポートする

1. **File > Import** でファイル選択ダイアログを開き、`nv_humanoid.xml` を選択します。
2. インポートオプションを必要に応じて変更します（既定のままでも構いません）。各オプションの詳細は公式の MJCF Importer Extension ドキュメントの Import Options を参照してください。

    ![MJCF インポートダイアログ](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_base_ext-isaacsim.asset.importer.mjcf-2.3.0_gui_0.png)

3. **Import** ボタンをクリックすると、ロボットがステージに追加されます。

    ![インポートされたヒューマノイド](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_base_ext-isaacsim.asset.importer.mjcf-2.3.0_gui_humanoid.png)

## ステップ 2：Python スクリプトによるインポート

GUI と同じことを Python スクリプトでも実行できます。ここではエクステンション同梱のアリ型モデル（`nv_ant.xml`）をインポートします。

1. **Window > Script Editor** で Script Editor を開きます。
2. 以下のコードを Script Editor にコピーします：

```python
import omni.kit.commands
from pxr import UsdLux, Sdf, Gf, UsdPhysics, PhysicsSchemaTools

# 新しいステージを作成
omni.usd.get_context().new_stage()

# インポート設定を作成
status, import_config = omni.kit.commands.execute("MJCFCreateImportConfig")
import_config.set_fix_base(False)            # ベースを固定しない（自由に動けるようにする）
import_config.set_make_default_prim(False)   # デフォルトプリムには設定しない

# エクステンションのインストール先パスを取得
ext_manager = omni.kit.app.get_app().get_extension_manager()
ext_id = ext_manager.get_enabled_extension_id("isaacsim.asset.importer.mjcf")
extension_path = ext_manager.get_extension_path(ext_id)

# MJCF をインポート
omni.kit.commands.execute(
    "MJCFCreateAsset",
    mjcf_path=extension_path + "/data/mjcf/nv_ant.xml",
    import_config=import_config,
    prim_path="/ant"
)

# ステージのハンドルを取得
stage = omni.usd.get_context().get_stage()

# 物理シーンを作成
scene = UsdPhysics.Scene.Define(stage, Sdf.Path("/physicsScene"))

# 重力を設定
scene.CreateGravityDirectionAttr().Set(Gf.Vec3f(0.0, 0.0, -1.0))
scene.CreateGravityMagnitudeAttr().Set(981.0)

# ライトを追加
distantLight = UsdLux.DistantLight.Define(stage, Sdf.Path("/DistantLight"))
distantLight.CreateIntensityAttr(500)
```

3. **Run**（Ctrl + Enter）をクリックすると、アリ型ロボットがインポートされます。

### コードのポイント

| コマンド／設定 | 説明 |
|---|---|
| `MJCFCreateImportConfig` | インポート設定オブジェクトを作成する |
| `set_fix_base(bool)` | ベースリンクをワールドに固定するか。歩行ロボットなら `False` |
| `set_make_default_prim(bool)` | インポートしたロボットをステージのデフォルトプリムにするか |
| `MJCFCreateAsset` | MJCF を解析して `prim_path` で指定したパスにインポートする |

!!! warning "重力の大きさ 981.0 はステージ単位に依存する値"
    公式サンプルコードの `CreateGravityMagnitudeAttr().Set(981.0)` は、**ステージの距離単位がセンチメートル**であることを前提とした値です（981 cm/s² = 9.81 m/s²）。ステージ単位がメートル（近年の Isaac Sim の既定）の場合は `9.81` を指定してください。重力が実際の 100 倍になっていると、ロボットが地面に叩きつけられるなど不自然な挙動の原因になります。

!!! note "地面がないので落下します"
    このサンプルコードは物理シーンと重力を設定しますが、**地面（Ground Plane）は作成しません**。そのままシミュレーションを再生するとロボットは落下し続けます。動作を確認したい場合は、メニューの **Create > Physics > Ground Plane** で地面を追加してから再生してください。

## インポート後の調整

ロボットはステージにインポートされた時点でシミュレーションに使用できます。インポート後のアセットには、センサーの追加、マテリアルの変更、ジョイントドライブや各種設定の更新といった変更を加えることで、より安定したシミュレーションを実現できます。

ロボットはシミュレーション内では**アーティキュレーション**として扱われます。アーティキュレーションのチューニングについては、公式の Articulation Stability Guide のほか、[ロボットセットアップ チュートリアル 11: ジョイントドライブゲインの調整](../robot_setup/11_joint_tuning.md)も参考にしてください。

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. **GUI** による MJCF ファイルのインポート（ヒューマノイドの例）
2. **Python スクリプト**によるインポート（アリ型ロボットの例）と物理シーンのセットアップ
3. インポート後の**アーティキュレーション調整**の指針

### さらに学ぶには

インポートオプションの詳細については、公式の MJCF Importer Extension ドキュメントを参照してください。

## 次のステップ

- [チュートリアル 4: ShapeNet インポーター](04_shapenet_importer.md) - ShapeNet データベースの 3D モデルの取り扱い（現在は非推奨のため代替手順）を紹介します。
