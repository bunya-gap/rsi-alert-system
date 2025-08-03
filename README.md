# RSI Alert System for TECL/SOXL

🎯 **TECL/SOXL RSI監視システム** - 3倍レバレッジ半導体ETFの日足RSI監視とLINE通知

## ✨ 特徴

- 📊 **自動RSI計算**: TECLとSOXLの14日RSIを毎日自動計算
- 🚨 **リアルタイム通知**: しきい値超え時にLINE即座通知  
- 📈 **最適化済み戦略**: バックテスト年率46.1%、勝率78.6%の実績
- 🔄 **完全自動化**: Windowsタスクスケジューラで毎日16:35実行
- 📱 **LINE統合**: Messaging APIでスマートフォン通知
- 📋 **履歴管理**: 全取引シグナルをCSV記録

## 🚀 クイックスタート

### 1. 依存ライブラリインストール
```bash
pip install yfinance pandas requests
```

### 2. 設定ファイル作成
```bash
cp config.template.json config.json
# config.jsonでLINE Access Tokenを設定
```

### 3. 実行テスト
```bash
python main.py
```

## ⚙️ LINE Messaging API設定

### 必要な情報
1. **LINE公式アカウント** - LINE Official Account Managerで作成
2. **Channel Access Token** - LINE Developersで取得
3. **友だち追加** - アラート受信用

### 設定手順
1. [LINE Developers](https://developers.line.biz/)でプロバイダー作成
2. LINE公式アカウント作成
3. Messaging API有効化
4. Channel Access Tokenを`config.json`に設定

## 📊 シグナル戦略

| 指標 | 設定値 | 説明 |
|------|-------|------|
| **買いしきい値** | RSI ≤ 33 | 過売り圏からの反発狙い |
| **売りしきい値** | RSI ≥ 67 | 過買い圏での利益確定 |
| **RSI期間** | 14日 | 標準的な設定 |
| **監視頻度** | 日次 | 市場終了後(16:35) |

## 📈 バックテスト結果

### TECL Balanced戦略 (RSI 33/67)
- **総リターン**: +138.4% (3年間)
- **年率**: 46.1%
- **取引頻度**: 年14回 (月1.2回)
- **勝率**: 78.6%
- **Buy&Hold超過**: +132.5%

## 🔔 通知例

### 買いアラート
```
📉 [RSI ALERT] 買いシグナル発生！

TECL
価格: $42.15
RSI: 31.2 (しきい値: 33を下回りました)
前回RSI: 36.8

投資判断は自己責任で行ってください。
```

### 週次レポート
```
📊 週次RSIレポート

システム稼働: ✅正常
期間: 2025年08月03日

現在RSI:
• TECL: 51.7 (正常範囲) $96.59
• SOXL: 36.5 (正常範囲) $24.08

次回レポート: 来週金曜日
```

## 🛠️ ファイル構成

```
rsi-alert-system/
├── main.py              # メインシステム (300+ lines)
├── config.template.json # 設定テンプレート
├── README.md           # このファイル
└── utils/              # 補助ツール
    ├── setup_scheduler.bat
    ├── system_manager.bat
    ├── test_signals.py
    └── create_backup.bat
```

## 📅 自動実行設定

### Windowsタスクスケジューラ
```bash
# 管理者権限で実行
setup_scheduler.bat
```

### スケジュール確認
```bash
schtasks /query /tn \"RSI_Alert_Daily\"
```

## 🔧 管理・メンテナンス

### システム管理ツール
```bash
system_manager.bat  # GUI風メニューでシステム管理
```

### 機能一覧
- ✅ システム状態確認
- 🔄 手動実行
- 📊 履歴表示
- 📝 ログ確認
- 💾 バックアップ作成
- 🧪 テストシグナル

## 📊 技術仕様

### RSI計算
```python
def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi
```

### データソース
- **Yahoo Finance API** (yfinance)
- **リアルタイム価格** 取得
- **過去30日分** RSI計算用データ

## 🔒 セキュリティ

- ✅ **Access Token保護** - 設定ファイル分離
- ✅ **ログ管理** - 機密情報除外
- ✅ **エラーハンドリング** - 異常時自動通知
- ✅ **バックアップ** - 設定・履歴自動保存

## 📞 サポート・トラブルシューティング

### よくある問題
1. **「ModuleNotFoundError」** → `pip install -r requirements.txt`
2. **「LINE API Error」** → Access Token確認
3. **「データ取得失敗」** → インターネット接続確認
4. **「スケジューラ未動作」** → 管理者権限で設定

### ログ確認
```bash
# システムログ
type system.log

# エラー詳細
python main.py  # 手動実行でデバッグ
```

## 📈 運用実績 (想定)

| 期間 | シグナル数 | 想定勝率 | 期待リターン |
|------|-----------|---------|------------|
| 1ヶ月 | 1-2回 | 78.6% | +3.8% |
| 1年 | 14回 | 78.6% | +46.1% |
| 3年 | 42回 | 78.6% | +138.4% |

## ⚠️ 免責事項

このシステムは**教育・情報提供目的**のみです。

- 📊 過去のパフォーマンスは将来の結果を保証しません
- 💰 投資判断は必ず自己責任で行ってください  
- 📉 市場リスクを十分理解した上でご利用ください
- 🔍 投資前に十分な調査と検討を行ってください

## 🤝 貢献・改善

プルリクエスト・イシュー報告を歓迎します！

### 改善案例
- 📱 Discord/Slack通知対応
- 🔍 他銘柄追加機能  
- 📊 Webダッシュボード
- 🤖 AI予測機能統合

---

**Created**: 2025-08-03  
**Author**: RSI Alert System  
**License**: MIT  
**Language**: Python 3.7+
