import requests
import datetime
import random
import urllib3
import string

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
URL     = "https://<host>:8088/services/collector/event"
TOKEN   = "<token>"
HEADER  = {"Authorization": "Splunk {}".format(TOKEN)}
PROXIES = {"http": None, "https": None}
USER    = "<user>"
HOST    = "<host>"
INDEX   = "<index>"

# UC1: Anomalous Login Behavior
print(f"Generating 4 login events for {USER}...")
event      = "{timestamp}, search_name=n/a, search_now=n/a, user={user}"
timestamps = [
    "08/31/2022 20:18:00 +0200",
    "08/31/2022 21:29:00 +0200",
    "08/31/2022 22:40:00 +0200",
    "08/31/2022 23:01:00 +0200"
]
for timestamp in timestamps:
    event = event.format(timestamp=timestamp, user=USER)
    json = {
        "time": datetime.datetime.strptime(timestamp, "%m/%d/%Y %H:%M:%S +0200").timestamp(),
        "host": "<splunk host>",
        "index": INDEX,
        "source": "uc1_raw_events",
        "sourcetype": "stash",
        "event": event
    }
    r = requests.post(URL, headers=HEADER, proxies=PROXIES, json=json, verify=False)
    print(r.text)

# UC3: Browsing Job Sites
print(f"Generating 1 job browsing event for {USER}...")
event     = f"{timestamp}, search_name=n/a, search_now=n/a, url=tunnel://stepstone.com, user={USER}, count=1"
timestamp = "08/31/2022 12:10:00 +0200"
json  = {
    "time": datetime.datetime.strptime(timestamp, "%m/%d/%Y %H:%M:%S +0200").timestamp(),
        "host": "<splunk host>",
    "index": INDEX,
    "source": "uc3_raw_events",
    "sourcetype": "stash",
    "event": event
}
r = requests.post(URL, headers=HEADER, proxies=PROXIES, json=json, verify=False)
print(r.text)

# UC7: Anomalous File Copy Behavior
print(f"Generating 1,300 file copy events for {USER}...")
timestamp = "08/31/2022 19:10:00 +0200"
for i in range(1300):
    file_path = f"E:\\\{''.join(random.choices(string.ascii_uppercase + string.digits, k=10))}.docx"
    event = f"{timestamp}, search_name=n/a, search_now=n/a, orig_host={HOST}, user={USER}, file_path=\"{file_path}\", process_path=\"C:\\\WINDOWS\\\Explorer.EXE\""
    json  = {
        "time": datetime.datetime.strptime(timestamp, "%m/%d/%Y %H:%M:%S +0200").timestamp(),
        "host": "<splunk host>",
        "index": INDEX,
        "source": "uc7_raw_events",
        "sourcetype": "stash",
        "event": event
    }
    r = requests.post(URL, headers=HEADER, proxies=PROXIES, json=json, verify=False)
    print(r.text)
