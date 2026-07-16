---
title: RMPflow（理論）
---

# RMPflow（理論）

## 概要

**Riemannian Motion Policy（RMP）** は、Isaac Sim のマニピュレータ制御の多くを支えるモーション生成ツール群です。知的な衝突回避を伴う滑らかな軌道を生成します。

RMP は、**加速度ポリシー**と、古典力学の用語を借りて「慣性行列（inertia matrix）」と呼ばれる行列 M(q, q̇) の組です（リーマン計量の概念とも密接に関連します）。**RMPflow** は、リーマン幾何学の枠組みを使い、複数の（時に競合する）目的・制約を表す RMP を、単一のグローバル加速度ポリシーに統合するフレームワークです。ローカル RMP は任意の数の中間タスク空間（エンドエフェクタの作業空間を含む）で定義できます。

広義には、Motion Policy は「ロボットの現在状態（一般化座標での位置・速度）を受け取り、望ましい状態変化を返す」関数です。**加速度ポリシー**は出力が望ましい加速度 q̈ = π(q, q̇) となる Motion Policy で、2 階の微分方程式になります。位置・速度制御では、Euler 積分などの数値積分で加速度ポリシーから位置・速度を得ます。

## RMPflow のデバッグ機能

`RmpFlow` インスタンスと直接やり取りすると、他の Motion Policy 実装にはない機能を使えます。開発者はしばしば、Motion Policy アルゴリズムをシミュレートロボットの Articulation から**切り離し**たいと考えます（例：ロボットの動きが鈍いとき、原因が Motion Policy か PD ゲインかを切り分けたい）。

- `RmpFlow.visualize_collision_spheres()` / `stop_visualizing_collision_spheres()` … 内部の衝突球を可視化します。
- `RmpFlow.visualize_end_effector_position()` / `stop_visualizing_end_effector()` … 公称エンドエフェクタ位置を可視化します。
- `RmpFlow.set_ignore_state_updates(True)` … `compute_joint_targets` に渡される `active_joint_positions` を無視し、物理シミュレーションから独立してロボット状態を内部追跡します。これと可視化を併用すると、望ましくない挙動が RMPflow 由来か、Articulation と PD ゲイン由来かを簡単に判別できます。

## RMPflow の設定

新しいロボットで RMPflow を使うには 3 つのファイルが必要です。

1. **URDF** … 運動学、関節・リンク名、各関節の位置リミット（質量・慣性・メッシュは省略可能）。
2. **Robot Description ファイル（YAML）** … C 空間の駆動関節の列挙、デフォルト C 空間構成、衝突回避用の衝突球セット、非駆動関節の固定位置。
3. **RMPflow 設定ファイル（YAML）** … 有効な全 RMP のパラメータ。

RMPflow は一般的な数学フレームワークで、個々の RMP の形式を規定しません。ただし Lula（したがって Isaac Sim）の実装は、多様なマニピュレーションタスクで滑らかな反応挙動を生むと経験的に確認された、事前定義済みの RMP セットを公開しています。

## 各 RMP とパラメータ

各 RMP は `metric_scalar` または `metric_weight` を 0 にすると無効化できます。以下、目的と主なパラメータを示します（単位は回転関節で q をラジアンと仮定。直動関節ならしきい値はメートル）。

### C-Space Target RMP（c-space_target_rmp）

**目的**：冗長性解決に使うデフォルト C 空間構成を指定します。PD コントローラに似た加速度（位置ゲイン＋ダンピングゲイン）ですが、C 空間距離がしきい値を超えると位置項の大きさが上限で頭打ちになり、ターゲットから遠いときの過大な力を避けます。

| パラメータ | 意味 |
|---|---|
| `metric_scalar` (μ) | 他 RMP に対する優先度重み |
| `position_gain` (k_p) | 位置ゲイン。構成をターゲットへ引く強さ |
| `damping_gain` (k_d) | ダンピングゲイン（「抵抗」の量） |
| `robust_position_term_thresh` (θ) | 位置補正ベクトルが頭打ちになる C 空間距離 |
| `inertia` (m) | 追加の C 空間慣性 |

