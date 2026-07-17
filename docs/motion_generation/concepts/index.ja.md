---
title: モーション生成のコンセプト
---

# モーション生成のコンセプト

<span class="badge badge-advanced">Advanced</span>

Isaac Sim のモーション生成 API の設計思想と、各アルゴリズムインターフェースの理論的背景を解説します。

!!! warning "Deprecated（非推奨）"
    Isaac Sim 6.0 では、本セクションが扱う Motion Generation 拡張機能（`isaacsim.robot_motion.motion_generation` / Lula）は非推奨（deprecated）になりました。引き続き動作しますが、新規開発では公式の [Robot Motion (Experimental)](https://docs.isaacsim.omniverse.nvidia.com/latest/robot_motion_experimental/index.html) セクション（Motion Generation (Experimental) API・cuMotion・PINK）の利用を検討してください。

## 概要

Motion Generation は、Isaac Sim 内のオブジェクトを制御する API を提供します。この API は、モーション制御アルゴリズムを Isaac Sim に組み込むための**抽象インターフェース**で構成され、次の 2 つの基本的な役割を持ちます。

- 新しいロボティクスアルゴリズムを Isaac Sim へ統合するのを簡素化する
- 類似アルゴリズムを比較するための標準的な構造を提供する

Motion Generation 拡張機能は、3 つのインターフェースを提供します。

- [Motion Policy アルゴリズム](motion_policy.md)
- [Path Planner アルゴリズム](path_planner.md)
- [Kinematics ソルバー](kinematics_solver.md)

## USD ロボットとアルゴリズムの橋渡し

Isaac Sim では、ロボットはステージに追加された USD ファイルで指定されます。一方、ロボティクスアルゴリズムは独自の方法でロボットの運動学構造やカスタムパラメータを指定します。特定のロボット記述形式に干渉しないよう、Motion Generation のインターフェースには、**USD ロボットとアルゴリズムの間の変換**を助ける関数が含まれています。

具体的には、アルゴリズムは「関心のある関節」と「それらを受け取る順序」を指定できます。この拡張機能が提供するヘルパークラス（**Articulation Motion Policy**、**Path Planner Visualizer**、**Articulation Kinematics Solver**）が、インターフェース関数を使って、USD ロボットの Articulation とアルゴリズム実装の間で関節状態を適切にマッピングします。

!!! note "「Articulation」という語"
    Isaac Sim では、USD で表現されるシミュレートロボットを **Articulation** と呼びます。Motion Generation では、アルゴリズムとシミュレートロボットの橋渡しを担うユーティリティクラスの接頭辞として「Articulation」が使われます。

## このセクションのページ

- [Motion Policy アルゴリズム](motion_policy.md) — 反応型のローカルポリシーの抽象化
- [RMPflow](rmpflow.md) — Riemannian Motion Policy の理論と各 RMP のパラメータ
- [RMPflow チューニングガイド](rmpflow_tuning_guide.md) — 新しいロボットへの調整手順
- [Path Planner アルゴリズム](path_planner.md) — グローバルパスプランニングの抽象化
- [Lula RRT](lula_rrt.md) — RRT-Connect / Jacobian 転置 RRT の実装
- [Kinematics ソルバー](kinematics_solver.md) — 順運動学・逆運動学の抽象化
- [軌道生成（Trajectory Interface）](trajectory_interface.md) — 軌道インターフェースと Lula 軌道生成

!!! tip "API ドキュメント"
    各クラスの詳細な使い方は、Omniverse の Motion Generation Extension API Documentation を参照してください。
