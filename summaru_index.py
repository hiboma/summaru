from typing import List, Optional
import time
import logging
import re

from llama_index import SlackReader
from llama_index.readers.schema.base import Document
from slack_sdk.errors import SlackApiError

logger = logging.getLogger(__name__)

class SlackThreadReader(SlackReader):

    """
    Slack のスレッドを読み込むクラスです。
    """

    def _read_channel(self, channel_id: str, thread_ts: str) -> str:

        texts: List[str] = []
        next_cursor = None
        while True:
            try:
                # Call the conversations.history method using the WebClient
                # conversations.history returns the first 100 messages by default
                # These results are paginated,
                # see: https://api.slack.com/methods/conversations.history$pagination
                result = self.client.conversations_replies(
                    channel=channel_id,
                    cursor=next_cursor,
                    ts=thread_ts,
                    limit=1000,
                )

                # Print results
                logger.info(
                    "{} messages found in {}".format(len(result["messages"]), id)
                )

                for message in result['messages']:
                    if message.get("bot_id") is not None:
                        print("bot message is ignored")
                        continue

                    clean_text = re.sub(r'<@[\w\d]+>\s+', '', message['text'])
                    texts.append(clean_text)

                if not result["has_more"]:
                    break

                next_cursor = result["response_metadata"]["next_cursor"]

            except SlackApiError as e:
                if e.response["error"] == "ratelimited":
                    logger.error(
                        "Rate limit error reached, sleeping for: {} seconds".format(
                            e.response.headers["retry-after"]
                        )
                    )
                    time.sleep(int(e.response.headers["retry-after"]))
                else:
                    raise e

        return "\n\n".join(texts)

    def load_data(self, channel_id: str, thread_ts: str):
        """
        channel_id: str
        thread_ts: str
        """
        thread_messages = self._read_channel(channel_id, thread_ts)
        return [ Document(thread_messages, extra_info={"channel": channel_id}) ]
