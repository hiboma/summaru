import sys
import os
import logging
import re
import dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

logging.basicConfig(level=logging.INFO)
dotenv.load_dotenv()

from llama_index import GPTSimpleVectorIndex, SimpleDirectoryReader
from summaru_index import SlackThreadReader

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

channel_id = "CHYATF79T"
ts = "1679972008.862549"

documents = SlackThreadReader().load_data(channel_id=channel_id, thread_ts=ts)
index      = GPTSimpleVectorIndex(documents=documents)
summary    = index.query("テキストの要約をしてください")


