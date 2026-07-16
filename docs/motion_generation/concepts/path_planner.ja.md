---
title: Path Planner アルゴリズム
---

# Path Planner アルゴリズム

## 概要

**Path Planner** は、C 空間（構成空間）のウェイポイント列を出力するアルゴリズムです。これを線形補間すると、開始 C 空間姿勢から C 空間またはタスク空間のターゲット姿勢への**衝突回避パス**になります。`PathPlanner` クラスは、Isaac Sim と連携できるパスプランニングアルゴリズムを定義するためのインターフェースです。実装として NVIDIA の Lula ライブラリの [Lula RRT](lula_rrt.md) が提供されています。

Path Planner は、[Motion Policy アルゴリズム](motion_policy.md) と同じ関数群で USD 世界とやり取りします。独自の内部ロボット表現を持てるため、内部表現と Articulation の間のマッピング用インターフェース関数が用意されています。

## アクティブ関節と監視関節

`PathPlanner` も、Motion Policy と同様に次の 2 関数を満たします。

- `get_active_joints()` … ターゲット達成のために直接制御する関節
- `get_watched_joints()` … 観測するが制御しない関節（パス生成中は一定と仮定）

Franka の例では、9 自由度のうち Lula RRT は位置ターゲットへの誘導で回転関節 7 つだけを扱い、`get_active_joints()` は 7 関節、`get_watched_joints()` は空リストを返します。

## 入力：World State / Robot State

- **World State** … `isaacsim.core.api.objects` のオブジェクトを追加し、`update_world()` で現在位置を問い合わせます（Lula RRT は球・カプセル・直方体をサポート。円錐は無視して警告）。メッシュや点群による高度なオブジェクトは将来のリリースで追加予定です。
- **Robot State** … `set_robot_base_pose()`（未呼び出しなら Lula RRT はステージ原点と仮定）と、`compute_path(active_joint_positions, watched_joint_positions)`。

## 出力：Path

`compute_path(...)` は、線形補間するとターゲット姿勢への衝突回避軌道になる C 空間ウェイポイントの集合を返します（`get_active_joints()` に対応）。ただし、線形補間したパスは C 空間で鋭い角を持つため、そのまま使うのは困難です。それでも、難しい環境で高品質な軌道を生成する有用な部品になります。

## Path Planner Visualizer

`PathPlannerVisualizer` は、Path Planner の出力パスの可視化を容易にするヘルパークラスで、Articulation の制御可能自由度と Path Planner のアクティブ関節のマッピングを扱います。主関数 `compute_plan_as_articulation_actions(max_cspace_dist)` は、Articulation からロボット状態を取得し、`compute_path()` を呼び、結果を線形補間して、順番に Articulation へ渡せる `ArticulationAction` のリストを生成します。`max_cspace_dist` は、出力中の任意の 2 つの C 空間位置間の L2 ノルムがこの値以下になるよう補間密度を決めます。

!!! warning "Visualizer の限界"
    `PathPlannerVisualizer` は名前のとおり**可視化**が目的で、密に線形補間した軌道は時間最適でも滑らかでもありません。理論的に妥当な追従には [Lula Trajectory Generator](trajectory_interface.md) と組み合わせます。

## 関連ページ

- 具体的な実装は [Lula RRT](lula_rrt.md) を参照してください。
- チュートリアルは [Lula RRT](../04_lula_rrt.md) を参照してください。
