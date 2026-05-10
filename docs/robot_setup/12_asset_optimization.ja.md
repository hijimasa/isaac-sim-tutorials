---
title: アセット最適化
---

# アセット最適化

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます：

- ロボットアセットを**シミュレーション向けに再構成**する手順（Reparenting とレイヤー設定）
- **Mesh Merge Tool** による不要なメッシュノードの統合
- **Scenegraph Instancing**（シーングラフインスタンシング）によるメモリ・描画コストの削減
- ライト、マテリアル、コライダーなど**パフォーマンスに影響する要素**の確認ポイント
- 最適化前後のフレームレート（FPS）比較による効果の評価

## はじめに

### 前提条件

- [チュートリアル 3: 基本ロボットのアーティキュレーション](03_articulate_robot.md) を完了していること
- USD のレイヤー、Reference、Payload など合成の仕組みを知っていること（[チュートリアル 10](10_closed_loop_structures.md) のステップ 1 で扱いました）

### 使用するアセット

このチュートリアルでは、Isaac Sim に同梱されている **Jetbot** のサンプルアセットを使用します：

| ファイル | 用途 |
|---|---|
| `Samples/Rigging/Jetbot/Jetbot_Base/Jetbot_base.usd` | 元のアセット（**ローカルにコピーして使用**） |
| `Samples/Rigging/Jetbot/Jetbot_Optimized/Jetbot_optimized.usd` | 最適化作業用空のステージ |
| `Samples/Rigging/Jetbot/Jetbot_Optimized/Jetbot_optimized_post_merge.usd` | メッシュ統合まで完了した中間状態（**参考用**） |
| `Samples/Rigging/Jetbot/Jetbot_Optimized/Jetbot_optimized_final.usd` | インスタンシングまで完了した最終形（**参考用**） |

サンプルフォルダの 3 つの `Jetbot_optimized*.usd` はすでに最適化処理が施された**参考データ**です。本チュートリアルでは、`Jetbot_base.usd` を作業用フォルダにコピーしたうえで、**自分で新規の `Jetbot_optimized.usd` を作成**して最適化作業を進めます。途中で詰まったときは、上記の参考ファイルを開いて期待される状態と見比べてください。

### 所要時間

約 20〜30 分

### 概要

Isaac Sim では、CAD や他の 3D ソフトからインポートしたロボットアセットは、メッシュやマテリアルが**細かく分かれた状態**になっていることがよくあります。たとえば 1 つの車輪が数十のメッシュとマテリアルに分割されていることも珍しくありません。これらは見た目には問題ありませんが、**シーングラフが肥大化し、描画と物理の両方でパフォーマンスを落とす原因**になります。

このチュートリアルでは、**Jetbot ロボット**を題材に、ロボットアセットをシミュレーション向けに最適化する手順を学びます。最適化により、デフォルト状態の **約 40 FPS から 64 FPS（約 1.6 倍）** への性能改善が得られます。

具体的には以下の流れで進めます：

1. **アセット構造の再編成** — シミュレーション用のレイヤーとプリム階層を準備する
2. **メッシュの統合** — Mesh Merge Tool で 1 リンクあたりのメッシュ数を 1 つにまとめる
3. **シーングラフインスタンシング** — 同一形状のメッシュを 1 つのデータとして共有する
4. **その他の最適化ポイント** — ライト、半透明マテリアル、コライダーなど

!!! note "なぜパフォーマンスが落ちるのか"
    USD のシーン構造（シーングラフ）に存在するプリムやメッシュは、**1 つひとつが描画コマンドや物理計算のオーバーヘッド**になります。リンクが 10 個でも、メッシュが 200 個に分割されていれば描画コストは約 200 個分です。**メッシュ統合**は描画コマンドを 1 つにまとめ、**インスタンシング**は同じデータを共有することでメモリ使用量を削減します。

