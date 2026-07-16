---
title: URDF インポート
---

# URDF インポート

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- URDF ファイルを Isaac Sim にインポートして USD に変換する方法
- インポート設定（ベースタイプ、密度、ジョイントドライブ、コリジョン）の構成
- コリジョンメッシュの可視化と確認方法
- 組み込みサンプル（Robotics Examples）を使ったインポートの流れ
- Python スクリプトによるプログラム的なインポート
- ROS 2 ノードからの URDF（XACRO）インポート

## はじめに

### 前提条件

- Isaac Sim のクイックチュートリアル（基本操作）を完了していること
- Python スクリプトの節では [Core API チュートリアル 1: Hello World](../core_api/01_hello_world.md) の Hello World サンプルを使用します

### 所要時間

約 10〜15 分

### 概要

このチュートリアルでは、URDF ファイルを Isaac Sim にインポートし、USD 形式に変換する方法を学びます。具体的には以下の 4 つの方法を順に解説します：

1. **GUI での直接インポート** — メニュー操作だけで URDF を読み込む基本の方法
2. **組み込みサンプルからのインポート** — Robotics Examples に用意された例で流れを体験する
3. **Python スクリプトによるインポート** — パイプラインへの組み込みに適したプログラム的な方法
4. **ROS 2 ノードからのインポート** — 既存の ROS 2 ワークフローと連携する方法（Linux のみ）

!!! note "URDF とは / なぜ変換が必要か"
    URDF（Unified Robot Description Format）は、ROS で標準的に使われるロボット記述形式です。XML でロボットのリンク（剛体）とジョイント（関節）の構成、質量、コリジョン形状などを記述します。

    一方、Isaac Sim はシーンやロボットを **USD（Universal Scene Description）** 形式で扱います。そのため URDF のロボットを Isaac Sim で使うには、URDF → USD の**変換（インポート）**が必要です。インポートは一方向の変換であり、元の URDF ファイルが書き換えられることはありません。

    逆方向（USD → URDF）の変換は[次のチュートリアル](02_export_urdf.md)で扱います。

## ステップ 1：GUI での直接インポート

ここでは、URDF インポーターエクステンションに同梱されている Franka Panda の URDF（`panda_arm_hand.urdf`）をインポートします。

### 1-1. エクステンションの有効化

URDF インポーター（`isaacsim.asset.importer.urdf`）は通常、Isaac Sim の起動時に自動的にロードされます。もし読み込まれていない場合は、**Window > Extensions** を開いて `isaacsim.asset.importer.urdf` を検索し、有効化してください。

![エクステンション有効化](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_full_tut_gui_import_urdf_enable_extension.png)

### 1-2. サンプル URDF の場所を確認する

今回使う `panda_arm_hand.urdf` は、URDF インポーターエクステンション自体に同梱されています。ファイルの場所は次の手順で確認できます：

1. **Window > Extensions** で `isaacsim.asset.importer.urdf` を検索します。
2. **AUTOLOAD** の横にあるフォルダアイコンをクリックすると、エクステンションのインストール先フォルダが開きます。
3. その中の `/data/urdf/robots/franka_description/robots` に `panda_arm_hand.urdf` があります。このパスをコピーしておきます。

### 1-3. ファイルを選択する

**File > Import** を開き、ファイル選択ダイアログのナビゲーションバーに先ほどコピーしたパスを貼り付けて、`panda_arm_hand.urdf` を選択します。

![ロボット選択](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_full_tut_gui_import_urdf_select_robot.png)

### 1-4. インポート設定を構成する

URDF ファイルを選択すると、ファイル選択ダイアログの右側に **Options** ペイン（インポート設定）が表示されます。設定は Model / Links / Joints & Drives / Colliders のセクションに分かれています。Franka（固定ベースのマニピュレータ）の場合は以下のように設定します：

| セクション | 設定項目 | 今回の設定 | 説明 |
|---|---|---|---|
| Model | **USD Output** | 既定のまま | 変換後の USD ファイルの保存先。既定（`Same as Imported Model(Default)`）では URDF と同じディレクトリになる |
| Links | **Moveable Base / Static Base** | Static Base | ベースを固定するか（マニピュレータ＝固定、モバイルロボット＝移動）。Franka では既定で Static Base が選択されている |
| Links | **Default Density** | 既定（`0.0`）のまま | 質量が未定義のリンクに適用する密度。`0.0` なら既定値を使用 |
| Joints & Drives | **Natural Frequency** | 既定より大きめに | ジョイントドライブの応答特性。**Joint Configuration** で Stiffness / Natural Frequency のどちらで指定するかを選び、ジョイントごとの表で値を設定する。大きくすると動作中の振動が減る |
| Colliders | **Allow Self-Collision** | オン | ロボット自身のリンク同士の衝突判定を有効にするか |

