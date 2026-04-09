# HW2 Audio Pipeline

A Python script that demonstrates a complete Text-to-Speech (TTS) and Speech-to-Text (STT) round-trip pipeline using OpenAI's `tts-1` and `whisper-1` models via the OpenAI API.

## Setup Instructions

### 1. Install dependencies
Requires Python 3.10+.
```bash
pip install -r requirements.txt
```

### 2. Set up your `.env` file
Copy the example and add your API key:
```bash
cp .env.example .env
# Edit .env and paste your OPENAI_API_KEY
```

Your `.env` file should contain:
```
OPENAI_API_KEY=sk-proj-...
```

### 3. Run the script
```bash
python hw2-audio-pipeline.py
```

Optionally, pass custom text:
```bash
python hw2-audio-pipeline.py "Your custom text here."
```

## Expected Output

```
=== HW2 Audio Pipeline ===

  Provider: OpenAI (tts-1 + whisper-1)

[1/4] Generating speech with voice: nova
  Text: "We are developing an ai company that can work simmiliarly to..."
  [2026-04-09 20:11:04] Model: tts-1 | Input: 75 chars | Latency: 4.33s
  Generated in 4.33s
  File: audio-output\voice_nova_sample.mp3 (90.0 KB)
  Cost: $0.0011

[2/4] Generating speech with voice: alloy
  Text: "We are developing an ai company that can work simmiliarly to..."
  [2026-04-09 20:11:08] Model: tts-1 | Input: 75 chars | Latency: 1.90s
  Generated in 1.90s
  File: audio-output\voice_alloy_sample.mp3 (86.7 KB)
  Cost: $0.0011

[3/4] Transcribing audio-output\voice_alloy_sample.mp3
  [2026-04-09 20:11:10] Model: whisper-1 | Duration: 4.4s | Latency: 1.40s
  Transcript: "We are developing an AI company that can work similarly to a..."
  Transcribed in 1.40s
  Audio duration: 4.4s
  Cost: $0.0004

[4/4] Comparing original vs transcribed text
  Original:    "We are developing an ai company that can work simmiliarly to a real company"     
  Transcribed: "We are developing an AI company that can work similarly to a real company."      
  Word overlap accuracy: 92.3%

=== Cost and Latency Summary ===
  TTS calls:  2 | Total cost: $0.0022 | Avg latency: 3.12s
  STT calls:  1 | Total cost: $0.0004 | Avg latency: 1.40s
  Pipeline total: $0.0027

=== Pipeline complete ===
```

## Generated Files

After running, the `audio-output/` directory will contain:
- `voice_nova_sample.mp3` — TTS output using the **nova** voice (~90 KB)
- `voice_alloy_sample.mp3` — TTS output using the **alloy** voice (~87 KB)
