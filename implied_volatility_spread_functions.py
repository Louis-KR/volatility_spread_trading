import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from csv import *
from math import *
from random import *


class EuropeanCall:
    strike = 100.0
    spot = 100.0
    maturity = 1.0

    def __init__(self, strike, my_underlying, maturity):
        self.strike = strike
        self.spot = my_underlying.spot
        self.maturity = maturity

    def bs_price(self, vol, r):
        d1 = (log(self.spot/self.strike)+self.maturity*(r+vol*vol/2))/(vol*sqrt(self.maturity))
        d2 = d1 - vol*sqrt(self.maturity)
        return phi(d1)*self.spot-phi(d2)*self.strike*exp(-r*self.maturity)

    def bs_delta(self, vol, r):
        d1 = (log(self.spot/self.strike)+self.maturity*(r+vol*vol/2))/(vol*sqrt(self.maturity))
        return phi(d1)

    def bs_vega(self, vol, r):
        d1 = (log(self.spot/self.strike)+self.maturity*(r+vol*vol/2))/(vol*sqrt(self.maturity))
        return self.spot*sqrt(self.maturity)*exp(-(d1*d1)/2)/sqrt(2*pi)/100


class Underlying:
    spot = 100.0
    ticker = "SX5E"

    def __init__(self, spot, ticker):
        self.spot = spot
        self.ticker = ticker


def generate_random_numbers(n):
    d = [random()]
    for i in range(n-1):
        d.append(random())
    return d


def generate_normal_random_numbers(n):
    d = []
    for i in range(n):
        d.append(gauss(0, 1))
        #d.append(-d[2*i])
    return d


def generate_multivar_normal_random_numbers(n, rho):
    d = generate_normal_random_numbers(n*2)
    dout = []
    for i in range(round(d.__len__()/2)):
        dtemp = [0, 0]
        dtemp[0] = d[i]
        dtemp[1] = rho*d[i]+sqrt(1-rho*rho)*d[round(d.__len__()/2)+i]
        dout.append(dtemp)
    return dout


def phi(x):
    #'Cumulative distribution function for the standard normal distribution'
    return (1.0 + erf(x / sqrt(2.0))) / 2.0


from csv import writer

def import_histo_prices_csv(path):
    historical_prices = []
    csv_file = open(path)
    csv_reader = reader(csv_file, delimiter=',')
    i = 0
    for row in csv_reader:
        price_array = []
        if i > 0:
            for price in row:
                if len(price)>0:
                    price_array.append(float(price))
            historical_prices.append(price_array)
        i = i+1
    return historical_prices
    

def mean_list (my_list, index):
    mean = 0
    for i in range(len(my_list)-1):
        mean = mean + my_list[i][index]/100
    return mean / len(my_list)


def stdev_list(my_list, index):
    stdev = 0
    mean = mean_list(my_list, index)
    for i in range(len(my_list)-1):
        stdev = stdev + pow(my_list[i][index]/100 - mean, 2)
    return sqrt(stdev / len(my_list))


def compute_spread(list_stock, list_bench):
    list_spread = []
    for i in range(len(list_stock)-1):
        spread_t = []
        spread_t.append(list_stock[i][0])
        spread_t.append(list_stock[i][2]-list_bench[i][2])
        list_spread.append(spread_t)
    return list_spread


