#Нууцлал тайлах verify.py code
from web3 import Web3
from cryptography.fernet import Fernet
import json
import os

W3_URL = "http://127.0.0.1:8545"
CONTRACT_ADDRESS = Web3.to_checksum_address("0x5FbDB2315678afecb367f032d93F642f64180aa3")
ABI_PATH = "artifacts/contracts/ProtocolIntegrity.sol/ProtocolIntegrity.json"

def verify_and_read_meeting(meeting_id, bin_file, key_file):
    
    w3 = Web3(Web3.HTTPProvider(W3_URL))

    try:
        with open(ABI_PATH) as f:
            abi = json.load(f)["abi"]
        contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)
        
        blockchain_hash = contract.functions.getHash(meeting_id).call()
    except Exception as e:
        print(f" Блокчэйнээс өгөгдөл уншихад алдаа гарлаа: {e}")
        return

    if not os.path.exists(bin_file):
        print(f"'{bin_file}' файл олдсонгүй!")
        return

    with open(bin_file, "rb") as f:
        content = f.read()
        local_hash = w3.keccak(content).hex()

    print("\n" + "-"*40)
    print(f"Блокчэйн дээрх Hash: {blockchain_hash}")
    print(f"Локал файлын Hash:   {local_hash}")
    
    if blockchain_hash == local_hash:
        print("\nБАТАЛГААЖЛАА: Файл өөрчлөгдөөгүй байна.")

        try:
            with open(key_file, "rb") as k:
                key = k.read()
            
            cipher = Fernet(key)
            decrypted_text = cipher.decrypt(content).decode()
            
            print("\n" + "="*40)
            print("ХУРЛЫН ТЭМДЭГЛЭЛ:")
            print(decrypted_text)
            print("="*40)
            return decrypted_text
        except Exception as e:
            print(f" Тайлахад алдаа гарлаа (Магадгүй буруу түлхүүр): {e}")
    else:
        print("\nАНХААРУУЛГА: Блокчэйн дээрх Hash-тай таарахгүй байна!")
        print("Өгөгдөл өөрчлөгдсөн эсвэл буруу файл байна.")

if __name__ == "__main__":
 
    ID = 1775566452
    BIN = "meeting_20260407_205412.bin" 
    KEY = "key_20260407_205412.key"    
    
    verify_and_read_meeting(ID, BIN, KEY)