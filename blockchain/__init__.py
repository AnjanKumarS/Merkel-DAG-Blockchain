"""
Blockchain implementation with Merkle Trees and DAG consensus.

This package provides the core components for a blockchain simulation:
- Block: Basic block structure with Merkle Tree for transaction verification
- Transaction: Cryptographically signed transactions
- Merkle Tree: Efficient transaction verification
- DAG: Directed Acyclic Graph for scalable consensus
- Wallet: Key management and transaction signing
"""

from .block import Block, Blockchain
from .transaction import Transaction
from .merkle_tree import MerkleTree
from .dag import DAG, DAGTransaction
from .wallet import Wallet
from .utils import calculate_hash, timestamp_to_string

__all__ = [
    'Block',
    'Blockchain',
    'Transaction',
    'MerkleTree',
    'DAG',
    'DAGTransaction',
    'Wallet',
    'calculate_hash',
    'timestamp_to_string'
]
