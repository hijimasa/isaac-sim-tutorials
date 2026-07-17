# isaac-sim-tutorials

This is unofficial tutorials for NVIDIA Isaac Sim. MkDocs is used.

NVIDIA Isaac Sim の非公式チュートリアルサイトです。MkDocs (Material theme) で構築しています。

## Development

```bash
pip install -r requirements.txt
mkdocs serve            # ローカルプレビュー
mkdocs build --strict   # ビルド検証（警告ゼロであること）
```

サイトは [mike](https://github.com/jimporter/mike) で複数バージョン（latest / 5.1.0 …）を公開しています。
編集方針・ブランチ運用・Isaac Sim のバージョン更新手順は **[MAINTENANCE.md](MAINTENANCE.md)** を、
更新作業用スクリプトは [tools/](tools/) を参照してください。

## License & Copyright

This site contains sample code and content derived from
[NVIDIA Isaac Sim Documentation](https://docs.isaacsim.omniverse.nvidia.com/).
All sample code, images, and related assets originating from NVIDIA are
copyrighted by **NVIDIA Corporation** and are subject to the
[NVIDIA Software License Agreement](https://www.nvidia.com/en-us/agreements/enterprise-software/nvidia-software-license-agreement/).
The tutorial text and site structure in this repository are provided for
educational purposes only.
