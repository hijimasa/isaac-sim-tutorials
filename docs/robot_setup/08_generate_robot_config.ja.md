---
title: ロボット設定ファイルの生成
---

# ロボット設定ファイルの生成

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- USD to URDF Exporter を使った URDF ファイルの生成方法
- Robot Description Editor（cuMotion/Lula Robot Description Editor）の使い方
- コリジョンスフィアの生成と調整方法
- cuMotion XRDF ファイルのエクスポート方法
- ツールフレーム（tool_frames）の追加とロボット設定ディレクトリの構成方法

## はじめに

### 前提条件

- [チュートリアル 7: マニピュレータの設定](07_configure_manipulator.md) を完了していること

### 所要時間

約 30 分

### 概要

前回までのチュートリアルでは、UR10e ロボットアームと Robotiq 2F-140 グリッパーをインポートし、物理パラメータを調整しました。しかし、ロボットを自律的に動かすには**モーションプランナー**（RMPFlow や cuMotion）が必要で、これらのプランナーにはロボットの構造情報やコリジョン情報を記述した**設定ファイル**が必要です。

このチュートリアルでは、以下の2つのツールを使って設定ファイルを生成します：

- **USD to URDF Exporter**：USD アセットから URDF ファイルを生成
- **Robot Description Editor（cuMotion/Lula Robot Description Editor）**：コリジョンスフィアの生成と XRDF ファイルのエクスポート

!!! note "設定ファイルの用途"
    生成される設定ファイルは、**cuMotion**（RMPflow を含む）などのモーションプランニングツールで使用されます。次のチュートリアル（ピック＆プレースの例）で実際に活用します。

!!! note "Isaac Sim 6.0 での変更"
    5.1 までは Lula ロボット記述ファイル（YAML）を生成して Lula キネマティクスソルバー／RMPFlow で使用していましたが、6.0 では旧 Lula 系 API（`isaacsim.robot_motion.lula` / `motion_generation`）が非推奨（deprecated）となり、**XRDF ファイルを cuMotion 系モーションプランナーに読み込む**ワークフローに移行しました。

### 使用するアセット

チュートリアル 7 で作成したアセットを使用します。まだ完了していない場合は、Isaac Sim に同梱されているサンプルアセットを代わりに使用できます。画面左下の **Content** タブから以下のパスでアクセスできます：

| アセット | パス | 用途 |
|---|---|---|
| **設定済みアセット** | `Samples > Rigging > Manipulator > configure_manipulator > ur10e > ur > ur_gripper.usd` | チュートリアル 7 の完成アセット |

!!! note "ur_gripper_lula.usd の廃止"
    5.1 まで提供されていた Instanceable 解除済みアセット（`ur_gripper_lula.usd`）は、6.0 の公式チュートリアルからは参照されなくなりました。ステップ 2 の手順に従って自分で Instanceable を解除してください。

## ステップ 1：ロボット URDF の生成

まず、USD アセットから URDF ファイルを生成します。URDF は cuMotion がロボットのキネマティクスを読み込むために必要です。

### 1-1. USD to URDF Exporter エクステンションの有効化

1. Isaac Sim のメニューから **Window > Extensions** を選択します。

2. 検索バーに「**URDF**」と入力します。

3. **Isaac Sim USD to URDF Exporter Extension** を見つけます。

    !!! tip "エクステンションが見つからない場合"
        検索結果にエクステンションが表示されない場合は、検索バー右側の「**@feature**」フィルターを削除してください。

4. **ENABLE** トグルをクリックして有効にします。

5. **AUTOLOAD** チェックボックスをオンにします（次回以降、Isaac Sim の起動時に自動的に読み込まれるようになります）。

![拡張機能の有効化](images/39_enable_extension.png)

### 1-2. URDF ファイルのエクスポート

1. チュートリアル 7 で作成した `ur_gripper.usd` アセットを開きます（Isaac Sim 同梱アセットを使用する場合は `Samples > Rigging > Manipulator > configure_manipulator > ur10e > ur > ur_gripper.usd`）。

