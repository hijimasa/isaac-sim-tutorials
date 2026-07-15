---
title: ROS 2 セットアップ
---

# ROS 2 セットアップ（Linux / Windows）

## このページについて

ROS 2 チュートリアルシリーズを進めるために必要な、**Isaac Sim と ROS 2 の接続環境のセットアップ手順**をまとめたページです。公式ドキュメントの [ROS 2 Installation](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/installation/install_ros.html) の内容を、Linux と Windows それぞれの流れに沿って整理し直しています。

!!! warning "Windows ユーザーへ：ROS 2 は WSL2 で動かすのが公式サポート方式です"
    Isaac Sim 5.1 の公式ドキュメントでは、**Windows 10 / 11 での ROS 2 の実行方法は「WSL2 上の Ubuntu 22.04 に ROS 2 Humble をインストールする」方式のみ**が案内されています。Windows ネイティブの ROS 2（Chocolatey や公式 Windows バイナリによるインストール）を Isaac Sim と組み合わせる手順は提供されていません。

    仕組みとしては、**Isaac Sim 本体は Windows 側で動かし**（ROS 2 ブリッジは Isaac Sim 同梱の内部 ROS 2 ライブラリを使用）、**ROS 2 のノード群（teleop、Nav2、RViz2 など）は WSL2 内で動かして**、両者を DDS（ネットワーク）経由で通信させます。手順は本ページの「Windows でのセットアップ」を参照してください。

## 対応プラットフォームと ROS 2 ディストリビューション

| プラットフォーム | 対応 ROS 2 | 備考 |
|---|---|---|
| Ubuntu 24.04 | Jazzy（推奨） | apt でデフォルトインストール |
| Ubuntu 22.04 | Humble（推奨）、Jazzy | Humble は apt、Jazzy はソースビルドが必要 |
| Windows 10 / 11 | Humble | **WSL2 上の Ubuntu 22.04** にインストール |

!!! note "重要な前提：Isaac Sim は Python 3.11 のみ対応"
    Isaac Sim 5.1 は **Python 3.11 のみ**に対応しています。一方、ROS 2 Humble（Ubuntu 22.04）は Python 3.10、Jazzy（Ubuntu 24.04）は Python 3.12 が標準です。このズレを吸収するために、Isaac Sim には **Python 3.11 でビルドされた内部 ROS 2 ライブラリ**（Humble / Jazzy）が同梱されています。

    - **Isaac Sim を起動するターミナル**では、通常の ROS 2 インストールを source **しない**でください（内部ライブラリが自動で使われます）。source すると Python バージョンの不一致でエラーになります。
    - **外部の ROS 2 ノードを動かすターミナル**では、通常どおり ROS 2 を source して構いません。データ転送は DDS が担うため、Python バージョンが違っても通信できます。
    - `rclpy` を Isaac Sim 内部（Script Editor など）で使いたい場合や、カスタムメッセージを使う場合は、Python 3.11 でワークスペースをビルドする追加手順が必要です（後述）。

## Linux でのセットアップ

### 1. ROS 2 のインストール

**Ubuntu 22.04（Humble）** の場合、[ROS 2 公式の手順](https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debians.html)どおり apt でインストールします。

（オプション）ROS 2 ブリッジの一部メッセージ型が依存するパッケージも入れておくと後がスムーズです：

```bash
# バウンディングボックス配信（Detection2DArray / Detection3DArray）に必要
sudo apt install ros-humble-vision-msgs
# アッカーマンステアリング指令（AckermannDriveStamped）に必要
sudo apt install ros-humble-ackermann-msgs
```

**Ubuntu 24.04（Jazzy）** の場合は、同様に [Jazzy 公式の手順](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debians.html)でインストールし、オプションパッケージは `ros-jazzy-vision-msgs` / `ros-jazzy-ackermann-msgs` になります。

### 2. Isaac Sim の起動方法

**推奨：内部 ROS 2 ライブラリを使う**（何も source していないターミナルから起動するだけです）：

```bash
./isaac-sim.sh
```

- Ubuntu 22.04 では内部の Humble ライブラリ、Ubuntu 24.04 では内部の Jazzy ライブラリが自動的にロードされます（`ROS_DISTRO` 環境変数が未設定の場合）。
- ROS 2 ブリッジエクステンション（`isaacsim.ros2.bridge`）は既定で有効です。

内部ライブラリをターミナルから明示的に指定したい場合は、次の環境変数を設定してから起動します（Humble の例）：

```bash
export isaac_sim_package_path=$HOME/isaacsim
export ROS_DISTRO=humble
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
# 注意：1 つのターミナルで 1 回だけ実行すること（複数回実行するとパスが重複して競合の原因になる）
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$isaac_sim_package_path/exts/isaacsim.ros2.bridge/humble/lib

$isaac_sim_package_path/isaac-sim.sh
```

### 3. Isaac Sim ROS ワークスペースのセットアップ

