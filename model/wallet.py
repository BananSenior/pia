from data_source import DataSource

import pandas as pd

class Wallet():
    def __init__(self):
        super().__init__()
        self.assets = []
        self.weights = []

    def add_asset(self, ds: DataSource, weight: float = 1.) -> None:
        self.assets.append(ds)
        self.weights.append(weight)

    @staticmethod
    def _add_period(series: pd.Series, period: pd.DateOffset):
        series.index = series.index.to_timestamp() - period
        series = series.groupby(series.index.to_period("M")).first()
        return series

    @staticmethod
    def _calc_returns(asset: DataSource, period: pd.DateOffset) -> pd.Series:
        price = asset.get_monthly_results()
        price_after_period = Wallet._add_period(price.copy(), period)

        returns = (price_after_period - price)/price

        return returns

    def calc_returns(self, period: pd.DateOffset) -> pd.Series:
        if len(self.assets) == 0:
            raise RuntimeError("No assets defined for this wallet")
        
        result = None
        for asset, weight in zip(self.assets, self.weights):
            res = self._calc_returns(asset, period) * weight
            if result is None:
                result = res
            else:
                result += res
        
        result /= sum(self.weights)

        return result[result.notnull()]

    
if __name__ == "__main__":
    from data_source import Wig20
    wallet = Wallet()
    wallet.add_asset(Wig20())

    gains = wallet.calc_returns(pd.DateOffset(months=60))
    print(f'gains: {gains}')