# -*- coding:utf-8 -*-
__author__ = 'zzx'

from EmQuantAPI import *
from datetime import timedelta, datetime
import time as _time

def mainCallback(quantdata):
    """
    mainCallback 是主回调函数，可捕捉如下错误
    在start函数第三个参数位传入，该函数只有一个为c.EmQuantData类型的参数quantdata
    :param quantdata:c.EmQuantData
    :return:
    """
    print "mainCallback",str(quantdata)
    #登录掉线或者 登陆数达到上线（即登录被踢下线） 这时所有的服务都会停止
    if str(quantdata.ErrorCode) == "10001011" or str(quantdata.ErrorCode) == "10001009":
        print "Your account is disconnect. You can force login automatically here if you need."
    #行情登录验证失败（每次连接行情服务器时需要登录验证）或者行情流量验证失败时，会取消所有订阅，用户需根据具体情况处理
    elif str(quantdata.ErrorCode) == "10001021" or str(quantdata.ErrorCode) == "10001022":
        print "Your all csq subscribe have stopped."
    #行情服务器断线自动重连连续6次失败（1分钟左右）不过重连尝试还会继续进行直到成功为止，遇到这种情况需要确认两边的网络状况
    elif str(quantdata.ErrorCode) == "10002009":
        print "Your all csq subscribe have stopped, reconnect 6 times fail."
    #行情订阅遇到一些错误(这些错误会导致重连，错误原因通过日志输出，统一转换成EQERR_QUOTE_RECONNECT在这里通知)，正自动重连并重新订阅,可以做个监控
    elif str(quantdata.ErrorCode) == "10002012":
        print "csq subscribe break on some error, reconnect and request automatically."
    #资讯服务器断线自动重连连续6次失败（1分钟左右）不过重连尝试还会继续进行直到成功为止，遇到这种情况需要确认两边的网络状况
    elif str(quantdata.ErrorCode) == "10002014":
        print "Your all cnq subscribe have stopped, reconnect 6 times fail."
    # 资讯订阅遇到一些错误(这些错误会导致重连，错误原因通过日志输出，统一转换成EQERR_INFO_RECONNECT在这里通知)，正自动重连并重新订阅,可以做个监控
    elif str(quantdata.ErrorCode) == "10002013":
        print "cnq subscribe break on some error, reconnect and request automatically."
    # 资讯登录验证失败（每次连接资讯服务器时需要登录验证）或者资讯流量验证失败时，会取消所有订阅，用户需根据具体情况处理
    elif str(quantdata.ErrorCode) == "10001024" or str(quantdata.ErrorCode) == "10001025":
        print "Your all cnq subscribe have stopped."
    else:
        pass
def startCallback(message):
    print "[EmQuantAPI Python]", message
    return 1
def csqCallback(quantdata):
    """
    csqCallback 是csq订阅时提供的回调函数模板。该函数只有一个为c.EmQuantData类型的参数quantdata
    :param quantdata:c.EmQuantData
    :return:
    """
    print "csqCallback,", str(quantdata)

def cstCallBack(quantdata):
    """
    cstCallBack 是cst订阅时提供的回调函数模板。该函数只有一个为c.EmQuantData类型的参数quantdata
    :param quantdata:c.EmQuantData
    :return:
    """
    for i in range(0, len(quantdata.Codes)):
        length = len(quantdata.Dates)
        for it in quantdata.Data.keys():
            print it
            for k in range(0, length):
                for j in range(0, len(quantdata.Indicators)):
                    print quantdata.Data[it][j * length + k], " ",
                print ""

def cnqCallback(quantdata):
    """
    cnqCallback 是cnq订阅时提供的回调函数模板。该函数只有一个为c.EmQuantData类型的参数quantdata
    :param quantdata:c.EmQuantData
    :return:
    """
    # print "cnqCallback,", str(quantdata)
    print "cnqCallback,"
    for code in quantdata.Data:
        total = len(quantdata.Data[code])
        for k in range(0, len(quantdata.Data[code])):
            print quantdata.Data[code][k]

