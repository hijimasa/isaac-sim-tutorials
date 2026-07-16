---
title: ROS 2 カスタム C++ OmniGraph ノード
---

# ROS 2 カスタム C++ OmniGraph ノード

## 学習目標

このチュートリアルでは、Isaac Sim で使う**カスタム C++ OmniGraph ノード**の書き方を学びます。

!!! warning "対応環境"
    このチュートリアルは **Linux の ROS 2 Humble のみ**でサポートされています。

## はじめに

### 前提条件

- [ROS 2 パッケージのビルドの基本](https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Custom-ROS2-Interfaces.html)を理解していること
- [チュートリアル 26: ROS 2 Python カスタム OmniGraph ノード](26_custom_python_node.md)を完了していると、対比として理解しやすくなります

### 所要時間

約 40〜60 分

### 概要

[チュートリアル 26](26_custom_python_node.md) の Python 版に対して、C++ 版のカスタムノードは**パフォーマンスが要求される処理**や、既存の C++ ライブラリを組み込みたい場合に適しています。仕組みは大きく異なり、rclpy ではなく **ROS 2 の C API（rcl）**を直接使い、Omniverse の **Kit Extension Template C++** でエクステンションをビルドします。

## ステップ 1：カスタムメッセージパッケージをビルドする

カスタムメッセージを Isaac Sim で使うには、まず ROS 2 でメッセージパッケージをビルドします。メッセージの定義は次のとおりです（球の中心と半径）：

```text
geometry_msgs/Point center
float64 radius
```

[ROS 2 Humble 公式の「Creating custom msg and srv files」](https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Custom-ROS2-Interfaces.html)の手順に従って、`tutorial_interfaces` パッケージを作成・ビルドしてください。

