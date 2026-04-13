import whisper
import speech_recognition as sr
import os
import warnings

# Анхааруулгыг нуух (FP16 гэх мэт)
warnings.filterwarnings("ignore")

# 1. Моделоо ачаалах ('small' нь Монгол хэлэнд 'base'-ээс илүү нарийвчлалтай)
print("Моделийг ачаалж байна (эхний удаад бага зэрэг удах болно)...")
model = whisper.load_model("small")

def transcribe_with_whisper():
    r = sr.Recognizer()
    
    # Микрофоны тохиргоог сайжруулах
    with sr.Microphone(sample_rate=16000) as source:
        print("\nОрчны чимээг тохируулж байна, битгий яриарай...")
        r.adjust_for_ambient_noise(source, duration=2)
        print("Одоо ярьж эхэлнэ үү (Монголоор)...")
        
        # Хэрэв таны яриа урт бол timeout болон phrase_time_limit-ийг ихэсгэ
        audio = r.listen(source, timeout=10, phrase_time_limit=30)

    # Аудиог файл руу хадгалах
    temp_filename = "temp_input.wav"
    with open(temp_filename, "wb") as f:
        f.write(audio.get_wav_data())

    # 2. Нарийвчлал сайжруулах тохиргоо (Гол нууц энд байна)
    print("Боловсруулж байна...")
    result = model.transcribe(
        temp_filename,
        language="mn",           # Хэлийг албадан заах
        fp16=False,              # CPU дээр ажиллахад алдаа гаргахгүй
        beam_size=5,             # Илүү сайн хайлт хийх (нарийвчлал өсгөнө)
        initial_prompt="Монгол хэл дээрх албан ёсны болон ярианы хэл." # Моделыг чиглүүлнэ
    )
    
    print("\n--- Хөрвүүлсэн текст ---")
    print(result["text"])
    
    # Файлыг устгах
    if os.path.exists(temp_filename):
        os.remove(temp_filename)

if __name__ == "__main__":
    try:
        transcribe_with_whisper()
    except Exception as e:
        print(f"Алдаа гарлаа: {e}")