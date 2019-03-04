import os
import time


d_BAND = {}
d_SIG = {}

header_SIG = 'Date,Time,Trader,Ticker,TargetPosition,Price,ModifiedPosition,Open,High,Low,Close,Volume,Bid,Ask,TradingSession,InitX\n'
header_BAND = 'Date,Time,Trader,Ticker1,Ticker2,Entry1,Entry2,BuyEntry,BuyExit,SellEntry,SellExit,Open1,High1,Low1,Close1,Volume1,Bid1,Ask1,TradingSession1,Open2,High2,Low2,Close2,Volume2,Bid2,Ask2,TradingSession2,InitX\n'

# path_root = r'C:\Users\Jeffery-user\Desktop\data\test_getdata'
path_root = os.getcwd()
path_log = os.path.join(path_root, 'Logs')

for i in os.listdir(path_log):
	if i.split('_')[0] != 'TraderLogs':
		continue
	path_trader_log = os.path.join(path_log, i)
	for j_file_name in os.listdir(path_trader_log):
		if j_file_name[:4] == 'BAND':
			path_file = os.path.join(path_trader_log, j_file_name)
			with open(path_file, 'r', encoding='gb2312') as f:
				s = f.read()
				s = s.replace(header_BAND, '')
				if j_file_name not in d_BAND.keys():
					d_BAND[j_file_name] = header_BAND
				d_BAND[j_file_name] = d_BAND[j_file_name] + s
		elif j_file_name[:3] == 'SIG':
			path_file = os.path.join(path_trader_log, j_file_name)
			with open(path_file, 'r', encoding='gb2312') as f:
				s = f.read()
				s = s.replace(header_SIG, '')
				if j_file_name not in d_SIG.keys():
					d_SIG[j_file_name] = header_SIG
				d_SIG[j_file_name] = d_SIG[j_file_name] + s
		else:
			continue

td = time.strftime('%Y%m%d',time.localtime(time.time()))
path_log = os.path.join(path_root, 'liveLog-%s' % td)
if not os.path.exists(path_log):
	os.mkdir(path_log)

for i in d_SIG.keys():
	path_file = os.path.join(path_log, i)
	s = d_SIG[i]
	with open(path_file, 'w') as f:
		f.write(s)
		print('writing %s' % i)

for i in d_BAND.keys():
	path_file = os.path.join(path_log, i)
	s = d_BAND[i]
	with open(path_file, 'w') as f:
		f.write(s)
		print('writing %s' % i)

print('Finish')
