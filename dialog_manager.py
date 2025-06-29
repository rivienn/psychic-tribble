import os
from config import PathConfig, TTSConfig
from audio_processing import AudioToText
from audio_processing import TextToSpeech


class DialogManager:
    """МЕНЕДЖЕР ДИАЛОГА: ОТСЛЕЖИВАЕТ ШАГИ, ОБНОВЛЯЕТ ИСТОРИЮ, КООРДИНИРУЕТ ЭЛЕМЕНТЫ ПАЙПАЛАЙНА"""

    def __init__(self):
        from llama_agent import LlamaGGUFModel     # отложенный импорт !!!

        self.paths = PathConfig()
        self.audio_pipeline = AudioToText()
        self.response_generator = LlamaGGUFModel()
        self.dialog_file = os.path.join(self.paths.data_text_dir, "dialog_history.txt")

        self.tts_config = TTSConfig()
        self.tts_model = TextToSpeech(self.tts_config)

        if not os.path.exists(self.dialog_file):
            with open(self.dialog_file, "w", encoding="utf-8") as f:
                f.write("")

    # Новая сессия
    def get_next_turn_number(self) -> str:
        if not os.path.exists(self.dialog_file):
            return "01"
        with open(self.dialog_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        turn_numbers = [int(line.split("_")[2].split(":")[0]) for line in lines if line.startswith("User_input_")]
        if turn_numbers:
            next_turn = max(turn_numbers) + 1
        else:
            next_turn = 1
        return f"{next_turn:02d}"

    # Добавление контекста
    def update_dialog_history(self, turn_num: str, user_text: str, assistant_text: str):
        with open(self.dialog_file, "a", encoding="utf-8") as f:
            f.write(f"User_input_{turn_num}: {user_text}\n")
            f.write(f"Assistant_output_{turn_num}: {assistant_text}\n\n")

    # Основная функция
    def run_pipeline(self):
        turn_num = self.get_next_turn_number()
        raw_audio = self.audio_pipeline.record_audio_raw(turn_num)
        clean_audio = self.audio_pipeline.process_audio(raw_audio, turn_num)
        user_text = self.audio_pipeline.transcribe_audio(clean_audio)
        assistant_text = self.response_generator.generate_response(user_text)
        self.tts_model = TextToSpeech(self.tts_config)
        self.tts_model.synthesize(assistant_text)
        self.update_dialog_history(turn_num, user_text, assistant_text)


# from llama_agent import DialogManager
# # Запуск
# if __name__ == "__main__":
#     pipeline = DialogManager()
#     pipeline.run_pipeline()
