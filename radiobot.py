import os.path
import sys
import re
from time import sleep

from mastodon import Mastodon
import requests

# Set to 1 to get some messages, 0 for error messages only
debug=1

# Posting delay (s), wait between mastodon posts, reduces the "burst" effect on timoeline, and instance workload if you hit rate limiters
posting_delay=1

# Solar image
solar_pics=["http://www.hamqsl.com/solarmap.php", "http://www.hamqsl.com/solar101vhfper.php", "http://www.spacew.com/www/realtime.gif"]
toot_body="Solar data from http://www.hamqsl.com http://www.spacew.com\n\n#HamRadio #SolarData #Propagation #AmateurRadio #CBradio"

if len(sys.argv) < 3:
    print("Usage: radiobot.py [instance (without http://)] [user] [password]")
    sys.exit(1)

instance=sys.argv[1]
mastodon_email_account=sys.argv[2]
passwd=sys.argv[3]

mastodon_api = None
instance_file='/var/run/lock/'+instance+'.secret'

# Create application if it does not exist
if debug: print("Creating mastodon client to https://" + instance + " " + instance_file)
try:
    Mastodon.create_app('radiobot', api_base_url='https://'+instance, to_file=instance_file)
except:
    print('ERROR: Failed to create app on instance '+instance)
    sys.exit(1)

try:
    if debug: print("Trying to connect with ",instance_file," to ",'https://'+instance," ...", end='')
    mastodon_api = Mastodon(client_id=instance_file,api_base_url='https://'+instance)
    if debug: print(" ok.")
except:
    print("ERROR: Can't connect to Mastodon instance")
    sys.exit(1)

if debug: print("Login with email ",mastodon_email_account," ...", end='')
try:
    mastodon_api.log_in(mastodon_email_account,passwd,to_file=instance_file)
    if debug: print(" ok.")
except:
    print("ERROR: First Login Failed !")
    sys.exit(1)

# get the solar image
if debug: print("Getting solar data...",end='')
toot_media = []
try:
    for solar in solar_pics:
        media = requests.get(solar)
        media_posted = mastodon_api.media_post(media.content, mime_type=media.headers.get('content-type'))
        toot_media.append(media_posted)
    if debug: print("done.")
except:
    print("ERROR: Can't get media !")

if debug: print("Tooting...",end='')
try:
    toot = mastodon_api.status_post(toot_body, in_reply_to_id=None, media_ids=toot_media,sensitive=False,visibility='public',spoiler_text=None)
    if debug: print(" done.")
except:
    print("ERROR: Can't toot !")
