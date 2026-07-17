---
title: Lula Robot Description と XRDF エディタ
---

# Lula Robot Description と XRDF エディタ

!!! warning "Isaac Sim 6.0 で非推奨（Deprecated）"
    公式ドキュメントでは、このページは Isaac Sim 6.0 で **Deprecated** とマークされました。新規開発には後継の **Robot Motion (Experimental)** API の利用が推奨されています。Robot Description Editor と Lula は 6.0 でも引き続き動作します。

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- ロボット記述ファイル（robot_description.yaml）が Lula アルゴリズムに必要な理由
- アクティブ関節・固定関節による C 空間の定義
- 衝突球（collision spheres）の役割と追加方法
- Robot Description Editor で設定ファイル（Lula 用 / cuMotion 用 XRDF）を生成・編集する方法

## はじめに

### 前提条件

- [モーション生成の概要](01_overview.md) を理解していること
- URDF と Articulation の基礎を理解していること

### 所要時間

約 20〜30 分

### 概要

**Robot Description Editor** は、ロボットの URDF を補完する設定ファイルを生成する UI ツールです。次の 2 つのモーション生成パッケージがこのファイルを利用します。

- **cuMotion**（XRDF ファイル）
- **Lula**（robot_description.yaml ファイル）

!!! tip "参照でアセットを開く"
    Robot Description Editor は、Articulation がすでにステージ上にある状態で使います。チュートリアルに沿って進めるには、USD ファイルを直接開くのではなく、空のステージに**ドラッグ＆ドロップして参照として開く**のがおすすめです。

## ロボット記述ファイルの中身

ロボット記述ファイルは、Lula アルゴリズムを使うために URDF と共に必要となる主要な設定ファイルです。新しいロボットで Lula を使う際、`robot_description.yaml` の作成が最初かつ最も時間のかかるステップになります。

### C 空間の定義：アクティブ関節と固定関節

ロボット記述ファイルの重要な役割は、ロボットの **C 空間** を定義することです。たとえば、2 自由度グリッパを備えた 7 自由度の Franka アームでは、URDF には計 9 個の非固定関節があります。しかし Lula アルゴリズム（RMPflow・Lula RRT・Lula Trajectory Generator）は、アーム本体を動かしてエンドエフェクタを位置決めするためのもので、グリッパ（把持機構）の開閉制御は行いません。典型的には、RMPflow でエンドエフェクタをブロックの上へ移動させ、グリッパの開閉は別途行います。

各関節は次のいずれかに区別します。

- **Active Joint（アクティブ関節）** … Lula に直接制御される
- **Fixed Joint（固定関節）** … Lula から見て固定とみなされる

Franka で RMPflow を使う場合、アームの 7 関節をアクティブ、グリッパの関節を固定とします。

!!! note "固定関節の位置は「デフォルト構成」になる"
    固定関節の位置は「デフォルト位置」として扱われます。RMPflow はターゲットが与えられないときデフォルト位置へ動き、ターゲットが与えられたときはヌル空間（エンドエフェクタの位置・姿勢を変えずに関節だけを動かせる冗長自由度）の挙動を解決するのにデフォルト位置を使います（7 自由度ロボットは 1 つのターゲットへ多様な姿勢で到達できるため、デフォルトに近い C 空間位置へバイアスされます）。固定関節の位置は実行時に上書きできないため、妥当な値を選ぶことが重要です。Franka の例では、グリッパを**開いた**状態に対応する値を与えます（閉じた指は開いた指の凸包の内側に入るため、状態を問わず衝突回避に有利）。

### 衝突球（Collision Spheres）

Lula アルゴリズムは、効率的な衝突回避のためにカスタム設定を使います。ロボットごとに、その表面をおおまかに覆う**衝突球の集合**を定義する必要があります。Lula は、記述ファイルで定義された衝突球が USD ワールド内の障害物と交差しないように動作します。Robot Description Editor は、任意のロボットに対して衝突球の完全な集合を素早く定義するツールを提供します。

### ロボット記述ファイルと XRDF ファイルの違い

**XRDF ファイル**は cuMotion が特定ロボットに要求する主要な設定ファイルで、Lula ロボット記述ファイルのデータの**上位集合**を含みます。Robot Description Editor は、cuMotion を使い始めるのに必要な最小限のデータを含む XRDF ファイルも生成できます。cuMotion 用と Lula 用でエディタの使い方は変わりません。

!!! note
    将来的に Lula は XRDF ファイルを完全サポートし、ロボット記述ファイルは非推奨になる予定です。Isaac Sim 4.0.0 で Robot Description Editor は XRDF をサポートするよう変更されました。

## 各 Lula アルゴリズムに必要な情報

アルゴリズムによって、必要となる記述ファイルの完成度が異なります。すべてのアルゴリズムでアクティブ・固定関節の選択は必須ですが、**衝突球は外部障害物との衝突回避を行うアルゴリズムでのみ必要**です。

- **Lula Kinematics Solver** … 純粋に運動学的で外界と相互作用しないため、衝突球は省略できます。
- **RMPflow** … 衝突球なしでも動作しますが、障害物を回避できません。

## Robot Description Editor を使う

!!! note "Instanceable Assets との互換性"
    Robot Description Editor は Instanceable Assets と互換性がありません。ただし、後で instanceable に変換したアセット用に生成した記述ファイルは、その instanceable アセットでも動作します。

Robot Description Editor を使うには、ロボット階層内のすべてのジオメトリ prim で **Instanceable** チェックボックスがオフになっていることを確認してください。この設定は、ジオメトリ prim を選択したときの Property パネルにあります。

