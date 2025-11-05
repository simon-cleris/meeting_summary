#!/bin/bash
set -e

echo "Starting WhisperX transcription and diarization..."
python src/transcribe.py

echo ""
echo "Transcription completed. Starting summary generation..."
python src/meeting_summary.py

echo ""
echo "Pipeline completed successfully!"
