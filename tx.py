from web3 import Web3
import json
import time
import random
from colorama import init, Fore, Style

init(autoreset=True)

# Constants
BASE_RPC_URL = "https://mainnet.base.org"
ARBITRUM_RPC_URL = "https://arb1.arbitrum.io/rpc"
BASE_CONTRACT_ADDRESS = "0xC5bf05cD32a14BFfb705Fb37a9d218895187376c"
ARBITRUM_CONTRACT_ADDRESS = "0xC5bf05cD32a14BFfb705Fb37a9d218895187376c"
MAX_DEPOSIT_ETH = 0.000001  # Updated maximum deposit limit in ETH

# Contract ABI
CONTRACT_ABI = '''
[
    {
        "constant": false,
        "inputs": [],
        "name": "depositETH",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    }
]
'''

# Network selection
def select_network():
    choice = input("Choose network (1 for Base, 2 for Arbitrum): ")
    if choice == "1":
        return BASE_RPC_URL, BASE_CONTRACT_ADDRESS
    elif choice == "2":
        return ARBITRUM_RPC_URL, ARBITRUM_CONTRACT_ADDRESS
    else:
        print(Fore.RED + "Invalid choice. Defaulting to Base network.")
        return BASE_RPC_URL, BASE_CONTRACT_ADDRESS

# Get maximum deposit amount
def get_max_deposit_amount():
    while True:
        try:
            max_amount = float(input(Fore.YELLOW + f"Enter the maximum deposit amount (Max {MAX_DEPOSIT_ETH} ETH): " + Style.RESET_ALL))
            if max_amount > MAX_DEPOSIT_ETH:
                print(Fore.RED + f"The maximum allowable deposit is {MAX_DEPOSIT_ETH} ETH.")
            else:
                return max_amount
        except ValueError:
            print(Fore.RED + "Invalid input. Please enter a numeric value.")

# Generate random deposit within the specified range up to a max of 0.000001 ETH
def get_random_deposit(max_amount):
    return random.uniform(0.00000001, min(0.000001, max_amount))

# Setup Web3 Connection
rpc_url, contract_address = select_network()
web3 = Web3(Web3.HTTPProvider(rpc_url))
contract = web3.eth.contract(address=contract_address, abi=json.loads(CONTRACT_ABI))

# Load Private Keys
with open("pvkey.txt", "r") as file:
    private_keys = [line.strip() for line in file if line.strip()]
nonces = {key: web3.eth.get_transaction_count(web3.eth.account.from_key(key).address) for key in private_keys}

# Send Transactions
def send_transactions(num_transactions, max_amount):
    tx_count = 0
    for i in range(num_transactions):
        for private_key in private_keys:
            from_address = web3.eth.account.from_key(private_key).address
            short_from_address = f"{from_address[:4]}...{from_address[-4:]}"
            try:
                deposit_amount = get_random_deposit(max_amount)
                tx_hash = execute_transaction(private_key, from_address, short_from_address, deposit_amount)
                tx_count += 1

                # Limit batch transactions
                if tx_count >= 50:
                    tx_count = 0
                time.sleep(1)  # Adjust delay if needed

            except Exception as e:
                handle_exception(e, private_key, from_address, short_from_address)

# Execute Transaction
def execute_transaction(private_key, from_address, short_from_address, amount_eth):
    amount_wei = web3.to_wei(amount_eth, 'ether')
    transaction = contract.functions.depositETH().build_transaction({
        'from': from_address,
        'value': amount_wei,
        'gas': 100000,
        'gasPrice': web3.eth.gas_price,
        'nonce': nonces[private_key]
    })

    signed_txn = web3.eth.account.sign_transaction(transaction, private_key=private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
    tx_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(Fore.GREEN + f"[{tx_time}] Transaction sent from {short_from_address} - Hash: {tx_hash.hex()} - Amount: {amount_eth:.8f} ETH")

    # Update nonce
    nonces[private_key] += 1
    return tx_hash

# Handle Exceptions
def handle_exception(e, private_key, from_address, short_from_address):
    if 'nonce too low' in str(e):
        print(Fore.YELLOW + f"[Warning] Nonce too low for {short_from_address}. Updating nonce...")
        nonces[private_key] = web3.eth.get_transaction_count(from_address)
    else:
        print(Fore.RED + f"[Error] Transaction failed from {short_from_address}: {str(e)}")

# Main Execution
if __name__ == "__main__":
    max_deposit_amount = get_max_deposit_amount()
    num_transactions = int(input(Fore.YELLOW + "Enter the number of transactions to be executed: " + Style.RESET_ALL))
    print(Fore.CYAN + "\nStarting Transactions...\n" + Style.RESET_ALL)
    
    start_time = time.time()
    send_transactions(num_transactions, max_deposit_amount)
    
    elapsed_time = time.time() - start_time
    print(Fore.MAGENTA + f"\nAll transactions completed in {elapsed_time:.2f} seconds.\n")
