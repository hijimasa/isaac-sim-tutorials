---
title: 軌道生成（Trajectory Interface）
---

# 軌道生成（Trajectory Interface）

## 概要

Motion Generation 拡張機能は、C 空間・タスク空間の軌道を定義するワークフローを提供します。次の要素で構成されます。

- **Trajectory Interface** … 軌道の抽象インターフェース
- **Articulation Trajectory** … 軌道を Articulation の制御にマッピング
- **Lula Trajectory Generator** … ウェイポイントから軌道を生成する実装

## Trajectory Interface

ロボットの軌道を定義するインターフェースです。`Trajectory` のインスタンスは、指定された時間ホライズン内で、**時間の連続関数**としてロボットの C 空間位置を返す必要があります。4 つの基本アクセサを持ちます。

| アクセサ | 説明 |
|---|---|
| `start_time` | この軌道が C 空間位置を返す最も早い時刻 |
| `end_time` | この軌道が C 空間位置を返す最も遅い時刻 |
| `active_joints` | この軌道が制御する関節名（ターゲットが返される順序に対応） |
| `joint_targets(time)` | `start_time` 〜 `end_time` の時刻に対する関節の位置/速度ターゲット |

`Trajectory` のインスタンスは、`ArticulationTrajectory` の初期化に使うことでロボットを直接制御できます。

## Articulation Trajectory

`ArticulationTrajectory` は、ロボットの Articulation と `Trajectory` のインスタンスで初期化します。定義された軌道からシミュレートロボットの制御へのマッピングを扱い、2 つの主関数を持ちます。

- `get_action_at_time(time)` … 軌道の時間ホライズン内の時刻の `ArticulationAction` を返します。
- `get_action_sequence(timestep)` … 指定 timestep で `start_time` 〜 `end_time` を補間した `ArticulationAction` のリストを返します（物理シミュレータの timestep が固定と分かっている場合の便利メソッド）。

!!! note
    `Trajectory` は与えられた時間ホライズン内でのみロボットの挙動を定義します。生成した `ArticulationAction` 列に従わせる前に、ロボットの Articulation を軌道の初期状態にしておく必要があります。

## Lula Trajectory Generator

C 空間・タスク空間のウェイポイントから `Trajectory` を生成する Lula 実装です。2 つのクラスが提供され、必要な設定情報を共有します。

- `LulaCSpaceTrajectoryGenerator`
- `LulaTaskSpaceTrajectoryGenerator`

**設定ファイル**：URDF（運動学・関節/リンク名・位置リミット）と、Robot Description ファイル（YAML。C 空間の駆動関節、デフォルト C 空間構成、加速度リミット、ジャークリミット、非駆動関節の固定位置）。

### Lula C-Space Trajectory Generator

Robot Description YAML の C 空間座標に対応する一連の C 空間ウェイポイントを受け取り、初速・終速 0 で**スプライン補間**して接続します。軌道は**時間最適**（任意の時点で速度・加速度・ジャークのいずれかのリミットを飽和させ、可能な限り短い所要時間にする）で、`Trajectory` インターフェースのインスタンスを返します。

### Lula Task-Space Trajectory Generator

一連のタスク空間ターゲットとエンドエフェクタフレーム名（URDF の有効なフレーム）を受け取り、可能なら `Trajectory` インスタンスを返します。タスク空間軌道は、位置・姿勢ターゲットの列として定義できます（この場合タスク空間で線形補間されます）。また `lula.TaskSpacePathSpec` クラスで、円弧・純回転・純並進などの便利なプリミティブでウェイポイントを接続することもできます。

内部的には、タスク空間軌道は [Lula Kinematics Solver](kinematics_solver.md) で C 空間軌道に変換され、`LulaCSpaceTrajectoryGenerator` に渡されます。このため、`LulaTaskSpaceTrajectoryGenerator` は `LulaCSpaceTrajectoryGenerator` と同じパラメータに加え、タスク空間→C 空間変換に影響するパラメータを持ちます。

## 関連ページ

- 実践的なチュートリアルは [Lula Trajectory Generator](../06_lula_trajectory_generator.md) を参照してください。
