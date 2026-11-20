#!/usr/bin/env bash
# Mux the rendered scene with narration + music bed.
#   voice: loudness-normalised to -16 LUFS (YouTube's target)
#   music: quiet bed, auto-ducked under the voice (sidechain), fades in/out
set -euo pipefail
cd "$(dirname "$0")"
VIDEO=${1:-../../media/videos/birthday_paradox/1080p60/BirthdayParadox.mp4}
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$VIDEO")
FADE_START=$(python3 -c "print(max(0, $DUR - 2.5))")
ffmpeg -y -loglevel error -i "$VIDEO" -i voice.mp3 -i music.mp3 -filter_complex "
  [1:a]loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000,apad=whole_dur=$DUR,asplit=2[v][vsc];
  [2:a]atrim=0:$DUR,volume=0.22,afade=t=in:d=1.5,afade=t=out:st=$FADE_START:d=2.5,aresample=48000[m];
  [m][vsc]sidechaincompress=threshold=0.03:ratio=6:attack=30:release=400[mduck];
  [v][mduck]amix=inputs=2:duration=longest:normalize=0,atrim=0:$DUR[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -shortest birthday_paradox_final.mp4
echo "wrote $(pwd)/birthday_paradox_final.mp4"