2. Isaac Sim のメニューから **File > Export URDF** を選択します。

3. エクスポートダイアログの下部でファイル名を `robot.urdf` に設定します。

    !!! tip "ファイル名を robot.urdf にする理由"
        `robot.urdf` は、ピック＆プレースチュートリアルのスクリプトにおける `--urdf` オプションのデフォルト値と一致します。この名前にしておくと、スクリプト実行時に `--urdf` を明示的に指定する必要がなくなります。

4. ダイアログ下部の **Export Options** セクションで、以下の項目を設定します：

    | 設定項目 | デフォルト値 | 説明 |
    |---|---|---|
    | **Mesh Folder Name** | `meshes` | エクスポート先に作成されるメッシュフォルダの名前。URDF 内のメッシュ参照パスにも使用される |
    | **Mesh Path Prefix** | `file://` | URDF ファイル内でメッシュファイルを参照する際のパスプレフィックス。`file://`（絶対パス URI）、`package://`（ROS パッケージパス）、`./`（相対パス）から選択 |
    | **Package Name** | （空） | **Mesh Path Prefix** で `package://` を選択した場合のみ表示される。ROS パッケージ名を指定する（例：`ur_gripper_description`） |
    | **Root Prim Path** | （空） | エクスポートするロボットのルートプリムパス。空の場合はステージのデフォルトプリムが使用される |
    | **Visualize Collisions** | オフ | オンにすると、非表示に設定されているコリジョンメッシュも URDF に含めてエクスポートする |

    !!! tip "Mesh Path Prefix の選択"
        - **`file://`**（デフォルト）：メッシュファイルを絶対パスの URI で参照します。ローカルでの使用に適しています。
        - **`package://`**：ROS パッケージのパス形式で参照します。ROS 環境でロボットを使用する場合に選択してください。選択すると **Package Name** フィールドが表示されるので、ROS パッケージ名を入力します。
        - **`./`**：相対パスで参照します。URDF ファイルとメッシュフォルダを一緒に移動する場合に便利です。

5. **Export** をクリックしてエクスポートを実行します。

    ![URDF エクスポート](images/40_export_to_urdf.png)

## ステップ 2：Robot Description Editor の準備

### 2-1. Robot Description Editor エクステンションの有効化

1. Isaac Sim のメニューから **Window > Extensions** を選択します。

2. 検索バーに「**isaacsim.robot_setup.xrdf_editor**」と入力します。

3. **cuMotion/Lula Robot Description Editor** エクステンションを見つけます。

    !!! tip "エクステンションが見つからない場合"
        検索結果にエクステンションが表示されない場合は、検索バー右側の「**@feature**」フィルターを削除してください。

4. **ENABLE** トグルをクリックして有効にします。

5. **AUTOLOAD** チェックボックスをオンにします。

![Robot Description Editor エクステンションの有効化](images/41_enable_lula_extension.png)

### 2-2. アセットの準備（Instanceable メッシュの解除）

Robot Description Editor は **Instanceable メッシュ**（インスタンス化されたメッシュ）をサポートしていません。URDF からインポートしたロボットのメッシュには Instanceable が設定されている場合があるため、事前に解除する必要があります。

1. まだ開いていない場合、`ur_gripper.usd` アセットを開きます。

2. **Stage** パネルで、ロボットの `visuals`（ビジュアルメッシュ）と `collisions`（コリジョンメッシュ）プリムをすべて選択します。

    !!! tip "効率的な選択方法"
        Stage パネルの検索機能を使って `visuals` や `collisions` で検索すると、対象のプリムを効率的に見つけることができます。

3. **Property** パネルで **Instanceable** フィールドのチェックを外します。

    ![Instanceable メッシュの解除](images/42_disable_instantiable_mesh.png)

    !!! tip "Instanceable が見つからないときは？"
        選択されているメッシュに**Instanceable**が有効なものと無効なものが混在している可能性があるので、注意深く選択して混在を防ぐ必要があります。

