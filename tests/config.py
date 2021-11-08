# Allow tolerance of 1 millionth REEF (10**12 / 10**18) in tests
TOLERANCE = 10 ** 12
# REEF Decimals
REEF_DECIMALS = 10 ** 18
# ERC20 Deploymnet bytecode
ERC2_DEPLOYMENT_BYTECODE = open(
    "tests/assets/erc20_deployment_bytecode.txt", "r"
).read()