![Instanceable チェックボックスをオフにする](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_6.0_full_tut_gui_lula_description_editor_instanceable_disable.png)

### 開始する

エディタは **Tools > Robotics > Lula Robot Description Editor** にあります。ロボットの USD を開き、左側の **Play** ボタンを押します。**Selection Panel** の **Select Articulation** でロボットの Articulation の prim パスを選択すると、**Select Link** ドロップダウンに各リンク名が表示されます。

![Robot Description Editor](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_4.5_full_tut_gui_lula_description_editor.png)

### 関節プロパティを設定する（Set Joint Properties）

Articulation を選択すると **Set Joint Properties** が展開されます。各関節に **Joint Position** と **Joint Status** を設定します。

- 直接制御したい関節のみを **Active Joint** にします（通常はアームの各関節をアクティブ、アームに付いたマニピュレータの関節を固定にします）。**最低 1 つ**はアクティブ関節にする必要があります。
- 固定関節の位置は Lula に真に固定とみなされ、実行時に上書きできません。
- 固定関節の位置はロボットの**デフォルト構成**とみなされ、主に RMPflow で使われます。デフォルト構成は、ロボットの前方（Isaac Sim の慣例では +X 軸方向）で、関節リミットに近くない姿勢を選びます。

!!! note "Isaac Sim 4.0.0 での変更"
    Isaac Sim 4.0.0 で Command Panel は Set Joint Properties に名称変更され、各関節にジャーク・加速度リミットのフィールドが追加されました。

### 衝突球を追加する

衝突球はリンクごとに追加します。**Select Link** で対象リンクを選び、**Link Sphere Editor** パネルで球の追加・スケール・クリアを行います。**Editor Tools** パネルには Undo/Redo、球の色変更、ロボット表示の切り替えがあります。球はリンク prim の下にネストされ、ステージ上で移動・半径変更できます。リンク原点に対する相対位置が記述ファイルに固定値として書き込まれます。

球を追加する主な方法は 3 つあります。

- **Add Sphere** … リンク原点から指定の相対位置に単一の球を追加します。
- **Connect Spheres** … 既存の 2 つの球を選び、指定した本数の球でつなぎます。位置とサイズは 2 球が定義する円錐台の体積を最もよく埋めるよう補間されます。
- **Generate Spheres** … リンクの体積を定義するメッシュを選び、その体積を最もよく埋める N 個の球を自動生成します。数を指定するとプレビューが表示され、**Generate Spheres** ボタンで確定します。

![衝突球の編集](https://docs.isaacsim.omniverse.nvidia.com/latest/_images/isim_4.5_full_tut_gui_lula_description_editor_spheres.png)

!!! tip "自動生成の注意"
    単純な円筒形状のリンクは、手動で **Connect Spheres** した方がよいことが多いです。自動生成は水密（water-tight）な三角形メッシュでのみ動作し、すべてのメッシュで機能する保証はありません。うまくいかない場合は手動で球を追加・接続してください。

### 設定ファイルをエクスポートする

**Lula ロボット記述ファイル**

Set Joint Properties と衝突球を作成したら、**Export To File > Export to Lula Robot Description File** でエクスポートします。ファイル名は `.yaml` で終わる必要があります。有効なパスを入力すると Save ボタンが有効になります。

**XRDF ファイル**

**Export to File > Export to cuMotion XRDF** で XRDF を生成します。パスは `.yaml` または `.xrdf` で終わる必要があります。バージョンのドロップダウンで XRDF フォーマットの **バージョン 1.0 または 2.0** を選択できます（1.0 は `collision`、2.0 は `world_collision` を使います）。XRDF エクスポート時のエディタの挙動は次のとおりです。

- 衝突グループ（1.0 では `collision`、2.0 では `world_collision`）と自己衝突（`self_collision`）の両方に使う単一の衝突グループを、エディタで作成した球から作成する
- self_collision で、各リンクが親リンクと同じ親を持つリンクを無視するよう設定する
- Tool Frames / Modifiers は書き込まない

既存の XRDF ファイルとデータをマージすることもできます（**Merge With Existing XRDF**）。マージ時は既存ファイルの Tool Frames・Modifiers・条件付きの self_collision（`self_collision > geometry` が衝突グループの geometry と一致する場合）・エディタで表現されなかったフレームの衝突球をコピーします。

### 設定ファイルをインポートする

**Import From File > Import Lula Robot Description File** で既存の記述ファイルを、**Import XRDF File** で既存の XRDF をインポートできます。XRDF インポートはフォーマットバージョン 1.0・2.0 の両方に対応し（1.0 は `collision`、2.0 は `world_collision`）、衝突グループの球のみが読み込まれます（Modifiers / Tool Frames / self_collision グループは使われません）。いずれもインポートするとエディタ内の情報はすべて上書きされます。

## まとめ

このチュートリアルでは、次の内容を学びました。

- ロボット記述ファイルが Lula アルゴリズムの主要設定であり、C 空間（アクティブ／固定関節）と衝突球を定義すること
- 衝突球は衝突回避を行うアルゴリズムでのみ必要なこと
- Robot Description Editor で Lula 用 YAML / cuMotion 用 XRDF を生成・マージ・インポートする方法

## 次のステップ

- [Lula RMPflow](03_rmpflow.md) で、生成した記述ファイルを使った反応型モーションを学びます。
- [新しいマニピュレータ用の RMPflow 設定](07_configure_rmpflow_denso.md) も参照してください。
