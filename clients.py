import anthropic
import openai
import os


class ChatGPTClient:
    def __init__(self):
        self.model="gpt-3.5-turbo"
        self.messages = [
                {"role": "system", "content": "You are a helpfull assistant."}
        ]

    def complete(self, question):

        self.messages.append({"role": "user", "content": question})

        resp = openai.ChatCompletion.create(
            model= self.model,
            messages = self.messages
        )

        message = resp["choices"][0]["message"]

        self.messages.append(message)


        return message["content"]


class ClaudeClient:
    def __init__(self):
        self.client = anthropic.Client(os.environ["ANTHROPIC_API_KEY"])
        self.question = f"{anthropic.HUMAN_PROMPT}"
 
    def complete(self, question, max_tokens_to_sample=100):

        self.question = f"{self.question} {question} {anthropic.AI_PROMPT}"

        resp = self.client.completion(
            prompt=self.question,
            stop_sequences=[anthropic.HUMAN_PROMPT, anthropic.AI_PROMPT],
            model="claude-v1",
            max_tokens_to_sample=max_tokens_to_sample,
        )

        answer = resp["completion"]

        print(answer)

        self.question = f"{self.question} {answer}"

        print(self.question)


        return answer

