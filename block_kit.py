"""
Slack Block Kit を生成するクラスです。
"""
import json
import yaml

from config import Config

class BlockKit:
    """
    Slack Block Kit を生成するクラスです。
    """

    def __init__(self):

        with open("components/menu.json", "r", encoding="utf8") as file:
            self.block = json.load(file)

        self.config = Config()

        for name, prompt in self.config.prompts().items():
            self.block["blocks"][0]["accessory"]["options"].append({
                "text": {
                    "type": "plain_text",
                    "text": prompt["title"],
                },
                "value": name
            })

    def blocks(self) -> dict:
        """
        Block Kit を返します。
        """
        return self.block["blocks"]
