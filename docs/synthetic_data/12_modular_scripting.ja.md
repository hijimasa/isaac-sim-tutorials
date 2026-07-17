---
title: モジュラービヘイビアスクリプティング
---

# モジュラービヘイビアスクリプティング

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- `isaacsim.replicator.behavior` エクステンションの**ビヘイビアスクリプト**の仕組み（プリムに添付する部品化されたランダマイザ）
- 6 つの組み込みビヘイビアの使い方と設定パラメータ
- **USD 属性として公開された変数**による、コードを書かない挙動カスタマイズ
- **タイムラインベース／カスタムイベントベース**の実行制御
- テンプレートからの**カスタムビヘイビア**の作成

## はじめに

### 前提条件

- USD / Isaac Sim API の基本、Python Scripting Component、omni.replicator の基本
- [チュートリアル 3: Getting Started スクリプト](03_getting_started_scripts.md)を完了していること

### 所要時間

約 40 分

### 概要

これまでのランダム化はスクリプト内に書いてきましたが、**ビヘイビアスクリプト**（Python Scripting Component）を使うと、ランダマイザを**プリムに添付できる部品**として扱えます。スクリプトが USD 側に紐づくため：

- **再利用可能** — 一度書けば複数のプリム・プロジェクトで使い回せる
- **共有可能** — アセットに埋め込んで配布できる
- **設定可能** — 変数が USD 属性として公開され、**UI から**コード変更なしで調整できる
- **永続的** — ステージと一緒に保存・バージョン管理される

ビヘイビア機能は 2 つのエクステンションに分かれています：

- **`isaacsim.replicator.behavior`** — ビヘイビアスクリプト本体を含むコア。UI に依存せず、**ヘッドレスモード**（自動化した SDG パイプラインなど）でも動作します
- **`isaacsim.replicator.behavior.ui`** — 公開変数を Property パネルに表示する UI

ビヘイビアスクリプトの実体は `/exts/isaacsim.replicator.behavior/isaacsim/replicator/behavior/behaviors/*` にあります。既定ではタイムラインイベント（start / update / stop など）に反応するテンプレートコードを持ちます。

![ビヘイビアスクリプトの公開変数](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_4.5_replicator_tut_gui_behavior_scripts_variables.jpg)

!!! note "変数の公開の仕組み（コア／UI の分離）"
    公開変数は、USD API でプリムに共有ネームスペース付きのカスタム属性（`exposedVar:<behaviorNamespace>:<attrName>`）を作ることで実装されています。コア側が公開変数を作成・削除するたびに carb イベント `isaacsim.replicator.behavior.EXPOSED_VARS_CHANGED` を発行し、UI 側（`isaacsim.replicator.behavior.ui`）はこのイベントを購読して、選択したプリムの Property パネルを編集可能なフィールドとして自動再構築します。このイベントベースの疎結合により、コアは UI なしで動作できます。

!!! note "Property パネルからスクリプトを添付するには"
    UI からプリムにビヘイビアスクリプトを添付する（Property パネル > **Add > Python Scripting**）には、**Window > Extensions** で `omni.behavior.scripting.ui` エクステンションを有効化する必要があります（既定では無効）。コアのビヘイビア自体はこのエクステンションなしでも動作します。

## 組み込みビヘイビア一覧

### Location Randomizer（location_randomizer.py）

指定した範囲内でプリムの**位置**をランダム化します。

| 公開変数 | 型 | 意味 |
|---|---|---|
| `range:minPosition` / `range:maxPosition` | Vector3d | ランダムオフセットの下限・上限 |
| `frame:useRelativeFrame` | Bool | True なら初期オフセット（ターゲット指定時はターゲットからの、未指定時は自身の初期位置からの）を保持して、その上にランダムオフセットを加算。False ならランダムオフセットを絶対位置として適用 |
| `frame:targetPrimPath` | String | 基準プリム（指定時はそのワールド位置にアンカー。空なら他プリムから独立してランダム化） |
| `includeChildren` | Bool | 子プリムも対象にする |
| `interval` | UInt | 更新間隔（0＝毎フレーム） |

`targetPrimPath` と `useRelativeFrame` の組み合わせで最終位置が決まります（空 + True＝初期位置まわりのジッター、指定 + False＝ターゲット近傍への配置、指定 + True＝相対オフセットを保ったままターゲットに追従）。

用途：背景オブジェクトの配置バリエーション、移動するターゲットへの追従／近傍配置、グループ単位の階層ランダム化。

### Rotation Randomizer（rotation_randomizer.py）

オイラー角の範囲指定で**回転**をランダム化します。変数は `range:minRotation` / `range:maxRotation`（度、XYZ）、`includeChildren`、`interval`。X・Y・Z 軸の回転を合成して `set_rotation_with_ops` で適用します。

### Look At Behavior（look_at_behavior.py）

