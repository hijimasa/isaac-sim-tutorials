---
title: データロギング
---

# データロギング

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます:

- `DataLogger` クラスを使ったシミュレーションデータの記録方法
- 記録データの JSON ファイルへの保存
- 保存されたデータの読み込みと再生（軌道再生・シーン再生）

## はじめに

### 前提条件

- [チュートリアル 4: マニピュレータロボットの追加](04_adding_a_manipulator_robot.md) を完了していること

### 所要時間

約 10〜15 分

### 概要

ロボットシミュレーションでは、ロボットの関節状態や制御入力、環境内のオブジェクトの位置などを記録しておくことがデバッグや解析に役立ちます。Isaac Sim では **`DataLogger`** クラスを使って、物理ステップごとにシミュレーションデータを記録し、JSON ファイルとして保存できます。

このチュートリアルでは、Franka ロボットがターゲットを追従する Follow Target サンプルを使い、データの記録と再生を行います。

## データの記録

### サンプルのロード

1. **Windows > Examples > Robotics Examples** をアクティブにして、Robotics Examples タブを開きます。
2. **Robotics Examples > Manipulation > Follow Target Task** をクリックします。
3. **LOAD** ボタンを押してワールドを読み込みます。Franka ロボットとターゲットの立方体がシーンに配置されます。

### 記録の実行

4. Follow Target メニューの **Data Logging** セクションで、JSON ファイルの **Output Directory**（出力先ディレクトリ）を指定します。
5. **Task Controls** の **Follow Target** ボタンをクリックしてタスクを開始します。
6. **START LOGGING** ボタンをクリックして記録を開始します。
7. ビューポート上でターゲットの立方体を移動させ、Franka がそれを追従する様子を観察します。
8. 数秒間操作した後、**SAVE DATA** ボタンをクリックしてデータを保存します。
9. **File > New From Stage Template > Empty** で新しいステージを作成します。

### コードの解説

Follow Target サンプルのコードを確認して、DataLogger の使い方を理解しましょう。

!!! tip "ソースコードの場所"
    Follow Target サンプルのソースコードは以下のパスにあります：
    `<Isaac Sim インストールディレクトリ>/exts/isaacsim.examples.interactive/isaacsim/examples/interactive/follow_target/follow_target.py`

#### ロギング関数の登録

`DataLogger` では、**物理ステップごとに呼ばれるロギング関数**を登録して、記録するデータを定義します。

```python linenums="1"
def _on_logging_event(self, val):
    world = self.get_world()
    data_logger = world.get_data_logger()
    if not world.get_data_logger().is_started():
        robot_name = self._task_params["robot_name"]["value"]
        target_name = self._task_params["target_name"]["value"]

        # 毎物理ステップで呼ばれるロギング関数を定義
        def frame_logging_func(tasks, scene):
            return {
                "joint_positions": scene.get_object(robot_name)
                    .get_joint_positions().tolist(),
                "applied_joint_positions": scene.get_object(robot_name)
                    .get_applied_action().joint_positions.tolist(),
                "target_position": scene.get_object(target_name)
                    .get_world_pose()[0].tolist(),
            }

        data_logger.add_data_frame_logging_func(frame_logging_func)
    if val:
        data_logger.start()
    else:
        data_logger.pause()
    return
```

`frame_logging_func` は `tasks` と `scene` を引数に取り、辞書を返します。辞書のキーがデータ項目名、値が記録するデータです。この関数は `DataLogger` が開始されている間、すべての物理ステップで自動的に呼ばれます。

| データ項目 | 内容 |
|---|---|
| `joint_positions` | ロボットの現在の関節角度 |
| `applied_joint_positions` | コントローラが指令した関節角度 |
| `target_position` | ターゲットのワールド座標 |

#### データの保存

```python linenums="1"
def _on_save_data_event(self, log_path):
    world = self.get_world()
    data_logger = world.get_data_logger()
    data_logger.save(log_path=log_path)
    data_logger.reset()
    return
```

`save()` で JSON ファイルに保存し、`reset()` で内部状態をクリアします。

### データ形式

保存される JSON ファイルの構造は以下の通りです：

```json
{
  "Isaac Sim Data": [
    {
      "current_time": 1.483,
      "current_time_step": 89,
      "data": {
        "joint_positions": [0.075, -1.231, 0.113, ...],
        "applied_joint_positions": [0.072, -1.220, 0.119, ...],
        "target_position": [0.0, 10.0, 70.0]
      }
    },
    ...
  ]
}
```

各フレームに自動的に付与されるメタデータ:

| フィールド | 内容 |
|---|---|
| `current_time` | シミュレーション開始からの経過時間（秒） |
| `current_time_step` | フレームインデックス |
| `data` | `frame_logging_func` が返した辞書 |