#调用登录函数（可以使用用户名密码登录，也可以不传账密激活后使用令牌登录）
UserName = raw_input("Please Enter your UserName: ")
Password = raw_input("Please Enter your Password: ")
startoptions = "ForceLogin=1" + ",UserName=" + UserName + ",Password=" + Password;
loginResult = c.start(startoptions, '', mainCallback)
#激活后直接登录，无需输入账密
#loginResult = c.start("ForceLogin=1", '', mainCallback)
if(loginResult.ErrorCode != 0):
    print "login in fail"
    exit()

# cfc使用范例
data = c.cfc("000001.SZ,000001.SH,600000.SH,000000.TEST", "CODE,NAME,TEST", "FunType=css")
if data.ErrorCode != 0:
    print "request cfc Error, ", data.ErrorMsg
else:
    print u"cfc输出结果======分割线======"
    for indicator in data.Indicators:
        print indicator,
    print ""
    for key, value in data.Data.items():
        for v in value:
            print v,
        print ""

# cec使用范例
# data = c.cec("000001,600000,000000", "ReturnType=1,SecuType=1,SecuMarket=0")
data = c.cec("000001.SZ,000001.SH,600000.SH,000000.TEST", "ReturnType=0")
if data.ErrorCode != 0:
    print "request cec Error, ", data.ErrorMsg
else:
    print u"cec输出结果======分割线======"
    for indicator in data.Indicators:
        print indicator,
    print ""
    for key, value in data.Data.items():
        for v in value:
            print v,
        print ""


# 资讯查询使用范例
data = c.cfn("300059.SZ,600519.SH,300024.SZ", "companynews,industrynews", eCfnMode_EndCount,
             "starttime=20190501010000,endtime=20190725,count=10")
print u"cfn输出结果======分隔线======"
if (not isinstance(data, c.EmQuantData)):
    print data
else:
    if (data.ErrorCode != 0):
        print "request cfn Error, ", data.ErrorMsg
    else:
        for code in data.Data:
            total = len(data.Data[code])
            for k in range(0, len(data.Data[code])):
                print data.Data[code][k]

#板块树查询使用范例
data = c.cfnquery("")
print u"cfnquery输出结果======分隔线======"
if(not isinstance(data, c.EmQuantData)):
    print data
else:
    if(data.ErrorCode != 0):
        print "request cfnquery Error, ", data.ErrorMsg
    else:
        for code in data.Codes:
            for i in range(0, len(data.Indicators)):
                    print data.Data[code][i]


#资讯订阅使用范例
data = c.cnq("S888005002API", "sectornews", "", cnqCallback)
if data.ErrorCode != 0:
    print "request cnq Error, ", data.ErrorMsg
else:
    print u"cnq输出结果======分隔线======"
    _time.sleep(60)
    text = raw_input("press any key to cancel cnq \r\n")
    #取消订阅
    data = c.cnqcancel(data.SerialID)

# cmc使用范例
data = c.cmc("300059.SZ", "OPEN,CLOSE,HIGH", (datetime.today() + timedelta(-6)).strftime("%Y-%m-%d"),
             datetime.today().strftime("%Y-%m-%d"), "Ispandas=0")
print u"cmc输出结果======分隔线======"
if (not isinstance(data, c.EmQuantData)):
    print data
else:
    if (data.ErrorCode != 0):
        print "request cmc Error, ", data.ErrorMsg
    else:
        for i in range(0, len(data.Indicators)):
            for j in range(0, len(data.Dates)):
                print "indicator=%s, value=%s" % (data.Indicators[i], str(data.Data[i][j]))

# csd使用范例
data = c.csd("300059.SZ,600425.SH", "open,close", "2016-07-01", "2016-07-06",
             "RowIndex=1,period=1,adjustflag=1,curtype=1,pricetype=1,year=2016,Ispandas=0")
print u"csd输出结果======分隔线======"
if (not isinstance(data, c.EmQuantData)):
    print data
else:
    if (data.ErrorCode != 0):
        print "request csd Error, ", data.ErrorMsg
    else:
        for code in data.Codes:
            for i in range(0, len(data.Indicators)):
                for j in range(0, len(data.Dates)):
                    print data.Data[code][i][j]

# css使用范例
data = c.css("300059.SZ,000002.SZ", "open,close", "TradeDate=20170308, Ispandas=0")
print u"css输出结果======分隔线======"
if (not isinstance(data, c.EmQuantData)):
    print data
