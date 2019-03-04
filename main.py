import os
import pandas as pd
from datetime import *
from pyecharts import Line, Grid
from trader import *
from matplotlib import pyplot as plt


'''
	设置
'''
path_root = r'C:\Users\Jeffery-user\Desktop\data\CnCom.Id807012.SQniWxNiN\SQni_WxNi@1'
date_start = datetime.strptime('20190226', '%Y%m%d')


'''
	识别文件,获取数据
'''
def set_trader_data():
	d_live_path = {}
	l_sim_path = []

	for i in os.listdir(path_root):
		path_i = os.path.join(path_root, i)
		if os.path.isfile(path_i):
			if i[:4] == 'BAND':
				if 'BAND' not in d_live_path.keys():
					d_live_path['BAND'] = []
				d_live_path['BAND'].append(path_i)
			elif i[:3] == 'SIG':
				if 'SIG' not in d_live_path.keys():
					d_live_path['SIG'] = []
				d_live_path['SIG'].append(path_i)
		elif i.find('@') > -1:
			l_sim_path.append(path_i)

	l_traders = []

	# 添加Live Trader
	if len(d_live_path.keys()) > 0:
		path_BAND = d_live_path['BAND']
		path_SIG = d_live_path['SIG']

		trader_name = path_BAND[0].split('\\')[-1][5:-4]
		obj_trader_live = Trader(trader_name=trader_name, trader_type='Live')

		for i in path_BAND:
			obj_trader_live.set_Band(i)
			obj_trader_live.set_Bar(i)
		for i in path_SIG:
			obj_trader_live.set_TargetPosition(i)
		obj_trader_live.set_Trades()

		l_traders.append(obj_trader_live)
	else:
		print('no LIVE file')

	# 添加Sim Trader
	if len(l_sim_path) > 0:
		for path_sim in l_sim_path:
			trader_name = path_sim.split('\\')[-1]
			path_BAND = os.path.join(path_sim, 'RawArbSignals.csv')
			path_SIG = os.path.join(path_sim, 'RawSignals.csv')
			path_Trades = os.path.join(path_sim, 'Trades.csv')
			obj_trader_sim = Trader(trader_name=trader_name, trader_type='Sim')
			obj_trader_sim.set_Band(path_BAND)
			obj_trader_sim.set_Bar(path_BAND)
			obj_trader_sim.set_TargetPosition(path_SIG)
			obj_trader_sim.set_Trades(path_file=path_Trades)

			l_traders.append(obj_trader_sim)
	else:
		print('no SIM file')

	return l_traders


# TODO 将获取Trader （l_traders）的数据，如Trader.Band Trader.Bar等，做成一个方法。
'''
	1 获取数据
	2 筛选数据起始日期
	在后面的draw_xx 方法中就不需要考虑数据问题了
'''
def get_useful_trader_data(data_type):
	def get_Band():
		pass

	def get_Bar():
		pass

	def get_Trades():
		pass

	if str(data_type).lower() == 'band':
		get_Band()
	elif str(data_type).lower() == 'bar':
		get_Bar()
	elif str(data_type).lower() == 'trades':
		get_Trades()

def draw_live_Band():
	l_df = []
	for i_trader in l_traders:
		df = i_trader.Band
		df = df[df['DateTime'] > date_start]
		df = df[['DateTime', 'Trader', 'BuyEntry', 'BuyExit', 'SellEntry', 'SellExit']]
		l_df.append(df)
	df_Band = pd.DataFrame(pd.concat(l_df))
	df_Band = df_Band.set_index('DateTime', drop=True)

	grid = Grid(
		width=1400,
		height=800
	)
	line = Line()
	grid.use_theme('dark')
	# line.use_theme('dark')
	y_max = float(max(df_Band[['BuyEntry', 'BuyExit', 'SellEntry', 'SellExit']].dropna().values.tolist())[0])
	y_min = float(min(df_Band[['BuyEntry', 'BuyExit', 'SellEntry', 'SellExit']].dropna().values.tolist())[0])

	l_traders_name = list(set(df_Band['Trader'].tolist()))
	for trader_i in l_traders_name:
		df_Band_i = df_Band[df_Band['Trader'] == trader_i]

		x = df_Band_i.index.tolist()
		for sign_j in ['BuyEntry', 'BuyExit', 'SellEntry', 'SellExit']:
			y = df_Band_i[sign_j].tolist()
			line.add(
				'%s - %s' % (trader_i, sign_j),
				x_axis=x,
				y_axis=y,
				yaxis_max=y_max+(y_max-y_min)*0.15,
				yaxis_min=y_min-(y_max-y_min)*0.15,
				# xaxis_max=index_longer_max,
				# xaxis_min=index_longer_min,
				is_datazoom_show=True,
				# legend_pos='center',
				# legend_top='bottom',
				grid_top='10%'
			)

	grid.add(line, grid_top='15%')
	grid.render(r"%s\test-band.html" % (path_root))
	# line.render(r"%s\test-band.html" % (path_root))

