---
title: ROS 2 RTF のパブリッシュ
---

# ROS 2 Real Time Factor（RTF）のパブリッシュ

## 学習目標

このチュートリアルでは、Isaac Sim の **Real Time Factor（RTF）** を ROS 2 の Float32 メッセージとしてパブリッシュする方法を学びます。

## はじめに

### 前提条件

- [ROS 2 セットアップ](00_setup.md)が完了していること
- ROS 2 ブリッジエクステンション（`isaacsim.ros2.bridge`）が有効であること（**Window > Extensions** で確認）

### 所要時間

約 5〜10 分

### 概要

!!! note "RTF（Real Time Factor）とは"
    RTF は、シミュレーションが実時間に対してどれだけ速く／遅く進んでいるかを表す指標で、フレームごとに次の式で計算されます：

    $$
    RTF = \frac{シミュレーション経過時間}{実経過時間}
    $$

    - **RTF > 1**：シミュレーション時間が実時間より**速く**進んでいる
    - **RTF < 1**：シミュレーションが実時間より**遅い**（重い処理などが原因）

    実機と連携するシステムやリアルタイム性が重要な検証では、RTF を監視してシミュレーションが実時間に追従できているかを確認します。ROS 2 トピックとして配信しておけば、既存の監視ツールでそのまま記録・可視化できます。

## RTF をパブリッシュする

このチュートリアルでは、前のチュートリアルの最後に登場した**グラフショートカット**（Generic Publisher）を使ってグラフを自動生成します。

1. **Tools > Robotics > ROS 2 OmniGraphs > Generic Publisher** を開きます。パラメータのポップアップウィンドウが表示されます。
2. **Publish RTF as Float32** を選択して **OK** をクリックします。

    ![RTF パラメータ設定](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/tutorial_ros2_rtf_param.png)

3. **Isaac Real Time Factor** ノードが汎用の **ROS2 Publisher** ノード（`std_msgs/msg/Float32` を配信するよう設定済み）に接続された、新しい Action Graph が作成されます。
4. Stage パネルで `/Graph/ROS_GenericPub` にある Action Graph プリムを右クリックし、**Open Graph** を選択します。自動生成されたグラフが次と一致することを確認します：

    ![RTF グラフ](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/tutorial_ros2_rtf_graph.png)

5. **Play** をクリックしてシミュレーションを開始します。
6. ROS 2 を source したターミナルで、Isaac Sim からパブリッシュされる RTF の値を確認します：

    ```bash
    ros2 topic echo /topic
    ```

    負荷のかかっていないシステムであれば、RTF は 1.0 に近い値になるはずです。

!!! tip "トピック名について"
    自動生成されたグラフのトピック名は既定で `/topic` です。実際のシステムに組み込む場合は、グラフ内の ROS2 Publisher ノードの **topicName** を `/rtf` などのわかりやすい名前に変更するとよいでしょう。

## まとめ

このチュートリアルでは、OmniGraph のショートカット（Generic Publisher）を使って、ROS 2 の RTF パブリッシャグラフを自動生成する方法を扱いました。

## 次のステップ

- [チュートリアル 5: ROS 2 カメラ](05_camera.md) - カメラを追加し、グラウンドトゥルースの合成知覚データを ROS 2 トピックで受信する方法を学びます。
