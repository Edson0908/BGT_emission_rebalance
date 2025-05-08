import json
import dotenv
import os
from queryGraph import *
from web3 import Web3

dotenv.load_dotenv(override=True)
web3 = Web3(Web3.HTTPProvider(os.getenv("BERA_RPC_URL")))

# 读取配置文件
with open("config/config.json", "r") as f:
    config = json.load(f)
contract_address = web3.to_checksum_address(config["contract"]["address"])
contract_abi = config["contract"]["abi"]

# 创建合约实例
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

def get_current_block():
    return web3.eth.block_number

def get_active_reward_allocation(pubkey):
        
    # 调用合约函数
    try:
        result = contract.functions.getActiveRewardAllocation(pubkey).call()
        active_reward_allocation = {
            "startBlock": result[0],
            "weights": [
                {
                    "receiver": weight[0],
                    "percentageNumerator": weight[1]
                }
                for weight in result[1]
            ]
        }
        with open("data/active_reward_allocation.json", "w", encoding="utf-8") as f:
            json.dump(active_reward_allocation, f, ensure_ascii=False, indent=2)
        return active_reward_allocation
    except Exception as e:
        print(f"❌ 调用合约失败：{str(e)}")
        return None

def get_queued_reward_allocation(pubkey):
    # 调用合约函数
    try:
        result = contract.functions.getQueuedRewardAllocation(pubkey).call()
        print(result)
        queued_reward_allocation = {
            "startBlock": result[0],
            "weights": [
                {
                    "receiver": weight[0],
                    "percentageNumerator": weight[1]
                }
                for weight in result[1]
            ]
        }
        with open("data/queued_reward_allocation.json", "w", encoding="utf-8") as f:
            json.dump(queued_reward_allocation, f, ensure_ascii=False, indent=2)
        return queued_reward_allocation
    except Exception as e:
        print(f"❌ 调用合约失败：{str(e)}")
        return None

def queue_new_reward_allocation(pubkey, start_block, weights):
    # 调用合约函数
    try:
        # 获取私钥
        private_key = os.getenv("PRIVATE_KEY")
        if not private_key:
            raise ValueError("没有设置 PRIVATE_KEY 环境变量")
        
        # 获取发送者账户地址
        account = web3.eth.account.from_key(private_key)
        sender_address = web3.to_checksum_address(account.address)
        
        # 转换权重格式为合约需要的格式
        formatted_weights = [
            (web3.to_checksum_address(vault["id"]), vault["weights"]) 
            for vault in weights
        ]
        
        # 转换合约地址为checksum格式
        checksum_contract_address = web3.to_checksum_address(contract_address)
        
        # 构建交易
        tx = contract.functions.queueNewRewardAllocation(
            pubkey, 
            start_block, 
            formatted_weights
        ).build_transaction({
            'from': sender_address,
            'nonce': web3.eth.get_transaction_count(sender_address),
            'gas': 2000000,  # 设置适当的gas限制
            'gasPrice': web3.eth.gas_price
        })
        
        # 签名交易
        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
        
        # 发送交易
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        # 等待交易被确认
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"✅ 新的奖励分配已排队，交易哈希: {tx_hash.hex()}")
        
        # 保存交易信息
        tx_info = {
            "tx_hash": tx_hash.hex(),
            "start_block": start_block,
            "weights": [
                {
                    "receiver": web3.to_checksum_address(vault["id"]),
                    "percentageNumerator": vault["weights"],
                    "name": vault["name"]
                }
                for vault in weights
            ]
        }
        with open("data/queued_tx_info.json", "w", encoding="utf-8") as f:
            json.dump(tx_info, f, ensure_ascii=False, indent=2)
            
        return tx_hash
    except Exception as e:
        print(f"❌ 调用合约失败：{str(e)}")
        return None




