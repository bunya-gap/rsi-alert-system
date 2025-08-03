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
        logging.FileHandler('system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RSIAlertSystem:
    def __init__(self, config_path="config.json"):
        """RSIアラートシステム初期化"""
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.symbols = self.config['symbols']
        self.rsi_period = self.config['rsi_period']
        self.buy_threshold = self.config['buy_threshold']
        self.sell_threshold = self.config['sell_threshold']
        
        self.access_token = self.config['notification']['line']['access_token']
        self.history_file = "signals_history.csv"
        
        # 履歴ファイル初期化
        self.init_history_file()
    
    def init_history_file(self):
        """履歴ファイルを初期化"""
        if not os.path.exists(self.history_file):
            with open(self.history_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['date', 'symbol', 'price', 'rsi', 'signal_type', 'prev_rsi'])
            logger.info("履歴ファイルを初期化しました")
    
    def calculate_rsi(self, prices, period=14):
        """RSI計算"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def get_stock_data(self, symbol):
        """株価データ取得"""
        try:
            ticker = yf.Ticker(symbol)
            # 過去30日分のデータを取得（RSI計算に十分）
            hist = ticker.history(period="1mo")
            
            if hist.empty:
                logger.error(f"{symbol}: データ取得失敗")
                return None
            
            current_price = hist['Close'].iloc[-1]
            rsi_values = self.calculate_rsi(hist['Close'], self.rsi_period)
            current_rsi = rsi_values.iloc[-1]
            
            logger.info(f"{symbol}: Price=${current_price:.2f}, RSI={current_rsi:.1f}")
            
            return {
                'symbol': symbol,
                'price': current_price,
                'rsi': current_rsi,
                'date': datetime.now().strftime('%Y-%m-%d')
            }
            
        except Exception as e:
            logger.error(f"{symbol}のデータ取得エラー: {e}")
            return None
    
    def get_previous_rsi(self, symbol):
        """前回のRSI値を取得"""
        try:
            if not os.path.exists(self.history_file):
                return None
            
            with open(self.history_file, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                
                # 指定銘柄の最新データを探す
                for row in reversed(rows):
                    if row['symbol'] == symbol:
                        return float(row['rsi'])
                        
                return None
        except Exception as e:
            logger.error(f"前回RSI取得エラー: {e}")
            return None
    
    def check_signal(self, current_data):
        """シグナル判定"""
        symbol = current_data['symbol']
        current_rsi = current_data['rsi']
        prev_rsi = self.get_previous_rsi(symbol)
        
        if prev_rsi is None:
            logger.info(f"{symbol}: 初回実行、シグナル判定スキップ")
            return None
        
        signal = None
        
        # 買いシグナル: 上から下へしきい値を下回った
        if prev_rsi > self.buy_threshold and current_rsi <= self.buy_threshold:
            signal = 'BUY'
            logger.info(f"{symbol}: 買いシグナル発生 (RSI: {current_rsi:.1f})")
        
        # 売りシグナル: 下から上へしきい値を上回った
        elif prev_rsi < self.sell_threshold and current_rsi >= self.sell_threshold:
            signal = 'SELL'
            logger.info(f"{symbol}: 売りシグナル発生 (RSI: {current_rsi:.1f})")
        
        if signal:
            return {
                'symbol': symbol,
                'signal_type': signal,
                'current_rsi': current_rsi,
                'prev_rsi': prev_rsi,
                'price': current_data['price']
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
    
    def create_alert_message(self, signal_data):
        """アラートメッセージ作成"""
        symbol = signal_data['symbol']
        signal_type = signal_data['signal_type']
        current_rsi = signal_data['current_rsi']
        prev_rsi = signal_data['prev_rsi']
        price = signal_data['price']
        
        if signal_type == 'BUY':
            emoji = "📉"
            action = "買いシグナル"
            direction = "下回りました"
            threshold = self.buy_threshold
        else:
            emoji = "📈"
            action = "売りシグナル"
            direction = "上回りました"
            threshold = self.sell_threshold
        
        message = f"""{emoji} [RSI ALERT] {action}発生！

{symbol}
価格: ${price:.2f}
RSI: {current_rsi:.1f} (しきい値: {threshold}を{direction})
前回RSI: {prev_rsi:.1f}

投資判断は自己責任で行ってください。"""
        
        return message
    
    def create_weekly_report(self):
        """週次レポート作成"""
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
        
        message = f"""📊 週次RSIレポート

システム稼働: ✅正常
期間: {today.strftime('%Y年%m月%d日')}

現在RSI:"""
        
        for data in report_data:
            symbol = data['symbol']
            rsi = data['rsi']
            price = data['price']
            
            # RSI状況判定
            if rsi <= self.buy_threshold:
                status = "過売り圏"
            elif rsi >= self.sell_threshold:
                status = "過買い圏"
            else:
                status = "正常範囲"
            
            message += f"\n• {symbol}: {rsi:.1f} ({status}) ${price:.2f}"
        
        message += f"\n\n次回レポート: 来週金曜日"
        return message
    
    def save_to_history(self, data, signal_type=None):
        """履歴保存"""
        try:
            with open(self.history_file, 'a', newline='') as f:
                writer = csv.writer(f)
                prev_rsi = self.get_previous_rsi(data['symbol'])
                writer.writerow([
                    data['date'],
                    data['symbol'],
                    f"{data['price']:.2f}",
                    f"{data['rsi']:.1f}",
                    signal_type or 'NONE',
                    f"{prev_rsi:.1f}" if prev_rsi else 'N/A'
                ])
        except Exception as e:
            logger.error(f"履歴保存エラー: {e}")
    
    def run(self):
        """メイン実行"""
        logger.info("=== RSIアラートシステム実行開始 ===")
        
        signals_sent = 0
        
        # 各銘柄をチェック
        for symbol in self.symbols:
            logger.info(f"{symbol} 処理開始")
            
            # データ取得
            current_data = self.get_stock_data(symbol)
            if not current_data:
                continue
            
            # シグナル判定
            signal = self.check_signal(current_data)
            
            if signal:
                # アラート送信
                message = self.create_alert_message(signal)
                if self.send_line_message(message):
                    signals_sent += 1
                
                # 履歴保存
                self.save_to_history(current_data, signal['signal_type'])
            else:
                # 通常時も履歴保存
                self.save_to_history(current_data)
        
        # 週次レポートチェック
        weekly_message = self.create_weekly_report()
        if weekly_message:
            self.send_line_message(weekly_message)
            logger.info("週次レポート送信")
        
        logger.info(f"=== 処理完了: {signals_sent}件のアラート送信 ===")

if __name__ == "__main__":
    try:
        system = RSIAlertSystem()
        system.run()
    except Exception as e:
        logger.error(f"システムエラー: {e}")
        # エラー通知も送信
        error_message = f"⚠️ RSIアラートシステムエラー\n\n{str(e)}\n\n管理者に連絡してください。"
        try:
            system = RSIAlertSystem()
            system.send_line_message(error_message)
        except:
            pass
