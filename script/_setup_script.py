from boa.contracts.abi.abi_contract import ABIContract
from typing import Tuple
from moccasin.config import get_active_network, Network
import boa

STARTING_ETH_BALANCE = int(1000e18)
STARTING_WETH_BALANCE = int(1e18)
STARTING_USDC_BALANCE = int(100e6)


def _add_eth_balance():
    boa.env.set_balance(boa.env.eoa, STARTING_ETH_BALANCE)


def _add_token_balance(usdc: ABIContract, weth: ABIContract, active_network: Network):
    print(f"STARTING WETH BALANCE: {weth.balanceOf(boa.env.eoa)}")
    weth.deposit(value=STARTING_WETH_BALANCE)  # type: ignore
    print(f"ENDING WETH BALANCE: {weth.balanceOf(boa.env.eoa)}")

    print(f"STARTING USDC BALANCE: {usdc.balanceOf(boa.env.eoa)}")
    current_addres = boa.env.eoa
    with boa.env.prank(usdc.owner()):  # type: ignore
        usdc.updateMasterMinter(current_addres)  # type: ignore

    usdc.configureMinter(current_addres, STARTING_USDC_BALANCE)  # type: ignore
    usdc.mint(current_addres, STARTING_USDC_BALANCE)  # type: ignore

    print(f"ENDING USDC BALANCE: {usdc.balanceOf(boa.env.eoa)}")


def _get_aave_pool_contract() -> ABIContract:
    active_network = get_active_network()
    aavev3_pool_address_provider = active_network.manifest_named(
        "aavev3_pool_address_provider"
    )
    pool_address = aavev3_pool_address_provider.getPool()
    print(f"Aave V3 Pool Address: {pool_address}")

    pool_contract = active_network.manifest_named("pool", address=pool_address)
    return pool_contract


def setup_script() -> Tuple[ABIContract, ABIContract, ABIContract, ABIContract]:
    print("Starting setup script")

    active_network = get_active_network()
    usdc = active_network.manifest_named("usdc")
    weth = active_network.manifest_named("weth")
    aave = active_network.manifest_named("aavev3_pool_address_provider")
    aavev3_protocol_data_provider = active_network.manifest_named(
        "aavev3_protocol_data_provider"
    )

    print(f"USDC Address: {usdc.address} {usdc.name()}")
    print(f"WETH Address: {weth.address} {weth.name()}")
    print(f"Aave V3 Pool Address: {aave.getPool()}")

    a_tokens = aavev3_protocol_data_provider.getAllATokens()
    for a_token in a_tokens:
        if "WETH" in a_token[0]:
            a_weth = active_network.manifest_named("weth", address=a_token[1])
        if "USDC" in a_token[0]:
            a_usdc = active_network.manifest_named("usdc", address=a_token[1])

    print(f"Aave V3 aWETH Address: {a_weth.address} {a_weth.name()}")
    print(f"Aave V3 aUSDC Address: {a_usdc.address} {a_usdc.name()}")

    if active_network.is_local_or_forked_network():
        # 1. Give ourselves some ETH
        _add_eth_balance()
        # 2. Give ourselves some USDC and WETH
        _add_token_balance(usdc, weth, active_network)
    return (a_usdc, a_weth, usdc, weth)


def moccasin_main():
    _, _, usdc, weth = setup_script()
    return usdc, weth
