import os
import sys
import time
import argparse
from dotenv import load_dotenv
from openai import OpenAI
from mutagen.mp3 import MP3
from mutagen.wave import WAVE

# ─── Cost constants (per rubric) ─────────────────────────────────────────────
TTS_COST_PER_1K_CHARS = 0.015
STT_COST_PER_MINUTE   = 0.006

# ─── Global accumulators ──────────────────────────────────────────────────────
tts_calls         = 0
tts_total_cost    = 0.0
tts_total_latency = 0.0
stt_calls         = 0
stt_total_cost    = 0.0
stt_total_latency = 0.0


def calculate_word_overlap(original: str, transcribed: str) -> float:
    """Calculates simple word overlap percentage between two strings."""
    def normalize(text):
        for punct in ['.', ',', '?', '!', '"', "'"]:
            text = text.replace(punct, '')
        return text.lower().split()

    orig_words  = set(normalize(original))
    trans_words = set(normalize(transcribed))
    if not orig_words:
        return 0.0
    return (len(orig_words & trans_words) / len(orig_words)) * 100.0


def get_audio_duration(file_path: str) -> float:
    """Returns audio duration in seconds using mutagen."""
    ext = os.path.splitext(file_path)[1].lower()
    try:
        data = MP3(file_path) if ext == '.mp3' else WAVE(file_path)
        return data.info.length
    except Exception:
        return 0.0


def call_tts_with_retry(client: OpenAI, text: str, voice: str, output_path: str, retries: int = 1):
    """Calls OpenAI TTS API with retry logic and per-call logging."""
    model = "tts-1"
    for attempt in range(retries + 1):
        try:
            timestamp  = time.strftime("%Y-%m-%d %H:%M:%S")
            start_time = time.time()

            response = client.audio.speech.create(model=model, voice=voice, input=text)
            with open(output_path, "wb") as f:
                f.write(response.content)

            latency = time.time() - start_time
            cost    = (len(text) / 1000) * TTS_COST_PER_1K_CHARS

            global tts_calls, tts_total_cost, tts_total_latency
            tts_calls         += 1
            tts_total_cost    += cost
            tts_total_latency += latency

            print(f"  [{timestamp}] Model: {model} | Input: {len(text)} chars | Latency: {latency:.2f}s")
            return latency, cost

        except Exception as e:
            if attempt < retries:
                print(f"  [Error] {time.strftime('%H:%M:%S')} - TTS failed ({e}). Retrying...")
                time.sleep(2)
            else:
                print(f"  [Error] TTS failed after {retries} retries: {e}")
                return None, 0.0


