"""
Хурлын Бүртгэлийн Систем
=========================
- Microsoft Azure Speech SDK (mn-MN)
- Batch Processing: бүх аудиог нэг дор бичиж дараа нь боловсруулна
- Speaker Diarization: яригч бүрийг тусад нь ялгана
- Монгол текст засвар: алдаатай үгийг зөв болгоно
- Гадаад нэр томьёог англиар хэвээр үлдээнэ
- Нууцлал (Fernet) + Blockchain (Web3) бүртгэл хэвээр
"""

import os
import re
import json
import wave
import time
import queue
import threading
import pyaudio
from datetime import datetime
from cryptography.fernet import Fernet
from web3 import Web3
import azure.cognitiveservices.speech as speechsdk
from dictionary import MONGOLIAN_CORRECTIONS, TECHNICAL_MN_TO_EN

# ============================================================
# ТОХИРГОО — орчны хувьсагчаар тохируулна
# ============================================================
AZURE_SPEECH_KEY    = os.environ.get("AZURE_SPEECH_KEY",    "YOUR_AZURE_SPEECH_KEY")
AZURE_SPEECH_REGION = os.environ.get("AZURE_SPEECH_REGION", "eastasia")

W3_URL            = "http://127.0.0.1:8545"
CONTRACT_ADDRESS  = Web3.to_checksum_address("0x5FbDB2315678afecb367f032d93F642f64180aa3")
ACCOUNT_ADDRESS   = Web3.to_checksum_address("0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266")
ABI_PATH          = "artifacts/contracts/ProtocolIntegrity.sol/ProtocolIntegrity.json"

# Аудио тохиргоо
AUDIO_FORMAT  = pyaudio.paInt16
CHANNELS      = 1
RATE          = 16000   # Azure mn-MN-д зөвшөөрөгдсөн
CHUNK         = 1024

# Зогсоох түлхүүр үгс (жижиг үсгээр шалгана)
STOP_KEYWORDS = [
    "дуусгах",
    "хурал дууслаа",
    "хурал өндөрлөлөө",
    "өндөрлөлөө",
    "зогсох",
]

def _apply_replacements(text: str, rules: dict[str, str]) -> str:
    """Regex орлуулалтуудыг дарааллаар хэрэглэх"""
    for pattern, replacement in rules.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


def correct_mongolian_text(text: str) -> str:
    """
    Монгол текст засварлах:
      1. Гадаад нэр томьёог англиар солих
      2. Нийтлэг дуудлагын алдааг засах
      3. Өгүүлбэрийн эхний үсгийг том болгох
      4. Олон зай, таслалын алдааг цэгцлэх
    """
    text = _apply_replacements(text, TECHNICAL_MN_TO_EN)
    text = _apply_replacements(text, MONGOLIAN_CORRECTIONS)

    # Олон зайг нэг болгох
    text = re.sub(r" {2,}", " ", text)

    # Өгүүлбэр бүрийн эхний үсгийг том болгох
    sentences = re.split(r"(?<=[.!?])\s+", text)
    sentences = [s.strip().capitalize() for s in sentences if s.strip()]
    text = " ".join(sentences)

    return text.strip()


def format_transcript(segments: list[dict]) -> str:
    """
    Яригч ялгасан хэлбэрт оруулах:
      [Яригч 1]: ... текст ...
      [Яригч 2]: ... текст ...
    Ижил яригчийн дараалсан мөрүүдийг нэгтгэнэ.
    """
    if not segments:
        return ""

    lines: list[str] = []
    current_speaker: str | None = None
    buffer: list[str] = []

    def flush():
        if buffer and current_speaker:
            combined = correct_mongolian_text(" ".join(buffer))
            lines.append(f"[{current_speaker}]: {combined}")

    for seg in segments:
        speaker = seg.get("speaker") or "Яригч"
        raw_text = seg.get("text", "").strip()
        if not raw_text:
            continue
        if speaker != current_speaker:
            flush()
            current_speaker = speaker
            buffer = [raw_text]
        else:
            buffer.append(raw_text)

    flush()
    return "\n".join(lines)


