---
title: ROS 2 Launch
---

# ROS 2 Launch

## 学習目標

このチュートリアルでは、**ROS 2 launch ファイルから Isaac Sim を起動**する方法を学びます。

!!! warning "対応環境"
    Isaac Sim の ROS 2 Launch は **Linux と、Windows の Pixi ベースのインストールのみ**でサポートされています。`isaacsim_bringup` パッケージは WSL2 では非対応です。

## はじめに

### 前提条件

- [チュートリアル 18: ROS 2 Navigation](18_navigation.md)を完了していること（ROS 2 と Nav2 のインストール、ROS 2 ブリッジの有効化）
- `carter_navigation`、`isaac_ros_navigation_goal`、`isaacsim_bringup` の各 ROS 2 パッケージが必要です。これらは ros2_ws に含まれており、launch ファイル・ナビゲーションパラメータ・ロボットモデルを提供します。ROS 2 ワークスペースがビルド・source 済みであることを確認してください（[セットアップページ](00_setup.md)参照）

### 所要時間

約 20〜30 分

### 概要

実際の ROS 2 システムは、多数のノードを **launch ファイル**で一括起動するのが普通です。`isaacsim_bringup` ROS 2 パッケージを使うと、**Isaac Sim 自体もこの launch の一部として起動**できるため、「シミュレータの起動 → シーンの読み込み → Nav2 の起動 → ゴール送信」までをコマンド 1 つで完結できます。CI や実験の自動化に特に有効です。

!!! note "パッケージ名の変更"
    ROS 2 ワークスペースの `isaacsim` パッケージは、Isaac Sim 6.0 で **`isaacsim_bringup`** にリネームされました。

## ステップ 1：launch パラメータを理解する

`isaacsim_bringup` パッケージの launch フォルダに `run_isaacsim.launch.py` という launch ファイルが含まれています。パラメータは次のとおりです：

| パラメータ | 既定値 | 説明 |
|---|---|---|
| `version` | "6.0.1" | 使用する Isaac Sim のバージョン。既定のインストールルートから起動。空なら最新版 |
| `install_path` | "" | 既定以外の場所にインストールした場合のルートパス（指定時は `version` は無視） |
| `use_internal_libs` | Humble: "true"<br>Jazzy: "false" | Isaac Sim 同梱の内部 ROS ライブラリを使うか |
| `dds_type` | "fastdds" | "fastdds" または "cyclonedds" |
| `gui` | "" | GUI モードで起動時に開く USD ファイルのパス。空なら空のステージ |
| `standalone` | "" | スタンドアロンワークフローで実行する Python ファイルのパス |
| `play_sim_on_start` | "false" | 読み込み後にシーンを自動再生するか（GUI モードのみ） |
| `ros_distro` | "humble" | 使用する ROS 2 ディストリビューション（"humble" または "jazzy"） |
| `ros_installation_path` | "" | ROS が `/opt/ros/` 以外にある場合の setup.bash / local_setup.bash のパス（カンマ区切り） |
| `headless` | "" | "webrtc" でヘッドレス＋WebRTC 配信。空なら GUI モード |
| `custom_args` | "" | isaac-sim.sh に転送する任意の引数 |
| `exclude_install_path` | "" | `LD_LIBRARY_PATH` / `PYTHONPATH` / `PATH` から除外するインストールパス（カンマ区切り） |

!!! note "use_internal_libs の既定値がディストロで異なる理由"
    Humble ではシステムの ROS ライブラリが Python 3.10 でビルドされており、Isaac Sim の Python 3.12 と互換性がないため、既定値が `true` です。Jazzy は Python 3.12 互換のライブラリを同梱しているため、既定値は `false` です。

## ステップ 2：基本の起動パターン

各例を試す前に、前の launch プロセスを終了しておいてください。

**既定構成で起動：**

```bash
ros2 launch isaacsim_bringup run_isaacsim.launch.py
```

**ワークスペースのカスタムパッケージと一緒に起動（Humble）：**

