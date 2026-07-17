---
title: Isaac Lab セットアップ
---

# Isaac Lab セットアップ（Linux / Windows）

## このページについて

Isaac Lab チュートリアルシリーズに関連する**セットアップ手順**をまとめたページです。[Isaac Lab 公式ドキュメントのインストールガイド](https://isaac-sim.github.io/IsaacLab/main/source/setup/installation/index.html)のうち、新規セットアップ向けに推奨されている **pip 方式**と、既にバイナリ版 Isaac Sim を使っている人向けの**バイナリ方式（Binary + Source）**を、Linux / Windows の違いがわかる形で整理しています。

!!! note "どこまでのセットアップが必要か"
    このサイトの Isaac Lab チュートリアルは、必要な環境がページによって異なります：

    - [チュートリアル 1: ポリシーのデプロイ](01_policy_deployment.md)の**デモ実行（ステップ 1）**、[チュートリアル 2: Cloner 入門](02_cloner.md)、[チュートリアル 3: Instanceable Assets](03_instanceable_assets.md) — **Isaac Sim 単体で完結**します。Isaac Lab のインストールは不要です。
    - [チュートリアル 1](01_policy_deployment.md) の**トレーニング／エクスポート（ステップ 2）**を自分で実行する場合 — **Isaac Lab のインストールが必要**です（本ページの手順）。

## 対応プラットフォームと要件

| 項目 | 要件 |
|---|---|
| OS | Ubuntu 22.04（Linux x64）／ Windows 11（x64） |
| Python | **3.11**（Isaac Sim 5.x に合わせる） |
| Isaac Sim | 5.1.0 推奨（4.2.0 以前はサポート終了） |
| メモリ | 32 GB 以上 |
| GPU VRAM | 16 GB 以上推奨 |

!!! note "Windows は WSL 不要（ネイティブ動作）"
    ROS 2 と異なり、**Isaac Lab は Windows 11 でネイティブに動作**します。Linux との違いは、スクリプトが `isaaclab.sh` ではなく `isaaclab.bat` になること、パス区切りがバックスラッシュ（`\`）になることくらいです。

    ただし、学習したポリシーを **ROS 2 経由でデプロイ**する段階（[ROS 2 チュートリアル](../ros/index.md)）に進む場合は、Windows では WSL2 上の ROS 2 が必要になります。[ROS 2 セットアップ](../ros/00_setup.md)を参照してください。

## インストール方式の選択

公式には 4 つの方式があります。このページでは上 2 つ（pip 方式・バイナリ方式）の手順をタブで切り替えて説明します：

| 方式 | 内容 | 向いている人 |
|---|---|---|
| **pip ＋ ソース（推奨）** | Isaac Sim を pip でインストールし、Isaac Lab を GitHub から取得 | 初めて Isaac Lab をセットアップする人 → 本ページ「pip 方式」タブ |
| **バイナリ ＋ ソース** | Isaac Sim は既存の公式バイナリを使い、Isaac Lab をソースで | 既にバイナリ版 Isaac Sim を使っている人 → 本ページ「バイナリ方式」タブ |
| フルソースビルド | 両方をソースからビルド | Isaac Sim 自体も改造する開発者（[公式ガイド](https://isaac-sim.github.io/IsaacLab/main/source/setup/installation/index.html)参照） |
| pip のみ | 両方を pip パッケージで | 外部エクステンション利用のみ（学習サンプルは使えない） |

!!! note "どちらのタブを選ぶか"
    本サイトの他の章（[Core API](../core_api/index.md) など）を、[Isaac Sim Quick Install](https://docs.isaacsim.omniverse.nvidia.com/latest/installation/quick-install.html) でダウンロードしたスタンドアロン（zip）版 Isaac Sim で進めてきた場合は、**「バイナリ方式」タブ**の手順を使ってください。pip 方式の手順をそのまま実行すると、pip 版 Isaac Sim が別途インストールされて二重インストールになります。

## インストール手順

=== "pip 方式（推奨・新規セットアップ）"

    Isaac Sim 本体も pip パッケージとして Python 仮想環境にインストールする方式です。

    **1. Python 3.11 の仮想環境を作成**

    conda を使う場合（推奨・Linux / Windows 共通）：

    ```bash
    conda create -n env_isaaclab python=3.11
    conda activate env_isaaclab
    ```

    venv を使う場合（Linux）：

    ```bash
    python3.11 -m venv env_isaaclab
    source env_isaaclab/bin/activate
    ```

    venv を使う場合（Windows）：

    ```bat
    python3.11 -m venv env_isaaclab
    env_isaaclab\Scripts\activate
    ```

    **2. Isaac Sim と PyTorch をインストール**

    Linux / Windows 共通：

    ```bash
    pip install "isaacsim[all,extscache]==5.1.0" --extra-index-url https://pypi.nvidia.com
    pip install -U torch==2.7.0 torchvision==0.22.0 --index-url https://download.pytorch.org/whl/cu128
    ```

    **3. Isaac Lab リポジトリの取得とインストール**

    Linux / Windows 共通：

    ```bash
    git clone https://github.com/isaac-sim/IsaacLab.git --branch main
    cd IsaacLab
    ```

    Linux：

    ```bash
    ./isaaclab.sh --install
    ```

    Windows：

    ```bat
    isaaclab.bat --install
    ```

    !!! note "以降の実行はすべて仮想環境内で"
        `isaaclab.sh` / `isaaclab.bat` の実行時は、常にこの仮想環境（`conda activate env_isaaclab` など）を有効化した端末を使ってください。

=== "バイナリ方式（既存のバイナリ版 Isaac Sim を利用）"

    スタンドアロン（zip）版 Isaac Sim 5.1.0 をインストール済みの環境に、Isaac Lab をソースから追加する方式です。

    !!! note "仮想環境の作成と pip install は不要"
        バイナリ版 Isaac Sim には Python 3.11 と PyTorch が同梱されており、`isaaclab.sh` / `isaaclab.bat` はそれを自動的に使用します。pip 方式にある仮想環境の作成や `pip install isaacsim...` / `pip install torch...` の手順は**実行しないでください**（Isaac Sim の二重インストールになります）。

    **1. Isaac Lab リポジトリの取得**

    ```bash
    git clone https://github.com/isaac-sim/IsaacLab.git --branch main
    cd IsaacLab
    ```

    **2. Isaac Sim へのシンボリックリンクを作成**

    IsaacLab リポジトリの直下に、バイナリ版 Isaac Sim のインストール先を指す `_isaac_sim` という名前のリンクを作成します。これにより `isaaclab.sh` / `isaaclab.bat` が同梱の Python 環境や Isaac Sim のエクステンションを参照できるようになります。

    Linux（インストール先が `~/isaacsim` の場合）：

    ```bash
    ln -s ${HOME}/isaacsim _isaac_sim
    ```

    Windows（インストール先が `C:\isaacsim` の場合）— **管理者として実行**した PowerShell で：

    ```powershell
    New-Item -ItemType SymbolicLink -Path _isaac_sim -Target C:\isaacsim
    ```

    `New-Item` で作成できない場合は、[公式ドキュメント](https://isaac-sim.github.io/IsaacLab/main/source/setup/installation/binaries_installation.html)に記載されているコマンドプロンプト（cmd）の `mklink` でも作成できます：

    ```bat
    mklink /D _isaac_sim C:\isaacsim
    ```

    !!! warning "Windows でのシンボリックリンク作成の注意"
        - シンボリックリンクの作成には基本的に**管理者権限**が必要です。PowerShell / コマンドプロンプトを「管理者として実行」で開いてから実行してください。
        - `mklink` はコマンドプロンプト（cmd）専用の内部コマンドのため、**PowerShell で実行すると「用語 'mklink' は…認識されません」エラーになります**。必ずコマンドプロンプトで実行してください。
        - Windows の「開発者モード」を有効にしている場合、cmd の `mklink` は管理者権限なしでも実行できます（Windows PowerShell 5.1 の `New-Item` は開発者モードでも管理者権限が必要です）。

    **3. Isaac Lab のインストール**

    Linux：

    ```bash
    ./isaaclab.sh --install
    ```

    Windows：

    ```powershell
    ./isaaclab.bat --install
    ```

## 動作確認

どちらの方式でも、以降のコマンドは共通です（pip 方式の場合は仮想環境を有効化した端末で実行してください）。空のシーンを起動できればインストールは成功です。初回起動はアセットのダウンロード等で時間がかかります。

**Linux：**

```bash
./isaaclab.sh -p scripts/tutorials/00_sim/create_empty.py
```

**Windows：**

```powershell
./isaaclab.bat -p scripts\tutorials\00_sim\create_empty.py
```

## 学習の実行例

インストールできたら、[チュートリアル 1: ポリシーのデプロイ](01_policy_deployment.md)で使う H1 平地歩行ポリシーの学習を実行できます：

**Linux：**

```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task Isaac-Velocity-Flat-H1-v0 --headless
```

**Windows：**

```powershell
./isaaclab.bat -p scripts\reinforcement_learning\rsl_rl\train.py --task Isaac-Velocity-Flat-H1-v0 --headless
```

!!! warning "既知の問題（Windows）: h5py の DLL 読み込みエラーで起動に失敗する"
    Windows で起動時に `Windows fatal exception: code 0xc0000139` と、次のようなエラーが出て `isaaclab_tasks` の読み込みに失敗することがあります：

    ```
    ImportError: DLL load failed while importing _errors: 指定されたプロシージャが見つかりません。
    ```

    これは h5py 3.16.0 以降と Isaac Sim 同梱の HDF5 DLL が競合する既知の問題です（[isaac-sim/IsaacLab #5076](https://github.com/isaac-sim/IsaacLab/issues/5076)）。IsaacLab リポジトリのルートで h5py を 3.15.1 に下げると解消します：

    ```powershell
    ./isaaclab.bat -p -m pip install h5py==3.15.1
    ```

    （Linux の場合は `./isaaclab.sh -p -m pip install h5py==3.15.1`）

!!! warning "既知の問題（Windows）: tensordict の access violation で学習スクリプトがクラッシュする"
    rsl_rl の学習スクリプト起動時に、`tensordict` の import 中（トレースバックに `site-packages\tensordict\utils.py` が現れる）に `Windows fatal exception: access violation` でクラッシュすることがあります。

    これは 2026 年 4 月リリースの tensordict 0.12 系が、Isaac Sim 5.1.0 同梱の PyTorch 2.7.0 とバイナリ非互換なことが原因の既知の問題です（[isaac-sim/IsaacLab #5393](https://github.com/isaac-sim/IsaacLab/issues/5393)、[Discussion #5373](https://github.com/isaac-sim/IsaacLab/discussions/5373)）。tensordict を 0.12 より前のバージョンに下げると解消します：

    ```powershell
    ./isaaclab.bat -p -m pip install tensordict==0.11.0
    ```

    （Linux の場合は `./isaaclab.sh -p -m pip install tensordict==0.11.0`。これで解消しない場合は `tensordict==0.9.0` に下げ、さらに `./isaaclab.bat -p -m pip install --force-reinstall rsl-rl-lib` で rsl-rl-lib を入れ直してみてください。）

!!! tip "トラブルシューティング"
    インストールや起動で問題が起きた場合は、[Isaac Lab 公式のトラブルシューティング](https://isaac-sim.github.io/IsaacLab/main/source/refs/troubleshooting.html)を参照してください。

## 次のステップ

- [チュートリアル 1: ポリシーのデプロイ](01_policy_deployment.md) - 学習済みポリシーを Isaac Sim で動かします。