上記以外の項目は既定のままで構いません。

!!! warning "出力先ディレクトリの書き込み権限"
    インポート時の出力先ディレクトリには**書き込み権限が必要**です。既定の出力先は URDF ファイルと同じディレクトリになるため、エクステンション同梱のサンプルのように読み取り専用の場所にある URDF をインポートする場合は、**USD Output** を書き込み可能な場所に変更してください。

!!! note "Natural Frequency（固有振動数）とは"
    Isaac Sim のジョイントドライブは PD 制御（Stiffness / Damping）で駆動されますが、URDF インポーターではこれらを直接指定する代わりに、**Natural Frequency（固有振動数）**という抽象化されたパラメータで応答の速さを指定できます。値を大きくするほどジョイントは目標値に素早く追従し、動作中の振動（オシレーション）が抑えられます。

    Stiffness / Damping と Natural Frequency の関係や、インポート後の再調整については[ロボットセットアップ チュートリアル 11: ジョイントドライブゲインの調整](../robot_setup/11_joint_tuning.md)で詳しく解説しています。

### 1-5. インポートを実行する

**Import** ボタンをクリックすると、**URDF Confirm Path** ダイアログが表示され、変換後の USD ファイルの保存先が確認できます。**Yes** をクリックするとインポートが実行され、ロボットがステージに追加されます。

![URDF Confirm Path ダイアログ](images/01_urdf_confirm_path.png)

同じ場所に一度インポートしたことがある場合は、続けて **URDF Confirm Overwrite** ダイアログが表示されます。上書きしてよければ **Yes** をクリックします。

![URDF Confirm Overwrite ダイアログ](images/01_urdf_confirm_overwrite.png)

!!! warning "確認ダイアログが他のウィンドウの背後に隠れることがある"
    環境によっては、この確認ダイアログが**ファイル選択ウィンドウや Extensions ウィンドウの背後に隠れて表示される**ことがあります。その間はメインウィンドウ全体がクリックに反応しなくなるため、フリーズしたように見えます。Import ボタンを押した後に操作できなくなった場合は、手前のウィンドウをドラッグで移動（または閉じる）して、隠れているダイアログの **Yes / No** に応答してください。

![インポート結果](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_full_tut_viewport_import_urdf_franka.png)

!!! note "モバイルロボット（車輪型）をインポートする場合"
    車輪で移動するロボットをインポートする場合は、次の設定に変更します：

    - **Moveable Base** を選択する
    - 速度制御するジョイント（車輪）のドライブタイプを **Velocity**、位置制御するジョイント（ステアリング）を **Position** に設定する
    - **Joint Drive Strength** を必要なレベルに設定する。この値はジョイントの **Damping** としてインポートされます（Velocity ドライブでは Stiffness は常に 0 になります）

!!! note "トルク制御ロボット（四足歩行ロボットなど）をインポートする場合"
    脚をトルクで直接制御するロボットの場合は、次のように設定します：

    - **Moveable Base** を選択する
    - トルク制御するジョイント（脚）のドライブタイプを **None**、それ以外のジョイントを **Position** または **Velocity** に設定する
    - **None** ドライブのジョイントでは Stiffness / Damping は効果を持たず、0 としてインポートされます

## ステップ 2：コリジョンメッシュの可視化

すべてのリジッドボディがコリジョンプロパティを持つとは限らず、また、コリジョンメッシュは見た目用のビジュアルメッシュより簡略化された形状であることが一般的です。意図した通りにコリジョンが設定されているかは、インポート後に目視で確認しておくと安心です。

ビューポートでコリジョンメッシュを可視化する手順：

1. ビューポート左上の**目のアイコン**をクリックします。
2. **Show By Type** にカーソルを合わせます。
3. **Physics** にカーソルを合わせます。
4. **Colliders** にカーソルを合わせます。
5. **All** を選択します（None / Selected / All の 3 択です）。

![Colliders 表示メニュー](images/01_show_colliders_menu.png)

コリジョンメッシュがワイヤーフレーム（ピンク〜緑色の線）で重ねて表示されます。

