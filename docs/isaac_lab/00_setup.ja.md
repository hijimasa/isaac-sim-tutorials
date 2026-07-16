---
title: Isaac Lab セットアップ
---

# Isaac Lab セットアップ（Linux / Windows）

## このページについて

Isaac Lab チュートリアルシリーズに関連する**セットアップ手順**をまとめたページです。[Isaac Lab 公式ドキュメントのインストールガイド](https://isaac-sim.github.io/IsaacLab/main/source/setup/installation/index.html)のうち、推奨されている pip インストール方式を Linux / Windows の違いがわかる形で整理しています。

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

公式には 4 つの方式がありますが、初めての場合は **1. の pip 方式が推奨**です：

| 方式 | 内容 | 向いている人 |
|---|---|---|
| **pip ＋ ソース（推奨）** | Isaac Sim を pip でインストールし、Isaac Lab を GitHub から取得 | ほとんどのユーザー |
| バイナリ ＋ ソース | Isaac Sim を公式バイナリで、Isaac Lab をソースで | 既にバイナリ版 Isaac Sim を使っている人 |
| フルソースビルド | 両方をソースからビルド | Isaac Sim 自体も改造する開発者 |
| pip のみ | 両方を pip パッケージで | 外部エクステンション利用のみ（学習サンプルは使えない） |

## pip インストール手順（推奨）

### 1. Python 3.11 の仮想環境を作成

**conda を使う場合（推奨・Linux / Windows 共通）：**

```bash
conda create -n env_isaaclab python=3.11
conda activate env_isaaclab
```

**venv を使う場合（Linux）：**

```bash
python3.11 -m venv env_isaaclab
source env_isaaclab/bin/activate
```

**venv を使う場合（Windows）：**

```bat
python3.11 -m venv env_isaaclab
env_isaaclab\Scripts\activate
```

### 2. Isaac Sim と PyTorch をインストール

Linux / Windows 共通：

```bash
pip install "isaacsim[all,extscache]==5.1.0" --extra-index-url https://pypi.nvidia.com
pip install -U torch==2.7.0 torchvision==0.22.0 --index-url https://download.pytorch.org/whl/cu128
```

!!! note "pip 版 Isaac Sim について"
    この方式では Isaac Sim 本体も pip パッケージとしてインストールされます。既にバイナリ版（Omniverse Launcher やスタンドアロン zip）の Isaac Sim を使っている場合は、公式の「Binary + Source」方式の手順を参照してください（Isaac Lab 側から既存の Isaac Sim を参照するようシンボリックリンク等を設定します）。

### 3. Isaac Lab リポジトリの取得とインストール

Linux / Windows 共通：

```bash
git clone https://github.com/isaac-sim/IsaacLab.git --branch main
cd IsaacLab
```

**Linux：**

```bash
./isaaclab.sh --install
```

**Windows：**

```bat
isaaclab.bat --install
```

### 4. 動作確認

空のシーンを起動できればインストールは成功です。初回起動はアセットのダウンロード等で時間がかかります。

**Linux：**

```bash
./isaaclab.sh -p scripts/tutorials/00_sim/create_empty.py
```

**Windows：**

```bat
isaaclab.bat -p scripts\tutorials\00_sim\create_empty.py
```

## 学習の実行例

インストールできたら、[チュートリアル 1: ポリシーのデプロイ](01_policy_deployment.md)で使う H1 平地歩行ポリシーの学習を実行できます：

**Linux：**

```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task Isaac-Velocity-Flat-H1-v0 --headless
```

**Windows：**

```bat
isaaclab.bat -p scripts\reinforcement_learning\rsl_rl\train.py --task Isaac-Velocity-Flat-H1-v0 --headless
```

!!! tip "トラブルシューティング"
    インストールや起動で問題が起きた場合は、[Isaac Lab 公式のトラブルシューティング](https://isaac-sim.github.io/IsaacLab/main/source/refs/troubleshooting.html)を参照してください。

## 次のステップ

- [チュートリアル 1: ポリシーのデプロイ](01_policy_deployment.md) - 学習済みポリシーを Isaac Sim で動かします。
