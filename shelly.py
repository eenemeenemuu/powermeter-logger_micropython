import json
from powermeter_functions import http_get
from powermeter_functions import convert_unix_timestamp
from powermeter_functions import power_threshold_get

def get_stats(host):
    stats = http_get('http://'+host+'/status')

    if (stats == ""):
        print('Failed')
        return False

    stats = json.loads(stats[stats.find('{'):])

    t = convert_unix_timestamp(stats['unixtime'])
    if (t < 500000000):
        from powermeter_functions import cettime
        t = cettime()
    else:
        import time
        t = time.localtime(t)

    stats_date = '{:02d}.{:02d}.{:04d}'.format(t[2], t[1], t[0])
    stats_time = ',{:02d}:{:02d}:{:02d}'.format(t[3], t[4], t[5])
    stats_power = ',{:.2f}'.format(power_threshold_get(float(stats['meters'][0]['power'])))
    if 'temperature' in stats:
        stats_temp = ',{:.2f}'.format(float(stats['temperature']))
    else:
        stats_temp = ''

    return stats_date + stats_time + stats_power + stats_temp
