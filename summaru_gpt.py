from llama_index import GPTSimpleVectorIndex, LLMPredictor
from langchain.chat_models import ChatOpenAI

from config import Config
from summaru_index import SlackThreadReader

class SummaruGPT:

    def __init__(self, bot_user_id):
        self.bot_user_id = bot_user_id
        self.config = Config()

    def llm_predictor(self):
        """
        LLM の予測器を返す
        """
        return LLMPredictor(llm=ChatOpenAI(temperature=0, model_name=self.config.llm_model_name()))

    def make_documents(self, channel_id, thread_ts):
        """
        SlackThreadReader でスレッドのデータを取得して Document の配列を返す
        """
        reader = SlackThreadReader(bot_user_id=self.bot_user_id)
        return reader.load_data(channel_id=channel_id, thread_ts=thread_ts)

    def make_summary(self, channel_id, thread_ts, query):
        """
        SlackThreadReader でスレッドのデータを取得し、GPTSimpleVectorIndex で要約を行う
        """
        documents = self.make_documents(channel_id=channel_id, thread_ts=thread_ts)
        index     = GPTSimpleVectorIndex(documents, llm_predictor=self.llm_predictor())
        summary   = index.query(query)
        return summary
