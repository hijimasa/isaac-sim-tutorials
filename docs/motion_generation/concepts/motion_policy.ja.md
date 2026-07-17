---
title: Motion Policy アルゴリズム
---

# Motion Policy アルゴリズム

!!! warning "Deprecated（非推奨）"
    Isaac Sim 6.0 では、この API を含む Motion Generation 拡張機能は非推奨（deprecated）になりました。引き続き動作しますが、新規開発では公式の [Robot Motion (Experimental)](https://docs.isaacsim.omniverse.nvidia.com/latest/robot_motion_experimental/index.html) API の利用を検討してください。

## 概要

Isaac Sim の **Motion Policy** は、単一のロボットを単一のタスク空間ターゲットへ導く、**衝突を考慮した**アルゴリズムで、毎フレームアクションを出力します。`MotionPolicy` クラスは、実装が満たすべき要件を最小限にしつつ、`ArticulationMotionPolicy` クラスと組み合わせて数行でロボットを動かせる完全性を備えたインターフェースです。柔軟な実装として、NVIDIA の Lula ライブラリの [RMPflow](rmpflow.md) が 1 つ提供されています。

広義には、Motion Policy は「ロボットの現在の状態（一般化座標での位置・速度）を受け取り、その状態の望ましい変化量を返す」数学的関数です。`MotionPolicy` インターフェースは、入力として **World State** と **Robot State** の 2 種類の状態を受け取ります。主な出力は次フレームのロボットの位置・速度ターゲットで、内部の世界更新と関節ターゲットの計算を**リアルタイム**（フレームあたり数 ms）で行うことが期待されます。

## アクティブ関節と監視関節（Active / Watched Joints）

USD ロボットの Articulation は、Motion Policy が内部で使う仕様と完全一致するとは限りません。適切なマッピングのため、`MotionPolicy` は次の 2 つの関数を満たします。

- `get_active_joints()` … エンドエフェクタのターゲット達成のために**直接制御**する関節
- `get_watched_joints()` … モーション計画のために**観測するが制御しない**関節

いずれも、Motion Policy が期待する順序で関節名のリストを返します。

!!! note "Franka の例"
    Franka は 9 自由度（アームの回転関節 7＋グリッパの直動関節 2）です。RMPflow は位置ターゲットへの誘導では回転関節 7 つだけを扱います（グリッパはピック＆プレースなどで別途制御するため）。よって `RmpFlow.get_active_joints()` は 7 つの回転関節名を返し、`get_watched_joints()` は空リストを返します。RmpFlow は常に長さ 7 の配列を扱い、`active_joint_positions` などの引数も `get_active_joints()` の順序に従う 7 要素ベクトルを期待します。

## 入力：World State

`isaacsim.core.api.objects` は、シミュレート世界を記述するオブジェクト群を提供します（現状は球・円錐などのプリミティブのみ）。`MotionPolicy` はオブジェクト種別ごとに追加関数（例：`add_sphere(...)`）を持ちます。これらのオブジェクトは USD ステージ上のオブジェクトをラップしており、`MotionPolicy.update_world()` を呼ぶと、渡された全オブジェクトの現在位置を問い合わせて内部の世界状態に渡します。

!!! note "未実装の追加関数"
    すべての種別の追加関数を実装する必要はありません。未実装の関数は警告を出します。たとえば RMPflow は球・カプセル・直方体をサポートし、円錐は無視して各円錐に警告を出します。

## 入力：Robot State

- `set_robot_base_pose()` … ロボットベースの姿勢を指定します。呼ばれない場合、実装は妥当な仮定を置きます（RMPflow はステージ原点と仮定）。
- `compute_joint_targets(active_joint_positions, active_joints_velocities, watched_joint_positions, watched_joint_velocities, ...)` … `get_active_joints()` / `get_watched_joints()` の順序で関節位置・速度を受け取ります。

## 出力：Robot Joint Targets

`compute_joint_targets(...)` は、次フレームのアクティブ関節の位置・速度ターゲットを返します（`active_joint_positions` と同じ形状）。`MotionPolicy` を `ArticulationMotionPolicy` に渡せば、Articulation との状態変換は自動で行われます。

!!! note "位置・速度ターゲットは常に両方返す"
    Motion Policy は位置・速度ターゲットを**常に両方**返します。Isaac Sim のコントローラは片方だけの指定にも対応します。片方だけの挙動に合わせるには、純粋なダンピングには速度ターゲットを 0 に、位置項を実質無効化するには位置ターゲットを現在の関節位置に等しく設定します。

### Articulation Motion Policy

`ArticulationMotionPolicy` は、Articulation と `MotionPolicy` で初期化します。重要な関数は `get_next_articulation_action()` で、Articulation からロボット状態を取得し、適切な関節を抽出・整列して `compute_joint_targets()` を呼び、Articulation に渡せる `ArticulationAction` を生成します。

Franka の例では、Articulation は 9 自由度のターゲットを期待しますが、RmpFlow は 7 自由度のみ制御します。7 ベクトルは 9 ベクトルにマッピングされ、アクション不要の関節は `None` でパディングされます。返される `ArticulationAction` は 9 ベクトルの位置・速度ターゲットを含み、`Articulation.get_articulation_controller().apply_action(...)` で適用できます。

### Motion Policy Controller

`MotionPolicyController` は、Motion Policy を `isaacsim.core.api.controllers.BaseController` のインスタンスにラップします。`isaacsim.robot.manipulators.franka` などの個別ロボット拡張機能はこの `BaseController` を持ち、`RMPFlowController` をインポートして `forward` 関数でロボットをターゲットへ動かせます。

## 関連ページ

- 具体的な実装は [RMPflow](rmpflow.md) を参照してください。
- チュートリアルは [Lula RMPflow](../03_rmpflow.md) を参照してください。
