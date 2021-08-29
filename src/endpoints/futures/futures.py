from flask import Blueprint, send_file, jsonify
from binance import Client
from src.utils.telegram_client import send_message_to_bot
import pandas as pd
from functools import reduce
from datetime import datetime
import numpy as np

from src.utils.json_helper import read_json
from src.configs import FAVORITE_PAIRS_JSON
from api_keys import BINANCE_API_KEY, BINANCE_API_SECRET

# define the blueprint
futures = Blueprint(name="futures_blueprint", import_name=__name__)

client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)

@futures.route('/get_coin_list', methods=['GET'])
def get_coin_list():
    return send_file("./static/resources/coin_list_futures.json")

@futures.route('/get_favourite_pairs', methods=['GET'])
def get_favourites_list():
    favourite_list = read_json(FAVORITE_PAIRS_JSON)
    return jsonify(favourite_list)

@futures.route('/get_positions', methods=['GET'])
def get_positions():
    position_list = []
    open_orders = client.futures_get_open_orders()
    positions = client.futures_account()["positions"]
    for pos in positions:
        if(float(pos["initialMargin"]) > 0):
            limit, stop = get_limits(open_orders, pos['symbol'])
            pos.pop("positionInitialMargin")
            pos.pop("isolated")
            pos.pop("positionSide")
            pos.pop("isolatedWallet")
            pos.pop("openOrderInitialMargin")
            pos.pop("maintMargin")
            pos['limit'] = limit
            pos['stop_limit'] = stop
            position_list.append(pos)
    # send_message_to_bot()
    get_limits(open_orders, pos["symbol"])
    return jsonify(position_list)

@futures.route('/get_pnl_data', methods=['GET'])
def get_pnl_data():
    df = pd.DataFrame(client.futures_account_trades())
    df.time = df.time.apply(lambda x: str(datetime.fromtimestamp(x/1000).date()))
    df.realizedPnl = df.realizedPnl.apply(lambda x: float(x))
    df = df[(df.realizedPnl) != 0]
    df = df[['symbol', 'realizedPnl', 'time']]
    df_profit = df[df.realizedPnl > 0]
    df_loss = df[df.realizedPnl < 0]
    df_profit = df_profit.rename(columns={'realizedPnl': 'profit'})
    df_loss = df_loss.rename(columns={'realizedPnl': 'loss'})
    df_profit = (df_profit.groupby('time').sum())
    df_loss = (df_loss.groupby('time').sum())
    df_pnl = (df.groupby('time').sum())
    dfs = [df_pnl, df_profit, df_loss]
    df_final = reduce(lambda left,right: left.join(right, how='outer', on='time'), dfs)
    df_final = df_final.replace(np.nan, 0, regex=True)
    final_data = (df_final.to_dict())
    labels = (list(final_data['profit'].keys()))
    profit = (list(final_data['profit'].values()))
    loss = (list(final_data['loss'].values()))
    pnl = (list(final_data['realizedPnl'].values()))
    response = {
        "labels": labels,
        "profit": profit,
        "loss": loss,
        "pnl": pnl 
    }
    return response

def get_limits(open_orders, symbol):
    stop_price = "NA"
    limit_price = "NA"
    for order in open_orders:
        if(order["symbol"] == symbol):
            if(order['type'] != "STOP_MARKET"):
                limit_price = order["price"]
            else:
                stop_price = order["stopPrice"]
    return limit_price, stop_price

