---
title: モーション生成チュートリアル
---

# モーション生成チュートリアル

<span class="badge badge-advanced">Advanced</span>

Isaac Sim でのマニピュレータのモーション生成（軌道計画・逆運動学・反応制御）のチュートリアルです。

## 概要

Isaac Sim は、マニピュレータのモーション生成に **Lula**（高性能ライブラリ）と **cuRobo**（GPU 加速）を提供します。Lula は RMPflow・RRT・軌道生成・運動学ソルバーを含み、cuRobo はバッチ処理の衝突回避 IK やメッシュ/Nvblox 障害物下での反応制御を追加します。

## チュートリアル

- [モーション生成の概要](01_overview.md) — Lula / cuRobo の全体像
- [Lula Robot Description と XRDF エディタ](02_robot_description_editor.md) — ロボット記述ファイルと衝突球の作成
- [Lula RMPflow](03_rmpflow.md) — 反応型のローカルモーションポリシー
- [Lula RRT](04_lula_rrt.md) — 静的環境でのグローバルパスプランニング
- [Lula Kinematics Solver](05_lula_kinematics.md) — 順運動学・逆運動学
- [Lula Trajectory Generator](06_lula_trajectory_generator.md) — 時間最適な軌道生成
- [新しいマニピュレータ用の RMPflow 設定](07_configure_rmpflow_denso.md) — 新規ロボットへの RMPflow 適用
- [cuRobo と cuMotion](08_curobo.md) — GPU 加速のモーション生成

## コンセプト（理論）

各アルゴリズムの設計思想と理論的背景は [モーション生成のコンセプト](concepts/index.md) にまとめています。

- [Motion Policy アルゴリズム](concepts/motion_policy.md) / [RMPflow（理論）](concepts/rmpflow.md) / [RMPflow チューニングガイド](concepts/rmpflow_tuning_guide.md)
- [Path Planner アルゴリズム](concepts/path_planner.md) / [Lula RRT](concepts/lula_rrt.md)
- [Kinematics ソルバー](concepts/kinematics_solver.md) / [軌道生成](concepts/trajectory_interface.md)
