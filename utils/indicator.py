from ta.trend import SMAIndicator
import pandas as pd
import numpy as np

def trueRange(data):
    data['PREVIOUS_CLOSE'] = data['CLOSE'].shift(1)
    data['HIGH-LOW'] = abs(data['HIGH'] - data['LOW'])
    data['HIGH-PC'] = abs(data['HIGH'] - data['PREVIOUS_CLOSE'])
    data['LOW-PC'] = abs(data['LOW'] - data['PREVIOUS_CLOSE'])

    tr = data[['HIGH-LOW', 'HIGH-PC', 'LOW-PC']].max(axis=1)

    return tr


def get_ci(df, lookback):
    highh = df['HIGH'].rolling(lookback).max()
    lowl = df['LOW'].rolling(lookback).min()
    df['CI'] = 100 * np.log10((df['TRUERANGE'].rolling(lookback).sum()) / (highh - lowl)) / np.log10(lookback)
    return df


def choppiness(tp, candlestick):
    high = candlestick["HIGH"]
    low = candlestick["LOW"]
    close = candlestick["CLOSE"]
    ATR = candlestick["TRUERANGE"]
    Timestamp = deque()
    CP = deque()
    for i in range(len(candlestick)):
        if i < tp * 2:
            Timestamp.append(candlestick.index[i])
            CP.append(0)
        else:
            nmrt = np.log10(np.sum(ATR[i - tp:i]) / (max(high[i - tp:i]) - min(low[i - tp:i])))
            dnmnt = np.log10(tp)
            Timestamp.append(candlestick.index[i])
            CP.append(round(100 * nmrt / dnmnt))
    CP = pd.DataFrame({"CP": CP}, index=Timestamp)
    return CP


def get_mdd(x):
    """
    MDD(Maximum Draw-Down)
    :return: (peak_upper, peak_lower, mdd rate)
    """
    arr_v = np.array(x)
    # print(arr_v)
    peak_lower = np.argmax(np.maximum.accumulate(arr_v) - arr_v)
    peak_upper = np.argmax(arr_v[:peak_lower])
    return peak_upper, peak_lower, (arr_v[peak_lower] - arr_v[peak_upper]) / arr_v[peak_upper]


def average_true_range(data, period):
    data['TRUERANGE'] = trueRange(data)
    atr = data['TRUERANGE'].rolling(period).mean()
    return atr


def get_pp_center(df):
    center = np.nan
    df['center'] = np.nan
    df['lastpp'] = np.nan
    for current in range(1, len(df.index)):
        previous = current - 1
        df['lastpp'][current] = df['pivothigh'][current] if df['pivothigh'][current] != np.nan else df['pivotlow'][
            current] if df['pivotlow'][current] != np.nan else np.nan
        if df['lastpp'][current] != np.nan:
            if center == np.nan:
                df['center'][current] = df['lastpp'][current]
            else:
                df['center'][current] = (df['center'][current] * 2 + df['lastpp'][current]) / 3
        # elif df['lastpp'][current] == np.nan:
        #   df['center'][current] = df['center'][previous]

    return df['center']


def PivotHigh(df, left, right=0):
    right = right if right else left
    df['pivot'] = None
    for i in range(len(df)):
        if i >= left + right:
            rolling = df['HIGH'][i - right - left:i + 1].values
            m = max(rolling)
            # print(GetTime(df['Time'][i], "%m-%d %H:%M"), df['High'][i-right], m, rolling)
            if df['HIGH'][i - right] == m:
                df['pivot'].values[i] = m
    return df['pivot']


""" the lowest price of pivot point """


def PivotLow(df, left, right=0):
    right = right if right else left
    df['rollingLow'] = df['LOW'].rolling(left + right).min()
    df['pivot'] = None
    for i in range(len(df)):
        if i >= left + right:
            rolling = df['LOW'][i - right - left:i + 1].values
            m = min(rolling)
            if df['LOW'][i - right] == m:
                df['pivot'].values[i] = m
    return df['pivot']


