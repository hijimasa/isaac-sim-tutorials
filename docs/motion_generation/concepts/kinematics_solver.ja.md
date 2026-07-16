---
title: Kinematics ソルバー
---

# Kinematics ソルバー

## 概要

[Motion Policy アルゴリズム](motion_policy.md) と同様に、**Kinematics ソルバー**は単一の実装を持つインターフェースクラスです。`KinematicsSolver` は順運動学（FK）・逆運動学（IK）を計算でき、NVIDIA の Lula ライブラリによる実装（[Lula Kinematics Solver](../05_lula_kinematics.md)）が提供されています。`KinematicsSolver` は独自の内部ロボット表現を持てるため、内部表現と Articulation の間のマッピング用インターフェース関数が用意されています。

## 関節名（Joint Names）

`KinematicsSolver.get_joint_names()` は、ソルバーが関心を持つ関節とその順序を指定します。移動ベースに載ったロボットアームを考えると、ソルバーはベースを知らずにアームの URDF だけを使えます。この場合、Articulation の多くの関節はソルバーに認識されません。FK では、渡す関節位置が `get_joint_names()` の出力に対応する必要があり、IK の出力も同じ形状になります。Articulation との間のマッピング層は `ArticulationKinematicsSolver` が提供します。

## フレーム名（Frame Names）

`KinematicsSolver.get_all_frame_names()` は、FK / IK の解決時に名前で位置参照できる、ロボットの運動学チェーン内のフレーム一覧を返します。フレーム名は Articulation のフレームと一致する必要はなく、個々のソルバーの設定ファイル構造に由来します。

## ロボットベース姿勢

`set_robot_base_pose()` でロボットベースの位置を指定できます。呼ばれた場合、ソルバーは FK / IK の計算時に適切な変換を適用します。`KinematicsSolver` は**ワールド座標**で動作します。FK の解はベース姿勢に応じて並進・回転され、ワールドフレーム基準のエンドエフェクタ位置を返します。IK の入力もワールド座標で与えられ、ベースフレーム基準に変換されます。ソルバー入力をベースフレーム基準にしたい場合は、ベース姿勢を原点に設定します。

## 衝突考慮（Collision Awareness）

`KinematicsSolver` の実装は外部オブジェクトとの衝突を考慮する必要はありませんが、オプションで可能です。`supports_collision_avoidance() -> bool` で対応可否を示します。対応する場合、Motion Policy と同じ World State 関数群を満たせます。衝突考慮の場合、オブジェクト位置はワールドフレーム基準でしか問い合わせられないため、ベース姿勢を正しく指定することが特に重要です。

## Articulation Kinematics Solver

`ArticulationKinematicsSolver` は、Articulation と Kinematics ソルバー実装の間のマッピングを扱います。

- **順運動学** … ソルバーの FK 関数をラップし、Articulation の関節位置を `get_joint_names()` の順序で渡します。シミュレートロボットのエンドエフェクタの現在位置を簡単に取得できます。
- **逆運動学** … IK をラップし、結果の関節位置を Articulation に直接適用できる `ArticulationAction` として返します。呼び出し時点の Articulation の関節位置が自動的に**ウォームスタート**として使われます。

## Lula Kinematics Solver

`LulaKinematicsSolver` は Kinematics ソルバーインターフェースを実装します。世界のオブジェクトとの衝突回避には対応しません。インターフェースの関数に加え、`set_max_iterations()`（IK が失敗を返すまでの最大反復回数）など内部設定のゲッター/セッターを含みます。

### 設定

新しいロボットで Lula Kinematics を使うには 2 つのファイルが必要です。

1. **URDF** … 運動学、関節・リンク名、位置リミット（質量・慣性・メッシュは省略可能）。
2. **Robot Description ファイル（YAML）** … C 空間の駆動関節の列挙と、デフォルト C 空間構成のセクション。非駆動関節の固定位置の指定にも使えます。

## 関連ページ

- 実践的なチュートリアルは [Lula Kinematics Solver](../05_lula_kinematics.md) を参照してください。
