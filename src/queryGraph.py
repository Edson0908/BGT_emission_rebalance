query_all_validators = """
    query GetValidators($where: GqlValidatorFilter, $sortBy: GqlValidatorOrderBy = lastDayDistributedBGTAmount, $sortOrder: GqlValidatorOrderDirection = desc, $pageSize: Int, $skip: Int, $search: String, $chain: GqlChain) {
    validators: polGetValidators(
        where: $where
        orderBy: $sortBy
        orderDirection: $sortOrder
        first: $pageSize
        skip: $skip
        search: $search
        chain: $chain
    ) {
        pagination {
        currentPage
        totalCount
        totalPages
        pageSize
        }
        validators {
        ...ApiValidator
        }
    }
    }

    fragment ApiValidator on GqlValidator {
    ...ApiValidatorMinimal
    operator
    rewardAllocationWeights {
        ...ApiRewardAllocationWeight
    }
    lastBlockUptime {
        isActive
    }
    metadata {
        name
        logoURI
        website
        description
    }
    }

    fragment ApiValidatorMinimal on GqlValidator {
    id
    pubkey
    operator
    metadata {
        name
        logoURI
    }
    dynamicData {
        activeBoostAmount
        usersActiveBoostCount
        queuedBoostAmount
        usersQueuedBoostCount
        allTimeDistributedBGTAmount
        rewardRate
        stakedBeraAmount
        lastDayDistributedBGTAmount
        activeBoostAmountRank
        boostApr
        commissionOnIncentives
    }
    }

    fragment ApiRewardAllocationWeight on GqlValidatorRewardAllocationWeight {
    percentageNumerator
    validatorId
    receivingVault {
        ...ApiVault
    }
    receiver
    startBlock
    }

    fragment ApiVault on GqlRewardVault {
    id: vaultAddress
    vaultAddress
    address: vaultAddress
    isVaultWhitelisted
    dynamicData {
        allTimeReceivedBGTAmount
        apr
        bgtCapturePercentage
        bgtCapturePerBlock
        activeIncentivesValueUsd
        activeIncentivesRateUsd
        tvl
    }
    stakingToken {
        address
        name
        symbol
        decimals
    }
    metadata {
        name
        logoURI
        url
        protocolName
        description
    }
    activeIncentives {
        ...ApiVaultIncentive
    }
    }

    fragment ApiVaultIncentive on GqlRewardVaultIncentive {
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
    """



query_all_vaults = """
    query GetVaults($where: GqlRewardVaultFilter, $pageSize: Int, $skip: Int, $orderBy: GqlRewardVaultOrderBy = activeIncentivesRateUsd, $orderDirection: GqlRewardVaultOrderDirection = desc, $search: String) {
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