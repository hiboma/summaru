"""
bot.py は、Slack Bolt for Python を使用して Slack アプリを作成するためのサンプルコードです。
"""
import os
import logging
import re
import json
import yaml
import dotenv

from summaru_index import SlackThreadReader

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from config import Config

logging.basicConfig(level=logging.INFO)
dotenv.load_dotenv()

from llama_index import GPTSimpleVectorIndex

app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
)

config =Config()

@app.event("app_mention")
def event_test(context, event, body, say, logger):
    """
    event_test() は、アプリがメンションされたときに呼び出されます。
    """

    command = re.sub(r'^<.*>\s+', '', event['text'])
    logger.info(command)

    if command == "summary":
        if not event.get("thread_ts"):
            say(text=config.config['message']['not_thread'])
            logger.info("not thread")
            return

        say(text=config.config["message"]["summarying"], thread_ts=event['thread_ts'])

        documents = SlackThreadReader().load_data(channel_id=event["channel"], ts=event["thread_ts"])
        index     = GPTSimpleVectorIndex(documents)
        summary   = index.query(config.config["prompts"]["default"]["query"])

        say(text=str(summary), thread_ts=event['thread_ts'])

    elif command == "help":
        with open("button.json", "r", encoding="utf8") as file:
            block = json.load(file)
            say(blocks=[block], text="Hey")
    elif command == "s":

        thread_replies = context.client.conversations_replies(
            channel=event['channel'],
            ts=event['ts'],
            limit=1000,
        )

        print(thread_replies)

        with open("components/button.json", "r", encoding="utf8") as file:
            block = json.load(file)
        say(blocks=[block], text="Hey")

    else:
        say(text=config.config['message']['unknown_command'])

@app.action("button_click")
def handle_some_action(ack, body, logger):
    """
    handle_some_action() は、ボタンがクリックされたときに呼び出されます。
    """
    ack()
    logger.info(body)

# Start your app
if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
