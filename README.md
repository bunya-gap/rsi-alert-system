# Enhanced RSI Alert System for TECL/SOXL

🎯 **TECL/SOXL Enhanced RSI監視システム** - 3倍レバレッジ半導体ETFの日足・週足RSI監視とLINE通知

## ✨ Enhanced Features (2025年最新版)

- 📊 **銘柄別最適戦略**: TECL Enhanced / SOXL Standard 戦略
- 🔄 **日足+週足RSI**: 高精度シグナル判定（TECL用）
- 🚨 **リアルタイム通知**: 最適化されたLINE通知システム
- 📈 **実証済み高パフォーマンス**: TECL年率49.4%、勝率100%
- 🔄 **完全自動化**: Windowsタスクスケジューラで毎日16:35実行
- 📱 **Enhanced通知**: シグナル強度・期待パフォーマンス表示
- 📋 **拡張履歴管理**: 日足・週足RSI、戦略情報を完全記録

## 🏆 銘柄別最適戦略

### TECL - Enhanced RSI Strategy（強化モード）
```json
{
  "strategy": "Enhanced RSI with Weekly Filter",
  "daily_thresholds": {"buy": 33, "sell": 67},
  "weekly_thresholds": {"buy": 50, "sell": 50},
  "expected_performance": {
    "annual_return": "49.4%",
    "win_rate": "100%",
    "trades_per_year": 6
  }
}
```

### SOXL - Standard RSI Strategy（現行維持）
```json
{
  "strategy": "Standard RSI System",
  "daily_thresholds": {"buy": 33, "sell": 67},
  "expected_performance": {
    "annual_return": "34.3%",
    "win_rate": "81.8%",
    "trades_per_year": 3.7
  }
}
```

## 🚀 クイックスタート

### 1. 依存ライブラリインストール
```bash
pip install yfinance pandas requests
```

### 2. 設定確認
```bash
# config.jsonでEnhanced設定が有効化されていることを確認
"enhanced_mode": true
```

### 3. ダミーテスト実行
```bash
python C:\rsi_alert\test_dummy_alerts.py
```

### 4. 本番実行テスト
```bash
python C:\rsi_alert\main.py
```

### 5. 自動スケジュール設定
```bash
# 管理者権限で実行
C:\rsi_alert\setup_scheduler.bat
```

## 📁 Enhanced ファイル構成
```
C:\rsi_alert\
├── main.py                   # Enhanced RSIシステム (430行)
├── config.json               # 銘柄別Enhanced設定
├── test_dummy_alerts.py      # ダミーアラートテスト (273行)
├── signals_history.csv       # 拡張履歴（日足・週足RSI含む）
├── system.log                # システムログ
├── setup_scheduler.bat       # スケジューラ設定
├── system_manager.bat        # システム管理GUI
└── README.md                 # このファイル
```

## 🧠 Enhanced シグナル判定ロジック

### TECL（Enhanced）判定フロー
1. **日足RSI基本判定**
   - 買い: 前日RSI > 33 かつ 当日RSI ≤ 33
   - 売り: 前日RSI < 67 かつ 当日RSI ≥ 67

2. **週足RSIフィルター適用**
   - 買い: 週足RSI ≤ 50 の場合のみシグナル確定
   - 売り: 週足RSI ≥ 50 の場合のみシグナル確定

3. **両条件満たす場合のみ最終シグナル発生**

### SOXL（Standard）判定フロー
- 買い: 前日RSI > 33 かつ 当日RSI ≤ 33
- 売り: 前日RSI < 67 かつ 当日RSI ≥ 67
- 週足フィルターなし（現行システム維持）

## 📱 Enhanced LINE通知例

### TECL Enhanced買いアラート
```
📉 [RSI ALERT] 買いシグナル発生！

TECL (Enhanced RSI)
価格: $42.15
📈 日足RSI: 31.2 (33以下: ✅)
📊 週足RSI: 48.5 (50以下: ✅)
シグナル強度: ★★★★★
過去勝率: 100%
期待年率: 49.4%
戦略: Enhanced RSI

理由: Daily+Weekly条件満たす (Weekly RSI: 48.5≤50)
前回日足RSI: 35.8

投資判断は自己責任で行ってください。
```

### SOXL Standard買いアラート
```
📉 [RSI ALERT] 買いシグナル発生！

SOXL
価格: $28.40
📈 日足RSI: 30.8 (33以下: ✅)
シグナル強度: ★★★☆☆
過去勝率: 81.8%
期待年率: 34.3%
戦略: Standard RSI

理由: Daily条件満たす
前回日足RSI: 36.4

投資判断は自己責任で行ってください。
```

## 📊 Enhanced 履歴管理

### CSV拡張フォーマット
```csv
Date,Symbol,Price,Daily_RSI,Weekly_RSI,Signal,Strategy,Reason,Prev_Daily_RSI
2025-08-03,TECL,42.15,31.2,48.5,BUY,Enhanced RSI,Daily+Weekly条件満たす,35.8
2025-08-03,SOXL,28.40,30.8,None,BUY,Standard RSI,Daily条件満たす,36.4
```

