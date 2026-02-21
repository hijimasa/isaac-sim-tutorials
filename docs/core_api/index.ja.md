---
title: Core API チュートリアル
---

# Core API チュートリアル

<span class="badge badge-beginner">Beginner</span>

## 概要

NVIDIA Omniverse™ Kitは、NVIDIA Isaac Simがアプリケーション構築に使用するツールキットであり、スクリプト作成用のPythonインタプリタを提供します。これは、すべてのGUIコマンドに加え、多くの追加機能がPython APIとして利用可能であることを意味します。しかし、PixarのUSD Python APIを使用してOmniverse Kitとインターフェースする学習曲線は急峻であり、手順はしばしば煩雑です。そこで我々は、ロボット工学アプリケーションでの使用を想定したAPI群を提供しています。これらのAPIはUSD APIの複雑さを抽象化し、頻繁に実行されるタスクにおいて複数のステップを1つに統合します。

本チュートリアルでは、コアAPIの概念とその使用方法を紹介します。まず空のステージに立方体を追加することから始め、それを基に複数のロボットが同時に複数のタスクを実行するシーンを構築します（下図参照）。

![チュートリアル目標](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/core_api_tutorials_6_2.webp)

## チュートリアル

<!-- 以下にチュートリアル記事を追加してください -->

!!! example "[チュートリアル 1: Hello World](01_hello_world.md)"
    Core API で定義される World と Scene の作成方法、Stage への剛体追加とシミュレーション方法を学びます。

!!! example "チュートリアル 2: USD ステージの操作"
    **準備中** - USD プリム（Prim）の作成・操作方法を学びます。
