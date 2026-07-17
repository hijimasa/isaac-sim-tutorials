---
title: ROS 2 セットアップ
---

# ROS 2 セットアップ（Linux / Windows）

## このページについて

ROS 2 チュートリアルシリーズを進めるために必要な、**Isaac Sim と ROS 2 の接続環境のセットアップ手順**をまとめたページです。公式ドキュメントの [ROS 2 Installation (Default)](https://docs.isaacsim.omniverse.nvidia.com/latest/installation/install_ros.html)（Ubuntu 24.04 + Jazzy）と [ROS 2 Installation (Other Platforms)](https://docs.isaacsim.omniverse.nvidia.com/latest/installation/install_ros_other_platforms.html)（Ubuntu 22.04 / Windows）の内容を、Linux と Windows それぞれの流れに沿って整理し直しています。

!!! warning "Windows ユーザーへ：Pixi によるネイティブ ROS 2 が正式サポートされました"
    Isaac Sim 6.0 から、**Windows 11 では [Pixi](https://pixi.sh/) を使った ROS 2 Jazzy のネイティブインストールが正式サポート**されました（[IsaacSim-ros_workspaces](https://github.com/isaac-sim/IsaacSim-ros_workspaces) リポジトリの Pixi ワークスペースを使用。RoboStack の conda パッケージで ROS 2 を導入します）。WSL2 が不要になり、**すべての ROS 2 チュートリアルが Windows でサポート対象**になります。

    従来の「WSL2 上の Ubuntu に ROS 2 をインストールする」方式も引き続き使えますが、公式ドキュメントでは **WSL 方式は非推奨（Deprecated）** の扱いになりました（WSL 方式ではカスタム ROS インターフェースが使えないなどの制限があります）。手順は本ページの「Windows でのセットアップ」を参照してください。

## 対応プラットフォームと ROS 2 ディストリビューション

| プラットフォーム | 対応 ROS 2 | 備考 |
|---|---|---|
| Ubuntu 24.04 | Jazzy（推奨） | apt でデフォルトインストール。**公式の既定構成** |
| Ubuntu 22.04 | Humble、Jazzy | Humble は apt、Jazzy はソースビルドが必要（Other Platforms 参照） |
| Windows 11 | Jazzy（**Pixi**）、Humble / Jazzy（WSL2・非推奨） | Pixi 方式は Jazzy のみ対応 |

!!! note "Isaac Sim 6.0 は Python 3.12 ベースになりました"
    Isaac Sim 6.0 は **Python 3.12** を使用します。**Ubuntu 24.04 の ROS 2 Jazzy も Python 3.12** なので、5.1 までのような「Python バージョンのズレを内部ライブラリで吸収する」必要がなくなり、**ネイティブの ROS 2 を source したターミナルからそのまま Isaac Sim を起動する**のが既定のワークフローになりました。

    - **既定の使い方**：ROS 2（とワークスペース）を source したターミナルから Isaac Sim を起動します。`rclpy` やカスタムメッセージも、Ubuntu 24.04 + Jazzy なら通常どおりビルドしたワークスペースをそのまま使えます。
    - 何も source していない場合は、Isaac Sim 同梱の**内部 ROS 2 Jazzy ライブラリ**が自動ロードされます（ROS 2 が sourced かどうかの判定には `ROS_DISTRO` 環境変数が使われます）。
    - **実験的機能**：ネイティブにインストールされていれば、Humble / Jazzy 以外の ROS 2 ディストロも source して起動するだけで動作する可能性があります（公式にテストされているのは Humble と Jazzy です）。

## Linux でのセットアップ

以降の手順は公式の既定構成（**Ubuntu 24.04 + ROS 2 Jazzy**）を前提にします。Ubuntu 22.04（Humble / Jazzy）を使う場合は公式の [ROS 2 Installation (Other Platforms)](https://docs.isaacsim.omniverse.nvidia.com/latest/installation/install_ros_other_platforms.html) を参照してください。

### 1. ROS 2 のインストール

[ROS 2 Jazzy 公式の手順](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html)どおり apt でインストールします。

（オプション）ROS 2 ブリッジの一部メッセージ型が依存するパッケージも入れておくと後がスムーズです：

```bash
# バウンディングボックス配信（Detection2DArray / Detection3DArray）に必要
sudo apt install ros-jazzy-vision-msgs
# アッカーマンステアリング指令（AckermannDriveStamped）に必要
sudo apt install ros-jazzy-ackermann-msgs
```

インストール後、ROS 2 コマンドを使うすべてのターミナル（または `~/.bashrc`）で source します：

```bash
source /opt/ros/jazzy/setup.bash
```

### 2. Isaac Sim ROS ワークスペースのセットアップ

ROS 2 チュートリアルの多く（Nav2、MoveIt 2、カスタムメッセージなど）は、NVIDIA が提供する [IsaacSim-ros_workspaces](https://github.com/isaac-sim/IsaacSim-ros_workspaces) リポジトリのパッケージを使います：

```bash
# ビルドに必要なツール
sudo apt install python3-rosdep build-essential python3-colcon-common-extensions

# ROS 2 を source
source /opt/ros/jazzy/setup.bash

# ワークスペースの取得とビルド
git clone https://github.com/isaac-sim/IsaacSim-ros_workspaces.git
cd IsaacSim-ros_workspaces/jazzy_ws
git submodule update --init --recursive
rosdep install -i --from-path src --rosdistro jazzy -y
colcon build
```

以降、新しいターミナルを開くたびに次を実行して使います：

```bash
source /opt/ros/jazzy/setup.bash
cd <クローン先>/IsaacSim-ros_workspaces/jazzy_ws
source install/local_setup.bash
```

!!! note "`isaacsim` パッケージは `isaacsim_bringup` にリネームされました"
    Isaac Sim を ROS 2 ノードとして起動するための launch ファイルを含むパッケージは、6.0 で `isaacsim` から **`isaacsim_bringup`** にリネームされました。launch コマンドは `ros2 launch isaacsim_bringup <launchファイル>` の形になります（詳細は[チュートリアル 28: ROS 2 Launch](28_launch.md)）。また、H.264 圧縮画像をデコードする **`isaac_compressed_image_decoder`** パッケージが新たに追加されています。

### 3. Isaac Sim の起動方法

**推奨：ROS 2 とワークスペースを source したターミナルから起動**します：

```bash
source /opt/ros/jazzy/setup.bash
source <クローン先>/IsaacSim-ros_workspaces/jazzy_ws/install/local_setup.bash
./isaac-sim.sh
```

- ROS 2 ブリッジエクステンション（`isaacsim.ros2.bridge`）は既定で有効です。
- 何も source していないターミナルから起動した場合は、内部の ROS 2 Jazzy ライブラリが自動的にロードされます。

### 4.（オプション）内部 ROS 2 ライブラリを使う

ネイティブの ROS 2 を用意できない場合（ROS を Docker コンテナで動かす構成など）は、Isaac Sim 同梱の内部ライブラリで動かせます。また、`./python.sh` で**スタンドアロンスクリプト**を実行する場合に内部ライブラリを使うには、環境変数の手動設定が必要です：

```bash
export isaac_sim_package_path=$HOME/isaacsim
export ROS_DISTRO=jazzy
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
# 注意：1 つのターミナルで 1 回だけ実行すること（複数回実行するとパスが重複して競合の原因になる）
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$isaac_sim_package_path/exts/isaacsim.ros2.core/jazzy/lib

# Isaac Sim 本体の起動
$isaac_sim_package_path/isaac-sim.sh
# または、スタンドアロンスクリプトの実行
$isaac_sim_package_path/python.sh <path/to/standalone/script>
```

!!! note "内部ライブラリのパスが変わりました"
    5.1 までの `exts/isaacsim.ros2.bridge/<distro>/lib` は、6.0 で **`exts/isaacsim.ros2.core/<distro>/lib`** に変わりました。

### 5.（必要な場合のみ）複数マシン・Docker と通信する

同一マシン内の通信であれば FastDDS の既定設定（共有メモリ転送）が最速のためそのままで構いません。**別マシンや Docker コンテナ上の ROS 2 ノード**と通信する場合は、UDP 転送を有効にした FastDDS プロファイルが必要です：

1. ワークスペースをセットアップした場合は `<ros2_ws>` 直下に `fastdds.xml` が用意されています。そうでない場合は `~/.ros/fastdds.xml` に UDP 転送を有効化するプロファイルを作成します（内容は公式ドキュメントの Enabling the ROS 2 Bridge using Fast DDS 節のスニペットをそのまま使用）。
2. ROS 2 を使うすべてのターミナルで `export FASTRTPS_DEFAULT_PROFILES_FILE=<パス>/fastdds.xml` を実行します。

!!! note "ミドルウェアの選択肢：Cyclone DDS / Zenoh"
    Isaac Sim 6.0 の ROS 2 ブリッジは、FastDDS（既定）のほかに **Cyclone DDS**（Linux、Humble / Jazzy）と **RMW Zenoh**（Linux、Jazzy）をサポートします。Zenoh を使う場合は `sudo apt install ros-jazzy-rmw-zenoh-cpp` でインストールし、別ターミナルで Zenoh ルーター（`ros2 run rmw_zenoh_cpp rmw_zenohd`）を起動した上で、Isaac Sim と各 ROS 2 ターミナルに `export RMW_IMPLEMENTATION=rmw_zenoh_cpp` を設定します。

## Windows でのセットアップ

Windows には 2 つの方式があります。**新規セットアップには Pixi 方式を推奨**します。

| 方式 | ROS 2 | 特徴 |
|---|---|---|
| **Pixi（正式サポート）** | Jazzy | WSL2 不要のネイティブ ROS 2。全チュートリアル対応。ミドルウェアは Zenoh |
| WSL2（非推奨） | Humble / Jazzy | ROS 2 を WSL2 内で実行し、DDS のポートフォワーディングで通信。カスタム ROS インターフェース非対応 |

### 方式 1：Pixi ワークスペース（推奨）

Pixi ワークスペースは、RoboStack の conda パッケージ経由で ROS 2 Jazzy を Windows にネイティブインストールします。ROS 2 本体・MSVC 互換コンパイラ・colcon・CMake などの依存関係はすべて Pixi がプロジェクトローカルの環境として管理するため、システム全体への ROS インストールは不要です。ミドルウェアには **Zenoh**（`rmw_zenoh_cpp`）が既定で使われ、WSL2 やポートフォワーディングは必要ありません。

**前提条件：**

- Windows 11 x64
- [pixi](https://pixi.sh/)：`winget install prefix-dev.pixi`
- Git for Windows
- MSVC Build Tools 2022（「C++ によるデスクトップ開発」ワークロードを選択）
- Isaac Sim 6.0（スタンドアロン版を `C:\isaacsim` に配置。別の場所に置いた場合は `pixi.toml` の `[target.win.activation]` にある `isaac_sim_package_path` を変更）

**セットアップ：**

```bat
git clone https://github.com/isaac-sim/IsaacSim-ros_workspaces.git C:\IsaacSim-ros_workspaces
cd C:\IsaacSim-ros_workspaces\jazzy_ws

REM ROS 2 Jazzy と依存関係のインストール（初回は数分かかる）
pixi install

REM MSVC でワークスペースをビルド（colcon build --merge-install が実行される）
pixi run build
```

!!! warning "ワークスペースのパスは短く"
    Windows の 260 文字パス制限を超えると Pixi のビルドや起動が失敗することがあります。ワークスペースのルートは `C:\IsaacSim-ros_workspaces` のような短いパスにしてください。

**実行（それぞれ別のコマンドプロンプトで順に起動）：**

```bat
REM ターミナル 1：Zenoh ルーター（ROS 2 ノードより先に起動しておく）
cd C:\IsaacSim-ros_workspaces\jazzy_ws
pixi run zenoh

REM ターミナル 2：Isaac Sim（ROS 2 ブリッジ有効で起動される）
cd C:\IsaacSim-ros_workspaces\jazzy_ws
pixi run sim

REM ターミナル 3：ROS 2 コマンド
cd C:\IsaacSim-ros_workspaces\jazzy_ws
pixi run ros2 topic list
```

- ビルド後は `pixi shell` / `pixi run` に入るたびに `install\setup.bat` が自動で source されるため、手動の source は不要です。
- スタンドアロン Python スクリプトは、`python.bat` ではなく **Pixi の Python 環境**で実行します：`pixi run python <path\to\script.py>`
- `package.xml` に依存を追加したときは `pixi ros init --distro jazzy` で `pixi.toml` を再生成してから `pixi install` します。

### 方式 2：WSL2（非推奨）

従来方式です。**Isaac Sim 本体は Windows 側で動かし**（ROS 2 ブリッジは内部 ROS 2 ライブラリを使用）、**ROS 2 のノード群（teleop、Nav2、RViz2 など）は WSL2 内で動かして**、両者を DDS（ネットワーク）経由で通信させます。

#### 1. WSL2 と Ubuntu のインストール

管理者権限の PowerShell で（Jazzy を使う場合は `Ubuntu-24.04` に読み替え）：

```powershell
wsl --set-default-version 2
wsl --install -d Ubuntu-22.04
```

インストール完了後にマシンを再起動し、スタートメニューから Ubuntu アプリを開きます（初回はセットアップに数分かかります）。

!!! note "仮想化のエラーが出る場合"
    仮想化の有効化に関するエラーが出る場合は、[Microsoft の仮想化有効化手順](https://support.microsoft.com/en-us/windows/enable-virtualization-on-windows-11-pcs-c5578302-6e43-4b4b-a449-8ced115f58e1)（BIOS/UEFI での設定を含む）に従ってください。

#### 2. WSL2 内に ROS 2 をインストール

WSL2 のターミナルで、上の「Linux でのセットアップ」の手順を実行します（Ubuntu 22.04 なら Humble、Ubuntu 24.04 なら Jazzy）。ワークスペースのセットアップ（IsaacSim-ros_workspaces のビルド）も WSL2 内で行います。

#### 3. Windows ⇔ WSL2 間の通信設定（ポートフォワーディング）

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

#### 4. Windows 側で Isaac Sim を起動

Windows では ROS ブリッジが既定で無効なため、起動オプションで有効化します。GUI の起動だけなら内部ライブラリ（既定は Humble）が自動ロードされるので、次のコマンドで十分です：

```bat
set isaac_sim_package_path=C:\isaacsim
REM ROS 2 ブリッジを有効にして Isaac Sim を起動
%isaac_sim_package_path%\isaac-sim.bat --/isaac/startup/ros_bridge_extension=isaacsim.ros2.bridge
```

内部ライブラリを Jazzy に切り替える場合や、`python.bat` でスタンドアロンスクリプトを実行する場合は、環境変数を明示的に設定します：

```bat
set isaac_sim_package_path=C:\isaacsim
set ROS_DISTRO=jazzy
set RMW_IMPLEMENTATION=rmw_fastrtps_cpp
REM 注意：1 つのターミナルで 1 回だけ実行すること
set PATH=%PATH%;%isaac_sim_package_path%\exts\isaacsim.ros2.core\jazzy\lib

REM ROS 2 ブリッジを有効にして Isaac Sim を起動
%isaac_sim_package_path%\isaac-sim.bat --/isaac/startup/ros_bridge_extension=isaacsim.ros2.bridge
REM または、スタンドアロンスクリプトの実行
%isaac_sim_package_path%\python.bat <path\to\standalone\script>
```

これで、Isaac Sim（Windows 側）と WSL2 内の ROS 2 ノードが通信できるようになります。

#### Windows（WSL2）方式の制限事項

公式ドキュメントに明記されている制限です：

- **カスタムパッケージ／カスタムメッセージ**（カスタム ROS インターフェース）は WSL 方式では非対応です。必要な場合は Pixi 方式を使ってください。
- **Docker ワークフロー**（ROS を Docker コンテナで動かす方式）は Windows（WSL2）では非対応です。
- **Cyclone DDS** は Windows（WSL2）では非対応です（FastDDS を使用してください）。Pixi 方式は Zenoh を使用するため、FastDDS / Cyclone DDS の設定は不要（非適用）です。

!!! note "GUI ツール（RViz2 など）について（本サイト補足）"
    最近の WSL2 は **WSLg** により Linux GUI アプリをそのまま表示できるため、RViz2 や rqt などの GUI ツールも WSL2 内から起動して使えます。特別な X サーバーのインストールは通常不要です。

## rclpy・カスタムパッケージを Isaac Sim 内で使う場合

Script Editor やスタンドアロン Python から `rclpy` を使う、またはカスタムメッセージを Isaac Sim 側でも認識させる場合、ワークスペースは **Python 3.12** でビルドされている必要があります。

- **Ubuntu 24.04 + Jazzy**：Jazzy の標準 Python が 3.12 なので、上記の手順どおり普通にビルドしたワークスペースをそのまま使えます（追加手順は不要です）。
- **Ubuntu 22.04（Humble / Jazzy）**：標準 Python（3.10）とズレるため、[IsaacSim-ros_workspaces](https://github.com/isaac-sim/IsaacSim-ros_workspaces) 同梱の Dockerfile で Python 3.12 版のワークスペースをビルドします：

    ```bash
    cd IsaacSim-ros_workspaces
    ./build_ros.sh -d humble -v 22.04   # Jazzy の場合は -d jazzy
    ```

    ビルド後、新しいターミナルで Python 3.12 版のビルドを source してから Isaac Sim を起動します：

    ```bash
    source build_ws/humble/humble_ws/install/local_setup.bash
    source build_ws/humble/isaac_sim_ros_ws/install/local_setup.bash
    # このターミナルから Isaac Sim を起動する
    ```

- **Windows（Pixi）**：Pixi 方式ではカスタム ROS インターフェースがサポートされます。WSL 方式では非対応です。

## 動作確認

セットアップの確認には、[チュートリアル 2: ROS 2 メッセージで TurtleBot を駆動する](02_drive_turtlebot.md)の「ROS 接続を確認する」の手順が使えます。より簡単には：

1. Isaac Sim 側で ROS 2 ブリッジが有効なことを確認（**Window > Extensions** で `isaacsim.ros2.bridge` が有効）
2. **Tools > Robotics > ROS 2 OmniGraphs > Clock** で Clock グラフを作成し、**Play** を押す
3. 外部ノード側のターミナル（Linux ならローカル、Windows なら Pixi の `pixi run ros2` または WSL2）で：

    ```bash
    ros2 topic list
    ```

    `/clock` が表示され、`ros2 topic echo /clock` でタイムスタンプが流れてくれば接続できています。

## まとめ

| 項目 | Linux（Ubuntu 24.04） | Windows（Pixi） | Windows（WSL2・非推奨） |
|---|---|---|---|
| ROS 2 の場所 | ローカル（apt、Jazzy） | ローカル（Pixi / RoboStack、Jazzy） | **WSL2 内**の Ubuntu |
| Isaac Sim 側のブリッジ | ネイティブ ROS 2 を source して起動 | `pixi run sim`（Zenoh） | 内部 ROS 2 ライブラリ（起動オプション指定） |
| 追加のネットワーク設定 | 不要（同一マシンなら共有メモリ） | 不要（Zenoh ルーターを起動） | ポートフォワーディング（または ミラーモード） |
| カスタムパッケージを Isaac Sim 内で使用 | 可（Python 3.12 ビルド。24.04 なら通常ビルドで可） | 可 | 不可（WSL2 側でのみ使用可） |
| Docker ワークフロー | 可 | 不要（Pixi が依存を管理） | 不可 |

## 次のステップ

- [チュートリアル 1: URDF インポート: Turtlebot](01_urdf_import_turtlebot.md)からシリーズを始めましょう。
