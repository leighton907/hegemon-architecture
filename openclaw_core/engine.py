import os
from .agent_loader import load_agent_config
from .memory import load_memory
from .logger import get_logger
from openai import OpenAI


class OpenClawEngine:

    def __init__(self, agent_path):
        self.config = load_agent_config(agent_path)
        self.memory = load_memory(self.config["memory"]["path"])
        self.logger = get_logger(self.config["logging"]["log_file"])
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def run(self, user_input):

        system_prompt = open(self.config["doctrine_file"]).read()

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
        )

        output = response.choices[0].message.content

        self.logger.info(output)

        return output
