"""
ヘルプ生成
"""
import yaml
from config import Config

class Help:

    """
    ヘルプ生成クラス
    """

    def __init__(self) -> None:
        self.config = Config()

    def help_text(self):
        """
        help_text() は、ヘルプを返します。
        """

        help_text = self.config.behavior()["help"]
        help_text += "\n"
        help_text += "```"
        for name, prompt in self.config.prompts().items():
            help_text += "#{}\n".format(prompt["title"])
            help_text += "@summaru summary {}\n\n".format(name)

        help_text += "@summaru help\n"
        help_text += "```"

        return help_text
