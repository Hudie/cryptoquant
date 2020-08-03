# cryptoquant
Quant framework for crypto market using Python

### Requirements
 - Python3.7 or above
 - pip install tornado zmq websockets numpy

### Run
 - Edit config.py
 - Run Deribit market data service: `python3 service/deribit_future_md.py`
 - Run Deribit transaction data service: `python3 service/deribit_td.py`
 - Edit and run the arbitrage strategy: `python3 strategy/deribit_cross_future.py`

Then you can check out the logs to see if the services run as you expected. Supervisord is strongly recommended to be used to manage the services.