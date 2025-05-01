from Controller.Http import web_service
from Controller.Miner import miner_service

web_service.ListenThread()

miner_service.start()