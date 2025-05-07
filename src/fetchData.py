import requests
import json
import time
from config import url, headers, query

def fetch_all_vaults():


    all_vaults = []
    page_size = 300
    skip = 0

    while True:
        payload = {
            "operationName": "GetVaults",
            "variables": {
                "orderBy": "apr",
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

    # 保存为 JSON 文件
    with open("data/berachain_all_vaults.json", "w", encoding="utf-8") as f:
        json.dump(all_vaults, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 共抓取 {len(all_vaults)} 条 Vault 数据，已保存为 berachain_all_vaults.json")

# 执行
fetch_all_vaults()
