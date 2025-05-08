import requests
import json
import time
import dotenv
import os
from queryGraph import *
from web3 import Web3

dotenv.load_dotenv(override=True)
web3 = Web3(Web3.HTTPProvider(os.getenv("BERA_RPC_URL")))

# 读取配置文件
with open("config/config.json", "r") as f:
    config = json.load(f)

def get_active_reward_allocation(pubkey):

    # 获取合约地址和ABI
    contract_address = config["contract"]["address"]
    contract_abi = config["contract"]["abi"]
    

    # 创建合约实例
    contract = web3.eth.contract(address=contract_address, abi=contract_abi)
    
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


def get_validator_data(pubkey=None):

    if pubkey is None:
        pubkey = config["validator_info"]["pubkey"]

    # GraphQL 查询语句
    url = "https://api.berachain.com/"
    headers = {
        "Content-Type": "application/json"
    }

    query = query_all_validators
    all_validators = []
    page_size = 100
    skip = 0

    while True: 
        payload = {
                "operationName": "GetValidators",
                "variables": {
                "sortBy": "boostApr",
                "sortOrder": "desc",
                "chain": "BERACHAIN",
                "where": {},
                "skip": skip,
                "pageSize": page_size
            },
            "query": query
        }

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            print(f"❌ 请求失败，状态码：{response.status_code}")
            break

        data = response.json()
        validators = data["data"]["validators"]["validators"]
        total = data["data"]["validators"]["pagination"]["totalCount"]
        print(f"✅ 已获取第 {skip // page_size + 1} 页，共 {len(validators)} 条")

        all_validators.extend(validators)
        skip += page_size

        if skip >= total:
            break
        time.sleep(0.5)

    validators_by_pubkey = next((v for v in all_validators if v["pubkey"].lower() == pubkey.lower()), None)

    bgt_per_block = 0
    for valut in validators_by_pubkey["rewardAllocationWeights"]:
        bgt_per_block += float(valut["receivingVault"]["dynamicData"]["bgtCapturePerBlock"])
    
    validators_by_pubkey["bgtPerBlock"] = bgt_per_block
    validator_name = validators_by_pubkey["metadata"]["name"]
    with open("data/snz_validator_data.json", "w", encoding="utf-8") as f:
        json.dump(validators_by_pubkey, f, ensure_ascii=False, indent=2)
    print(f"✅ 已保存 {validator_name} 的 Validator 数据")

    return validators_by_pubkey

def get_all_vaults():

    # GraphQL 查询语句
    url = "https://api.berachain.com/"
    headers = {
        "Content-Type": "application/json"
    }

    query = query_all_vaults

    all_vaults = []
    page_size = 300
    skip = 0

    while True:
        payload = {
            "operationName": "GetVaults",
            "variables": {
                "orderBy": "activeIncentivesRateUsd",
                "orderDirection": "desc",
                "skip": skip,
                "pageSize": page_size,
                "where": {
                    "includeNonWhitelisted": False
                }
            },
            "query": query
        }

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            print(f"❌ 请求失败，状态码：{response.status_code}")
            break

        data = response.json()
        vaults = data["data"]["polGetRewardVaults"]["vaults"]
        total = data["data"]["polGetRewardVaults"]["pagination"]["totalCount"]

        print(f"✅ 已获取第 {skip // page_size + 1} 页，共 {len(vaults)} 条")

        all_vaults.extend(vaults)
        skip += page_size

        if skip >= total:
            break

        time.sleep(0.5)

    # 移除 activeIncentivesValueUsd 为 0 的 vault
    all_vaults = [vault for vault in all_vaults if float(vault['dynamicData']['activeIncentivesValueUsd']) > 0]
    
    total_incentives_rate = 0
    for vault in all_vaults:
        calculate_remaining_time(vault)
        total_incentives_rate += float(vault["dynamicData"]["activeIncentivesRateUsd"])
    avg_incentives_rate = total_incentives_rate / len(all_vaults)
    print(f"✅ 平均激励率: {avg_incentives_rate}")
    # 保存为 JSON 文件

    data = {
        "avgIncentivesRate": avg_incentives_rate,
        "vaults": all_vaults
    }
    with open("data/berachain_all_vaults.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ 共抓取 {len(all_vaults)} 条 Vault 数据，已保存为 berachain_all_vaults.json")

    return data
def calculate_remaining_time(vault):

    max_weight_per_vault = config["params"]["max_weight_per_vault"]
    with open("data/snz_validator_data.json", "r") as f:
        validator_data = json.load(f)
    snz_bgt_per_block = validator_data["bgtPerBlock"]

    bgt_capture_per_block = float(vault["dynamicData"]["bgtCapturePerBlock"])

    block_time = config["params"]["avg_block_time"]
    block_per_hour = 3600 / block_time

    if bgt_capture_per_block > 0:
        bgt_capture_per_hour = bgt_capture_per_block * block_per_hour
    else:
        bgt_capture_per_hour = snz_bgt_per_block * block_per_hour * max_weight_per_vault / 10000
        
    index = 0
    for incentive in vault["activeIncentives"]:
        incentive_rate = float(incentive["incentiveRate"])
        remaining_amount = float(incentive["remainingAmount"])
        if index == 0:
            remaining_hour = round(remaining_amount / (incentive_rate * bgt_capture_per_hour), 2)
        else:
            remaining_hour = min(remaining_hour, round(remaining_amount / (incentive_rate * bgt_capture_per_hour), 2))
        index += 1

 
    vault["dynamicData"]["remainingHours"] = remaining_hour
    print(f"✅ 已计算 {vault['metadata']['name']} 的剩余时间: {remaining_hour} 小时")
    
    return None



