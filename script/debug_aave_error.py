"""Debug script to identify the exact Aave V3 supply() revert reason."""

import boa
from moccasin.config import get_active_network


def main():
    # Set up the forked network
    network = get_active_network()

    # Contract addresses from the error trace
    pool_address = "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2"
    weth_address = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    pool_data_provider_address = "0x497a1994c46d4f6C864904A9f1fac6328Cb7C8a6"

    # Load contracts
    pool = network.manifest_named("pool", address=pool_address)
    weth = network.manifest_named("weth", address=weth_address)
    data_provider = network.manifest_named(
        "aavev3_protocol_data_provider", address=pool_data_provider_address
    )

    # Get WETH reserve data to check if it's properly configured
    print("Checking WETH reserve configuration...")
    try:
        reserve_data = pool.getReserveData(weth_address)
        print(f"✓ Reserve data retrieved")
        print(f"  aToken: {reserve_data[10]}")
        print(f"  Variable Debt Token: {reserve_data[12]}")
        print(f"  Liquidity Index: {reserve_data[1]}")
        print(f"  Variable Borrow Index: {reserve_data[3]}")
    except Exception as e:
        print(f"✗ Failed to get reserve data: {e}")
        return

    # Check if the variable debt token is properly initialized
    variable_debt_token_address = reserve_data[12]
    print(f"\nChecking Variable Debt Token at {variable_debt_token_address}...")

    try:
        # Try to get the implementation of the variable debt token
        variable_debt_token = network.manifest_named(
            "pool", address=variable_debt_token_address
        )

        # Try calling scaledTotalSupply directly
        print("Attempting to call scaledTotalSupply()...")
        scaled_supply = boa.env.raw_call(
            to=variable_debt_token_address,
            data=bytes.fromhex("b1bf962d"),  # scaledTotalSupply()
        )
        print(f"✓ scaledTotalSupply() returned: {int.from_bytes(scaled_supply, 'big')}")
    except Exception as e:
        print(f"✗ scaledTotalSupply() failed: {e}")
        print("\nThis is the root cause of the supply() revert!")

    # Mint some WETH and approve
    print("\nMinting and approving WETH...")
    weth.deposit(value=int(1e18))
    weth.approve(pool_address, int(1e18))
    print(f"WETH balance: {weth.balanceOf(boa.env.eoa)}")
    print(f"WETH allowance: {weth.allowance(boa.env.eoa, pool_address)}")

    # Try to supply with verbose error capture
    print("\nAttempting pool.supply()...")
    try:
        # Enable tracing
        with boa.env.anchor():
            pool.supply(weth_address, int(1e18), boa.env.eoa, 0)
        print("✓ Supply succeeded!")
    except Exception as e:
        print(f"✗ Supply failed: {type(e).__name__}")
        print(f"Error: {str(e)[:500]}")

        # Try to extract revert reason
        if hasattr(e, "__cause__") and hasattr(e.__cause__, "args"):
            print(f"\nCause: {e.__cause__}")

        # Check if it's a specific Aave error
        error_msg = str(e)
        if "CALLER_NOT_POOL_ADMIN" in error_msg:
            print("\n⚠️  Error: CALLER_NOT_POOL_ADMIN")
            print("The pool configuration might need admin access.")
        elif "RESERVE_INACTIVE" in error_msg:
            print("\n⚠️  Error: RESERVE_INACTIVE")
            print("The WETH reserve is not active on this fork.")
        elif "scaledTotalSupply" in error_msg:
            print("\n⚠️  The Variable Debt Token's scaledTotalSupply() is reverting.")
            print(
                "This suggests the token proxy is not properly initialized on the fork."
            )
            print("\nPossible solutions:")
            print("1. Use a more recent fork block number")
            print("2. Manually initialize the variable debt token")
            print("3. Use USDC only (which seems to work)")


def moccasin_main():
    main()


if __name__ == "__main__":
    main()
