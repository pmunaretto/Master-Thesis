import requests
import time
import datetime
import random
import sys

url="http://localhost:8088/services/collector/event"
token="d952ade0-dc6a-4e42-904d-299a0f4f9953"
auth_header = {
    "Authorization": "Splunk {}".format(token)
}
insiders = {
  "user1": {
    "computer": "desktop-1",
    "start": "2022-06-01T15:10:53+00:00",
    "end": "2022-06-01T16:10:53+00:00",
    "bytes_lower_limit": 600000,
    "bytes_upper_limit": 10000000,
    "pages_lower_limit": 1,
    "pages_upper_limit": 12,
    "count": 500,
  },
  "user2": {
    "computer": "desktop-2",
    "start": "2022-06-02T15:10:53+00:00",
    "end": "2022-06-02T16:10:53+00:00",
    "bytes_lower_limit": 600000,
    "bytes_upper_limit": 10000000,
    "pages_lower_limit": 1,
    "pages_upper_limit": 12,
    "count": 5,
  },
  "user3": {
    "computer": "desktop-3",
    "start": "2022-06-03T15:10:53+00:00",
    "end": "2022-06-03T16:10:53+00:00",
    "bytes_lower_limit": 600000,
    "bytes_upper_limit": 10000000,
    "pages_lower_limit": 1,
    "pages_upper_limit": 12,
    "count": 5
  }
}
event_template = r"""<Event xmlns="http://schemas.microsoft.com/win/2004/08/events/event">
  <System>
    <Provider Name="Microsoft-Windows-PrintService" Guid="{{747ef6fd-e535-4d16-b510-42c90f6873a1}}" />
    <EventID>307</EventID>
    <Version>0</Version>
    <Level>4</Level>
    <Task>26</Task>
    <Opcode>11</Opcode>
    <Keywords>0x4000000000000840</Keywords>
    <TimeCreated SystemTime="2022-06-04T15:01:52.1290446Z" /> {timestamp}
    <EventRecordID>10</EventRecordID>
    <Correlation />
    <Execution ProcessID="4976" ThreadID="21288" />
    <Channel>Microsoft-Windows-PrintService/Operational</Channel>
    <Computer>{computer}</Computer>
    <Security UserID="S-1-5-21-2232877017-2372290985-1818511433-1002" />
  </System>
  <UserData>
    <DocumentPrinted xmlns="http://manifests.microsoft.com/win/2005/08/windows/printing/spooler/core/events">
      <Param1>3</Param1>
      <Param2>Print Document</Param2>
      <Param3>{owner}</Param3>
      <Param4>\\{computer}</Param4>
      <Param5>Microsoft Print to PDF</Param5>
      <Param6>{path}</Param6>
      <Param7>{bytes}</Param7>
      <Param8>{pages}</Param8>
    </DocumentPrinted>
  </UserData>
</Event>
"""

for key, value in insiders.items():

    print(f"Generating {value['count']} events for {key}...")

    for i in range(0, value["count"]):

        start = time.mktime(datetime.datetime.strptime(value["start"], "%Y-%m-%dT%H:%M:%S%z").timetuple())
        end = time.mktime(datetime.datetime.strptime(value["end"], "%Y-%m-%dT%H:%M:%S%z").timetuple())
        timestamp = random.random() * (end - start) + start

        event = event_template.format(
            timestamp=datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            computer="computer",
            owner="owner",
            path="path",
            bytes=random.randint(value["bytes_lower_limit"], value["bytes_upper_limit"]),
            pages=random.randint(value["pages_lower_limit"], value["pages_upper_limit"])
        )
        event = "".join(line.strip() for line in event.split("\n"))

        json = {
            "time": timestamp,
            "index": "test",
            "source": "XmlWinEventLog:Security",
            "sourcetype": "XmlWinEventLog",
            "event": event
        }

        r = requests.post(url, headers=auth_header, json=json, verify=False)

sys.exit(0)