!!! note "推奨されるアセット構造"
    Isaac Sim 公式の[アセット構造ガイドライン](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/robot_setup/asset_structure.html)では、ロボットアセットを以下の 3 段階に分けて整理することが推奨されています：

    | 段階 | 内容 |
    |---|---|
    | **Asset Source**（元データ） | CAD などからインポートした生のメッシュ・マテリアル。**変更しない** |
    | **Transformation**（最適化済み） | メッシュ統合・インスタンシング適用後のアセット。本チュートリアルで作成 |
    | **Features**（機能レイヤー） | 物理・センサー・ROS など、用途別のレイヤーを追加 |

    この設計により、CAD を更新したい場合は Asset Source を差し替えるだけで、リギングや物理設定を作り直す必要がなくなります。

## ステップ 1：アセット構造の再編成

まず、最適化されたシミュレーション用アセットを格納する**新しいプリム階層**を準備します。元のアセット（`Jetbot_base.usd`）は変更せず、別の USD ファイル（`Jetbot_optimized.usd`）に最適化済みの構造を作っていきます。

### 1-1. Inherit Parent Transform を有効にする

メッシュをドラッグ＆ドロップで階層を変えると、**親が変わると子の表示位置が動いてしまう**ことがあります。これを防ぐために、Reparenting 時に親の Transform を継承する設定を有効にします：

1. **Edit > Preferences** を開きます
2. 左側のリストから **Stage > Authoring** を選択
3. **Inherit Parent Transform** のチェックを入れます

   ![Inherit Parent Transform を有効化](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_asset_optimization_2.png)

!!! tip "なぜこの設定が必要か"
    USD のプリムは、最終的なワールド座標 = 親の Transform × 自身のローカル Transform で決まります。`Inherit Parent Transform` が無効だと、親を変更したときに**親の Transform を継承しない**ため、子のローカル Transform が変わらなくてもワールド位置が大きくズレます。最適化作業では多数のメッシュを別の親に移動するため、ここで一括して設定しておきます。

### 1-2. 作業用フォルダの準備とアセットのコピー

サンプルアセットは書き込み禁止のため、まずベースアセットを作業用フォルダにコピーします（[チュートリアル 10](10_closed_loop_structures.md) のステップ 1-1 と同じ流れです）：

1. 任意の場所（例：デスクトップ）に作業用フォルダを作成します（例：`Jetbot_optimization`）
2. **Content** タブで `Samples/Rigging/Jetbot/Jetbot_Base/` フォルダを開き、`Jetbot_base.usd` ファイルと、同じフォルダ内の関連リソース（`Materials`、`parts` など、フォルダ内に存在するもの）を作業用フォルダにダウンロードします

!!! tip "サンプルフォルダ内の `Jetbot_optimized*.usd` はコピー不要"
    `Jetbot_Optimized` 配下のファイルはすでに最適化済みの参考データです。これらを開いて中身を確認するのは構いませんが、**作業用フォルダにコピーする必要はありません**。

### 1-3. 新規 `Jetbot_optimized.usd` の作成とサブレイヤー読み込み

作業用フォルダで、最適化結果を記録するための新規 USD ファイルを作成し、ベースアセットをサブレイヤーとして読み込みます：

1. **File > New** で新しい空のステージを作成します
2. **File > Save As** で、ステップ 1-2 で作成した作業用フォルダに `Jetbot_optimized.usd` として保存します
3. **Layer** タブを開きます（表示されていない場合は **Window > Layer**）
4. **Root Layer**（`Jetbot_optimized.usd`）を選択した状態で **Insert Sublayer** ボタンをクリック
5. ファイル選択ダイアログで、作業用フォルダにコピーした `Jetbot_base.usd` を指定

   ![サブレイヤーの挿入](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_asset_optimization_3.png)

これで Jetbot のメッシュとマテリアルがビューポートに表示されます。**`Jetbot_optimized.usd` を Root Layer として作業を進めるので、以降の編集はすべてこのファイルに記録され、`Jetbot_base.usd` 自体は変更されません**。

