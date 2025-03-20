import hashlib
import time
import json
from typing import List, Dict, Any, Optional
from .transaction import Transaction
from .merkle_tree import MerkleTree

class Block:
    def __init__(self, index: int, previous_hash: str, transactions: List[Transaction], timestamp: Optional[float] = None):
        """
        Initialize a block in the blockchain.
        
        Args:
            index: Block position in the chain
            previous_hash: Hash of the previous block
            transactions: List of transactions in this block
            timestamp: Block creation timestamp (default: current time)
        """
        self.index = index
        self.timestamp = timestamp if timestamp else time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.merkle_tree = MerkleTree([tx.get_hash() for tx in transactions])
        self.merkle_root = self.merkle_tree.get_root()
        self.nonce = 0
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calculate the hash of the block."""
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "merkle_root": self.merkle_root,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True)
        
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty: int) -> None:
        """
        Mine a block by finding a hash that starts with the required number of zeros.
        
        Args:
            difficulty: Number of leading zeros required in the hash
        """
        target = "0" * difficulty
        
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
    
    def verify_transaction(self, transaction: Transaction, proof: List[str]) -> bool:
        """
        Verify a transaction using Merkle proof.
        
        Args:
            transaction: Transaction to verify
            proof: Merkle proof
            
        Returns:
            bool: True if transaction is verified, False otherwise
        """
        tx_hash = transaction.get_hash()
        return self.merkle_tree.verify_proof(tx_hash, self.merkle_root, proof)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert block to dictionary representation."""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "merkle_root": self.merkle_root,
            "hash": self.hash,
            "nonce": self.nonce
        }
    
    def __str__(self) -> str:
        return f"Block #{self.index} [Hash: {self.hash[:10]}..., Transactions: {len(self.transactions)}]"


class Blockchain:
    def __init__(self, difficulty: int = 4):
        """
        Initialize a blockchain.
        
        Args:
            difficulty: Mining difficulty (default: 4)
        """
        self.chain: List[Block] = []
        self.pending_transactions: List[Transaction] = []
        self.difficulty = difficulty
        
        # Create genesis block
        self.create_genesis_block()
    
    def create_genesis_block(self) -> Block:
        """Create and return the genesis block."""
        genesis_block = Block(0, "0", [Transaction("Genesis", "Genesis", 0)])
        genesis_block.mine_block(self.difficulty)
        self.chain.append(genesis_block)
        return genesis_block
    
    def get_latest_block(self) -> Block:
        """Get the latest block in the chain."""
        return self.chain[-1]
    
    def add_transaction(self, transaction: Transaction) -> bool:
        """
        Add a transaction to pending transactions.
        
        Args:
            transaction: Transaction to add
            
        Returns:
            bool: True if transaction is added, False otherwise
        """
        if not transaction.verify_signature():
            return False
        
        self.pending_transactions.append(transaction)
        return True
    
    def mine_block(self, miner_address: str) -> Block:
        """
        Mine a new block with all pending transactions.
        
        Args:
            miner_address: Address of the miner to receive the reward
            
        Returns:
            Block: The newly mined block
        """
        if not self.pending_transactions:
            raise ValueError("No transactions to mine")
        
        latest_block = self.get_latest_block()
        new_block = Block(
            index=latest_block.index + 1,
            previous_hash=latest_block.hash,
            transactions=self.pending_transactions
        )
        
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)
        self.pending_transactions = []
        
        return new_block
    
    def is_chain_valid(self) -> bool:
        """
        Validate the blockchain.
        
        Returns:
            bool: True if blockchain is valid, False otherwise
        """
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            # Verify current block hash
            if current_block.hash != current_block.calculate_hash():
                return False
            
            # Verify previous hash reference
            if current_block.previous_hash != previous_block.hash:
                return False
            
            # Verify all transactions in the block
            for tx in current_block.transactions:
                if not tx.verify_signature():
                    return False
        
        return True
    
    def get_balance(self, address: str) -> float:
        """
        Calculate balance for an address.
        
        Args:
            address: Address to calculate balance for
            
        Returns:
            float: Balance of the address
        """
        balance = 0.0
        
        # Calculate all inputs and outputs for the address
        for block in self.chain:
            for tx in block.transactions:
                if tx.sender == address:
                    balance -= tx.amount
                if tx.recipient == address:
                    balance += tx.amount
        
        return balance
    
    def find_transaction_block(self, transaction_hash: str) -> Optional[Block]:
        """
        Find the block containing a specific transaction.
        
        Args:
            transaction_hash: Hash of the transaction to find
            
        Returns:
            Optional[Block]: Block containing the transaction, or None if not found
        """
        for block in self.chain:
            for tx in block.transactions:
                if tx.get_hash() == transaction_hash:
                    return block
        
        return None
