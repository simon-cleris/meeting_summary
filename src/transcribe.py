import os
import multiprocessing as mp
import torch
import whisperx
import yaml
from whisperx.diarize import DiarizationPipeline
from pydub import AudioSegment

# --- Load configuration ---
with open("config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

whisper_cfg = config["whisperx"]
file_cfg = config["files"]

# --- Extract settings ---
audio_file = file_cfg["audio_file"]
device = whisper_cfg.get("device", "cpu")
hf_token = whisper_cfg["hf_token"]
output = whisper_cfg.get("output", "reunion_diarized.txt")
model_size = whisper_cfg.get("model_size", "medium")
language = whisper_cfg.get("language", "fr")
test_duration = whisper_cfg.get("test_duration", 60)

# --- Check if test mode is enabled ---
test_mode = os.environ.get("TEST_MODE", "false").lower() == "true"

if test_mode:
    print(f"TEST MODE: Processing only first {test_duration} seconds")
    # Create a temporary audio file with only the first N seconds
    audio = AudioSegment.from_file(audio_file)
    audio_test = audio[:test_duration * 1000]  # pydub works in milliseconds
    test_audio_file = audio_file.replace(".mp3", "_test.mp3")
    audio_test.export(test_audio_file, format="mp3")
    audio_file = test_audio_file
    output = output.replace(".txt", "_test.txt")

# --- Optimize CPU usage ---
total_cores = mp.cpu_count()
usable_cores = max(1, total_cores - 1)

os.environ["OMP_NUM_THREADS"] = str(usable_cores)
os.environ["MKL_NUM_THREADS"] = str(usable_cores)
torch.set_num_threads(usable_cores)

print(f" Using {usable_cores} CPU threads out of {total_cores}")

# --- Step 1: diarization ---
print("🔹 Running diarization...")
diarize_model = DiarizationPipeline(use_auth_token=hf_token, device=device)
diarization = diarize_model(audio_file)

# --- Step 2: transcription ---
print("🔹 Running transcription...")
model = whisperx.load_model(model_size, device, compute_type="float32")
transcription = model.transcribe(audio_file, language=language)

# --- Step 3: merge results ---
print("🔹 Merging results...")
final = whisperx.assign_word_speakers(diarization, transcription)

# --- Write diarized transcript ---
with open(output, "w", encoding="utf-8") as f:
    for seg in final["segments"]:
        f.write(f"[{seg['start']:.2f}s - {seg['end']:.2f}s] "
                f"{seg['speaker']}: {seg['text']}\n")

print(f" Diarized transcription saved to: {output}")
