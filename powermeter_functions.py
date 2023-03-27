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

def power_threshold_get(power):
    try:
        power_threshold
    except:
        return power
    if (power < power_threshold):
        return 0
    else:
        return power

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

def convert_unix_timestamp(t):
    import time
    year = time.localtime()[0]       #get current year
    HHMarch   = time.mktime((year,3 ,(31-(int(5*year/4+4))%7),1,0,0,0,0,0)) #Time of March change to CEST
    HHOctober = time.mktime((year,10,(31-(int(5*year/4+1))%7),1,0,0,0,0,0)) #Time of October change to CET
    now=time.time()
    if now < HHMarch :               # we are before last sunday of march
        t = t - 946684800            # CET:  UTC+1H
    elif now < HHOctober :           # we are before last sunday of october
        t = t - 946684800 + 7200     # CEST: UTC+2H
    else:                            # we are after last sunday of october
        t = t - 946684800            # CET:  UTC+1H
    return(t)
