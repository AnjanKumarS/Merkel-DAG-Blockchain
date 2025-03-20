import matplotlib.pyplot as plt
import networkx as nx
import io
import base64
from typing import Dict, List, Any
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

class DAGVisualizer:
    def __init__(self, dag):
        """
        Initialize DAG visualizer.
        
        Args:
            dag: DAG instance to visualize
        """
        self.dag = dag
    
    def plot_dag(self) -> str:
        """
        Generate a visualization of the DAG structure.
        
        Returns:
            str: Base64 encoded PNG image
        """
        G = self.dag.graph.copy()
        
        plt.figure(figsize=(14, 10))
        
        # Use a layout algorithm that works well for DAGs
        pos = nx.kamada_kawai_layout(G)
        
        # Get node weights for sizing
        weights = [G.nodes[node].get('weight', 1) * 200 for node in G.nodes]
        
        # Determine node colors (tips are highlighted)
        node_colors = []
        for node in G.nodes:
            if node in self.dag.tips:
                node_colors.append('orange')
            else:
                node_colors.append('skyblue')
        
        # Draw nodes with weights affecting size
        nx.draw_networkx_nodes(
            G, pos,
            node_color=node_colors,
            node_size=weights,
            alpha=0.8
        )
        
        # Draw edges
        nx.draw_networkx_edges(
            G, pos,
            arrows=True,
            arrowstyle='-|>',
            arrowsize=15,
            width=1.5,
            edge_color='gray',
            alpha=0.6
        )
        
        # Node labels (shortened hashes)
        node_labels = {node: node[:6] + "..." for node in G.nodes}
        nx.draw_networkx_labels(
            G, pos,
            labels=node_labels,
            font_size=8,
            font_family='sans-serif'
        )
        
        plt.title("DAG Transaction Structure", fontsize=16)
        plt.axis('off')
        
        # Convert plot to base64 encoded image
        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight')
        img.seek(0)
        plt.close()
        
        return base64.b64encode(img.getvalue()).decode('utf-8')
    
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
            "stats": stats,
            "dag_image": self.plot_dag()
        }