!!! note "ワイヤーフレームが表示されない場合"
    環境やアセットによっては、**All** を選択してもワイヤーフレームがすぐに反映されないことがあります。その場合は、ビューポートのカメラを動かす、対象のプリムに近づく、あるいは一度シミュレーションを再生するなどして表示が更新されるか確認してください。

![コリジョンメッシュ](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_full_tut_viewport_import_urdf_visualize_franka_colliders.png)

## ステップ 3：組み込みサンプルからのインポート

Isaac Sim には、インポートから駆動設定・シミュレーションまでの一連の流れを体験できるサンプルが組み込まれています。

**Window > Examples > Robotics Examples** を有効にすると、画面下部のドックに **Robotics Examples** タブが表示されます。サイドバーの **IMPORT ROBOTS** セクションには 4 つの例が用意されています：

- Carter URDF（モバイルロボット。公式ドキュメントでは Nova Carter URDF と表記されていますが、実際の UI 上の表記は Carter URDF です）
- Franka URDF（マニピュレータ）
- Kaya URDF（モバイルロボット）
- UR10 URDF（マニピュレータ）

!!! note "マテリアルの読み込みを待つ"
    これらのサンプルではマテリアルの読み込みに時間がかかることがあります。UI 右下のプログレス表示で進行状況を確認できます。

それぞれインポート設定とインポート後のセットアップ内容は異なりますが、使い方は共通です：

1. **Robotics Examples** タブで **IMPORT ROBOTS > （ロボット名） URDF** をクリックすると、右側に例のパネルが開きます。
2. **Command Panel** の **Load Robot** 行にある **LOAD** ボタン — URDF をステージにインポートし、地面・ライト・物理シーンを追加します。
3. **Configure Drives** 行にある **CONFIGURE** ボタン — 各ジョイントドライブの Stiffness / Damping を設定します。
4. パネル右上の**鉛筆アイコン（Open Source Code）** — この一連の処理を Python API でどう実装しているか、ソースコードを確認できます。
5. 左側ツールバーの **PLAY** ボタン — シミュレーションを開始します。
6. **Move to Pose** 行にある **MOVE** ボタン — ロボットをホーム（休止）姿勢へ動かします。

![UI 統合例](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_full_ext-isaacsim.asset.importer.urdf-2.3.0_gui_example_import_franka.png)

## ステップ 4：Python スクリプトによるインポート

Import ウィンドウで行っていた操作は、Python スクリプトでも実行できます。ここでは URDF をプログラム的にインポートし、さらにインポートしたロボットを `isaacsim.robot.manipulators.examples.franka` エクステンションの **FollowTarget** タスク（ターゲットを追従するタスク）に組み込んで動かします。

### 4-1. Hello World サンプルを開く

1. メニューバーから **Window > Examples > Robotics Examples** をクリックします。
2. 画面下部の **Robotics Examples** タブで **GENERAL > Hello World** を選択します。
3. Hello World のパネル（Information / World Controls）が表示されることを確認します。
4. パネル右上の**鉛筆アイコン（Open Source Code）**をクリックして、Visual Studio Code でソースコードを開きます。

### 4-2. コードを編集する

`hello_world.py` を以下のように書き換えます：

