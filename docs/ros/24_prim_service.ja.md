---
title: プリム属性を操作する ROS 2 サービス
---

# プリム属性を操作する ROS 2 サービス

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- プリム属性を操作するための Isaac Sim の **ROS 2 サービスメッセージ型**（`isaac_ros2_messages`）
- プリムの一覧取得・属性一覧取得・特定属性の読み書きを行う ROS 2 サービスの作成

## はじめに

### 前提条件

- [ROS 2 セットアップ](00_setup.md)が完了していること（`.bashrc` で ROS 2 を source している場合は、Isaac Sim を直接起動できます）
- [チュートリアル 23: ROS 2 汎用サービスサーバとクライアント](23_generic_server_client.md)を完了していること
- サービスを**呼び出す側のターミナル**で、Isaac Sim ROS 2 ワークスペース（`isaac_ros2_messages` パッケージを含む）がビルド・source されていること

!!! note
    Isaac Sim 側では、このサービスは内部 ROS 2 ブリッジライブラリの一部として既に含まれています。ワークスペースが必要なのは、`ros2 service call` を実行する外部ターミナル側でメッセージ型を解決するためです。

### 所要時間

約 15 分

### 概要

**ROS2 Service Prim** ノードを使うと、ステージ上のプリムを ROS 2 サービス経由で外部から調査・操作できます。デバッグや、外部の ROS 2 ノードからシーンの状態を読み書きしたい場合（たとえばテストスクリプトからオブジェクトを動かす）に便利です。

## サービスメッセージ型

ROS2 Service Prim ノードは、次の 4 つのサービスを提供します：

**1. 指定パス配下の全プリムパス（と型）を取得** — `isaac_ros2_messages/srv/GetPrims`

```text
string path             # このパス配下のプリムを取得
---
string[] paths          # プリムパスのリスト
string[] types          # プリムの型名
bool success            # サービス実行の成否
string message          # 情報（エラーメッセージなど）
```

**2. 特定プリムの全属性名と型を取得** — `isaac_ros2_messages/srv/GetPrimAttributes`

```text
string path             # プリムパス
---
string[] names          # 属性のベース名のリスト（Get / Set に使う名前）
string[] displays       # 属性の表示名のリスト（Property タブに表示される名前）
string[] types          # 属性のデータ型のリスト
bool success            # サービス実行の成否
string message          # 情報（エラーメッセージなど）
```

**3. プリム属性の型と値を取得** — `isaac_ros2_messages/srv/GetPrimAttribute`

```text
string path             # プリムパス
string attribute        # 属性名
---
string value            # 属性値（JSON）
string type             # 属性の型
bool success            # サービス実行の成否
string message          # 情報（エラーメッセージなど）
```

**4. プリム属性の値を設定** — `isaac_ros2_messages/srv/SetPrimAttribute`

```text
string path             # プリムパス
string attribute        # 属性名
string value            # 属性値（JSON）
---
bool success            # サービス実行の成否
string message          # 情報（エラーメッセージなど）
```

!!! note "属性値は JSON として読み書きされる"
    プリム属性はキーなしの JSON として直接読み書きされます。配列・ベクトル・行列などの数値コンテナ（例：`pxr.Gf.Vec3f`、`pxr.Gf.Matrix4d`、`pxr.Gf.Quatd`）は**数値のリスト（行優先）**として解釈されます。

## プリム属性を操作してみる

キューブの姿勢をサービス経由で読み書きしてみます。

1. 新しいステージで **Create > Shape > Cube** でキューブを作成します。
2. Action Graph を作成し、次のように **ROS2 Service Prim** ノードを接続します：

    ![プリムサービスグラフ](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/tutorial_ros2_prim_service.png)

3. **Play** するとサービスが開始されます。
4. 新しい ROS 2 ターミナル（`isaac_ros2_messages` を含むワークスペースを source 済み）で、次のコマンドを試します。

サービスの一覧：

```bash
ros2 service list
```

`/World` 配下の全プリムパスと型の取得：

```bash
ros2 service call /get_prims isaac_ros2_messages/srv/GetPrims "{path: /World}"
```

キューブの全属性名と型の取得：

```bash
ros2 service call /get_prim_attributes isaac_ros2_messages/srv/GetPrimAttributes "{path: /World/Cube}"
```

キューブの姿勢（位置・向き）の取得：

```bash
# 位置の取得
ros2 service call /get_prim_attribute isaac_ros2_messages/srv/GetPrimAttribute "{path: /World/Cube, attribute: xformOp:translate}"
# 向きの取得（クォータニオン: wxyz）
ros2 service call /get_prim_attribute isaac_ros2_messages/srv/GetPrimAttribute "{path: /World/Cube, attribute: xformOp:orient}"
```

キューブの姿勢の設定：

```bash
# 位置の設定
ros2 service call /set_prim_attribute isaac_ros2_messages/srv/SetPrimAttribute "{path: /World/Cube, attribute: xformOp:translate, value: [1, 2, 3]}"
# 向きの設定（クォータニオン: wxyz）
ros2 service call /set_prim_attribute isaac_ros2_messages/srv/SetPrimAttribute "{path: /World/Cube, attribute: xformOp:orient, value: [0.7325378, 0.4619398, 0.1913417, 0.4619398]}"
```

ビューポートで、キューブが指定した位置・向きに動くことを確認してください。

## まとめ

このチュートリアルでは、**ROS2 Service Prim** ノードで 4 つのサービス（プリム一覧・属性一覧・属性の取得・属性の設定）を提供し、外部の ROS 2 ターミナルからステージ上のプリムを読み書きしました。

## 次のステップ

- [チュートリアル 25: ROS 2 Python カスタムメッセージ](25_custom_message.md) - 独自のメッセージ型を定義して Isaac Sim で使う方法を学びます。
