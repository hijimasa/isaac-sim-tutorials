---
title: Lula RMPflow
---

# Lula RMPflow

!!! warning "Isaac Sim 6.0 で非推奨（Deprecated）"
    公式ドキュメントでは、このページは Isaac Sim 6.0 で **Deprecated** とマークされました。新規開発には後継の **Robot Motion (Experimental)** API の利用が推奨されています。Lula RMPflow は 6.0 でも引き続き動作します。

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- `RmpFlow` クラスを直接インスタンス化してモーションを生成する方法
- `ArticulationMotionPolicy` でポリシーをロボットに接続する方法
- 動的障害物・ロボットベースの移動に対応させる方法
- サポート済みロボットの設定を名前で簡単に読み込む方法
- 衝突球の可視化などのデバッグ機能

## はじめに

### 前提条件

- [マニピュレータロボットの追加](../core_api/04_adding_a_manipulator_robot.md) を完了していること
- [モーション生成の概要](01_overview.md) と [Robot Description エディタ](02_robot_description_editor.md) を理解していること

### 所要時間

約 25〜30 分

### 概要

**RMPflow** は、動的障害物を回避しながらタスク空間のターゲットへ到達する滑らかなモーションを生成する、反応型のローカルモーションポリシーです。このチュートリアルでは、`RmpFlow` クラスを直接使ってモーションを生成する方法を、基本→世界状態→簡易ロード→デバッグの順に段階的に学びます。

!!! tip "サンプル拡張機能"
    公式ドキュメントには、ターゲット追従・世界認識・デバッグ機能を含む完全な RMPflow サンプル拡張機能（`scenario.py`）が用意されています。以下のコードは、その `scenario.py` を基本機能から完成形へ組み上げていくものです。

## ステップ 1：RmpFlow インスタンスでモーションを生成する

`RmpFlow` クラスを直接インスタンス化するには、3 つの設定ファイル（robot_description / URDF / rmpflow_config）が必要です。これらとエンドエフェクタのターゲットを指定すると、ロボットを目標へ動かすアクションを計算できます。

```python
import numpy as np
import os

from isaacsim.core.utils.extensions import get_extension_path_from_name
from isaacsim.core.utils.stage import add_reference_to_stage
from isaacsim.core.prims import SingleArticulation as Articulation
from isaacsim.core.utils.nucleus import get_assets_root_path
from isaacsim.core.prims import SingleXFormPrim as XFormPrim
from isaacsim.core.utils.numpy.rotations import euler_angles_to_quats
from isaacsim.core.api.objects.cuboid import FixedCuboid

from isaacsim.robot_motion.motion_generation import RmpFlow, ArticulationMotionPolicy

class FrankaRmpFlowExample():
    def __init__(self):
        self._rmpflow = None
        self._articulation_rmpflow = None
        self._articulation = None
        self._target = None

    def load_example_assets(self):
        # Franka とターゲットをステージに追加
        robot_prim_path = "/panda"
        path_to_robot_usd = get_assets_root_path() + "/Isaac/Robots/FrankaRobotics/FrankaPanda/franka.usd"
        add_reference_to_stage(path_to_robot_usd, robot_prim_path)
        self._articulation = Articulation(robot_prim_path)

        add_reference_to_stage(get_assets_root_path() + "/Isaac/Props/UIElements/frame_prim.usd", "/World/target")
        self._target = XFormPrim("/World/target", scale=[.04, .04, .04])
        # core.World に登録できるよう、追加したアセットを返す
        return self._articulation, self._target

    def setup(self):
        # サポート済みロボットの RMPflow 設定は motion_generation 拡張の "/motion_policy_configs" にある
        mg_extension_path = get_extension_path_from_name("isaacsim.robot_motion.motion_generation")
        rmp_config_dir = os.path.join(mg_extension_path, "motion_policy_configs")

        # RmpFlow オブジェクトを初期化
        self._rmpflow = RmpFlow(
            robot_description_path=rmp_config_dir + "/franka/rmpflow/robot_descriptor.yaml",
            urdf_path=rmp_config_dir + "/franka/lula_franka_gen.urdf",
            rmpflow_config_path=rmp_config_dir + "/franka/rmpflow/franka_rmpflow_common.yaml",
            end_effector_frame_name="right_gripper",
            maximum_substep_size=0.00334
        )
        # ArticulationMotionPolicy で rmpflow を Franka の Articulation に接続
        self._articulation_rmpflow = ArticulationMotionPolicy(self._articulation, self._rmpflow)
        self._target.set_world_pose(np.array([.5, 0, .7]), euler_angles_to_quats([0, np.pi, 0]))

    def update(self, step: float):
        # step はこのフレームの経過時間
        target_position, target_orientation = self._target.get_world_pose()
        self._rmpflow.set_end_effector_target(target_position, target_orientation)
        action = self._articulation_rmpflow.get_next_articulation_action(step)
        self._articulation.apply_action(action)

    def reset(self):
        # RmpFlow は明示的に指示しない限りステートレス
        self._target.set_world_pose(np.array([.5, 0, .7]), euler_angles_to_quats([0, np.pi, 0]))
```

**ポイント**

- `RmpFlow` は Motion Policy Algorithm インターフェースの実装です。任意の `MotionPolicy` を `ArticulationMotionPolicy` に渡すとロボットを動かせます。
- `ArticulationMotionPolicy` は、`RmpFlow` とシミュレート Franka の Articulation との**変換レイヤ**として機能します。
- 毎フレーム、エンドエフェクタのターゲットを `RmpFlow` に渡し（`set_end_effector_target`）、`get_next_articulation_action` でアクションを計算して適用します。

