import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from csv import *
from implied_volatility_spread_functions import *


# Strategy : Implied Volatility Spread : Stock & Index

# Inputs
stock = r'\Users\Louis\Desktop\Volatilité\Projet Volatilité\Stratégie 1\ABBN.csv'
index = r'\Users\Louis\Desktop\Volatilité\Projet Volatilité\Stratégie 1\SMI.csv'

maturity = 1
in_sample = 250
stdev_trd = 1.5
take_profit_target = 3

date = pd.read_csv(stock)
date = pd.to_datetime(date['12MO_PUT_IMP_VOL'],unit="D",origin=pd.Timestamp('1900-01-01'))


if __name__ == '__main__':

    # Backtest
    strat = BackTestSpread(stock, index, maturity, in_sample, stdev_trd, take_profit_target)
    strat = pd.DataFrame(strat)
    strat[1] = date
    strat.index = strat[1]
    strat.columns = ["strategy_entrances","date","cum_days_strat","bool","pnl"]
    print(strat)


    # Graphic
    fig, axs = plt.subplots(3, sharex=True, figsize=(15, 10))
    plt.suptitle(f"ABBN Stock & SMI Index Implied Volatility Strategy (2010-2021)")

    axs[0].plot(strat["pnl"], color='navy')
    axs[0].axhline(0, color='grey', alpha=0.2)
    axs[0].set_title("Profit & Loss")
    axs[0].set_ylabel("PnL")
    axs[0].spines['left'].set_bounds(-1, 1)
    axs[0].spines['right'].set_visible(False)
    axs[0].spines['top'].set_visible(False)
    axs[0].legend(['PnL'], loc=2)

    axs[1].plot(strat["strategy_entrances"], color='green')
    axs[1].axhline(0, color='grey', alpha=0.2)
    axs[1].set_title("Strategy Entrances")
    axs[1].set_ylabel("Number")
    axs[1].spines['left'].set_bounds(-1, 1)
    axs[1].spines['right'].set_visible(False)
    axs[1].spines['top'].set_visible(False)
    axs[1].legend(['Trades'], loc=2)

    axs[2].plot(strat["bool"], color='green')
    axs[2].axhline(0, color='grey', alpha=0.2)
    axs[2].set_title("Boolean : Enter new strategy if True")
    axs[2].set_ylabel("Boolean Value")
    axs[2].spines['left'].set_bounds(0, 1)
    axs[2].spines['right'].set_visible(False)
    axs[2].spines['top'].set_visible(False)
    axs[2].legend(['True (1) or False (0)'], loc=2)

    plt.show()