# def draw_live_Band():
# 	l_df = []
# 	for i_trader in l_traders:
# 		df = i_trader.Band
# 		df = df[df['DateTime'] > date_start]
# 		df = df[['DateTime', 'Trader', 'BuyEntry', 'BuyExit', 'SellEntry', 'SellExit']]
# 		l_df.append(df)
# 	df_Band = pd.concat(l_df)
#
# 	grid = Grid(
# 		width=1200,
# 		height=1600
# 	)
#
# 	i = 0
# 	for sign_i in ['BuyEntry', 'BuyExit', 'SellEntry', 'SellExit']:
# 		i += 1
# 		df_Band_pivot = pd.pivot_table(
# 			df_Band,
# 			index='DateTime',
# 			columns=["Trader"],
# 			values=sign_i
# 		)
# 		y_max = float(max(df_Band_pivot.values.tolist())[0])
# 		y_min = float(min(df_Band_pivot.values.tolist())[0])
#
# 		line = Line()
# 		# line = Line(
# 		# 	width=1200,
# 		# 	height=400
# 		# )
# 		x = df_Band_pivot.index.tolist()
# 		j = 0
# 		for j_trader in df_Band_pivot.columns.tolist():
# 			j += 1
# 			y = df_Band_pivot[j_trader].tolist()
# 			line.add(
# 				'%s' % j_trader,
# 				x_axis=x,
# 				y_axis=y,
# 				yaxis_max=y_max,
# 				yaxis_min=y_min,
# 				# xaxis_max=index_longer_max,
# 				# xaxis_min=index_longer_min,
# 				is_datazoom_show=True,
# 				datazoom_xaxis_index=[0, 1, 2, 3],
# 				# legend_pos="0%",
# 				# legend_top='53%',
# 			)
#
# 		grid.add(line, grid_top="%s%%" % ((25*(i-1))+2), grid_bottom="%s%%" % ((25*(4-i))+2))
# 	grid.render(r"%s\test-band.html" % (path_root))


def draw_live_Bar():
	# 数据准备
	l_df = []
	for i_trader in l_traders:
		df = i_trader.Bar
		df = df[df['DateTime'] > date_start]
		df = df[['DateTime', 'Trader', 'Ticker', 'Open', 'High', 'Low', 'Close', 'Volume']]
		l_df.append(df)
	df_Bar = pd.concat(l_df)

	n_tickers = len(list(set(df_Bar['Ticker'].tolist())))
	datazoom_index = list(range(n_tickers))

	grid_bar = Grid(
		width=1200,
		height=800*n_tickers
	)
	grid_volume = Grid(
		width=1200,
		height=600*n_tickers
	)
	grid_bar.use_theme('dark')
	grid_volume.use_theme('dark')

	# 遍历ticker
	i = 0
	for sign_ticker in list(set(df_Bar['Ticker'].tolist())):
		i += 1
		df_Bar_ticker = df_Bar[df_Bar['Ticker'] == sign_ticker]

		# 画价格
		# for sign_i in ['Open', 'High', 'Low', 'Close']:
		for sign_i in ['Open']:
			df_Bar_pivot = pd.pivot_table(
				df_Bar_ticker,
				index='DateTime',
				columns=["Trader"],
				values=sign_i
			)

			line = Line()
			x = df_Bar_pivot.index.tolist()
			y_max = float(max(df_Bar_pivot.values.tolist())[0])
			y_min = float(min(df_Bar_pivot.values.tolist())[0])
			j = 0

			for j_trader in df_Bar_pivot.columns.tolist():
				j += 1
				y = df_Bar_pivot[j_trader].tolist()
				line.add(
					'%s-%s' % (sign_ticker, j_trader),
					x_axis=x,
					y_axis=y,
					yaxis_max=y_max,
					yaxis_min=y_min,
					is_datazoom_show=True,
					datazoom_xaxis_index=datazoom_index,
					# legend_pos="0%",
					legend_top='%s%%' % (100/n_tickers*(i-1)+2),
				)
			grid_bar.add(
				line,
				grid_top="%s%%" % (100/n_tickers*(i-1)+10),
				grid_bottom="%s%%" % (100/n_tickers*(n_tickers-i)+10)
			)

		# 画Volume
		if True:
			df_Bar_pivot = pd.pivot_table(
				df_Bar_ticker,
				index='DateTime',
				columns="Trader",
				values='Volume'
			)

			line = Line()
			x = df_Bar_pivot.index.tolist()
			j = 0
			for j_trader in df_Bar_pivot.columns.tolist():
				j += 1
				y = df_Bar_pivot[j_trader].groupby(by=df_Bar_pivot.to_period('D').index).cumsum().tolist()
				line.add(
					'%s-%s' % (sign_ticker, j_trader),
					x_axis=x,
					y_axis=y,
					is_datazoom_show=True,
					datazoom_xaxis_index=datazoom_index,
					# legend_pos="0%",
					legend_top='%s%%' % (100/n_tickers*(i-1)+2)
				)
			grid_volume.add(
				line,
				grid_top="%s%%" % (100/n_tickers*(i-1)+10),
				grid_bottom="%s%%" % (100/n_tickers*(n_tickers-i)+10)
			)

	grid_bar.render(r"%s\test-bar.html" % path_root)
	grid_volume.render(r"%s\test-volume.html" % path_root)

	# TODO 增加bar_data统计