!!! note "サンプルから直接サブレイヤーすることもできるが…"
    技術的には、作業用フォルダにコピーせず、サンプル側の `Jetbot_base.usd` を直接サブレイヤーとして指定することも可能です。しかし、Isaac Sim のサンプル配置やパスはバージョンアップで変わることがあり、そのままだと将来アセットが見つからなくなる可能性があります。**ローカルにコピーして相対パスで参照する**運用にしておくと、再現性が高まります。

!!! note "サブレイヤーとリファレンスの違い"
    [チュートリアル 10](10_closed_loop_structures.md) でも触れたように、**サブレイヤー**は同じプリム階層を共有してプロパティを上書きする合成方法、**リファレンス／ペイロード**は外部アセットを独立した子プリムとして配置する方法です。ここではベースアセットのプリム階層をそのまま受け継ぎながら、最適化された Xform 階層を**追加・並列に**作っていく流れになるため、サブレイヤーが適しています。

### 1-4. 最適化用の階層を作成

最適化されたアセットを格納する Xform を作成します：

1. **Stage** パネル上で右クリックして **Show Root** を選択し、`/`（ルート）レベルを表示します

   ![Show Root の有効化](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_asset_optimization_4.png)

2. ルート上で右クリック > **Create > Xform** を選択し、新しい Xform を `Jetbot_Sim` にリネーム
3. `Jetbot_Sim` の上で右クリック > **Set as Default Prim** を選択（このプリムがアセットの「玄関」になります）
4. ルート直下にもう 1 つ、**Scope** を作成して `Visuals` にリネーム（`Jetbot_Sim` の**外**に配置することがポイント）

最終的に Stage は次の構造になります：

```
/
├── Jetbot_Sim       <- Default Prim（シミュレーション用のリンク階層）
├── Visuals          <- ビジュアルメッシュ置き場（インスタンシングの参照元）
└── Jetbot           <- 元のアセット（このあと中身を移動して空にしていく）
```

!!! note "Scope と Xform の使い分け"
    **Xform** は座標変換を持ち、子プリムに位置・回転・スケールを与える「枠」です。一方 **Scope** は座標変換を持たない**ただのグループ**で、整理用のフォルダのように使えます。`Visuals` は中身のメッシュ自体が独自の Transform を持つ参照元なので、Scope のほうが意図に合います。

### 1-5. プリムのリペアレント

元の `Jetbot` プリムの中身を `Jetbot_Sim` 配下に移動します：

1. `Jetbot` 配下のすべての子プリムを Shift クリックでまとめて選択
2. 選択したまま `Jetbot_Sim` にドラッグ＆ドロップ

   ![プリムの移動](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_asset_optimization_5.png)

3. 移動したプリムが**グレーアウト（非アクティブ）**になっている場合は、選択して右クリック > **Activate** で再度有効にします

   ![プリムのアクティベート](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_asset_optimization_6.png)

4. `Jetbot_Sim/<リンク名>`（例：`Jetbot_Sim/left_wheel`）の**配下にコピーされたメッシュやマテリアル**を、リンク Xform 自体は残したまま**削除**します。リンク Xform は次のステップで Mesh Merge Tool が出力する統合メッシュを受け取る器として使うため、中身だけを空にしておきます。

   ![Jetbot_Sim 配下の残骸を削除](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_asset_optimization_6a.png)

!!! note "なぜ Jetbot_Sim 側の中身を消すのか"
    リペアレント操作によって、元の `Jetbot/<リンク>` の子要素（メッシュ・マテリアルなど）も `Jetbot_Sim/<リンク>` 配下に一緒に移動してきます。これらは未マージのままで、これから Mesh Merge Tool で**新しい統合メッシュを作って差し替える**ため、ここで一度きれいに片付けておきます。元のメッシュデータはサブレイヤーである `Jetbot_base.usd`（および `Jetbot/<元のリンク>` 配下）に保持されているため、Mesh Merge Tool はそちらを入力として参照できます。

!!! note "なぜ非アクティブになるのか"
    USD のサブレイヤー間でプリムを「移動」する操作は、内部的には**移動元の deactivate と移動先での再定義**になります。Stage パネルで非アクティブになっている場合は明示的に **Activate** することで、移動先のプリムが有効化されます。

