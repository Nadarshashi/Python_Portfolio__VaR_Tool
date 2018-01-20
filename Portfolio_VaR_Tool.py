
import datetime
import pandas as pd
import pandas_datareader.data as web
import numpy as np
import math
import matplotlib as plt
import matplotlib.dates as mdates
from matplotlib import cm as cm
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
import re
import scipy.stats
import wx.lib.pubsub
from wx.lib.pubsub import pub
import wx


# First tab

class PageOne(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        fontbold = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.BOLD)

        title = wx.StaticText(self, wx.ID_ANY, 'Portfolio Tool')
        title.SetFont(fontbold)

        stock_a_label = wx.StaticText(self, -1, "Ticker Stock A", (20, 20))
        stock_b_label = wx.StaticText(self, -1, "Ticker Stock B", (20, 20))
        stock_c_label = wx.StaticText(self, -1, "Ticker Stock C", (20, 20))
        stock_d_label = wx.StaticText(self, -1, "Ticker Stock D", (20, 20))

        self.stock_a_ticker_input = wx.TextCtrl(self, size=(60, -1))
        self.stock_b_ticker_input = wx.TextCtrl(self, size=(60, -1))
        self.stock_c_ticker_input = wx.TextCtrl(self, size=(60, -1))
        self.stock_d_ticker_input = wx.TextCtrl(self, size=(60, -1))

        stock_a_weight_label = wx.StaticText(self, -1, "Weight Stock A", (20, 20))
        stock_b_weight_label= wx.StaticText(self, -1, "Weight Stock B", (20, 20))
        stock_c_weight_label = wx.StaticText(self, -1, "Weight Stock C", (20, 20))
        stock_d_weight_label = wx.StaticText(self, -1, "Weight Stock D", (20, 20))

        self.stock_a_weight_input = wx.TextCtrl(self, size=(60, -1))
        self.stock_b_weight_input = wx.TextCtrl(self, size=(60, -1))
        self.stock_c_weight_input = wx.TextCtrl(self, size=(60, -1))
        self.stock_d_weight_input = wx.TextCtrl(self, size=(60, -1))

        timeseries_label = wx.StaticText(self, -1, "Time series from: [dd/mm/yyyy]", (20, 20))
        self.timeseries_input = wx.TextCtrl(self, size=(85, -1))

        background_a = wx.StaticText(self, -1, "> Tickers should be inserted in alphabetical order", (20, 20))
        background_a.SetForegroundColour(wx.BLUE)

        background_b = wx.StaticText(self, -1, "> Stock weights should be decimals (i.e. 40% = 0.4)", (20, 20))
        background_b.SetForegroundColour(wx.BLUE)

        self.export = wx.CheckBox(self, label = 'Export data to CSV')

        button = wx.Button(self, label="Retrieve data",)
        self.Bind(wx.EVT_BUTTON, self.onRETRIEVE, button)

        self.warning = wx.StaticText(self, -1, "", (20, 20))

        sizer = wx.GridBagSizer(10, 15)

        sizer.Add(title, (1, 0))

        sizer.Add(stock_a_label, (3, 0))
        sizer.Add(stock_b_label, (4, 0))
        sizer.Add(stock_c_label, (5, 0))
        sizer.Add(stock_d_label, (6, 0))

        sizer.Add(self.stock_a_ticker_input, (3, 2))
        sizer.Add(self.stock_b_ticker_input, (4, 2))
        sizer.Add(self.stock_c_ticker_input, (5, 2))
        sizer.Add(self.stock_d_ticker_input, (6, 2))

        sizer.Add(stock_a_weight_label, (3, 5))
        sizer.Add(stock_b_weight_label, (4, 5))
        sizer.Add(stock_c_weight_label, (5, 5))
        sizer.Add(stock_d_weight_label, (6, 5))

        sizer.Add(self.stock_a_weight_input, (3, 7))
        sizer.Add(self.stock_b_weight_input, (4, 7))
        sizer.Add(self.stock_c_weight_input, (5, 7))
        sizer.Add(self.stock_d_weight_input, (6, 7))

        sizer.Add(timeseries_label, (3, 9))
        sizer.Add(self.timeseries_input, (3, 11))

        sizer.Add(background_a, (5, 9))
        sizer.Add(background_b, (6, 9))

        sizer.Add(self.export, (8, 9))

        sizer.Add(button, (9, 0))

        sizer.Add(self.warning, (11, 0))

        self.border = wx.BoxSizer()
        self.border.Add(sizer, 1, wx.ALL | wx.EXPAND, 5)

        self.SetSizerAndFit(self.border)

    def onRETRIEVE(self, event):

        stock_a_ticker = self.stock_a_ticker_input.GetValue()
        stock_b_ticker = self.stock_b_ticker_input.GetValue()
        stock_c_ticker = self.stock_c_ticker_input.GetValue()
        stock_d_ticker = self.stock_d_ticker_input.GetValue()

        stock_a_weight = self.stock_a_weight_input.GetValue()
        stock_b_weight = self.stock_b_weight_input.GetValue()
        stock_c_weight = self.stock_c_weight_input.GetValue()
        stock_d_weight = self.stock_d_weight_input.GetValue()

        stocks = [stock_a_ticker, stock_b_ticker, stock_c_ticker, stock_d_ticker, ]

        try:

            datetime.datetime.strptime(self.timeseries_input.GetValue(), '%d/%m/%Y')

            if re.match("^\d+?\.\d+?$", stock_a_weight) is None or re.match("^\d+?\.\d+?$", stock_b_weight) is None or re.match("^\d+?\.\d+?$", stock_c_weight) is None or re.match("^\d+?\.\d+?$", stock_d_weight) is None:

                self.warning.SetLabel("Stock weight should be a digit")

            elif any(x == '' for x in stocks) or any(x == None for x in stocks):

                self.warning.SetLabel("One or more inputs are missing. Please insert all required values")

            else:

                weights = np.asarray([float(stock_a_weight), float(stock_b_weight), float(stock_c_weight), float(stock_d_weight), ])

                if sum(weights) != 1:

                    self.warning.SetLabel("Portfolio weights should sum up to 1")

                else:

                    try:

                        self.warning.SetLabel("")

                        # Get data

                        data = web.DataReader(stocks, data_source='yahoo', start= self.timeseries_input.GetValue())['Adj Close']

                        data.sort_index(inplace=True, ascending=True)
                        data.index = pd.to_datetime(data.index)

                        # Calculate metrics

                        returns = data.pct_change().dropna()
                        mean_daily_returns = returns.mean()
                        std = returns.std()
                        cov_matrix = returns.cov()

                        mean_daily_return_label = wx.StaticText(self, -1, "Mean daily return (%)", (20, 20))
                        expected_annual_return_label = wx.StaticText(self, -1, "Expected annual return (%)", (20, 20))
                        daily_std_label = wx.StaticText(self, -1, "Standard Deviation (%)", (20, 20))
                        annual_std_label = wx.StaticText(self, -1, "Annual Standard Deviation (%)", (20, 20))
                        sharpe_label = wx.StaticText(self, -1, "Sharpe Ratio", (20, 20))

                        stock_a_header = wx.StaticText(self, -1, str(stocks[0]), (20, 20))
                        stock_b_header = wx.StaticText(self, -1, str(stocks[1]), (20, 20))
                        stock_c_header = wx.StaticText(self, -1, str(stocks[2]), (20, 20))
                        stock_d_header = wx.StaticText(self, -1, str(stocks[3]), (20, 20))
                        portfolio_header = wx.StaticText(self, -1, "Portfolio", (20, 20))

                        stock_a_mean_daily_return = wx.StaticText(self, -1, str(round(mean_daily_returns[stocks[0]]*100, 2)), (20, 20))
                        stock_b_mean_daily_return = wx.StaticText(self, -1, str(round(mean_daily_returns[stocks[1]]*100, 2)), (20, 20))
                        stock_c_mean_daily_return = wx.StaticText(self, -1, str(round(mean_daily_returns[stocks[2]]*100, 2)), (20, 20))
                        stock_d_mean_daily_return = wx.StaticText(self, -1, str(round(mean_daily_returns[stocks[3]]*100, 2)), (20, 20))
                        portfolio_mean_daily_return = np.sum(mean_daily_returns * weights)
                        portfolio_mean_daily_return_scr = wx.StaticText(self, -1, str(round(portfolio_mean_daily_return * 100, 2)), (20, 20))

                        stock_a_annual_return = wx.StaticText(self, -1, str(round(mean_daily_returns[stocks[0]]*100*252, 2)), (20, 20))
                        stock_b_annual_return = wx.StaticText(self, -1, str(round(mean_daily_returns[stocks[1]]*100*252, 2)), (20, 20))
                        stock_c_annual_return = wx.StaticText(self, -1, str(round(mean_daily_returns[stocks[2]]*100*252, 2)), (20, 20))
                        stock_d_annual_return = wx.StaticText(self, -1, str(round(mean_daily_returns[stocks[3]]*100*252, 2)), (20, 20))
                        portfolio_annual_return = wx.StaticText(self, -1, str(round(portfolio_mean_daily_return  * 100 * 252, 2)), (20, 20))

                        stock_a_daily_std = wx.StaticText(self, -1, str(round(std[stocks[0]]*100, 2)), (20, 20))
                        stock_b_daily_std = wx.StaticText(self, -1, str(round(std[stocks[1]]*100, 2)), (20, 20))
                        stock_c_daily_std = wx.StaticText(self, -1, str(round(std[stocks[2]]*100, 2)), (20, 20))
                        stock_d_daily_std = wx.StaticText(self, -1, str(round(std[stocks[3]]*100, 2)), (20, 20))
                        portfolio_daily_std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
                        portfolio_daily_std_scr = wx.StaticText(self, -1, str(round(portfolio_daily_std * 100, 2)), (20, 20))

                        stock_a_annual_std = wx.StaticText(self, -1, str(round(std[stocks[0]] * 100 * np.sqrt(252), 2)), (20, 20))
                        stock_b_annual_std = wx.StaticText(self, -1, str(round(std[stocks[1]] * 100 * np.sqrt(252), 2)), (20, 20))
                        stock_c_annual_std = wx.StaticText(self, -1, str(round(std[stocks[2]] * 100 * np.sqrt(252), 2)), (20, 20))
                        stock_d_annual_std = wx.StaticText(self, -1, str(round(std[stocks[3]] * 100 * np.sqrt(252), 2)), (20, 20))
                        portfolio_annual_std = wx.StaticText(self, -1, str(round(portfolio_daily_std * 100 * np.sqrt(252), 2)), (20, 20))

                        risk_free_rate = 2.25 # 10 year US-treasury rate (annual)

                        sharpe_a = ((mean_daily_returns[stocks[0]]*100*252) -  risk_free_rate ) / (std[stocks[0]] * 100 * np.sqrt(252))
                        sharpe_b = ((mean_daily_returns[stocks[1]] * 100 * 252) - risk_free_rate) / (std[stocks[1]] * 100 * np.sqrt(252))
                        sharpe_c = ((mean_daily_returns[stocks[2]] * 100 * 252) - risk_free_rate) / (std[stocks[2]] * 100 * np.sqrt(252))
                        sharpe_d = ((mean_daily_returns[stocks[3]] * 100 * 252) - risk_free_rate) / (std[stocks[3]] * 100 * np.sqrt(252))
                        sharpe_portfolio = ((portfolio_mean_daily_return * 100 * 252) - risk_free_rate) / (portfolio_daily_std * 100 * np.sqrt(252))

                        sharpe_a_scr = wx.StaticText(self, -1, str(round(sharpe_a, 2)),(20, 20))
                        sharpe_b_scr = wx.StaticText(self, -1, str(round(sharpe_b, 2)), (20, 20))
                        sharpe_c_scr = wx.StaticText(self, -1, str(round(sharpe_c, 2)), (20, 20))
                        sharpe_d_scr = wx.StaticText(self, -1, str(round(sharpe_d, 2)), (20, 20))
                        sharpe_portfolio_scr = wx.StaticText(self, -1, str(round(sharpe_portfolio, 2)), (20, 20))

                        # Put metrics in Sizer

                        sizer = wx.GridBagSizer(10, 10)

                        sizer.Add(mean_daily_return_label, (12, 0))
                        sizer.Add(expected_annual_return_label, (13, 0))
                        sizer.Add(daily_std_label, (14, 0))
                        sizer.Add(annual_std_label, (15, 0))
                        sizer.Add(sharpe_label, (16, 0))

                        sizer.Add(stock_a_header, (11, 2))
                        sizer.Add(stock_b_header, (11, 4))
                        sizer.Add(stock_c_header, (11, 6))
                        sizer.Add(stock_d_header, (11, 8))
                        sizer.Add(portfolio_header, (11, 11))

                        sizer.Add(stock_a_mean_daily_return, (12, 2))
                        sizer.Add(stock_b_mean_daily_return, (12, 4))
                        sizer.Add(stock_c_mean_daily_return, (12, 6))
                        sizer.Add(stock_d_mean_daily_return, (12, 8))
                        sizer.Add(portfolio_mean_daily_return_scr, (12, 11))

                        sizer.Add(stock_a_annual_return, (13, 2))
                        sizer.Add(stock_b_annual_return, (13, 4))
                        sizer.Add(stock_c_annual_return, (13, 6))
                        sizer.Add(stock_d_annual_return, (13, 8))
                        sizer.Add(portfolio_annual_return, (13, 11))

                        sizer.Add(stock_a_daily_std, (14, 2))
                        sizer.Add(stock_b_daily_std, (14, 4))
                        sizer.Add(stock_c_daily_std, (14, 6))
                        sizer.Add(stock_d_daily_std, (14, 8))
                        sizer.Add(portfolio_daily_std_scr, (14, 11))

                        sizer.Add(stock_a_annual_std, (15, 2))
                        sizer.Add(stock_b_annual_std, (15, 4))
                        sizer.Add(stock_c_annual_std, (15, 6))
                        sizer.Add(stock_d_annual_std, (15, 8))
                        sizer.Add(portfolio_annual_std, (15, 11))

                        sizer.Add(sharpe_a_scr, (16, 2))
                        sizer.Add(sharpe_b_scr, (16, 4))
                        sizer.Add(sharpe_c_scr, (16, 6))
                        sizer.Add(sharpe_d_scr, (16, 8))
                        sizer.Add(sharpe_portfolio_scr, (16, 11))

                        self.border = wx.BoxSizer()
                        self.border.Add(sizer, 1, wx.ALL | wx.EXPAND, 5)

                        self.SetSizerAndFit(self.border)

                        pub.sendMessage("panelListener", arg1 = data, arg2 = weights, arg3 = stocks)

                        # Export to CSV it box is ticked

                        if self.export.GetValue() == True:

                            data.to_csv("data"+stock_a_ticker+"to"+stock_d_ticker+".csv", sep=';', encoding='utf-8')

                        else:
                            pass

                    except Exception as e:

                        self.warning.SetLabel(str(e))

        except ValueError:

            self.warning.SetLabel("Date not in the right format")

