import yaml

class Config:
    """
    このクラスは、config.yaml を読み込みます。
    """

    BLOCK_ID  = "summary_type"
    ACTION_ID = "static_select-action"

    def __init__(self):
        with open('config.yaml', encoding="utf8") as file:
            self.config = yaml.safe_load(file)

    def reload(self):
        """
        _summary_config() は、config.yaml を再読み込みします。
        """
        with open('config.yaml', encoding="utf8") as file:
            self.config = yaml.safe_load(file)
