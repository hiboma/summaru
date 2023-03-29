import yaml

class Config:
    """
    このクラスは、config.yaml を読み込みます。
    """

    BLOCK_ID  = "summary_type"
    ACTION_ID = "static_select-action"

    def __init__(self):
        with open('config.yaml', encoding="utf8") as file:
            self._config = yaml.safe_load(file)

        with open('prompt.yaml', encoding="utf8") as file:
            self._prompt = yaml.safe_load(file)

    def behavior(self):
        return self._config.get("behavior")

    def shared_prompts(self):
        return self._prompt.get("shared_prompts")

    def user_prompts(self):
        return self._prompt.get("user_prompts")

    def get_user_prompts(self, username: str, index: int):
        return self._prompt.get("user_prompts")[username][index]
