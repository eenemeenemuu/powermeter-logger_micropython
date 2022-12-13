def r():
    import machine
    machine.reset()

import machine
pwm = machine.PWM(machine.Pin(2))
pwm.duty(1020)
pwm.freq(20)

from wifi_manager import WifiManager
wm = WifiManager()
wm.connect()

pwm.freq(1)
import sys
del wm
del WifiManager
del sys.modules['wifi_manager']
gc.collect()

import time
for wait in range(3, 0, -1):
    print(wait)
    time.sleep(1)

print('--- powermeter start ---')
from powermeter import powermeter_stats
powermeter_stats()
