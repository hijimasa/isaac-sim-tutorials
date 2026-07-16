---
title: 新しいマニピュレータ用の RMPflow 設定
---

# 新しいマニピュレータ用の RMPflow 設定

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- RMPflow に必要な 3 つの設定ファイルと、テンプレート rmpflow_config.yaml の構成
- Lula Test Widget で新しいロボットの RMPflow を検証する方法
- 自己衝突回避（body_cylinders / body_collision_controllers）の設定
- URDF に新しいエンドエフェクタフレームを追加する方法
- ロボット固有パラメータ（joint_velocity_cap_rmp など）の調整

## はじめに

### 前提条件

- [Robot Description と XRDF エディタ](02_robot_description_editor.md) で `robot_description.yaml` を作成できること
- [Lula RMPflow](03_rmpflow.md) の基本を理解していること
- ロボットの Articulation USD アセットを用意していること（[マニピュレータのセットアップ](../robot_setup/06_setup_manipulator.md) 参照）

### 所要時間

約 25〜30 分

### 概要

このチュートリアルでは、Robot Description ファイル作成後に **RMPflow アルゴリズムを完全に設定する**方法を、Denso **Cobotta Pro 900**（6 自由度）を例に学びます。公式チュートリアルには Cobotta Pro 900 の URDF・USD・完成済み `robot_description.yaml` が付属しています。

!!! tip "Lula Test Widget で検証する"
    **Lula Test Widget** は、RMPflow 設定ファイルとステージ上の Articulation を選んでシナリオを実行し、RMPflow が意図通り動くか検証できる拡張機能です。Extensions メニューで有効化し、**Tools > Robotics > Lula Test Widget** からアクセスします。

## RMPflow に必要な 3 つのファイル

ロボットの記述と RMPflow のパラメータ化には 3 つのファイルが必要です。

1. **URDF** … ロボットの運動学、関節・リンク名、各関節の位置リミットを指定します。質量・慣性モーメント・可視/衝突メッシュは無視されるため省略可能です。
2. **Robot Description ファイル（YAML）** … [Robot Description エディタ](02_robot_description_editor.md) で生成する補足ファイル。
3. **RMPflow 設定ファイル（YAML）** … 有効な全 RMP のパラメータを含みます。

このチュートリアルは、URDF と Robot Description ファイルはすでにある前提で、残りの **RMPflow 設定** をテンプレートから Cobotta 用に修正します。

## テンプレート RMPflow 設定ファイル

RMPflow には 50 以上の設定可能パラメータがありますが、これらは類似の運動学構造・長さスケールのロボット間で概ね一般化できます。テンプレート（`./rmpflow_configs/template_rmpflow_config.yaml`）は Franka Emika Panda 向けに調整されていますが、多くの 6・7 自由度アームの良い出発点になります。

このチュートリアルで注目する 3 つのフィールドは次のとおりです。

- **`joint_limit_buffers`** … URDF の関節リミットの内側に人工的なリミットを設けます。形状は `robot_description.yaml` の C 空間と一致させる必要があります。例：`.01` は関節リミットの手前 0.01 ラジアン（prismatic 関節なら 0.01 m）まで駆動することを意味します。
- **`body_cylinders`** … カプセルの集合で「想定上のロボットベース」を定義します（絶対座標の pt1・pt2・radius）。
- **`body_collision_controllers`** … URDF の各フレームに配置する衝突球を定義します。これらの球は body_cylinders のカプセルと接触できません。

```yaml
# 関節を人工的に制限する（例：±pi の関節を ±(pi-.01) に制限）
joint_limit_buffers: [.01, .01, .01, .01, .01, .01, .01]

rmp_params:
    # cspace_target_rmp / joint_limit_rmp / joint_velocity_cap_rmp /
    # target_rmp / collision_rmp / damping_rmp など多数（多くは変更不要）
    joint_velocity_cap_rmp:
        max_velocity: 4.
        velocity_damping_region: 1.5
        damping_gain: 1000.0
        metric_weight: 100.

# ロボットとベースの自己衝突回避を促す想定ベース（カプセル）
body_cylinders:
     - name: base
       pt1: [0, 0, .333]
       pt2: [0, 0, 0.]
       radius: .05

# URDF の各フレームに配置する衝突球
body_collision_controllers:
     - name: end_effector
       radius: .05
```

!!! note "自己衝突回避の範囲"
    RMPflow は、エンドエフェクタとベースの衝突回避を除き、衝突ジオメトリに基づく自己衝突を直接回避しません。ただし多くの用途では、関節リミットで運動学チェーン中間のリンク同士の衝突を防ぐのに十分です。

## ステップ 1：最小限の変更で動かす

Cobotta を RMPflow でターゲット追従させるための最小限の変更です（`./rmpflow_configs/rmpflow_config_basic.yaml`）。

- `rmp_params` は当面無視してよい。
- `joint_limit_buffers` を、テンプレートの 7 個から Cobotta の**6 自由度**に合わせて 6 個にする。
- `body_collision_controllers` の衝突球を置くフレームを変更する。Cobotta の URDF には `end_effector` フレームが無いため、エンドエフェクタ付近の `right_inner_finger` を選ぶ。

```yaml
joint_limit_buffers: [.01, .01, .01, .01, .01, .01]
# rmp_params は省略

body_cylinders:
     - name: base
       pt1: [0, 0, .333]
       pt2: [0, 0, 0.]
       radius: .05

body_collision_controllers:
     - name: right_inner_finger
       radius: .05
```

