---
title: Cloner 入門
---

# Cloner 入門

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- **Cloner** クラスを使った環境の複製
- **GridCloner** クラスによるグリッド状の自動配置
- 複製したオブジェクトへの**ベクトル化 API**（`XformPrim`）でのアクセス
- **Physics Replication**（物理レプリケーション）と `copy_from_source` などの応用パラメータ

## はじめに

### 前提条件

- Isaac Sim の基本操作と Script Editor の使い方に慣れていること
- [Core API チュートリアル](../core_api/index.md)程度の Python スクリプティングの知識

### 所要時間

約 10〜15 分

### 概要

強化学習では、同じタスクを実行する**環境のコピーを大量に並べて**同時にデータ（軌跡）を収集するのが一般的です。**Cloner** インターフェースは、この「環境を必要な数だけ複製する」作業を簡単にするための API です。複製そのものに加えて、複製先パスの生成、配置座標の自動計算、クローン同士の衝突除外といったユーティリティも提供します。

このチュートリアルでは以下の流れで進めます：

1. **Cloner の基本** — キューブを 4 つに複製する
2. **GridCloner** — グリッド状に自動配置する
3. **複製したオブジェクトへのアクセス** — ベクトル化された API でまとめて操作する
4. **応用** — Physics Replication と `copy_from_source`

## ステップ 1：準備

1. **Window > Extensions** でエクステンションウィンドウを開き、**Isaac Sim Cloner**（`isaacsim.core.cloner`）を検索して、名前の右側のトグルスイッチで有効化します。
2. **Window > Script Editor** で Script Editor を開きます。以降のサンプルコードはすべて Script Editor に貼り付けて **Run** で実行できます。

!!! warning "エクステンションの有効化を忘れずに"
    以降のスニペットを実行する前に、`isaacsim.core.cloner` が有効になっていることを確認してください。有効でないと `from isaacsim.core.cloner import Cloner` の時点で ImportError になります。

## ステップ 2：Cloner の基本

まずはシンプルな例として、キューブを 4 つ持つシーンを作ります：

```python
from isaacsim.core.cloner import Cloner    # Cloner インターフェースをインポート
from isaacsim.core.experimental.utils.stage import get_current_stage
from pxr import UsdGeom

# キューブ 1 個のベース環境を作成
base_env_path = "/World/Cube_0"
UsdGeom.Cube.Define(get_current_stage(), base_env_path)

# Cloner のインスタンスを作成
cloner = Cloner()

# "/World/Cube" で始まるパスを 4 つ生成する（末尾に _{index} が付く）
target_paths = cloner.generate_paths("/World/Cube", 4)

# 生成したパスにキューブを複製
cloner.clone(source_prim_path="/World/Cube_0", prim_paths=target_paths)
```

これでステージに `/World/Cube_0`、`/World/Cube_1`、`/World/Cube_2`、`/World/Cube_3` の 4 つのキューブができました。ただし、このままでは**全部同じ位置に重なって**作成されています。

各キューブに位置を指定するには、最後の行を次のように置き換えます：

```python
import numpy as np

cube_positions = np.array([[0, 0, 0], [3, 0, 0], [6, 0, 0], [9, 0, 0]])

# 指定した位置に複製
cloner.clone(source_prim_path="/World/Cube_0", prim_paths=target_paths, positions=cube_positions)
```

各クローンの向きを指定したい場合は、同様に `orientations` 引数（こちらも `np.ndarray`）を渡します。

## ステップ 3：GridCloner でグリッド配置する

**GridCloner** は Cloner の特化版で、位置や向きを事前に計算しなくても、クローンを自動的に**グリッド状**に配置してくれます。初期化時にクローン同士の間隔（`spacing`）を指定します：

```python
from isaacsim.core.cloner import GridCloner    # GridCloner インターフェースをインポート
from isaacsim.core.experimental.utils.stage import get_current_stage
from pxr import UsdGeom

# キューブ 1 個のベース環境を作成
base_env_path = "/World/Cube_0"
UsdGeom.Cube.Define(get_current_stage(), base_env_path)

# 間隔 3 の GridCloner を作成
cloner = GridCloner(spacing=3)

# "/World/Cube" で始まるパスを 4 つ生成
target_paths = cloner.generate_paths("/World/Cube", 4)

# 複製（配置は自動計算される）
cloner.clone(source_prim_path="/World/Cube_0", prim_paths=target_paths)
```

これで 4 つのキューブがグリッド状に配置されたシーンができます。強化学習の並列環境（`env_0`, `env_1`, …）の配置はこの仕組みで行われています。

## ステップ 4：複製したオブジェクトにアクセスする

