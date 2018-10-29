import functools
from time import sleep
import traceback

from bluepy.btle import Scanner
from bluepy.btle import Peripheral
from bluepy.btle import BTLEException
import bluepy.btle


class Audrey:
    audrey = None

    def __init__(self, mac_address, debug=False):
        bluepy.btle.Debugging = debug
        self.mac_address = mac_address

    def scan(self):
        scan_timeout = 10 # seconds
        scanner = Scanner()
        retry = True
        while (retry):
            try:
                print('Scanning...')
                devices = scanner.scan(scan_timeout)
                for device in devices:
                    name = None
                    for ad_type, description, value in device.getScanData():
                        if ad_type == 9:
                            name = value
                    if name is None or 'Audrey' not in name:
                        continue
                    print('Audrey is found: {}({} {})'.format(name, device.addr, device.addrType))
                    if device.connectable:
                        print('Connectable audrey is found.')
                        self.mac_address = device.addr
                        retry = False
                        break
                    else:
                        print('Audrey is busy')
                if not self.mac_address:
                    print('Connectable audrey is not found. Retry...')
                    sleep(2)
            except Exception as e:
                print('Error on scanning')
                traceback.print_exc()
        self.connect()

    def connect(self, callback=None):
        retry = True
        while retry:
            try:
                print('Try to connect to Audrey...')
                self.audrey = Peripheral(self.mac_address, 'public')
                retry = False
            except Exception as e:
                print('Error on connecting')
                traceback.print_exc()
        print('Audrey is connected')
        if callback:
            try:
                callback.on_connected(self)
            except BTLEException as e:
                traceback.print_exc()
                if e.code == BTLEException.DISCONNECTED:
                    print('Audrey has gone')
                    self.audrey = None
                    # TODO: try re-connect
            except Exception as e:
                print('Error on using')
                traceback.print_exc()
            finally:
                if self.audrey:
                    print('Disconnect due to an error')
                    self.audrey.disconnect()

    def auto_reconnect(func):
        @functools.wraps(func)
        def wrap(self, *args, **kargs):
            if self.audrey is None:
                self.connect()
            while(True):
                try:
                    return func(self, *args, **kargs)
                except BTLEException as e:
                    if e.code == BTLEException.DISCONNECTED:
                        print('Audrey has gone')
                    else:
                        traceback.print_exc()
                    print('Try reconnect...')
                    self.connect()
        return wrap

    def disconnect(self):
        if self.audrey:
            self.audrey.disconnect()
            print('Audrey is disconnected')

    def to_bytes(self, digits):
        return bytearray(int(ch) for ch in str(digits))

    @auto_reconnect
    def send_command(self, command, on_success=None):
        command += '\r\n'
        print('Write: {}'.format(command))
        result = self.audrey.writeCharacteristic(0x25, command.encode('utf-8'), True)
        print(result)
        if on_success:
            on_success()

    def load_uuids(self):
        import json

        with open('uuid.json') as f:
            self.uuids = {v: k for k, v in json.load(f).items()}

    def get_uuid_description(self, uuid):
        try:
            return self.uuids[uuid]
        except:
            return 'Unknown'

    def get_services(self, print_services=False):
        print('get_services')
        services = self.audrey.getServices()
        if print_services:
            for service in services:
                uuid = str(service.uuid)
                print('UUID: {} ({})'.format(uuid, self.get_uuid_description(uuid)))

    def get_characteristics(self, print_characteristics=False):
        print('get_characteristics')
        if self.characteristics is None:
            self.characteristics = self.audrey.getCharacteristics()
        if print_characteristics:
            for ch in self.characteristics:
                uuid = str(ch.uuid)
                print('UUID: {} ({})'.format(uuid, self.get_uuid_description(uuid)))
                print('Properties: {} ({})'.format(ch.properties, ch.propertiesToString()))
                print('Handler: 0x{:02x}'.format(ch.getHandle()))
                print('\n')
        return self.characteristics

    def get_descriptors(self):
        """
        Audrey sends no response for this method
        """
        descriptors = self.audrey.getDescriptors()
        print('descriptors')
        print(descriptors)
