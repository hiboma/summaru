import time
import logging
import re
import os

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from llama_index.readers.schema.base import Document

logger = logging.getLogger(__name__)

class SlackThreadReader:

    """
    Slack のスレッドを読み込むクラスです。
    """

    def __init__(self, bot_user_id) -> None:
        self.bot_user_id = bot_user_id

        slack_token = os.environ["SLACK_BOT_TOKEN"]
        if slack_token is None:
            raise ValueError(
                "Must specify `slack_token` or set environment "
                "variable `SLACK_BOT_TOKEN`."
            )
        self.client = WebClient(token=slack_token)

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

                logger.info(
                    "{} messages found in {}".format(len(result["messages"]), id)
                )

                for message in result['messages']:
                    # ignore message from summaru
                    if message["user"] == self.bot_user_id:
                       logger.info("summaru message is ignored!")
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
