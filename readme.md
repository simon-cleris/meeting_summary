# Meeting Summarizer with WhisperX and Albert AI

A complete solution for transcribing, diarizing, and summarizing meeting recordings locally. This project combines **WhisperX** for local audio transcription, **Pyannote** for speaker identification, and **Albert AI** (French government LLM) for intelligent summarization.

## Data Privacy & Security

**All audio processing is done locally on your machine:**
- **Transcription**: Performed locally using WhisperX
- **Diarization** (speaker identification): Performed locally using Pyannote models
- **Audio files never leave your machine**

The only external service used is **Albert AI** (French government LLM) for text summarization:
- Only the transcribed text is sent to Albert AI (not the audio)
- Albert AI is provided by the French government and guarantees that data is not shared with third parties
- The choice to process transcription locally was made because Albert AI do not handle diarization, making it simpler to use WhisperX for complete local audio processing

---

## 1) System Requirements

- Linux (or Windows Subsystem for Linux)
- Docker installed

If you don't have sudo rights on your machine, ask the DSI to install Docker and ensure that you can use Docker without sudo following these steps :

From the [Docker documentation](https://docs.docker.com/engine/install/linux-postinstall/):

The Docker daemon binds to a Unix socket, not a TCP port. By default, it's the root user that owns the Unix socket, and other users can only access it using `sudo`. The Docker daemon always runs as the root user.

If you don't want to preface the `docker` command with `sudo`, create a Unix group called `docker` and add users to it. When the Docker daemon starts, it creates a Unix socket accessible by members of the docker group. On some Linux distributions, the system automatically creates this group when installing Docker Engine using a package manager. In that case, there is no need for you to manually create the group.

### To create the docker group and add your user:

1. Create the docker group:
   ```bash
   sudo groupadd docker
   ```

2. Add your user to the docker group:
   ```bash
   sudo usermod -aG docker $USER
   ```

3. Log out and log back in so that your group membership is re-evaluated.
   - If you're running Linux in a virtual machine, it may be necessary to restart the virtual machine for changes to take effect.

4. You can also run the following command to activate the changes to groups:
   ```bash
   newgrp docker
   ```

5. Verify that you can run docker commands without sudo:
   ```bash
   docker run hello-world
   ```


---

## 2) Create a Hugging Face Token (Required)

1. Go to: https://huggingface.co/settings/tokens
2. Click **New token**
3. Choose access type **Read**
4. Copy your token (e.g., `hf_XXXXXXXXXXXXXXXXXXXXXXXX`)

Keep this token ready; you'll need it to access Pyannote models.

## 3) Accept Pyannote Model Terms (Mandatory)

While signed in to the same Hugging Face account as your token, open these pages and click **"Agree and access repository"**:

- https://huggingface.co/pyannote/segmentation-3.0
- https://huggingface.co/pyannote/embedding
- https://huggingface.co/pyannote/speaker-diarization-3.1

If you don't accept these gates, diarization downloads will fail even with a valid token.

## 4) Get Albert API Key (Required for Summarization)

Albert is a French government AI service that provides language models for public administration. It guarantees data sovereignty and ensures that your data is not shared with third parties.

**Important**: Only the transcribed text (not the audio) is sent to Albert AI for summarization.

1. Go to: https://albert.sites.beta.gouv.fr/
2. Click on **"Essayer notre API"** (Try our API)
3. Follow the registration process to obtain your API key
4. Copy your API token (format: `sk-XXXXXXXXXXXXXXXXXXXXXXXX`)

Keep this token ready; you'll need it in the configuration file for the summarization feature.

## 5) Configuration File

The project uses a `config.yaml` file to manage all settings. Before running the application, you need to configure this file with your API keys and preferences.

### Template Recommendation

**It is strongly recommended to use a LaTeX template** instead of a Markdown template for better formatting control and professional output.

Place your template in the `input/` directory and update the configuration accordingly (e.g., `input/template.tex`).

### Configuration Structure

```yaml
# ALBERT API Configuration
albertai:
  api_key: "your-albert-api-key-here"  # REQUIRED: Your Albert API token
  base_url: "https://albert.api.etalab.gouv.fr/v1"

# File paths
files:
  template: "input/template.md"       # RECOMMENDED: Use your template (LaTeX prefered)
  output: "output/meeting_summary.txt"
  audio_file: "input/your-audio-file.mp3"

# WhisperX settings
whisperx:
  device: "cpu"                    # or "cuda" if you have a GPU
  hf_token: "your-hf-token-here"   # REQUIRED: Your Hugging Face token
  output: "output/meeting_diarized.txt"
  model_size: "medium"             # Options: tiny/base/small/medium/large
  language: "fr"                   # Language of the meeting (e.g., "fr", "en")
  test_duration: 60                # Duration in seconds for test mode
```

### Required Configuration Steps

1. **ALBERT API Key** (required for summarization):
   - Replace `api_key` with your ALBERT API key from step 4
   - This is needed to generate meeting summaries using the Albert language model

2. **Hugging Face Token** (required for diarization):
   - Replace `hf_token` with your Hugging Face token (from step 2)

3. **Audio File**:
   - Place your audio file in the `input/` directory
   - Update `audio_file` with the path to your file

4. **Model Settings**:
   - `model_size`: Choose based on accuracy vs. speed tradeoff
     - `tiny`: Fastest, lowest accuracy
     - `small`: Fast, good for testing
     - `medium`: Balanced (recommended)
     - `large`: Best accuracy, slowest
   - `language`: Set to your audio language (e.g., "fr" for French, "en" for English)
   - `device`: Use "cpu" for CPU-only systems, "cuda" for GPU

## 6) Running the Application

Once your configuration is complete, you can run the application using the provided shell script.

### Test Mode (Recommended for First Run)

To verify that everything is configured correctly, you can run the application in test mode, which will process only the first 60 seconds of your audio file:

```bash
./run.sh test
```

This is useful for:
- Verifying your API keys are valid
- Testing that all dependencies are installed correctly
- Quickly checking the output format
- Saving time during initial setup

### Full Mode

To process the entire audio file:

```bash
./run.sh
```

### What the Script Does

The script will:
1. Build the Docker image named `meeting-summarizer`
2. Mount your `input/`, `output/` directories and `config.yaml` file
3. Run the transcription and diarization locally using WhisperX
4. Generate a summary using Albert AI
5. Save all results to the `output/` directory

### Output Files

After running, check the `output/` directory for:
- `meeting_diarized.txt` - Transcription with speaker identification
- `meeting_summary.txt` - AI-generated summary of the meeting