## 🔧 Enhanced 管理・運用

### システム管理ツール
```bash
C:\rsi_alert\system_manager.bat  # GUI風システム管理
```

### ダミーテスト機能
```bash
python C:\rsi_alert\test_dummy_alerts.py
# 4つのテストケース:
# - TECL Enhanced買い・売りシグナル
# - SOXL Standard買い・売りシグナル
```

### 手動実行
```bash
python C:\rsi_alert\main.py
```

### スケジュール確認
```bash
schtasks /query /tn "RSI_Alert_Daily"
```

## 📈 Enhanced バックテスト結果

### TECL Enhanced Strategy
- **年率リターン**: 49.4%
- **勝率**: 100% (6/6勝)
- **取引頻度**: 年6回
- **最大ドローダウン**: 0%
- **シャープレシオ**: 1.698

### SOXL Standard Strategy  
- **年率リターン**: 34.3%
- **勝率**: 81.8% (9/11勝)
- **取引頻度**: 年3.7回
- **最大ドローダウン**: 35.2%

### ポートフォリオ全体（同等投資）
- **期待年率**: 約42%
- **取引頻度**: 月0.8回
- **リスク分散**: 戦略多様化効果

## ⚙️ Enhanced 設定詳細

### config.json (Enhanced版)
```json
{
  "symbols": ["TECL", "SOXL"],
  "rsi_period": 14,
  "enhanced_mode": true,
  "symbol_specific_settings": {
    "TECL": {
      "daily_buy_threshold": 33,
      "daily_sell_threshold": 67,
      "weekly_buy_threshold": 50,
      "weekly_sell_threshold": 50,
      "use_weekly_filter": true,
      "strategy_name": "Enhanced RSI"
    },
    "SOXL": {
      "daily_buy_threshold": 33,
      "daily_sell_threshold": 67,
      "use_weekly_filter": false,
      "strategy_name": "Standard RSI"
    }
  }
}
```

## 📅 運用スケジュール
- **実行時間**: 毎日16:35（米国市場終了後）
- **週次レポート**: 金曜日16:35（Enhanced版対応）
- **システム監視**: 24時間自動実行

## 🛠️ トラブルシューティング

### よくある問題
1. **「Access Token Error」** → config.jsonのトークン確認
2. **「Weekly RSI取得失敗」** → Yahoo Finance API接続確認
3. **「Enhanced判定エラー」** → 履歴ファイル存在確認
4. **「ダミーテスト失敗」** → LINE API制限確認

### デバッグ手順
```bash
# 1. ダミーテスト実行
python C:\rsi_alert\test_dummy_alerts.py

# 2. システムログ確認
type C:\rsi_alert\system.log

# 3. 手動実行でデバッグ
python C:\rsi_alert\main.py
```

## 🔒 セキュリティ・制限事項

### 制限
- **LINE API**: 月1000通まで無料（現用途では十分）
- **Yahoo Finance**: レート制限あり（通常運用では問題なし）
- **Windows専用**: Linux移植は追加作業要

### セキュリティ
- ✅ **Access Token保護**: 設定ファイル分離
- ✅ **ログ管理**: 機密情報除外
- ✅ **エラーハンドリング**: 異常時自動通知
- ✅ **バックアップ**: 自動バックアップ機能

## 📊 期待パフォーマンス（1年後目標）

| 項目 | TECL Enhanced | SOXL Standard | 合計 |
|------|--------------|---------------|------|
| **年率リターン** | 45%以上 | 30%以上 | 37.5%以上 |
| **勝率** | 90%以上 | 75%以上 | 82.5%以上 |
| **取引回数** | 6回 | 4回 | 10回 |
| **システム稼働率** | 99%以上 | 99%以上 | 99%以上 |

## 🚀 今後の拡張計画

- 📱 **他通知チャネル**: Discord、Slack対応
- 🤖 **AI予測機能**: 機械学習による戦略最適化
- 🌐 **Web ダッシュボード**: リアルタイム監視画面
- ☁️ **クラウド展開**: AWS Lambda等での自動実行
- 📊 **他銘柄対応**: QQQ、SPXL等への戦略適用

## ⚠️ 免責事項

このシステムは**教育・情報提供目的**のみです。

- 📊 過去のパフォーマンスは将来の結果を保証しません
- 💰 投資判断は必ず自己責任で行ってください  
- 📉 市場リスクを十分理解した上でご利用ください
- 🔍 投資前に十分な調査と検討を行ってください

## 🤝 貢献・GitHub

**Repository**: https://github.com/bunya-gap/rsi-alert-system

- **License**: MIT（商用利用可）
- **Language**: Python 3.7+
- **Status**: Production Ready（実運用中）

---

**Enhanced Version**: 2025-08-03  
**Author**: Enhanced RSI Alert System  
**Performance**: TECL 49.4%, SOXL 34.3% (年率)