## ステップ 2：メッシュの統合（Mesh Merge Tool）

CAD インポート直後の Jetbot は、1 つのリンクが**数十個のメッシュとマテリアル**に分かれています。これらをリンクごとに 1 つのメッシュにまとめることで、描画コマンド数とシーングラフのプリム数を大幅に削減できます。

!!! note "Mesh Merge Tool でできること"
    Mesh Merge Tool は、複数のメッシュを 1 つの統合メッシュに結合し、同時に**マテリアルも 1 つの統合マテリアル**にまとめてくれるツールです。元のメッシュは別の場所に保管されたままなので、必要なら再利用できます。

### 2-1. Mesh Merge Tool を開く

メニューから次の順にクリックします：

**Tools > Robotics > Asset Editors > Mesh Merge Tool**

ツールウィンドウが開きます。

### 2-2. 1 つのリンク（左車輪）でのマージ手順

まずは `left_wheel` を例に、メッシュ統合の流れをひととおり実行します：

1. **Stage** パネルで `Jetbot/left_wheel`を選択
2. Mesh Merge Tool で **Combine Materials** にチェックを入れる
3. **Material Save Location** ( **Combine Materials** チェックボックス横の入力欄) に `/Jetbot_Sim/Looks` を指定（マテリアルを集約する保存先）
4. **Merge** ボタンをクリック

   ![Mesh Merge Tool の設定](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_asset_optimization_7.png)

5. 統合結果が `/Merged/left_wheel` として一時的に作成されます
6. 作成されたメッシュを選択し、**Properties** パネルの **Transform** セクションで位置・回転・スケールを**すべて 0（または恒等値）にクリア**

   ![Transform のクリア](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_asset_optimization_8.png)

!!! tip "Transform をクリアする理由"
    Mesh Merge Tool は、選択したプリムのワールド座標を基準にメッシュを焼き込みます。そのため、新しく作られた `/Merged/left_wheel` には**ワールド位置と同じ Transform**が入った状態になります。次のステップでこのメッシュを `Visuals` 配下に置いて参照させる場合、Transform をゼロに戻しておかないと、参照元と参照先で Transform が**二重に適用**されてしまいます。

### 2-3. ビジュアル参照構造を作る

統合したメッシュを `Visuals` 配下に置き、シミュレーション用の `Jetbot_Sim/left_wheel` からは**リファレンスで参照**する構造を作ります。これにより、後のステップでインスタンシングが効くようになります。

1. `/Visuals` 配下に Xform を作成し、`left_wheel` にリネーム
2. `/Merged/left_wheel` を `/Visuals/left_wheel` にドラッグ＆ドロップで移動
3. 空になった `/Merged` プリムを削除

   ![Visuals 配下への配置](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_asset_optimization_9.png)

次に、シミュレーション側のリンク `Jetbot_Sim/left_wheel` に、`Visuals/left_wheel` を参照する Xform を追加します：

4. `Jetbot_Sim/left_wheel` 配下に新しい Xform を作成し、`Visuals` にリネーム
5. その Xform 上で右クリック > **Add > Reference** を選択

   ![Reference の追加](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_asset_optimization_10.png)

6. ファイル選択ダイアログで、作業用フォルダにコピーした `Jetbot_base.usd` を選択（次のステップで Asset Path を空にして内部参照に変えるため、ここでの選択ファイルは「ダイアログを閉じる足場」として一時的に使うだけです）

   ![ファイル選択](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_asset_optimization_11.png)

7. Prim Path に `/Visuals/left_wheel` と入力

   ![Prim Path の入力](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_asset_optimization_12.png)

8. **Properties** パネルの **References** セクションを開き、**Asset Path** の値を消して空にする（同じステージ内を参照する「内部参照」になります）

   ![Asset Path のクリア](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_asset_optimization_12a.png)

9. ビューポートに左車輪が正しく表示され、Stage 上は `Jetbot_Sim/left_wheel/Visuals` 配下に統合済みメッシュが現れることを確認

   ![完成した参照構造](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_asset_optimization_13.png)

