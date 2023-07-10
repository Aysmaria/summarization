from typing import Dict, Union, List

# Import the necessary openai modules and initialize the API
import openai
import tiktoken

openai.api_key = "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"
class GPTModel:
    model_info = {
        'text-curie-001': {'token_limit': 2049, 'encoding': 'r50k_base'},
        'text-davinci-003': {'token_limit': 4097, 'encoding': 'r50k_base'},
        'gpt-3.5-turbo': {'token_limit': 4096, 'encoding': 'cl100k_base'},
        'gpt-3.5-turbo-16k': {'token_limit': 16384, 'encoding': 'cl100k_base'},
    }

    def __init__(self, model, prompt='Fasse den Text auf deutsch zusammen:'):
        self.model = model
        self.token_limit = self.model_info[model]['token_limit']
        self.encoding = self.model_info[model]['encoding']
        self.prompt = prompt

    def count_tokens(self, text) -> int:
        """Returns the number of tokens in a text string."""
        encoding = tiktoken.get_encoding(self.encoding)
        num_tokens = len(encoding.encode(text))
        return num_tokens

    def generate_summary_prompt_instruct(self, text: str, prompt: str = None) -> str:
        if prompt is None:
            prompt = self.prompt
            print(prompt)
        return f"{prompt} {text}"

    def summarize_instruct(self, text, params):
        # prompt = self.prompt
        prompt = self.generate_summary_prompt_instruct(text, self.prompt)
        print(self.count_tokens(prompt))
        print(prompt)
        # 1850 is for the issue if prompt len is ok for 2049 Curie but needs completion 200 which exceeds the limit
        if self.count_tokens(prompt) > self.token_limit or self.count_tokens(text) > 1850:
            print("Skipping text because it exceeds the maximum token limit for the model.")
            return ''
        else:
            response = openai.Completion.create(
                engine=self.model,
                prompt=prompt,
                max_tokens=params['max_tokens'],
                temperature=params['temperature']
            )

        summary = response.choices[0].text.strip()
        return summary

    def summarize_chat_model(self, text):
        if self.count_tokens(text) > self.token_limit:
            print(f'Skipping {text} because it exceeds the maximum token limit for the model.')
            return ''
        else:
            system_msg = 'You are a helpful assistant who knows how to summarize texts in german.'
            user_msg = f'Summarize following texts in german: {text}'

            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg}
                ]
            )
            summary = response.choices[0].message['content']

            return summary

    def generate_summary(self, text: str, params: Dict[str, Union[float, bool]]):
        if self.model == 'gpt-3.5-turbo' or self.model == 'gpt-3.5-turbo-16k':
            return self.summarize_chat_model(text)
        else:
            return self.summarize_instruct(text, params)

    def generate_summaries(self, texts: List[str], params: Dict[str, Union[float, bool]]) -> List[str]:
        return [self.generate_summary(text, params) for text in texts]

if __name__ == "__main__":
    # text = "Das ist ein Beispielsatz, um GPT zu prüfen."
    text = ["Italien hat als erstes Land Chat GPT aus Datenschutzgründen gesperrt. Ein solches Verbot droht jetzt auch in Deutschland. Der Bundesdatenschutzbeauftragte Ulrich Kelber hält eine Sperrung des auf künstlicher Intelligenz basierenden Chatbots hierzulande für denkbar. „Grundsätzlich ist ein solches Vorgehen auch in Deutschland möglich“, sagte eine Sprecherin Kelbers dem Handelsblatt. Allerdings falle das in den Zuständigkeitsbereich der Landeschutzbehörden."]
    models = ["text-curie-001", "gpt-3.5-turbo"]
    param_grid = {
        "max_tokens": 200,
        'temperature': 1
    }
    for model in models:
        text_summarizer = GPTModel(model)
        summaries = text_summarizer.generate_summaries(text, param_grid)
        print(summaries)
