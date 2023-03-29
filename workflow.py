import dotenv
import os

from slack_bolt.workflows.step import WorkflowStep
from slack_bolt import App

dotenv.load_dotenv()

def edit(ack, step, configure):
    ack()

    blocks = [
        {
            "type": "input",
            "block_id": "task_name_input",
            "element": {
                "type": "plain_text_input",
                "action_id": "name",
                "placeholder": {"type": "plain_text", "text": "前ステップのフォームで入力させる変数を設定。"},
            },
            "label": {"type": "plain_text", "text": "ClickUpのTask name"},
        },
        {
            "type": "input",
            "block_id": "task_description_input",
            "element": {
                "type": "plain_text_input",
                "action_id": "description",
                "placeholder": {"type": "plain_text", "text": "前ステップのフォームで入力させる変数を設定。"},
            },
            "label": {"type": "plain_text", "text": "ClickUpのTask description"},
        },
        {
            "type": "input",
            "block_id": "listid_input",
            "element": {
                "type": "plain_text_input",
                "action_id": "listid",
                "placeholder": {"type": "plain_text", "text": "タスクを登録させたいClickUpのリストIDを入力。（8ケタの数字）"},
            },
            "label": {"type": "plain_text", "text": "タスクを登録させたいClickUpのList ID"},
        },
    ]
    configure(blocks=blocks)


def save(ack, view, update):
    ack()

    values = view["state"]["values"]
    task_name = values["task_name_input"]["name"]
    task_description = values["task_description_input"]["description"]
    clickup_listid= values['listid_input']['listid']

    inputs = {
        "task_name": {"value": task_name["value"]},
        "task_description": {"value": task_description["value"]},
        "clickup_listid": {"value": clickup_listid["value"]}
    }

    outputs = [
        {
            "type": "text",
            "name": "task_name",
            "label": "Task name",
        },
        {
            "type": "text",
            "name": "task_description",
            "label": "Task description",
        },
        {
            "type": "text",
            "name": "clickup_listid",
            "label": "Clickup ListID",
        }
    ]
    update(inputs=inputs, outputs=outputs)


def execute(step, complete, fail):
    inputs = step["inputs"]
    # すべての処理が成功した場合
    outputs = {
        "task_name": inputs["task_name"]["value"],
        "task_description": inputs["task_description"]["value"],
        "clickup_listid": inputs["clickup_listid"]["value"],
    }
    complete(outputs=outputs)

    # 失敗した処理がある場合
    error = {"message": "Just testing step failure!"}
    fail(error=error)

# WorkflowStep の新しいインスタンスを作成する
ws = WorkflowStep(
    callback_id="clickup_task_create",
    edit=edit,
    save=save,
    execute=execute,
)

app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    token_verification_enabled=False,
)
# ワークフローステップを渡してリスナーを設定する
app.step(ws)