4. **Ctrl + S** で変更を保存します。

## ステップ 3：ジョイントの設定

### 3-1. シミュレーションの開始と Robot Description Editor の起動

Robot Description Editor はシミュレーション実行中に使用する必要があります。

1. ツールバーの **Play** ボタンをクリックしてシミュレーションを開始します。

2. Isaac Sim のメニューから **Tools > Robotics > cuMotion/Lula Robot Description Editor** を選択します。

3. Robot Description Editor ウィンドウが表示されます。

### 3-2. アーティキュレーションの選択

1. Robot Description Editor の **Selection Panel** で、**Select Articulation** に **ur10e** アーティキュレーションのプリムパスを設定します。

2. ロボットの全ジョイントが一覧で表示されます。

![Robot Description Editor ウィンドウ](images/43_lula_robot_description_editor_window.png)

### 3-3. ジョイントステータスの設定

**Set Joint Properties** セクションで、各ジョイントの **Joint Status** を設定します。ここでの設定は、キネマティクスソルバーがどのジョイントを制御対象とするかを決定します。

**UR10e のジョイント**（ロボットアームの6軸）：

| ジョイント名 | Joint Status | 説明 |
|---|---|---|
| shoulder_pan_joint | **Active Joint** | cuMotion が直接制御するジョイント |
| shoulder_lift_joint | **Active Joint** | cuMotion が直接制御するジョイント |
| elbow_joint | **Active Joint** | cuMotion が直接制御するジョイント |
| wrist_1_joint | **Active Joint** | cuMotion が直接制御するジョイント |
| wrist_2_joint | **Active Joint** | cuMotion が直接制御するジョイント |
| wrist_3_joint | **Active Joint** | cuMotion が直接制御するジョイント |

**Robotiq 2F-140 グリッパーのジョイント**（すべて）：

| ジョイント名 | Joint Status | 説明 |
|---|---|---|
| （グリッパーの全ジョイント） | **Fixed Joint** | cuMotion は指定されたデフォルト位置に保持する |

![Robot Description Editor](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_6.0_full_tut_gui_robot_description_editor.png)

!!! note "なぜグリッパーのジョイントを Fixed にするのか"
    グリッパーとアームは通常、別々に制御されます。モーションプランナーの制御空間（cspace）にはアームのジョイントのみを含めれば十分で、グリッパーのジョイントを含めると不要な計算が発生し、コリジョンチェック時にグリッパーが動いてしまう可能性があります。

!!! warning "ジョイントの初期値について"
    Fixed Joint に設定したジョイントのデフォルト位置には、エクスポート時点での Robot Description Editor 上のジョイント位置がそのまま使われます。そのため、マニピュレータの USD での初期ポーズと一致している必要があります。一致していない場合は、タスク初期化時にジョイントのリセットを行ってください。

!!! warning "シミュレーションを停止しないでください"
    次のステップ（コリジョンスフィアの生成）でもシミュレーションの実行が必要です。Robot Description Editor を閉じたり、シミュレーションを停止したりしないでください。

## ステップ 4：コリジョンスフィアの生成

コリジョンスフィアは、ロボットの各リンクの形状を球体で近似したもので、モーションプランナーが障害物との衝突を高速に判定するために使用します。ロボットの各リンクに対して、複数の球体を配置してリンクの形状をカバーします。

### 4-1. コリジョンスフィアの生成手順

以下の手順を**ロボットの各リンク**に対して繰り返します。ここでは `upper_arm_link` を例に説明します。

1. Robot Description Editor の **Link Sphere Editor** セクションを開きます。

2. **Selection Panel / Select link** ドロップダウンから、コリジョンスフィアを生成するリンク（例：`upper_arm_link`）を選択します。

3. **Generate Spheres / Select Mesh** ドロップダウンから、対応するメッシュ（例：`/collisions/upperarm/mesh`）を選択します。

