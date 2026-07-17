---
title: ROS 2 カスタム C++ OmniGraph ノード
---

# ROS 2 カスタム C++ OmniGraph ノード

## 学習目標

このチュートリアルでは、Isaac Sim で使う**カスタム C++ OmniGraph ノード**の書き方を学びます。

!!! warning "対応環境"
    このチュートリアルは **Linux の ROS 2 Jazzy のみ**でサポートされています。

## はじめに

### 前提条件

- [ROS 2 パッケージのビルドの基本](https://docs.ros.org/en/jazzy/Tutorials/Beginner-Client-Libraries/Custom-ROS2-Interfaces.html)を理解していること
- [チュートリアル 26: ROS 2 Python カスタム OmniGraph ノード](26_custom_python_node.md)を完了していると、対比として理解しやすくなります

### 所要時間

約 40〜60 分

### 概要

[チュートリアル 26](26_custom_python_node.md) の Python 版に対して、C++ 版のカスタムノードは**パフォーマンスが要求される処理**や、既存の C++ ライブラリを組み込みたい場合に適しています。仕組みは大きく異なり、rclpy ではなく **ROS 2 の C API（rcl）**を直接使い、**Isaac Sim リポジトリ**（GitHub）のエクステンションテンプレートでエクステンションをビルドします。

## ステップ 1：カスタムメッセージパッケージをビルドする

カスタムメッセージを Isaac Sim で使うには、まず ROS 2 でメッセージパッケージをビルドします。メッセージ（`Sphere.msg` ファイル）の定義は次のとおりです（球の中心と半径）：

```text
geometry_msgs/Point center
float64 radius
```

[ROS 2 Jazzy 公式の「Creating custom msg and srv files」](https://docs.ros.org/en/jazzy/Tutorials/Beginner-Client-Libraries/Custom-ROS2-Interfaces.html)の手順に従って、`tutorial_interfaces` パッケージを作成・ビルドしてください。

!!! note
    公式チュートリアルは「[6. Confirm msg and srv creation](https://docs.ros.org/en/jazzy/Tutorials/Beginner-Client-Libraries/Custom-ROS2-Interfaces.html#confirm-msg-and-srv-creation)」の小節まで完了すれば十分です。また、公式チュートリアルどおりのパッケージ名・メッセージ名を使ってください。自作の C++ OmniGraph ノードをビルドする際に、この名前が重要になります。

## ステップ 2：Isaac Sim リポジトリでエクステンションテンプレートをセットアップする

カスタムの ROS 2 OmniGraph ノードを使うには、C++ コードを含む自前のエクステンションをビルドする必要があります。Isaac Sim 6.0 では、このために **Isaac Sim リポジトリ**を使います。

1. [Isaac Sim リポジトリ](https://github.com/isaac-sim/IsaacSim)を GitHub からクローンし、[Quick Start](https://github.com/isaac-sim/IsaacSim?tab=readme-ov-file#quick-start) の手順に従ってビルドします。`_build/linux-*/release` フォルダにある `isaac-sim.sh` スクリプトが正しく動くことを確認します。
2. `./repo.sh template new` コマンドで、新しい **Isaac Sim OmniGraph Node Extension** テンプレートを作成します。プロンプトには矢印キーで選択、または入力で次の値を指定します：

    ```text
    ? Do you accept the governing terms? Yes
    ? Select what you want to create with arrow keys: Extension
    ? Select desired template with arrow keys: [isaacsim-omnigraph-extension]: Isaac Sim OmniGraph Node Extension
    ? Enter name of extension [name-spaced, lowercase, alphanumeric]: custom.cpp.ros2_node
    ? Enter title: ROS 2 C++ Custom OmniGraph Node
    ? Enter version: 0.1.0
    ? Enter description: A new Isaac Sim OmniGraph node extension.
    ? Enter category: Simulation
    ```

    プロンプトに答え終わると、テンプレートが `source/extensions/custom.cpp.ros2_node` パスに作成されます。

3. `deps/kit-sdk-deps.packman.xml` の末尾（`</project>` 閉じタグの前）に次の行を追加します：

    ```xml
    <dependency name="system_ros" linkPath="../_build/target-deps/system_ros" tags="${config}">
        <source path="<FULL_PATH_TO_THE_ROS_2_INSTALL>" />
    </dependency>

    <dependency name="additional_ros_workspace" linkPath="../_build/target-deps/additional_ros" tags="${config}">
        <source path="<FULL_PATH_TO_WORKSPACE_CREATED_ABOVE>/install/tutorial_interfaces" />
    </dependency>
    ```

    source path はローカル環境に合わせて更新します。例：

    - `<FULL_PATH_TO_THE_ROS_2_INSTALL>`：`/opt/ros/jazzy`
    - `<FULL_PATH_TO_WORKSPACE_CREATED_ABOVE>`：`/home/user/ros2_ws`

    この追加により、`premake5.lua` がシステム上の ROS 2 のヘッダとライブラリを見つけられるようになります（カスタムノードのビルドに必要です）。

    !!! warning "パスは完全パスで"
        2 つの dependency の source path には**完全なパス**を指定してください。ローカルの ROS ワークスペースとインストールに対してエクステンションをビルドするために必要です。

4. `source/extensions/custom.cpp.ros2_node/premake5.lua` を編集し、カスタムメッセージパッケージのヘッダとライブラリを組み込みます。`-- C++ Carbonite plugin` セクションの `includedirs` 定義を拡張してシステムレベルの ROS インクルードと追加の ROS ワークスペースのインクルードを含め、ROS 2 C API ライブラリとカスタムメッセージのライブラリにリンクするための `libdirs` と `links` 定義を追加します：

    ```lua
    includedirs {
        "%{root}/source/extensions/custom.cpp.ros2_node/include",
        -- システムレベルの ROS インクルード
        "%{target_deps}/system_ros/include/builtin_interfaces",
        "%{target_deps}/system_ros/include/geometry_msgs",
        "%{target_deps}/system_ros/include/rcl",
        "%{target_deps}/system_ros/include/rcl_yaml_param_parser",
        "%{target_deps}/system_ros/include/rcutils",
        "%{target_deps}/system_ros/include/rmw",
        "%{target_deps}/system_ros/include/rosidl_dynamic_typesupport",
        "%{target_deps}/system_ros/include/rosidl_runtime_c",
        "%{target_deps}/system_ros/include/rosidl_typesupport_interface",
        "%{target_deps}/system_ros/include/service_msgs",
        "%{target_deps}/system_ros/include/std_msgs",
        "%{target_deps}/system_ros/include/type_description_interfaces",
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
        -- カスタムメッセージとその依存ライブラリ
        "geometry_msgs__rosidl_typesupport_c", "geometry_msgs__rosidl_generator_c",
        "tutorial_interfaces__rosidl_typesupport_c", "tutorial_interfaces__rosidl_generator_c",
    }
    ```

    !!! note "本サイト補足"
        公式ページの `links` には `geometry_msgs__rosidl_typesupport_c` が 2 回記載されていますが、おそらく誤記のため、本ページでは 2 つ目を `geometry_msgs__rosidl_generator_c` としています。

## ステップ 3：ノードを実装する（.ogn / .cpp）

`source/extensions/custom.cpp.ros2_node/nodes` フォルダに、ノード定義ファイル `ROS2CustomMessageNode.ogn` とソースコード `ROS2CustomMessageNode.cpp` を次の内容で作成します。

`ROS2CustomMessageNode.ogn`：

```json
{
    "ROS2CustomMessageNode": {
        "version": 1,
        "icon": "icons/isaac-sim.svg",
        "description": [
            "This node publishes a custom message with a ROS 2 OG node"
        ],
        "metadata": {
            "uiName": "ROS2 Publish Custom Message"
        },
        "categories": ["tutorials"],
        "inputs": {
            "execIn": {
                "type": "execution",
                "description": "The input execution port."
            },

            "publishCenter": {
                "type": "float[3]",
                "description": "Center co-ordinates to publish in order [x, y, z]",
                "default" : [0.0, 0.0, 0.0]
            },

            "publishRadius": {
                "type": "float",
                "description": "Value of radius to publish",
                "default" : 1.5
            }
        }
    }
}
```

`ROS2CustomMessageNode.cpp`：

```cpp
// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include <ROS2CustomMessageNodeDatabase.h>
#include <string>

// この例では、OmniGraph ノードでカスタムメッセージを配信する
#include "tutorial_interfaces/msg/sphere.h"

// ノードやパブリッシャの作成などに使う ROS のインクルード
#include "rcl/rcl.h"

// 使用する名前を明示的に短縮するためのヘルパー
using omni::graph::core::Type;
using omni::graph::core::BaseDataType;


class ROS2CustomMessageNode
{
public:
    static bool compute(ROS2CustomMessageNodeDatabase& db)
    {
        auto& state = db.internalState<ROS2CustomMessageNode>();

        if(!state.pub_created)
        {
            state.context = rcl_get_zero_initialized_context();
            state.init_options = rcl_get_zero_initialized_init_options();
            state.allocator = rcl_get_default_allocator();
            rcl_ret_t rc;
            // init_options を作成
            rc = rcl_init_options_init(&state.init_options, state.allocator);
            if (rc != RCL_RET_OK)
            {
                printf("Error rcl_init_options_init.\n");
                return false;
            }

            // コンテキストを作成
            rc = rcl_init(0, nullptr, &state.init_options, &state.context);
            if (rc != RCL_RET_OK)
            {
                printf("Error in rcl_init.\n");
                return false;
            }

            // rcl_node を作成
            state.my_node = rcl_get_zero_initialized_node();
            state.node_ops = rcl_node_get_default_options();
            rc = rcl_node_init(&state.my_node, "node_0", "custom_node", &state.context, &state.node_ops);
            if (rc != RCL_RET_OK)
            {
                printf("Error in rcl_node_init\n");
                return false;
            }

            const char * topic_name = "sphere_msg";

            const rosidl_message_type_support_t * my_type_support = ROSIDL_GET_MSG_TYPE_SUPPORT(tutorial_interfaces, msg, Sphere);

            state.pub_options = rcl_publisher_get_default_options();

            // パブリッシャを初期化
            rc = rcl_publisher_init(
                &state.my_pub,
                &state.my_node,
                my_type_support,
                topic_name,
                &state.pub_options);
            if (RCL_RET_OK != rc)
            {
                printf("Error in rcl_publisher_init %s.\n", topic_name);
                return false;
            }
            // ノードとパブリッシャの作成に成功
            state.pub_created = true;

            return true;
        }

        tutorial_interfaces__msg__Sphere* ros_msg = tutorial_interfaces__msg__Sphere__create();

        // OG ノードへの入力で球の中心を設定
        ros_msg->center.x = db.inputs.publishCenter()[0];
        ros_msg->center.y = db.inputs.publishCenter()[1];
        ros_msg->center.z = db.inputs.publishCenter()[2];

        // 入力された半径を球の半径に設定
        ros_msg->radius = db.inputs.publishRadius();

        rcl_ret_t rc;
        rc = rcl_publish(&state.my_pub, ros_msg, NULL);
        if (rc != RCL_RET_OK)
        {
            // 最初は RCL_RET_PUBLISHER_INVALID が返り、その後メッセージが配信される
            return false;
        }

        // 配信した ROS メッセージを破棄してメモリを解放
        tutorial_interfaces__msg__Sphere__destroy(ros_msg);

        // true を返すと、compute が成功して出力値が有効になったことを OmniGraph に伝える
        return true;
    }

    static void releaseInstance(NodeObj const& nodeObj, GraphInstanceID instanceId)
    {
        auto& state = ROS2CustomMessageNodeDatabase::sPerInstanceState<ROS2CustomMessageNode>(nodeObj, instanceId);


        // パブリッシャを削除
        rcl_ret_t rc = rcl_publisher_fini(&state.my_pub, &state.my_node);
        if (rc != RCL_RET_OK) {
            printf("Failed to finalize publisher: %d\n", rc);
        }

        // ノードを削除
        rc = rcl_node_fini(&state.my_node);
        if (rc != RCL_RET_OK) {
            printf("Failed to finalize node: %d\n", rc);
        }

        state.pub_created = false;
    }

private:
    rcl_publisher_t my_pub;
    rcl_node_t my_node;
    rcl_context_t context;
    rcl_node_options_t node_ops;
    rcl_init_options_t init_options;
    rcl_allocator_t allocator;
    rcl_publisher_options_t pub_options;
    bool pub_created {false};

};

// このマクロにより、OmniGraph がノードタイプ定義を自動的に登録・登録解除できるようになる
REGISTER_OGN_NODE()
```

OmniGraph ノード内での ROS 2 コンポーネントの作成・操作には **rcl** ROS 2 API が使われています。C++ ノードでは、**Exec In の条件が真になったときに `compute()` が呼ばれ**、そこで ROS 2 ノードとパブリッシャの初回作成とメッセージの配信が行われます。

## ステップ 4：エクステンションをビルドする

`./build.sh` を実行して、ROS 2 OmniGraph ノードを含む新しいエクステンションをビルドします。ビルドされたエクステンションは `_build/linux-*/release/exts` フォルダに配置されます。

!!! note "Python スタブ生成のエラーは無視してよい"
    ビルド後の Python スタブ生成ステップで出る次のようなエラーメッセージは無視して構いません。ビルドを実行しているターミナルで ROS 2 が source されていないため、スタブファイル（型ヒントや関数／クラスのシグネチャ）の生成時に動的ライブラリをロードできないことが原因です。

    ```text
    running kit for python stubs generation...
    ...
    [Error] [carb] [Plugin: libcustom.cpp.ros2_node.plugin.so] Could not load the dynamic library from ...exts/custom.cpp.ros2_node/bin/libcustom.cpp.ros2_node.plugin.so.
    Error: librcutils.so: cannot open shared object file: No such file or directory...
    [Warning] [carb] Potential plugin preload failed: ...exts/custom.cpp.ros2_node/bin/libcustom.cpp.ros2_node.plugin.so
    [Error] [omni.ext.plugin] [ext: custom.cpp.ros2_node-0.1.0] failed to load native plugin: ...exts/custom.cpp.ros2_node/bin/libcustom.cpp.ros2_node.plugin.so
    ```

## ステップ 5：エクステンションを Isaac Sim に追加する

1. ROS 2 インストールと、上で作成した `tutorial_interfaces` パッケージを含むローカル ROS 2 ワークスペースを source します：

    ```bash
    source /opt/ros/jazzy/setup.bash
    source install/local_setup.bash
    ```

2. このターミナルから Isaac Sim を起動します。
3. **Window > Extensions** を開いて `custom.cpp.ros2_node` エクステンションを検索し、スイッチを切り替えて有効化します。

!!! note "ビルドに使ったのとは別の Isaac Sim アプリケーションで使う場合"
    ビルドに使用したものとは別の Isaac Sim アプリケーションでエクステンションを使いたい場合は、次の手順でエクステンションを利用可能にします：

    1. **Window > Extensions** を開き、検索バー右側のハンバーガーメニュー（1）から **Settings**（2）をクリックします。
    2. **Extension Search Paths** の **+** アイコンをクリックし、前のステップでビルドしたエクステンションのパス（`_build/linux-*/release/exts` 配下）を追加します。
    3. **Third Party** タブ（3）にエクステンションが表示されることを確認し、スイッチを切り替えて有効化します。

    ![エクステンションの追加](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_4.5_full_tut_gui_add_ext_to_isim.png)

## ステップ 6：Action Graph を構築してノードを動かす

`custom.cpp.ros2_node` エクステンションを有効にした状態で：

1. **Window > Graph Editors > Action Graph** を開き、新しい Action Graph を作成します。Action Graph タブで「ROS 2」を検索し、**ROS2 Publish Custom Message** ノードをグラフにドラッグします。
2. **Playback Tick** を検索してグラフに追加します。
3. **On Playback Tick** の Tick を、ROS 2 ノードの **Exec In** に接続します。

    ![カスタム C++ ノードのグラフ](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_4.5_full_tut_gui_custom_cpp_nodes_graph.png)

4. **Play** すると、ノードが ROS 2 への配信を始めます。
5. 新しいターミナルで ROS 2 とローカルワークスペースを source し、トピックを確認します：

    ```bash
    ros2 topic list
    ```

    `/custom_node/sphere_msg` トピックが表示されることを確認し、配信されているメッセージを表示します：

    ```bash
    ros2 topic echo /custom_node/sphere_msg
    ```

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. カスタムメッセージパッケージ（`tutorial_interfaces`）のビルド
2. **Isaac Sim リポジトリ**のテンプレート（`./repo.sh template new`）による、ROS 2 C++ OmniGraph ノードを含むエクステンションの作成とビルド（packman 依存の追加と premake5.lua の構成）
3. エクステンションの Isaac Sim への追加とノードの実行

## 次のステップ

- [チュートリアル 28: ROS 2 Launch](28_launch.md) - ROS 2 Launch で Isaac Sim をデプロイする方法を学びます。
