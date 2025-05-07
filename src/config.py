
url = "https://api.berachain.com/"
headers = {
    "Content-Type": "application/json"
}

# GraphQL 查询语句
query = """
query GetVaults($where: GqlRewardVaultFilter, $pageSize: Int, $skip: Int, $orderBy: GqlRewardVaultOrderBy = bgtCapturePercentage, $orderDirection: GqlRewardVaultOrderDirection = desc, $search: String) {
polGetRewardVaults(
    where: $where
    first: $pageSize
    skip: $skip
    orderBy: $orderBy
    orderDirection: $orderDirection
    search: $search
) {
    pagination {
    currentPage
    totalCount
    }
    vaults {
    id: vaultAddress
    vaultAddress
    address: vaultAddress
    isVaultWhitelisted
    dynamicData {
        bgtCapturePercentage
        bgtCapturePerBlock
        activeIncentivesValueUsd
        activeIncentivesRateUsd
        tvl
    }
    metadata {
        name
        protocolName
    }
    activeIncentives {
        active
        remainingAmount
        remainingAmountUsd
        incentiveRate
        tokenAddress
        token {
        address
        name
        symbol
        decimals
        }
    }
    }
}
}
"""