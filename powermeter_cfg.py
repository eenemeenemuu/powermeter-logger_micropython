device = ''             # possible options: fritzbox, shelly
host = ''               # host name or ip address of power meter, e.g. fritz.box or 192.168.178.1
username = ''           # fritzbox only: user name
fritz_pw = ''           # fritzbox only: password
ain = ''                # fritzbox only: Aktor Identifikationsnummer (AIN), on your FRITZ!Box go to "Heimnetz > Smart Home" and edit your device to get the AIN
host_external = ''      # external host for logging and display - must end with trailing slash (/)
host_auth_key = ''      # auth key must match on external host
power_threshold = 0     # optional: minimum required power to log power value (may be required if micro inverter has measurable consumption at night); can be float value like 0.25