!!! note "なぜ「内部参照」にするのか"
    `Jetbot_optimized.usd` の `Visuals` 配下にメッシュを置き、同じファイル内で参照する形にすると、外部ファイルへの依存なくアセット 1 つで完結します。次のインスタンシング設定もこの内部参照に対して適用します。

!!! tip "Reference と Payload"
    [チュートリアル 10](10_closed_loop_structures.md) で扱ったように、**Reference は常に読み込まれ**、**Payload は遅延読み込み（Unload 可能）** です。ここでは「ロボット本体には常に必要なビジュアル」なので Reference を使っています。

### 2-4. 残りのリンクへの適用

`right_wheel`、`chassis`、`caster_wheel` など、ほかのリンクにも同じ手順を繰り返します：

1. `Jetbot/<リンク名>` を選択
2. Mesh Merge Tool で **Merge**
3. `/Merged/<リンク名>` の Transform をクリア
4. `/Visuals/<リンク名>` に移動
5. `Jetbot_Sim/<リンク名>/Visuals` に内部参照を作成

!!! tip "途中結果のサンプルファイル"
    すべてのリンクをマージするのは手間がかかるため、Isaac Sim にはマージ済みの中間ファイル `Samples/Rigging/Jetbot/Jetbot_Optimized/Jetbot_optimized_post_merge.usd` が同梱されています。次のインスタンシングのステップから始めたい場合は、このファイルとその関連リソースを作業用フォルダにコピーしてから開き、作業を続けてください（サンプル領域は書き込み禁止のため、直接開いて編集すると保存できません）。

## ステップ 3：シーングラフインスタンシング

Jetbot の左右の車輪は**まったく同じ形状**です。同じメッシュデータを 2 つ持つのではなく、**1 つのデータを共有して描画する**ように設定すれば、メモリ使用量と描画コストを下げられます。これが**シーングラフインスタンシング**です。

!!! note "シーングラフインスタンシングとは"
    インスタンシングは「同じ形状を別の場所に描く」ための GPU の標準的な仕組みです。USD では、リファレンスされたプリムに `Instanceable = true` を設定することで、Hydra（USD の描画系）が**同じソースから来ているプリムを 1 つの描画呼び出しにまとめてくれます**。

    制限として、**Instanceable なプリム配下の子プロパティを個別に上書きできなく**なります（マテリアルや Transform の差し替えなど）。今回はビジュアルメッシュにのみ適用するため、この制限は問題になりません。

### 3-1. 共通形状の統合

左右の車輪は同じ形状なので、参照元の `Visuals` 配下を 1 つにまとめます：

1. ステップ 2 のマージ作業を行ったファイル（または作業用フォルダにコピーした `Jetbot_optimized_post_merge.usd`）を開きます
2. `/Visuals/left_wheel` を `/Visuals/wheel` にリネーム
3. `/Visuals/right_wheel` を**削除**
4. `Jetbot_Sim/right_wheel/Visuals` の **References** で、Prim Path を `/Visuals/wheel` に書き換え

これで、左右の `Jetbot_Sim/<wheel>/Visuals` がどちらも `/Visuals/wheel` を参照する形になります。

### 3-2. Instanceable を有効にする

リファレンスされた Visuals プリムをインスタンシング対象にします：

1. `Jetbot_Sim` 配下の各リンクの `Visuals` プリム（`left_wheel/Visuals`、`right_wheel/Visuals`、`chassis/Visuals` など）を Shift クリックでまとめて選択
2. **Properties** パネルで **Instanceable** にチェックを入れる
3. Stage 上で参照アイコンに**青い「I」のマーク**が表示されることを確認

   ![Instanceable インジケータ](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/isim_5.0_full_tut_gui_asset_optimization_16.png)

