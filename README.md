# Mox Algorithmic Trading

An automated DeFi portfolio rebalancing system built with Python and Moccasin, integrating Aave V3 lending protocol and Uniswap V3 for algorithmic trading strategies on Ethereum networks.

## 🎯 Project Goals

This project demonstrates an automated algorithmic trading strategy that:

- **Maintains Target Allocations**: Automatically rebalances a portfolio between WETH and USDC to maintain target percentage allocations (70% WETH / 30% USDC by default)
- **Maximizes Capital Efficiency**: Deposits idle assets into Aave V3 to earn yield while maintaining liquidity
- **Price-Aware Rebalancing**: Uses Chainlink price feeds for accurate USD valuations to determine when rebalancing is needed
- **Automated Execution**: Combines deposits, withdrawals, and swaps in a single execution flow
- **Risk Management**: Implements slippage protection and rebalancing thresholds to prevent unnecessary trades

## 🛠️ Technologies Used

### Core Framework
- **[Moccasin](https://github.com/cyfrin/moccasin)** - Pythonic smart contract development framework for Vyper
- **[Titanoboa](https://github.com/vyperlang/titanoboa)** - Python interpreter for Vyper contracts
- **Python 3.11+** - Primary programming language

### DeFi Protocols
- **[Aave V3](https://aave.com/)** - Decentralized lending and borrowing protocol for yield generation
- **[Uniswap V3](https://uniswap.org/)** - Decentralized exchange for token swaps
- **[Chainlink](https://chain.link/)** - Decentralized oracle network for price feeds

### Supported Networks
- Ethereum Mainnet (Forked)
- ZKSync Sepolia Testnet
- Local PyEVM (for development)

## 📁 Project Structure

```
mox-algorithmic-trading/
├── script/                          # Python scripts for contract interaction
│   ├── _setup_script.py            # Network setup and contract initialization
│   ├── deposit.py                  # Aave deposit functionality
│   ├── rebalance.py                # Portfolio rebalancing logic
│   └── deposit_and_rebalance.py    # Combined deposit and rebalance workflow
├── abis/                            # Contract ABI files
│   ├── aavev3_pool_address_provider.json
│   ├── aavev3_protocol_data_provider.json
│   ├── pool.json
│   ├── usdc.json
│   ├── weth.json
│   ├── eth_usd.json
│   ├── usdc_usd.json
│   └── uniswap_swap_router.json
├── tests/                           # Test files
├── moccasin.toml                   # Moccasin configuration file
├── pyproject.toml                  # Python project configuration
├── notebook.ipynb                  # Jupyter notebook for interactive development
└── README.md                       # This file
```

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) or pip for package management
- An Ethereum RPC endpoint (Alchemy, Infura, or similar)
- A wallet with funds for testing (optional, can use forked network)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/mox-algorithmic-trading.git
   cd mox-algorithmic-trading
   ```

2. **Create a virtual environment and install dependencies**
   ```bash
   # Using uv (recommended)
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e .

   # Or using pip
   python -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```

3. **Install Moccasin**
   ```bash
   uv tool install moccasin
   # or
   pip install moccasin
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# RPC Endpoints
MAINNET_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_ALCHEMY_KEY
SEPOLIA_RPC_URL=https://eth-sepolia.g.alchemy.com/v2/YOUR_ALCHEMY_KEY
ZKSYNC_SEPOLIA_RPC_URL=https://sepolia.era.zksync.dev

# Wallet Configuration
# IMPORTANT: Never commit your private keys or passwords!
# Use this for testing with test accounts only
ANVIL_1_PASSWORD_FILE=/path/to/your/password/file

# Block Explorer API Keys (for contract verification)
ETHERSCAN_API_KEY=your_etherscan_api_key_here
ZKSYNC_EXPLORER_API_KEY=your_explorer_api_key_here

# Optional: Custom Gas Settings
# GAS_PRICE=20000000000
# GAS_LIMIT=3000000
```

### Network Configuration

The project is configured in [`moccasin.toml`](moccasin.toml) with the following networks:

#### Ethereum Mainnet Fork (Default)
```toml
[networks.eth-forked]
fork = true
url = "${MAINNET_RPC_URL}"
default_account_name = "anvil_1"
```

**Contract Addresses (Ethereum Mainnet):**
- USDC: `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48`
- WETH: `0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2`
- Aave V3 Pool Address Provider: `0x2f39d218133AFaB8F2B819B1066c7E434Ad94E9e`
- Aave V3 Protocol Data Provider: `0x497a1994c46d4f6C864904A9f1fac6328Cb7C8a6`
- Chainlink ETH/USD: `0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419`
- Chainlink USDC/USD: `0x8fFfFfd4AfB6115b954Bd326cbe7B4BA576818f6`
- Uniswap V3 Router: `0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45`

#### ZKSync Sepolia Testnet
```toml
[networks.zksync-sepolia]
url = "https://sepolia.era.zksync.dev"
chain_id = 300
is_zksync = true
prompt_live = true
```

## 📖 Usage

### Running Scripts

The project provides three main scripts:

#### 1. Deposit Assets into Aave
Deposits WETH and USDC into Aave V3 to earn yield:

```bash
mox run deposit
```

#### 2. Rebalance Portfolio
Rebalances the portfolio between WETH and USDC based on target allocations:

```bash
mox run rebalance
```

#### 3. Deposit and Rebalance (Combined)
Performs both deposit and rebalancing in a single transaction:

```bash
mox run deposit_and_rebalance
```

### Network Selection

Run on a forked network (default):
```bash
mox run deposit_and_rebalance --fork
```

Run on a specific network:
```bash
mox run deposit_and_rebalance --network zksync-sepolia
```

Run on local PyEVM:
```bash
mox run deposit_and_rebalance --network pyevm
```

### Interactive Development

Use the Jupyter notebook for interactive exploration:

```bash
jupyter notebook notebook.ipynb
```

## 🔄 How It Works

### 1. Setup Phase
- Connects to the specified network (fork, testnet, or local)
- Initializes contract interfaces for USDC, WETH, Aave, and Uniswap
- On local/forked networks, mints test tokens for the user

### 2. Deposit Phase
- Approves Aave Pool to spend tokens
- Deposits USDC and WETH into Aave V3
- Receives aUSDC and aWETH tokens representing deposited amounts

### 3. Rebalancing Phase
- Fetches current portfolio balances from Aave
- Gets USD prices from Chainlink oracles
- Calculates current allocation percentages
- If allocation drift exceeds threshold (10% by default):
  - Withdraws assets from Aave
  - Swaps on Uniswap to rebalance
  - Re-deposits balanced amounts into Aave

### 4. Yield Generation
- While assets remain in Aave, they earn interest
- aTokens automatically accrue value over time

## 🎯 Strategy Configuration

### Target Allocations
Edit in [`rebalance.py`](script/rebalance.py):

```python
target_usdc_percent_allocation = 0.3  # 30% USDC
target_weth_percent_allocation = 0.7  # 70% WETH
```

### Rebalancing Threshold
Edit the `BUFFER` variable in [`rebalance.py`](script/rebalance.py):

```python
BUFFER = 0.1  # Rebalance if allocation drifts by more than 10%
```

### Initial Balances (Testing)
Edit in [`_setup_script.py`](script/_setup_script.py):

```python
STARTING_ETH_BALANCE = int(1000e18)   # 1000 ETH
STARTING_WETH_BALANCE = int(1e18)     # 1 WETH
STARTING_USDC_BALANCE = int(100e6)    # 100 USDC
```

## 🧪 Testing

Run the test suite:

```bash
mox test
```

Run tests with verbose output:
```bash
mox test -v
```

## 🔒 Security Considerations

### For Development/Testing
- ✅ Use forked networks to test with real contract state
- ✅ Test with small amounts first
- ✅ Never commit private keys or passwords to git
- ✅ Use environment variables for sensitive data

### For Production
- ⚠️ **This is a learning/demo project** - use at your own risk
- ⚠️ Always audit smart contracts before deploying real funds
- ⚠️ Implement proper access controls and pausability
- ⚠️ Consider flash loan attack vectors
- ⚠️ Monitor gas prices and set appropriate limits
- ⚠️ Implement circuit breakers for extreme market conditions

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Cyfrin/Moccasin](https://github.com/cyfrin/moccasin) for the excellent development framework
- [Aave](https://aave.com/) for the lending protocol
- [Uniswap](https://uniswap.org/) for the DEX infrastructure
- [Chainlink](https://chain.link/) for reliable price feeds

## 📚 Additional Resources

- [Moccasin Documentation](https://cyfrin.github.io/moccasin/)
- [Aave V3 Documentation](https://docs.aave.com/developers/)
- [Uniswap V3 Documentation](https://docs.uniswap.org/)
- [Chainlink Price Feeds](https://docs.chain.link/data-feeds/price-feeds)

## 🐛 Known Issues & Troubleshooting

### Common Errors

**"Global Config object not initialized"**
- Ensure you're running commands from the project root directory
- Try running `mox config` from the project directory

**Contract interaction reverts**
- Check that you're on the correct network
- Verify contract addresses in `moccasin.toml`
- Ensure you have sufficient balance/allowances

**Fork network issues**
- Verify your RPC URL is correct and has available credits
- Some RPC providers rate limit - consider using a dedicated endpoint

---

**Built with ❤️ using Moccasin and Python**

