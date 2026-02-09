#!/usr/bin/env python
from click_and_drop_api.simple import ClickAndDrop
import os

# navigate to https://business.parcel.royalmail.com/settings/channels/
# Configure API key authorization: Bearer
API_KEY = os.environ["API_KEY"]

api = ClickAndDrop(API_KEY)

version = api.get_version()

# https://api.parcel.royalmail.com/#tag/Version
print("commit:", version.commit)
print("build:", version.build)
print("release:", version.release)
print("release date:", version.release_date)
