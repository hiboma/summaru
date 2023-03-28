import sys
import os
import json
import yaml

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import bot
from block_kit import BlockKit

def test_json():
  with open("components/menu.json", "r", encoding="utf8") as file:
      block = json.load(file)

def test_yaml():
   with open('config.yaml', encoding="utf8") as file:
      config = yaml.safe_load(file)

def test_block_kit():
    block_kit = BlockKit()
    assert block_kit.blocks(), 'block_kit.blocks()'

def test_load_bot():
  assert True, 'only load test'