### Target RMP（target_rmp）

**目的**：エンドエフェクタを指定した位置ターゲットへ駆動します。慣性行列は、ターゲット方向のみを見るランク落ち計量 S = nnᵀ と、全方向を見る単位行列 I の間をブレンドします。ゴールから遠いほど S の寄与が大きく（障害物がシステムを効果的に押せる）、ゴール近くでは I が支配し収束を速めます。

| パラメータ | 意味 |
|---|---|
| `accel_p_gain` / `accel_d_gain` | 位置ゲイン / ダンピングゲイン |
| `accel_norm_eps` (ε) | ターゲットから遠い定加速度域と近くの線形域の遷移を制御する長さスケール |
| `metric_alpha_length_scale` (σ_a) | S と I のブレンドを制御するガウシアンの長さスケール |
| `min_metric_alpha` | 等方 M_near 項の最小寄与 |
| `max_metric_scalar` (μ_near) / `min_metric_scalar` (μ_far) | 等方 M_near / 方向性 M_far の計量スカラー |
| `proximity_metric_boost_scalar` (b) / `proximity_metric_boost_length_scale` (σ_b) | ターゲット近傍でのブースト強度 / 長さスケール |

### Axis Target RMP（axis_target_rmp）

**目的**：姿勢ターゲットが設定されている場合に、制御フレーム（エンドエフェクタなど）の向きをターゲット姿勢に合わせます。位置ターゲットへの距離に依存する「優先度ブースト」を含み、姿勢を詰める前に位置ターゲットへ進めるようにします。

主なパラメータ：`accel_p_gain` / `accel_d_gain` / `metric_scalar` / `proximity_metric_boost_scalar` / `proximity_metric_boost_length_scale`。

### Joint Limit RMP（joint_limit_rmp）

**目的**：関節リミットを回避します。適切に調整すれば、リミット回避以外の挙動は変わりません。

主なパラメータ：`metric_scalar`、`metric_length_scale`（リミット接近時の計量の立ち上がり）、`metric_velocity_gate_length_scale`（障壁方向の速度に伴う計量増加率）、`accel_damper_gain` / `accel_potential_gain`、`accel_potential_exploder_length_scale`（位置障壁の急峻さ）ほか。

### Joint Velocity Limit RMP（joint_velocity_cap_rmp）

**目的**：各関節の速度に上限を設けます。ロボット固有のパラメータで、URDF の速度リミットに合わせます。

| パラメータ | 意味 |
|---|---|
| `max_velocity` (v_max) | 許容する最大速度の大きさ（rad/s） |
| `velocity_damping_region` (v_r) | ダンピングの影響を受ける速度領域の幅 |
| `damping_gain` (k_d) | ダンピングゲイン |
| `metric_weight` (μ) | 優先度重み |

### Collision Avoidance RMP（collision_rmp）

**目的**：Robot Description の衝突球と外部障害物の衝突を回避します。

主なパラメータ：`repulsion_gain` / `repulsion_std_dev`（位置反発項のゲイン / 距離依存）、`damping_gain` / `damping_std_dev`、`metric_modulation_radius`（RMP を完全に無効化する障害物からの距離）、`metric_scalar`、`metric_exploder_std_dev` / `metric_exploder_eps` ほか。

### Damping RMP（damping_rmp）

**目的**：ジャークを抑えるための非線形ダンピングを加えます。

| パラメータ | 意味 |
|---|---|
| `accel_d_gain` (k_d) | 非線形ダンピングゲイン |
| `metric_scalar` (μ) | 優先度重み |
| `inertia` (m) | 追加の慣性 |

## 関連ページ

- 新しいロボットへの調整手順は [RMPflow チューニングガイド](rmpflow_tuning_guide.md) を参照してください。
- 実践的なチュートリアルは [Lula RMPflow](../03_rmpflow.md) を参照してください。
- インターフェースの理論は [Motion Policy アルゴリズム](motion_policy.md) を参照してください。
