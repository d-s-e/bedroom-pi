import logging
from paho.mqtt import client as mqtt_client


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class MQTT:
    def __init__(self, client_id: str, broker_address: str, broker_port: int, topic_prefix: str):
        self.client_id = client_id
        self.broker_address = broker_address
        self.broker_port = broker_port
        self.topic_prefix = topic_prefix
        self.client = self.connect()

    def connect(self):
        client = mqtt_client.Client(self.client_id)
        client.on_connect = self._on_connect
        client.connect(self.broker_address, self.broker_port)
        return client

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            log.info("Connected to MQTT broker.")
        else:
            log.error(f"Failed to connect, code {rc}")
    
    def run(self):
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()

    def publish(self, topic, data):
        result, _ = self.client.publish(self.topic_prefix + topic, data)
        if result != 0:
            log.warn(f"Failed to send message!")

    def subscribe(self, topic):
        self.client.subscribe(self.topic_prefix + topic)