複製したオブジェクトの状態は、`isaacsim.core.experimental.prims` の**ベクトル化された API** でまとめて読み書きできます。ループで 1 個ずつ処理する代わりに、全オブジェクト（または一部）のデータをテンソルとして一括で取得・適用できるため、環境数が多くても効率的です。

以下は、シーン内の全キューブのワールド座標を取得し、まとめて 1.5 単位持ち上げる例です：

```python
# Xform プリム用のベクトル化 API をインポート
import numpy as np
from isaacsim.core.experimental.prims import XformPrim

# 正規表現で 4 つのキューブ全部にマッチするラッパーを作成
boxes = XformPrim("/World/Cube_.*")

# 全キューブのワールド座標を取得
#   - positions は shape (4, 3)：X, Y, Z の並進
#   - orientations は shape (4, 4)：W, X, Y, Z のクォータニオン
positions, orientations = boxes.get_world_poses()
positions = positions.numpy()
orientations = orientations.numpy()

# Z 座標を 1.5 増やして持ち上げる
positions[:, 2] += 1.5
# 新しい位置を適用
boxes.set_world_poses(positions, orientations)
```

!!! note "旧 API（XFormPrimView）からの変更点"
    Isaac Sim 5.x のチュートリアルでは `isaacsim.core.prims` の `XFormPrimView` を使い、パスを**ワイルドカード**（`/World/Cube_*`）で指定していました。6.0 の `isaacsim.core.experimental.prims.XformPrim` では、パスは**正規表現**（`/World/Cube_.*`）で指定します。また、`get_world_poses()` の戻り値は Warp 配列なので、NumPy で加工する場合は `.numpy()` で変換してから操作します。

## ステップ 5：Physics Replication（物理レプリケーション）

クローン作成時に `replicate_physics=True` を渡すと、USD の物理プロパティをコピーする代わりに **PhysX 内部で直接物理を複製**するため、物理の解析（パース）が高速になります。環境数が数千になる強化学習では特に効果的です。

この機能を使うには、追加のパラメータも指定する必要があります：

- `base_env_path` — すべてのクローンの共通祖先となるプリムのパス
- `root_path` — 各クローンのパスの、インデックス直前までのプレフィックス

```python
cloner.clone(
    source_prim_path="/World/Ants/Ant_0",
    prim_paths=target_paths,
    positions=position_offsets,
    replicate_physics=True,
    base_env_path="/World/Ants",
    root_path="/World/Ants/Ant_",
)
```

!!! note "指定を省略できる場合"
    `define_base_env()` と `generate_paths()` を先に呼んでいる場合は、Cloner が既に必要な情報を持っているため、`base_env_path` と `root_path` の指定は省略できます。なお、この機能を使う場合、すべてのクローンのパスは「プレフィックス＋連番インデックス」の形式である必要があります。

    完全なサンプルは `standalone_examples/api/isaacsim.core.cloner/cloner_ants.py` にあります。

!!! warning "Physics Replication の制限"
    Physics Replication で作成したプリムでは、**実行時に形状プロパティを変更できません**。マテリアル、摩擦係数、反発係数などを実行時にランダマイズ・変更したいシーンでは、`replicate_physics` を有効にしないでください。

## ステップ 6：copy_from_source

Cloner にはもう 1 つ重要なオプション、`copy_from_source` があります：

```python
cloner.clone(
    source_prim_path="/World/Ants/Ant_0",
    prim_paths=target_paths,
    positions=position_offsets,
    replicate_physics=True,
    base_env_path="/World/Ants",
    root_path="/World/Ants/Ant_",
    copy_from_source=True,
)
```

| 設定 | クローンの実体 | 特徴 |
|---|---|---|
| `copy_from_source=False`（既定） | ソースプリムの [USD Inherits](https://openusd.org/release/api/class_usd_inherits.html)（継承） | 複製が**高速**。ただし複製後にソースプリムへ加えた変更が**全クローンに反映される** |
| `copy_from_source=True` | ソースプリムの独立したコピー | 各クローンが独立した実体になり、ソースの変更は反映されない。環境ごとに異なるカスタマイズをしたい場合に有効 |

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. **Cloner** による環境の複製と位置指定
2. **GridCloner** によるグリッド自動配置
3. **XformPrim**（`isaacsim.core.experimental.prims`）によるクローンへのベクトル化アクセス
4. **Physics Replication** による高速化とその制限
5. **copy_from_source** による継承／独立コピーの使い分け

## 次のステップ

- [チュートリアル 3: Instanceable Assets](03_instanceable_assets.md) - 大量に複製した環境のメモリ消費を抑える、インスタンス化可能なアセットの作り方を学びます。
