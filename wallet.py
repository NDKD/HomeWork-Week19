# Import dependencies
import subprocess
import json
import os
from dotenv import load_dotenv


# Load and set environment variables
load_dotenv()
mnemonic=os.getenv("mnemonic")

# Import constants.py and necessary functions from bit and web3
# YOUR CODE HERE
from constants import BTC, BTCTEST, ETH
from pprint import pprint
 
from bit import PrivateKeyTestnet
from bit.network import NetworkAPI
  
from web3 import Web3, middleware, Account
from web3.gas_strategies.time_based import medium_gas_price_strategy
from web3.middleware import geth_poa_middleware


 # connect Web3
w3 = Web3(Web3.HTTPProvider(os.getenv('WEB3_PROVIDER', 'http://localhost:8545')))

# enable PoA middleware
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
 


# set gas price strategy to built-in "medium" algorithm (est ~5min per tx)
w3.eth.setGasPriceStrategy(medium_gas_price_strategy)

mnemonic = os.getenv("MNEMONIC", "cinnamon suit clutch elite become rare hurt asthma scout sibling hope miracle")
 
 
# Create a function called `derive_wallets`
def derive_wallets(coin=BTC, mnemonic=mnemonic, depth=3):
    command = f'php ./derive -g --mnemonic="{mnemonic}" --cols=all --coin={coin} --numderive={depth} --format=json'
    # print(command)
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    return json.loads(output)
    
       


# Create a function called `priv_key_to_account` that converts privkey strings to account objects.
def priv_key_to_account( coin, priv_key):
    # YOUR CODE HERE
    if coin == ETH:
        return Account.privateKeyToAccount(priv_key)
    if coin == BTCTEST:
        return PrivateKeyTestnet(priv_key)

# Create a function called `create_tx` that creates an unsigned transaction appropriate metadata.
def create_tx(coin, account, to, amount):
    # YOUR CODE HERE
    if coin == ETH:
        value = w3.toWei(amount, "ether") # convert 1.2 ETH to 120000000000 wei
        gasEstimate = w3.eth.estimateGas({ "to": to, "from": account.address, "amount": value })
        return {
            "to": to,
            "from": account.address,
            "value": value,
            "gas": gasEstimate,
            "gasPrice": w3.eth.generateGasPrice(),
            "nonce": w3.eth.getTransactionCount(account.address),
            "chainId": w3.net.chainId
        }
    if coin == BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(account.address, [(to, amount, BTC)])
    

# Create a function called `send_tx` that calls `create_tx`, signs and sends the transaction.
def send_tx(coin, account, to, amount):
    # YOUR CODE HERE
    if coin == ETH:
        raw_tx = create_tx(coin, account, to, amount)
        signed = account.signTransaction(raw_tx)
        return w3.eth.sendRawTransaction(signed.rawTransaction)
    if coin == BTCTEST:
        raw_tx = create_tx(coin, account, to, amount)
        signed = account.sign_transaction(raw_tx)
        return NetworkAPI.broadcast_tx_testnet(signed)

# Create a dictionary object called coins to store the output from `derive_wallets`.
coins = {
    ETH: derive_wallets(coin=ETH),
    BTCTEST: derive_wallets(coin=BTCTEST),
}

from_account = priv_key_to_account(BTCTEST, coins[BTCTEST][2]["privkey"])
#from_account = coins[BTCTEST][2]

amount = 0.00001
coin = BTCTEST
to_account = coins[BTCTEST][0]["address"]
pprint(coins[BTCTEST][2])

print(send_tx(coin, from_account, to_account, amount))
