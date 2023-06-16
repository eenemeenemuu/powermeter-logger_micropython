powermeter_cfg = """
# structure of config file 'powermeter_cfg.py'
device = ''             # possible options: fritzbox, shelly
host = ''               # host name or ip address of power meter, e.g. fritz.box or 192.168.178.1
username = ''           # fritzbox only: user name
fritz_pw = ''           # fritzbox only: password
ain = ''                # fritzbox only: Aktor Identifikationsnummer (AIN), on your FRITZ!Box go to "Heimnetz > Smart Home" and edit your device to get the AIN
host_external = ''      # external host for logging and display - must end with trailing slash (/)
host_auth_key = ''      # auth key must match on external host
power_threshold = 0     # optional: minimum required power to log power value (may be required if micro inverter has measurable consumption at night); can be float value like 0.25
"""

import machine
pwm = machine.PWM(machine.Pin(2))
pwm.duty(1020)

try:
    from powermeter_cfg import *
    del powermeter_cfg
except ImportError:
    pwm.freq(2)
    print('Failed to load config file')
    print(powermeter_cfg)
    raise SystemExit(0)

def powermeter_stats():
    pwm.freq(1)

    import time
    import gc

    if (device == "fritzbox"):
        from fritzbox import get_stats
    elif (device == "shelly3em"):
        from shelly3em import get_stats
    elif (device == "shelly"):
        from shelly import get_stats
    elif (device == "tasmota"):
        from tasmota import get_stats
    elif (device == "ahoydtu"):
        from ahoydtu import get_stats
    else:
        def get_stats(host):
            print('wrong device configured (' + device + ')')
            time.sleep(10)
            print()
            return False

    error_counter = 0
    i = -1

    while True:
        try:
            if i < 0:
                i = 10
                sync_time()

            i -= 1

            time_start = time.time_ns()
            pwm.freq(5)

            gc.collect()

            print('Collecting stats: ', end = '')
            if type(host) is str:
                stats = get_stats(host)
                if (stats == False):
                    continue
            else:
                print()
                power_sum = 0
                power_array = list()
                for h in host:
                    print('- ' + h + ': ', end = '')
                    stats = get_stats(h)
                    if (stats == False):
                        continue
                    else:
                        print(stats)
                        stats_parts = stats.split(',')
                        stats_date = stats_parts[0]
                        stats_time = stats_parts[1]
                        power_sum += float(stats_parts[2])
                        power_array.append(stats_parts[2])
                        if (len(stats_parts) > 3):
                            stats_temp = stats_parts[3]
                        else:
                            stats_temp = ''
                print('--> ', end = '')
                stats = stats_date + ',' + stats_time + ',' + str(power_sum) + ',' + stats_temp + ',' + ','.join(power_array)
            print(stats)

            gc.collect()

            print('Sending stats to '+host_external+': ', end = '')
            print(http_s_send_stats(host_external+'log.php?key='+host_auth_key+'&stats='+stats))

            sleep_ms = (10 * 1000) - round(((time.time_ns() - time_start) / 1000 / 1000))
            if (sleep_ms > 0):
                pwm.freq(1)
                print('Sleep '+str(sleep_ms)+' ms')
                time.sleep_ms(sleep_ms)

            error_counter = 0
            print()
        except KeyboardInterrupt:
            print()
            print('Keyboard interrupt detected, stopping...')
            break
        except:
            print()
            error_counter += 1
            if error_counter > 3:
                print('Something went wrong too often, rebooting...')
                import machine
                time.sleep(1)
                machine.reset()
            else:
                print('Something went wrong, retrying... ['+str(error_counter)+']')
                time.sleep(1)
                print()
                continue

def sync_time():
    pwm.freq(10)
    from powermeter_functions import cettime
    from ntptime import settime
    print('Syncing time')
    t = cettime()
    print('Old time: {:02d}:{:02d}:{:02d}'.format(t[3], t[4], t[5]))
    settime()
    t = cettime()
    print('New time: {:02d}:{:02d}:{:02d}'.format(t[3], t[4], t[5]))
    print()

def http_s_send_stats(url):
    import socket
    if (host_external[0:5] == "https"):
        port = 443
        try:
            import ussl as ssl
        except:
            import ssl
    else:
        port = 80
    _, _, host, path = url.split('/', 3)
    addr = socket.getaddrinfo(host, port)[0][-1]
    s = socket.socket()
    s.connect(addr)
    s.settimeout(5)
    if (host_external[0:5] == "https"):
        s = ssl.wrap_socket(s)
    s.write(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
    str_return = ''
    end = 0
    while True:
        data = s.read(128)
        if data:
            str_return = str(data, 'utf8')
            end = str_return.find("\r")
            break
            #print(str(data, 'utf8'))
        else:
            break
    s.close()
    return str_return[0:end]