# ============================================================
# АУДИО БИЧЛЭГ — BATCH (нэг дор бичиж, дараа нь боловсруулна)
# ============================================================

import threading
import wave
import os
import pyaudio
import azure.cognitiveservices.speech as speechsdk
from datetime import datetime

# Эдгээр тогтмол утгууд тодорхойлогдсон байх шаардлагатай
# AUDIO_FORMAT = pyaudio.paInt16
# STOP_KEYWORDS = ["дуусгах", "хурал дууслаа", "өндөрлөлөө"]

def record_audio_to_file(output_wav: str) -> bool:
    """
    Микрофоноос аудио бичиж WAV файлд хадгалана.
    Enter дарах эсвэл түлхүүр үг хэлэх → бичлэг зогсоно.
    Дараа нь batch processing үргэлжилнэ.
    """
    stop_event = threading.Event()
    audio_frames: list[bytes] = []

    # ── Real-time зогсоох үг + Enter хянагч ─────────────────
    def _start_realtime_watcher(push_stream: speechsdk.audio.PushAudioInputStream):
        config = speechsdk.SpeechConfig(
            subscription=AZURE_SPEECH_KEY,
            region=AZURE_SPEECH_REGION,
        )
        config.speech_recognition_language = "mn-MN"
        audio_cfg = speechsdk.audio.AudioConfig(stream=push_stream)
        recognizer = speechsdk.SpeechRecognizer(
            speech_config=config,
            audio_config=audio_cfg,
        )

        def _enter_watcher():
            print(">>> БИЧЛЭГИЙГ ЗОГСООХЫН ТУЛД 'ENTER' ДАРНА УУ...\n")
            try:
                input()
            except Exception:
                pass
            if not stop_event.is_set():
                print("\n  [ Enter → бичлэг зогсоно, боловсруулалт үргэлжилнэ... ]")
                stop_event.set()

        threading.Thread(target=_enter_watcher, daemon=True).start()

        def on_recognized(evt: speechsdk.SpeechRecognitionEventArgs):
            if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
                text = evt.result.text.strip().lower()
                if not text:
                    return
                print(f"  >> {text}")
                if any(kw in text for kw in STOP_KEYWORDS):
                    print("\n  [ Түлхүүр үг → бичлэг зогсоно, боловсруулалт үргэлжилнэ... ]")
                    stop_event.set()

        recognizer.recognized.connect(on_recognized)
        recognizer.start_continuous_recognition()
        return recognizer

    # ── PyAudio тохиргоо ─────────────────────────────────────
    pa = pyaudio.PyAudio()
    sample_width = pa.get_sample_size(AUDIO_FORMAT)
    mic_stream = None
    push_stream = None
    recognizer = None

    try:
        mic_stream = pa.open(
            format=AUDIO_FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )
        push_stream = speechsdk.audio.PushAudioInputStream(
            stream_format=speechsdk.audio.AudioStreamFormat(
                samples_per_second=RATE,
                bits_per_sample=16,
                channels=CHANNELS,
            )
        )
        recognizer = _start_realtime_watcher(push_stream)

        print(f"\n{'='*60}")
        print(f"  Хурлын бүртгэл эхэллээ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Зогсоох үгс: {', '.join(STOP_KEYWORDS)}")
        print(f"{'='*60}\n")

        # ── Бичлэгийн үндсэн давталт ─────────────────────────
        while not stop_event.is_set():
            data = mic_stream.read(CHUNK, exception_on_overflow=False)
            audio_frames.append(data)
            push_stream.write(data)

    except Exception as exc:
        print(f"  Бичлэгийн явцад алдаа: {exc}")
        return False

    finally:
        # ── ЗӨВ ДАРААЛАЛ: recognizer → push_stream → mic_stream → pa ──
        print("\n  [ Нөөцүүд хаагдаж байна... ]")

        if recognizer is not None:
            try:
                # async + get() → хэвтэхгүй, хугацааны хязгаартай
                recognizer.stop_continuous_recognition_async().get()
            except Exception as e:
                print(f"  Recognizer хаах алдаа (үргэлжилнэ): {e}")

        if push_stream is not None:
            try:
                push_stream.close()
            except Exception as e:
                print(f"  PushStream хаах алдаа (үргэлжилнэ): {e}")

        if mic_stream is not None:
            try:
                mic_stream.stop_stream()
                mic_stream.close()
            except Exception as e:
                print(f"  MicStream хаах алдаа (үргэлжилнэ): {e}")

        try:
            pa.terminate()
        except Exception as e:
            print(f"  PyAudio terminate алдаа (үргэлжилнэ): {e}")

    # ── finally-н ГАДНА: WAV хадгалах ───────────────────────
    # (finally дотор return хийхгүй — алдаа дарагдах тул)
    if not audio_frames:
        print("  Аудио өгөгдөл бичигдсэнгүй.")
        return False

    try:
        with wave.open(output_wav, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(sample_width)
            wf.setframerate(RATE)
            wf.writeframes(b"".join(audio_frames))

        size_mb = os.path.getsize(output_wav) / (1024 * 1024)
        duration_s = len(audio_frames) * CHUNK / RATE
        print(f"\n  Аудио файл хадгалагдлаа: {output_wav}")
        print(f"  Хэмжээ: {size_mb:.2f} MB | Үргэлжлэх хугацаа: {duration_s:.1f}с")
        print(f"\n  >>> Batch transcription + Blockchain үргэлжилж байна...\n")
        return True

    except Exception as e:
        print(f"  WAV хадгалах алдаа: {e}")
        return False
    

# ============================================================
# AZURE BATCH TRANSCRIPTION + SPEAKER DIARIZATION
# ============================================================

def transcribe_with_diarization(audio_wav: str) -> list[dict]:
    """
    Бичигдсэн WAV файлыг Azure ConversationTranscriber-р
    batch боловсруулалт хийж яригч бүрийг ялгана.

    Returns:
        [{"speaker": "...", "text": "...", "offset": int}, ...]
    """
    config = speechsdk.SpeechConfig(
        subscription=AZURE_SPEECH_KEY,
        region=AZURE_SPEECH_REGION,
    )
    config.speech_recognition_language = "mn-MN"

    # Аудио логийг Azure-д илгээхгүй (нууцлал)
    config.set_property(
        speechsdk.PropertyId.SpeechServiceConnection_EnableAudioLogging,
        "false",
    )

    audio_cfg = speechsdk.audio.AudioConfig(filename=audio_wav)
    transcriber = speechsdk.transcription.ConversationTranscriber(
        speech_config=config,
        audio_config=audio_cfg,
    )

    segments: list[dict] = []
    done = threading.Event()

    def on_transcribed(evt: speechsdk.transcription.ConversationTranscriptionEventArgs):
        result = evt.result
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            speaker = result.speaker_id or "Яригч"
            text = result.text.strip()
            if text:
                print(f"    [{speaker}]: {text}")
                segments.append({
                    "speaker": speaker,
                    "text":    text,
                    "offset":  result.offset,
                })

    def on_canceled(evt):
        details = speechsdk.CancellationDetails.from_result(evt.result)
        print(f"\n  Цуцлагдлаа: {details.reason}")
        if details.reason == speechsdk.CancellationReason.Error:
            print(f"  Алдааны дэлгэрэнгүй: {details.error_details}")
        done.set()

    def on_session_stopped(_evt):
        done.set()

    transcriber.transcribed.connect(on_transcribed)
    transcriber.canceled.connect(on_canceled)
    transcriber.session_stopped.connect(on_session_stopped)

    print("\n  Batch Transcription + Speaker Diarization эхэлж байна...\n")
    transcriber.start_transcribing_async()

    # Аудионы уртаас хамааран хүлээнэ (хамгийн ихдээ 60 мин)
    done.wait(timeout=3600)
    transcriber.stop_transcribing_async()

    # Цаг эрэмбэлэх
    segments.sort(key=lambda x: x.get("offset", 0))
    return segments


# ============================================================
# НУУЦЛАЛ БА BLOCKCHAIN — ҮНДСЭН АГУУЛГА ХЭВЭЭР
# ============================================================

def secure_process(meeting_content: str):
    """
    Хурлын контентыг шифрлэж .bin файлд хадгалж,
    SHA-3 хэшийг blockchain-д бүртгэнэ.
    
    Returns:
        (data_hash, tx_hash_hex, enc_filename, key_filename, meeting_id)
    """
    if not meeting_content:
        print("Бичлэг хоосон байна.")
        return None, None, None, None, None          

    key = Fernet.generate_key()
    cipher = Fernet(key)
    encrypted_data = cipher.encrypt(meeting_content.encode())

    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    enc_filename = f"meeting_{timestamp_str}.bin"
    key_filename = f"key_{timestamp_str}.key"       

    with open(enc_filename, "wb") as f:
        f.write(encrypted_data)
    with open(key_filename, "wb") as k:
        k.write(key)

    meeting_id = int(time.time())                  
    w3 = Web3(Web3.HTTPProvider(W3_URL))

    try:
        with open(ABI_PATH) as f:
            abi = json.load(f)["abi"]

        contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)
        data_hash = w3.keccak(encrypted_data).hex()

        print(f"\n  --> Blockchain-д хадгалж байна. Meeting ID: {meeting_id}")
        tx_hash = contract.functions.storeHash(meeting_id, data_hash).transact(
            {"from": ACCOUNT_ADDRESS}
        )
        w3.eth.wait_for_transaction_receipt(tx_hash)

        return data_hash, tx_hash.hex(), enc_filename, key_filename, meeting_id  

    except Exception as exc:
        print(f"  Blockchain алдаа: {exc}")
        return None, None, enc_filename, key_filename, meeting_id               

