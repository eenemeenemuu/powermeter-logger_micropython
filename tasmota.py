import json
from powermeter_cfg import host
from powermeter_functions import http_get
from powermeter_functions import power_threshold_get

def get_stats():
    stats = http_get('http://'+host+'/cm?cmnd=Status%208')

    if (stats == ""):
        print('Failed')
        return False

    stats = json.loads(stats[stats.find('{'):])

    t = stats['StatusSNS']['Time']

    stats_date = '{:02d}.{:02d}.{:04d}'.format(int(t[8:10]), int(t[5:7]), int(t[0:4]))
    stats_time = ',{:02d}:{:02d}:{:02d}'.format(int(t[11:13]), int(t[14:16]), int(t[17:19]))
    stats_power = ',{:.2f}'.format(power_threshold_get(float(stats['StatusSNS']['ENERGY']['Voltage'])*float(stats['StatusSNS']['ENERGY']['Current'])*float(stats['StatusSNS']['ENERGY']['Factor'])))

    return stats_date + stats_time + stats_power