```bash
ros2 launch isaacsim_bringup run_isaacsim.launch.py exclude_install_path:=/home/user/IsaacSim-ros_workspaces/humble_ws/install ros_installation_path:=/home/user/IsaacSim-ros_workspaces/build_ws/humble/humble_ws/install/local_setup.bash
```

!!! warning "exclude_install_path が必要な理由（Ubuntu 22.04 のみ）"
    Isaac Sim は Python 3.12 のみをサポートするため、**互換性のない Python 3.10 モジュールを含む通常のワークスペースの install フォルダ**（例：`humble_ws/install`）を `exclude_install_path` で環境変数から除外する必要があります（Ubuntu 22.04 の場合のみ）。その上で、`ros_installation_path` に **Python 3.12 ビルドのワークスペース**の `local_setup.bash` を指定します（[セットアップページ](00_setup.md)参照）。Jazzy を Ubuntu 22.04 で使う場合も同様です。

**USD ファイルを開いてすぐ再生：**

```bash
ros2 launch isaacsim_bringup run_isaacsim.launch.py gui:=https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/6.0/Isaac/Samples/ROS2/Robots/Nova_Carter_ROS.usd play_sim_on_start:=true
```

**スタンドアロンワークフローで起動：**

```bash
ros2 launch isaacsim_bringup run_isaacsim.launch.py standalone:=$HOME/isaacsim/standalone_examples/api/isaacsim.ros2.bridge/moveit.py
```

## ステップ 3：Isaac Sim ＋ Nav2 を 1 つの launch で起動する

Isaac Sim の launch ファイルは、他の launch ファイルに **include** して ROS 2 ワークフローに組み込めます。ここでは Isaac Sim、Nav2、`isaac_ros_navigation_goal` を統合した例を実行します。

launch ファイルは `carter_navigation` パッケージの `carter_navigation/launch/carter_navigation_isaacsim.launch.py` にあります。このシナリオでは、launch ファイルは Isaac Sim のコンソール出力 **「Stage loaded and simulation is playing.」を待ってから**次に進むよう構成されています。このメッセージは、GUI モードで任意のシーンを読み込むための `open_isaacsim_stage.py` スクリプト（`isaacsim_bringup` パッケージの scripts フォルダ）が出力します。

!!! note "スタンドアロンで同じことをする場合"
    スタンドアロンワークフローで Isaac Sim を動かす場合は、launch ファイルが監視できる独自の print 文を自分で追加する必要があります。

統合 launch ファイルを実行します：

```bash
ros2 launch carter_navigation carter_navigation_isaacsim.launch.py
```

シーンの読み込みを待つと、倉庫のナビゲーションシーンが Isaac Sim に自動で読み込まれ、RViz2 がロボットのセンサーデータを表示し始め、ロボットが自動生成されたゴールへ向かってナビゲーションを開始します。

!!! tip "自動ゴールが始まらない場合"
    Nav2 の初期化が間に合っていない可能性があります。回避策として、`carter_navigation_isaacsim.launch.py` 内の `execute_second_node_if_condition_met` 関数を探し、コメントの説明に従って該当行のコメントアウトを外すと、`isaac_ros_navigation_goal` の起動前に手動で遅延を入れられます。

iw.hub のナビゲーションシーンと `iw_hub_navigation` パッケージでも同じワークフローを実行できます：

```bash
ros2 launch iw_hub_navigation iw_hub_navigation_isaacsim.launch.py
```

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. `isaacsim_bringup` パッケージの **run_isaacsim.launch.py** による Isaac Sim の起動と全パラメータの意味
2. Python バージョン非互換を回避する **exclude_install_path / ros_installation_path** の使い方
3. Isaac Sim・Nav2・自動ゴール送信を統合した **1 コマンドでの起動**

## 次のステップ

- [チュートリアル 29: ROS 2 Simulation Control](29_simulation_control.md) - ROS 2 からシミュレーション自体（再生・停止・シーン操作）を制御します。