# Second tab

class PageTwo(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        pub.subscribe(self.myListener, "panelListener")

    def myListener(self, arg1, arg2, arg3):

        data = arg1
        stocks = arg3

        returns = data.pct_change().dropna()

        # Histogram daily returns

        figure_1 = Figure(figsize=(7, 2.5))
        canvas_1 = FigureCanvas(self, -1, figure_1)

        axes_1 = figure_1.add_subplot(111)
        axes_2 = figure_1.add_subplot(111)
        axes_3 = figure_1.add_subplot(111)
        axes_4 = figure_1.add_subplot(111)

        axes_1.hist(returns[stocks[0]], bins=50, normed=True, histtype='stepfilled', alpha=0.5)
        axes_2.hist(returns[stocks[1]], bins=50, normed=True, histtype='stepfilled', alpha=0.5)
        axes_3.hist(returns[stocks[2]], bins=50, normed=True, histtype='stepfilled', alpha=0.5)
        axes_4.hist(returns[stocks[3]], bins=50, normed=True, histtype='stepfilled', alpha=0.5)
        axes_1.set_title(u"Historic return distribution", weight='bold')
        axes_1.legend(loc='upper left')

        # Daily price chart

        figure_2 = Figure(figsize=(7, 2.5))
        canvas_2 = FigureCanvas(self, -1, figure_2)

        axes_A = figure_2.add_subplot(111)
        axes_B = figure_2.add_subplot(111)
        axes_C = figure_2.add_subplot(111)
        axes_D = figure_2.add_subplot(111)

        years = mdates.YearLocator()
        yearsFmt = mdates.DateFormatter("'%y")

        axes_A.plot(data.index, data[stocks[0]])
        axes_A.xaxis.set_major_locator(years)
        axes_A.xaxis.set_major_formatter(yearsFmt)

        axes_B.plot(data.index, data[stocks[1]])
        axes_B.xaxis.set_major_locator(years)
        axes_B.xaxis.set_major_formatter(yearsFmt)

        axes_C.plot(data.index, data[stocks[2]])
        axes_C.xaxis.set_major_locator(years)
        axes_C.xaxis.set_major_formatter(yearsFmt)

        axes_D.plot(data.index, data[stocks[3]])
        axes_D.xaxis.set_major_locator(years)
        axes_D.xaxis.set_major_formatter(yearsFmt)

        axes_A.set_title(u" Adjusted Price", weight='bold')
        axes_A.legend(loc='upper left')

        sizer = wx.GridBagSizer(7, 2.5)
        sizer.Add(canvas_1, (1, 0))
        sizer.Add(canvas_2, (2, 0))

        self.border = wx.BoxSizer()
        self.border.Add(sizer, 1, wx.ALL | wx.EXPAND, 5)

        self.SetSizerAndFit(self.border)

# Third tab

class PageThree(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        pub.subscribe(self.myListener, "panelListener")

    def myListener(self, arg1, arg2, arg3):

        fontbold = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.BOLD)

        data = arg1

        stocks = arg3
        weights = arg2

        returns = data.pct_change().dropna()

        mean_daily_returns = returns.mean()
        std = returns.std()
        cov_matrix = returns.cov()

        # Historical Simulation VaR

        title_historical = wx.StaticText(self, wx.ID_ANY, 'VaR - Historical Simulation')
        title_historical.SetFont(fontbold)

        stock_a_hist_var_lab = wx.StaticText(self, -1, str(stocks[0]) + " - Daily VaR (5%)", (20, 20))
        stock_b_hist_var_lab = wx.StaticText(self, -1, str(stocks[1]) + " - Daily VaR (5%)", (20, 20))
        stock_c_hist_var_lab = wx.StaticText(self, -1, str(stocks[2]) + " - Daily VaR (5%)", (20, 20))
        stock_d_hist_var_lab = wx.StaticText(self, -1, str(stocks[3]) + " - Daily VaR (5%)", (20, 20))
        portfolio_hist_var_lab = wx.StaticText(self, -1, "Portfolio - Daily VaR (5%)", (20, 20))

        stock_a_hist_var = wx.StaticText(self, -1, str(round(returns[stocks[0]].quantile(0.05) * 100, 2)), (20, 20))
        stock_b_hist_var = wx.StaticText(self, -1, str(round(returns[stocks[1]].quantile(0.05) * 100, 2)), (20, 20))
        stock_c_hist_var = wx.StaticText(self, -1, str(round(returns[stocks[2]].quantile(0.05) * 100, 2)), (20, 20))
        stock_d_hist_var = wx.StaticText(self, -1, str(round(returns[stocks[3]].quantile(0.05) * 100, 2)), (20, 20))

        portfolio_hist_ret = returns.mul(weights).sum(1)
        portfolio_hist_var = wx.StaticText(self, -1, str(round(portfolio_hist_ret.quantile(0.05) * 100, 2)), (20, 20))

        # Variance-Covariance VaR

        title_varcov = wx.StaticText(self, wx.ID_ANY, 'VaR - Variance Covariance')
        title_varcov.SetFont(fontbold)

        stock_a_cov_var_lab = wx.StaticText(self, -1, str(stocks[0]) + " - Daily VaR (5%)", (20, 20))
        stock_b_cov_var_lab = wx.StaticText(self, -1, str(stocks[1]) + " - Daily VaR (5%)", (20, 20))
        stock_c_cov_var_lab = wx.StaticText(self, -1, str(stocks[2]) + " - Daily VaR (5%)", (20, 20))
        stock_d_cov_var_lab = wx.StaticText(self, -1, str(stocks[3]) + " - Daily VaR (5%)", (20, 20))

        stock_a_cov_var = wx.StaticText(self, -1, str(round(scipy.stats.norm.ppf(0.05, mean_daily_returns[stocks[0]], std[stocks[0]]) * 100, 2)))
        stock_b_cov_var = wx.StaticText(self, -1, str(round(scipy.stats.norm.ppf(0.05, mean_daily_returns[stocks[1]], std[stocks[1]]) * 100, 2)))
        stock_c_cov_var = wx.StaticText(self, -1, str(round(scipy.stats.norm.ppf(0.05, mean_daily_returns[stocks[2]], std[stocks[2]]) * 100, 2)))
        stock_d_cov_var = wx.StaticText(self, -1, str(round(scipy.stats.norm.ppf(0.05, mean_daily_returns[stocks[3]], std[stocks[3]]) * 100, 2)))

        portfolio_return_daily = np.sum(mean_daily_returns * weights)
        portfolio_std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

        portfolio_cov_var_lab = wx.StaticText(self, -1, "Portfolio - Daily VaR (5%)", (20, 20))
        portfolio_cov_var = wx.StaticText(self, -1, str(round(scipy.stats.norm.ppf(0.05, portfolio_return_daily, portfolio_std) * 100, 2)))

        # Monte Carlo - Single Stock - Geometric Brownian Motion VaR

        title_MC = wx.StaticText(self, wx.ID_ANY, 'VaR - Monte Carlo')
        title_MC.SetFont(fontbold)

        MC_return =[]

        for item in range(len(stocks)):

            result = []

            S = data[stocks[item]].iloc[-1]
            T = 252
            mu = returns[stocks[item]].mean()*252
            vol = returns[stocks[item]].std()*np.sqrt(252)

            for i in range(1000):

                daily_returns = np.random.normal(mu/T,vol/math.sqrt(T),T)+1

                price_list = [S]

                price_list.append(price_list[-1] * daily_returns)

                result.append(price_list[-1])

            MC_return.append((np.percentile(result,5) - S) / S)

        stock_a_MC_lab = wx.StaticText(self, -1, str(stocks[0]) + " - Daily VaR (5%)", (20, 20))
        stock_b_MC_lab = wx.StaticText(self, -1, str(stocks[1]) + " - Daily VaR (5%)", (20, 20))
        stock_c_MC_lab = wx.StaticText(self, -1, str(stocks[2]) + " - Daily VaR (5%)", (20, 20))
        stock_d_MC_lab = wx.StaticText(self, -1, str(stocks[3]) + " - Daily VaR (5%)", (20, 20))

        stock_a_MC = wx.StaticText(self, -1, str(round(MC_return[0] * 100, 2)), (20, 20))
        stock_b_MC = wx.StaticText(self, -1, str(round(MC_return[1] * 100, 2)), (20, 20))
        stock_c_MC = wx.StaticText(self, -1, str(round(MC_return[2] * 100, 2)), (20, 20))
        stock_d_MC = wx.StaticText(self, -1, str(round(MC_return[3] * 100, 2)), (20, 20))

        MC_assumptions_lab = wx.StaticText(self, -1, "Monte Carlo - Assumptions", (20, 20))

        MC_assumption_1 = wx.StaticText(self, -1, "Geometric Brownian Motion", (20, 20))
        MC_assumption_2 = wx.StaticText(self, -1, "N = 1000", (20, 20))
        MC_assumption_3 = wx.StaticText(self, -1, "μ = mean daily stock return (i.e. drift)", (20, 20))
        MC_assumption_4 = wx.StaticText(self, -1, "σ = standard deviation of returns", (20, 20))

        MC_assumption_1.SetForegroundColour(wx.BLUE)
        MC_assumption_2.SetForegroundColour(wx.BLUE)
        MC_assumption_3.SetForegroundColour(wx.BLUE)
        MC_assumption_4.SetForegroundColour(wx.BLUE)

        # Put metrics in Sizer

        sizer = wx.GridBagSizer(10, 15)

        sizer.Add(title_historical, (1, 0))

        sizer.Add(stock_a_hist_var_lab, (3, 0))
        sizer.Add(stock_b_hist_var_lab, (4, 0))
        sizer.Add(stock_c_hist_var_lab, (5, 0))
        sizer.Add(stock_d_hist_var_lab, (6, 0))
        sizer.Add(portfolio_hist_var_lab, (8, 0))

        sizer.Add(stock_a_hist_var, (3, 1))
        sizer.Add(stock_b_hist_var, (4, 1))
        sizer.Add(stock_c_hist_var, (5, 1))
        sizer.Add(stock_d_hist_var, (6, 1))
        sizer.Add(portfolio_hist_var, (8, 1))

        sizer.Add(title_varcov, (10, 0))

        sizer.Add(stock_a_cov_var_lab, (12, 0))
        sizer.Add(stock_b_cov_var_lab, (13, 0))
        sizer.Add(stock_c_cov_var_lab, (14, 0))
        sizer.Add(stock_d_cov_var_lab, (15, 0))
        sizer.Add(portfolio_cov_var_lab, (17, 0))

        sizer.Add(stock_a_cov_var, (12, 1))
        sizer.Add(stock_b_cov_var, (13, 1))
        sizer.Add(stock_c_cov_var, (14, 1))
        sizer.Add(stock_d_cov_var, (15, 1))
        sizer.Add(portfolio_cov_var, (17, 1))

        sizer.Add(title_MC, (1, 8))

        sizer.Add(stock_a_MC_lab, (3, 8))
        sizer.Add(stock_b_MC_lab, (4, 8))
        sizer.Add(stock_c_MC_lab, (5, 8))
        sizer.Add(stock_d_MC_lab, (6, 8))

        sizer.Add(stock_a_MC, (3, 9))
        sizer.Add(stock_b_MC, (4, 9))
        sizer.Add(stock_c_MC, (5, 9))
        sizer.Add(stock_d_MC, (6, 9))

        sizer.Add(MC_assumptions_lab, (8, 8))
        sizer.Add(MC_assumption_1, (10, 8))
        sizer.Add(MC_assumption_2, (11, 8))
        sizer.Add(MC_assumption_3, (12, 8))
        sizer.Add(MC_assumption_4, (13, 8))

        self.border = wx.BoxSizer()
        self.border.Add(sizer, 1, wx.ALL | wx.EXPAND, 5)

        self.SetSizerAndFit(self.border)

# Fourth tab

class PageFour(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        pub.subscribe(self.myListener, "panelListener")

    def myListener(self, arg1, arg2, arg3):

        data = arg1

        returns = data.pct_change().dropna()

        # Construct correlation matrix

        figure_3 = Figure(figsize=(6, 4))
        canvas_3 = FigureCanvas(self, -1, figure_3)

        axes_E = figure_3.add_subplot(111)

        axes_E.pcolor(returns.corr(), cmap=plt.cm.Blues)
        axes_E.set_xticks(np.arange(5)+0.5)  # center x ticks
        axes_E.set_yticks(np.arange(5)+0.5)  # center y ticks
        axes_E.set_xticklabels(returns.columns)
        axes_E.set_yticklabels(returns.columns)

        sizer = wx.GridBagSizer(7, 2.5)
        sizer.Add(canvas_3, (1, 0))

        self.border = wx.BoxSizer()
        self.border.Add(sizer, 1, wx.ALL | wx.EXPAND, 5)

        self.SetSizerAndFit(self.border)

class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="Portfolio Tool")

        p = wx.Panel(self)
        nb = wx.Notebook(p)

        page1 = PageOne(nb)
        page2 = PageTwo(nb)
        page3 = PageThree(nb)
        page4 = PageFour(nb)

        nb.AddPage(page1, "Portfolio Data")
        nb.AddPage(page2, "Descriptive Data +")
        nb.AddPage(page3, "VAR")
        nb.AddPage(page4, "Correlation Matrix")

        sizer = wx.BoxSizer()
        sizer.Add(nb, 1, wx.EXPAND)
        p.SetSizer(sizer)


if __name__ == "__main__":

    app = wx.App()
    frame = MainFrame()
    frame.SetSize(0, 0, 1200, 750)
    frame.Center()
    frame.Show()
    app.MainLoop()