Lula Test Widget で、ロボットがターゲットを追従し障害物を回避できることを確認します。ただし、RMPflow がターゲットへ動かすフレームはグリッパ中心ではありません（`right_inner_finger` を選んでいるため。利用可能なフレームは URDF 由来で、グリッパ中心のフレームは存在しません）。

## ステップ 2：自己衝突を回避する

Robot Description ファイルがあれば外部障害物は回避しますが、自己衝突は回避しません。産業用アームは関節リミットで自己衝突の大半を排除しているため、ツールは限定的です。基本設定ではエンドエフェクタとベースの衝突を起こしやすいので、より保守的に設定します。

```yaml
body_cylinders:
     - name: base
       pt1: [0, 0, .12]
       pt2: [0, 0, 0.]
       radius: .08
     - name: second_link
       pt1: [0, 0, .12]
       pt2: [0, 0, .12]
       radius: .16

body_collision_controllers:
     - name: J5
       radius: .05
     - name: J6
       radius: .05
     - name: right_inner_finger
       radius: .02
     - name: left_inner_finger
       radius: .02
     - name: right_inner_knuckle
       radius: .02
     - name: left_inner_knuckle
       radius: .02
```

ベースリンク「J1」を半径 .08 m のカプセルで、第 2 リンクを大きめの球で表現し、グリッパの他フレームも覆います。Test Widget で、第 1・第 2 リンクとの衝突がかなり減ることを確認できます（完全には防げませんが、ケースは大幅に限定されます）。

!!! warning "保守的すぎるとマニピュレータビリティを損なう"
    Cobotta で自己衝突を完全に不可能にするには、ベースを非常に保守的に見積もる必要がありますが、その分だけベース周りの可動性を犠牲にします。最適な設定は用途依存です。**自己衝突が観測されない限り、可動性を削る理由はありません**。

## ステップ 3：エンドエフェクタフレームを作成する

選んだ `right_inner_finger` はグリッパの位置を直接表しません。RMPflow がエンドエフェクタとみなすフレームは URDF に存在する必要があります。グリッパ中心を直接制御するには 2 つの選択肢があります。

1. 実行時に、望むターゲットと RMPflow に送るターゲットの間の変換を手動で計算する。
2. **URDF にフレームを追加する**。

このチュートリアルでは 2 の方法を採ります。Cobotta の URDF を調べると、`right_inner_finger` はグリッパベースの `onrobot_rg6_base_link` の孫にあたります。原点オフセットから、`onrobot_rg6_base_link` から Z 方向に `.064495 + .136813 = .2013` オフセットすればグリッパ中心を表せます。指先に近づけるなら Z オフセットを `.24` に増やします。

```xml
<link name="gripper_center"/>
<joint name="gripper_center_joint" type="fixed">
  <origin rpy="0 0 0" xyz="0.0 0.0 .24"/>
  <parent link="onrobot_rg6_base_link"/>
  <child link="gripper_center"/>
</joint>
```

これで、ターゲットの Z 軸がグリッパ中心に沿い、Y 軸がグリッパ平面に整列します。この検証には次の 3 ファイルを使います。

```text
./robot_description.yaml
./cobotta_pro_900_gripper_frame.urdf
./rmpflow_configs/cobotta_rmpflow_config_basic.yaml
```

![Lula Test Widget](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_ref_gui_lula_test_widget.webp)

## ステップ 4：RMPflow パラメータを調整する

残るは `rmpflow_config.yaml` の RMPflow パラメータです。テンプレートは Franka 向けに調整されており、類似スケールのロボットではあまり変更不要です。ただし**ロボット固有**のパラメータが 1 つあります。`joint_velocity_cap_rmp` は、指定した C 空間内の各関節に RMPflow が許す最大速度を設定します。

Cobotta Pro 900 の各関節は URDF で速度リミット 1 rad/s です。RMPflow がこれを尊重するよう、1 rad/s の 0.3 rad/s 手前から減衰を始めるように変更します。

```yaml
joint_velocity_cap_rmp:
    max_velocity: 1.
    velocity_damping_region: .3
    damping_gain: 1000.0
    metric_weight: 100.
```

!!! note "PD ゲインの調整"
    付属の Cobotta USD の PD ゲインは、Franka 向けに選んだ P=10000 N·m / D=1000 N·m·s がベースです。`max_velocity` を 1 rad/s に下げると Cobotta で振動が生じたため、付属 USD では比例ゲイン 10000 N·m・減衰ゲイン 10000 N·m·s に設定されています。各パラメータの意味と新規ロボットでの改善方法は RMPflow Tuning Guide を参照してください。

## まとめ

このチュートリアルでは、次の内容を学びました。

- RMPflow に必要な 3 ファイルと、テンプレート rmpflow_config.yaml の主要フィールド
- Lula Test Widget での検証と、最小構成での動作確認
- body_cylinders / body_collision_controllers による自己衝突回避の調整
- URDF に `gripper_center` フレームを追加してエンドエフェクタを正しく表す方法
- `joint_velocity_cap_rmp` などロボット固有パラメータの調整

## 次のステップ

- GPU 加速のモーション生成は [cuRobo と cuMotion](08_curobo.md) を参照してください。
