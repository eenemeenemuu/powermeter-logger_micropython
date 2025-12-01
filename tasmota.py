import json
from powermeter_functions import http_get
from powermeter_functions import cettime
from powermeter_functions import power_threshold_get

def get_stats(host):
    stats = http_get('http://'+host+'/cm?cmnd=Status%208')

    if (stats == ""):
        print('Failed')
        return False

    stats = json.loads(stats[stats.find('{'):stats.rfind('}')+1])

    t = cettime()

    stats_date = '{:02d}.{:02d}.{:04d}'.format(t[2], t[1], t[0])
    stats_time = ',{:02d}:{:02d}:{:02d}'.format(t[3], t[4], t[5])
    stats_power = ',{:.2f}'.format(power_threshold_get(float(stats['StatusSNS']['ENERGY']['Voltage'])*float(stats['StatusSNS']['ENERGY']['Current'])*float(stats['StatusSNS']['ENERGY']['Factor'])))

    return stats_date + stats_time + stats_power