def call_stt_with_retry(client: OpenAI, file_path: str, retries: int = 1):
    """Calls OpenAI Whisper API with format/file checks and retry logic."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in ['.mp3', '.wav']:
        print(f"  [Error] Unsupported audio format: '{ext}'. Only MP3 and WAV are supported.")
        return None, 0.0, 0.0, 0.0

    if not os.path.exists(file_path):
        print(f"  [Error] File not found: {file_path}")
        return None, 0.0, 0.0, 0.0

    duration = get_audio_duration(file_path)
    model    = "whisper-1"

    for attempt in range(retries + 1):
        try:
            timestamp  = time.strftime("%Y-%m-%d %H:%M:%S")
            start_time = time.time()

            with open(file_path, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model=model,
                    file=audio_file,
                    response_format="text"
                )

            text    = str(transcript).strip()
            latency = time.time() - start_time
            cost    = (duration / 60) * STT_COST_PER_MINUTE

            global stt_calls, stt_total_cost, stt_total_latency
            stt_calls         += 1
            stt_total_cost    += cost
            stt_total_latency += latency

            print(f"  [{timestamp}] Model: {model} | Duration: {duration:.1f}s | Latency: {latency:.2f}s")
            return text, latency, duration, cost

        except Exception as e:
            if attempt < retries:
                print(f"  [Error] {time.strftime('%H:%M:%S')} - STT failed ({e}). Retrying...")
                time.sleep(2)
            else:
                print(f"  [Error] STT failed after {retries} retries: {e}")
                return None, 0.0, 0.0, 0.0


def main():
    parser = argparse.ArgumentParser(description="HW2 Audio Pipeline — TTS/STT Roundtrip via OpenAI")
    parser.add_argument(
        "text", nargs="?",
        default="Machine learning models learn patterns from data and use them to make predictions.",
        help="Text to process through the audio pipeline"
    )
    args       = parser.parse_args()
    text_input = args.text

    # ── Load API key ──────────────────────────────────────────────────────────
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[Error] OPENAI_API_KEY not found in .env file.")
        print("  Please add: OPENAI_API_KEY=sk-proj-...")
        sys.exit(1)

    client = OpenAI(api_key=api_key)  # uses api.openai.com by default

    out_dir = "audio-output"
    os.makedirs(out_dir, exist_ok=True)

    print("\n=== HW2 Audio Pipeline ===\n")
    print("  Provider: OpenAI (tts-1 + whisper-1)\n")

    voices         = ["nova", "alloy"]
    last_file_path = None

    # ── Steps 1 & 2: TTS for both voices ─────────────────────────────────────
    for i, voice in enumerate(voices, 1):
        print(f"[{i}/4] Generating speech with voice: {voice}")
        output_file    = os.path.join(out_dir, f"voice_{voice}_sample.mp3")
        last_file_path = output_file

        print(f"  Text: \"{text_input[:60]}{'...' if len(text_input) > 60 else ''}\"")
        latency, cost = call_tts_with_retry(client, text_input, voice, output_file)

        if latency is not None:
            file_size_kb = os.path.getsize(output_file) / 1024
            print(f"  Generated in {latency:.2f}s")
            print(f"  File: {output_file} ({file_size_kb:.1f} KB)")
            print(f"  Cost: ${cost:.4f}\n")
        else:
            print(f"  [Skip] TTS failed for voice '{voice}'.\n")

    # ── Step 3: STT ───────────────────────────────────────────────────────────
    print(f"[3/4] Transcribing {last_file_path}")
    transcript_text, stt_latency, duration, stt_cost = call_stt_with_retry(client, last_file_path)

    if transcript_text:
        print(f"  Transcript: \"{transcript_text[:60]}{'...' if len(transcript_text) > 60 else ''}\"")
        print(f"  Transcribed in {stt_latency:.2f}s")
        print(f"  Audio duration: {duration:.1f}s")
        print(f"  Cost: ${stt_cost:.4f}\n")
    else:
        print(f"  [Error] Transcription failed or was skipped.\n")
        transcript_text = ""

    # ── Step 4: Compare ───────────────────────────────────────────────────────
    print(f"[4/4] Comparing original vs transcribed text")
    print(f"  Original:    \"{text_input}\"")
    print(f"  Transcribed: \"{transcript_text}\"")
    accuracy = calculate_word_overlap(text_input, transcript_text)
    print(f"  Word overlap accuracy: {accuracy:.1f}%\n")

    # ── Summary ───────────────────────────────────────────────────────────────
    print("=== Cost and Latency Summary ===")
    avg_tts = (tts_total_latency / tts_calls) if tts_calls > 0 else 0
    avg_stt = (stt_total_latency / stt_calls) if stt_calls > 0 else 0
    total   = tts_total_cost + stt_total_cost
    print(f"  TTS calls:  {tts_calls} | Total cost: ${tts_total_cost:.4f} | Avg latency: {avg_tts:.2f}s")
    print(f"  STT calls:  {stt_calls} | Total cost: ${stt_total_cost:.4f} | Avg latency: {avg_stt:.2f}s")
    print(f"  Pipeline total: ${total:.4f}\n")
    print("=== Pipeline complete ===")


if __name__ == "__main__":
    main()
