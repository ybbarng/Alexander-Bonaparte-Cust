import functools
from time import sleep
import traceback

from bluepy.btle import Scanner
from bluepy.btle import Peripheral
from bluepy.btle import BTLEException
import bluepy.btle


class Switcher:
    switcher = None
    characteristics = None
    battery_handler = None
    hashed_share_code_handler = None
    authority_handler = None
    time_handler = None
    switch_handler = None
    uuids = None
    share_code = None

    def __init__(self, mac_address, share_code, debug=False):
        bluepy.btle.Debugging = debug
        self.mac_address = mac_address
        self.share_code = share_code

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
                    if name is None or 'SWITCHER_M' not in name:
                        continue
                    print('A switcher is found: {}({} {})'.format(name, device.addr, device.addrType))
                    if device.connectable:
                        print('Connectable switcher is found.')
                        self.mac_address = device.addr
                        retry = False
                        break
                    else:
                        print('The switcher is busy')
                if retry:
                    print('Connectable switcher is not found. Retry...')
                    sleep(2)
            except Exception as e:
                print('Error on scanning')
                traceback.print_exc()
        self.connect()

    def connect(self, callback=None):
        retry = True
        while retry:
            try:
                print('Try to connect to the switcher...')
                self.switcher = Peripheral(self.mac_address, 'random')
                retry = False
            except Exception as e:
                print('Error on connecting')
                traceback.print_exc()
        print('Switcher is connected')
        if callback:
            try:
                callback.on_connected(self)
            except BTLEException as e:
                traceback.print_exc()
                if e.code == BTLEException.DISCONNECTED:
                    print('Switcher disconnected')
                    self.switcher = None
                    # TODO: try re-connect
            except Exception as e:
                print('Error on using')
                traceback.print_exc()
            finally:
                if self.switcher:
                    print('Disconnect due to an error')
                    self.switcher.disconnect()

    def auto_reconnect(func):
        @functools.wraps(func)
        def wrap(self, *args, **kargs):
            if self.switcher is None:
                self.connect()
            while(True):
                try:
                    return func(self, *args, **kargs)
                except BTLEException as e:
                    if e.code == BTLEException.DISCONNECTED:
                        print('Switcher has gone')
                    else:
                        traceback.print_exc()
                    print('Try reconnect...')
                    self.connect()
        return wrap

    def disconnect(self):
        if self.switcher:
            self.switcher.disconnect()
            print('Switcher is disconnected')

    def to_bytes(self, digits):
        return bytearray(int(ch) for ch in str(digits))

    def show_informations(self):
        self.load_uuids()
        self.get_services(True)
        self.get_characteristics(True)

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
        services = self.switcher.getServices()
        if print_services:
            for service in services:
                uuid = str(service.uuid)
                print('UUID: {} ({})'.format(uuid, self.get_uuid_description(uuid)))

    def get_characteristics(self, print_characteristics=False):
        print('get_characteristics')
        if self.characteristics is None:
            self.characteristics = self.switcher.getCharacteristics()
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
        Switcher sends no response for this method
        """
        descriptors = self.switcher.getDescriptors()
        print('descriptors')
        print(descriptors)

    def get_handler(self, number_of_handler):
        characteristics = self.get_characteristics()
        for ch in characteristics:
            if ch.getHandle() == number_of_handler:
                return ch
        print('There is no handler: {}'.format(number_of_handler))
        return None

    def get_hashed_share_code_handler(self):
        if not self.hashed_share_code_handler:
            self.hashed_share_code_handler = self.get_handler(0x1d)
        return self.hashed_share_code_handler

    @auto_reconnect
    def get_battery(self):
        battery = int.from_bytes(self.switcher.readCharacteristic(0xe), byteorder='big')
        return battery

    @auto_reconnect
    def compare_hashed_share_code(self):
        hashed_share_code = self.to_bytes('0' + self.share_code)
        print('Write: {}'.format(hashed_share_code))
        result = self.switcher.writeCharacteristic(0x1d, hashed_share_code, True)
        print(result)

    @auto_reconnect
    def get_authority(self):
        return self.switcher.readCharacteristic(0x1f)[0]

    def get_day_name(self, day):
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return days[day]

    @auto_reconnect
    def get_time(self):
        day, hours, minutes = self.switcher.readCharacteristic(0x2b)
        return '{} {:02d}:{:02d}'.format(self.get_day_name(day), hours, minutes)

    @auto_reconnect
    def manage_switch(self, switch, on=True):
        """
            switch: 1, 2
            on: True / False
            switch 1 on -> 0
            switch 1 off -> 1
            switch 2 on -> 2
            switch 2 off -> 3
        """
        if switch not in [1, 2]:
            print('Switch must be 1 or 2')
            return
        print('Switch {} {}'.format(switch, 'ON' if on else 'OFF'))
        param = (switch - 1) * 2 + (0 if on else 1)
        print(param)
        result = self.switcher.writeCharacteristic(0x11, bytes([param]), True)
        print(result)

    @auto_reconnect
    def test_switch(self, value):
        result = self.switcher.writeCharacteristic(0x11, bytes([value]), True)
        print(result)
