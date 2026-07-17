---
title: ROS 2 ノードからの URDF インポート
---

# ROS 2 ノードからの URDF インポート

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- ROS 2 ノード（`robot_state_publisher`）が配信するロボット記述を Isaac Sim に直接インポートする方法
- XACRO ファイルを URDF へ明示的に変換せずにインポートする流れ
- 別のロボットに切り替えて再インポートする手順

## はじめに

### 前提条件

- [チュートリアル 1: URDF インポート](01_import_urdf.md)を完了していること
- ROS 2 がインストールされていること（インストールには root / sudo 権限が必要な場合があります）
- ロボット記述パッケージを含む ROS 2 ワークスペースがあること（例：[Universal Robots ROS 2 Description](https://github.com/UniversalRobots/Universal_Robots_ROS2_Description)）

### 所要時間

約 10 分

### 概要

ROS 2 ノード経由で URDF をインポートすると、既存の ROS 2 ワークフローと Isaac Sim を直接連携できます。`robot_state_publisher` が配信するロボット記述を読み込むため、**XACRO ファイル**（マクロやパラメータを使って URDF を生成する ROS の記述形式）**も明示的に URDF へ変換することなく間接的にインポートできる**のが大きな利点です。

!!! warning "対応プラットフォーム"
    この機能は **Linux 上の Isaac Sim のみ**でサポートされています（他の Omniverse アプリケーションでも動作する可能性はありますが、想定どおり動作しない場合があります）。

## ステップ 1：ロボット記述ノードを起動する

**ターミナル 1** — ROS 2 環境を source し、ロボット記述を配信するノードを起動します：

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

## ステップ 2：Isaac Sim からインポートする

**ターミナル 3** — Isaac Sim を起動してインポートします：

1. ROS 2 環境を source してから Isaac Sim を起動します。
2. エクステンション `isaacsim.ros2.urdf` をインストール・有効化します。
3. **File > Import from ROS 2 URDF Node** メニューを開きます。
4. テキストボックスにノード名（例：`robot_state_publisher`）を入力します。
5. **Find Node** ボタンをクリックしてノードを検索します。
6. 出力ディレクトリを指定します。
7. **Import** をクリックします。

!!! note "出力ディレクトリを指定しなかった場合"
    出力ディレクトリを指定しないと、USD はシステムの一時ディレクトリに書き出され、そのパスを示す警告がログに出力されます。保存先を制御したい場合は必ず出力ディレクトリを指定してください。

!!! note "ROS 2 Bridge が必要"
    この機能は ROS 2 Bridge（`isaacsim.ros2.bridge`）が有効な場合にのみ利用できます。ROS 2 環境のセットアップについては [ROS 2 セットアップ](../ros/00_setup.md)を参照してください。

## ステップ 3：応用 — 別のロボットに切り替えて再インポート

1. ターミナル 1 のパブリッシャーを停止し、別のロボットで再起動します（例：`ros2 launch ur_description view_ur.launch.py ur_type:=ur3`）。
2. Isaac Sim 側で **Find Node** ボタンをクリックします。
3. 出力ディレクトリを変更して **Import** をクリックします。

!!! note "旧 Kit コマンド `URDFImportFromROS2Node` は非推奨"
    Isaac Sim 6.0 では、この機能をスクリプトから使う際の Kit コマンド `URDFImportFromROS2Node` は**非推奨（deprecated）**となりました。プログラムから同等の処理を行う場合は、`RobotDefinitionReader` でロボット記述を取得し、`URDFImporter` でインポートする方法が推奨されています。

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. `robot_state_publisher` が配信するロボット記述（XACRO 対応）の **Isaac Sim への直接インポート**
2. **Find Node** によるノード検索と出力ディレクトリの指定
3. 別のロボットへの切り替えと再インポート

## 次のステップ

- [チュートリアル 2: URDF エクスポート](02_export_urdf.md) - USD から URDF への変換方法を学びます。
- [ROS 2 チュートリアル](../ros/index.md) - Isaac Sim と ROS 2 の連携をさらに深く学びます。