```python
from isaacsim.examples.interactive.base_sample import BaseSample
from isaacsim.core.utils.extensions import get_extension_path_from_name
from isaacsim.asset.importer.urdf import _urdf
from isaacsim.robot.manipulators.examples.franka.controllers.rmpflow_controller import RMPFlowController
from isaacsim.robot.manipulators.examples.franka.tasks import FollowTarget
import omni.kit.commands
import omni.usd

class HelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        return

    def setup_scene(self):
        # ワールドオブジェクトを取得してシミュレーション環境をセットアップ
        world = self.get_world()

        # ロボットが接地するデフォルトの地面を追加
        world.scene.add_default_ground_plane()

        # URDF の解析・インポートを行うエクステンションのインターフェースを取得
        urdf_interface = _urdf.acquire_urdf_interface()

        # URDF インポートの設定
        import_config = _urdf.ImportConfig()
        import_config.convex_decomp = False      # コリジョンの凸分解を無効化（シンプルにするため）
        import_config.fix_base = True            # ベースを地面に固定
        import_config.make_default_prim = True   # ロボットをデフォルトプリムに設定
        import_config.self_collision = False     # 自己衝突を無効化（パフォーマンスのため）
        import_config.distance_scale = 1         # 距離スケール
        import_config.density = 0.0              # 密度（0 なら既定値を使用）

        # エクステンションに同梱された URDF ファイルのパスを取得
        extension_path = get_extension_path_from_name("isaacsim.asset.importer.urdf")
        root_path = extension_path + "/data/urdf/robots/franka_description/robots"
        file_name = "panda_arm_hand.urdf"

        # URDF ファイルを解析してロボットモデルを生成
        result, robot_model = omni.kit.commands.execute(
            "URDFParseFile",
            urdf_path="{}/{}".format(root_path, file_name),
            import_config=import_config
        )

        # 各ジョイントのドライブパラメータ（Stiffness / Damping）を設定
        for joint in robot_model.joints:
            robot_model.joints[joint].drive.strength = 1047.19751
            robot_model.joints[joint].drive.damping = 52.35988

        # ロボットモデルを現在のステージにインポートし、プリムパスを取得
        result, prim_path = omni.kit.commands.execute(
            "URDFImportRobot",
            urdf_robot=robot_model,
            import_config=import_config,
        )

        # （オプション）別ステージにインポートして現在のステージから参照する方法
        # テクスチャ付きのアセットでテクスチャを正しく読み込ませたい場合に有効
        # dest_path = "/path/to/dest.usd"
        # result, prim_path = omni.kit.commands.execute(
        #     "URDFParseAndImportFile",
        #     urdf_path="{}/{}".format(root_path, file_name),
        #     import_config=import_config,
        #     dest_path=dest_path
        # )
        # prim_path = omni.usd.get_stage_next_free_path(
        #     self.world.scene.stage, str(current_stage.GetDefaultPrim().GetPath()) + prim_path, False
        # )
        # robot_prim = self.world.scene.stage.OverridePrim(prim_path)
        # robot_prim.GetReferences().AddReference(dest_path)

        # インポートしたロボットを使ってタスク（ターゲット追従）を作成
        my_task = FollowTarget(
            name="follow_target_task",
            franka_prim_path=prim_path,          # シーン内のロボットのプリムパス
            franka_robot_name="fancy_franka",    # ロボットインスタンスの名前
            target_name="target"                 # 追従するターゲットの名前
        )

        # タスクをシミュレーションワールドに追加
        world.add_task(my_task)
        return

    async def setup_post_load(self):
        # ロード後のセットアップ（コントローラの初期化など）
        self._world = self.get_world()
        self._franka = self._world.scene.get_object("fancy_franka")

        # RMPFlow コントローラを初期化
        self._controller = RMPFlowController(
            name="target_follower_controller",
            robot_articulation=self._franka
        )

        # 物理シミュレーションの各ステップで呼ばれるコールバックを登録
        self._world.add_physics_callback("sim_step", callback_fn=self.physics_step)
        await self._world.play_async()
        return

    async def setup_post_reset(self):
        # リセット時にコントローラを初期状態に戻す
        self._controller.reset()
        await self._world.play_async()
        return

    def physics_step(self, step_size):
        # 毎ステップ、ターゲットの位置・姿勢に追従するアクションを計算して適用
        world = self.get_world()
        observations = world.get_observations()

        actions = self._controller.forward(
            target_end_effector_position=observations["target"]["position"],
            target_end_effector_orientation=observations["target"]["orientation"]
        )

        self._franka.apply_action(actions)
        return
```

### 4-3. 実行する

1. **Ctrl+S** でコードを保存すると、Isaac Sim がホットリロードされます（VS Code 以外のエディタで保存しても同様にリロードされます）。
2. **File > New From Stage Template > Empty** で新しいステージを作成します。保存を促すダイアログが出た場合は **Don't Save** をクリックします。
3. メニューからもう一度 Hello World のサンプルを開きます。
4. **World Controls** の **LOAD** ボタンをクリックすると、地面・Franka・ターゲットが読み込まれてシミュレーションが開始します。ステージ上のターゲットプリム（キューブ）を動かすと、ロボットのエンドエフェクタがターゲットを追従します。

![Python インポート](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isaac_sim_import_urdf.gif)

### 4-4. コードのポイント

**ImportConfig の主な設定項目**

| 項目 | 型 | 説明 |
|---|---|---|
| `convex_decomp` | bool | コリジョンメッシュを凸分解するか。単純な凸包で十分なら `False` |
| `fix_base` | bool | ベースリンクを地面（ワールド）に固定するか。GUI の Static Base に相当 |
| `make_default_prim` | bool | インポートしたロボットをステージのデフォルトプリムにするか |
| `self_collision` | bool | 自己衝突を有効にするか |
| `distance_scale` | float | 距離のスケール係数（通常は 1） |
| `density` | float | 質量未定義のリンクに適用する密度。0 なら既定値 |

