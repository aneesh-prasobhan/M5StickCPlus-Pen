import asyncio
from bleak import BleakClient

class BLECommunication:
    def __init__(self, address, service_uuid, characteristic_uuid):
        self.address = address
        self.service_uuid = service_uuid
        self.characteristic_uuid = characteristic_uuid
        self.client = BleakClient(address)

    async def connect(self):
        retries = 10
        for attempt in range(retries):
            try:
                await self.client.connect()
                return self.client.is_connected
            except Exception as e:
                print(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < retries - 1:
                    print("Retrying...")
                    await asyncio.sleep(1)  # wait a bit before retrying
                else:
                    raise ConnectionError("Failed to connect after several attempts")

    async def start_notify(self, handler):
        await self.client.start_notify(self.characteristic_uuid, handler)

    async def stop_notify(self):
        await self.client.stop_notify(self.characteristic_uuid)

    async def disconnect(self):
        if self.client and self.client.is_connected:
            try:
                await asyncio.wait_for(self.client.disconnect(), timeout=3)
                print("Disconnection timed out.")
            except asyncio.TimeoutError:
                print("Disconnected from BLE device.")

    def is_connected(self):
        return self.client.is_connected if self.client else False

def notification_handler(sender, data):
    print(f"Received data: {data}")

async def main():
    ble_device_address = "E8:9F:6D:09:2E:8A"  # Replace with actual device BLE address
    service_uuid = '4fafc201-1fb5-459e-8fcc-c5c9c331914b'
    characteristic_uuid = 'beb5483e-36e1-4688-b7f5-ea07361b26a8'
    ble_comms = BLECommunication(ble_device_address, service_uuid, characteristic_uuid)
    
    if await ble_comms.connect():
        print("Connected to the device!")
        await ble_comms.start_notify(notification_handler)
        await asyncio.sleep(30)  # Keep receiving data for 30 seconds
        await ble_comms.stop_notify()
        await ble_comms.disconnect()
    else:
        print("Failed to connect.")

if __name__ == '__main__':
    asyncio.run(main())