def BackTestSpread (path, pathbench, maturity, in_sample, stdev_trd, take_profit):
    
    # import data and compute spread
    market_data_stock = import_histo_prices_csv(path)
    market_data_bench = import_histo_prices_csv(pathbench)
    market_data_spread = compute_spread(market_data_stock, market_data_bench) # spread de implied vol
    pnl_Long= 0.0
    pay_off = []
    bool_long = False
    strat_days = 0
    pnL_Strat = 0.0
    strat_number = 0
    
    for i in range(len(market_data_spread)-1):

        # 0 to 3000 ...
        
        sub_list = []
        if i > in_sample:
            # i > 250
            # 251
            
            # implied volatilities spread
            sub_list = market_data_spread[i-in_sample-1: i-1] # implied vol spread = imp stock - imp index
            # 0 : 250
            
            mean = mean_list(sub_list, 1)
            # stdev spread implied vol = vol of vol
            stdev = stdev_list(sub_list, 1)
            rea_one_month = compute_rea(sub_list_stock_spot) - compute_rea(sub_list_index_spot)

            # INITIALIZE (first : Bool = False)
            # False : nouvelle option avec nouveau K et nouvelle implied vol
            if not bool_long:
            #2*market_data_spread[i][1]/100 < mean - stdev_trd * stdev + rea_one_month and not bool_long:
            # Choose to apply distribution metrics or not for entering
                
                # Fix Bool to True to start iterating afterwards
                bool_long = True
                strat_days = 0
                pnL_Strat = 0
                
                # strike = spot i = ATM
                strike_stock = market_data_stock[i][1]
                strike_index = market_data_bench[i][1]
                
                # implied vol ATM
                pricing_vol_stock = market_data_stock[i][2] / 100
                pricing_vol_index = market_data_bench[i][2] / 100
                
                # fix spot (here spot = strike) : create underlying object
                my_stock = Underlying(strike_stock, "ABBN")
                my_index = Underlying(strike_index, "SMI")
                
                # strike, spot (=strike=ATM) , maturity
                # ATM
                my_call_stock = EuropeanCall(strike_stock, my_stock, maturity)
                my_call_index = EuropeanCall(strike_index, my_index, maturity)
                delta_stock = my_call_stock.bs_delta(pricing_vol_stock, 0)
                delta_index = my_call_index.bs_delta(pricing_vol_index, 0)
                vega_stock = my_call_stock.bs_vega(pricing_vol_stock, 0)
                vega_index = my_call_index.bs_vega(pricing_vol_index, 0)
                
                # price call : stock & index
                call_price_stock = my_call_stock.bs_price(pricing_vol_stock, 0)
                call_price_index = my_call_index.bs_price(pricing_vol_index, 0)
                
                # store prices
                old_price_stock = call_price_stock
                old_price_index = call_price_index
            
            
            # START ITERATING
            # Bool reste True si les 3 conditions à la fin ne sont pas réalisées
            # itère le spot en gardant le strike (donc même option) en espérant en tirer du PNL (on n'est plus ATM du coup)
            # si 1 est réalisée : nouvelle option avec nouveau strike et nouvelle implied vol
            if bool_long:
                
                # spot = spot at t+1 ... t+n
                my_stock = Underlying(market_data_stock[i+1][1], "ABBN")
                my_index = Underlying(market_data_bench[i + 1][1], "SMI")
                
                # strike, spot (not ATM), maturity diminue avec temps
                my_call_stock = EuropeanCall(strike_stock, my_stock, maturity - (strat_days + 1)/252)
                my_call_index = EuropeanCall(strike_index, my_index, maturity - (strat_days + 1)/252)
                
                # NEW CALL PRICES (t+1) (versus OLD = t)
                # price call : stock & index
                # Implied vol reste celle ATM du début = c'est une vol pour un strike donné = pour une nouvelle option
                call_price_stock = my_call_stock.bs_price(pricing_vol_stock, 0)
                call_price_index = my_call_index.bs_price(pricing_vol_index, 0)
                
                # PNL
                # pnl = diff call - delta * (diff stock) / vega (security type differences reason)
                pnl_stock = (call_price_stock - old_price_stock - delta_stock * (market_data_stock[i+1][1] - market_data_stock[i][1]))/ vega_stock
                pnl_index = (call_price_index - old_price_index - delta_index * (market_data_bench[i+1][1] - market_data_bench[i][1]))/ vega_index
                
                # PNL STRAT réalisé sur chaque option = on joue le spread
                # stock - index
                pnL_Strat = pnL_Strat + pnl_stock - pnl_index
                
                # PNL FINAL qui récupère tous les PNL pour les storer à la fin
                pnl_Long = pnl_Long + pnl_stock - pnl_index
                
                # old (t) = new (t+1)
                old_price_stock = call_price_stock
                old_price_index = call_price_index
                
                # new delta (t+1)
                # delta stock & index
                delta_stock = my_call_stock.bs_delta(pricing_vol_stock, 0)
                delta_index = my_call_index.bs_delta(pricing_vol_index, 0)
                
                # add days : maturité diminue
                strat_days = strat_days + 1
                
            
            # Bool : reste True si les 3 conditions ne sont pas réalisées
            # Borne haute
            pos_stop_signal = 100*take_profit * stdev_trd * stdev
            # Borne basse
            neg_stop_signal = -1 * stdev_trd * stdev
            # + si expiration
            if pnL_Strat > pos_stop_signal or strat_days + 1 == round(maturity * 252) or pnL_Strat < neg_stop_signal:
                bool_long = False
                strat_number = strat_number + 1
            # Si aucune condition verifié : reste TRUE et continue dans TRUE = stratégie continue sur la même option
            
        
        # Store [Bool, PNL] avec PNL = [date, PNL]
        pay_off_T = []
        pay_off_T.append(strat_number)
        pay_off_T.append(market_data_stock[i][0])
        pay_off_T.append(strat_days)
        pay_off_T.append(bool_long)
        pay_off_T.append(pnl_Long)
        pay_off.append(pay_off_T)
        
    return pay_off

