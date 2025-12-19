import requests
import time
from datetime import datetime
from threading import Thread
from flask import Flask

# ==================== تنظیمات ====================
BOT_TOKEN = "8421756738:AAFeLglRcghEEBmkESvz-8oHBCznfm5Zt38"  # توکن ربات شما
CHAT_ID = "131349718"                                        # چت آیدی شما

# ==================== Flask برای رندر ====================
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 MarketPlayer Bot - ACTIVE"

Thread(target=lambda: app.run(host='0.0.0.0', port=8080), daemon=True).start()
time.sleep(2)

# ==================== تابع ارسال تلگرام ====================
def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=data, timeout=10)
        print(f"✅ ارسال شد: {datetime.now().strftime('%H:%M:%S')}")
        return True
    except:
        print("❌ خطا در ارسال")
        return False

# ==================== اسکن اسپات حرفه‌ای ====================
def scan_spot():
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        signals = []
        for page in range(1, 13):  # بررسی تا 3000 ارز (12 صفحه 250 تایی)
            params = {
                "vs_currency": "usd",
                "order": "volume_desc",
                "per_page": 250,
                "page": page,
                "sparkline": False
            }
            response = requests.get(url, params=params, timeout=15)
            coins = response.json()
            if not coins:
                break
            for coin in coins:
                symbol = coin.get('symbol', '').upper()
                name = coin.get('name', '')
                price = coin.get('current_price', 0)
                volume = coin.get('total_volume', 0)
                change_1h = coin.get('price_change_percentage_1h_in_currency', 0) or 0
                change_24h = coin.get('price_change_percentage_24h', 0) or 0
                market_cap = coin.get('market_cap', 0)
                if (volume > 25000000 and abs(change_1h) < 1.5 and abs(change_24h) < 10 and market_cap > 10000000):
                    signal = (
                        f"🔥 **SPOT WHALE ALERT** 🔥\n"
                        f"Token: {name} ({symbol})\n"
                        f"Price: ${price:,.4f}\n"
                        f"Volume 24h: ${volume:,.0f}\n"
                        f"Market Cap: ${market_cap:,.0f}\n"
                        f"Change 1h: {change_1h:+.2f}% | Change 24h: {change_24h:+.2f}%\n"
                        f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    )
                    signals.append(signal)
            time.sleep(1)
        return signals[:5]  # فقط ۵ سیگنال برتر
    except Exception as e:
        print(f"خطا در اسکن اسپات: {e}")
        return []

# ==================== اسکن میم‌کوین حرفه‌ای ====================
def scan_meme():
    try:
        url = "https://api.dexscreener.com/latest/dex/tokens"
        response = requests.get(url, timeout=15)
        data = response.json()
        signals = []
        for pair in data.get('pairs', [])[:50]:
            base_symbol = pair.get('baseToken', {}).get('symbol', '').upper()
            base_name = pair.get('baseToken', {}).get('name', '')
            chain = pair.get('chainId', '')
            volume_h1 = pair.get('volume', {}).get('h1', 0)
            price_change_m5 = pair.get('priceChange', {}).get('m5', 0) or 0
            price_change_h1 = pair.get('priceChange', {}).get('h1', 0) or 0
            price = pair.get('priceUsd', 0)
            liquidity = pair.get('liquidity', {}).get('usd', 0)
            dex_url = pair.get('url', '')
            if (volume_h1 > 75000 and abs(price_change_m5) < 2 and abs(price_change_h1) < 8 and liquidity > 50000):
                risk_note = "⚠️ High Risk"
                if liquidity < 100000:
                    risk_note += " - Low Liquidity / Possible Rug Pull"
                signal = (
                    f"🚀 **MEME COIN ALERT** 🚀\n"
                    f"Token: {base_symbol} | Name: {base_name}\n"
                    f"Chain: {chain}\n"
                    f"Price: ${price:.10f}\n"
                    f"Volume 1h: ${volume_h1:,.0f}\n"
                    f"Liquidity: ${liquidity:,.0f}\n"
                    f"Change 5m: {price_change_m5:+.2f}% | Change 1h: {price_change_h1:+.2f}%\n"
                    f"Signal: Volume Spike\n"
                    f"{risk_note}\n"
                    f"Trade: [DEX Link]({dex_url})\n"
                    f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
                signals.append(signal)
        return signals[:5]  # ۵ سیگنال برتر
    except Exception as e:
        print(f"خطا در اسکن میم: {e}")
        return []

# ==================== گزارش دوره‌ای ====================
def send_report(cycle):
    report = (
        f"📊 **DAILY REPORT #{cycle}** 📊\n"
        f"Spot Signals Ready\nMeme Signals Ready\n"
        f"Status: ACTIVE\nNext Scan: 3 min\n"
        f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    send_telegram(report)

# ==================== اسکنر خودکار ====================
def auto_scanner():
    cycle = 0
    send_telegram("🤖 **MarketPlayer Bot ACTIVATED**")
    while True:
        try:
            cycle += 1
            print(f"\n🌀 Cycle #{cycle} - {datetime.now().strftime('%H:%M:%S')}")
            # اسپات
            spot_signals = scan_spot()
            for signal in spot_signals:
                send_telegram(signal)
                time.sleep(2)
            # میم‌کوین
            meme_signals = scan_meme()
            for signal in meme_signals:
                send_telegram(signal)
                time.sleep(2)
            # گزارش هر 10 چرخه
            if cycle % 10 == 0:
                send_report(cycle)
            time.sleep(180)
        except KeyboardInterrupt:
            send_telegram("🛑 Bot Stopped")
            break
        except Exception as e:
            print(f"⚠️ Error: {e}")
            time.sleep(60)

# ==================== اجرا ====================
if __name__ == "__main__":
    scanner_thread = Thread(target=auto_scanner, daemon=True)
    scanner_thread.start()
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        print("\n🛑 Stopping bot...")