ROS 2 チュートリアルの多く（Nav2、MoveIt 2、カスタムメッセージなど）は、NVIDIA が提供する [IsaacSim-ros_workspaces](https://github.com/isaac-sim/IsaacSim-ros_workspaces) リポジトリのパッケージを使います。**外部ノード用のターミナル**で次のようにビルドしておきます（Humble の例）：

```bash
# ビルドに必要なツール
sudo apt install python3-rosdep build-essential python3-colcon-common-extensions

# ROS 2 を source
source /opt/ros/humble/setup.bash

# ワークスペースの取得とビルド
git clone https://github.com/isaac-sim/IsaacSim-ros_workspaces.git
cd IsaacSim-ros_workspaces/humble_ws
git submodule update --init --recursive
rosdep install -i --from-path src --rosdistro humble -y
colcon build
```

以降、新しいターミナルを開くたびに次を実行して使います：

```bash
source /opt/ros/humble/setup.bash
cd <クローン先>/IsaacSim-ros_workspaces/humble_ws
source install/local_setup.bash
```

### 4.（必要な場合のみ）複数マシン・Docker と通信する

同一マシン内の通信であれば FastDDS の既定設定（共有メモリ転送）が最速のためそのままで構いません。**別マシンや Docker コンテナ上の ROS 2 ノード**と通信する場合は、UDP 転送を有効にした FastDDS プロファイルが必要です：

1. `~/.ros/fastdds.xml` に UDP 転送を有効化するプロファイルを作成します（内容は公式ドキュメントの On Linux with Fast DDS 節のスニペットをそのまま使用）。
2. ROS 2 を使うすべてのターミナルで `export FASTRTPS_DEFAULT_PROFILES_FILE=~/.ros/fastdds.xml` を実行します。

## Windows でのセットアップ（WSL2）

前述のとおり、Windows では **ROS 2 を WSL2 内で動かす**のが公式サポート方式です。役割分担は次のとおりです：

| 場所 | 動かすもの |
|---|---|
| Windows 側 | Isaac Sim 本体（内部 ROS 2 Humble ライブラリでブリッジを実行） |
| WSL2（Ubuntu 22.04）側 | ROS 2 Humble と外部ノード（teleop、Nav2、RViz2 など） |

### 1. WSL2 と Ubuntu 22.04 のインストール

管理者権限の PowerShell で：

```powershell
wsl --set-default-version 2
wsl --install -d Ubuntu-22.04
```

インストール完了後にマシンを再起動し、スタートメニューから Ubuntu 22.04 アプリを開きます（初回はセットアップに数分かかります）。

!!! note "仮想化のエラーが出る場合"
    仮想化の有効化に関するエラーが出る場合は、[Microsoft の仮想化有効化手順](https://support.microsoft.com/en-us/windows/enable-virtualization-on-windows-11-pcs-c5578302-6e43-4b4b-a449-8ced115f58e1)（BIOS/UEFI での設定を含む）に従ってください。

### 2. WSL2 内に ROS 2 Humble をインストール

WSL2 のターミナルで、上の「Linux でのセットアップ」の Ubuntu 22.04（Humble）の手順をそのまま実行します。ワークスペースのセットアップ（IsaacSim-ros_workspaces のビルド）も WSL2 内で行います。

### 3. Windows ⇔ WSL2 間の通信設定（ポートフォワーディング）

WSL2 は既定で Windows ホストとは別の仮想ネットワーク（NAT）上にあるため、DDS の通信を通すための設定を行います。

1. WSL2 側の IP アドレスを確認します（WSL2 のターミナルで）：

    ```bash
    hostname -I
    ```

2. Windows 側の IPv4 アドレスを確認します（管理者権限の PowerShell で）：

    ```powershell
    ipconfig /all
    ```

3. PowerShell で変数に IP アドレスを設定します：

    ```powershell
    $Windows_IP = "<WINDOWS_IP>"
    $WSL2_IP = "<WSL2_IP>"
    ```

4. ROS 2 の既定 DDS（FastDDS）が使うポートのフォワーディングを設定します：

    ```powershell
    netsh interface portproxy add v4tov4 listenport=7400 listenaddress=$Windows_IP connectport=7400 connectaddress=$WSL2_IP
    netsh interface portproxy add v4tov4 listenport=7410 listenaddress=$Windows_IP connectport=7410 connectaddress=$WSL2_IP
    netsh interface portproxy add v4tov4 listenport=9387 listenaddress=$Windows_IP connectport=9387 connectaddress=$WSL2_IP
    ```

!!! tip "通信がうまくいかない場合：WSL2 のミラーモード（本サイト補足）"
    ここから先はこのサイト独自の補足です。WSL2 の IP アドレスは**再起動のたびに変わる**ため、うまくいかなくなったらポートフォワーディングを再設定する必要があります。また `netsh interface portproxy` は TCP の転送を対象とした仕組みのため、環境によっては DDS（UDP を多用）の通信が確立しないという報告もあります。

    その場合の代替として、**Windows 11 22H2 以降**では WSL2 の**ミラーモード（mirrored networking mode）**が利用できます。`%UserProfile%\.wslconfig` に以下を記述して `wsl --shutdown` で再起動すると、WSL2 が Windows とネットワークインターフェースを共有するようになり、ポートフォワーディングなしで localhost 同士のように通信できる場合があります：

    ```ini
    [wsl2]
    networkingMode=mirrored
    ```

    公式ドキュメントに記載された手順はあくまでポートフォワーディング方式なので、まず公式手順を試し、だめならこちらを検討してください。

### 4. Windows 側で Isaac Sim を起動

コマンドプロンプトの場合：

```bat
set isaac_sim_package_path=C:\isaacsim
set ROS_DISTRO=humble
set RMW_IMPLEMENTATION=rmw_fastrtps_cpp
REM 注意：1 つのターミナルで 1 回だけ実行すること
set PATH=%PATH%;%isaac_sim_package_path%\exts\isaacsim.ros2.bridge\humble\lib

REM ROS 2 ブリッジを有効にして Isaac Sim を起動
%isaac_sim_package_path%\isaac-sim.bat --/isaac/startup/ros_bridge_extension=isaacsim.ros2.bridge
```

PowerShell の場合：

```powershell
$env:isaac_sim_package_path = "C:\isaacsim"
$env:ROS_DISTRO = "humble"
$env:RMW_IMPLEMENTATION = "rmw_fastrtps_cpp"
$env:PATH = "$env:PATH;$env:isaac_sim_package_path\exts\isaacsim.ros2.bridge\humble\lib"

& "$env:isaac_sim_package_path\isaac-sim.bat" --/isaac/startup/ros_bridge_extension=isaacsim.ros2.bridge
```

これで、Isaac Sim（Windows 側）と WSL2 内の ROS 2 ノードが通信できるようになります。

### Windows（WSL2）方式の制限事項

公式ドキュメントに明記されている制限です：

- **カスタムパッケージ／カスタムメッセージ**を Isaac Sim 側（Python 3.11）に組み込む方式は Windows では非対応です。すべての ROS 2 パッケージは WSL2 内で動かします。
- **Docker ワークフロー**（ROS を Docker コンテナで動かす方式）は Windows（WSL2）では非対応です。
- **Cyclone DDS** は Windows（WSL2）では非対応です（FastDDS を使用してください）。

!!! note "GUI ツール（RViz2 など）について（本サイト補足）"
    最近の WSL2 は **WSLg** により Linux GUI アプリをそのまま表示できるため、RViz2 や rqt などの GUI ツールも WSL2 内から起動して使えます。特別な X サーバーのインストールは通常不要です。

## rclpy・カスタムパッケージを Isaac Sim 内で使う場合（Linux のみ）

Script Editor やスタンドアロン Python から `rclpy` を使う、またはカスタムメッセージを Isaac Sim 側でも認識させる場合は、**Python 3.11 でビルドした ROS 2 ワークスペース**が必要です。[IsaacSim-ros_workspaces](https://github.com/isaac-sim/IsaacSim-ros_workspaces) に専用の Dockerfile が用意されています：

```bash
cd IsaacSim-ros_workspaces
./build_ros.sh -d humble -v 22.04
```

ビルド後、新しいターミナルで Python 3.11 版のビルドを source してから Isaac Sim を起動します：

```bash
source build_ws/humble/humble_ws/install/local_setup.bash
source build_ws/humble/isaac_sim_ros_ws/install/local_setup.bash
# このターミナルから Isaac Sim を起動する
```

## 動作確認

セットアップの確認には、[チュートリアル 2: ROS 2 メッセージで TurtleBot を駆動する](02_drive_turtlebot.md)の「ROS 接続を確認する」の手順が使えます。より簡単には：

1. Isaac Sim 側で ROS 2 ブリッジが有効なことを確認（**Window > Extensions** で `isaacsim.ros2.bridge` が有効）
2. 外部ノード側のターミナル（Linux ならローカル、Windows なら WSL2）で：

    ```bash
    ros2 topic list
    ```

    Isaac Sim 側でトピックをパブリッシュするグラフを動かしていれば、そのトピックが見えるはずです。

## まとめ

| 項目 | Linux | Windows |
|---|---|---|
| ROS 2 の場所 | ローカル（apt インストール） | **WSL2 内**の Ubuntu 22.04 |
| Isaac Sim 側のブリッジ | 内部 ROS 2 ライブラリ（自動） | 内部 ROS 2 ライブラリ（起動オプション指定） |
| 追加のネットワーク設定 | 不要（同一マシンなら共有メモリ） | ポートフォワーディング（または ミラーモード） |
| カスタムパッケージを Isaac Sim 内で使用 | 可（Python 3.11 ビルドが必要） | 不可（WSL2 側でのみ使用可） |
| Docker ワークフロー | 可 | 不可 |

## 次のステップ

- [チュートリアル 1: URDF インポート: Turtlebot](01_urdf_import_turtlebot.md)からシリーズを始めましょう。
