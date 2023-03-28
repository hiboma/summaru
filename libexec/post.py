import sys
import os
import logging
import yaml
import re
import dotenv
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# from sssbot import SssSlackReader

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

logging.basicConfig(level=logging.INFO)
dotenv.load_dotenv()

from llama_index import GPTSimpleVectorIndex, SimpleDirectoryReader

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
response = client.chat_postMessage(
    channel="#dev",
    text="Hello from your app! :tada:"
)

