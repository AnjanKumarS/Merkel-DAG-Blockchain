import hashlib
import time
from typing import Dict, List, Set, Any, Optional
import networkx as nx
from .transaction import Transaction

class DAGTransaction:
    def __init__(self, transaction: Transaction, references: List[str]):
        """
        Initialize a DAG transaction.
        
        Args:
            transaction: The actual transaction
            references: List of previous transaction hashes this one approves
        """
        self.transaction = transaction
        self.references = references  # References to previous transactions (approvals)
        self.timestamp = time.time()
        self.weight = 1.0  # Initial weight
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calculate DAG transaction hash."""
        data = (
            self.transaction.get_hash() + 
            "".join(self.references) + 
            str(self.timestamp)
        )
        return hashlib.sha256(data.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert DAG transaction to dictionary representation."""
        return {
            "transaction": self.transaction.to_dict(),
            "references": self.references,
            "timestamp": self.timestamp,
            "weight": self.weight,
            "hash": self.hash
        }


class DAG:
    def __init__(self):
        """Initialize a Directed Acyclic Graph for transaction consensus."""
        self.transactions: Dict[str, DAGTransaction] = {}  # Hash -> DAGTransaction
        self.tips: Set[str] = set()  # Set of unconfirmed transaction hashes
        self.graph = nx.DiGraph()  # NetworkX graph for visualization and analysis
        
        # Create genesis transaction
        self.create_genesis()
    
    def create_genesis(self) -> DAGTransaction:
        """Create and return the genesis transaction."""
        genesis_tx = Transaction("Genesis", "Genesis", 0.0)
        dag_tx = DAGTransaction(genesis_tx, [])
        
        self.transactions[dag_tx.hash] = dag_tx
        self.tips.add(dag_tx.hash)
        
        # Add to graph
        self.graph.add_node(dag_tx.hash, **dag_tx.to_dict())
        
        return dag_tx
    
    def select_tips(self, num_tips: int = 2) -> List[str]:
        """
        Select tips to reference using a simplified MCMC random walk algorithm.
        
        Args:
            num_tips: Number of tips to select
            
        Returns:
            List[str]: List of selected tip hashes
        """
        if len(self.tips) <= num_tips:
            return list(self.tips)
        
        # Simple random tip selection for demonstration
        # In a real implementation, this would use MCMC or other algorithms
        import random
        return random.sample(list(self.tips), num_tips)
    
    def add_transaction(self, transaction: Transaction, num_tips: int = 2) -> DAGTransaction:
        """
        Add a transaction to the DAG.
        
        Args:
            transaction: Transaction to add
            num_tips: Number of tips to reference
            
        Returns:
            DAGTransaction: The DAG transaction object
        """
        # Select tips to reference
        references = self.select_tips(num_tips)
        
        # Create DAG transaction
        dag_tx = DAGTransaction(transaction, references)
        
        # Update tips (remove referenced tips, add this transaction)
        for ref in references:
            if ref in self.tips:
                self.tips.remove(ref)
        
        self.tips.add(dag_tx.hash)
        
        # Add to transactions dictionary
        self.transactions[dag_tx.hash] = dag_tx
        
        # Add to graph
        self.graph.add_node(dag_tx.hash, **dag_tx.to_dict())
        for ref in references:
            self.graph.add_edge(dag_tx.hash, ref)
        
        # Update cumulative weights
        self.update_weights(dag_tx.hash)
        
        return dag_tx
    
    def update_weights(self, start_hash: str) -> None:
        """
        Update cumulative weights based on a new transaction.
        
        Args:
            start_hash: Hash of the new transaction
        """
        # Simple BFS to update weights
        visited = set()
        queue = [start_hash]
        
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
                
            visited.add(current)
            
            # Update weight for successors
            for successor in self.graph.successors(current):
                self.transactions[successor].weight += 1
                queue.append(successor)
    
    def get_transaction(self, tx_hash: str) -> Optional[DAGTransaction]:
        """
        Get a transaction by hash.
        
        Args:
            tx_hash: Transaction hash
            
        Returns:
            Optional[DAGTransaction]: The transaction or None if not found
        """
        return self.transactions.get(tx_hash)
    
    def is_confirmed(self, tx_hash: str, confirmation_threshold: float = 10.0) -> bool:
        """
        Check if a transaction is confirmed based on cumulative weight.
        
        Args:
            tx_hash: Transaction hash
            confirmation_threshold: Weight threshold for confirmation
            
        Returns:
            bool: True if transaction is confirmed, False otherwise
        """
        tx = self.get_transaction(tx_hash)
        if not tx:
            return False
        
        return tx.weight >= confirmation_threshold
    
    def get_all_transactions(self) -> List[DAGTransaction]:
        """
        Get all transactions in the DAG.
        
        Returns:
            List[DAGTransaction]: List of all transactions
        """
        return list(self.transactions.values())
    
    def get_tips(self) -> List[DAGTransaction]:
        """
        Get all tip transactions.
        
        Returns:
            List[DAGTransaction]: List of tip transactions
        """
        return [self.transactions[tip_hash] for tip_hash in self.tips]
