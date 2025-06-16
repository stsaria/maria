import re

# https://github.com/dolfies/discord.py-self/blob/master/discord/utils.py
SENTRY_ASSET_REGEX = re.compile(r'assets/(sentry\.\w+)\.js')
BUILD_NUMBER_REGEX = re.compile(r'buildNumber\D+(\d+)"')