4. 以下のパラメータを設定します：

    | パラメータ | 推奨値 | 説明 |
    |---|---|---|
    | **Radius Offset** | **0.03** | 球体の半径のオフセット（メッシュ表面からのマージン） |
    | **Number of Spheres** | **8** | 生成する球体の数 |

    ![コリジョンスフィア生成対象の選択](images/44_generate_sphere.png)

5. **Generate Spheres** ボタンをクリックします。

6. リンク上に赤い球体が表示されます。生成が完了すると球体がシアン（水色）に変わります。

7. 必要に応じて、球体の位置をドラッグして調整できます。

8. この手順をロボットのすべてのリンク（アームのリンクおよびグリッパーのリンク）に対して繰り返します。選択されていないリンクで生成完了しているメッシュは黄色で表示されます。手先の細かい部分の**Radius Offset**は**0.01**などの小さい値にするのをオススメします。

![コリジョンスフィアの生成](images/45_generate_collision_sphere.png)

公式チュートリアルでは、ur10e + Robotiq 2F-140 の各リンクに対して以下の設定が推奨されています（複数のメッシュエントリを持つリンクは、メッシュごとに球体を生成して同じリンク上で組み合わせます）：

| Select Link | Number of Spheres | Radius Offset | Select Mesh |
|---|---|---|---|
| /shoulder_link | 1 | 0.03 | /collisions/shoulder/mesh |
| /upper_arm_link | 8 | 0.03 | /visuals/upperarm/mesh |
| /forearm_link | 8 | 0.03 | /visuals/forearm/mesh |
| /wrist_1_link | 1 | 0.03 | /visuals/wrist1/mesh |
| /wrist_2_link | 1 | 0.02 | /visuals/wrist3/mesh |
| /wrist_3_link | 1 | 0.02 | /visuals/wrist3/mesh |
| /ee_link/robotiq_arg2f_base_link | 1 | 0.02 | /visuals/robotiq_arg2f_base_link/mesh |
| /ee_link/left_outer_knuckle | 2 | 0.02 | /visuals/robotiq_arg2f_140_outer_knuckle/mesh |
| /ee_link/left_outer_knuckle | 2 | 0.02 | /visuals/robotiq_arg2f_140_outer_finger/mesh |
| /ee_link/left_inner_finger | 2 | 0.02 | /collisions/robotiq_arg2f_140_inner_finger/mesh |
| /ee_link/right_inner_finger | 2 | 0.02 | /collisions/robotiq_arg2f_140_inner_finger/mesh |
| /ee_link/left_inner_knuckle | 2 | 0.02 | /visuals/robotiq_arg2f_140_inner_knuckle/mesh |
| /ee_link/right_inner_knuckle | 2 | 0.02 | /visuals/robotiq_arg2f_140_inner_knuckle/mesh |
| /ee_link/right_outer_knuckle | 2 | 0.02 | /visuals/robotiq_arg2f_140_outer_knuckle/mesh |
| /ee_link/right_outer_knuckle | 2 | 0.02 | /visuals/robotiq_arg2f_140_outer_finger/mesh |

### 4-2. コリジョンスフィアの調整のコツ

コリジョンスフィアの品質はモーションプランニングの性能に大きく影響します。以下のガイドラインを参考にしてください：

| ポイント | 説明 |
|---|---|
| **サイズのバランス** | 球体はリンクの形状を十分にカバーする大きさにしつつ、大きすぎないようにします。大きすぎるとソルバーが障害物のない場所でも衝突と判定し、適切な経路を見つけられなくなります |
| **数と精度のトレードオフ** | 球体の数を増やすとリンク形状の近似精度が向上しますが、ソルバーの計算コストが増加します。精度とパフォーマンスのバランスを考慮してください |
| **メッシュの選択** | 通常はコリジョンメッシュ上に球体を生成します。ビジュアルメッシュの方がリンク形状をより正確に近似できる場合は、そちらを使用してください |
| **長いリンクへの対応** | 長い円筒状のリンクの場合は、両端に球体を生成してから **Connect Spheres** で中間に均等に配置すると効果的です |
| **サイズの調整** | 自動生成された球体のサイズが適切でない場合は、**Scale Spheres in Link** 機能を使って拡大・縮小できます |
| **非閉曲面メッシュ** | 自動球体生成はウォータータイト（閉じた）三角メッシュでのみ動作します。非閉曲面メッシュの場合は、手動で球体を追加して調整してください |

