import strategy.strategy as strategy
import pandas as pd


class BackTester:
    def __init__(
            self,
            data: pd.DataFrame,
            target_strategy: strategy,
            initial_balance: float = 10000,
            maker_fee: float = 0.0002,
            taker_fee: float = 0.0004):
        self.data = data
        self.target_strategy = target_strategy
        self.initial_balance = initial_balance
        self.maker_fee = maker_fee
        self.taker_fee = taker_fee
        self.balance = initial_balance

