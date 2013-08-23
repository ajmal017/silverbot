#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
# This script is an exmple of using the generated code within IbPy in
# the same manner as the Java code.  We subclass EWrapper and give an
# instance of the wrapper to an EClientSocket.
##

from random import randint
from sys import argv
from time import sleep, strftime

from ib.ext.Contract import Contract
from ib.ext.EWrapper import EWrapper
from ib.ext.EClientSocket import EClientSocket
from ib.ext.ExecutionFilter import ExecutionFilter

import sys

def showmessage(message, mapping):
    try:
        del(mapping['self'])
    except (KeyError, ):
        pass
    items = mapping.items()
    items.sort()
    print '### %s' % (message, )
    for k, v in items:
        print '    %s:%s' % (k, v)

def gen_tick_id():
    i = randint(100, 10000)
    while True:
        yield i
        i += 1
gen_tick_id = gen_tick_id().next

class Orders:
    order_list = [] 
    def add(self, orderId, symbol, qty, price, action):
        order = {'orderId': orderId, 'symbol': symbol, 'qty': qty, 'price': price, 'action': action}
        self.order_list.append(order)

class Parameters:
    bid = 0
    ask = 0
    def spread(self):
        f = open('parameters.yaml', 'r')
        temp = yaml.safe_load(f)
        f.close()
        return temp["spread"]
    def floor(self):
        f = open('parameters.yaml', 'r')
        temp = yaml.safe_load(f)
        f.close()
        return float(temp["floor"])
    def step(self):
        f = open('parameters.yaml', 'r')
        temp = yaml.safe_load(f)
        f.close()
        return float(temp["step"])
    def symbol(self):
        return "SLV"
    def qty(self):
        f = open('parameters.yaml', 'r')
        temp = yaml.safe_load(f)
        f.close()
        return int(temp["qty"])
    def ceiling(self):

        if self.bid <= 0:
            return 0
        else:
            ceiling = self.bid

            # Gap lower so market has to drop before we buy anything
            gap = self.spread() * 0.90
            ceiling = ceiling - gap

            return ceiling
    def tickers(self):
        return {1: "SLV"}

class ReferenceWrapper(EWrapper):
    orders = None
    order_ids = [0]
    parameters = None

    def __init__(self, parameters):
        # Variable initialization
        self.orders = Orders()
        self.parameters = parameters

        print "--> Initialized wrapper"

    def makeContract(self, symbol):
        contract = Contract()
        contract.m_symbol = symbol
        contract.m_secType = 'STK'
        contract.m_exchange = 'SMART'
        contract.m_primaryExch = 'SMART'
        contract.m_currency = 'USD'
        contract.m_localSymbol = symbol
        return contract

    def tickPrice(self, tickerId, field, price, canAutoExecute):
        showmessage('tickPrice', vars())

    def tickSize(self, tickerId, field, size):
        showmessage('tickSize', vars())
    
    def tickGeneric(self, tickerId, tickType, value):
        showmessage('tickGeneric', vars())

    def tickString(self, tickerId, tickType, value):
        showmessage('tickString', vars())
    
    def tickEFP(self, tickerId, tickType, basisPoints, formattedBasisPoints, impliedFuture, holdDays, futureExpiry, dividendImpact, dividendsToExpiry):
        showmessage('tickEFP', vars())

    def tickOptionComputation(self, tickerId, field, impliedVolatility, delta):
        showmessage('tickOptionComputation', vars())

    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeId):
        pass #showmessage('orderStatus', vars())

    def openOrder(self, orderId, contract, order, state):
        orderId = order.m_orderId
        symbol = contract.m_symbol
        qty = order.m_totalQuantity
        price = order.m_lmtPrice
        action = order.m_action
        self.orders.add(orderId, symbol, qty, price, action)
        
        order = [orderId, symbol, qty, price, action]
        print "--> Open order:%s Status:%s Warning:%s" % (order, state.m_status, state.m_warningText)

    def openOrderEnd(self):
        showmessage('openOrderEnd', vars())

    def connectionClosed(self):
        showmessage('connectionClosed', {})

    def updateAccountValue(self, key, value, currency, accountName):
        showmessage('updateAccountValue', vars())

    def updatePortfolio(self, contract, position, marketPrice, marketValue, averageCost, unrealizedPNL, realizedPNL, accountName):
        showmessage('updatePortfolio', vars())

    def updateAccountTime(self, timeStamp):
        showmessage('updateAccountTime', vars())

    def accountDownloadEnd(self, accountName):
        showmessage('accountDownloadEnd', vars())

    def nextValidId(self, orderId):
        self.order_ids.append(orderId)

    def contractDetails(self, contractDetails):
        showmessage('contractDetails', vars())

    def bondContractDetails(self, contractDetails):
        showmessage('bondContractDetails', vars())

    def contractDetailsEnd(self, reqId):
        showmessage('contractDetailsEnd', vars())

    def execDetails(self, orderId, contract, execution):
        showmessage('execDetails', vars())

    def execDetailsEnd(self, reqId):
        showmessage('execDetailsEnd', vars())

    def error(self, id=None, errorCode=None, errorMsg=None):
        if errorCode == 2104:
            print "--> %s" % errorMsg
        else:
            showmessage('error', vars())
    
    def error_0(self, strval):
        showmessage('error_0', vars())
    
    def error_1(self, strval):
        showmessage('error_1', vars())
        
    def updateMktDepth(self, tickerId, position, operation, side, price, size):
        showmessage('updateMktDepth', vars())

    def updateMktDepthL2(self, tickerId, position, marketMaker, operation, side, price, size):
        showmessage('updateMktDepthL2', vars())

    def updateNewsBulletin(self, msgId, msgType, message, origExchange):
        showmessage('updateNewsBulletin', vars())

    def managedAccounts(self, accountsList):
        pass #showmessage('managedAccounts', vars())

    def receiveFA(self, faDataType, xml):
        showmessage('receiveFA', vars())

    def historicalData(self, reqId, date, open, high, low, close, volume, count, WAP, hasGaps):
        showmessage('historicalData', vars())

    def scannerParameters(self, xml):
        showmessage('scannerParameters', vars())

    def scannerData(self, reqId, rank, contractDetails, distance, benchmark, projection):
        showmessage('scannerData', vars())

    def scannerDataEnd(self, reqId):
        showmessage('scannerDataEnd', vars())

    def realtimeBar(self, reqId, time, open, high, low, close, volume, wap, count):
        showmessage('realtimeBar', vars())

    def currentTime(self, time):
        showmessage('currentTime', vars())

    def fundamentalData(self, reqId, data):
        showmessage('fundamentalData', vars())

    def deltaNeutralValidation(self, reqId, underComp):
        showmessage('deltaNeutralValidation', vars())

    def tickSnapshotEnd(self, reqId):
        showmessage('tickSnapshotEnd', vars())

    def marketDataType(self, reqId, marketDataType):
        showmessage('marketDataType', vars())

    def commissionReport(self, commissionReport):
        showmessage('commissionReport', vars())


