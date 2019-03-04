import os
import pandas as pd
import numpy as np
import time
from datetime import *
from MSSQL import MSSQL

class Trader:
	def __init__(self, trader_name, trader_type='Sim'):
		self.name = trader_name
		self.type = trader_type
		self.Band = pd.DataFrame()
		self.Bar = pd.DataFrame()
		self.TargetPosition = pd.DataFrame()
		self.Trades = pd.DataFrame()
		self.TradingSession = ''

	@staticmethod
	def chose_digit(s):
		try:
			s2 = float(s)
		except:
			return np.nan
		else:
			return s2

	@staticmethod
	def fix_time_session(df):
		df['DateTime'] = df['DateTime'] + timedelta(hours=5)
		return df

	def set_Trading_session(self, s):
		self.TradingSession = s

	# 接收RawArbSignal.csv 或 BAND.csv
	def set_Band(self, path_file):
		df = pd.read_csv(path_file, encoding='gb2312')
		df["DateTime"] = df["Date"] + " " + df["Time"]
		df["DateTime"] = pd.to_datetime(df["DateTime"], format="%Y-%m-%d %H:%M:%S").dt.round('60s')

		# 检查时区调整时间
		if self.type.lower() == 'sim':
			if self.TradingSession == "":
				self.set_Trading_session(str(df['TradingSession1'].tolist()[0]))
			if self.TradingSession.split('-')[0] != '090000' and self.TradingSession.split('-')[0]  in ['160000', '040000']:
				df = self.fix_time_session(df)

		df = df[[
			'DateTime',
			'Trader',
			'BuyEntry',
			'BuyExit',
			'SellEntry',
			'SellExit'
		]]

		# 检验清洗数据
		for i in ['BuyEntry', 'BuyExit', 'SellEntry', 'SellExit']:
			df[i] = df[i].apply(self.chose_digit)
		df = df.dropna()

		if self.type.lower() == 'live':
			df['Trader'] = df['Trader']+'-Live'

		self.Band = pd.concat([self.Band, df])

	# 接收RawArbSignal.csv 或 BAND.csv
	def set_Bar(self, path_file):
		df = pd.read_csv(path_file, encoding='gb2312')
		df["DateTime"] = df["Date"] + " " + df["Time"]
		df["DateTime"] = pd.to_datetime(df["DateTime"], format="%Y-%m-%d %H:%M:%S").dt.round('60s')

		# 检查时区调整时间
		if self.type.lower() == 'sim':
			if self.TradingSession == "":
				self.set_Trading_session(str(df['TradingSession1'].tolist()[0]))
			if self.TradingSession.split('-')[0] != '090000' and self.TradingSession.split('-')[0] in ['160000', '040000']:
				df = self.fix_time_session(df)

		# 双腿合并
		df1 = df[[
			'DateTime',
			'Trader',
			'Ticker1',
			'Open1',
			'High1',
			'Low1',
			'Close1',
			'Volume1'
		]]
		df2 = df[[
			'DateTime',
			'Trader',
			'Ticker2',
			'Open2',
			'High2',
			'Low2',
			'Close2',
			'Volume2'
		]]
		df1.columns = ['DateTime', 'Trader', 'Ticker', 'Open', 'High', 'Low', 'Close', 'Volume']
		df2.columns = ['DateTime', 'Trader', 'Ticker', 'Open', 'High', 'Low', 'Close', 'Volume']
		df = pd.concat([df1, df2])

		# 检验清洗数据
		for i in ['Open', 'High', 'Low', 'Close', 'Volume']:
			df[i] = df[i].apply(self.chose_digit)
		df = df.dropna()

		if self.type.lower() == 'live':
			df['Trader'] = df['Trader']+'-Live'

		self.Bar = pd.concat([self.Bar, df])

	# 接收RawSignal.csv 或 SIG.csv
	def set_TargetPosition(self, path_file):
		df = pd.read_csv(path_file, encoding='gb2312')
		df["DateTime"] = df["Date"] + " " + df["Time"]
		df["DateTime"] = pd.to_datetime(df["DateTime"], format="%Y-%m-%d %H:%M:%S").dt.round('60s')

		# 检查时区调整时间
		if self.type.lower() == 'sim':
			if self.TradingSession == "":
				self.set_Trading_session(str(df['TradingSession1'].tolist()[0]))
			if self.TradingSession.split('-')[0] != '090000' and self.TradingSession.split('-')[0]  in ['160000', '040000']:
				df = self.fix_time_session(df)

		df = df[[
			'DateTime',
			'Trader',
			'TargetPosition'
		]]

		# 检验清洗数据
		for i in ['TargetPosition']:
			df[i] = df[i].apply(self.chose_digit)
		df = df.dropna()

		if self.type.lower() == 'live':
			df['Trader'] = df['Trader']+'-Live'

		self.TargetPosition = pd.concat([self.TargetPosition, df])

	# 接收trades.csv 或 通过db获取
	def set_Trades(self, path_file=''):
		def init_mssql(dict_db_info):
			db = dict_db_info['db']
			host = dict_db_info['host']
			user = dict_db_info['user']
			pwd = dict_db_info['pwd']

			mssql = MSSQL(host=host, user=user, pwd=pwd, db=db)
			func_sql_exec = mssql.ExecQuery
			return mssql, func_sql_exec

		def set_trader_name(s):
			s = str(s)
			s = s.replace('@Long', '')
			s = s.replace('@Short', '')
			return s

		if self.type.lower() == 'sim':
			df = pd.read_csv(path_file, encoding='gb2312')
			df["DateTime"] = df["Date"] + " " + df["Time"]
			df["DateTime"] = pd.to_datetime(df["DateTime"], format="%Y-%m-%d %H:%M:%S").dt.round('60s')

			# 检查时区调整时间
			if self.TradingSession.split('-')[0] != '090000' and self.TradingSession.split('-')[0] in ['160000', '040000']:
				df = self.fix_time_session(df)
			# 字段转换
			df['Direction'] = df['Direction'].apply(
				lambda x: int(1)*(x == 'Buy')+int(-1)*(x == 'Sell')
			)
			df['OffsetFlag'] = df['OffsetFlag'].apply(
				lambda x: int(1)*(x == 'Open')+int(-1)*(x == 'FlatToday')+int(-1)*(x == 'Flat')
			)

			df = df[[
				'DateTime',
				'Trader',
				'Ticker',
				'Direction',
				'OffsetFlag',
				'TradedPrice',
				'TradedVolume',
				'Commission'
			]]

			# 检验清洗数据
			for i in ['TradedVolume']:
				df[i] = df[i].apply(self.chose_digit)
			df = df.dropna()

			self.Trades = df
		else:
			# 从db取数据
			dict_db_info = {
				'db': "Platinum.Settle",
				'host': 'atsasset.com',
				'user': 'sa',
				'pwd': 'st@s2013'
			}

			mssql, func_sql_exec = init_mssql(dict_db_info)

			trader_short_name = self.name.split('@')[0]
			trader_port = self.name.split('@')[-1]

			sql = '''
			SELECT TOP (1000) [CreateTime]
			      ,[Trader]
			      ,[Ticker]
			      ,[TradedPrice]
			      ,[TradedVolume]
			      ,[Commission]
			      ,[Direction]
			      ,[OffsetFlag]
			  FROM [Platinum.Settle].[dbo].[SettleTrades]
			  where trader like '%%%s%%%s%%' and mode=1 and createtime > '2019-01-01'
			''' % (trader_short_name, trader_port)

			re_sql = func_sql_exec(sql)
			mssql.close()

			df = pd.DataFrame(
				re_sql,
				columns=['DateTime', 'Trader', 'Ticker', 'TradedPrice', 'TradedVolume', 'Commission', 'Direction', 'OffsetFlag']
			)
			df["DateTime"] = pd.to_datetime(df["DateTime"], format="%Y-%m-%d %H:%M:%S").dt.round('60s')
			df['Trader'] = df['Trader'].apply(set_trader_name)
			# 检验清洗数据
			for i in ['TradedVolume']:
				df[i] = df[i].apply(self.chose_digit)
			df = df.dropna()

			self.Trades = df
