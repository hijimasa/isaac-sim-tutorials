# メンテナンスガイド

本サイトの編集方針・ブランチ運用・バージョン更新の手順をまとめたドキュメントです。
別の PC で作業する場合も、このファイルと `tools/` のスクリプトだけで同じ手順を再現できます。

- 執筆スタイルの要点は [CLAUDE.md](CLAUDE.md) にも要約されています（Claude Code は自動で読み込みます）。
- 実績: 5.1.0 → 6.0.1 移行（2026-07）はこの手順で実施しました。

## 1. サイト構成とブランチ運用

- MkDocs + Material + mkdocs-static-i18n（suffix 方式: `*.ja.md` / `*.en.md`）+ **mike**（バージョニング）。
- 公開サイトは gh-pages ブランチを mike が管理し、`5.1.0/`・`6.0.1/`・`latest`（エイリアス）・`versions.json` を並置。
  ルート URL は latest にリダイレクト。ヘッダーのバージョンセレクタは `mkdocs.yml` の `extra.version.provider: mike` で有効化。

| ブランチ | 役割 | push 時の CI |
|---|---|---|
| `main` | 最新バージョン（latest）のソース | `mike deploy --push --update-aliases $DOCS_VERSION latest` + `set-default latest` |
| `5.1.0`（等、バージョン名ブランチ） | 過去バージョンの保守 | `mike deploy --push $DOCS_VERSION`（そのバージョンのみ再デプロイ） |
| `devel` | 開発用（大規模作業はここで行い main へマージ） | なし |
| `gh-pages` | mike 管理の公開サイト | （手動編集しない） |

- 過去バージョンの修正はバージョン名ブランチへ、最新版の修正は devel → main へ。**それぞれの CI は他バージョンのディレクトリに触れない**ため、両系統を独立して更新できます。
- ローカルからのデプロイも可能: 対象ブランチをチェックアウトして `mike deploy <version>`（latest なら `mike deploy 6.0.1 latest --update-aliases`）→ `git push origin gh-pages`。

## 2. バージョン更新プレイブック（例: 6.0.1 → 7.0）

### Phase 0: 旧バージョンの凍結

1. `main`（= 現行 latest のソース）から保守ブランチを作成: `git checkout -b 6.0.1 origin/main`
2. 保守ブランチの `.github/workflows/deploy.yml` を書き換え:
   - `on.push.branches` をブランチ名（`"6.0.1"`）に
   - `DOCS_VERSION: 6.0.1` に
   - デプロイコマンドを `mike deploy --push "$DOCS_VERSION"` のみに（`latest` エイリアスと `set-default` を付けない）
   - 参考: 現在の `5.1.0` ブランチの deploy.yml がそのままテンプレートになる
3. push すると CI が gh-pages に `6.0.1/` スナップショットを維持し続ける。

### Phase 1: 変更点の調査

1. リリースノートを取得して主要変更（リネーム・削除・deprecated・新機能）を把握:
   `python3 tools/extract_official_page.py https://docs.isaacsim.omniverse.nvidia.com/latest/overview/release_notes.html`
   特に「Breaking changes and deprecations」の表が重要。
2. 移行ガイドの有無を確認: `https://docs.isaacsim.omniverse.nvidia.com/latest/migration_guides/`
   あれば各ガイドを `extract_official_page.py` でテキスト化して保存しておく（担当エージェント/作業者に配る一次資料）。
3. チュートリアル一覧の増減を確認:
   `python3 tools/diff_tutorial_list.py --old 6.0.1 --new latest`
   - 「削除されたページ」→ §3 の削除ページポリシー対象（本当に 404 かは curl で個別確認。移転のこともある）
   - 「追加されたページ」→ 新規作成候補としてリスト化（全部は作らず、まず既存ページ更新を優先）
4. 調査結果を「変更点チートシート」（1 ファイル）にまとめる。含めるもの:
   機械的置換ルール（URL のバージョン部分、バージョン表記）、リネーム/削除/deprecated 一覧、
   移行ガイドの場所、削除ページの扱い、スタイル規約、en 更新ポリシー、報告フォーマット。

### Phase 2: ページ単位の更新

セクションごと（並列作業する場合はファイル担当が重複しないように分割）に、各ページで:

1. ページの元になった公式 URL を特定（ページ内の公式リンクから分かることが多い）。
2. 差分を取得: `python3 tools/diff_official_page.py <ページパス> --old 6.0.1 --new latest`
   - 新バージョンで 404 → tutorial_list で移転先を探し、真に削除なら削除ページポリシー（§3）
   - 差分なし → URL のバージョン置換のみ
3. 差分（コード・手順・メニュー名・パッケージ名・追加/削除された節）を `.ja.md` に反映。
   **既存ページの構成は維持し、差分だけを反映する**（全面書き直しは公式自体が全面改稿された場合のみ）。
4. `.en.md` にも反映（§4 の en ポリシー参照）。
5. 公式リンク・画像 URL のバージョンを更新し、**必ず 200 を確認**。404 なら latest ページの HTML から新しい画像名を探す（`isim_X.Y_...` の版数部分が変わっていることが多い）。

注意事項:

