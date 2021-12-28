import datetime
from typing import overload
from numpy import NAN
import pandas as pd

from binance import Client
from api_keys import BINANCE_API_KEY, BINANCE_API_SECRET

client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)

def get_percentage_difference(current, previous):
    if current == previous:
        return 0
    try:
        diff = _float((abs(current - previous) / previous) * 100.0)
        print(diff)
        if current > previous:
            return diff
        return diff * (-1)
    except ZeroDivisionError:
        return float('inf')

def _float(flt):
    return float("{0:.2f}".format(flt))

def generate_insights(df):
    if df.empty:
        return 0, 0, 0, 0, 0
    df["realizedPnl"] = pd.to_numeric(df["realizedPnl"])
    df["commission"] = pd.to_numeric(df["commission"])
    bnb_fee = df[df["commissionAsset"] == "BNB"]
    usd_fee = df[df["commissionAsset"] == "USDT"]
    profit = df[df["realizedPnl"] > 0]
    loss = df[df["realizedPnl"] < 0]

    bnb_fee = bnb_fee["commission"].sum()*530
    usd_fee = usd_fee["commission"].sum()
    fee = bnb_fee+usd_fee
    pnl = df["realizedPnl"].sum()
    profit = profit["realizedPnl"].sum()
    loss = loss["realizedPnl"].sum()
    pnl_fee = pnl-fee
    return _float(pnl), _float(profit), _float(loss), _float(fee), _float(pnl_fee)

def get_df(start_date, end_date=None):
    start_date_timestamp = int(datetime.datetime.strptime(str(start_date), '%Y-%m-%d').timestamp()*1000)
    if end_date:
        end_date_timestamp = int(datetime.datetime.strptime(str(end_date), '%Y-%m-%d').timestamp()*1000)
        df = pd.DataFrame(client.futures_account_trades(startTime=start_date_timestamp, endTime=end_date_timestamp, recvWindow=6000000))
    else: df = pd.DataFrame(client.futures_account_trades(startTime=start_date_timestamp, recvWindow=6000000))
    return df

def get_current_week_df():
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days = today.weekday())
    start_date_timestamp = int(datetime.datetime.strptime(str(start_date), '%Y-%m-%d').timestamp()*1000)
    df = pd.DataFrame(client.futures_account_trades(startTime=start_date_timestamp, recvWindow=6000000))
    return df

def get_previous_week_df():
    today = datetime.date.today()
    start_date = (today - datetime.timedelta(days = today.weekday())) - datetime.timedelta(days=7)
    start_date_timestamp = int(datetime.datetime.strptime(str(start_date), '%Y-%m-%d').timestamp()*1000)
    df = pd.DataFrame(client.futures_account_trades(startTime=start_date_timestamp, recvWindow=6000000))
    return df

def generate_monthly_trades_overview():
    current_date = datetime.date.today()
    monthly_trades_overview = {}
    for i in range(30):
        end_day = current_date + datetime.timedelta(days=1)
        df = get_df(current_date, end_day)
        _, _, _, _, gain = generate_insights(df)
        monthly_trades_overview[str(current_date)] = gain
        # monthly_trades_overview.append(str(current_date))
        # monthly_trades_overview.append(gain)
        # monthly_trades_overview.append("success" if gain > 0 else "error")
        # monthly_trades_overview.append("arrow_upward" if gain > 0 else "arrow_downward")
        current_date = current_date - datetime.timedelta(days=1)

    return monthly_trades_overview

def generate_previous_week_comparison(current_week_df):
    # current_week_df = get_current_week_df()
    previous_week_df = get_previous_week_df()
    _, current_profit, current_loss, current_fee, current_total_gain = generate_insights(current_week_df)
    _, previous_profit, previous_loss, previous_fee, previous_total_gain = generate_insights(previous_week_df)
    gain_diff = get_percentage_difference(current_total_gain, previous_total_gain)
    profit_diff = get_percentage_difference(current_profit, previous_profit)
    loss_diff = get_percentage_difference(current_loss, previous_loss)
    fee_diff = get_percentage_difference(current_fee, previous_fee)
    return {
        "gain_difference": gain_diff,
        "gain_status": "success" if gain_diff > 0 else "error",
        "profit_difference": profit_diff,
        "profit_status": "success" if profit_diff > 0 else "error",
        "loss_difference": loss_diff,
        "loss_status": "success" if loss_diff > 0 else "error",
        "fee_difference": fee_diff,
        "fee_status": "success" if fee_diff > 0 else "error"
        }
    
def generate_yesterday_comparison(trades_overview):
    percentage = get_percentage_difference(trades_overview[1], trades_overview[5])
    return {
        "percentage": percentage,
        "status": "success" if percentage > 0 else "error",
        "icon": "arrow_upward" if percentage > 0 else "arrow_downward"
    }
    
def generate_daily_trades_overview():
    current_date = datetime.date.today()
    trades_overview = []
    for i in range(5):
        end_day = current_date + datetime.timedelta(days=1)
        df = get_df(current_date, end_day)
        _, _, _, _, gain = generate_insights(df)
        trades_overview.append(str(current_date))
        trades_overview.append(gain)
        trades_overview.append("success" if gain > 0 else "error")
        trades_overview.append("arrow_upward" if gain > 0 else "arrow_downward")
        current_date = current_date - datetime.timedelta(days=1)
    return trades_overview
        

def generate_overview():
    overview = {}
    df = get_current_week_df()
    _, profit, loss, fee, total_gain = generate_insights(df)
    weekly_comparison_overview = generate_previous_week_comparison(df)
    trades_overview = generate_daily_trades_overview()
    yesterday_comparison_percentage = generate_yesterday_comparison(trades_overview)
    monthly_trades_overview = generate_monthly_trades_overview()

    overview["weekly_comparison_overview"] = weekly_comparison_overview
    overview["trades_overview"] = trades_overview
    overview["yesterday_comparison_percentage"] = yesterday_comparison_percentage
    overview["monthly_trades_overview"] = monthly_trades_overview
    overview["pnl_overview"] = {
        "profit": profit, 
        "loss": loss,
        "fee": fee,
        "total_gain": total_gain
    }
    return overview

