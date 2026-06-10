# UseCase レベルにインターフェースを設けない

`ICollectAssetDailyUseCase` / `INotifyWeeklySummaryUseCase` は Application 層に定義されており、実装クラスも同じ Application 層に存在した。これは「インターフェースを消費者（高レベルモジュール）が所有する」という DIP の原則を満たさない。DIP として正しい置き場所は Presentation 層だが、単一実装かつ代替実装の予定がない現時点では過剰な抽象化になる。

インターフェースを削除し、`Presentation.Main` は具体型（`CollectAssetDailyUseCase` / `NotifyWeeklySummaryUseCase`）を直接受け取るよう変更した。

## Considered Options

**却下: Application 層に UseCase インターフェースを残す（現状維持）** — 同一層内の ABC は DIP にならず、形式的な抽象化にとどまる。

**却下: Presentation 層に UseCase インターフェースを移動する** — DIP としては正しいが、代替実装がない現状では YAGNI。代替実装が必要になった時点で導入すれば十分。