!!! warning "シミュレーションを停止しないでください"
    引き続き次のステップでもシミュレーションが必要です。シミュレーションを停止したり、ファイルを保存したりしないでください。

## ステップ 5：設定ファイルのエクスポート

### 5-1. cuMotion XRDF ファイルのエクスポート

!!! warning "エクスポートまでシミュレーションを停止しないでください"
    シミュレーションを停止すると、ここまでの設定が失われます。

1. Robot Description Editor の下部にある **Export To File > Export to cuMotion XRDF** を展開します。

2. ファイルアイコンをクリックし、ファイル名を `robot.xrdf` に設定します。保存先は、ステップ 1 でエクスポートした URDF ファイルと同じディレクトリにします。

3. エクスポートする **XRDF version** を選択します（**2.0** が推奨です）。

4. **Save** をクリックしてエクスポートを実行します。

5. エクスポートが完了したら、ツールバーの **Stop** ボタンをクリックしてシミュレーションを停止します。

!!! note "XRDF とは"
    XRDF（Extended Robot Description Format）は、cuMotion（CUDA アクセラレーションされたモーションプランニング）で使用されるロボット記述フォーマットです。ジョイントの構成、制御空間の定義、コリジョンスフィアの位置とサイズなどが記述されます。

!!! note "Lula YAML エクスポートの廃止"
    5.1 まで手順に含まれていた Lula ロボット記述ファイル（YAML）のエクスポートは、Lula 系 API の非推奨化に伴い 6.0 の公式チュートリアルから削除されました。

### 5-2. ツールフレームの追加

cuMotion は、XRDF ファイルに**ツールフレーム（tool frame）**が定義されている必要があります。ツールフレームは、ロボットのエンドエフェクタフレームを指定するために使われます。

1. `robot.xrdf` ファイルをテキストエディタで開きます。

2. 以下の行をファイルに追加します：

    ```yaml
    tool_frames: ["wrist_3_link"]
    ```

