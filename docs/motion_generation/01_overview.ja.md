---
title: モーション生成の概要
---

# モーション生成の概要

!!! warning "Isaac Sim 6.0 で非推奨（Deprecated）"
    公式ドキュメントでは、このページ（Motion Generation）は Isaac Sim 6.0 で **Deprecated** とマークされました。新規開発には、後継の **Robot Motion (Experimental)** API（`isaacsim.robot_motion.experimental.motion_generation`）や **cuMotion 統合**・**PINK 統合** の利用が推奨されています。本セクションの Lula 系機能は 6.0 でも引き続き動作します。

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- Isaac Sim のモーション生成ツール群（Lula / cuRobo）の全体像
- RMPflow・RRT・軌道生成・運動学ソルバーそれぞれの役割
- インタラクティブ例と Standalone 例の実行方法

## はじめに

### 前提条件

- Isaac Sim 6.0 が起動できること
- マニピュレータ（アーム型ロボット）と Articulation の基礎を理解していること

### 所要時間

約 10 分

### 概要

**Lula** は、ロボットマニピュレーションのための高性能なモーション生成ライブラリです。Isaac Sim は Lula を通じて次の機能を提供します。

- **RMPflow** … タスク空間のターゲットへマニピュレータを導く、リアルタイム・反応型のローカルポリシー。動的障害物を回避します。
- **RRT（Rapidly-exploring Random Tree）** … RRT-Connect や JT-RRT を含む、静的環境でのグローバルプランニングソルバー。
- **軌道生成（Trajectory Generation）** … c 空間（C-space：構成空間。各関節の角度が張る空間で、関節空間とも呼ばれます）・タスク空間（エンドエフェクタの位置・姿勢の空間）の一連の移動として記述されたパスに対して、時間最適な軌道を生成するツール。
- **運動学ソルバー（Kinematics Solver）** … 上位のモーション生成ツールを支える、高性能な順運動学・逆運動学ソルバーへのインターフェース。

さらに Isaac Sim は、GPU で高速化されたモーション生成ライブラリ **cuRobo** ともインターフェースします。cuRobo は、バッチ処理による衝突回避 IK、衝突回避モーションプランニング、メッシュや Nvblox（深度カメラなどの入力から環境の 3D 占有情報を GPU 上で再構成する NVIDIA のマッピングライブラリ）のマップで表現された障害物下での反応制御などを追加します。

## モーション生成ツール一覧

| ツール | 説明 |
|---|---|
| [Lula Robot Description と XRDF エディタ](02_robot_description_editor.md) | ロボット記述ファイル（衝突球など）を作成・編集する |
| [Lula RMPflow](03_rmpflow.md) | 反応型のローカルモーションポリシー |
| [Lula RRT](04_lula_rrt.md) | 静的環境でのグローバルパスプランニング |
| [Lula Kinematics Solver](05_lula_kinematics.md) | 順運動学・逆運動学ソルバー |
| [Lula Trajectory Generator](06_lula_trajectory_generator.md) | 時間最適な軌道生成 |
| [新しいマニピュレータ用の RMPflow 設定](07_configure_rmpflow_denso.md) | 新規ロボットに RMPflow を適用する |
| [cuRobo と cuMotion](08_curobo.md) | GPU 加速のモーション生成 |

## 例の実行方法

### インタラクティブ例

**Windows > Examples > Robotics Examples** で Robotics Examples タブを開き、右側の Information タブの手順に従って実行します。

- **Follow Target Example**：Manipulation > Follow Target
- **RoboFactory Example**：Multi-Robot > RoboFactory
- **RoboParty Example**：Multi-Robot > RoboParty

!!! note "ワールドのリセット"
    このワークフローでは、STOP → PLAY を押してもワールドが正しくリセットされないことがあります。代わりに **RESET** ボタンを使ってください。

### Standalone 例

`<isaac_sim_root_dir>` に移動し、Linux なら `./python.sh`、Windows なら `python.bat` で実行します。

```bash
# RMPflow でターゲットを追従（Franka）
./python.sh standalone_examples/api/isaacsim.robot.experimental.manipulators/franka/follow_target_with_rmpflow.py

# RMPflow でターゲットを追従（UR10）
./python.sh standalone_examples/api/isaacsim.robot.experimental.manipulators/universal_robots/follow_target_with_rmpflow.py

# IK でターゲットを追従（UR10）
./python.sh standalone_examples/api/isaacsim.robot.experimental.manipulators/universal_robots/follow_target_with_ik.py
```

## まとめ

このチュートリアルでは、次の内容を学びました。

- Lula が RMPflow・RRT・軌道生成・運動学ソルバーを提供すること
- cuRobo が GPU 加速のモーション生成（バッチ IK・衝突回避プランニング）を追加すること
- インタラクティブ例と Standalone 例の実行方法

## 次のステップ

- [Lula Robot Description と XRDF エディタ](02_robot_description_editor.md) から、ロボット記述の作成を学びます。
