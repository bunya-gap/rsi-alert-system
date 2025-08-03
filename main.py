import yfinance as yf
import pandas as pd
import json
import csv
import requests
from datetime import datetime, timedelta
import os
import logging

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('C:\\rsi_alert\\system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnhancedRSIAlertSystem:
    def __init__(self, config_path="C:\\rsi_alert\\config.json"):
        """Enhanced RSIアラートシステム初期化"""
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.symbols = self.config['symbols']
        self.rsi_period = self.config['rsi_period']
        self.enhanced_mode = self.config.get('enhanced_mode', False)
        self.symbol_settings = self.config.get('symbol_specific_settings', {})
        
        self.access_token = self.config['notification']['line']['access_token']
        self.history_file = "C:\\rsi_alert\\signals_history.csv"
        
        # 履歴ファイル初期化
        self.init_history_file()
        
        logger.info("Enhanced RSI Alert System initialized")
        logger.info(f"Enhanced Mode: {self.enhanced_mode}")
    
    def init_history_file(self):
        """Enhanced対応履歴ファイルを初期化"""
        if not os.path.exists(self.history_file):
            with open(self.history_file, 'w', newline='') as f:
                writer = csv.writer(f)
                # Enhanced版のヘッダー
                writer.writerow([
                    'date', 'symbol', 'price', 'daily_rsi', 'weekly_rsi', 
                    'signal_type', 'strategy', 'reason', 'prev_daily_rsi'
                ])
            logger.info("Enhanced履歴ファイルを初期化しました")
    
    def calculate_rsi(self, prices, period=14):
        """RSI計算"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def get_stock_data(self, symbol):
        """株価データ取得（日足・週足対応）"""
        try:
            ticker = yf.Ticker(symbol)
            
            # 日足データ取得（過去2ヶ月分、RSI計算に十分）
            daily_hist = ticker.history(period="2mo")
            if daily_hist.empty:
                logger.error(f"{symbol}: 日足データ取得失敗")
                return None
            
            # 週足データ取得（過去6ヶ月分）
            weekly_hist = ticker.history(period="6mo", interval="1wk")
            if weekly_hist.empty:
                logger.warning(f"{symbol}: 週足データ取得失敗")
                weekly_rsi = None
            else:
                weekly_rsi_values = self.calculate_rsi(weekly_hist['Close'], self.rsi_period)
                weekly_rsi = weekly_rsi_values.iloc[-1] if not weekly_rsi_values.empty else None
            
            # 日足RSI計算
            current_price = daily_hist['Close'].iloc[-1]
            daily_rsi_values = self.calculate_rsi(daily_hist['Close'], self.rsi_period)
            daily_rsi = daily_rsi_values.iloc[-1]
            
            weekly_rsi_str = f"{weekly_rsi:.1f}" if weekly_rsi is not None else "N/A"
            logger.info(f"{symbol}: Price=${current_price:.2f}, Daily RSI={daily_rsi:.1f}, Weekly RSI={weekly_rsi_str}")
            
            return {
                'symbol': symbol,
                'price': current_price,
                'daily_rsi': daily_rsi,
                'weekly_rsi': weekly_rsi,
                'date': datetime.now().strftime('%Y-%m-%d')
            }
            
        except Exception as e:
            logger.error(f"{symbol}のデータ取得エラー: {e}")
            return None
    
    def get_previous_data(self, symbol):
        """前回のRSIデータを取得（日足・週足対応）"""
        try:
            if not os.path.exists(self.history_file):
                return None
            
            with open(self.history_file, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                
                # 指定銘柄の最新データを探す
                for row in reversed(rows):
                    if row['symbol'] == symbol:
                        return {
                            'daily_rsi': float(row['daily_rsi']),
                            'weekly_rsi': float(row['weekly_rsi']) if row['weekly_rsi'] != 'None' else None
                        }
                        
                return None
        except Exception as e:
            logger.error(f"前回データ取得エラー: {e}")
            return None
    
    def check_enhanced_signal(self, current_data):
        """Enhanced RSIシグナル判定（銘柄別戦略対応）"""
        symbol = current_data['symbol']
        settings = self.symbol_settings.get(symbol, {})
        
        # デフォルト設定
        daily_buy_threshold = settings.get('daily_buy_threshold', 33)
        daily_sell_threshold = settings.get('daily_sell_threshold', 67)
        use_weekly_filter = settings.get('use_weekly_filter', False)
        strategy_name = settings.get('strategy_name', 'Standard RSI')
        
        current_daily_rsi = current_data['daily_rsi']
        current_weekly_rsi = current_data['weekly_rsi']
        prev_data = self.get_previous_data(symbol)
        
        if prev_data is None:
            logger.info(f"{symbol}: 初回実行、シグナル判定スキップ")
            return None
        
        prev_daily_rsi = prev_data['daily_rsi']
        signal = None
        reason = None
        
        # 日足RSI基本判定
        daily_buy_signal = prev_daily_rsi > daily_buy_threshold and current_daily_rsi <= daily_buy_threshold
        daily_sell_signal = prev_daily_rsi < daily_sell_threshold and current_daily_rsi >= daily_sell_threshold
        
        if daily_buy_signal:
            if use_weekly_filter and current_weekly_rsi is not None:
                # Enhanced mode: 週足フィルター適用
                weekly_buy_threshold = settings.get('weekly_buy_threshold', 50)
                if current_weekly_rsi <= weekly_buy_threshold:
                    signal = 'BUY'
                    reason = f"Daily+Weekly条件満たす (Weekly RSI: {current_weekly_rsi:.1f}≤{weekly_buy_threshold})"
                    logger.info(f"{symbol}: Enhanced買いシグナル発生 (Daily: {current_daily_rsi:.1f}, Weekly: {current_weekly_rsi:.1f})")
                else:
                    reason = f"Weekly RSIフィルターで除外 (Weekly RSI: {current_weekly_rsi:.1f}>{weekly_buy_threshold})"
                    logger.info(f"{symbol}: 買いシグナル候補だが{reason}")
            else:
                # Standard mode: 日足のみ
                signal = 'BUY'
                reason = "Daily条件満たす"
                logger.info(f"{symbol}: Standard買いシグナル発生 (Daily: {current_daily_rsi:.1f})")
        
        elif daily_sell_signal:
            if use_weekly_filter and current_weekly_rsi is not None:
                # Enhanced mode: 週足フィルター適用
                weekly_sell_threshold = settings.get('weekly_sell_threshold', 50)
                if current_weekly_rsi >= weekly_sell_threshold:
                    signal = 'SELL'
                    reason = f"Daily+Weekly条件満たす (Weekly RSI: {current_weekly_rsi:.1f}≥{weekly_sell_threshold})"
                    logger.info(f"{symbol}: Enhanced売りシグナル発生 (Daily: {current_daily_rsi:.1f}, Weekly: {current_weekly_rsi:.1f})")
                else:
                    reason = f"Weekly RSIフィルターで除外 (Weekly RSI: {current_weekly_rsi:.1f}<{weekly_sell_threshold})"
                    logger.info(f"{symbol}: 売りシグナル候補だが{reason}")
            else:
                # Standard mode: 日足のみ
                signal = 'SELL'
                reason = "Daily条件満たす"
                logger.info(f"{symbol}: Standard売りシグナル発生 (Daily: {current_daily_rsi:.1f})")
        
        if signal:
            return {
                'symbol': symbol,
                'signal_type': signal,
                'current_daily_rsi': current_daily_rsi,
                'current_weekly_rsi': current_weekly_rsi,
                'prev_daily_rsi': prev_daily_rsi,
                'price': current_data['price'],
                'strategy': strategy_name,
                'reason': reason,
                'use_weekly_filter': use_weekly_filter
            }
        
        return None
    
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
    
    def create_enhanced_alert_message(self, signal_data):
        """Enhanced アラートメッセージ作成"""
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
        
        message = f"""{emoji} [RSI ALERT] {action}発生！

{strategy_display}
価格: ${price:.2f}
📈 日足RSI: {current_daily_rsi:.1f} ({daily_threshold}{'以下' if signal_type == 'BUY' else '以上'}: ✅)
{weekly_info}シグナル強度: {strength}
{performance_info}
戦略: {strategy}

理由: {reason}
前回日足RSI: {prev_daily_rsi:.1f}

投資判断は自己責任で行ってください。"""
        
        return message
    
    def create_enhanced_weekly_report(self):
        """Enhanced 週次レポート作成"""
        today = datetime.now()
        if today.weekday() != 4:  # 金曜日=4
            return None
        
        # 今週の全データを取得
        report_data = []
        for symbol in self.symbols:
            data = self.get_stock_data(symbol)
            if data:
                report_data.append(data)
        
        if not report_data:
            return None
        
        message = f"""📊 Enhanced週次RSIレポート

システム稼働: ✅正常 (Enhanced Mode)
期間: {today.strftime('%Y年%m月%d日')}

現在RSI状況:"""
        
        for data in report_data:
            symbol = data['symbol']
            daily_rsi = data['daily_rsi']
            weekly_rsi = data['weekly_rsi']
            price = data['price']
            
            settings = self.symbol_settings.get(symbol, {})
            strategy = settings.get('strategy_name', 'Standard RSI')
            use_weekly_filter = settings.get('use_weekly_filter', False)
            
            # RSI状況判定
            buy_threshold = settings.get('daily_buy_threshold', 33)
            sell_threshold = settings.get('daily_sell_threshold', 67)
            
            if daily_rsi <= buy_threshold:
                status = "過売り圏"
            elif daily_rsi >= sell_threshold:
                status = "過買い圏"
            else:
                status = "正常範囲"
            
            weekly_display = f", 週足: {weekly_rsi:.1f}" if weekly_rsi else ""
            strategy_display = " (Enhanced)" if use_weekly_filter else ""
            
            message += f"\n• {symbol}{strategy_display}: 日足 {daily_rsi:.1f} ({status}){weekly_display} ${price:.2f}"
        
        message += f"\n\n📈 期待パフォーマンス:"
        message += f"\n• TECL Enhanced: 年率49.4%, 勝率100%"
        message += f"\n• SOXL Standard: 年率34.3%, 勝率81.8%"
        message += f"\n\n次回レポート: 来週金曜日"
        return message
    
    def save_enhanced_history(self, data, signal_data=None):
        """Enhanced履歴保存"""
        try:
            with open(self.history_file, 'a', newline='') as f:
                writer = csv.writer(f)
                
                # 前回データ取得
                prev_data = self.get_previous_data(data['symbol'])
                prev_daily_rsi = prev_data['daily_rsi'] if prev_data else None
                
                # Enhanced履歴形式で保存
                writer.writerow([
                    data['date'],                                    # date
                    data['symbol'],                                  # symbol
                    f"{data['price']:.2f}",                         # price
                    f"{data['daily_rsi']:.1f}",                     # daily_rsi
                    f"{data['weekly_rsi']:.1f}" if data['weekly_rsi'] else 'None', # weekly_rsi
                    signal_data['signal_type'] if signal_data else 'NONE',         # signal_type
                    signal_data['strategy'] if signal_data else 'N/A',             # strategy
                    signal_data['reason'] if signal_data else 'No signal',         # reason
                    f"{prev_daily_rsi:.1f}" if prev_daily_rsi else 'N/A'          # prev_daily_rsi
                ])
                
        except Exception as e:
            logger.error(f"Enhanced履歴保存エラー: {e}")
    
    def run(self):
        """Enhanced メイン実行"""
        logger.info("=== Enhanced RSIアラートシステム実行開始 ===")
        
        signals_sent = 0
        
        # 各銘柄をチェック
        for symbol in self.symbols:
            logger.info(f"{symbol} Enhanced処理開始")
            
            # データ取得
            current_data = self.get_stock_data(symbol)
            if not current_data:
                continue
            
            # Enhanced シグナル判定
            signal = self.check_enhanced_signal(current_data)
            
            if signal:
                # Enhanced アラート送信
                message = self.create_enhanced_alert_message(signal)
                if self.send_line_message(message):
                    signals_sent += 1
                
                # Enhanced履歴保存
                self.save_enhanced_history(current_data, signal)
            else:
                # 通常時も履歴保存
                self.save_enhanced_history(current_data)
        
        # Enhanced週次レポートチェック
        weekly_message = self.create_enhanced_weekly_report()
        if weekly_message:
            self.send_line_message(weekly_message)
            logger.info("Enhanced週次レポート送信")
        
        logger.info(f"=== Enhanced処理完了: {signals_sent}件のアラート送信 ===")

# 後方互換性のため旧クラス名も維持
RSIAlertSystem = EnhancedRSIAlertSystem

if __name__ == "__main__":
    try:
        system = EnhancedRSIAlertSystem()
        system.run()
    except Exception as e:
        logger.error(f"Enhanced システムエラー: {e}")
        # エラー通知も送信
        error_message = f"⚠️ Enhanced RSIアラートシステムエラー\n\n{str(e)}\n\n管理者に連絡してください。"
        try:
            system = EnhancedRSIAlertSystem()
            system.send_line_message(error_message)
        except:
            pass
