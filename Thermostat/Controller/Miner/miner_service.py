"""
Class to manage the real time service reading data from miners and 
saving it locally
"""
import threading
import time
from ..utils import Utils
from .miner import Miner

class MinerService:
    def __init__(self, jObj):
        """Initialize a MinerService instance with a JSON object."""
        self.jObj = jObj  # Specific miner JSON object
        self.lock = Utils.threadingLock()  # Thread-safe lock for jObj updates
        self.stop_event = threading.Event()  # Control thread termination
        self.thread = None  # Reference to the instance's thread
        # Subscribe to Pub/Sub topic using the PubSub instance
        Utils.pubsub_instance.subscribe(Utils.PubSub.TOPIC_DATA_HAS_CHANGED, self.dataHasChanged)

    def dataHasChanged(self, event):
        event_action, jObj = checkEventData(event)
        # Check if action is 'update' or 'delete'
        if event_action is None or event_action not in ['update', 'delete']:
            Utils.logger.info(f"dataHasChanged: Invalid action value: {event['action']}")
            return
        # Check if uuid matches the instance's uuid
        if jObj['uuid'] != self.jObj['uuid']:
            Utils.logger.info(f"dataHasChanged: UUID mismatch. Self.uuid: {self.jObj['uuid']}, Published.uuid: {jObj['uuid']}")
            return
        # Handle 'delete' action
        if event_action == 'delete':
            Utils.logger.info(f"dataHasChanged: Deleting MinerService for uuid {self.jObj['uuid']}")
            self.stop()  # Stop the instance's thread
            miner_service_manager.stop_by_uuid(self.jObj['uuid'])  # Remove from manager
            return
        # Handle 'update' action
        with self.lock:  # Update jObj in memory
            self.jObj = jObj

    def run(self):
        """Continuous process executed by the instance's thread."""
        while not self.stop_event.is_set():
            # Example continuous process: access jObj and perform actions
            with self.lock:
                uuid = self.jObj.get('uuid', 'unknown')
            Utils.logger.info(f"running...")
            # Replace with actual logic, e.g.:
            # - Read miner data
            # - Publish events
            # - Update state
            time.sleep(5)  # Simulate work (replace with actual logic)

    def start(self):
        """Start the thread for this instance."""
        if self.thread is None or not self.thread.is_alive():
            self.stop_event.clear()  # Reset stop event
            self.thread = threading.Thread(target=self.run, name=f"MinerService-{self.jObj.get('uuid', 'unknown')}")
            self.thread.start()
            Utils.logger.info(f"Started thread for MinerService {self.jObj.get('uuid', 'unknown')}")

    def stop(self):
        """Stop the thread and clean up the instance."""
        if self.thread and self.thread.is_alive():
            self.stop_event.set()  # Signal thread to stop
            self.thread.join()  # Wait for thread to terminate
            Utils.logger.info(f"Stopped thread for MinerService {self.jObj.get('uuid', 'unknown')}")
        # Unsubscribe from Pub/Sub using the PubSub instance
        Utils.pubsub_instance.unsubscribe(Utils.PubSub.TOPIC_DATA_HAS_CHANGED, self.dataHasChanged)

class MinerServiceManager:
    def __init__(self):
        """Initialize the manager for MinerService instances."""
        self.services = {}  # Dictionary: uuid -> MinerService instance
        self.lock = threading.Lock()  # Thread-safe lock for services
        # Subscribe to Pub/Sub topic to handle delete events
        Utils.pubsub_instance.subscribe(Utils.PubSub.TOPIC_DATA_HAS_CHANGED, self.handle_data_changed)

    def add(self, jObj):
        uuid = jObj.get('uuid')
        with self.lock:
            if uuid and uuid not in self.services:
                service = MinerService(jObj)
                service.start()  # Start the instance's thread
                self.services[uuid] = service
                Utils.logger.info(f"Created MinerService for uuid {uuid}")

    def handle_data_changed(self, event):
        event_action, jObj = checkEventData(event)
        # Check if action is 'delete'
        if event_action is None:
            return
        if event_action == 'delete':
            # Remove the service for the given uuid
            self.stop_by_uuid(jObj['uuid'])
            return
        if event_action == 'add':
            self.add(jObj)

    def start(self):
        """Start MinerService for each jObj."""
        Utils.logger.info("MinerServiceManager.start")
        jAry = Miner.dataAsJson()
        for jObj in jAry:
            self.add(jObj)

    def stop_all(self):
        """Stop all threads and clear instances."""
        with self.lock:
            for uuid, service in list(self.services.items()):
                service.stop()
                del self.services[uuid]
            Utils.logger.info("All MinerService instances stopped and cleared")
        # Unsubscribe from Pub/Sub to prevent memory leaks
        Utils.pubsub_instance.unsubscribe(Utils.PubSub.TOPIC_DATA_HAS_CHANGED, self.handle_data_changed)

    def stop_by_uuid(self, uuid):
        """Stop a specific instance by uuid."""
        with self.lock:
            if uuid in self.services:
                service = self.services[uuid]
                service.stop()
                del self.services[uuid]
                Utils.logger.info(f"MinerService for uuid {uuid} stopped and cleared")

    def start_thread(self):
        """Start the manager in a separate thread."""
        server_thread = threading.Thread(target=self.start)
        server_thread.start()
        Utils.logger.info("MinerServiceManager.startThread")

# Global instance of the manager
miner_service_manager = MinerServiceManager()

def checkEventData(event):
    """Validate the event and return event['action'] as string and jObj as Dict"""
    # Check if event is a dictionary
    if not Utils.jsonCheckIsObj(event):
        Utils.logger.error(f"checkEventData: Event is not a dict: {event}")
        return None, None
    # Check if event contains 'action' key with string type
    if not Utils.jsonCheckKeyTypeStr(event, 'action', False, False):
        Utils.logger.error(f"checkEventData: Missing 'action' key")
        return None, None
    # Check if event contains 'data' key with string type
    if not Utils.jsonCheckKeyTypeStr(event, 'data', False, False):
        Utils.logger.error(f"checkEventData: Missing 'data' key")
        return None, None
    jObj = event['data']
    # Check if jObj is a dictionary
    if not Utils.jsonCheckIsObj(jObj):
        Utils.logger.error(f"checkEventData: DATA is not a dict: {jObj}")
        return None, None
    # Check if jObj contains 'uuid' key with string type
    if not Utils.jsonCheckKeyTypeStr(jObj, 'uuid', False, False):
        Utils.logger.error(f"checkEventData: Missing 'uuid' in data: {jObj}")
        return None, None
    return event['action'], jObj

# Convenience functions
def start():
    """Start the MinerServiceManager."""
    miner_service_manager.start()

def startThread():
    """Start the MinerServiceManager in a thread."""
    miner_service_manager.start_thread()