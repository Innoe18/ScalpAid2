import time
import board
import adafruit_dht
from pubnub.pubnub import PubNub
from pubnub.pnconfiguration import PNConfiguration
from pubnub.exceptions import PubNubException

pnconfig = PNConfiguration()
pnconfig.subscribe_key = "sub-c-32b1cee9-bf8b-410f-871b-8048d45a7b21"
pnconfig.publish_key = "pub-c-cb72b7b6-e6dd-420c-8a8c-0a351316e386"
pnconfig.uuid = "scalp-device-001"

pubnub = PubNub(pnconfig)

dht = adafruit_dht.DHT22(board.D4)

while True:
    try:
        temperature = dht.temperature

        data = {
            "device_id": "pi-zero-001",
            "temperature": temperature,
            "timestamp": time.time()
                }

        print("Publishing:", data)
        pubnub.publish().channel("scalpAid_channel").message(data).sync()

    except PubNubException as e:
        print("PubNub error:", e)

    except Exception as e:
        print("Sensor error:", e)

    time.sleep(5)