!!! warning "Instanceable とコリジョン／マテリアルの個別設定"
    **Instanceable** が有効なプリムでは、その配下のメッシュごとにマテリアルやコリジョン近似を変更できなくなります。[チュートリアル 10](10_closed_loop_structures.md) のステップ 2-5、6-2 でも触れたように、後からリンクごとにマテリアルを差し替えたい場合は、対象プリムの Instanceable を**一時的にオフ**にしてから設定し、終わったら戻します。

### 3-3. 保存前のクリーンアップ

保存する前に、最適化済みアセットを使うときに紛らわしくならないよう、不要なプリムを整理しておきます。原典のドキュメントでも「Visuals スコープは隠せる」と触れられているステップで、必須ではありませんが推奨される後片付けです。

**`/Visuals` スコープの非表示化**

`/Visuals` 配下のメッシュは、`Jetbot_Sim/<リンク>/Visuals` から内部リファレンスされて表示されます。`/Visuals` 自身もルート直下に存在するため、そのままだとビューポートで**ベースメッシュが Jetbot_Sim 側と二重に表示**される場合があります。

1. **Stage** パネルで `/Visuals` を選択
2. パネル右側の**目のアイコン**をクリックして非表示にする（`visibility = invisible`）

これにより `/Visuals` 自体はビューポートに描画されなくなりますが、リファレンス元としては引き続き機能するため `Jetbot_Sim/<リンク>/Visuals` 経由のメッシュ表示には影響しません。

**`/Jetbot` 配下の整理**

ステップ 1-5 のリペアレントにより、`/Jetbot` 配下はリンク階層が抜けた状態になっています。実際の見え方は USD の合成挙動次第で、グレーアウトしている／空の Xform だけが残っている／元のメッシュがまだ見える、などのいずれかです。Stage パネルが見にくいと感じる場合は、以下のいずれかで整理できます：

- `/Jetbot` プリムを**削除**する（Root Layer に削除指示が記録される。サブレイヤーの `Jetbot_base.usd` は変更されない）
- `/Jetbot` プリム自体を**非表示**にする（目のアイコンで切り替え）

!!! tip "削除と非表示の使い分け"
    **削除**は USD の合成上 `/Jetbot` がない状態にするため、最もすっきりします。Mesh Merge の入力として `/Jetbot/<元のリンク>` を参照する作業が完了していれば、削除して問題ありません。一方、後で「あの部分のメッシュをもう一度参照したい」となる可能性があるなら**非表示**にしておく方が安全です。

### 3-4. 保存

クリーンアップが終わったら、**Ctrl + S** でファイルを保存します。

!!! tip "完成形のサンプルファイル"
    `Jetbot_optimized_final.usd` がインスタンシングまで完了した状態のファイルです。手順の最終結果と見比べたいときに参照してください。

## ステップ 4：その他のパフォーマンス最適化

メッシュ統合とインスタンシングが効果の大きい 2 大施策ですが、以下の点も合わせて見直すとさらにフレームレートを稼げます。

### 4-1. レンダリングまわり

**ライトの数を減らす**

Isaac Sim のデフォルトレンダラーは、**シーンに 10 個以上のライトがあるとサンプルベースのライティングモード**に切り替わり、計算コストが急増します。デフォルトの環境ライトと、必要なポイントライトだけに絞るのが基本です。

**半透明マテリアルを避ける**

ガラスや煙のような **OmniPBR Translucent** 系マテリアルは、不透明な OmniPBR と比べて描画コストが大きく、シーン全体のボトルネックになりやすいパーツです。デモ目的でなければ可能な限り不透明マテリアルに置き換えてください。

### 4-2. 物理計算まわり

**コライダー形状を単純化する**

メッシュコライダー（Triangle Mesh）は最も正確ですが、**Convex Hull** や **Convex Decomposition**、または基本形状（Box / Sphere / Cylinder / Capsule）に置き換えるだけで物理計算が大幅に軽くなります。

| コライダー | 計算コスト | 用途 |
|---|---|---|
| **Box / Sphere / Cylinder** | 低 | 単純な形状の代替（車輪など） |
| **Convex Hull** | 中 | バランス重視のデフォルト |
| **Convex Decomposition** | 中〜高 | 凹みのある形状 |
| **Triangle Mesh** | 高 | 高精度が必要なときのみ |

