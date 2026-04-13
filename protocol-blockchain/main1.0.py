import speech_recognition as sr
from cryptography.fernet import Fernet
from web3 import Web3
import json
from datetime import datetime
import time

W3_URL = "http://127.0.0.1:8545" 
CONTRACT_ADDRESS = Web3.to_checksum_address("0x5FbDB2315678afecb367f032d93F642f64180aa3")
ACCOUNT_ADDRESS = Web3.to_checksum_address("0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266")
ABI_PATH = "artifacts/contracts/ProtocolIntegrity.sol/ProtocolIntegrity.json"

def record_continuous_meeting():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    full_transcript = []
    print(f"\n--- Хурлын бүртгэл эхэллээ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
    print("--- Хурлын бүртгэл дуусгахын тулд 'Дуусгах' гэж хэлнэ үү. ---\n")

    with microphone as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)

        while True:
            try:
                print("Хурал үргэлжилж байна...")
              
                audio_data = recognizer.listen(source, phrase_time_limit=10)

                text = recognizer.recognize_google(audio_data, language="mn-MN")
                print(f">> {text}")

                if "дуусгах" in text.lower():
                    print("\nХурлын бүртгэл дууслаа.")
                    break
                if "Хурал дууслаа" in text.lower():
                    print("\nХурлын бүртгэл дууслаа.")
                    break
                if "Зогсох" in text.lower():
                    print("\nХурлын бүртгэл дууслаа.")
                    break
                if "Хурал өндөрлөлөө" in text.lower():
                    print("\nХурлын бүртгэл дууслаа.")
                    break
                full_transcript.append(text)

            except sr.UnknownValueError:
                continue
            except sr.RequestError:
                print("Интернэт холболтонд асуудал гарлаа.")
                break
            except Exception as e:
                print(f"Алдаа гарлаа: {e}")
                break

    return " ".join(full_transcript)

def secure_process(meeting_content):
    if not meeting_content:
        print("Бичлэг хоосон байна.")
        return None, None, None

    key = Fernet.generate_key()
    cipher = Fernet(key)
    encrypted_data = cipher.encrypt(meeting_content.encode())

    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"meeting_{timestamp_str}.bin"

    with open(filename, "wb") as f:
        f.write(encrypted_data)
    with open(f"key_{timestamp_str}.key", "wb") as k:
        k.write(key)

    meeting_id = int(time.time())
    w3 = Web3(Web3.HTTPProvider(W3_URL))
    
    try:
        with open(ABI_PATH) as f:
            abi = json.load(f)["abi"]
        
        contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)
        data_hash = w3.keccak(encrypted_data).hex() # Файлын агуулгын хэшийг тооцоолох SHA-3 ашиглана
        
        print(f"--> Блокчэйнд хадгалж байна. ID: {meeting_id}")
        tx_hash = contract.functions.storeHash(meeting_id, data_hash).transact({'from': ACCOUNT_ADDRESS})

        w3.eth.wait_for_transaction_receipt(tx_hash) # Блокчэйн дээрх гүйлгээний баталгаажуулалт хүлээх
        
        return data_hash, tx_hash.hex(), filename
    except Exception as e:
        print(f"Blockchain алдаа: {e}")
        return None, None, filename

if __name__ == "__main__":
   
    final_text = record_continuous_meeting()
    
    if final_text:
       
        b_hash, tx_id, fname = secure_process(final_text)
        
        if b_hash:
            print("\n" + "="*60)
            print(f"Бүрэн эх: {final_text}")
            print(f"Файл: {fname}")
            print(f"Blockchain Hash: {b_hash}")
            print(f"Transaction ID: {tx_id}")
            print("="*60)
    else:
        print("Бүртгэгдсэн текст олдсонгүй.")