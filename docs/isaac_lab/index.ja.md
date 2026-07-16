---
title: Isaac Lab チュートリアル
---

# Isaac Lab チュートリアル

<span class="badge badge-intermediate">Intermediate</span>

Isaac Lab で学習したポリシーの Isaac Sim へのデプロイと、強化学習向けのシーン構築（環境の複製・メモリ最適化）を学ぶチュートリアルです。

## 概要

**Isaac Lab** は、Isaac Sim を基盤とする公式のロボット学習フレームワークです。強化学習・模倣学習などのための API とサンプルを提供し、最新のシミュレーション機能を活用しながら、モジュラーな設計でロボット学習環境を簡単かつ効率的に構築できます。

主な特徴：

- 環境を簡単に作成・変更できる、設定ファイル駆動のモジュラーシステム
- パフォーマンスを最適化できる柔軟なワークフロー
- 学習・評価用のロボット学習環境スイート
- 各種の強化学習・模倣学習ライブラリへの対応
- ゲームパッドやキーボードなどの周辺機器と接続したデモンストレーション収集
- Sim-to-Real 転移のためのカスタムアクチュエータモデルによるシミュレーション拡張

!!! note "このセクションで扱う範囲"
    Isaac Lab を使った**学習（トレーニング）そのもの**は [Isaac Lab 公式ドキュメント](https://isaac-sim.github.io/IsaacLab)の担当範囲です。このセクションでは、Isaac Sim 側の視点から「学習済みポリシーをどうデプロイするか」「強化学習向けの大規模シーンをどう効率的に作るか」を扱います。

## チュートリアル

!!! example "[Isaac Lab セットアップ（Linux / Windows）](00_setup.md)"
    Isaac Lab のインストール手順（pip 方式）を Linux / Windows の違いがわかる形で解説します。デモの実行だけなら Isaac Sim 単体で可能なため、まずはチュートリアル 1 から始めて、学習を自分で回す段階でセットアップしても構いません。

!!! example "[チュートリアル 1: ポリシーのデプロイ](01_policy_deployment.md)"
    Isaac Lab で学習したポリシーを Isaac Sim にデプロイする方法を学びます。H1 / Spot の歩行デモ、環境パラメータファイル（env.yaml）の読み方、Policy Controller クラスの構造、デバッグの定石までを解説します。

!!! example "[チュートリアル 2: Cloner 入門](02_cloner.md)"
    強化学習の並列環境構築に使う Cloner / GridCloner インターフェースを学びます。クローンへのベクトル化アクセス、Physics Replication による高速化も解説します。

!!! example "[チュートリアル 3: Instanceable Assets](03_instanceable_assets.md)"
    大量のロボットを配置してもメモリ消費を抑えられる、インスタンス化可能なアセットの作り方を学びます。インポーターのオプションと既存アセットの変換方法を解説します。

## あわせて読みたいチュートリアル

Isaac Lab に関連する Isaac Sim 側のチュートリアルです：

- ロボットの準備：[URDF インポート](../importer_exporter/01_import_urdf.md)、[MJCF インポート](../importer_exporter/03_import_mjcf.md)
- ポリシー推論用のリギング：[脚ロボットのリギング](../robot_setup/13_rig_legged_robot.md)
- Python スクリプティング：[Core API チュートリアル](../core_api/index.md)

## Isaac Lab リソース

- [Isaac Lab リポジトリ（GitHub）](https://github.com/isaac-sim/IsaacLab)
- [Isaac Lab 公式ドキュメント](https://isaac-sim.github.io/IsaacLab)

## 非推奨となった旧フレームワーク

Isaac Lab は、これまでに公開されてきたロボット学習・強化学習フレームワークを置き換えるものです。以下のフレームワークは**非推奨**となっており、Isaac Lab への移行が推奨されています：

| 旧フレームワーク | 移行ガイド |
|---|---|
| [IsaacGymEnvs](https://github.com/isaac-sim/IsaacGymEnvs)（Isaac Gym Preview Release 用） | [Migrating from IsaacGymEnvs](https://isaac-sim.github.io/IsaacLab/main/source/migration/migrating_from_isaacgymenvs.html) |
| [OmniIsaacGymEnvs](https://github.com/isaac-sim/OmniIsaacGymEnvs)（Isaac Sim 用） | [Migrating from OmniIsaacGymEnvs](https://isaac-sim.github.io/IsaacLab/main/source/migration/migrating_from_omniisaacgymenvs.html) |
| [Orbit](https://isaac-orbit.github.io)（Isaac Sim 用） | [Migrating from Orbit](https://isaac-sim.github.io/IsaacLab/main/source/migration/migrating_from_orbit.html) |
