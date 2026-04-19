from moccasin import setup_notebook
from moccasin.config import get_active_network, get_or_initialize_config, Network
from boa.contracts.abi.abi_contract import ABIContract
from typing import Tuple
from script._setup_script import setup_script
from script.deposit import deposit_into_aave
from script.rebalance import rebalance


def moccasin_main():
    a_usdc, a_weth, usdc, weth = setup_script()
    deposit_into_aave(usdc, weth)
    rebalance(a_weth, a_usdc, weth, usdc)
    return usdc, weth
