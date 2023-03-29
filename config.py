import yaml

# https://refactoring.guru/ja/design-patterns/singleton/python/example
class SingletonMeta(type):
    """
    The Singleton class can be implemented in different ways in Python. Some
    possible methods include: base class, decorator, metaclass. We will use the
    metaclass because it is best suited for this purpose.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]
class Config(metaclass=SingletonMeta):
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

    def llm_model_name(self):
        return self._config["model"]

    def behavior(self):
        return self._config.get("behavior")

    def shared_prompts(self):
        return self._prompt.get("shared_prompts")

    def user_prompts(self):
        return self._prompt.get("user_prompts")

    def get_user_prompts(self, username: str, index: int):
        return self._prompt.get("user_prompts")[username][index]
