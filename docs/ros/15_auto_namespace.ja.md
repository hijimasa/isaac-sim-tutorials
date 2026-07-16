---
title: 自動 ROS 2 ネームスペース生成
---

# 自動 ROS 2 ネームスペース生成

## 学習目標

このチュートリアルでは、Isaac Sim のアセットを設定して、各 ROS 2 OmniGraph ノードの **ROS 2 ネームスペースを自動生成**する方法を学びます。

## はじめに

### 前提条件

- [ROS 2 セットアップ](00_setup.md)が完了しており、Isaac Sim 起動前に必要な環境変数が設定され、ROS 2 エクステンションが有効であること
- ROS 2 公式の [Namespaces の設計ドキュメント](https://design.ros2.org/articles/topic_and_service_names.html)を読んでおくこと

### 所要時間

約 20〜25 分

### 概要

**マルチロボット**のシミュレーションでは、各ロボットのトピックを一意に識別できるように、ネームスペース（`/robot1/scan`、`/robot2/scan` のような接頭辞）の管理が不可欠です。

OmniGraph で ROS のパブリッシャ／サブスクライバ／サービスにネームスペースを設定する方法は、現在 2 つあります：

1. 各ノードの **nodeNamespace** フィールドに手動で設定する

    ![nodeNamespace フィールド](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_ros_tut_gui_ros2_nodeNamespace.png)

2. **（推奨）**アセットに `isaac:namespace` 属性を設定し、すべての ROS OmniGraph ノードのネームスペースを**自動生成**する

方法 1 はノードの数だけ手作業が必要で、ロボットを複製するたびに全ノードを修正することになります。方法 2 なら、プリム階層に属性を付けておくだけで、**ロボットを Duplicate してもネームスペースの変更は 1 箇所**で済みます。このチュートリアルでは方法 2 をハンズオンで学びます。

## ステップ 1：ベースアセットをセットアップする

まず、ロボットのアーティキュレーションを模した XForm のセットを作ります。

1. 新しいステージを開き、**Window > Script Editor** で次のスニペットを実行します：

```python
# 必要なモジュールをインポート
from pxr import UsdGeom
import omni.usd

# 現在のステージを取得
stage = omni.usd.get_context().get_stage()

# ステージが読み込まれていることを確認
if not stage:
    print("No stage is currently loaded. Please load a stage and try again.")
else:
    # ルートとなる mock_robot Xform を作成
    mock_robot = UsdGeom.Xform.Define(stage, "/mock_robot")

    # mock_robot の下に base_link Xform を作成
    base_link = UsdGeom.Xform.Define(stage, "/mock_robot/base_link")

    # lidar_link を作成し、base_link の 0.4 m 上（Z 軸）に配置
    lidar_link = UsdGeom.Xform.Define(stage, "/mock_robot/base_link/lidar_link")
    lidar_link.AddTranslateOp().Set(value=(0, 0, 0.4))

    # camera_link を作成し、base_link の 0.2 m 上（Z 軸）に配置
    camera_link = UsdGeom.Xform.Define(stage, "/mock_robot/base_link/camera_link")
    camera_link.AddTranslateOp().Set(value=(0, 0, 0.2))

    # base_link の下に wheel_left / wheel_right Xform を作成
    wheel_left = UsdGeom.Xform.Define(stage, "/mock_robot/base_link/wheel_left")
    wheel_right = UsdGeom.Xform.Define(stage, "/mock_robot/base_link/wheel_right")

    # wheel_left を中心から 0.2 m 左（X 軸）に配置
    wheel_left.AddTranslateOp().Set(value=(-0.2, 0, 0))

    # wheel_right を中心から 0.2 m 右（X 軸）に配置
    wheel_right.AddTranslateOp().Set(value=(0.2, 0, 0))
```

2. **Create > Sensors > RTX Lidar > NVIDIA > Example Rotary 2D** で 2D RTX Lidar を追加し、`/mock_robot/base_link/lidar_link` の下にドラッグします。
3. **Create > Sensors > Camera and Depth Sensors > LeopardImaging > Hawk** で Hawk ステレオカメラを追加し、`/mock_robot/base_link/camera_link` の下にドラッグします。
4. グラフショートカットで各パブリッシャを作成します：

| パブリッシャ | メニュー | 設定 |
|---|---|---|
| Generic Publisher | Tools > Robotics > ROS 2 OmniGraphs > Generic Publisher | Publish String、Graph Path：`/mock_robot/base_link/wheel_left/String_graph` |
| TF Publisher | 同 > TF Publisher | Target Prim：`/mock_robot`、Graph Path：`/mock_robot/base_link/wheel_left/TF_graph` |
| Camera Publisher（左） | 同 > Camera | Camera Prim：`/mock_robot/base_link/camera_link/Hawk/left/camera_left`、Graph Path：`/mock_robot/base_link/camera_link/Hawk/Camera_Left_Graph`、Depth のチェックを外す |
| Camera Publisher（右） | 同 > Camera | Camera Prim：`.../Hawk/right/camera_right`、Graph Path：`.../Hawk/Camera_Right_Graph`、Depth のチェックを外す |
| RTX Lidar Publisher | 同 > RTX Lidar | Lidar Prim：`/mock_robot/base_link/lidar_link/Example_Rotary_2D`、Graph Path：`/mock_robot/base_link/lidar_link/Lidar_Graph`、Laser Scan のみ有効 |

## ステップ 2：ネームスペースの生成ルールを理解する

ベースアセットができたので、ネームスペースを付けたいプリムに **`isaac:namespace`** 属性を追加していきます。ネームスペースは、**プリム階層の上から各 ROS パブリッシャまでの経路上にある `isaac:namespace` 属性の値を連結**して生成されます。

ただし、「どの経路を見るか」はノードの種類によって異なります：

| ノードの種類 | ネームスペースの探索経路 |
|---|---|
| **TF 系ノード** | 階層の**最上位**にある namespace 属性の値**のみ**を使う（1 台のロボットの TF はすべてそのロボットのネームスペース直下、例：`robot1/tf` に置かれるため） |
| **Camera / Lidar Helper ノード** | **センサープリムの場所**を基準に経路を探索する（Helper ノード自体の場所は無関係） |
| **その他の OmniGraph ノード** | **OmniGraph ノード自体の場所**を基準に経路を探索する（グラフの配置場所が意味を持つ） |

!!! note "これまでのチュートリアルの伏線回収"
    [チュートリアル 8](08_rtx_lidar.md) や [10](10_publish_rate.md) で「グラフの配置場所は自動ネームスペース生成に関係する」と述べていたのは、この「その他のノードはグラフの場所で経路が決まる」ルールのためです。

## ステップ 3：isaac:namespace 属性を追加してテストする

属性の追加手順：

1. プリムを選択し、Property ウィンドウの **Add** をクリックして、ポップアップメニューから **Isaac > Namespace** を選択します。
2. Property パネルの **Namespace** フィールドにネームスペースの値を入力します。

このチュートリアルでは、次のプリムに `isaac:namespace` 属性を付け、値は**プリム名と同じ**にします（任意の値でも構いません）：

- `/mock_robot/base_link/lidar_link`
- `/mock_robot/base_link/camera_link`
- `/mock_robot/base_link/camera_link/Hawk`
- `/mock_robot/base_link/camera_link/Hawk/left`
- `/mock_robot/base_link/camera_link/Hawk/right`
- `/mock_robot/base_link/wheel_left`

3. **Play** でシミュレーションを開始します。
4. ROS を source したターミナルで `ros2 topic list` を実行し、少なくとも次のトピックが見えることを確認します：

```text
/camera_link/Hawk/left/camera_info
/camera_link/Hawk/left/rgb
/camera_link/Hawk/right/camera_info
/camera_link/Hawk/right/rgb
/lidar_link/laser_scan
/wheel_left/tf
/wheel_left/topic
```

経路上の属性値が連結されてトピック名になっていることがわかります。

## ステップ 4：ロボットを複製してマルチロボット構成にする

自動生成の真価は、ロボットの複製時に発揮されます。

1. シミュレーションを停止し、`/mock_robot` プリムを選択して `isaac:namespace` 属性を追加し、値をプリム名（`mock_robot`）にします。
2. `/mock_robot` を右クリックして **Duplicate** で複製します。生成された `/mock_robot_01` を選択し、Property パネルで `isaac:namespace` 属性を `mock_robot_01` に変更します。
3. **Play** でシミュレーションを開始します。
4. `ros2 topic list` で、両方のロボットのトピックがそれぞれのネームスペース配下に生成されていることを確認します：

```text
/mock_robot/camera_link/Hawk/left/camera_info
/mock_robot/camera_link/Hawk/left/rgb
/mock_robot/camera_link/Hawk/right/camera_info
/mock_robot/camera_link/Hawk/right/rgb
/mock_robot/lidar_link/laser_scan
/mock_robot/tf
/mock_robot/wheel_left/topic

/mock_robot_01/camera_link/Hawk/left/camera_info
/mock_robot_01/camera_link/Hawk/left/rgb
/mock_robot_01/camera_link/Hawk/right/camera_info
/mock_robot_01/camera_link/Hawk/right/rgb
/mock_robot_01/lidar_link/laser_scan
/mock_robot_01/tf
/mock_robot_01/wheel_left/topic
```

TF 系だけ `/mock_robot/tf`（最上位のネームスペースのみ）になっている点にも注目してください。

!!! note "カスタム命名がしたい場合"
    自動生成された名前がシステムの命名規約に合わない場合は、これまでどおり各 ROS OmniGraph ノードの **nodeNamespace** 入力フィールドを個別に設定してください。

## まとめ

このチュートリアルでは、ロボットのプリムに `isaac:namespace` 属性を設定して、ROS 2 ネームスペースを自動生成する方法を扱いました：

1. ノード種別ごとの**ネームスペース探索ルール**（TF＝最上位のみ／センサー＝センサープリム基準／その他＝グラフ基準）
2. **isaac:namespace 属性**の追加とトピック名の確認
3. ロボットの **Duplicate** による、属性 1 箇所の変更だけのマルチロボット化

## 次のステップ

- [チュートリアル 16: 強化学習ポリシーの ROS 2 実行](16_rl_controller.md) - Isaac Sim で ROS 2 を介してロコモーションポリシーを動かす方法を学びます。
