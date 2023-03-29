"""
Slack Block Kit を生成するクラスです。
"""
import json
import yaml
import os

from config import Config

class BlockKit:
    """
    Slack Block Kit を生成するクラスです。
    """

    def __init__(self):
        self.config = Config()

    def modal_template(self):
        template = {
            "type": "modal",
            "title": {"type": "plain_text", "text": "@summaru"},
            "submit": {"type": "plain_text", "text": "Submit"},
 	        "blocks": [
		    {
			    "type": "input",
       			"block_id": "summary_type",
	    		"element": {
		    		"type": "plain_text_input",
			    	"multiline": True,
				    "action_id": "plain_text_input-action",
                    "initial_value": "Please make summary",
			    },
			    "label": {
    				"type": "plain_text",
				    "text": "Free Prompt",
			    }
            }
	        ]
        }
        return template

    def load_block(self):
        with open("components/menu.json", "r", encoding="utf8") as file:
            self.block = json.load(file)

        self.block["blocks"][0]["text"]["text"] = self.config.behavior()["menu"]

    def build_free_prompts(self):
        """
        shared prompts を追加します。
        """

        options_groups = {
            "label": {
            	"type": "plain_text",
				"text": "free prompts",
            },
            "options": [
                {
                    "text": {
                        "type": "plain_text",
                        "text": self.config.behavior()["free_prompt"],
                    },
                    "value": "free-prompt",
                }
            ],
        }

        self.block["blocks"][0]["accessory"]["option_groups"].append(options_groups)

    def build_shared_prompts(self):
        """
        shared prompts を追加します。
        """
        for name, prompt in self.config.shared_prompts().items():
            self.block["blocks"][0]["accessory"]["option_groups"][0]["options"].append({
                "text": {
                    "type": "plain_text",
                    "text": prompt["title"],
                },
                "value": name
            })

    def build_user_prompts(self, username: str):
        """
        user prompts を追加します。
        """
        user_prompts = self.config.user_prompts()
        prompts = user_prompts.get(username)
        if prompts is None:
            return

        options_groups = {
            "label": {
                "type": "plain_text",
				"text": "user prompts",
            },
            "options": [],
        }

        for i, prompt in enumerate(prompts):
            options_groups["options"].append({
                "text": {
                    "type": "plain_text",
                    "text": prompt["title"],
                },
                "value": "USER-{}-{}".format(username, i),
            })

        self.block["blocks"][0]["accessory"]["option_groups"].append(options_groups)

    def blocks(self, username: str) -> dict:
        """
        Block Kit を返します。
        """
        self.load_block()
        self.build_shared_prompts()
        self.build_user_prompts(username=username)
        self.build_free_prompts()

        return self.block["blocks"]