def get_pp_center(df, period):
    pd.set_option('mode.chained_assignment', None)  # <==== 경고를 끈다

    df['pivothigh'] = PivotHigh(df, period, period)
    df['pivotlow'] = PivotLow(df, period, period)

    center = None
    df['center'] = None
    df['lastpp'] = None
    for current in range(1, len(df.index)):
        previous = current - 1
        df['lastpp'][current] = df['pivothigh'][current] if df['pivothigh'][current] != None else df['pivotlow'][
            current] if df['pivotlow'][current] != np.nan else None
        if df['lastpp'][current] != None:
            if center == None:
                center = df['lastpp'][current]
                df['center'][current] = center
            else:
                center = (center * 2 + df['lastpp'][current]) / 3
                df['center'][current] = center
        elif df['lastpp'][current] == None:
            df['center'][current] = center

    return df['center']


def supertrend(df, period=10, atr_multiplier=3, type='Nor', pperiod=1):
    # 무시
    pd.set_option('mode.chained_assignment', None)  # <==== 경고를 끈다
    df['ATR'] = average_true_range(df, period)
    df['IN_UPTREND'] = True
    if type == 'Nor':
        hl2 = (df['HIGH'] + df['LOW']) / 2
        df['UPPERBAND'] = hl2 + (atr_multiplier * df['ATR'])
        df['LOWERBAND'] = hl2 - (atr_multiplier * df['ATR'])
    elif type == 'Pivot':
        df['center'] = get_pp_center(df, pperiod)
        df['UPPERBAND'] = df['center'] + (atr_multiplier * df['ATR'])
        df['LOWERBAND'] = df['center'] - (atr_multiplier * df['ATR'])

    for current in range(1, len(df.index)):
        previous = current - 1

        if df['CLOSE'][current] > df['UPPERBAND'][previous]:
            df['IN_UPTREND'][current] = True
        elif df['CLOSE'][current] < df['LOWERBAND'][previous]:
            df['IN_UPTREND'][current] = False
        else:
            df['IN_UPTREND'][current] = df['IN_UPTREND'][previous]
            if df['IN_UPTREND'][current] == True:
                df['UPPERBAND'][current] = np.nan
            elif df['IN_UPTREND'][current] == False:
                df['LOWERBAND'][current] = np.nan

            if df['IN_UPTREND'][current] and df['LOWERBAND'][current] < df['LOWERBAND'][previous]:
                df['LOWERBAND'][current] = df['LOWERBAND'][previous]
                df['UPPERBAND'][current] = np.nan

            if not df['IN_UPTREND'][current] and df['UPPERBAND'][current] > df['UPPERBAND'][previous]:
                df['UPPERBAND'][current] = df['UPPERBAND'][previous]
                df['LOWERBAND'][current] = np.nan
    return df


# 변동률 구하기
def def_rate(open, close):
    return abs(((close - open) / open) * 100)


# 단계별 구매 수량
def get_buy_amt_list(buy_amt_unit, buy_cnt_limit, increace_rate):
    buy_amt = 0
    buy_amt_list = [0.0]
    for idx in range(0, buy_cnt_limit):
        temp_amt = buy_amt_unit + buy_amt * increace_rate
        buy_amt = round(buy_amt + temp_amt, 4)
        buy_amt_list.append(buy_amt)
    return buy_amt_list


# 손실 최소화 실현 금액 계산
def get_max_loss(close, buy_amt_unit, buy_cnt_limit, increace_rate, max_loss_rate):
    buy_amt = 0  # 누적 구매 수량
    buy_price = 0  # 누적 구매 금액
    for idx in range(0, buy_cnt_limit):
        temp_amt = buy_amt_unit + buy_amt * increace_rate
        buy_price = round(buy_price + close * temp_amt, 4)
        buy_amt = round(buy_amt + temp_amt, 4)
    return round(buy_price * max_loss_rate, 4)


# 평균단가 계산
def get_avrg_price(orgn_price, orgn_amt, buy_price, buy_amt):
    return round(((orgn_price * orgn_amt) + (buy_price * buy_amt)) // (orgn_amt + buy_amt), 4)