# isaac-sim-tutorials

NVIDIA Isaac Sim 公式チュートリアルを日本語で解説し直す MkDocs サイト（Material + mkdocs-static-i18n suffix 方式 + mike バージョニング）。
公式の誤植・説明不足を補足 note で解消するのがこのサイトの価値。

**詳細な手順・ポリシーは [MAINTENANCE.md](MAINTENANCE.md) を必ず参照**（バージョン更新プレイブック、削除ページ/deprecated ポリシー、ブランチ運用）。
未作成ページ・バックログは [TODO.md](TODO.md) にある。新規ページを作成・完了したら TODO.md のチェックを更新すること。

## ブランチ

- `main` = 最新バージョン（latest）のソース。push で CI が gh-pages の latest を再デプロイ。
- `5.1.0` 等のバージョン名ブランチ = 過去バージョン保守。push でそのバージョンのみ再デプロイ。
- `devel` = 開発用。大規模作業はここで行い main へマージ。
- `gh-pages` = mike 管理。手動編集しない。

## 執筆規約（要点）

- ja を先に完成、en は後追い。core_api / robot_setup / importer_exporter / isaac_lab の en は ja と完全同期。他セクションの en は「Preliminary version」要約版（事実の修正のみ、文量を増やさない）。
- ページ構成: 学習目標 → はじめに（前提条件/所要時間/概要） → `## ステップ N：…`（全角コロン） → まとめ → 次のステップ。既存ページは構成を維持し差分のみ反映。
- `!!! note`（用語解説）/ `!!! warning`（注意）/ `!!! tip`（小技）。サイト独自の補足は「本サイト補足」と明示。
- 日本語見出しへの `#アンカー` リンク禁止。`.en.md` から `.ja.md` への直接リンク禁止。
- 画像は公式 `/latest/_images/` をホットリンク（curl で 200 確認必須）。独自画像は `docs/<section>/images/`。
- 公式ページの正確な本文・コードは `tools/extract_official_page.py`（curl ベース）で取得する。WebFetch は要約されてコードが欠けるため使わない。
- 公式ドキュメント自体の誤記は、正しい内容に直した上で note で公式との差異を明示。
- 新規ページは `mkdocs.yml` の nav（ja / en 両方）へ追加。

## 検証（編集後に実行）

```bash
python3 tools/check_links.py   # 公式 URL の 200 全数チェック
mkdocs build --strict          # 警告ゼロであること（Material 運営告知バナーは無視可）
```

## ツール

- `tools/diff_official_page.py <page.html> --old 5.1.0 --new latest` — 公式ページのバージョン間 diff（更新作業のグラウンドトゥルース）
- `tools/diff_tutorial_list.py` — 公式チュートリアル一覧の増減
- `tools/extract_official_page.py` — 公式ページの本文抽出
