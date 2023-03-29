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

from llama_index import GPTSimpleVectorIndex, LLMPredictor
from langchain.chat_models import ChatOpenAI


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

    text    = re.sub(r'^<.*>\s+', '', event['text'])
    command = re.split(r'\s+', text)

    logger.info(event)
    logger.info("text: {}".format(text))
    logger.info("command: {}".format(command))

    if command[0] == "prompt":
        if not event.get("thread_ts"):
            say(text=config.behavior()['not_thread'])
            return

        subcommand = "default"
        if len(command) > 1:
            subcommand = command[1]

        if config.shared_prompts().get(subcommand) is None:
            say(text=config.behavior()['subcommand_not_found'], thread_ts=event['thread_ts'])
            logger.info("subcommand not found")
            return

        say(text=config.behavior()["summarying"], thread_ts=event['thread_ts'])

        channel_id  = event["channel"]
        thread_ts   = event["thread_ts"]
        bot_user_id = context["bot_user_id"]
        prompt      = config.shared_prompts()[ subcommand ]

        gpt     = SummaruGPT(bot_user_id=bot_user_id)
        summary = gpt.make_summary(channel_id=channel_id, thread_ts=thread_ts, query=prompt["query"])

        say(text=str(summary), thread_ts=event['thread_ts'])
    elif command[0] == "help":
        thread_ts = event.get("thread_ts")
        say(text=Help().help_text(), thread_ts=thread_ts)
    elif command[0] == "__debug":
        import pdb
        pdb.set_trace()
    else:
        if not event.get("thread_ts"):
            say(text=config.behavior()['not_thread'])
            logger.info("not thread")
            return

        response = context.client.users_info(user=event["user"])
        username = response["user"]["name"]
        blocks   = BlockKit().blocks(username=username)
        text     = config.behavior()["default"]

        say(blocks=blocks, text=text, thread_ts=event['thread_ts'])

@app.action("static_select-action")
def handle_some_action(ack, context, body, say, logger):
    logger.info(body)
    ack()

    channel_id  = body["container"]["channel_id"]
    thread_ts   = body["container"]["thread_ts"]
    bot_user_id = context["bot_user_id"]

    # dict is deep ...
    selected_type = body["state"]["values"][ Config.BLOCK_ID ][ Config.ACTION_ID ]["selected_option"]["value"]

    if re.match(r'\AUSER-', selected_type):
        _, username, index = selected_type.split("-")
        prompt = config.get_user_prompts(username, int(index))
    else:
        prompt = config.shared_prompts()[selected_type]

    query = prompt["query"]
    title = prompt["title"]

    say(text="<@{}> が `{}` を押したよ".format(body["user"]["id"], title), thread_ts=thread_ts)
    say(text=config.behavior()["summarying"], thread_ts=thread_ts)

    gpt     = SummaruGPT(bot_user_id=bot_user_id)
    summary = gpt.make_summary(channel_id=channel_id, thread_ts=thread_ts, query=query)

    say(text=str(summary), thread_ts=thread_ts)


class SummaruGPT:

    def __init__(self, bot_user_id):
        self.bot_user_id = bot_user_id

    def make_summary(self, channel_id, thread_ts, query):
        """
        SlackThreadReader でスレッドのデータを取得し、GPTSimpleVectorIndex で要約を行う
        """
        documents     = SlackThreadReader(bot_user_id=self.bot_user_id).load_data(channel_id=channel_id, thread_ts=thread_ts)
        llm_predictor = LLMPredictor(llm=ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo"))
        index    = GPTSimpleVectorIndex(documents, llm_predictor=llm_predictor)
        summary = index.query(query)
        return summary

# Start your app
if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
