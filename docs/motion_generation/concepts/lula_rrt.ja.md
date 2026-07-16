---
title: Lula RRT（コンセプト）
---

# Lula RRT（コンセプト）

## 概要

[Path Planner](path_planner.md) インターフェースを満たす、古典的な **RRT（Rapidly-exploring Random Tree）** アルゴリズムの Lula 実装です。

- **C 空間 RRT** … RRT-Connect ベース
- **タスク空間 RRT** … Jacobian 転置（Jacobian transpose）RRT ベース

!!! note
    この RRT 実装は**姿勢（orientation）ターゲットをサポートしません**。

## Lula RRT の設定

新しいロボットで Lula RRT を使うには、3 つのファイルが必要です。

1. **URDF** … ロボットの運動学、関節・リンク名、各関節の位置リミットを指定します（質量・慣性・メッシュは無視され省略可能）。
2. **Robot Description ファイル（YAML）** … C 空間を定義する駆動関節の列挙に加え、デフォルト C 空間構成のセクションを含みます。非駆動関節の固定位置の指定にも使えます。
3. **RRT アルゴリズム設定ファイル（YAML）** … 終了条件・探索重み・ステップサイズなどのパラメータを指定します。これらは `RRT.set_param()` 関数でプログラム的に変更できます。

## 参考文献

- J. J. Kuffner and S. M. LaValle, "RRT-connect: An efficient approach to single-query path planning," ICRA 2000.
- M. Vande Weghe, D. Ferguson and S. S. Srinivasa, "Randomized path planning for redundant manipulators without inverse kinematics," Humanoids 2007.

## 関連ページ

- インターフェースの理論は [Path Planner アルゴリズム](path_planner.md) を参照してください。
- 実践的なチュートリアルは [Lula RRT](../04_lula_rrt.md) を参照してください。