プリムを**ターゲットへ向け続けます**。カメラのトラッキングやセンサーの照準合わせに使います。

| 公開変数 | 意味 |
|---|---|
| `targetLocation` | 注視する固定座標 |
| `targetPrimPath` | 注視するプリム（指定時は targetLocation より優先） |
| `upAxis` | 姿勢維持のための上方向軸（例：Z-up なら (0, 0, 1)） |

### Light Randomizer（light_randomizer.py）

ライトの**色と強度**をランダム化します。変数は `range:minColor` / `range:maxColor`（Color3f）、`range:intensity`（Float2 の min/max）、`includeChildren`、`interval`。`UsdLux.LightAPI` を持つプリムを対象として検出します。用途：昼夜サイクル、ちらつき、色温度の変化。

### Texture Randomizer（texture_randomizer.py）

ビジュアルプリムに**テクスチャをランダム適用**します。テクスチャは `textures:assets`（AssetArray）または `textures:csv`（URL の CSV）で与え、`textureScaleRange`・`textureRotateRange`・`projectUvwProbability`（UV 投影を有効にする確率）でマテリアルパラメータもランダム化します。

### Volume Stack Randomizer（volume_stack_randomizer.py）

**物理シミュレーションでオブジェクトをランダムに積み上げます**。他のビヘイビアと異なり、**カスタムイベントベース**で動作します（シミュレーション開始前に物理で山を作る、という使い方のため）。

| 公開変数 | 意味 |
|---|---|
| `event:input` / `event:output` | 購読するイベント名／完了時に発行するイベント名 |
| `assets:assets` / `assets:csv` | スポーンするアセットのリスト |
| `assets:numRange` | スポーン数の範囲（min, max） |
| `dropHeight` | 落下開始の高さ |
| `renderSimulation` | シミュレーションステップを描画するか |
| `removeRigidBodyDynamics` | シミュレーション後にリジッドボディを除去するか |
| `preserveSimulationState` | 最終状態を保持するか |

イベントフローは「リセット（前回状態のクリーンアップ）→ セットアップ（アセットのスポーン）→ 実行（物理シミュレーション）→ 完了イベントの発行」で、外部スクリプトからイベントで**正確なタイミング制御・連鎖実行**ができます。

!!! note "タイムラインベースとイベントベース"
    既定のビヘイビアはタイムラインイベント（start / update / stop）で動きますが、**タイムラインから独立して**動かしたい挙動（例：シミュレーション開始前の積み上げ）は、既定のビヘイビア関数をスキップして**カスタムイベントの購読・発行**で制御します。これにより、コアのシミュレーションループから挙動を分離（モジュール化）でき、毎フレームの不要な計算も避けられます。

## テンプレートからカスタムビヘイビアを作る

自作ビヘイビアの出発点となるテンプレートが用意されています：

- `example_behavior.py` — 新規ビヘイビアのボイラープレート
- `base_behavior.py` / `example_base_behavior.py` — 基底クラス継承による構造化された開発
- `example_custom_event_behavior.py` — イベントベースビヘイビアの実装例

テンプレートは、変数の USD 属性としての公開、タイムライン統合に必要なメソッド群（`on_init` / `on_play` / `on_update` / `on_stop` / `on_destroy`）、基底クラスによる拡張の各パターンを示しています。

## 統合例：ビヘイビアベースの SDG パイプライン

公式ページ末尾には、これらを組み合わせた SDG デモスクリプト（Script Editor で実行）が掲載されています：

1. **Volume Stack Randomizer** で物理シミュレーションによるリアルな積み上げを作成
2. **Texture Randomizer** でアセットの見た目を多様化
3. **Light Randomizer** と **Look At Behavior**（カメラのターゲット追跡）を追加
4. ランダム化されたシーン構成で合成画像をキャプチャ

!!! note "seed による再現性"
    各ビヘイビアは公開変数 `seed` を持ち、デモスクリプトではビヘイビアインスタンスごとに固有のシードを割り当てることで、実行順序に依存しない決定的なランダム化を実現しています（物理シミュレーションを使う積み上げは非決定的で、最終位置は変わり得ます）。

![ビヘイビア SDG のキャプチャ](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_4.5_replicator_tut_viewport_behavior_scripts_capture.jpg)

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. **ビヘイビアスクリプト**による、プリム添付型・再利用可能なランダマイザの部品化
2. 6 つの組み込みビヘイビア（位置・回転・注視・ライト・テクスチャ・積み上げ）の設定
3. **USD 属性による変数公開**と UI からの調整
4. **タイムライン／カスタムイベント**の 2 つの実行制御と、それらを組み合わせた SDG パイプライン

## 次のステップ

- [チュートリアル 13: ランダム化スニペット集](13_isaac_randomizers.md) - コピペで使えるランダム化のコード集です。
