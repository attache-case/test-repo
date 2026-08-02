# test-repo — Pokémon TCG AI Battle Challenge ベースライン

Kaggle コンペティション「The Pokémon Company - PTCG AI Battle Challenge」の
**Simulation カテゴリ**向けエージェントと、**Strategy カテゴリ**向けレポートの
ベースライン実装です。

## 何を作ったか

公式ゲームエンジン（`kaggle_environments` に同梱された `cabt` 環境、実体は
`libcg.so` を `ctypes` 経由で呼び出すもの）が内部に持つ探索用 API
（`SearchBegin` / `SearchStep` / `SearchEnd` など）をリバースエンジニアリングし、
それを使って **PIMC（Perfect Information Monte Carlo）** 方式の先読み探索を行う
エージェントを実装しました。ルール判定は常に本物のエンジンに委譲するため、
不正な行動を返すことがなく、隠れ情報（相手の手札・山札・自分の未ドロー分）を
ランダムに具体化（determinization）した上で候補手ごとに複数回プレイアウトし、
平均スコアが最も高い手を選びます。

- `ptcg_ai/agent/main.py` — Kaggle 提出用の単一ファイルエージェント
  （`agent(obs)` がエントリポイント。ファイル内で最後に定義されたトップレベル
  関数である必要があるという kaggle-environments の制約を満たしています）。
- `ptcg_ai/eval/run_eval.py` / `ptcg_ai/eval/smoke_test.py` — ローカル評価スクリプト。
- `ptcg_ai/report/strategy_report.md` — Strategy カテゴリ提出用レポート（英語、
  2000 語以内）。

既存のリポジトリ内容（SQL バックアップファイルや `dir/` 以下など）には
一切手を加えていません。

## リポジトリ構成

```
.
├── README.md                          # このファイル
├── 2018-11-14-1.0.10J-r2_database_backup.sql   # 既存ファイル（変更なし）
├── dir/                                # 既存ファイル（変更なし）
└── ptcg_ai/
    ├── agent/
    │   └── main.py                    # Kaggle 提出用エージェント本体
    ├── eval/
    │   ├── run_eval.py                # N 戦の対戦評価スクリプト
    │   └── smoke_test.py              # 1 戦だけの疎通確認スクリプト
    └── report/
        └── strategy_report.md         # Strategy カテゴリ提出用レポート（英語）
```

## ローカル実行方法

`kaggle-environments` がインストール済みの Python 3.11 venv
（`/home/user/venv-ptcg`）を使う想定です。自分で環境を作る場合は以下の手順です。

```bash
python3.11 -m venv venv-ptcg
source venv-ptcg/bin/activate
pip install kaggle-environments
```

以降、このリポジトリ内の全スクリプトは **必ずこの venv の Python** で実行してください
（`kaggle-environments` が入っていない通常の `python3` では動きません）。

## 評価の実行方法と結果

疎通確認（1 戦のみ、エージェント vs 組み込み `random` エージェント）:

```bash
/home/user/venv-ptcg/bin/python ptcg_ai/eval/smoke_test.py
```

`ERROR` / `INVALID` / `TIMEOUT` が一切発生せず `DONE` で終了することを確認します。

複数戦の勝率評価（デフォルト 20 戦、`--games` で変更可、相手は `--opponent random|first`）:

```bash
/home/user/venv-ptcg/bin/python ptcg_ai/eval/run_eval.py --games 20
```

先手・後手を 1 戦ごとに入れ替えながら対戦し、勝敗・引き分け数・勝率・平均報酬・
所要時間（ウォールクロック）を出力します。

### 実測結果（このリポジトリでの検証結果）

対 `random` エージェント、`INVALID` / `ERROR` / `TIMEOUT` は **0 件**（全戦 `DONE`）。

| 実行 | 対戦数 | 勝ち | 負け | 引分 | 勝率 | 所要時間 |
|---|---:|---:|---:|---:|---:|---:|
| 1 回目 | 20 | 16 | 4 | 0 | 80.0% | 約 36 秒（約 1.8 秒/戦） |
| 2 回目（より多い対戦数での再検証） | 40 | 38 | 2 | 0 | 95.0% | 約 64 秒（約 1.6 秒/戦） |

ベースラインの合格基準（対 `random` で 20 戦以上・勝率 80% 以上）を両方の実行で
達成しています。1 回目が 2 回目よりやや低いのは、探索・プレイアウトが確率的な
モンテカルロ法であることによる自然なばらつきです。20 戦・40 戦とも
`ERROR` / `INVALID` / `TIMEOUT` は発生していません。

## Kaggle への提出方法

- **Simulation カテゴリ**: `ptcg_ai/agent/main.py` をそのまま提出します。
  標準ライブラリと `kaggle_environments` のみに依存する単一ファイルで、
  実行時に外部ファイルを一切読み込みません。
- **Strategy カテゴリ**: `ptcg_ai/report/strategy_report.md`
  （英語、2000 語以内）を提出します。モデルのアプローチ（探索アルゴリズム、
  determinization、候補手列挙、プレイアウト方策、リーフ評価、時間管理、
  フォールバック）、デッキコンセプト、限界と今後の改善案（ISMCTS + UCB、
  相手デッキ推定、学習済みプレイアウト/価値関数など）をまとめています。

## 検証済み Search API の要約

`kaggle_environments.envs.cabt.cg.sim` の `lib`（`libcg.so` の ctypes ラッパー）が
公開している、探索用の内部関数群です（`ptcg_ai/agent/main.py` 内で実際に使用）。

- `AgentStart() -> ctx`: 探索用コンテキストをプロセスごとに 1 回作成し使い回す。
- `SearchBegin(ctx, search_begin_input, len, myDeck, myPrize, oppDeck, oppPrize,
  oppHand, spare, flag=0)`: 現在の `obs` を起点に、隠れゾーンを具体化した状態で
  探索セッションを開始する。渡す 6 本の int 配列の長さは、それぞれの実際の
  ゾーンの枚数（`deckCount`、`prize[]` 中の `null` の数、相手の `handCount` など）
  と厳密に一致していないと `error: 1` になる。成功すると根ノードが
  **ハンドル 0** として割り当てられ、その `select` は現在の実際の `obs["select"]`
  と一致する。
- `SearchStep(ctx, handle, action_indices, n)`: 指定したハンドルの状態に対して
  選択（`select["option"]` へのインデックス列）を適用し、新しい状態を返す。
  ハンドルは直前の `SearchEnd` 以降、`SearchBegin` / `SearchStep` の成功のたびに
  **0, 1, 2, ... と連番で採番**され、**同じハンドルは 1 回しかステップできない**
  （不正な行動や再ステップは `error: 4` または `5` を返すだけで、その行動を
  別のものに変えて再試行すればよい）。
- `SearchEnd(ctx)`: それまでに確保した全状態を解放し、ハンドル採番を 0 に
  リセットする。本実装では **プレイアウト 1 回ごとに** `try/finally` で必ず
  呼び出しており、これにより各プレイアウトが独立してハンドル 0 から
  始まることを保証している（`SearchEnd` を挟まずに `SearchBegin` を連続で
  呼ぶと、根ノードのハンドルが 0 以外になってしまうので要注意）。
- `SearchRelease(ctx, handle)`: 個別ハンドルのみを解放する API（バインドのみ、
  本ベースラインでは未使用）。

実測スループット（シングルスレッド）: `SearchStep` 約 18,000 回/秒、
完全ランダムプレイアウト 約 195 回/秒。これにより 1 手あたり 1 秒未満の
予算内で複数候補 × 複数 determinization のロールアウトが可能になっています。
