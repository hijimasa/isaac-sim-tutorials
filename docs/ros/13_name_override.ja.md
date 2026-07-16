---
title: NameOverride 属性
---

# NameOverride 属性

## 学習目標

このチュートリアルでは、**`isaac:nameOverride`** プリム属性について学び、ジョイント名や TF の配信にカスタム名を使う方法を習得します。

## はじめに

### 前提条件

- [チュートリアル 12: ROS 2 ジョイント制御](12_manipulation.md)を完了し、Joint State パブリッシャ／サブスクライバの構築方法を理解していること
- [チュートリアル 9: ROS 2 Transform ツリーとオドメトリ](09_tf.md)を完了し、TF パブリッシャの構築方法を理解していること
- Python スクリプトを実行するターミナルで適切な ros2_ws が source されていること
- 複数マシンで使う場合は、Isaac Sim 起動前に `FASTRTPS_DEFAULT_PROFILES_FILE` が設定され、ROS 2 ブリッジが有効であること

### 所要時間

約 10〜15 分

### 概要

Joint State や TF のパブリッシャは、ROS のリンク名・ジョイント名として**プリム名**をそのまま使います。しかし、既存の ROS スタック（URDF やコントローラ設定）が期待する名前とプリム名が一致しないことがあります。たとえば USD への変換過程で名前が変わってしまった場合や、同じアセットを別の命名規約のシステムに接続したい場合です。

**`isaac:nameOverride`** プリム属性を使うと、**プリム自体の名前は変えずに**、ROS への配信時に使われる名前だけを内部的に上書きできます。

## ステップ 1：isaac:nameOverride 属性を追加する

先に[チュートリアル 12 のステップ 3（Python スクリプトでグラフを構築する）](12_manipulation.md)の手順でシーンをセットアップしておきます。

1. 任意のジョイントプリムをクリックします。
2. Property パネルの Raw USD Properties に **Name Override** フィールドがあるか確認します。既にあれば次のステップへ進みます。
3. ない場合は、Property パネルの **Add** をクリックし、ポップアップメニューから **Isaac > NameOverride** を選択して属性を適用します。
4. **Name Override** フィールドに任意のカスタム名を入力します。
5. **Play** を押して `/joint_states` トピックを echo すると、ジョイント名が設定したカスタム名に変わっていることを確認できます：

    ```bash
    ros2 topic echo /joint_states
    ```

## ステップ 2：パブリッシャとサブスクライバでの挙動

### ROS パブリッシャ側

**ROS2 Publish Transform Tree** と **ROS2 Publish Joint State** の OmniGraph ノードは、プリムに `isaac:nameOverride` 属性が定義されていれば、**自動的に**その名前を使って配信します。追加の設定は不要です。

### ROS サブスクライバ側

サブスクライバ側（`/joint_command` を受けて Articulation Controller でロボットを動かすパイプライン）では、外部から届く指令に含まれる**カスタム名を実際のプリムパスに解決する**必要があります。そのために **Isaac Joint Name Resolver** OmniGraph ノードを使います。

1. **Isaac Joint Name Resolver** ノードをグラフにドラッグし、次のようにパイプラインに接続します：

    ![NameOverride 属性とサブスクライバ](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_4.5_ros_tut_gui_ros2_isaac_nameoverride_attr.png)

2. **Isaac Joint Name Resolver** ノードの **Target Prim**（または **Robot Path**）を `/panda` に設定します。

外部の ROS 2 ノードがカスタムプリム名でジョイント指令を配信すると、Isaac Joint Name Resolver ノードが実際のプリムパスを Articulation Controller に渡し、指令どおりにロボットを操作できるようになります。

## まとめ

このチュートリアルでは、プリムに `isaac:nameOverride` 属性を追加して、ROS への配信・ROS からの操作にカスタム名を使う方法を扱いました：

1. **Name Override** 属性の追加とカスタム名の設定
2. パブリッシャ（Joint State / TF）は**自動的に**カスタム名を使用
3. サブスクライバ側は **Isaac Joint Name Resolver** ノードで名前を解決

## 次のステップ

- [チュートリアル 14: ROS 2 Ackermann コントローラ](14_ackermann.md) - アッカーマンステアリング車両のコントローラをセットアップする方法を学びます。
