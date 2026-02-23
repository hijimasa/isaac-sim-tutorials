---
title: URDF エクスポート
---

# URDF エクスポート

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- USD ファイルを URDF 形式にエクスポートする方法
- エクスポートオプション（メッシュパス、ルートプリムパス）の設定
- コリジョンオブジェクトと可視性のマッピング
- エクスポーターの制限事項の理解
- エクスポート結果の検証方法

## はじめに

### 前提条件

- Isaac Sim のクイックチュートリアルを完了していること

### 所要時間

約 10〜20 分

### 概要

このチュートリアルでは、Isaac Sim の USD to URDF Exporter を使用して、USD 形式のロボットファイルを URDF 形式に変換する方法を学びます。コリジョンオブジェクトの取り扱い方法や、エクスポーターの制限事項についても解説します。

## エクスポーターの有効化

1. **Windows > Extensions** から "urdf" を検索し、USD to URDF Exporter を有効化します。

2. **File > Export to URDF** メニューが追加されます。

3. Franka ロボット (`/Isaac/Robots/FrankaRobotics/FrankaPanda/franka.usd`) を読み込み、エクスポートします。

    ![URDF エクスポート](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.1_full_ext-usd_to_urdf_exporter-1.3.3_gui_urdf_export.png)

4. `.urdf` ファイルと `meshes` ディレクトリが生成されることを確認します。

## インポートオプション

### メッシュフォルダ名

`.obj` ファイルの保存先ディレクトリ名を指定します（デフォルト: "meshes"）。

### メッシュパスプレフィックス

| プレフィックス | 説明 |
|--------------|------|
| `file://` | 絶対パス |
| `package://` | パッケージパス（ROS 互換） |
| `./` | 相対パス |

### ルートプリムパス

シーンに複数のロボットが存在する場合、エクスポート対象のロボットプリムを指定できます。

## コリジョンオブジェクトの取り扱い

USD のジオメトリプリムは URDF のビジュアルメッシュとコリジョンメッシュにマッピングされます：

- `PhysicsCollisionAPI` を持つプリム → コリジョンメッシュ
- 可視性が有効なプリム → ビジュアルメッシュ

![USD モデル（球体追加）](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/franka_usd_sphere_mesh_no_collision_visible.png)

コリジョン API の適用と可視性の切り替えにより、URDF 出力が変化することを確認できます。

![URDF ビューア](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/urdf_viewer_franka.png)

## 制限事項

エクスポーターには以下の制限があります：

- キネマティック構造はツリー階層である必要がある
- ジョイントタイプは `prismatic`、`revolute`、`fixed` に限定
- リンクタイプは `Xform` に限定
- センサーはカメラまたは IMU のみ対応
- ジオメトリはキューブ、球体、シリンダー、メッシュのみ対応
- ジオメトリプリムはリーフノードでなければならない

## エクスポート結果の検証

以下の方法で検証できます：

1. エクスポートした URDF を Isaac Sim に再インポート
2. オンライン URDF Viewer でジョイント構造とコリジョンジオメトリを確認

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. **USD to URDF Exporter** の有効化と使用
2. **エクスポートオプション**（メッシュパス、ルートプリムパス）の設定
3. **コリジョンオブジェクト**と可視性の URDF へのマッピング
4. エクスポーターの**制限事項**
5. エクスポート結果の**検証方法**

## 次のステップ

- [チュートリアル 3: MJCF インポート](03_import_mjcf.md) - MuJoCo 形式のファイルをインポートする方法を学びます。
