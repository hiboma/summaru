import sys
import os
import json
import yaml
import re

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import bot
from block_kit import BlockKit
from help import Help
from config import Config
from summaru_gpt import SummaruGPT

def test_json():
  with open("components/menu.json", "r", encoding="utf8") as file:
      block = json.load(file)
      assert(block)

def test_config():
    config = Config()
    assert config.behavior(), 'config.behavior()'
    assert config.shared_prompts(), 'config.shared_prompts()'
    assert config.user_prompts(), 'config.user_prompts()'
    assert config.get_user_prompts("hito", 0), 'config.user_prompts()'

def test_block_kit():
    block_kit = BlockKit()
    assert block_kit.blocks(username="testuser"), 'block_kit.blocks()'
    assert block_kit.blocks(username="unknown"), 'block_kit.blocks()'

def test_help_text():
    assert Help().help_text().find("help")
    assert Help().help_text().find("@summaru summary summary")
    assert Help().help_text().find("@summaru summary kanso")

def test_summaru_gpt():
    gpt = SummaruGPT(bot_user_id="test")
    assert gpt

def test_load_bot():
  assert True, 'only load test'