allMethods = []
def ref(method):
    allMethods.append(method.__name__)
    return method

class ReferenceApp:
    parameters = None
    def __init__(self, host='localhost', port=7496, clientId=0):
        self.host = host
        self.port = port
        self.clientId = clientId
        self.parameters = Parameters()
        self.wrapper = ReferenceWrapper(self.parameters)
        self.connection = EClientSocket(self.wrapper)
        
    @ref
    def eConnect(self):
        self.connection.eConnect(self.host, self.port, self.clientId)

    @ref
    def reqAccountUpdates(self):
        self.connection.reqAccountUpdates(1, '')

    @ref
    def reqOpenOrders(self):
        self.connection.reqOpenOrders()

    @ref
    def reqExecutions(self):
        filt = ExecutionFilter()
        self.connection.reqExecutions(filt)

    @ref
    def reqIds(self):
        self.connection.reqIds(10)

    @ref
    def reqNewsBulletins(self):
        self.connection.reqNewsBulletins(1)

    @ref
    def cancelNewsBulletins(self):
        self.connection.cancelNewsBulletins()

    @ref
    def setServerLogLevel(self):
        self.connection.setServerLogLevel(3)

    @ref
    def reqAutoOpenOrders(self):
        self.connection.reqAutoOpenOrders(1)

    @ref
    def reqAllOpenOrders(self):
        self.connection.reqAllOpenOrders()

    @ref
    def reqManagedAccts(self):
        self.connection.reqManagedAccts()

    @ref
    def requestFA(self):
        self.connection.requestFA(1)

    @ref
    def reqMktData(self):
        for tick_id, symbol in self.parameters.tickers().iteritems():
            contract = app.wrapper.makeContract(symbol)
            self.connection.reqMktData(tick_id, contract, [], False)

    @ref
    def reqHistoricalData(self):
        contract = Contract()
        contract.m_symbol = 'QQQQ'
        contract.m_secType = 'STK'
        contract.m_exchange = 'SMART'
        endtime = strftime('%Y%m%d %H:%M:%S')
        self.connection.reqHistoricalData(
            tickerId=1,
            contract=contract,
            endDateTime=endtime,
            durationStr='1 D',
            barSizeSetting='1 min',
            whatToShow='TRADES',
            useRTH=0,
            formatDate=1)

    @ref
    def eDisconnect(self):
        sleep(5)
        self.connection.eDisconnect()


if __name__ == '__main__':
    app = ReferenceApp()
    methods = argv[1:]

    app.eConnect()
    app.reqMktData()
    
    while True:
        line = sys.stdin.readline()[0:-1]
        if line == "quit" or line == "exit":
            print "--> Exiting..."
            sys.exit()

    #if not methods:
        #methods = ['eConnect', 'eDisconnect', ]
    #elif methods == ['all']:
        #methods = allMethods
    #if 'eConnect' not in methods:
        #methods.insert(0, 'eConnect')
    #if 'eDisconnect' not in methods:
        #methods.append('eDisconnect')
#
    #print '### calling functions:', str.join(', ', methods)
    #for mname in methods:
        #call = getattr(app, mname, None)
        #if call is None:
            #print '### warning: no call %s' % (mname, )
        #else:
            #print '## calling', call.im_func.func_name
            #call()
            #print '## called', call.im_func.func_name

