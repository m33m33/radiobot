import os.path
import sys
import re
from time import sleep
from mastodon import Mastodon
import requests

# Program configuration
auth_file = "radiobot.auth"
auth_session = auth_file+'.session'
mastodon_api = None

# Set to 1 to get some messages, 0 for error messages only
debug=1

# Posting delay (s), wait between mastodon posts, reduces the "burst" effect on timoeline, and instance workload if you hit rate limiters
posting_delay=1

# Solar image
solar_pics=["http://www.hamqsl.com/solarmap.php", "http://www.hamqsl.com/solar101vhfper.php", "https://www.sws.bom.gov.au/Images/HF%20Systems/Global%20HF/HAP%20Charts/New%20York%20LDOCF.gif"]
toot_body="Solar data from http://www.hamqsl.com https://www.sws.bom.gov.au"
hashtags="#SolarData #Propagation #AmateurRadio #CBradio"

# Program logic below this line

if len(sys.argv) < 3:
    print("Usage: radiobot.py [config file] [--with-hashtags OR --without-hashtags]")
    print("All arguments are mandatory")
    sys.exit(1)

auth_file=sys.argv[1]
auth_session=auth_file+'.secret'
wiwo_hashtags=sys.argv[2]

# Will we mark this toot with hashtages or not ?
# Hastag are usefull for search results in current (3.X) Mastodon
if wiwo_hashtags == "--with-hashtags":
    toot_body = toot_body + " " + hashtags

# Returns the parameter from the specified file
def get_config(parameter, file_path):
    # Check if secrets file exists
    if not os.path.isfile(file_path):
        print("ERROR: Config file (%s) not found"%file_path)
        sys.exit(0)

    # Find parameter in file
    with open( file_path ) as f:
        for line in f:
            if line.startswith( parameter ):
                return line.replace(parameter + ":", "").strip()

    # Cannot find parameter, exit
    print(file_path + "  Missing parameter %s "%parameter)
    sys.exit(0)
# end get_config()

# Look for credentials in the coniguration file
auth_type = get_config("auth_type",auth_file)
if "token" in auth_type:
    # We are using an application token (developer options in the mastodon account, new app...)
    app_client_id = get_config("app_client_id",auth_file)
    app_client_secret = get_config("app_client_secret",auth_file)
    app_access_token  = get_config("app_access_token",auth_file)
else:
    if "email" in auth_type:
        # We are using theuser account credential
        mastodon_email_account = get_config("mastodon_email_account",auth_file)
        mastodon_email_password  = get_config("mastodon_email_password",auth_file)
    else:
        print("ERROR: Check the configuration file, no authentication method found")
        sys.exit(1)

instance = get_config("instance",auth_file)

if debug:
    if "token" in auth_type: print("Trying to connect with app client id:",app_client_id," on ",instance,"...", end='')
    else: print("Trying to login with email ",mastodon_email_account," on ",instance,"...", end='')
try:
    if "token" in auth_type:
        mastodon_api = Mastodon(client_id=app_client_id, client_secret=app_client_secret, access_token=app_access_token, api_base_url='https://'+instance)
    else:
        Mastodon.create_app('radiobot', api_base_url='https://'+instance, to_file=auth_session)
        mastodon_api = Mastodon(client_id=auth_session, api_base_url='https://'+instance)
        mastodon_api.log_in(mastodon_email_account, mastodon_email_password, to_file=auth_session)
except:
    print("ERROR: Can't connect to Mastodon instance")
    sys.exit(1)
if debug: print("ok")

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
    print("ERROR: Authentication error, or error fetching the media !")

if debug: print("Tooting...",end='')
try:
    toot = mastodon_api.status_post(toot_body, in_reply_to_id=None, media_ids=toot_media,sensitive=False,visibility='public',spoiler_text=None)
    if debug: print(" done.")
except:
    print("ERROR: Can't toot !")

sys.exit(0)
# end

