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

    if (device == "shelly"):
        import json
    import time
    import gc

    error_counter = 0
    i = -1
    sid = ""

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

            if (device == "fritzbox"):
                stats = http_get_stats('http://'+host+'/webservices/homeautoswitch.lua?ain='+ain+'&switchcmd=getbasicdevicestats&sid='+sid)
                if (stats == ""):
                    print('Failed')
                    sid = fritz_login()
                    print('Collecting stats: ', end = '')
                    stats = http_get_stats('http://'+host+'/webservices/homeautoswitch.lua?ain='+ain+'&switchcmd=getbasicdevicestats&sid='+sid)
                if (stats == ""):
                    print('Failed')
                    continue

                t = cettime()
                stats_date = '{:02d}.{:02d}.{:04d}'.format(t[2], t[1], t[0])
                stats_time = ',{:02d}:{:02d}:{:02d}'.format(t[3], t[4], t[5])
                stats_power = ',{:.2f}'.format(power_threshold_get(int(xml_get(stats, 'power')) / 100))
                stats_temp = ',{:.1f}'.format(int(xml_get(stats, 'temperature')) / 10)

            elif (device == "shelly"):
                stats = http_get('http://'+host+'/status')

                if (stats == ""):
                    print('Failed')
                    continue

                stats = json.loads(stats[stats.find('{'):])

                t = int(stats['meters'][0]['timestamp'] - 946684800)
                if (t < 500000000):
                    t = cettime()
                else:
                    t = time.localtime(t)

                stats_date = '{:02d}.{:02d}.{:04d}'.format(t[2], t[1], t[0])
                stats_time = ',{:02d}:{:02d}:{:02d}'.format(t[3], t[4], t[5])
                stats_power = ',{:.2f}'.format(power_threshold_get(float(stats['meters'][0]['power'])))
                if 'temperature' in stats:
                    stats_temp = ',{:.2f}'.format(float(stats['temperature']))
                else:
                    stats_temp = ''

            else:
                print('wrong device configured')
                continue

            stats = stats_date + stats_time + stats_power + stats_temp
            print(stats)

            gc.collect()

            print('Sending stats to '+host_external+': ', end = '')
            print(https_put(host_external+'log.php?key='+host_auth_key+'&stats='+stats))

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
                machine.reset()
            else:
                print('Something went wrong, retrying... ['+str(error_counter)+']')
                print()
                continue

def fritz_login():
    print('Check for valid session ID')
    text = http_get('http://'+host+'/login_sid.lua')
    sid = xml_get(text, 'SID')

    if (sid == "0000000000000000"):
        print('No valid session ID found, login to Fritzbox')
        import md5
        challenge = xml_get(text, 'Challenge')
        text = http_get('http://'+host+'/login_sid.lua?username='+username+'&response='+challenge+'-'+md5.digest(utf8_to_utf16(challenge+'-'+fritz_pw)))
        sid = xml_get(text, 'SID')

    print('Session ID: '+sid)
    print()

    return sid

def xml_get(text, xml_tag):
    start = text.find('<' + xml_tag + '>') + len(xml_tag) + 2
    end = text.find('</' + xml_tag + '>')
    return text[start:end]

def utf8_to_utf16(text):
    text_utf16 = ''
    for x in text:
        text_utf16 += x + '\x00'
    return text_utf16

def power_threshold_get(power):
    try:
        power_threshold
    except:
        return power
    if (power < power_threshold):
        return 0
    else:
        return power

def sync_time():
    pwm.freq(10)
    from ntptime import settime
    print('Syncing time')
    t = cettime()
    print('Old time: {:02d}:{:02d}:{:02d}'.format(t[3], t[4], t[5]))
    settime()
    t = cettime()
    print('New time: {:02d}:{:02d}:{:02d}'.format(t[3], t[4], t[5]))
    print()

def http_get(url):
    import socket
    _, _, host, path = url.split('/', 3)
    addr = socket.getaddrinfo(host, 80)[0][-1]
    s = socket.socket()
    s.connect(addr)
    s.settimeout(5)
    s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
    str_return = ''
    while True:
        data = s.recv(128)
        if data:
            str_return += str(data, 'utf8')
        else:
            break
    s.close()
    return str_return

def http_get_stats(url):
    import socket
    import re
    _, _, host, path = url.split('/', 3)
    addr = socket.getaddrinfo(host, 80)[0][-1]
    s = socket.socket()
    s.connect(addr)
    s.settimeout(5)
    s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
    str_return = ''
    while True:
        data = s.recv(128)
        if data:
            str_return += str(data, 'utf8')
            str_return = re.sub(',[-0-9]+', ',', str_return)
            str_return = re.sub(',+', ',', str_return)
        else:
            break
    s.close()
    str_return = str_return[str_return.find('<devicestats'):len(str_return)].strip()
    str_return = re.sub('<stats count="[0-9]+" grid="[0-9]+">', '', str_return)
    str_return = str_return.replace('</stats>', '')
    str_return = str_return.replace(',<', '<')
    return str_return

def https_put(url):
    import socket
    try:
        import ussl as ssl
    except:
        import ssl
    _, _, host, path = url.split('/', 3)
    addr = socket.getaddrinfo(host, 443)[0][-1]
    s = socket.socket()
    s.connect(addr)
    s.settimeout(5)
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

def cettime():
    #Source: https://forum.micropython.org/viewtopic.php?f=2&t=4034
    import time
    year = time.localtime()[0]       #get current year
    HHMarch   = time.mktime((year,3 ,(31-(int(5*year/4+4))%7),1,0,0,0,0,0)) #Time of March change to CEST
    HHOctober = time.mktime((year,10,(31-(int(5*year/4+1))%7),1,0,0,0,0,0)) #Time of October change to CET
    now=time.time()
    if now < HHMarch :               # we are before last sunday of march
        cet=time.localtime(now+3600) # CET:  UTC+1H
    elif now < HHOctober :           # we are before last sunday of october
        cet=time.localtime(now+7200) # CEST: UTC+2H
    else:                            # we are after last sunday of october
        cet=time.localtime(now+3600) # CET:  UTC+1H
    return(cet)