!!! note
    公式チュートリアルは「[6. Confirm msg and srv creation](https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Custom-ROS2-Interfaces.html#confirm-msg-and-srv-creation)」の小節まで完了すれば十分です。また、公式チュートリアルどおりのパッケージ名・メッセージ名を使ってください。自作の C++ OmniGraph ノードをビルドする際に、この名前が重要になります。

## ステップ 2：Kit Extension C++ テンプレートをセットアップする

カスタムの ROS 2 OmniGraph ノードを使うには、C++ コードを含む自前のエクステンションをビルドする必要があります。[Omniverse Kit Extension Template C++](https://github.com/NVIDIA-Omniverse/kit-extension-template-cpp) の ReadMe に目を通しておくことを強く推奨します。

1. Kit Extension Template C++ をクローンし、`release/107.3.0` ブランチに切り替えます（ルートフォルダで `git checkout release/107.3.0`）。
2. ディレクトリ内で `./build.sh` を実行してサンプルエクステンションをビルドします。
3. `./_build/linux-x86_64/release/omni.app.kit.dev.sh` が正しく動くことを確認します。
4. このチュートリアル用のサンプルエクステンション [Custom ROS 2 OmniGraph Node Extension (Humble)](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_downloads/5418eff6891a41d71ac8b5f687bf1cbd/omni.example.cpp.omnigraph_node_ros.zip) をダウンロードします。
5. `omni.example.cpp.omnigraph_node_ros` フォルダを、クローンしたテンプレートフォルダの `source/extensions` 配下に展開します。
6. `deps/kit-sdk-deps.packman.xml` の末尾（`</project>` 閉じタグの前）に次の行を追加します：

```xml
<dependency name="system_ros" linkPath="../_build/target-deps/system_ros" tags="${config}">
    <source path="<FULL_PATH_TO_THE_ROS_2_INSTALL>" />
</dependency>

<dependency name="additional_ros_workspace" linkPath="../_build/target-deps/additional_ros" tags="${config}">
    <source path="<FULL_PATH_TO_WORKSPACE_CREATED_ABOVE>/install/tutorial_interfaces" />
</dependency>
```

source path はローカル環境に合わせて更新します。例：

- `<FULL_PATH_TO_THE_ROS_2_INSTALL>`：`/opt/ros/humble`
- `<FULL_PATH_TO_WORKSPACE_CREATED_ABOVE>`：`/home/user/ros2_ws`

この追加により、`premake5.lua` がシステム上の ROS 2 のヘッダとライブラリを見つけられるようになります（カスタムノードのビルドに必要です）。

7. `./build.sh` を実行して、ROS 2 OmniGraph ノードを含む新しいエクステンションをビルドします。

!!! warning "パスは完全パスで"
    2 つの dependency の source path には**完全なパス**を指定してください。ローカルの ROS ワークスペースとインストールに対してエクステンションをビルドするために必要です。

## ステップ 3：エクステンションを Isaac Sim に追加する

1. 上で作成した `tutorial_interfaces` パッケージを含むワークスペースの `install/local_setup.bash` を source します：

    ```bash
    source install/local_setup.bash
    ```

    !!! warning "ROS 2 本体は source しない"
        ここでは **ROS 2 インストール自体は source しません**。source すると、ROS 2 ディストリビューションの Python バージョン（Humble は 3.10）と Isaac Sim（3.11）の違いによる**シンボル競合**が起きる可能性があります。

2. このターミナルから Isaac Sim を起動します。
3. **Window > Extensions** を開き、検索バー右側のハンバーガーメニュー（1）から **Settings**（2）をクリックします。
4. **Extension Search Paths** の **+** アイコンをクリックし、前のステップでビルドしたエクステンションのパス（`kit-extension-template-cpp/_build/linux-x86_64/release/exts` 配下）を追加します。
5. **Third Party** タブ（3）にエクステンションが表示されることを確認します。

    ![エクステンションの追加](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_full_tut_gui_add_ext_to_isim.png)

6. **Custom ROS2 OGN Example Extension** を有効化します。

!!! tip "libtutorial_interfaces...so が見つからないエラー"
    次のようなエラーが出る場合は、カスタムの `tutorial_interfaces` パッケージが正しく source されていない可能性が高いです：

    ```text
    Error: libtutorial_interfaces__rosidl_typesupport_c.so: cannot open shared object file: No such file or directory
    ```

## ステップ 4：Action Graph を構築してノードを動かす

Custom ROS2 OGN Example Extension を有効にした状態で：

1. **Window > Graph Editors > Action Graph** を開きます。
2. Action Graph タブで「ROS 2」を検索し、**ROS 2 Publish Custom Message** と **ROS 2 Publish String** の 2 つのノードをグラフにドラッグします。
3. **Playback Tick** を検索してグラフに追加します。
4. **On Playback Tick** の Tick を、両方の ROS 2 ノードの **Exec In** に接続します。

    ![カスタム C++ ノードのグラフ](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_full_tut_gui_custom_cpp_nodes_graph.png)

5. **Play** すると、ノードが ROS 2 への配信を始めます。
6. 新しいターミナルで ROS 2 ワークスペースを source し、トピックを確認します：

    ```bash
    ros2 topic list
    ```

    ```text
    /custom_node/my_string    # 文字列が配信されるトピック
    /custom_node/sphere_msg   # ステップ 1 で作成したカスタム SphereMsg が配信されるトピック
    ```

## ノードとエクステンションの中身を掘り下げる

エクステンションのビルドは `premake5.lua` が担います。指定した ROS インストールパスに対するコンパイルとリンクを行う部分を確認しておきましょう：

```lua
-- エクステンションがロードする C++ プラグインをビルドする
project_ext_plugin(ext, ogn.plugin_project)
    -- C++ コードを含むすべてのサブディレクトリをこのプロジェクトに追加することが重要
    add_files("source", "plugins/"..ogn.module)
    add_files("nodes", "plugins/nodes")

    -- すべての OGN プロジェクト共通の標準依存（インクルード、リンクするライブラリ、コンパイラフラグ）を追加
    add_ogn_dependencies(ogn)

    includedirs {
        -- システムレベルの ROS インクルード
        "%{target_deps}/system_ros/include/std_msgs",
        "%{target_deps}/system_ros/include/geometry_msgs",
        "%{target_deps}/system_ros/include/rosidl_runtime_c",
        "%{target_deps}/system_ros/include/rosidl_typesupport_interface",
        "%{target_deps}/system_ros/include/rcl",
        "%{target_deps}/system_ros/include/rcutils",
        "%{target_deps}/system_ros/include/rmw",
        "%{target_deps}/system_ros/include/rcl_yaml_param_parser",

        -- 追加で source した ROS ワークスペースのインクルード
        "%{target_deps}/additional_ros/include/tutorial_interfaces",
    }

    libdirs {
        -- システムレベルの ROS ライブラリ
        "%{target_deps}/system_ros/lib",

        -- 追加で source した ROS ワークスペースのライブラリ
        "%{target_deps}/additional_ros/lib",
    }

    links{
        -- ノードの動作に必要な最小限の ROS 2 C API ライブラリ
        "rosidl_runtime_c", "rcutils", "rcl", "rmw",

        -- シンプルな文字列メッセージ用の依存
        "std_msgs__rosidl_typesupport_c", "std_msgs__rosidl_generator_c",

        -- カスタムメッセージとその依存ライブラリ
        "geometry_msgs__rosidl_typesupport_c", "geometry_msgs__rosidl_generator_c",
        "tutorial_interfaces__rosidl_typesupport_c", "tutorial_interfaces__rosidl_generator_c",
    }

    filter { "system:linux" }
        linkoptions { "-Wl,--export-dynamic" }

    cppdialect "C++17"
```

OmniGraph ノード本体は `plugins/nodes` にあります。OmniGraph ノード内での ROS 2 コンポーネントの作成・操作には **rcl** ROS 2 API が使われています。C++ ノードでは、**Exec In の条件が真になったときに `compute()` が呼ばれ**、そこで ROS 2 ノードとパブリッシャの初回作成とメッセージの配信が行われます。

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. カスタムメッセージパッケージ（`tutorial_interfaces`）のビルド
2. **Kit Extension Template C++** による、ROS 2 C++ OmniGraph ノードを含むエクステンションのビルド（packman 依存の追加と premake5.lua の構成）
3. エクステンションの Isaac Sim への追加（**ROS 2 本体を source しない**理由を含む）とノードの実行

## 次のステップ

- [チュートリアル 28: ROS 2 Launch](28_launch.md) - ROS 2 Launch で Isaac Sim をデプロイする方法を学びます。
