import hashlib
import random
import time
from typing import List, Dict, Any, Callable

def calculate_hash(data: str) -> str:
    """
    Calculate SHA-256 hash of data.
    
    Args:
        data: String data to hash
        
    Returns:
        str: Hexadecimal hash string
    """
    return hashlib.sha256(data.encode()).hexdigest()

def generate_nonce() -> int:
    """
    Generate a random nonce.
    
    Returns:
        int: Random nonce
    """
    return random.randint(0, 2**32 - 1)

def timestamp_to_string(timestamp: float) -> str:
    """
    Convert Unix timestamp to human-readable string.
    
    Args:
        timestamp: Unix timestamp
        
    Returns:
        str: Human-readable date/time string
    """
    import datetime
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def calculate_merkle_root(hashes: List[str]) -> str:
    """
    Calculate Merkle root from a list of hashes.
    
    Args:
        hashes: List of hash strings
        
    Returns:
        str: Merkle root hash
    """
    if not hashes:
        return ""
    
    if len(hashes) == 1:
        return hashes[0]
    
    # Make sure we have an even number of hashes
    if len(hashes) % 2 == 1:
        hashes.append(hashes[-1])
    
    # Combine pairs of hashes
    next_level = []
    for i in range(0, len(hashes), 2):
        combined = hashes[i] + hashes[i+1]
        next_hash = calculate_hash(combined)
        next_level.append(next_hash)
    
    # Recursively calculate Merkle root for the next level
    return calculate_merkle_root(next_level)

def mine_with_difficulty(hash_function: Callable[[], str], difficulty: int) -> str:
    """
    Mine a hash that satisfies the difficulty requirement.
    
    Args:
        hash_function: Function that generates a new hash
        difficulty: Number of leading zeros required
        
    Returns:
        str: Hash that satisfies the difficulty requirement
    """
    target = "0" * difficulty
    current_hash = hash_function()
    
    nonce = 0
    while not current_hash.startswith(target):
        nonce += 1
        current_hash = hash_function()
    
    return current_hash

def format_amount(amount: float) -> str:
    """
    Format an amount with 2 decimal places.
    
    Args:
        amount: Amount to format
        
    Returns:
        str: Formatted amount string
    """
    return f"{amount:.2f}"
