# TODO — Isaac Sim 6.0.1 対応の残作業

5.1.0 → 6.0.1 移行（2026-07）時点で未着手の作業リスト。
作業手順・執筆規約は [MAINTENANCE.md](MAINTENANCE.md) を参照。
URL はすべて 2026-07-17 時点で 200 を確認済み。

**★** = 既存ページの warning / note / index から公式ページへ外部リンクで言及済み（本サイト内に受け皿ページを作ると導線が完結する）。

## 1. 未作成ページ（公式 6.0 で新設されたチュートリアル）

### ROS 2（`docs/ros/`）

- [ ] ★ Heightmap Importer によるナビゲーション — [tutorial_ros2_navigation_heightmap.html](https://docs.isaacsim.omniverse.nvidia.com/latest/ros2_tutorials/tutorial_ros2_navigation_heightmap.html)（Block World Generator（20）の公式後継。20 の warning から言及済み）
- [ ] ROS 2 圧縮画像 — [tutorial_ros2_compressed_image.html](https://docs.isaacsim.omniverse.nvidia.com/latest/ros2_tutorials/tutorial_ros2_compressed_image.html)（`isaac_compressed_image_decoder` パッケージを使用）
- [ ] RTX Radar の ROS 2 パブリッシュ — [tutorial_ros2_rtx_radar.html](https://docs.isaacsim.omniverse.nvidia.com/latest/ros2_tutorials/tutorial_ros2_rtx_radar.html)（OgnROS2RtxRadarHelper、PointCloud2）
- [ ] 総合演習（Putting It All Together） — [tutorial_ros2_putting_it_all_together.html](https://docs.isaacsim.omniverse.nvidia.com/latest/ros2_tutorials/tutorial_ros2_putting_it_all_together.html)
- [ ] ROS 2 FAQ — [ros2_faq.html](https://docs.isaacsim.omniverse.nvidia.com/latest/ros2_tutorials/ros2_faq.html)（troubleshooting セクションへの統合でも可）

### 合成データ生成（`docs/synthetic_data/`）

- [ ] ★ SDG ワークフロー例（Replicator Functional API） — [tutorial_replicator_sdg_workflows.html](https://docs.isaacsim.omniverse.nvidia.com/latest/replicator_tutorials/tutorial_replicator_sdg_workflows.html)（index から言及済み。6.0 の Functional API 時代の代表例）
- [ ] テレオペレーション SDG — [tutorial_replicator_teleop_sdg.html](https://docs.isaacsim.omniverse.nvidia.com/latest/synthetic_data_generation/tutorial_replicator_teleop_sdg.html)（isaacsim.replicator.teleop / episode_recorder、6.0 新機能）
- [ ] AI ビヘイビアツリー生成 — [tutorial_behavior_tree_gen.html](https://docs.isaacsim.omniverse.nvidia.com/latest/action_and_event_data_generation/tutorial_behavior_tree_gen.html)（自然言語 → ビヘイビアツリー JSON。IRA 1.x と関連）
- [ ] Metropolis パイプライン — [tutorial_omni_metropolis_pipeline.html](https://docs.isaacsim.omniverse.nvidia.com/latest/action_and_event_data_generation/tutorial_omni_metropolis_pipeline.html)（Action/Event Data Generation の統合オーケストレーション）
- 備考: IRA / IRO の公式サブページ群（configuration / sample_configs / custom_writer / chat_iro / empty_space_detection 等）は 17・18 に要約済み。詳細ページ化は必要になってから。

### センサー（`docs/sensors/`）

- [ ] ★ Physics Raycast センサー — [isaacsim_sensors_physics_raycast.html](https://docs.isaacsim.omniverse.nvidia.com/latest/sensors/isaacsim_sensors_physics_raycast.html)（**優先度高**: PhysX Lidar/Generic/Lightbeam（15〜17）の後継として 3 ページから移行表で言及済み）
- [ ] ★ Joint State センサー — [isaacsim_sensors_physics_joint_state.html](https://docs.isaacsim.omniverse.nvidia.com/latest/sensors/isaacsim_sensors_physics_joint_state.html)（index・08 から言及済み）
- [ ] ★ マルチティックレンダリング — [isaacsim_sensors_multitick_rendering.html](https://docs.isaacsim.omniverse.nvidia.com/latest/sensors/isaacsim_sensors_multitick_rendering.html)（tick_rate 駆動の基盤概念。ros/05・07・10 とセンサー各ページの理解に効く）
- [ ] ★ 構造化光カメラ — [isaacsim_sensors_camera_structured_light.html](https://docs.isaacsim.omniverse.nvidia.com/latest/sensors/isaacsim_sensors_camera_structured_light.html)（index・01 から言及済み）
- [ ] ★ RTX Acoustic（超音波）センサー — [isaacsim_sensors_rtx_acoustic.html](https://docs.isaacsim.omniverse.nvidia.com/latest/sensors/isaacsim_sensors_rtx_acoustic.html)（index・03 から言及済み）
- [ ] ★ RTX カスタムセンサー — [isaacsim_sensors_rtx_custom.html](https://docs.isaacsim.omniverse.nvidia.com/latest/sensors/isaacsim_sensors_rtx_custom.html)（index から言及済み）

### モーション生成（`docs/motion_generation/`）— 6.0 の新世代スタック

Lula 系（既存 01〜08）は deprecated のまま保持中。後継の新セクション群が丸ごと未作成：

- [ ] ★ Robot Motion (Experimental) 概要 — [robot_motion_experimental/index.html](https://docs.isaacsim.omniverse.nvidia.com/latest/robot_motion_experimental/index.html)（index の warning から言及済み。まずこれを入口として作るのが良い）
- [ ] ★ Motion Generation (Experimental) — [motion_generation/index.html](https://docs.isaacsim.omniverse.nvidia.com/latest/motion_generation/index.html) ＋ サブページ 3 本：[scene_interaction](https://docs.isaacsim.omniverse.nvidia.com/latest/motion_generation/scene_interaction.html) / [trajectory_planning](https://docs.isaacsim.omniverse.nvidia.com/latest/motion_generation/trajectory_planning.html) / [mobile_robot_control_example](https://docs.isaacsim.omniverse.nvidia.com/latest/motion_generation/mobile_robot_control_example.html)
- [ ] ★ cuMotion Integration — [cumotion/index.html](https://docs.isaacsim.omniverse.nvidia.com/latest/cumotion/index.html) ＋ チュートリアル 6 本（robot_configuration / world_interface / rmpflow / graph_planner / trajectory_generator / trajectory_optimizer）
- [ ] ★ PINK Integration（task-based differential IK） — [pink/index.html](https://docs.isaacsim.omniverse.nvidia.com/latest/pink/index.html) ＋ チュートリアル 3 本（robot_configuration / ik_controller / multi_task)
- 備考: 着手する場合は `docs/motion_generation/` 配下にサブディレクトリ（`experimental/`・`cumotion/`・`pink/`）を切り、nav にネストグループを追加する構成を推奨（concepts/ と同じ方式）。

### OmniGraph（`docs/omnigraph/`）

- [ ] ★ カスタム IPC ノードの構築 — [omnigraph_custom_ipc_nodes.html](https://docs.isaacsim.omniverse.nvidia.com/latest/omnigraph/omnigraph_custom_ipc_nodes.html)（index の「本サイト補足」から言及済み）

### 新セクション候補（本サイトに対応セクション自体がないもの）

- [ ] Newton 物理エンジン — [physics/newton_physics.html](https://docs.isaacsim.omniverse.nvidia.com/latest/physics/newton_physics.html)、[newton_actuators_tutorials/index.html](https://docs.isaacsim.omniverse.nvidia.com/latest/newton_actuators_tutorials/index.html) ＋ チュートリアル 4 本（6.0 の目玉機能。troubleshooting か新セクションでの解説を検討）
- [ ] OpenUSD チューニングチュートリアル — [openusd_tuning_tutorials/index.html](https://docs.isaacsim.omniverse.nvidia.com/latest/openusd_tuning_tutorials/index.html) ＋ 7 本（robot_setup と関連が深い）
- [ ] Robot Inspector / Robot Poser / Joint Inspector / Asset Transformer — [robot_inspector](https://docs.isaacsim.omniverse.nvidia.com/latest/robot_setup/robot_inspector.html) / [robot_poser](https://docs.isaacsim.omniverse.nvidia.com/latest/robot_setup/robot_poser.html) / [joint_inspector](https://docs.isaacsim.omniverse.nvidia.com/latest/robot_setup/joint_inspector.html) / [asset_transformer](https://docs.isaacsim.omniverse.nvidia.com/latest/robot_setup/asset_transformer.html)（6.0 の新ロボットセットアップツール群。robot_setup 05a・06 から一部言及済み）

## 2. .en.md の完全版化（既存方針のバックログ）

ros / synthetic_data / sensors / motion_generation / omnigraph / isaac_lab の 6 セクションの `.en.md` は
「Preliminary version」の要約版。**動作確認が完了したセクションから順に ja と同内容の完全版へ引き上げる**
（2026-07 の 6.0.1 移行では事実修正のみ実施済み。isaac_lab は 00/01 がユーザー加筆によりほぼ同期済み）。

- [ ] ros
- [ ] synthetic_data
- [ ] sensors
- [ ] motion_generation
- [ ] omnigraph
- [ ] isaac_lab（残り: 02_cloner / 03_instanceable_assets / index の確認）

## 3. その他の小タスク

- [ ] `docs/robot_setup/images/55〜57_*.png` が未参照になっている（10_closed_loop_structures の旧自作 OmniGraph 手順の画像。公式レイヤー方式への更新で本文から外れた）。削除するか、本サイト補足として再掲するか判断する。
- [ ] `docs/importer_exporter/images/03_mjcf_import_options.png` も未参照（6.0 で UI が変わり公式画像に差し替えたため）。同上。
- [ ] Isaac Lab が Isaac Sim 6.0 に正式対応したら、`docs/isaac_lab/00_setup` の「6.0 未対応」warning を外し、インストール手順（`isaacsim==5.1.0` 固定箇所）を更新する。定期的に [Isaac Lab 公式](https://isaac-sim.github.io/IsaacLab/main/source/setup/installation/index.html) を確認。
- [ ] nav 上の `13_proximity_sensor` の位置（公式 latest では PhysX SDK センサー節に分類変更。index 本文は対応済み、nav の並びは現状 12 と 14 の間で実質問題なし）。
