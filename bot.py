"""
bot.py は、Slack Bolt for Python を使用して Slack アプリを作成するためのサンプルコードです。
"""
import os
import logging
import re
import dotenv
from optparse import OptionParser

from help import Help
from config import Config
from block_kit import BlockKit
from summaru_gpt import SummaruGPT

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

dotenv.load_dotenv()

app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    token_verification_enabled=False,
)

@app.event("app_mention")
def event_test(context, event, say, logger):
    """
    event_test() は、アプリがメンションされたときに呼び出されます。
    """
    config  = Config()
    text    = re.sub(r'^<.*>\s+', '', event['text'])
    command = re.split(r'\s+', text)
    thread_ts = event.get("thread_ts")

    logger.info(event)
    logger.info("text: {}".format(text))
    logger.info("command: {}".format(command))

    if command[0] == "prompt":
        if thread_ts is None:
            say(text=config.behavior()['not_thread'])
            return

        subcommand = "default"
        if len(command) > 1:
            subcommand = command[1]

        if config.shared_prompts().get(subcommand) is None:
            say(text=config.behavior()['subcommand_not_found'], thread_ts=thread_ts)
            logger.info("subcommand not found")
            return

        say(text="ちょっと待ってててね ...", thread_ts=thread_ts)

        channel_id  = event["channel"]
        thread_ts   = event["thread_ts"]
        bot_user_id = context["bot_user_id"]
        prompt      = config.shared_prompts()[ subcommand ]

        gpt     = SummaruGPT(bot_user_id=bot_user_id)
        summary = gpt.make_summary(channel_id=channel_id, thread_ts=thread_ts, query=prompt["query"])

        say(text=str(summary), thread_ts=thread_ts)
    elif command[0] == "help":
        say(text=Help().help_text(), thread_ts=thread_ts)
    elif command[0] == "ping":
        say(text="pong", thread_ts=thread_ts)
    elif command[0] == "__debug":
        import pdb
        pdb.set_trace()
    else:
        if thread_ts is None:
            say(text=config.behavior()['not_thread'])
            logger.info("not thread")
            return

        # response = context.client.users_info(user=event["user"])
        # username = response["user"]["name"]
        blocks   = BlockKit().blocks(username="hoge")
        text     = config.behavior()["default"]

        say(blocks=blocks, text=text, thread_ts=thread_ts)

@app.view("")
def handle_view_submission_events(ack, context, body, logger):
    logger.info(body)

    ack()

    query = body["view"]["state"]["values"][ Config.BLOCK_ID ]["plain_text_input-action"]["value"]
    channel_id, thread_ts = body["view"]["private_metadata"].split("/")
    bot_user_id           = context["bot_user_id"]

    context.client.chat_postMessage(
        channel=channel_id,
        text="execute free prompt ...\n```\n{}\n```".format(query),
        thread_ts=thread_ts
    )

    gpt = SummaruGPT(bot_user_id=bot_user_id)
    summary = gpt.make_summary(
        channel_id=channel_id,
        thread_ts=thread_ts,
        query=query
    )
    context.client.chat_postMessage(
        channel=channel_id,
        text=str(summary),
        thread_ts=thread_ts
    )


@app.action("static_select-action")
def handle_some_action(ack, context, body, say, logger):
    logger.info(body)
    ack()

    config      = Config()
    channel_id  = body["container"]["channel_id"]
    thread_ts   = body["container"]["thread_ts"]
    user_id     = body["user"]["id"]
    bot_user_id = context["bot_user_id"]

    # dict is deep ...
    selected_type = body["state"]["values"][ Config.BLOCK_ID ][ Config.ACTION_ID ]["selected_option"]["value"]

    if selected_type == "free-prompt":
        private_metadata = "{}/{}".format(channel_id, thread_ts)
        modal = BlockKit().modal_template()
        modal["private_metadata"] = private_metadata
        response = context.client.views_open(trigger_id=body["trigger_id"], view=modal)
        print(response)
        return

    # user prompt
    if re.match(r'\AUSER-', selected_type):
        _, username, index = selected_type.split("-")
        prompt = config.get_user_prompts(username, int(index))
    else:
        prompt = config.shared_prompts()[selected_type]

    query = prompt["query"]
    title = prompt["title"]

    # feedback message
    if user_id is not None:
        say(text=config.behavior()["summarying"].format(user_id, title), thread_ts=thread_ts)
    else:
        say(text="ちょっと待ってててね ...", thread_ts=thread_ts)

    gpt     = SummaruGPT(bot_user_id=bot_user_id)
    summary = gpt.make_summary(channel_id=channel_id, thread_ts=thread_ts, query=query)

    # show summary
    say(text=str(summary), thread_ts=thread_ts)

# Start your app
if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-d", "--debug", action="store_true", dest="debug", default=False,  help="debug output")

    (options, args) = parser.parse_args()
    if options.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
