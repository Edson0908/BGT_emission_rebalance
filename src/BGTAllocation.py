import fetchData
import json
import contractInteraction

# 读取配置文件
with open("config/config.json", "r") as f:
    config = json.load(f)

def select_vaults(all_vaults_data):

    min_remaining_hours = config["params"]["min_remaining_hours"]
    vaults_allocation = config["params"]["vaults_allocation"]

    all_vaults = all_vaults_data["vaults"]
    avg_incentives_rate = all_vaults_data["avgIncentivesRate"]
    # 读取白名单
    whitelisted_vaults = config["whitelisted_vaults"]
    selected_vaults = []
    for vault in whitelisted_vaults:
        vault_id = vault["id"]
        for item in all_vaults:
            if item["id"] == vault_id:
                vault["incentivesRate"] = item["dynamicData"]["activeIncentivesRateUsd"]
                vault["remainingHours"] = item["dynamicData"]["remainingHours"]
                break

        if float(vault.get("incentivesRate", 0)) > avg_incentives_rate and float(vault.get("remainingHours", 0)) > min_remaining_hours:
            selected_vaults.append(vault)

    if len(selected_vaults) < len(vaults_allocation):
        for vault in all_vaults:
            if float(vault["dynamicData"]["remainingHours"]) > min_remaining_hours:
                selected_vaults.append({"id": vault["id"], "name": vault["metadata"]["name"], "incentivesRate": vault["dynamicData"]["activeIncentivesRateUsd"], "remainingHours": vault["dynamicData"]["remainingHours"]})
                if len(selected_vaults) == len(vaults_allocation):
                    break

    selected_vaults = sorted(selected_vaults, key=lambda x: float(x["incentivesRate"]), reverse=True)  
    selected_vaults = selected_vaults[:len(vaults_allocation)]
    return selected_vaults
                

def main():
    
    # 获取SNZ Validator 数据
    validator_data = fetchData.get_validator_data()
    # 获取所有Vault 数据
    all_vaults_data = fetchData.get_all_vaults()

    selected_vaults = select_vaults(all_vaults_data) 
    index = 0
    for vault in selected_vaults:
        vault["weights"] = config["params"]["vaults_allocation"][index]
        index += 1
    print(json.dumps(selected_vaults, indent=4))
    
    # 获取当前区块
    current_block = contractInteraction.get_current_block()
    print(f"当前区块: {current_block}")
    # 计算开始区块
    start_block = current_block + config["params"]["delay_blocks"] + 10
    # 获取验证者公钥
    pubkey = config["validator_info"]["pubkey"]
    
    # 调用合约函数排队新的奖励分配
    print(f"当前区块: {current_block}, 开始区块: {start_block}")
    print(f"正在排队新的BGT分配...")
    tx_hash = contractInteraction.queue_new_reward_allocation(pubkey, start_block, selected_vaults)
    
    if tx_hash:
        print(f"BGT分配成功排队，将在区块 {start_block} 开始生效")
    else:
        print("BGT分配排队失败")



if __name__ == "__main__":
    main()
