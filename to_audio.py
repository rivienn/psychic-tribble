import os
import re
from TTS.api import TTS
from config import TTSConfig
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.config.shared_configs import BaseDatasetConfig
from TTS.tts.models.xtts import XttsAudioConfig, XttsArgs
from torch.serialization import safe_globals, add_safe_globals


# Регистрируем классы как безопасные глобалы
add_safe_globals([XttsConfig, XttsAudioConfig, BaseDatasetConfig, XttsArgs])


class TextToSpeech:
    """TTS-МОДЕЛЬ ДЛЯ ГЕНЕРАЦИИ АУДИО ПО ГОЛОСОВОМУ СЛЕПКУ."""

    def __init__(self, config: TTSConfig):
        self.config = config
        self.language = self.config.language
        self.speaker_wav = self.config.speaker_wav

        with safe_globals([XttsConfig, XttsAudioConfig, BaseDatasetConfig, XttsArgs]):
            self.tts = TTS(
                model_name=self.config.model_name,
                progress_bar=False,
                gpu=self.config.device == "cuda"
            )

    @staticmethod
    # Проверка пути
    def _get_next_output_path(directory: str, prefix: str = "output_", extension: str = ".wav") -> str:
        os.makedirs(directory, exist_ok=True)
        existing = [f for f in os.listdir(directory) if f.startswith(prefix) and f.endswith(extension)]
        numbers = [
            int(re.search(rf"{prefix}(\d+){extension}", f).group(1))
            for f in existing if re.search(rf"{prefix}(\d+){extension}", f)
        ]
        next_index = max(numbers, default=0) + 1
        filename = f"{prefix}{next_index:02d}{extension}"
        return os.path.join(directory, filename)

    # Синтез речи
    def synthesize(self, text: str) -> str:
        output_path = self._get_next_output_path(str(self.config.output_dir))

        if self.speaker_wav:
            self.tts.tts_to_file(
                text=text,
                speaker_wav=self.speaker_wav,
                language=self.language,
                file_path=output_path
            )
        else:
            self.tts.tts_to_file(
                text=text,
                language=self.language,
                file_path=output_path
            )

        return output_path


# from config import TTSConfig
# from pipeline.tts import TextToSpeech
# # Запуск
# if __name__ == "__main__":
#     config = TTSConfig()
#     tts_model = TextToSpeech(config)
#     text = "[output_text]"
#     output_file = tts_model.synthesize(text)
