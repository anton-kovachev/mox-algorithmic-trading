from moccasin.config import get_active_network, ABIContract
import boa
from script._setup_script import _get_aave_pool_contract

BUFFER = 0.1


def rebalance(
    a_weth: ABIContract, a_usdc: ABIContract, weth: ABIContract, usdc: ABIContract
):
    print(f"Aave V3 aWETH Contract: {a_weth.address} {a_weth.name()}")
    print(f"Aave V3 aUSDC Contract: {a_usdc.address} {a_usdc.name()}")
    # %%
    a_usdc_balance = a_usdc.balanceOf(boa.env.eoa)
    print(f"aUSDC Balance: {a_usdc_balance}")
    a_weth_balance = a_weth.balanceOf(boa.env.eoa)
    print(f"aWETH Balance: {a_weth_balance}")

    # %%
    a_usdc_balance_normalized = a_usdc_balance // 1e6
    a_weth_balance_normalized = a_weth_balance // 1e18
    print(f"aUSDC Balance Normalized: {a_usdc_balance_normalized}")
    print(f"aWETH Balance Normalized: {a_weth_balance_normalized}")

    usdc_price = _get_price("usdc_usd")
    eth_proce = _get_price("eth_usd")
    print(f"USDC Price: {usdc_price}")
    print(f"ETH Price: {eth_proce}")

    # %%
    usdc_value = a_usdc_balance_normalized * usdc_price
    weth_value = a_weth_balance_normalized * eth_proce
    total_value = usdc_value + weth_value
    print(f"USDC Value: {usdc_value}")
    print(f"WETH Value: {weth_value}")

    target_usdc_percent_allocation = 0.3
    target_weth_percent_allocation = 0.7

    usdc_percent_allocation = usdc_value / total_value
    weth_percent_allocation = weth_value / total_value

    print(f"USDC Percent Allocation: {usdc_percent_allocation}")
    print(f"WETH Percent Allocation: {weth_percent_allocation}")

    needs_rebalancing = (
        abs(usdc_percent_allocation - target_usdc_percent_allocation) > BUFFER
        or abs(weth_percent_allocation - target_weth_percent_allocation) > BUFFER
    )
    print(f"Needs Rebalancing: {needs_rebalancing}")

    pool_contract = _get_aave_pool_contract()
    a_weth.approve(pool_contract.address, a_weth_balance)
    pool_contract.withdraw(weth.address, a_weth_balance, boa.env.eoa)

    _print_token_balances(usdc, weth, a_usdc, a_weth)
    # a_weth.approve(pool_contract.address, a_weth_balance)
    # pool_contract.withdraw(weth.address, a_weth_balance, boa.env.eoa)

    usdc_data = {
        "balance": a_usdc_balance_normalized,
        "price": usdc_price,
        "contract": a_usdc,
    }
    weth_data = {
        "balance": a_weth_balance_normalized,
        "price": eth_proce,
        "contract": a_weth,
    }
    target_allocations = {
        "usdc": target_usdc_percent_allocation,
        "weth": target_weth_percent_allocation,
    }

    print("Calculating rebalancing trades...")
    trades = _calculate_rebalancing_trades(usdc_data, weth_data, target_allocations)

    print(f"Trades: {trades}")
    active_network = get_active_network()
    uniswap_router = active_network.manifest_named("uniswap_swap_router")

    weth_to_sell = int(abs(trades["weth"]["trade"]) * 1e18)
    min_usdc_to_buy = abs(
        int(abs(trades["usdc"]["trade"]) * 1e6 * 0.95)
    )  # Slippage tolerance of 5%

    weth.approve(uniswap_router.address, weth_to_sell)

    uniswap_router.exactInputSingle(
        (
            weth.address,
            usdc.address,
            int(3000),
            boa.env.eoa,
            weth_to_sell,
            min_usdc_to_buy,
            0,
        )
    )

    print("After Swap:")
    _print_token_balances(usdc, weth, a_usdc, a_weth)

    weth_balance_after_swap = weth.balanceOf(boa.env.eoa)
    usdc_balance_after_swap = usdc.balanceOf(boa.env.eoa)

    if weth_balance_after_swap > 0:
        weth.approve(pool_contract.address, weth_balance_after_swap)
        pool_contract.supply(weth.address, weth_balance_after_swap, boa.env.eoa, 0)

    if usdc_balance_after_swap > 0:
        usdc.approve(pool_contract.address, usdc_balance_after_swap)
        pool_contract.supply(usdc.address, usdc_balance_after_swap, boa.env.eoa, 0)

    print("After Rebalance:")
    _print_token_balances(usdc, weth, a_usdc, a_weth)


def _calculate_rebalancing_trades(
    usdc_data: dict,  # {"balance": float, "price": float, "contract": Contract}
    weth_data: dict,  # {"balance": float, "price": float, "contract": Contract}
    target_allocations: dict[str, float],  # {"usdc": 0.3, "weth": 0.7}
) -> dict[str, dict]:
    """
    Calculate the trades needed to rebalance a portfolio of USDC and WETH.

    Args:
        usdc_data: Dict containing USDC balance, price and contract
        weth_data: Dict containing WETH balance, price and contract
        target_allocations: Dict of token symbol to target allocation (must sum to 1)

    Returns:
        Dict of token symbol to dict containing contract and trade amount:
            {"usdc": {"contract": Contract, "trade": int},
             "weth": {"contract": Contract, "trade": int}}
    """
    # Calculate current values
    usdc_value = usdc_data["balance"] * usdc_data["price"]
    weth_value = weth_data["balance"] * weth_data["price"]
    print(f"Current USDC Value: {usdc_value}")
    print(f"Current WETH Value: {weth_value}")
    total_value = usdc_value + weth_value

    # Calculate target values
    target_usdc_value = total_value * target_allocations["usdc"]
    target_weth_value = total_value * target_allocations["weth"]

    # Calculate trades needed in USD
    usdc_trade_usd = target_usdc_value - usdc_value
    weth_trade_usd = target_weth_value - weth_value

    # Convert to token amounts
    return {
        "usdc": {
            "contract": usdc_data["contract"],
            "trade": usdc_trade_usd / usdc_data["price"],
        },
        "weth": {
            "contract": weth_data["contract"],
            "trade": weth_trade_usd / weth_data["price"],
        },
    }


def _get_price(feed_name: str) -> float:
    active_network = get_active_network()
    price_feed = active_network.manifest_named(feed_name)
    price = price_feed.latestAnswer()
    decimals = price_feed.decimals()
    decimals_normalized = 10**decimals
    print(
        f"Price from feed {feed_name}: {price} with decimals {decimals} and decimals_normalized {decimals_normalized}"
    )
    return price / decimals_normalized


def _print_token_balances(
    usdc: ABIContract, weth: ABIContract, a_usdc: ABIContract, a_weth: ABIContract
):
    print(f"USDC Balance: {usdc.balanceOf(boa.env.eoa)}")
    print(f"WETH Balance: {weth.balanceOf(boa.env.eoa)}")
    print(f"aUSDC Balance: {a_usdc.balanceOf(boa.env.eoa)}")
    print(f"aWETH Balance: {a_weth.balanceOf(boa.env.eoa)}")


def moccasin_main():
    rebalance()
