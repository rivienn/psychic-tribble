import os
from gpt4all import GPT4All
from config import LlamaGGUFConfig, PathConfig


class LlamaGGUFModel:
    """ПРЕДОБУЧЕННАЯ И ДИСТИЛИРОВАННАЯ LLaMA-МОДЕЛЬ"""

    def __init__(self, config: LlamaGGUFConfig = None):
        from llama_agent import PromptRouting       # отложенный импорт !!!

        self.config = config or LlamaGGUFConfig()
        self.paths = PathConfig()
        self.dialog_file = os.path.join(self.paths.data_text_dir, "dialog_history.txt")

        self.model = GPT4All(
            model_name=self.config.model_name,
            model_path=self.config.model_path,
            n_ctx=self.config.context_size,
            verbose=self.config.verbose,
            allow_download=False,
            device=self.config.device,
        )

        self.prompt_engineer = PromptRouting()

    # Импорт контекста
    def _load_dialog_history(self) -> list:
        if not os.path.exists(self.dialog_file):
            return []

        history = []
        with open(self.dialog_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        user_input, assistant_output = None, None
        for line in lines:
            if line.startswith("User_input_"):
                user_input = line.split(":", 1)[1].strip()
            elif line.startswith("Assistant_output_"):
                assistant_output = line.split(":", 1)[1].strip()
                if user_input is not None:
                    history.append((user_input, assistant_output))
                    user_input, assistant_output = None, None
        return history

    @staticmethod
    # Шаблон для входа-выхода
    def _build_prompt(history: list, current_input: str) -> str:
        prompt = ""
        for user_text, assistant_text in history:
            prompt += f"User: {user_text}\nAssistant: {assistant_text}\n"
        prompt += f"User: {current_input}\nAssistant:"
        return prompt

    # Осмысленный ответ
    def generate_response(self, current_input: str) -> str:
        history = self._load_dialog_history()
        prompt = self.prompt_engineer.build_prompt(user_input=current_input, history=history)

        with self.model.chat_session():
            response = self.model.generate(
                prompt=prompt,
                max_tokens=self.config.max_tokens,
                temp=self.config.temp,
                top_k=self.config.top_k,
                top_p=self.config.top_p,
                min_p=self.config.min_p,
                repeat_penalty=self.config.repeat_penalty,
                repeat_last_n=self.config.repeat_last_n,
                n_batch=self.config.n_batch,
                n_predict=self.config.n_predict,
                streaming=self.config.streaming,
            ).strip()

        return response


# # from llama_agent import LlamaGGUFModel
# # Запуск
# if __name__ == "__main__":
#     model = LlamaGGUFModel()
#     user_input = "text"
#     assistant_response = model.generate_response(user_input)
#     print(f"Assistant: {assistant_response}")
