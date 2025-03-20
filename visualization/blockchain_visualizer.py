import matplotlib.pyplot as plt
import networkx as nx
import io
import base64
from typing import Dict, List, Any, Optional
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

class BlockchainVisualizer:
    def __init__(self, blockchain):
        """
        Initialize blockchain visualizer.
        
        Args:
            blockchain: Blockchain instance to visualize
        """
        self.blockchain = blockchain
    
    def generate_graph(self) -> nx.DiGraph:
        """
        Generate a directed graph representation of the blockchain.
        
        Returns:
            nx.DiGraph: NetworkX directed graph
        """
        G = nx.DiGraph()
        
        # Add blocks as nodes
        for block in self.blockchain.chain:
            # Add block
            G.add_node(
                f"Block {block.index}",
                label=f"Block {block.index}",
                hash=block.hash[:10] + "...",
                tx_count=len(block.transactions),
                timestamp=block.timestamp,
                height=block.index
            )
            
            # Add edge from this block to previous block
            if block.index > 0:
                G.add_edge(
                    f"Block {block.index}",
                    f"Block {block.index - 1}",
                    label="Previous"
                )
        
        return G
    
    def plot_blockchain(self) -> str:
        """
        Generate a visualization of the blockchain.
        
        Returns:
            str: Base64 encoded PNG image
        """
        G = self.generate_graph()
        
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(G, k=0.5, iterations=50)
        
        # Draw nodes with custom attributes
        nx.draw_networkx_nodes(
            G, pos,
            node_color='skyblue',
            node_size=2000,
            alpha=0.8
        )
        
        # Draw edges
        nx.draw_networkx_edges(
            G, pos,
            arrows=True,
            arrowstyle='-|>',
            arrowsize=20,
            width=2,
            edge_color='gray'
        )
        
        # Node labels
        node_labels = {}
        for node in G.nodes:
            node_data = G.nodes[node]
            node_labels[node] = f"{node}\nHash: {node_data['hash']}\nTx: {node_data['tx_count']}"
        
        nx.draw_networkx_labels(
            G, pos,
            labels=node_labels,
            font_size=10,
            font_family='sans-serif'
        )
        
        plt.title("Blockchain Structure", fontsize=16)
        plt.axis('off')
        
        # Convert plot to base64 encoded image
        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight')
        img.seek(0)
        plt.close()
        
        return base64.b64encode(img.getvalue()).decode('utf-8')
    
    def get_blockchain_data(self) -> Dict[str, Any]:
        """
        Get blockchain data for visualization.
        
        Returns:
            Dict[str, Any]: Data for visualizing the blockchain
        """
        blocks_data = []
        
        for block in self.blockchain.chain:
            blocks_data.append({
                "index": block.index,
                "hash": block.hash,
                "previous_hash": block.previous_hash,
                "timestamp": block.timestamp,
                "nonce": block.nonce,
                "merkle_root": block.merkle_root,
                "transaction_count": len(block.transactions)
            })
        
        return {
            "blocks": blocks_data,
            "blockchain_image": self.plot_blockchain(),
            "chain_length": len(self.blockchain.chain),
            "is_valid": self.blockchain.is_chain_valid()
        }
