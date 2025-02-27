import secrets

from tqdm import tqdm

from flexpkit.basic_utils import *


def mine_block(transaction_str_list):
    trans_str = '-'.join(transaction_str_list) 

    max_nonce = 1000000000
    # Using secrets.randbelow() for cryptographically secure random number generation
    # to prevent nonce prediction attacks in the mining process
    min_nonce = secrets.randbelow(int(max_nonce / 10))
    
    leading_zeros = 4
    for i in tqdm(range(min_nonce, max_nonce), desc='mining'):
        hash = generate_str_sha1('{}-{}'.format(trans_str, i))
        if hash[:leading_zeros] == ''.zfill(leading_zeros):
            return i, hash
    
    return None, None