![RMPflow](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_4.5_full_tut_gui_rmpflow.webp)

!!! note "組み立てロボットの URDF"
    RMPflow は設定 URDF が与えるロボット構造を考慮します。グリッパを付けた UR10 のように部品を組み立てたロボットで作業する場合は、正しい構造・エンドエフェクタフレームのオフセット・追加の制御関節を反映するよう URDF を更新してください。最終的な組み立て URDF は USD to URDF Exporter で書き出せます。URDF を変更したら、Robot Description ファイルも見直してください。

## ステップ 2：世界状態（障害物・ベース移動）に対応する

`RmpFlow` は動的な衝突回避が可能です。`isaacsim.core.api.objects` で作成したオブジェクトを障害物として登録すると、自動的に衝突を回避します。基本例に対する主な追加は次のとおりです。

```python
# load_example_assets 内：障害物を追加
self._obstacle = FixedCuboid("/World/obstacle", size=.05,
                             position=np.array([0.4, 0.0, 0.65]), color=np.array([0., 0., 1.]))
return self._articulation, self._target, self._obstacle

# setup 内：障害物を RmpFlow に登録
self._rmpflow.add_obstacle(self._obstacle)

# update 内：毎フレーム世界状態とベース姿勢を更新
self._rmpflow.update_world()  # 障害物の現在位置を問い合わせて反映
robot_base_translation, robot_base_orientation = self._articulation.get_world_pose()
self._rmpflow.set_robot_base_pose(robot_base_translation, robot_base_orientation)
```

- `RmpFlow.update_world()` を呼ぶと、追跡中の全オブジェクトの現在状態を問い合わせます。
- オブジェクト位置はワールド座標で問い合わされるため、ロボットのベースが USD ステージ上で動く場合は `RmpFlow.set_robot_base_pose()` を呼ぶことが重要です。ベースが原点から動かない場合は不要なので、この処理は他の世界状態更新と分けています。

## ステップ 3：サポート済みロボットの設定を簡単に読み込む

`RmpFlow` の初期化には 5 つの引数（3 つの設定ファイルパス、エンドエフェクタフレーム名、Euler 積分の最大ステップサイズ）が必要です。NVIDIA Isaac Sim ライブラリのマニピュレータについては、`isaacsim.robot_motion.motion_generation` 拡張機能に設定情報がロボット名で索引付けされており、簡単に読み込めます。

```python
from isaacsim.robot_motion.motion_generation.interface_config_loader import (
    get_supported_robot_policy_pairs,
    load_supported_motion_policy_config,
)

# setup 内：サポート済みロボットの設定を名前で読み込む
print("Supported Robots:", list(get_supported_robot_policy_pairs().keys()))
rmp_config = load_supported_motion_policy_config("Franka", "RMPflow")
self._rmpflow = RmpFlow(**rmp_config)  # 辞書を展開して初期化
```

執筆時点でサポートされているロボット例：`Franka`, `UR3`〜`UR16e`, `Rizon4`, `Cobotta_Pro_900/1300`, `RS007L/N`ほか川崎系, `FestoCobot`, `Techman_TM12`, `Kuka_KR210`, `Fanuc_CRX10IAL`。`load_supported_motion_policy_config()` がサポート済みロボットを読み込む最も簡単な方法です。

## ステップ 4：デバッグ機能

`RmpFlow` クラスには、Motion Policy Algorithm インターフェースには一般に無いデバッグ機能があります。これらは、シミュレータと RMPflow アルゴリズムを切り離して問題を診断するのに役立ちます。

```python
# setup 内（デバッグモード時）
self._rmpflow.set_ignore_state_updates(True)      # ロボットの状態更新を無視
self._rmpflow.visualize_collision_spheres()        # 衝突球を可視化

# ゲインを意図的に悪くして、遅れを観察する
bad_proportional_gains = self._articulation.get_articulation_controller().get_gains()[0] / 50
self._articulation.get_articulation_controller().set_gains(kps=bad_proportional_gains)

# reset 内（デバッグモード時）
self._rmpflow.reset()
self._rmpflow.visualize_collision_spheres()
```

- `visualize_collision_spheres()` は、RMPflow がロボットを妥当に表現しているかを確認できます。
- `set_ignore_state_updates(True)` は Articulation からの状態更新を無視し、返した関節ターゲットが常に完璧に達成されると仮定します。これにより RMPflow は、シミュレート Articulation とは独立した経路を計算します。
- 上の例では Franka に弱い比例ゲインを与えています。可視化により、RMPflow は妥当なモーションを生成しているが、シミュレートロボットが追従できていない（速く動かすと指令位置に大きく遅れる）ことが一目で分かります。

## まとめ

このチュートリアルでは、次の内容を学びました。

- `RmpFlow` + `ArticulationMotionPolicy` でターゲットへの反応型モーションを生成すること
- `add_obstacle` / `update_world` / `set_robot_base_pose` で動的環境・ベース移動に対応すること
- `load_supported_motion_policy_config()` でサポート済みロボットの設定を名前で読み込むこと
- 衝突球の可視化と状態更新の無視でデバッグする方法

## 次のステップ

- 静的環境でのグローバルプランニングは [Lula RRT](04_lula_rrt.md) を参照してください。
- 新しいロボットへの RMPflow 適用は [新しいマニピュレータ用の RMPflow 設定](07_configure_rmpflow_denso.md) を参照してください。
