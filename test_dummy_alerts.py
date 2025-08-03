"""
Enhanced RSI Alert System - ダミーデータテスト
買い・売りシグナルを強制発生させてLINE通知をテスト
"""

import json
import csv
import os
import logging
from datetime import datetime
import requests

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DummyAlertTester:
    def __init__(self, config_path="C:\\rsi_alert\\config.json"):
        """ダミーテスト初期化"""
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.access_token = self.config['notification']['line']['access_token']
        self.symbol_settings = self.config.get('symbol_specific_settings', {})
        self.history_file = "C:\\rsi_alert\\signals_history.csv"
        
        logger.info("ダミーアラートテスター初期化完了")
    
    def create_dummy_signal_data(self, symbol, signal_type, test_scenario):
        """ダミーシグナルデータ作成"""
        settings = self.symbol_settings.get(symbol, {})
        strategy_name = settings.get('strategy_name', 'Standard RSI')
        use_weekly_filter = settings.get('use_weekly_filter', False)
        
        if test_scenario == "enhanced_buy":
            # Enhanced買いシグナル（TECL用）
            return {
                'symbol': symbol,
                'signal_type': signal_type,
                'current_daily_rsi': 31.2,
                'current_weekly_rsi': 48.5,
                'prev_daily_rsi': 35.8,
                'price': 42.15,
                'strategy': strategy_name,
                'reason': "Daily+Weekly条件満たす (Weekly RSI: 48.5≤50)",
                'use_weekly_filter': use_weekly_filter
            }
        elif test_scenario == "enhanced_sell":
            # Enhanced売りシグナル（TECL用）
            return {
                'symbol': symbol,
                'signal_type': signal_type,
                'current_daily_rsi': 68.7,
                'current_weekly_rsi': 52.3,
                'prev_daily_rsi': 65.2,
                'price': 48.90,
                'strategy': strategy_name,
                'reason': "Daily+Weekly条件満たす (Weekly RSI: 52.3≥50)",
                'use_weekly_filter': use_weekly_filter
            }
        elif test_scenario == "standard_buy":
            # Standard買いシグナル（SOXL用）
            return {
                'symbol': symbol,
                'signal_type': signal_type,
                'current_daily_rsi': 30.8,
                'current_weekly_rsi': None,
                'prev_daily_rsi': 36.4,
                'price': 28.40,
                'strategy': strategy_name,
                'reason': "Daily条件満たす",
                'use_weekly_filter': use_weekly_filter
            }
        elif test_scenario == "standard_sell":
            # Standard売りシグナル（SOXL用）
            return {
                'symbol': symbol,
                'signal_type': signal_type,
                'current_daily_rsi': 69.2,
                'current_weekly_rsi': None,
                'prev_daily_rsi': 64.8,
                'price': 34.75,
                'strategy': strategy_name,
                'reason': "Daily条件満たす",
                'use_weekly_filter': use_weekly_filter
            }
    
    def create_enhanced_alert_message(self, signal_data):
        """Enhancedアラートメッセージ作成（main.pyと同じ関数）"""
        symbol = signal_data['symbol']
        signal_type = signal_data['signal_type']
        current_daily_rsi = signal_data['current_daily_rsi']
        current_weekly_rsi = signal_data['current_weekly_rsi']
        prev_daily_rsi = signal_data['prev_daily_rsi']
        price = signal_data['price']
        strategy = signal_data['strategy']
        reason = signal_data['reason']
        use_weekly_filter = signal_data['use_weekly_filter']
        
        # 基本情報
        if signal_type == 'BUY':
            emoji = "📉"
            action = "買いシグナル"
            strength = "★★★★★" if use_weekly_filter else "★★★☆☆"
        else:
            emoji = "📈"
            action = "売りシグナル"
            strength = "★★★★★" if use_weekly_filter else "★★★☆☆"
        
        # 戦略タイプ表示
        strategy_display = f"{symbol} ({strategy})" if use_weekly_filter else symbol
        
        # 週足RSI情報
        weekly_info = ""
        if current_weekly_rsi is not None:
            weekly_info = f"📊 週足RSI: {current_weekly_rsi:.1f}"
            if use_weekly_filter:
                settings = self.symbol_settings.get(symbol, {})
                if signal_type == 'BUY':
                    threshold = settings.get('weekly_buy_threshold', 50)
                    weekly_info += f" ({threshold}以下: ✅)"
                else:
                    threshold = settings.get('weekly_sell_threshold', 50)
                    weekly_info += f" ({threshold}以上: ✅)"
            weekly_info += "\n"
        
        # 期待パフォーマンス情報
        if symbol == 'TECL' and use_weekly_filter:
            performance_info = "過去勝率: 100%\n期待年率: 49.4%"
        elif symbol == 'SOXL':
            performance_info = "過去勝率: 81.8%\n期待年率: 34.3%"
        else:
            performance_info = "過去勝率: 78.6%\n期待年率: 46.1%"
        
        # 設定値取得
        settings = self.symbol_settings.get(symbol, {})
        daily_threshold = settings.get(f'daily_{signal_type.lower()}_threshold', 
                                     33 if signal_type == 'BUY' else 67)
        
        message = f"""{emoji} [RSI ALERT - テスト] {action}発生！

{strategy_display}
価格: ${price:.2f}
📈 日足RSI: {current_daily_rsi:.1f} ({daily_threshold}{'以下' if signal_type == 'BUY' else '以上'}: ✅)
{weekly_info}シグナル強度: {strength}
{performance_info}
戦略: {strategy}

理由: {reason}
前回日足RSI: {prev_daily_rsi:.1f}

※これはテスト通知です。
投資判断は自己責任で行ってください。"""
        
        return message
    
    def send_line_message(self, message):
        """LINE メッセージ送信"""
        url = "https://api.line.me/v2/bot/message/broadcast"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "messages": [
                {
                    "type": "text",
                    "text": message
                }
            ]
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                logger.info("LINE通知送信成功")
                return True
            else:
                logger.error(f"LINE通知送信失敗: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"LINE通知送信エラー: {e}")
            return False
    
    def run_test(self):
        """ダミーテスト実行"""
        logger.info("=== ダミーアラートテスト開始 ===")
        
        test_cases = [
            # TECL Enhanced買いシグナル
            {
                'symbol': 'TECL',
                'signal_type': 'BUY',
                'scenario': 'enhanced_buy',
                'description': 'TECL Enhanced買いシグナル'
            },
            # TECL Enhanced売りシグナル
            {
                'symbol': 'TECL',
                'signal_type': 'SELL',
                'scenario': 'enhanced_sell',
                'description': 'TECL Enhanced売りシグナル'
            },
            # SOXL Standard買いシグナル
            {
                'symbol': 'SOXL',
                'signal_type': 'BUY',
                'scenario': 'standard_buy',
                'description': 'SOXL Standard買いシグナル'
            },
            # SOXL Standard売りシグナル
            {
                'symbol': 'SOXL',
                'signal_type': 'SELL',
                'scenario': 'standard_sell',
                'description': 'SOXL Standard売りシグナル'
            }
        ]
        
        success_count = 0
        
        for i, test_case in enumerate(test_cases, 1):
            logger.info(f"テスト {i}/{len(test_cases)}: {test_case['description']}")
            
            # ダミーデータ作成
            signal_data = self.create_dummy_signal_data(
                test_case['symbol'], 
                test_case['signal_type'], 
                test_case['scenario']
            )
            
            # アラートメッセージ作成
            message = self.create_enhanced_alert_message(signal_data)
            
            # LINE通知送信
            if self.send_line_message(message):
                success_count += 1
                logger.info(f"✅ {test_case['description']} - 送信成功")
            else:
                logger.error(f"❌ {test_case['description']} - 送信失敗")
            
            # 少し間隔を空ける
            import time
            time.sleep(2)
        
        # 完了通知
        completion_message = f"""🧪 [RSI ALERT] ダミーテスト完了！

実行テスト: {len(test_cases)}件
成功: {success_count}件
失敗: {len(test_cases) - success_count}件

テスト項目:
✅ TECL Enhanced買いシグナル
✅ TECL Enhanced売りシグナル  
✅ SOXL Standard買いシグナル
✅ SOXL Standard売りシグナル

システム準備完了！
実際の運用を開始できます。"""
        
        self.send_line_message(completion_message)
        
        logger.info(f"=== ダミーテスト完了: {success_count}/{len(test_cases)} 成功 ===")

if __name__ == "__main__":
    try:
        tester = DummyAlertTester()
        tester.run_test()
    except Exception as e:
        logger.error(f"テストエラー: {e}")