def draw_live_Trades():
	# 重置index
	def reset_datatime_index(df, start, end, trade_session='day'):
		t = pd.date_range(start=start, end=end, freq='60s').to_list()
		if trade_session.lower() == 'day':
			t = [i for i in t if i.hour in [9, 10, 11, 13, 14]]
		elif trade_session.lower() == 'night':
			t = [i for i in t if i.hour in [21, 22]]
		else:
			t = [i for i in t if i.hour in [9, 10, 11, 13, 14, 21, 22]]
		df = df.reindex(t, fill_value=0)
		return df

	'''
	get_most_count_num原用于平滑y （成交量cumsum）曲线，后发现想错了，并不需要，改为 (max-min)/2
	'''
	def get_most_count_num(l):
		l = list(l)
		most_count = 0
		most_count_num = ''
		for i in list(set(l)):
			i_count = l.count(i)
			if i_count > most_count:
				most_count = i_count
				most_count_num = i
		return most_count_num

	# 数据准备
	l_df = []
	str_trading_session = 'day'
	for i_trader in l_traders:
		df = i_trader.Trades
		df = df[df['DateTime'] > date_start]
		df = df[['DateTime', 'Trader', 'Ticker', 'TradedPrice', 'TradedVolume', 'Commission', 'Direction', 'OffsetFlag']]
		if i_trader.type.lower() == 'sim':
			df['TradedVolume'] = df['TradedVolume'] / 1000
		l_df.append(df)
		str_trading_session = {
			'090000-101500&103000-113000&133000-150000': 'day',
			'040000-051500&053000-063000&083000-100000&160000-18000': 'day and night',
			'160000-180000': 'night'
		}.get(i_trader.TradingSession)
	df_trades = pd.concat(l_df)
	df_trades['Volume'] = df_trades['TradedVolume'] * df_trades['Direction']

	n_tickers = len(list(set(df_trades['Ticker'].tolist())))
	datazoom_index = list(range(n_tickers))

	# 开始画图
	grid = Grid(
		width=1200,
		height=800*n_tickers
	)
	grid.use_theme('dark')

	i = 0
	for ticker_i in list(set(df_trades['Ticker'].tolist())):
		i += 1
		line = Line()
		line.use_theme('dark')
		df_trades_ticker = df_trades[df_trades['Ticker'] == ticker_i]
		df_trades_ticker_pivot = pd.pivot_table(
			df_trades_ticker,
			index='DateTime',
			columns="Trader",
			values='Volume',
			aggfunc='sum'
		)
		df_trades_ticker_pivot = df_trades_ticker_pivot.fillna(0)

		df_trades_ticker_pivot = reset_datatime_index(
			df_trades_ticker_pivot,
			start=min(df_trades_ticker_pivot.index.tolist()).date(),
			end=max(df_trades_ticker_pivot.index.tolist()).date(),
			trade_session=str_trading_session
		)
		df_trades_ticker_pivot_sum = df_trades_ticker_pivot.cumsum()
		max_value = df_trades_ticker_pivot_sum.values.max()
		min_value = df_trades_ticker_pivot_sum.values.min()
		max_value = round(max(max_value, abs(min_value))*1.1, 0)
		min_value = -max_value

		x = df_trades_ticker_pivot.index.tolist()
		j = 0
		for trader_j in df_trades_ticker_pivot_sum.columns.tolist():
			j += 1

			'''
				整理y， y = y - (y.max + y.min)/2，
				用于调整 y数组 使数组出现最多的值为 0，从而达到用‘成交的累计’拟合‘持仓量’的效果，
				即可以在不知道原始持仓（交易前）的情况下，推出原始持仓，并拟合出持仓的时间序列。
			'''
			y = df_trades_ticker_pivot_sum[trader_j]
			y_max = y.values.max()
			y_min = y.values.min()
			if y_min<0:
				pass
			else:
				y_min = -y_max
			if y_max>0:
				pass
			else:
				y_max = -y_min
			y = y - (y_max + y_min)/2
			y = y.tolist()

			line.add(
				'%s-%s' % (ticker_i, trader_j),
				x_axis=x,
				y_axis=y,
				is_datazoom_show=True,
				yaxis_max=max_value,
				yaxis_min=min_value,
				datazoom_xaxis_index=datazoom_index,
				datazoom_type='both',
				legend_pos='center',
				legend_top='%s%%' % (100/n_tickers*(i-1)+2)
			)
		# line.render(r"%s\test-trades1.html" % path_root)
		grid.add(
			line,
			grid_top="%s%%" % (100/n_tickers*(i-1)+10),
			grid_bottom="%s%%" % (100/n_tickers*(n_tickers-i)+10)
		)
	grid.render(r"%s\test-trades.html" % path_root)


if __name__ == '__main__':
	print('geting data')
	l_traders = set_trader_data()
	print('drawing band')
	draw_live_Band()
	print('drawing bar')
	draw_live_Bar()
	print('drawing trades')
	draw_live_Trades()
	print('Finished All')
