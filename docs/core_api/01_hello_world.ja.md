---
title: Hello World
---

# Hello World

## 学習目標

このチュートリアルを修了すると、以下の内容を習得できます:

- Core API で定義される World と Scene の作成方法
- Stage に剛体(rigid body)を追加し、NVIDIA Isaac Sim で Python を使用してシミュレーションする方法
- Extension Workflow と Standalone Workflow、および Jupyter Notebook での Python 実行の違い

## はじめに

**前提条件**

- このチュートリアルには、Pythonおよび非同期プログラミングの中級レベルの知識が必要です。
- チュートリアルを開始する前に、[Visual Studio Code](https://code.visualstudio.com/download)をダウンロードしてインストールしてください。
- チュートリアルを開始する前に、クイックチュートリアルおよびワークフローを確認してください。

まず、Hello Worldサンプルを開きます。

1. **Windows** > **Examples** > **Robotics Examples**をアクティブにして、Robotics Examplesタブを開きます。

   ![robotics_example_place](images/01_robotics_example_place.png)

2. **Robotics Examples** > **General** > **Hello World** をクリックします。

   ![hello_world_place](images/02_hello_world_place.png)

3. ワークスペースにHello Worldサンプル拡張機能のウィンドウが表示されていることを確認してください。
4. ソースコードを開くボタンをクリックし、Visual Studio Codeで編集可能なソースコードを起動します。
5. フォルダを開くボタンをクリックし、サンプルファイルを含むディレクトリを開きます。

このフォルダには以下の3つのファイルが含まれています：hello_world.py、hello_world_extension.py、および__init__.py

hello_world.pyスクリプトにはアプリケーションのロジックを追加し、アプリケーションのUI要素はhello_world_extension.pyスクリプトに追加してロジックとリンクさせます。

1. LOADボタンをクリックしてワールドを読み込みます。
2. ファイル > ステージテンプレートから新規作成 > 空をクリックして新しいステージを作成し、現在のステージを保存するかどうかの確認で保存しないをクリックします。
3. LOADボタンをクリックしてワールドを再度読み込みます。
4. hello_world.pyを開き「Ctrl+S」を押してホットリロード機能を使用します。ワークスペースからメニューが消えていることに気付くでしょう（再起動されたためです）。
5. 例示メニューを再度開き、LOADボタンをクリックします。

これでこの例への追加を開始できます。

## コード概要

この例はBaseSampleを継承しています。BaseSampleは、あらゆるロボティクス拡張アプリケーションの基本設定を行う定型拡張アプリケーションです。BaseSampleが実行するアクションの例をいくつか挙げます：

1. ボタンを使用して対応するアセットと共にワールドを読み込みます。
2. 新しいステージ作成時にワールドをクリアする。
3. ワールド内のオブジェクトをデフォルト状態にリセットする。
4. ホットリロードを処理する。

World は、シミュレータと容易かつモジュール化された方法で対話することを可能にする中核クラスです。コールバックの追加、物理演算のステップ実行、シーンのリセット、タスクの追加（詳細は後述のマニピュレータロボットの追加で説明）など、多くの時間関連イベントを処理します。
ワールドはSceneのインスタンスを含みます。SceneクラスはUSDのStage内で対象となるシミュレーションアセットを管理します。ステージ内の様々なUSDアセットを追加・操作・検査・リセットするための簡易APIを提供します。

```python
from isaacsim.examples.interactive.base_sample import BaseSample #boiler plate of a robotics extension application

class HelloWorld(BaseSample):
    def __init__(self) -> None:
        super().__init__()
        return

    # This function is called to setup the assets in the scene for the first time
    # Class variables should not be assigned here, since this function is not called
    # after a hot-reload, its only called to load the world starting from an EMPTY stage
    def setup_scene(self):
        # A world is defined in the BaseSample, can be accessed everywhere EXCEPT __init__
        world = self.get_world()
        world.scene.add_default_ground_plane() # adds a default ground plane to the scene
        return
```

## まとめ
このチュートリアルでは以下のトピックを扱いました：

1. WorldおよびSceneクラスの概要
2. PythonによるSceneへのコンテンツ追加
3. コールバックの追加
4. オブジェクトの動的プロパティへのアクセス
5. スタンドアロンアプリケーションにおける主な違い

## 次のステップ
Hello Robotに進み、シミュレーションにロボットを追加する方法を学びましょう。

!!! note "注釈"
    次のチュートリアルでは主に拡張機能アプリケーションワークフローを使用して開発を進めます。ただし、本チュートリアルで扱った内容を踏まえれば、他のワークフローへの変換も同様の手順で行えます。