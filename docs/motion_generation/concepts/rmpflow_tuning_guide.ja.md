---
title: RMPflow チューニングガイド
---

# RMPflow チューニングガイド

## 概要

完全な RMP セットを指定するパラメータ数は多く、新しいロボットやタスク向けに RMPflow ベースの Motion Policy を調整するのは一見難しく感じられます。しかし実際には、あるロボットでうまく動くパラメータは、**形態の似た他のロボットでもうまく動く**ことが多く、あるロボットでは幅広いタスクに使えるパラメータを選べるのが一般的です。

RMPflow とその機能については [RMPflow（理論）](rmpflow.md) を参照してください。

## テンプレートからの調整

Isaac Sim には、7 自由度の Franka Emika Panda と 6 自由度の Universal Robots UR10 の RMPflow 設定ファイル例が含まれています。新しいマニピュレータを調整する際は、まずこのどちらかから始めるのが最善です。

- 参照ロボットより**大幅に大きい/小さい**場合は、長さの単位を持つパラメータをリスケールする必要があります。
- **関節数が異なる**場合は、`cspace_target_rmp/robust_position_term_thresh` も調整が必要なことがあります。

多くの場合、これらの手順だけで動作する Motion Policy が得られます。

## ゼロから調整する手順

既存設定の流用でうまくいかない場合は、次の手順でゼロから調整します。

!!! tip
    既存ロボット（例：Franka）でパラメータ値をいろいろ試してみると理解が深まります。

### 1. すべての RMP をオフにする

- 各 RMP の `metric_weight` または `metric_scalar` を 0 にして無効化します。target RMP は `min_metric_scalar` / `max_metric_scalar` / `min_metric_alpha` をすべて 0 にします。
- すべての慣性項を 0 にします（`cspace_target_rmp/inertia`、`damping_rmp/inertia`）。

### 2. RMP を 1 つずつ再有効化する

推奨順序で有効化します。

**cspace_target_rmp**：ロボットを C 空間の構成へ確実に動かします。`metric_scalar` は全 RMP のグローバルスケールを決めるため、比較的小さく保ちます（例：1〜100）。Robot Description ファイル（YAML）のデフォルト構成を、妥当な自然な「レディ」姿勢に設定します（移動中に favor される姿勢）。

**target_rmp**：冗長性解決に cspace target RMP を使いつつ、エンドエフェクタをターゲットへ確実に動かします。

- `target_rmp/min_metric_alpha` を 0、`target_rmp/metric_alpha_length_scale` をロボットサイズに対して大きな値（例：100,000）にし、計量中の方向性 S 項を実質オフにして等方計量に簡略化します。
- `target_rmp/proximity_metric_boost_length_scalar` を 1 にして優先度ブーストをオフにします。
- `target_rmp/max_metric_scalar` を `cspace_target_rmp/metric_scalar` に対して十分大きくし、target RMP が支配的になるようにします（cspace target RMP が target RMP のヌル空間でのみ働くようになります）。
- `accel_p_gain` / `accel_d_gain` / `accel_norm_eps` を、エンドエフェクタに良いアトラクタ挙動が得られるまで調整します。
- `max_metric_scalar` を減らしてみて、大きすぎないか確認します。適切な値へ増やすにつれ収束精度は徐々に向上します。値に達する前に小さな一定誤差で精度が頭打ちなら、設定が高すぎる可能性があります。

**collision_rmp**：`collision_rmp/metric_scalar` を `target_rmp/max_metric_scalar` と同程度にして衝突回避 RMP を有効化します。加速度と計量の式をプロットすると各パラメータの役割を理解しやすくなります。

**target_rmp（再調整）**：衝突 RMP を有効化すると、target RMP と衝突 RMP がせめぎ合い、障害物付近で通常より遅く動くことがあります。計量の方向性項をオンにするとこれが補正されます。

- 目標からの距離の関数として target RMP の計量をプロットして理解を深めます。まずブースト項なしで、低ランクの遠距離計量からフルランクの近距離計量へどう遷移するか観察します。
- `target_rmp/min_metric_alpha` を非ゼロにし、良い挙動になるまで `target_rmp/metric_alpha_length_scale` を減らします。

**axis_target_rmp**：姿勢ターゲットを設定する場合、制御フレームの向きをターゲット姿勢に合わせます。位置ターゲットへの距離に依存する優先度ブーストを含み、姿勢を詰める前に位置を進められます。

**joint_limit_rmp**：適切に調整すれば、関節リミットが回避される以外は挙動が変わりません。

**damping_rmp**：必要に応じて damping RMP と `target_rmp/inertia` を有効化し、ジャークを抑えます。

!!! note
    この手順全体を通して、既存の RMPflow 設定ファイルを参照すると役立ちます。

## 関連ページ

- パラメータの意味は [RMPflow（理論）](rmpflow.md) を参照してください。
- 新しいロボットへの適用の実例は [新しいマニピュレータ用の RMPflow 設定](../07_configure_rmpflow_denso.md) を参照してください。
