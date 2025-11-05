# Using with Docker

## Prerequisites
- Docker is installed  
- Your audio files are placed in the `input/` folder  
- A valid Hugging Face token is set in `config.yaml`  
- A valid Albert API key is set in `config.yaml`  

## Usage

### Full mode (entire audio)
```bash
./run.sh


### Mode test (1 minute seulement)
```bash
./run.sh test
```

The run.sh script:
- Automatically builds the Docker image
- Runs transcription with speaker diarization (WhisperX)
- Generates a meeting summary using Albert AI
- Saves all results in the output/ folder

In test mode, generated files will include the _test suffix (e.g. meeting_diarized_test.txt).
