from moccasin.config import get_active_network
from boa.contracts.abi.abi_contract import ABIContract
from script._setup_script import setup_script, _get_aave_pool_contract
import boa

STARTING_ETH_BALANCE = int(1000e18)
STARTING_WETH_BALANCE = int(1e18)
STARTING_USDC_BALANCE = int(100e6)
REFERAL_CODE = 0


def deposit_into_aave(usdc: ABIContract, weth: ABIContract):
    pool_contract = _get_aave_pool_contract()
    print(f"Aave V3 Pool Contract: {pool_contract.address}")

    usdc_balance = usdc.balanceOf(boa.env.eoa)
    weth_balance = weth.balanceOf(boa.env.eoa)
    print(f"USDC Balance: {usdc_balance}")
    print(f"WETH Balance: {weth_balance}")

    if usdc_balance > 0:
        _deposit(pool_contract, usdc, usdc_balance)

    if weth_balance > 0:
        _deposit(pool_contract, weth, weth_balance)

    (
        totalCollateralBase,
        totalDebtBase,
        availableBorrowsBase,
        currentLiquidationThreshold,
        ltv,
        healthFactor,
    ) = pool_contract.getUserAccountData(boa.env.eoa)

    print(f"Total Collateral Base: {totalCollateralBase}")
    print(f"Total Debt Base: {totalDebtBase}")
    print(f"Available Borrows Base: {availableBorrowsBase}")
    print(f"Current Liquidation Threshold: {currentLiquidationThreshold}")
    print(f"LTV: {ltv}")
    print(f"Health Factor: {healthFactor}")


def _deposit(pool_contract, token, amount):
    allowed_amount = token.allowance(boa.env.eoa, pool_contract.address)
    print(
        f"Allowed Amount: {allowed_amount} from {token.address} with balance {token.balanceOf(boa.env.eoa)}"
    )
    if allowed_amount < amount:
        token.approve(pool_contract.address, amount)
    allowed_amount = token.allowance(boa.env.eoa, pool_contract.address)
    print(
        f"Allowed Amount: {allowed_amount} from {token.address} with balance {token.balanceOf(boa.env.eoa)}"
    )
    print(
        f"Balance of {token.address} for {boa.env.eoa}: {token.balanceOf(boa.env.eoa)}"
    )
    print(
        f"Depositing {amount} of token {token.address} into Aave V3 Pool at address {pool_contract.address}"
    )

    pool_contract.supply(token.address, amount, boa.env.eoa, REFERAL_CODE)


def moccasin_main():
    _, _, usdc, weth = setup_script()
    deposit_into_aave(usdc, weth)
