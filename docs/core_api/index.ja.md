---
title: Core API チュートリアル
---

# Core API チュートリアル

<span class="badge badge-beginner">Beginner</span>

## 概要

NVIDIA Isaac Simは、NVIDIA Omniverse（より正確には Omniverse Kit）を基盤として構築されたロボティクス向けのリファレンスアプリケーションです。Omniverse上で開発を行う際には、NVIDIA Omniverse™ Kit と Pixar の USD Python API を利用できます。

NVIDIA Omniverse™ Kit は、アプリケーション構築に必要な GUI、拡張機能、実行環境などを提供するツールキットであり、スクリプト作成のための Python インタプリタも備えています。これにより、GUI で実行できる操作の多くに加えて、さまざまな機能を Python API として利用できます。

一方、Pixar の USD Python API は、シーン内のオブジェクト、階層、属性、変換などを操作するための低レベル API を提供します。Isaac Sim のシーンも内部的には USD で表現されているため、必要に応じてこれらの API を直接利用できます。

ただし、Omniverse Kit と USD Python API を横断して扱うには学習コストが高く、手順も煩雑になりがちです。そこで Isaac Sim では、ロボット工学アプリケーション向けの高レベル API 群を提供しており、USD API の複雑さを抽象化し、頻繁に行う処理をより少ない手順で実装できるようにしています。

本チュートリアルでは、コアAPIの概念とその使用方法を紹介します。まず空のステージに立方体を追加することから始め、それを基に複数のロボットが同時に複数のタスクを実行するシーンを構築します（下図参照）。

![チュートリアル目標](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/core_api_tutorials_6_2.webp)

## チュートリアル

<!-- 以下にチュートリアル記事を追加してください -->

!!! example "[チュートリアル 1: Hello World](01_hello_world.md)"
    Core API で定義される World と Scene の作成方法、Stage への剛体追加とシミュレーション方法を学びます。

!!! example "[チュートリアル 2: Hello Robot](02_hello_robot.md)"
    Nucleus サーバーからロボットアセットを読み込み、Robot クラスや WheeledRobot クラスを使ってロボットを制御する方法を学びます。

!!! example "[チュートリアル 3: コントローラの追加](03_adding_a_controller.md)"
    カスタムコントローラの作成方法と、Isaac Sim に用意されている既存コントローラの利用方法を学びます。

!!! example "[チュートリアル 4: マニピュレータロボットの追加](04_adding_a_manipulator_robot.md)"
    Franka Panda マニピュレータのシーンへの追加、ピック＆プレースコントローラ、タスクのモジュール化を学びます。
