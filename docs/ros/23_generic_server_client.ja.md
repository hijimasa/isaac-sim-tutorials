---
title: ROS 2 汎用サービスサーバとクライアント
---

# ROS 2 汎用サービスサーバとクライアント

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- 任意の型の ROS 2 サービスリクエストを受信して応答する**汎用サーバーノード**の使い方
- 任意の型のリクエストを送信して応答を受け取る**汎用クライアントノード**の使い方

## はじめに

### 前提条件

- [ROS 2 セットアップ](00_setup.md)が完了していること（`.bashrc` で ROS 2 を source している場合は、Isaac Sim を直接起動できます）
- [チュートリアル 22: ROS 2 汎用パブリッシャとサブスクライバ](22_generic_pub_sub.md)を完了していること（メッセージ型の指定と属性再構成の考え方は共通です）
- 複数マシンで使う場合は `FASTRTPS_DEFAULT_PROFILES_FILE` の設定と ROS 2 エクステンションの有効化

### 所要時間

約 15〜20 分

### 概要

!!! note "サービスとトピックの違い"
    トピックが連続的なデータストリームの一方向配信であるのに対し、**サービス**は「リクエストを送ると応答が返ってくる」**双方向・一回ごと**の通信です。サービスの設定ファイルは 2 つのセクションから成ります：

    1. クライアントが送り、サーバーが受け取る**リクエスト**メッセージの定義
    2. サーバーが送り、クライアントが受け取る**レスポンス**メッセージの定義

    環境に存在するサービス型は次のコマンドで一覧できます：

    ```bash
    ros2 interface list --only-srvs
    ```

    実際のサービス定義は、ROS ディストロの `share/<packageName>/srv/<serviceName>` で確認できます（例：`std_srvs/srv/SetBool` なら `share/std_srvs/srv/SetBool`）。

## 汎用サーバー

### 基本の使い方

1. Action Graph を作成し、次のノードを追加します：

| ノード | 役割 |
|---|---|
| **On Playback Tick** | 毎フレーム実行 |
| **ROS2 Context** | コンテキストの作成 |
| **ROS2 Service Server Request** | 任意の型のサービスリクエストを**受信**する |
| **ROS2 Service Server Response** | 任意の型のサービスリクエストに**応答**する |

2. 次の接続がポイントです：
    - Request ノードの **Server Handle** 出力 → Response ノードの **Server Handle** 入力：2 つのノードが**同じサーバーを共有**するための接続
    - Request ノードの **On received** 実行出力 → Response ノードの **On received** 入力：**リクエストを受信したときだけ**応答を送るための接続
    - Playback Tick → Request ノード、Context → Request / Response 両ノード

    ![汎用サーバーグラフ](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/tutorial_ros2_server_1.PNG)

3. Property パネルでメッセージ型を `messagePackage` / `messageSubfolder` / `messageName` のパターンで指定します。たとえば `std_srvs/srv/SetBool` なら、messagePackage は `std_srvs`、messageSubfolder は `srv`、messageName は `SetBool` です。

!!! warning "Request と Response で同じ型を指定すること"
    Server Handle で接続された **ROS2 Service Server Request と Response の両ノードに、同じメッセージフィールドを入力**する必要があります。有効な型を指定すると、Request ノードの**出力**にはサービスの**リクエスト**フィールドが、Response ノードの**入力**には**レスポンス**フィールドが再構成されます（再生は不要です）。

![Request ノードの出力再構成](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/tutorial_ros2_server_2.PNG)

![Response ノードの入力再構成](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/tutorial_ros2_server_3.PNG)

4. Request ノードの **Service Name** プロパティは変更できます。クライアントはこの名前でサーバーと通信します。

### 動かしてみる

設定完了後のサーバーの例：

![サーバーの最終形](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/tutorial_ros2_server_4.PNG)

1. シミュレーションを **Play** します。サーバーがリクエストを受け付ける状態になります。
2. **ROS2 Service Server Response** の入力フィールドに、クライアントへ返すサンプルメッセージと成否の bool 値を設定します。
3. 別のターミナルで ROS を source し、`data: true` の SetBool リクエストをサービス名 `/service_name` のサーバーへ送ります：

    ```bash
    ros2 service call /service_name std_srvs/srv/SetBool "{data: true}"
    ```

4. サーバーノードで設定した応答が返ることを確認します：

    ```text
    requester: making request: std_srvs.srv.SetBool_Request(data=True)

    response:
    std_srvs.srv.SetBool_Response(success=True, message='Sample response message')
    ```

## 汎用クライアント

### 基本の使い方

1. Action Graph に **On Playback Tick**、**ROS2 Context**、**ROS2 Service Client**（任意の型のリクエストを送信し、応答を受信するノード）を追加・接続します。
2. Property パネルでメッセージ型を同じパターンで指定します。Client ノードの**入力**にはリクエストフィールド、**出力**にはレスポンスフィールドが再構成されます：

    ![Client ノードの再構成](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/tutorial_ros2_client_1.PNG)

3. **Play** すると、クライアントは入力データに従ってリクエストの送信を開始します。サーバーの応答はノードの出力から取得できます。

### 例：サーバーとクライアントを同じグラフでつなぐ

先ほどのサーバーの例にクライアントノードを追加すると、ターミナルの代わりに OmniGraph 内からリクエストを送れます。

1. 次のようなグラフを作成します：

    ![サーバー＋クライアントグラフ](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/tutorial_ros2_server_client_1.PNG)

2. **Play** すると、クライアントとサーバーがリクエストとレスポンスを送受信し始めます。
3. **ROS2 Service Server Response** を選択して、入力の **Response Message** フィールドでサーバーの応答メッセージを変更します。
4. **ROS2 Service Client** ノードを選択し、サーバーで設定した応答をクライアントが受信していることを確認します。

## まとめ

このチュートリアルでは、汎用サーバー（Request / Response の 2 ノード構成と Server Handle の共有）と汎用クライアントのノードを設定し、任意の ROS 2 サービスメッセージを Isaac Sim で送受信する方法を学びました。

## 次のステップ

- [チュートリアル 24: プリム属性を操作する ROS 2 サービス](24_prim_service.md) - プリムの一覧取得や属性の読み書きを ROS 2 サービスとして提供する方法を学びます。
