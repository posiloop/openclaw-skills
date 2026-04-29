#!/usr/bin/env bash
# meeting-video-to-summary pipeline
# Usage: run.sh <google-drive-url-or-local-file> [meeting-name]
# Output: ~/Desktop/meeting-records/<YYYY-MM-DD>_<meeting-name>/
#         ├── video.mp4
#         ├── audio.mp3
#         └── transcript.txt

set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 <google-drive-url-or-local-file> [meeting-name]" >&2
  exit 1
fi

INPUT="$1"
MEETING_NAME="${2:-meeting}"
SAFE_NAME=$(echo "$MEETING_NAME" | tr ' /\\' '---')
DATE=$(date +%Y-%m-%d)

ROOT="$HOME/Desktop/meeting-records"
OUTDIR="$ROOT/${DATE}_${SAFE_NAME}"

# avoid overwriting existing folder
if [ -d "$OUTDIR" ]; then
  OUTDIR="${OUTDIR}_$(date +%H%M%S)"
fi
mkdir -p "$OUTDIR"

echo "[info] output dir: $OUTDIR"
cd "$OUTDIR"

# ---- Step 1: fetch video ----
echo "[1/3] fetching video..."
if [[ "$INPUT" =~ ^https?:// ]]; then
  gdown --fuzzy "$INPUT" -O video.mp4
else
  if [ ! -f "$INPUT" ]; then
    echo "[error] local file not found: $INPUT" >&2
    exit 1
  fi
  cp "$INPUT" ./video.mp4
fi

# ---- Step 2: extract audio ----
echo "[2/3] extracting audio (mono 16kHz mp3)..."
ffmpeg -y -hide_banner -loglevel error \
  -i video.mp4 -vn -ac 1 -ar 16000 -c:a libmp3lame -q:a 4 audio.mp3

DURATION=$(ffprobe -v error -show_entries format=duration \
  -of default=noprint_wrappers=1:nokey=1 audio.mp3 | awk '{printf "%02d:%02d:%02d\n", $1/3600, ($1%3600)/60, $1%60}')
echo "[info] audio duration: $DURATION"

# ---- Step 3: transcribe via OpenAI whisper-1 ----
# Model choice: whisper-1 (not gpt-4o-transcribe). Rationale, tested 2026-04 on a 63-min
# Chinese meeting: gpt-4o-transcribe truncated output past ~8min, produced Simplified Chinese
# even with language=zh, and hallucinated phrases. whisper-1 ran the full 63-min file in one
# call (no duration cap), produced Traditional Chinese, and was more accurate on tech terms.
# Override with TRANSCRIBE_MODEL=gpt-4o-transcribe if you specifically want to try it.
MODEL="${TRANSCRIBE_MODEL:-whisper-1}"
echo "[3/3] transcribing with OpenAI ${MODEL}..."

# load API key: env var takes priority, else fall back to ~/.config/openai/api_key
if [ -z "${OPENAI_API_KEY:-}" ]; then
  if [ -r "$HOME/.config/openai/api_key" ]; then
    OPENAI_API_KEY=$(tr -d '\n\r ' < "$HOME/.config/openai/api_key")
  else
    echo "[error] OPENAI_API_KEY not set and $HOME/.config/openai/api_key not readable" >&2
    exit 1
  fi
fi

# OpenAI's transcription endpoint has a 25MB upload limit per file.
# whisper-1 has no duration limit (so a 25MB/~85min meeting at 40kbps fits in one call).
AUDIO_BYTES=$(stat -c%s audio.mp3)
if [ "$AUDIO_BYTES" -gt 26214400 ]; then
  echo "[error] audio.mp3 is ${AUDIO_BYTES} bytes, exceeds OpenAI 25MB limit" >&2
  echo "[hint]  re-encode at lower bitrate or split the audio before retry" >&2
  exit 1
fi

HTTP_CODE=$(curl -sS https://api.openai.com/v1/audio/transcriptions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F file=@audio.mp3 \
  -F "model=${MODEL}" \
  -F language=zh \
  -F response_format=text \
  -o transcript.txt \
  -w '%{http_code}')

if [ "$HTTP_CODE" != "200" ]; then
  echo "[error] transcription failed (HTTP $HTTP_CODE). Response body:" >&2
  cat transcript.txt >&2
  exit 1
fi

WORDS=$(wc -m < transcript.txt | tr -d ' ')

echo ""
echo "[done] pipeline finished"
echo "  folder:   $OUTDIR"
echo "  duration: $DURATION"
echo "  chars:    $WORDS"
echo ""
echo "Next: Claude reads transcript.txt and writes summary.md in the same folder."
