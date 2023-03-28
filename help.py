"""
ヘルプ生成
"""
import yaml

class Help:

    """
    ヘルプ生成クラス
    """

    def __init__(self) -> None:
        with open("config.yaml", "r", encoding="utf8") as file:
            self.config = yaml.safe_load(file)

    def help_text(self):
        """
        help_text() は、ヘルプを返します。
        """

        help_text = self.config['message']['help']
        help_text += "\n"
        help_text += "```"
        for name, prompt in self.config["prompts"].items():
            help_text += "#{}\n".format(prompt["title"])
            help_text += "@summaru summary {}\n\n".format(name)

        help_text += "@summaru help\n"
        help_text += "```"

        return help_text
