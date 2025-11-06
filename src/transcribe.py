import os
import multiprocessing as mp
import gc
import psutil
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
compute_type = "float16" if device == "cuda" else "float32"

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

# --- Auto-detect optimal batch size ---
if device == "cuda":
    # Get available GPU memory
    gpu_memory_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
    # Adjust batch size based on GPU memory
    if gpu_memory_gb >= 24:
        batch_size = 32
    elif gpu_memory_gb >= 16:
        batch_size = 24
    elif gpu_memory_gb >= 8:
        batch_size = 16
    elif gpu_memory_gb >= 4:
        batch_size = 8
    else:
        batch_size = 4
    print(f" GPU detected: {gpu_memory_gb:.1f}GB, using batch_size={batch_size}")
else:
    # For CPU, check available RAM
    ram_gb = psutil.virtual_memory().available / (1024**3)
    if ram_gb >= 32:
        batch_size = 16
    elif ram_gb >= 16:
        batch_size = 8
    elif ram_gb >= 8:
        batch_size = 4
    else:
        batch_size = 2
    print(f" CPU mode: {ram_gb:.1f}GB RAM available, using batch_size={batch_size}")

# --- Step 1: Transcribe with batched processing ---
print(f"🔹 Step 1: Running transcription (language: {language})...")
model = whisperx.load_model(model_size, device, compute_type=compute_type, language=language)
audio = whisperx.load_audio(audio_file)
result = model.transcribe(audio, batch_size=batch_size)

# Delete model if low on GPU resources
if device == "cuda":
    gc.collect()
    torch.cuda.empty_cache()
    del model

# --- Step 2: Align whisper output ---
print("🔹 Step 2: Aligning transcription...")
model_a, metadata = whisperx.load_align_model(language_code=language, device=device)
result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)

# Delete alignment model if low on GPU resources
if device == "cuda":
    gc.collect()
    torch.cuda.empty_cache()
    del model_a

# --- Step 3: Diarization ---
print("🔹 Step 3: Running diarization...")
diarize_model = DiarizationPipeline(use_auth_token=hf_token, device=device)
diarize_segments = diarize_model(audio)

# --- Step 4: Assign speaker labels ---
print("🔹 Step 4: Assigning speaker labels...")
result = whisperx.assign_word_speakers(diarize_segments, result)

# --- Write diarized transcript ---
with open(output, "w", encoding="utf-8") as f:
    for seg in result["segments"]:
        speaker = seg.get("speaker", "UNKNOWN")
        f.write(f"[{seg['start']:.2f}s - {seg['end']:.2f}s] "
                f"{speaker}: {seg['text']}\n")

print(f" Diarized transcription saved to: {output}")
