# Radiobot get solar data images from popular hamradio websites and toots to Mastodon

### Usage
python3 radiobot.py [full path to config file]

Example
python3 radiobot.py /home/bot/radiobot@my_bot@my_instance.conf

### Configuration file
The configuration file should be placed in a safe directory (not world or group readable), and contains the instance and authentication credentials.
You must complete the config file and provide authentication credentials to your desired mastodon account.
A sample config file 'radiobot@my_bot@my_instance.conf' is provided as a starting point.

### Authentication methods
This app support both email and application token authentication.
You are strongly encouraged to create an application with dedicated app id, secret and access token for this bot.
See the "Development" and "New application" pannel in your mastodon account settings.
