import os
import yaml
from openai import OpenAI


# --- Load configuration from YAML ---
with open("config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)


# --- Extract configuration values ---
api_key = config["albertai"]["api_key"]
base_url = config["albertai"].get("base_url", "https://albert.api.etalab.gouv.fr/v1")

paths = config["files"]
transcription_path = config["whisperx"]["output"]
template_path = paths["template"]
output_path = paths["output"]

# --- Check if test mode is enabled ---
test_mode = os.environ.get("TEST_MODE", "false").lower() == "true"

if test_mode:
    print("TEST MODE: Using test transcription file")
    transcription_path = transcription_path.replace(".txt", "_test.txt")
    output_path = output_path.replace(".txt", "_test.txt")

# --- Initialize AlbertAI client ---
client = OpenAI(
    base_url=base_url,
    api_key=api_key,
)

# Read the meeting transcription
with open(transcription_path, "r", encoding="utf-8") as f:
    transcription = f.read()

# Read the summary template
with open(template_path, "r", encoding="utf-8") as f:
    template = f.read()

# Prepare the messages for the model
messages = [
    {"role": "system", "content": "You are an expert assistant in writing meeting summaries. Your answer should consist only of the meeting summary, as detailed as possible. When information is missing, guess and prefix it with “IA-”. Ultrathink."},
    {"role": "user",   "content": f"Here is the template to follow:\n\n{template}"},
    {"role": "user",   "content": f"Here is the transcription to summarize:\n\n{transcription}"}
]

# Generate the summary
completion = client.chat.completions.create(
    model="albert-large",
    messages=messages
)

summary = completion.choices[0].message.content

# Save the summary to a file
with open(output_path, "w", encoding="utf-8") as f:
    f.write(summary)

print("Summary written to:", output_path)