# ============================================================
# ҮНДСЭН ПРОГРАМ
# ============================================================

if __name__ == "__main__":
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    audio_file = f"audio_{ts}.wav"

    # ── 1. Batch аудио бичлэг ────────────────────────────────
    if not record_audio_to_file(audio_file):
        print("Аудио бичлэг амжилтгүй боллоо.")
        raise SystemExit(1)

    # ── 2. Azure Batch Transcription + Diarization ────────────
    segments = transcribe_with_diarization(audio_file)

    if not segments:
        print("Транскрипц хоосон буцлаа — шалгана уу.")
        raise SystemExit(1)

    # ── 3. Яригч ялгасан эцсийн текст ────────────────────────
    formatted_transcript = format_transcript(segments)

    print(f"\n{'='*60}")
    print("  ХУРЛЫН ТЭМДЭГЛЭЛ (яригчаар ялгасан):")
    print(f"{'='*60}")
    print(formatted_transcript)
    print(f"{'='*60}\n")

    # ── 4. Нууцлал + Blockchain ──────────────────────────────
    b_hash, tx_id, enc_file, key_file, mtg_id = secure_process(formatted_transcript)  # ← 5 утга

    if b_hash:
        print(f"\n{'='*60}")
        print(f"  Шифрлэгдсэн файл : {enc_file}")
        print(f"  Түлхүүр файл     : {key_file}")
        print(f"  Blockchain Hash  : {b_hash}")
        print(f"  Transaction ID   : {tx_id}")
        print(f"{'='*60}")

    # ── 5. verify.py-д хэрэглэх мэдээлэл ─────────────────────
    if mtg_id and enc_file and key_file:
        print(f"\n{'='*60}")
        print("  VERIFY.PY-Д ХЭРЭГЛЭХ МЭДЭЭЛЭЛ:")
        print(f"{'='*60}")
        print(f"  ID  = {mtg_id}")
        print(f"  BIN = \"{enc_file}\"")
        print(f"  KEY = \"{key_file}\"")
        print(f"\n  Ажиллуулах команд:")
        print(f"  python verify.py")
        print(f"  (эсвэл verify.py дотор дараах утгуудыг тохируулна уу)")
        print(f"{'='*60}")

    # ── 6. Түр аудио файлыг устгах ───────────────────────────
    if os.path.exists(audio_file):
        os.remove(audio_file)
        print(f"\n  Түр аудио файл устгагдлаа: {audio_file}")