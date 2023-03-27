from powermeter_cfg import *
from powermeter_functions import cettime
from powermeter_functions import power_threshold_get

sid = ""

def get_stats():
    global sid
    stats = http_get_stats('http://'+host+'/webservices/homeautoswitch.lua?ain='+ain+'&switchcmd=getbasicdevicestats&sid='+sid)
    if (stats == ""):
        print('Failed')
        sid = fritz_login()
        print('Collecting stats: ', end = '')
        stats = http_get_stats('http://'+host+'/webservices/homeautoswitch.lua?ain='+ain+'&switchcmd=getbasicdevicestats&sid='+sid)
    if (stats == ""):
        print('Failed')
        return False

    t = cettime()

    stats_date = '{:02d}.{:02d}.{:04d}'.format(t[2], t[1], t[0])
    stats_time = ',{:02d}:{:02d}:{:02d}'.format(t[3], t[4], t[5])
    stats_power = ',{:.2f}'.format(power_threshold_get(int(xml_get(stats, 'power')) / 100))
    stats_temp = ',{:.1f}'.format(int(xml_get(stats, 'temperature')) / 10)

    return stats_date + stats_time + stats_power + stats_temp

def fritz_login():
    from powermeter_functions import http_get
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

def utf8_to_utf16(text):
    text_utf16 = ''
    for x in text:
        text_utf16 += x + '\x00'
    return text_utf16

def xml_get(text, xml_tag):
    start = text.find('<' + xml_tag + '>') + len(xml_tag) + 2
    end = text.find('</' + xml_tag + '>')
    return text[start:end]

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
    str_return = re.sub('<stats count="[0-9]+" grid="[0-9]+"( datatime="[0-9]+")?>', '', str_return)
    str_return = str_return.replace('</stats>', '')
    str_return = str_return.replace(',<', '<')
    return str_return
