import os
import time
import whisper
import torchaudio
import numpy as np
import soundfile as sf
import sounddevice as sd
from config import AudioConfig, PathConfig, WhisperConfig, CUDAConfig

CUDAConfig()


class AudioToText:
    """ЗАПИСЬ И ТРАНСКРИБИРОВАНИЕ АУДИО ОТ ПОЛЬЗОВАТЕЛЯ"""

    def __init__(self):
        from audio_processing import UVRSeparator
        self.paths = PathConfig()
        self.audio_cfg = AudioConfig()
        self.whisper_cfg = WhisperConfig()
        self.uvr_separator = UVRSeparator()

        self.model = whisper.load_model(
            self.paths.whisper_model_path,
            device=self.whisper_cfg.device
        )

    # Запись аудио
    def record_audio_raw(self, turn_num: str) -> str:
        file_path = os.path.join(self.paths.data_speech_dir, f"input_{turn_num}_raw.wav")
        frames = []
        silent_duration = 0.0
        start_time = time.time()

        with sd.InputStream(
                samplerate=self.audio_cfg.sample_rate,
                channels=1,
                dtype="float32"
        ) as stream:
            while True:
                data, _ = stream.read(self.audio_cfg.chunk_samples)
                frames.append(data.copy())
                rms = np.sqrt(np.mean(data ** 2))
                if rms < self.audio_cfg.silence_threshold:
                    silent_duration += self.audio_cfg.chunk_duration
                else:
                    silent_duration = 0.0
                if silent_duration >= self.audio_cfg.silence_limit or \
                        (time.time() - start_time) >= self.audio_cfg.max_duration:
                    break

        audio_data = np.concatenate(frames, axis=0)
        audio_data = (audio_data * 32767).astype(np.int16)
        stereo_data = np.column_stack((audio_data, audio_data))
        sf.write(file_path, stereo_data, self.audio_cfg.sample_rate, subtype="PCM_16")
        return file_path

    # Аудио процесиинг (сегментация голоса, нормализация и ресемплинг)
    def process_audio(self, input_file: str, turn_num: str) -> str:
        output_file = os.path.join(self.paths.data_speech_dir, f"input_{turn_num}_clean.wav")
        if os.path.exists(output_file):
            return output_file

        waveform, sr = torchaudio.load(input_file)
        if sr != self.audio_cfg.sample_rate:
            resampler = torchaudio.transforms.Resample(orig_freq=sr, new_freq=self.audio_cfg.sample_rate)
            waveform = resampler(waveform)

        max_val = waveform.abs().max()
        if max_val > 0:
            waveform = waveform / max_val * 0.99

        torchaudio.save(output_file, waveform, self.audio_cfg.sample_rate)
        return output_file

    # Транскрибирование
    def transcribe_audio(self, clean_audio_file: str) -> str:
        result = self.model.transcribe(
            clean_audio_file,
            language=self.whisper_cfg.target_language,
            fp16=self.whisper_cfg.fp16
        )
        return result.get("text", "").strip()


# # from modeling import AudioToText
# # Запуск
# if __name__ == "__main__":
#     pipeline = AudioToText()
#     turn_num = "01"  # сессия
#     raw_path = pipeline.record_audio_raw(turn_num)
#     clean_path = pipeline.process_audio(raw_path, turn_num)
#     transcript = pipeline.transcribe_audio(clean_path)
