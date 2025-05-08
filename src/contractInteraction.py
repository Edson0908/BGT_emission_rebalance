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
contract_address = config["contract"]["address"]
contract_abi = config["contract"]["abi"]

# 创建合约实例
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

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