- 公式のコード全面整形（black 化など）は非実質差分として無視し、事実が変わる差分（import・API・値）だけ反映する。
- ユーザー（サイト管理者）が独自に追加した補足・ローカル画像（`docs/*/images/`）・検証注記は**必ず保持**する。
- 「Isaac Sim X.Y で検証」のような検証注記は比較文脈なので旧バージョン表記のまま残してよい。
- 公式側の明らかな誤記を見つけたら、本サイトでは正しい内容に直しつつ `!!! note` で公式との差異を明示（既存ページに前例多数）。

### Phase 3: 検証

```bash
python3 tools/check_links.py          # 公式 URL の全数 200 チェック
mkdocs build --strict                 # リンク切れ・nav 漏れの検出（警告ゼロであること）
grep -rn "docs.isaacsim.omniverse.nvidia.com/6.0.1" docs --include='*.md'   # 旧バージョン URL の残存確認
grep -rn "Isaac Sim 6\.0" docs --include='*.md'                             # 本文の旧バージョン表記の棚卸し
```

残存 URL・表記は、意図的な保持（削除ページの旧画像、比較文脈）かどうかを個別に判断する。

### Phase 4: デプロイ

1. devel → main へマージ。
2. main の `.github/workflows/deploy.yml` の `DOCS_VERSION` を新バージョン（例: 7.0）に更新。
3. push すると CI が `mike deploy 7.0 latest` + `set-default latest` を実行。旧バージョンは gh-pages 上にそのまま残る。
4. トップページ（`docs/index.{ja,en}.md`）の「対応バージョン」info の版数を更新する。

## 3. コンテンツポリシー

### 削除ページの扱い

公式 latest で削除されたチュートリアルに対応する本サイトのページは**削除しない**。
タイトル直後に以下の様式の warning を置き、可能なら公式の代替ページへ誘導する:

```markdown
!!! warning "Isaac Sim X.Y での位置づけ"
    このチュートリアルは Isaac Sim X.Y の公式ドキュメントからは削除されました。
    本ページは旧バージョン時点の内容をもとにした本サイト独自の解説です。
    （使用している API は X.Y では非推奨（deprecated）ですが、引き続き動作します。）
```

### deprecated API の扱い

- 公式ページ自体に Deprecated バナーが付いた場合 → 同趣旨の `!!! warning` をページ冒頭に付け、移行先へのリンクを添える。
- 公式ページが旧 API のままの場合 → 手順は公式に合わせて維持し、「はじめに」等に `!!! note` で移行先を一言添える。

### 過去バージョンブランチへのバックポート

ja/en 共通の誤り修正など、旧バージョンにも当てはまる修正は、バージョン名ブランチへ cherry-pick する
（自動では行わない。修正が新 API 前提でないか確認すること）。

## 4. 執筆スタイル規約（要点）

- ページ構成: `学習目標` → `はじめに`（前提条件/所要時間/概要+番号付きの流れ） → `## ステップ N：…`（全角コロン、`### N-1.` 小節） → `まとめ` → `次のステップ`。
- 用語解説は `!!! note`、注意は `!!! warning`、小技は `!!! tip`。サイト独自の補足は「**本サイト補足**」と明示。
- 日本語（.ja.md）を先に完成させ、英語（.en.md）は後追い。
  - **完全同期セクション**（core_api / robot_setup / importer_exporter / isaac_lab）: ja の差分を英語でも完全反映。
  - **要約版セクション**（ros / synthetic_data / sensors / motion_generation / omnigraph）: 「Preliminary version」の要約版。コード・パッケージ名・URL・バージョン表記など事実が変わる箇所のみ修正し、文量は増やさない。動作確認完了後にセクション単位で完全版化する方針。
- 画像は原則、公式の `https://docs.isaacsim.omniverse.nvidia.com/latest/_images/...` をホットリンク（200 確認必須）。サイト独自のスクリーンショットは `docs/<section>/images/` に置く。
- 日本語見出しへの `#アンカー` リンクは使わない（mkdocs でアンカーが生成されず警告になる）。
- `.en.md` から `.ja.md` へ直接リンクしない（i18n suffix 方式では未解決警告になる。言語切替はセレクタに任せる）。
- 新規ページを作ったら `mkdocs.yml` の nav（ja / en 両方）へ追加する。
- コード超大型ページ（30KB 超）は「構成解説＋鍵コード抜粋＋実行コマンド」形式にし、全文転載しない。

## 5. tools/ スクリプト一覧

| スクリプト | 用途 |
|---|---|
| `tools/extract_official_page.py <URL/ファイル>` | 公式ページの本文・コードをテキスト抽出（WebFetch はコードが欠けるため使わない） |
| `tools/diff_official_page.py <ページパス> --old A --new B` | 公式ページの 2 バージョン間 diff（ページ更新のグラウンドトゥルース） |
| `tools/diff_tutorial_list.py --old A --new B` | チュートリアル一覧の増減（削除/追加ページの洗い出し） |
| `tools/check_links.py [--all]` | docs 内の外部 URL 全数 200 チェック |

いずれも Python 3.9+ と curl のみに依存（MkDocs 環境は `pip install -r requirements.txt`）。
