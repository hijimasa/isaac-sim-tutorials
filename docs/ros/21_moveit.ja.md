---
title: MoveIt 2
---

# MoveIt 2

## 学習目標

このチュートリアルでは、Isaac Sim のマニピュレーションシーンを **MoveIt 2** と組み合わせて動かします。

## はじめに

### 前提条件

- `isaac_moveit` ROS 2 パッケージが必要です。このパッケージは humble_ws / jazzy_ws に含まれており、launch ファイルと MoveIt の設定を提供します。[ROS 2 セットアップ](00_setup.md)でワークスペース環境が正しくセットアップされていることを確認してください
- 複数マシンで使う場合は、Isaac Sim の起動前と ROS メッセージを送受信するすべてのターミナルで `FASTRTPS_DEFAULT_PROFILES_FILE` を設定し、ROS 2 エクステンションを有効にしておくこと
- [チュートリアル 12: ROS 2 ジョイント制御](12_manipulation.md)を完了していること

### 所要時間

約 15〜20 分

### 概要

!!! note "MoveIt 2 とは"
    [MoveIt 2](https://moveit.picknik.ai/humble/index.html) は ROS 2 の標準的な**モーションプランニングフレームワーク**です。マニピュレータの逆運動学、衝突回避を考慮した軌道計画、実行までを担当します。Isaac Sim 側は[チュートリアル 12](12_manipulation.md) で構築したのと同じ Joint State の双方向接続（`/joint_states` の配信と `/joint_command` の購読）で MoveIt 2 とつながります。つまり、**モバイルロボットにとっての Nav2 に相当するものが、マニピュレータにとっての MoveIt 2** です。

## ステップ 1：MoveIt 2 を実行する

1. **Window > Examples > Robotics Examples** から **ROS2 > MoveIt > Franka MoveIt** のサンプルを開いて環境を読み込み、**Play** でシミュレーションを開始します。
2. launch ファイルで MoveIt 2 を起動します：

    ```bash
    ros2 launch isaac_moveit isaac_moveit.launch.py
    ```

## ステップ 2：ハンド（グリッパー）のプランニング

RViz が起動したら、プランナを操作してみます。

1. **Planning Group** で `hand` が選択されていることを確認します。
2. **Goal State** で `open` を選択します。
3. **Commands** の **Plan** をクリックすると、ハンドの計画された動きが可視化されます。
4. **Execute** をクリックすると、計画どおりにハンドが動きます。

!!! note "既知の問題：hand の close"
    一部のマシンでは、hand プランニンググループの Goal State に `close` を選ぶと実行が失敗／中断し、遅れて実行されたり次の実行時に動いたりすることがあります。

## ステップ 3：アームのプランニング

1. **Planning Group** で `panda_arm` を選択します。
2. 表示される**矢印と回転ディスク**をドラッグして、ロボットの目標位置を設定します。あるいは **Goal State** で `<random_valid>` を選んでも構いません。
3. **Commands** の **Plan** → **Execute** の順にクリックすると、アームの計画された動きが可視化され、そのとおりに動きます。

Isaac Sim 側のビューポートでも、Franka が RViz の計画と同じ軌道で動くことを確認してください。

## トラブルシューティング

RViz のウィンドウで、ロボットが表示されるはずの場所が黒くなっている場合は、Mesa ドライバを更新してください：

```bash
# Mesa ドライバの更新
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:kisak/kisak-mesa
sudo apt install -y mesa-utils
sudo apt -y upgrade
```

## まとめ

このチュートリアルでは、Isaac Sim のマニピュレーションシーン（Franka）を MoveIt 2 と接続し、ハンドとアームのモーションプランニング（Plan / Execute）を実行しました。

## 次のステップ

- [チュートリアル 22: ROS 2 汎用パブリッシャとサブスクライバ](22_generic_pub_sub.md) - 任意の ROS 2 トピックへの配信・購読を学びます。

### さらに学ぶには

- [MoveIt 2 公式ドキュメント](https://moveit.picknik.ai/humble/index.html)
- スタンドアロン版のサンプルは[チュートリアル 17](17_standalone_python.md) の MoveIt 2 の節を参照してください。
