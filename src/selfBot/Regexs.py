import re

# https://github.com/dolfies/discord.py-self/blob/master/discord/utils.py
SENTRY_ASSET_REGEX = re.compile(r'assets/(sentry\.\w+)\.js')
BUILD_NUMBER_REGEX = re.compile(r'buildNumber\D+(\d+)"')

ELECTRON_VERSION_REGEX = r"Electron/([0-9]+\.[0-9]+\.[0-9]+)"
CHROME_VERSION_REGEX = r"Chrome/([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)"
DISCORD_NATIVE_VERSION_REGEX = r"metadata_version\":([0-9]+)"
DISCORD_CLIENT_VERSION_REGEX = r"version\": \"([0-9]+\.[0-9]+\.[0-9]+)"
WINDOWS_SDK_VERSION = r"[0-9]+\.[0-9]+\.([0-9]+)\.[0-9]+"