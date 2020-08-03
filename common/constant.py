from enum import Enum, unique

MAX_NP_DATETIME64     = "2099-01-01T00:00:00"  # max datetime allowed in system

@unique
class Ecn(Enum):                               # ecn = electronic connection network, which includes exchange, otc, darkpool, etc
    binance           = 1
    deribit           = 2
    okex	      = 3
    unknown           = -1

@unique
class EcnStatus(Enum):                    
    init              = 1                      # service setup, yet trying to connect 
    connected         = 2            
    disconnected      = 3
    error             = 4                      # fail to connect or reconnect
    unknown           = -1

@unique
class Broker(Enum):
    binance_dma       = 1                      # binance direct market access
    deribit_dma       = 2
    unknown           = -1

@unique
class MarketDataApi(Enum):
    binance_md_restful   = 1
    binance_md_websocket = 2
    deribit_md_restful   = 3
    deribit_md_websocket = 4
    okex_md_restful	 = 5
    okex_md_websocket	 = 6
    unknown              = -1

@unique
class TradeDataApi(Enum):
    binance_td_restful   = 1
    binance_td_websocket = 2
    deribit_td_restful   = 3
    deribit_td_websocket = 4
    okex_td_restful	 = 5
    okex_td_websocket	 = 6
    unknown              = -1

@unique
class UserType(Enum):                          # typical rights include, code read, code write, money transfer, order read, order trade, admin, approval
    developer         = 1                      # code read, code write, order read
    trader            = 2                      # code read, order read, order trade
    treasury          = 3                      # order read, money transfer
    manager           = 4                      # admin, approval, but DEFINITELY no money transfer    
    unknown           = -1        

@unique
class InstrumentBaseType(Enum):                # btc option is the name of an instrument, btc-25-oct-10000-c is a particular contract's ticker
    stock             = 1
    fx                = 2
    bond              = 3
    commodity         = 4
    crypto            = 5
    unknown           = -1

@unique
class InstrumentDerivativeType(Enum):  
    spot              = 1
    futures           = 2
    option            = 3
    perpetual         = 4
    unknown           = -1

@unique
class Currency(Enum):                 
    btc               = "btc"
    eth               = "eth"
    usdt              = "usdt"
    usdc              = "usdc"
    usd               = "usd"
    cny               = "cny"
    jpy               = "jpy"
    unknown           = "unknown"

@unique
class FeeType(Enum):                 
    percentage        = 1
    absolute          = 2
    deribit_option    = 3
    unknown           = -1

class OptionType(Enum):
    call              = "C"
    put               = "P"  
    unknown           = "U"

@unique
class OrderDirection(Enum):
    buy               = 1
    sell              = -1 
    unknown           = 0

@unique
class OrderType(Enum):
    limit             = "limit"
    market            = "market"
    unknown           = "unknown"

@unique
class OrderTimeInForce(Enum):
    gtc               = 1                         # good until cancel
    fok               = 2                         # fill or kill, no parital fills
    fak               = 3                         # fill and kill
    unknown           = -1

@unique
class OrderStatus(Enum):
    pending           = 1
    acked             = 2
    reject            = 3
    cancel_pending    = 4
    canceled          = 5
    filled            = 6  
    partial_filled    = 7
    unknown           = -1

@unique
class EventType(Enum):
    unknown           = -1

@unique
class Product(Enum):
    btc_option        = 'btc_option'
