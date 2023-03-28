"""
bot.py は、Slack Bolt for Python を使用して Slack アプリを作成するためのサンプルコードです。
"""
import os
import logging
import re
import json
import yaml
import dotenv
from optparse import OptionParser


from help import Help
from summaru_index import SlackThreadReader
from config import Config
from block_kit import BlockKit

dotenv.load_dotenv()

from llama_index import GPTSimpleVectorIndex

parser = OptionParser()
parser.add_option("-d", "--debug",
                  action="store_true", dest="debug", default=False,
                  help="debug output")

(options, args) = parser.parse_args()

if options.debug:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    token_verification_enabled=False,
)

config =Config()

@app.event("app_mention")
def event_test(context, event, body, say, logger):
    """
    event_test() は、アプリがメンションされたときに呼び出されます。
    """

    text = re.sub(r'^<.*>\s+', '', event['text'])
    logger.info(text)
    command = re.split(r'\s+', text)
    logger.info(command)

    if command[0] == "summary":
        if not event.get("thread_ts"):
            say(text=config.config['message']['not_thread'])
            logger.info("not thread")
            return

        subcommand = "default"
        if len(command) > 1:
            subcommand = command[1]

        if config.config["prompts"].get(subcommand) is None:
            say(text=config.config['message']['subcommand_not_found'], thread_ts=event['thread_ts'])
            logger.info("subcommand not found")
            return

        say(text=config.config["message"]["summarying"], thread_ts=event['thread_ts'])

        channel_id = event["channel"]
        thread_ts  = event["thread_ts"]
        query = config.config["prompts"][ subcommand ]["query"]

        summary = SummaruGPT().make_summary(channel_id=channel_id, thread_ts=thread_ts, query=query)

        say(text=str(summary), thread_ts=event['thread_ts'])
    elif command[0] == "help":
        thread_ts = event.get("thread_ts")
        say(text=Help().help_text(), thread_ts=thread_ts)
    elif command[0] == "s":

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
        if not event.get("thread_ts"):
            say(text=config.config['message']['not_thread'])
            logger.info("not thread")
            return

        say(blocks=BlockKit().blocks(), text=config.config["message"]["default"], thread_ts=event['thread_ts'])

@app.action("static_select-action")
def handle_some_action(ack, body, event, say, logger):
    ack()

    channel_id = body["container"]["channel_id"]
    thread_ts  = body["container"]["thread_ts"]

    selected_type = body["state"]["values"][ Config.BLOCK_ID ][ Config.ACTION_ID ]["selected_option"]["value"]
    query      = config.config["prompts"][selected_type]["query"]

    say(text=config.config["message"]["summarying"], thread_ts=thread_ts)

    summary = SummaruGPT().make_summary(channel_id=channel_id, thread_ts=thread_ts, query=query)
    say(text=str(summary), thread_ts=thread_ts)


class SummaruGPT:

    def make_summary(self, channel_id, thread_ts, query):
        """
        SlackThreadReader でスレッドのデータを取得し、GPTSimpleVectorIndex で要約を行う

        """
        documents = SlackThreadReader().load_data(channel_id=channel_id, thread_ts=thread_ts)
        index = GPTSimpleVectorIndex(documents)
        summary = index.query(query)
        return summary

# Start your app
if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
