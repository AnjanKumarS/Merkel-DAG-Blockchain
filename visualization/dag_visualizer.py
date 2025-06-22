from typing import Dict, List, Any

class DAGVisualizer:
    def __init__(self, dag):
        """
        Initialize DAG visualizer.
        
        Args:
            dag: DAG instance to visualize
        """
        self.dag = dag
    
    def get_dag_data(self) -> Dict[str, Any]:
        """
        Get DAG data for visualization.
        
        Returns:
            Dict[str, Any]: Data for visualizing the DAG
        """
        # Get tips
        tips = [self.dag.transactions[tip_hash].to_dict() for tip_hash in self.dag.tips]
        
        # Get all transactions
        all_transactions = []
        for tx_hash, dag_tx in self.dag.transactions.items():
            tx_data = dag_tx.to_dict()
            tx_data['is_tip'] = tx_hash in self.dag.tips
            all_transactions.append(tx_data)
        
        # Get DAG stats
        stats = {
            "transaction_count": len(self.dag.transactions),
            "tip_count": len(self.dag.tips),
            "edge_count": self.dag.graph.number_of_edges()
        }
        
        return {
            "transactions": all_transactions,
            "tips": tips,
            "stats": stats
        }