## データの再生

記録したデータを使って、ロボットの動作を再現します。

### サンプルのロード

1. **Robotics Examples > Manipulation > Replay Follow Target Task** をクリックします。
2. **LOAD** ボタンを押してワールドを読み込みます。
3. **Data Replay** セクションの **Data File** フィールドに、先ほど保存した JSON ファイルのパスを指定します。

### 軌道再生（Replay Trajectory）

軌道再生では、記録された関節角度指令値をロボットに適用して動作を再現します。ターゲットの位置は更新しません。

4. **Replay Trajectory** ボタンをクリックします。

!!! tip "ソースコードの場所"
    Replay Follow Target サンプルのソースコードは以下のパスにあります：
    `<Isaac Sim インストールディレクトリ>/exts/isaacsim.examples.interactive/isaacsim/examples/interactive/replay_follow_target/replay_follow_target.py`

#### 軌道再生のコード

```python linenums="1"
async def _on_replay_trajectory_event_async(self, data_file):
    self._data_logger.load(log_path=data_file)
    world = self.get_world()
    await world.play_async()
    world.add_physics_callback("replay_trajectory", self._on_replay_trajectory_step)
    return

def _on_replay_trajectory_step(self, step_size):
    if self._world.current_time_step_index < self._data_logger.get_num_of_data_frames():
        data_frame = self._data_logger.get_data_frame(
            data_frame_index=self._world.current_time_step_index
        )
        self._articulation_controller.apply_action(
            ArticulationAction(
                joint_positions=data_frame.data["applied_joint_positions"]
            )
        )
    return
```

再生処理の流れ:

1. `load()` で JSON ファイルからデータを読み込む
2. 物理コールバックを登録
3. 各物理ステップで `get_data_frame()` を使い、現在のステップに対応するフレームデータを取得
4. `applied_joint_positions` を `ArticulationAction` として適用

### シーン再生（Replay Scene）

シーン再生では、関節角度に加えてターゲットの位置も更新し、記録時のシーンを完全に再現します。

5. 再生が完了したら **Reset** ボタンを押します。
6. **Replay Scene** ボタンをクリックします。

#### シーン再生のコード

```python linenums="1"
def _on_replay_scene_step(self, step_size):
    if self._world.current_time_step_index < self._data_logger.get_num_of_data_frames():
        target_name = self._task_params["target_name"]["value"]
        data_frame = self._data_logger.get_data_frame(
            data_frame_index=self._world.current_time_step_index
        )
        self._articulation_controller.apply_action(
            ArticulationAction(
                joint_positions=data_frame.data["applied_joint_positions"]
            )
        )
        self._world.scene.get_object(target_name).set_world_pose(
            position=np.array(data_frame.data["target_position"])
        )
    return
```

軌道再生との違いは、`set_world_pose()` でターゲットの位置も復元している点です。これにより、記録時の環境状態を含めた完全な再生が可能になります。

7. **File > New From Stage Template > Empty** で新しいステージを作成します。

## DataLogger API リファレンス

| メソッド | 説明 |
|---|---|
| `world.get_data_logger()` | World から DataLogger インスタンスを取得 |
| `add_data_frame_logging_func(func)` | 各物理ステップで呼ばれるロギング関数を登録 |
| `start()` | データ記録を開始 |
| `pause()` | データ記録を一時停止 |
| `is_started()` | 記録中かどうかを返す |
| `save(log_path=path)` | 記録データを JSON ファイルに保存 |
| `reset()` | 内部状態をクリア |
| `load(log_path=path)` | JSON ファイルからデータを読み込み |
| `get_num_of_data_frames()` | 記録フレーム数を取得 |
| `get_data_frame(data_frame_index=i)` | 指定インデックスのフレームデータを取得 |

## まとめ

このチュートリアルでは以下のトピックを扱いました：

1. `DataLogger` による**シミュレーションデータの記録**
2. `frame_logging_func` を使った**カスタムデータ項目の定義**
3. **JSON 形式**でのデータ保存とデータ構造
4. **軌道再生**（関節角度のみ）と**シーン再生**（環境状態を含む完全再生）

!!! tip "発展的な使い方"
    `DataLogger` は強化学習のエピソードデータ記録や、シミュレーション結果の定量評価にも活用できます。`frame_logging_func` でカスタムデータを記録することで、さまざまな解析に対応できます。

!!! note "注釈"
    以降のチュートリアルでも主に Extension Workflow を使用して開発を進めます。Standalone Workflow への変換方法は [Hello World](01_hello_world.md) で学んだ手順と同様です。