**インポートに使うコマンド**

| コマンド | 役割 |
|---|---|
| `URDFParseFile` | URDF を解析してロボットモデル（`robot_model`）を生成する。インポート前にジョイントドライブなどを調整できる |
| `URDFImportRobot` | ロボットモデルを現在のステージにインポートする |
| `URDFParseAndImportFile` | 解析とインポートを一括で行う。`dest_path` を指定すると別の USD ファイルとして出力し、現在のステージから参照できる（テクスチャ付きアセット向け） |

!!! note "ドライブ値 1047.19751 / 52.35988 の意味"
    一見中途半端に見えるこれらの値は、**度単位の値をラジアン単位に換算したもの**です。Stiffness 1047.19751 は 60000 [deg 単位]、Damping 52.35988 は 3000 [deg 単位] に相当します（60000 × π/180 ≈ 1047.19751）。回転ジョイントのドライブパラメータはラジアン単位で指定する必要がある点に注意してください。

## ステップ 5：ROS 2 ノードからのインポート

ROS 2 ノード経由で URDF をインポートすると、既存の ROS 2 ワークフローと Isaac Sim を直接連携できます。`robot_state_publisher` が配信するロボット記述を読み込むため、**XACRO ファイル**（マクロやパラメータを使って URDF を生成する ROS の記述形式）**も明示的に URDF へ変換することなく間接的にインポートできる**のが大きな利点です。

!!! warning "対応プラットフォーム"
    この機能は **Linux 上の Isaac Sim のみ**でサポートされています（他の Omniverse アプリケーションでも動作する可能性はありますが、想定どおり動作しない場合があります）。

### 前提条件

- ROS 2（例：Humble）がインストールされていること
- ロボット記述パッケージを含む ROS 2 ワークスペースがあること（例：[Universal Robots ROS 2 Description](https://github.com/UniversalRobots/Universal_Robots_ROS2_Description)）

### 手順

**ターミナル 1** — ロボット記述を配信するノードを起動します：

```bash
source /opt/ros/humble/setup.bash
# ワークスペースの setup.bash も source しておく
ros2 launch ur_description view_ur.launch.py ur_type:=ur10e
```

**ターミナル 2** — 起動したノードの名前を確認します：

```bash
source /opt/ros/humble/setup.bash
ros2 node list
# 例：/robot_state_publisher が表示される
```

**ターミナル 3** — Isaac Sim を起動してインポートします：

1. ROS 2 環境を source してから Isaac Sim を起動します。
2. エクステンション `isaacsim.ros2.urdf` を有効化します。
3. **File > Import from ROS 2 URDF Node** メニューを開きます。
4. テキストボックスにノード名（例：`robot_state_publisher`）を入力します。
5. 出力ディレクトリを指定します。
6. **Import** をクリックします。

### 応用：別のロボットに切り替えて再インポート

1. ターミナル 1 のパブリッシャーを停止し、別のロボットで再起動します（例：`ros2 launch ur_description view_ur.launch.py ur_type:=ur3`）。
2. Isaac Sim 側で **Refresh** ボタンをクリックします。
3. 出力ディレクトリを変更して **Import** をクリックします。

## インポート後の調整

ロボットはステージにインポートされた時点でシミュレーションに使用できますが、インポート後のアセットには次のような変更を加えられます：

- センサー（カメラ、IMU、LiDAR など）の追加
- マテリアルの変更
- ジョイントドライブや各種設定の更新によるシミュレーションの安定化

ロボットはシミュレーション内では**アーティキュレーション**として扱われます。アーティキュレーションのチューニングについては、公式の Articulation Stability Guide のほか、[ロボットセットアップ チュートリアル 11: ジョイントドライブゲインの調整](../robot_setup/11_joint_tuning.md)も参考にしてください。

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. GUI による **URDF ファイルの直接インポート**と設定項目の意味
2. **コリジョンメッシュ**の可視化と確認
3. **組み込みサンプル**（Robotics Examples）によるインポートの流れ
4. **Python スクリプト**によるインポートとタスクへの組み込み
5. **ROS 2 ノード**からのインポート（XACRO 対応）

### さらに学ぶには

インポート設定の全項目については、公式の [URDF Importer Extension](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/robot_setup/ext_isaacsim_asset_importer_urdf.html) ドキュメントを参照してください。

## 次のステップ

- [チュートリアル 2: URDF エクスポート](02_export_urdf.md) - 逆方向、つまり USD から URDF への変換方法を学びます。