**接触点の数を減らす**

複数のリジッドボディが重なって接触する局面では、接触点（Contact Point）の数が物理計算量を支配します。コライダーを単純化することで結果的に接触点も減るため、上の項目と密接に関連します。

**車輪はメッシュではなくシリンダー／スフィアに**

走行ロボットの車輪をメッシュコライダーで扱うと、地面との接触計算が非常に重くなります。**Cylinder** または **Sphere** で近似することで、走行性能と計算コストの両方が改善します。

### 4-3. 計測の習慣

最適化の効果は環境やシーンによって異なります。**変更前後でフレームレートを記録**し、効いた施策と効かなかった施策を分けて把握するのが、無駄な作業を減らすコツです。Isaac Sim では HUD のオーバーレイで FPS を表示できるので、最適化のたびに確認しましょう。

## トラブルシューティング

| 症状 | 原因 | 解決方法 |
|---|---|---|
| プリムをドラッグ移動するとワールド位置がズレる | **Inherit Parent Transform** が無効 | **Edit > Preferences > Stage > Authoring** で有効化 |
| 移動先のプリムがグレーアウトしてビューポートに出ない | サブレイヤーをまたいだ移動で deactivate された | 該当プリムを右クリック > **Activate** |
| Mesh Merge 後の表示位置がズレる | `/Merged/<リンク名>` の Transform が残っている | Properties > Transform をすべてクリア（位置 0、回転 0、スケール 1） |
| インスタンス化したいのに参照アイコンに青い "I" が出ない | 参照先が外部ファイルのまま、または Instanceable が未チェック | **References** の Asset Path を空にして内部参照にし、**Instanceable** をオン |
| Instanceable プリム配下のマテリアルやコライダーを変更できない | Instanceable が有効 | 対象 Xform で一時的に Instanceable をオフ、変更後に戻す |
| 最適化したのに FPS が変わらない | ライト数が多い／半透明マテリアルが残っている／メッシュコライダー使用 | ステップ 4 のチェックリストを確認 |
| ベースメッシュが二重に表示される | `/Visuals` スコープが表示されたまま | ステップ 3-3 に従い `/Visuals` を非表示にする |
| Stage パネルに `/Jetbot` の残骸が残って見にくい | リペアレント後の元アセット階層がそのまま残っている | ステップ 3-3 に従い `/Jetbot` を非表示または削除（サブレイヤーは変更されない） |

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. **アセット構造の再編成** — Inherit Parent Transform を有効にしたうえで、`Jetbot_Sim`（リンク階層）と `Visuals`（参照元の置き場）に分離
2. **Mesh Merge Tool** — 1 リンクあたりのメッシュとマテリアルを 1 つに統合
3. **内部参照によるビジュアル分離** — シミュレーション用リンクから `Visuals/<リンク名>` を Reference する構造
4. **シーングラフインスタンシング** — 同形状のメッシュを 1 つのデータで共有、Instanceable で描画コストを削減
5. **その他の最適化** — ライト、半透明マテリアル、コライダー、接触点の見直し

これらを組み合わせることで、Jetbot サンプルでは **40 FPS → 64 FPS（約 1.6 倍）** の改善が得られます。実機ロボットの USD アセットでも、メッシュ統合とインスタンシングは特に効果が大きいため、シミュレーションが重いと感じたらまずここから着手するのがおすすめです。

!!! tip "アセット構造ガイドラインも合わせて参照"
    本チュートリアルで作成した「ベース／最適化／機能（物理・センサー）」の分離構造は、Isaac Sim 公式の[アセット構造ガイドライン](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/robot_setup/asset_structure.html) に基づいています。物理・センサー・ROS など機能ごとにレイヤーを分けると、アセットの再利用性とメンテナンス性がさらに高まります。

## 次のステップ

次のチュートリアル「[脚ロボットのリギング](13_rig_legged_robot.md)」に進み、ロコモーションポリシーに合わせた脚ロボットのリギング方法を学びましょう。