else:
    if (data.ErrorCode != 0):
        print "request css Error, ", data.ErrorMsg
    else:
        for code in data.Codes:
            for i in range(0, len(data.Indicators)):
                print data.Data[code][i]

# cses使用范例
data = c.cses("B_011001003,B_018005001001,B_007159,B_014010016006002,B_003002001005,B_027004002003001", "SECTOPREAVG,CFOPSAVG,MANAEXPAVG,SECTORCOUNT", "TradeDate=2020-10-19,DelType=1,IsHistory=0,type=1,ReportDate=2020-06-30,DataAdjustType=1,PREDICTYEAR=2020,StartDate=2019-05-30,EndDate=2020-10-19,Payyear=2019")
print u"cses输出结果======分隔线======"
if (not isinstance(data, c.EmQuantData)):
    print data
else:
    if (data.ErrorCode != 0):
        print "request cses Error, ", data.ErrorMsg
    else:
        for code in data.Codes:
            for i in range(0, len(data.Indicators)):
                print data.Data[code][i]

# sector使用范例
# 001004 全部A股板块  "001004", "2022-05-26", "Ispandas=0"
data = c.sector("001004", "2022-05-26", "Ispandas=0")
if (not isinstance(data, c.EmQuantData)):
    print data
else:
    if data.ErrorCode != 0:
        print "request sector Error, ", data.ErrorMsg
    else:
        print u"sector输出结果======分隔线======"
        for code in data.Data:
            print code

# tradedate使用范例
data = c.tradedates("2016-07-01", "2016-07-12")
if data.ErrorCode != 0:
    print "request tradedates Error, ", data.ErrorMsg
else:
    print u"tradedate输出结果======分隔线======"
    for item in data.Data:
        print item

# getdate使用范例
data = c.getdate("20160426", -3, "Market=CNSESH")
if data.ErrorCode != 0:
    print "request getdate Error, ", data.ErrorMsg
else:
    print u"getdate输出结果======分隔线======"
    print data.Data

# 实时行情订阅使用范例
data = c.csq("300059.SZ,002716.SZ,600834.SH,600616.SH", "TIME,OPEN,HIGH,LOW,NOW,AMOUNT", "Pushtype=2", csqCallback)
if data.ErrorCode != 0:
    print "request csq Error, ", data.ErrorMsg
else:
    print u"csq输出结果======分隔线======"
    _time.sleep(2)
    text = raw_input("press any key to cancel csq \r\n")
    # 取消订阅
    data = c.csqcancel(data.SerialID)

# 实时行情订阅使用范例
data = c.csq('AUDUSD.FX', 'Time,now', 'Pushtype=0,alltick=1', csqCallback)
if data.ErrorCode != 0:
    print "request csq Error, ", data.ErrorMsg
else:
    print u"csq输出结果======分隔线======"
    _time.sleep(2)
    text = raw_input("press any key to cancel csq \r\n")
    # 取消订阅
    data = c.csqcancel(data.SerialID)

# 日内跳价服务使用范例
data = c.cst('300059.SZ,600000.SH', 'TIME,OPEN,HIGH,LOW,NOW', '100000', '101000', "", cstCallBack)
if data.ErrorCode != 0:
    print "request cst Error, ", data.ErrorMsg
else:
    print u"cst输出结果======分割线======"
    _time.sleep(2)
    raw_input("press any key to quit cst \r\n")

# 行情快照使用范例
data = c.csqsnapshot(
    "000005.SZ,600602.SH,600652.SH,600653.SH,600654.SH,600601.SH,600651.SH,000004.SZ,000002.SZ,000001.SZ,000009.SZ",
    "PRECLOSE,OPEN,HIGH,LOW,NOW,AMOUNT", "IsPandas=0")
if not isinstance(data, c.EmQuantData):
    print(data)
else:
    if data.ErrorCode != 0:
        print "request csqsnapshot Error, ", data.ErrorMsg
    else:
        print u"csqsnapshot输出结果======分割线======"
        for key, value in data.Data.items():
            print key, ">>> ",
            for v in value:
                print v,
            print ""

# 获取专题报表使用范例 "StockInfo", "", "StartDate=2019-07-01,EndDate=2019-07-02,Ispandas=0"
data = c.ctr("StockInfo", "", "StartDate=2019-07-01,EndDate=2019-07-02,Ispandas=0")
if not isinstance(data, c.EmQuantData):
    print(data)
