import os
import logging
import yaml
import re
import dotenv
import json

logging.basicConfig(level=logging.INFO)
dotenv.load_dotenv()

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))

channel = "CHYATF79T"
ts = "1679970197.164539"

thread_replies = client.conversations_replies(
    channel=channel,
    ts=ts,
    limit=1000
)

texts = []
for message in thread_replies['messages']:
    text = re.sub(r'<@[\w\d]+>\s+', '', message['text'])
    texts.append(text)

print(texts)