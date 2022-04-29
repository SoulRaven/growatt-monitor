#  -*- coding: utf-8 -*-

#############################
# Global settings           #
#############################
# how many seconds each task will be delayed from the next task
SCHEDULE_DELAY_TASKS: int = 50

##################
# Growatt server #
##################

GROWATT_USERNAME: str = ""
GROWATT_PASSWORD: str = ""

# Growatt unofficial API endpoint based on engineered the API from the Growatt mobile app
GROWATT_ENDPOINT_WEB_API: list[str, ...] = [
    "https://server.growatt.com/",
    "https://server-us.growatt.com/",
    "https://server.smten.com/",
]
GROWATT_DEFAULT_URL: str = GROWATT_ENDPOINT_WEB_API[0]

# if the default plant ID is 0 or less, api will query first plant
GROWATT_DEFAULT_PLANT_ID: int = 0

DOMAIN = "growatt_server"
###########################
# Unimplemented settings  #
###########################

# Growatt official API
GROWATT_ENDPOINT_API: str = 'https://test.growatt.com/v1/'

# In the future is possible that Growatt will change this
GROWATT_TEST_API_KEY_TOKEN = '6eb6f069523055a339d71e5b1f6c88cc'

####################################
# Growatt user authentication data #
####################################

GROWATT_AUTH_TYPE: str = 'auth'

GROWATT_API_KEY_TOKEN: str = ""
