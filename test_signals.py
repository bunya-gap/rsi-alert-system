import json
import sys
import os

def create_test_config():
    \"\"\"テスト用の設定ファイルを作成（しきい値を現在のRSI付近に設定）\"\"\"
    
    config_file = \"config.json\"
    backup_file = \"config_original.json\"
    
    # 現在の設定読み込み
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(\"❌ config.json が見つかりません。config.template.json をコピーして設定してください。\")
        return
    
    # バックアップ作成
    with open(backup_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(\"🔧 テスト用しきい値設定\")
    print(\"現在のRSI想定値: TECL=51.7, SOXL=36.5\")
    print()
    
    mode = input(\"テストモード選択:\\n1. 買いシグナルテスト\\n2. 売りシグナルテスト\\n3. 設定を元に戻す\\n選択 (1-3): \")
    
    if mode == \"1\":
        # 買いシグナルテスト: しきい値を現在RSI+5に設定
        config['buy_threshold'] = 55  # TECL RSI=51.7より少し上
        config['sell_threshold'] = 67
        print(\"✅ 買いシグナルテスト用設定:\")
        print(f\"  買いしきい値: {config['buy_threshold']} (TECL RSIが下がればシグナル)\")
        
    elif mode == \"2\":
        # 売りシグナルテスト: しきい値を現在RSI-5に設定
        config['buy_threshold'] = 33
        config['sell_threshold'] = 30  # SOXL RSI=36.5より少し下
        print(\"✅ 売りシグナルテスト用設定:\")
        print(f\"  売りしきい値: {config['sell_threshold']} (SOXL RSIが上がればシグナル)\")
        
    elif mode == \"3\":
        # 元の設定に戻す
        try:
            with open(backup_file, 'r') as f:
                config = json.load(f)
            print(\"✅ 設定を元に戻しました\")
        except FileNotFoundError:
            config['buy_threshold'] = 33
            config['sell_threshold'] = 67
            print(\"✅ デフォルト設定(33/67)に戻しました\")
    else:
        print(\"❌ 無効な選択です\")
        return
    
    # 設定保存
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f\"\\n📊 現在の設定:\")
    print(f\"  買いしきい値: {config['buy_threshold']}\")
    print(f\"  売りしきい値: {config['sell_threshold']}\")
    print(f\"\\n🚀 次回 'python main.py' 実行時にテスト可能\")

def show_current_config():
    \"\"\"現在の設定を表示\"\"\"
    try:
        with open(\"config.json\", 'r') as f:
            config = json.load(f)
        
        print(\"📊 現在の設定:\")
        print(f\"  監視銘柄: {config['symbols']}\")
        print(f\"  RSI期間: {config['rsi_period']}日\")
        print(f\"  買いしきい値: {config['buy_threshold']}\")
        print(f\"  売りしきい値: {config['sell_threshold']}\")
        print(f\"  週次レポート: {'有効' if config['weekly_report']['enabled'] else '無効'}\")
        
    except FileNotFoundError:
        print(\"❌ config.json が見つかりません\")

if __name__ == \"__main__\":
    if len(sys.argv) > 1 and sys.argv[1] == \"--show\":
        show_current_config()
    else:
        create_test_config()
