from Controller.Http import web_service
from Controller.Miner import miner_service

web_service.ListenThread()

# Service that reads data from miners
miner_service.start()    