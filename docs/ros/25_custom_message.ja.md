---
title: ROS 2 Python カスタムメッセージ
---

# ROS 2 Python カスタムメッセージ

## 学習目標

このチュートリアルでは、**独自に定義したカスタムメッセージ**を、Isaac Sim 内の ROS 2 rclpy Python インターフェースから使う方法を学びます。

!!! warning "Windows（WSL）非対応"
    ROS 2 Python カスタムメッセージのワークフローは **Linux で完全サポート**されています。Windows（WSL）ではこのワークフローはサポートされていません（[セットアップページ](00_setup.md)の制限事項どおり、カスタムパッケージの Isaac Sim 側への組み込みは Windows 非対応です）。

## はじめに

### 前提条件

- [ROS 2 パッケージのビルドの基本](https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Custom-ROS2-Interfaces.html)（カスタムインターフェースの作成）を理解していること
- [セットアップページ](00_setup.md)の「rclpy・カスタムパッケージを Isaac Sim 内で使う場合」の手順（Python 3.11 ワークスペースのビルド）を完了していること

### 所要時間

約 15〜20 分

### 概要

!!! note "なぜ Python 3.11 ビルドが必要か"
    Isaac Sim は **Python 3.11 のみ**をサポートします。Isaac Sim 内（Script Editor やスタンドアロンスクリプト）で `rclpy` からカスタムメッセージを import するには、そのメッセージパッケージが **Python 3.11 でビルドされている**必要があります。Ubuntu 22.04 標準の Python 3.10 でビルドしたパッケージは、外部ノードでは使えますが Isaac Sim 内では import できません。

このチュートリアルでは、[IsaacSim-ros_workspaces](https://github.com/isaac-sim/IsaacSim-ros_workspaces) リポジトリに含まれる `custom_message` パッケージを使ってワークフローを確認します。このパッケージには `custom_message/msg/SampleMsg.msg` に次の定義のカスタムメッセージが含まれています：

```text
std_msgs/String my_string
int64 my_num
```

!!! tip "自作パッケージの組み込み方"
    自作の ROS 2 カスタムメッセージパッケージを Isaac Sim で使うには、Isaac Sim ROS Workspace フォルダの `humble_ws/src`（または `jazzy_ws/src`）にパッケージを置き、`./build_ros.sh` を実行してから、ワークスペースを source して Isaac Sim を起動します。カスタムパッケージ向けのインストールトラック（[セットアップページ](00_setup.md)参照）を完了していることを確認してください。

## ステップ 1：Script Editor から使う

1. `custom_message` パッケージを含む Python 3.11 ワークスペースを source したターミナルから Isaac Sim を起動します。
2. **Window > Script Editor** を開き、次のコードを入力します：

```python
import rclpy
from custom_message.msg import SampleMsg

# メッセージを作成
sample_msg = SampleMsg()

# メッセージの文字列部と整数部にデータを代入
sample_msg.my_string.data = "hello from Isaac Sim!"
sample_msg.my_num = 23

print("Message assignment completed!")
```

3. **Run** を押して、コンソールに `Message assignment completed!` が表示されることを確認します。これでメッセージの import と操作が成功しています。

## ステップ 2：スタンドアロン Python スクリプトから使う

スタンドアロンスクリプトでも、ROS 2 ブリッジを有効化した上でカスタムメッセージを import できます。

1. Isaac Sim のインストールディレクトリに `ros2_custom_message.py` という名前のファイルを作成し、次の内容を貼り付けます：

```python
import carb
from isaacsim import SimulationApp

simulation_app = SimulationApp({"renderer": "RayTracedLighting", "headless": True})

import omni
from isaacsim.core.utils.extensions import enable_extension

# ROS 2 ブリッジエクステンションを有効化
enable_extension("isaacsim.ros2.bridge")

# rclpy 関連の import
import rclpy
from custom_message.msg import SampleMsg

# メッセージを作成
sample_msg = SampleMsg()

# メッセージの文字列部と整数部にデータを代入
sample_msg.my_string.data = "hello from Isaac Sim!"
sample_msg.my_num = 23

print("Message assignment completed!")
```

2. `custom_message` パッケージを含む ROS 2 ワークスペースを source した状態で、`./python.sh` のあるディレクトリからスクリプトを実行します：

    ```bash
    ./python.sh ros2_custom_message.py
    ```

3. コンソールに `Message assignment completed!` が表示されることを確認します。

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. **Python 3.11** でのカスタムメッセージパッケージのビルドが必要な理由
2. **Script Editor** からの rclpy によるカスタムメッセージの使用
3. **スタンドアロンスクリプト**からの使用（`enable_extension("isaacsim.ros2.bridge")` → rclpy import の順序）

## 次のステップ

- [チュートリアル 26: ROS 2 Python カスタム OmniGraph ノード](26_custom_python_node.md) - rclpy を使うカスタム OmniGraph ノードをエクステンションとして作成します。
