import json
from web3 import Web3

# 1. Hardhat локал блокчэйнтэй холбогдох
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

# 2. ABI файлыг унших (Замаа зөв зааж өгөх)
with open("artifacts/contracts/ProtocolIntegrity.sol/ProtocolIntegrity.json") as f:
    info_json = json.load(f)
abi = info_json["abi"]

# 3. Contract-ийн хаяг (Deploy хийсний дараа энд хаягаа бичнэ)
# Одоогоор deploy хийгээгүй байгаа тул доорх алхмыг хийнэ.
contract_address = "0xf39fd6e51aad88f6f4ce6ab8827279cfffb92266" 

def store_to_blockchain(meeting_id, ipfs_hash):
    # Wallet хаяг (Hardhat node-оос нэгийг нь хуулж тавина)
    account = "0xf39fd6e51aad88f6f4ce6ab8827279cfffb92266" 
    
    contract = w3.eth.contract(address=contract_address, abi=abi)
    
    # Гүйлгээ хийх (Transaction)
    tx_hash = contract.functions.storeHash(meeting_id, ipfs_hash).transact({'from': account})
    
    # Баталгаажихыг хүлээх
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Амжилттай! Гүйлгээний Hash: {receipt.transactionHash.hex()}")

# Туршиж үзэх
# store_to_blockchain(1, "QmXoypizjW3WknFiJnKLwHCnL72vedxjQkDDP1mXWo6uco")