else:
    if data.ErrorCode != 0:
        print "request ctr Error, ", data.ErrorMsg
    else:
        print u"ctr输出结果======分割线======"
        for indicator in data.Indicators:
            print indicator,
        print ""
        for key, value in data.Data.items():
            for v in value:
                print v,
            print ""


# 选股使用范例
data = c.cps("B_001004", "s0,OPEN,2017/2/27,1;s1,NAME", "[s0]>0", "orderby=rd([s0]),top=max([s0],100)")
if data.ErrorCode != 0:
    print "request cps Error, ", data.ErrorMsg
else:
    print u"cps输出结果======分割线======"
    for it in data.Data:
        print it

# 宏观指标服务
data = c.edb("EMM00087117", "IsPublishDate=1,RowIndex=1,Ispandas=1")
if not isinstance(data, c.EmQuantData):
    print(data)
else:
    if (data.ErrorCode != 0):
        print "request edb Error, ", data.ErrorMsg
    else:
        print "edbid           date          ",
        for ind in data.Indicators:
            print ind, "   ",
        print ""
        for code in data.Codes:
            for j in range(0, len(data.Dates)):
                print code, "    ", data.Dates[j], "   ",
                for i in range(0, len(data.Indicators)):
                    print data.Data[code][i][j], "   ",
                print ""
# 宏观指标id详情查询
data = c.edbquery("EMM00058124,EMM00087117,EMG00147350")
if (data.ErrorCode != 0):
    print("request edbquery Error, ", data.ErrorMsg)
else:
    print "edbid         ",
    for ind in data.Indicators:
        print ind, "   ",
    print ""
    for code in data.Codes:
        for j in range(0, len(data.Dates)):
            print code, "    ", "   ",
            for i in range(0, len(data.Indicators)):
                print data.Data[code][i][j], "   ",
            print ""

# 新建组合
data = c.pcreate("quant001", "组合牛股", 100000000, "这是一个牛股的组合")
if (data.ErrorCode != 0):
    print "request pcreate Error, ", data.ErrorMsg
else:
    print "create succeed"

#组合资金调配
data = c.pctransfer("quant001", "IN", "2019-08-13", 10000, "追加资金", "TRANSFERTYPE=1")
if(data.ErrorCode != 0):
    print "request pctransfer Error, ", data.ErrorMsg
else:
    print "pctransfer succeed"

#组合下单
orderdict = {'code':['300059.SZ','600000.SH'],
             'volume':[1000,200],
             'price':[13.11,12.12],
             'date':['2017-08-14','2017-08-24'],
             'time':['14:22:18','14:22:52'],
             'optype':[eOT_buy,eOT_buy],
             'cost':[0,3],
             'rate':[0,2],
             'destvolume':[0,0],
             'weight':[0.1,0.1]}

data = c.porder("quant001", orderdict, "this is a test")
if(data.ErrorCode != 0):
    print "porder Error, ", data.ErrorMsg
else:
    print "order succeed"

# 组合报表查询
data = c.preport("quant001", "record", "startdate=2017/07/12,enddate=2018/01/15")
if (data.ErrorCode != 0):
    print "request preport Error, ", data.ErrorMsg
else:
    for ind in data.Indicators:
        print ind, "   ",
    print ""
    for k in data.Data:
        for it in data.Data[k]:
            print it, "   ",
        print ""

# 组合信息查询
data = c.pquery()
if (data.ErrorCode != 0):
    print("request pquery Error, ", data.ErrorMsg)
else:
    print "[key]:",
    for index in range(0, len(data.Indicators)):
        print "\t", data.Indicators[index],
    print ""
    for k, v in data.Data.items():
        print k, ": ",
        for vv in v:
            print "\t", vv,
        print ""

# 删除组合
data = c.pdelete("quant001")
if (data.ErrorCode != 0):
    print "request pdelete Error, ", data.ErrorMsg
else:
    print "delete succeed"

# 获取区间日期内的交易日天数
data = c.tradedatesnum("2018-01-01", "2018-09-15")
if data.ErrorCode != 0:
    print "request tradedatesnum Error, ", data.ErrorMsg
else:
    print u"tradedatesnum======分割线======"
    print data.Data


# 退出
data = logoutResult = c.stop()
print 'demo end'