XRDF ファイルの詳細と cuMotion への読み込み方法については、[cuMotion Robot Configuration Tutorial（公式ドキュメント）](https://docs.isaacsim.omniverse.nvidia.com/latest/cumotion/tutorial_robot_configuration.html) を参照してください。

### 5-3. ロボット設定ディレクトリの構成

ピック＆プレースチュートリアルのスクリプトと `load_cumotion_robot` API は、ロボット設定ファイル一式が単一のディレクトリにまとまっていることを想定しています。エクスポートが完了した時点で、ディレクトリは次のようになっているはずです：

```
/path/to/robot/config/
├── robot.urdf
├── robot.xrdf
├── rmp_flow.yaml
└── meshes/
    └── ...
```

このディレクトリを、チュートリアルスクリプトに `--xrdf-dir /path/to/robot/config` として渡します。

`rmp_flow.yaml` は RMPflow リアクティブモーションコントローラの設定ファイルです。以下の内容を `rmp_flow.yaml` という名前で、`robot.urdf` / `robot.xrdf` と同じディレクトリに保存してください：

```yaml
format: rmpflow
api_version: 2.0

joint_limit_buffers: [.01, .01, .01, .01, .01, .01]

rmp_params:
  cspace_target_rmp:
    metric_scalar: 50.
    position_gain: 100.
    damping_gain: 50.
    robust_position_term_thresh: .5
    inertia: 1.
  cspace_trajectory_rmp:
    p_gain: 80.
    d_gain: 10.
    ff_gain: .25
    weight: 50.
  cspace_affine_rmp:
    final_handover_time_std_dev: .25
    weight: 2000.
  joint_limit_rmp:
    metric_scalar: 1000.
    metric_length_scale: .01
    metric_exploder_eps: 1e-3
    metric_velocity_gate_length_scale: .01
    accel_damper_gain: 200.
    accel_potential_gain: 1.
    accel_potential_exploder_length_scale: .1
    accel_potential_exploder_eps: 1e-2
  joint_velocity_cap_rmp:
    max_velocity: 2.15
    velocity_damping_region: 0.5
    damping_gain: 300.
    metric_weight: 100.
  target_rmp:
    accel_p_gain: 80.
    accel_d_gain: 120.
    accel_norm_eps: .075
    metric_alpha_length_scale: .05
    min_metric_alpha: .01
    max_metric_scalar: 10000.
    min_metric_scalar: 2500.
    proximity_metric_boost_scalar: 20.
    proximity_metric_boost_length_scale: .02
    accept_user_weights: false
  axis_target_rmp:
    accel_p_gain: 200.
    accel_d_gain: 40.
    metric_scalar: 10.
    proximity_metric_boost_scalar: 3000.
    proximity_metric_boost_length_scale: .05
    accept_user_weights: false
  collision_rmp:
    damping_gain: 50.
    damping_std_dev: .04
    damping_robustness_eps: 1e-2
    damping_velocity_gate_length_scale: .01
    repulsion_gain: 1000.
    repulsion_std_dev: .01
    metric_modulation_radius: .5
    metric_scalar: 500.
    metric_exploder_std_dev: .02
    metric_exploder_eps: .001
  damping_rmp:
    accel_d_gain: 30.
    metric_scalar: 50.
    inertia: 100.

canonical_resolve:
  max_acceleration_norm: 50.
  projection_tolerance: .01
  verbose: false

body_capsules:
  - name: base_link
    pt1: [0, 0, 0.22]
    pt2: [0, 0, 0]
    radius: .09

body_collision_controllers:
  - name: wrist_2_link
    radius: .04
  - name: wrist_3_link
    radius: .04
```

これらのファイルが cuMotion でどのように使われるかの詳細は、[cuMotion チュートリアルの Robot Configuration Files セクション（公式ドキュメント）](https://docs.isaacsim.omniverse.nvidia.com/latest/cumotion/tutorial_robot_configuration.html) を参照してください。

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. **USD to URDF Exporter** による URDF ファイル（`robot.urdf`）の生成
2. **Robot Description Editor** のセットアップとアセットの準備（Instanceable の解除）
3. **ジョイントステータスの設定**：アームのジョイントを Active、グリッパーのジョイントを Fixed に設定
4. **コリジョンスフィアの生成**：各リンクに対する球体の配置と調整
5. **cuMotion XRDF ファイル（`robot.xrdf`）** のエクスポートと **tool_frames** の追加
6. **ロボット設定ディレクトリの構成**：`robot.urdf` / `robot.xrdf` / `rmp_flow.yaml` を単一ディレクトリに集約

生成した XRDF ファイルは、cuMotion 系モーションプランナーにそのまま読み込めます。

!!! tip "参考ドキュメント"
    - [Robot Description Editor（公式ドキュメント）](https://docs.isaacsim.omniverse.nvidia.com/latest/manipulators/manipulators_robot_description_editor.html)
    - [USD to URDF Exporter（公式ドキュメント）](https://docs.isaacsim.omniverse.nvidia.com/latest/importer_exporter/export_urdf.html)
    - [cuMotion Robot Configuration Tutorial（公式ドキュメント）](https://docs.isaacsim.omniverse.nvidia.com/latest/cumotion/tutorial_robot_configuration.html)

## 次のステップ

次のチュートリアル「[ピック＆プレースの例](09_pick_and_place.md)」に進み、生成した設定ファイルを使って、cuMotion RMPflow や PINK 微分 IK によるマニピュレーションタスクを実行する方法を学びましょう。
