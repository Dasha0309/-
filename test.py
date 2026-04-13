import speech_recognition as sr

r = sr.Recognizer()
with sr.Microphone() as source:
    print("Ярьж эхэлнэ үү...")
    audio = r.listen(source)
    
    try:
        # Google-ийн таних системийг ашиглах (Монгол хэл дэмжинэ)
        text = r.recognize_google(audio, language="mn-MN")
        print("Таны хэлсэн зүйл: " + text)
    except:
        print("Уучлаарай, яриаг таньж чадсангүй.")