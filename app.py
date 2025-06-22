import os
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from blockchain.block import Block, Blockchain
from blockchain.transaction import Transaction
from blockchain.wallet import Wallet
from blockchain.dag import DAG
from visualization.blockchain_visualizer import BlockchainVisualizer
from visualization.dag_visualizer import DAGVisualizer
import datetime
import json

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "blockchain_simulation_secret")

# Add custom Jinja2 filter for timestamp formatting
@app.template_filter('strftime')
def _jinja2_filter_datetime(timestamp):
    """Convert a timestamp to formatted datetime string."""
    try:
        dt = datetime.datetime.fromtimestamp(timestamp)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return str(timestamp)

# Initialize blockchain components
blockchain = Blockchain()
dag = DAG()
blockchain_visualizer = BlockchainVisualizer(blockchain)
dag_visualizer = DAGVisualizer(dag)

# Create default wallets
wallets = {
    "Alice": Wallet(name="Alice"),
    "Bob": Wallet(name="Bob"),
    "Charlie": Wallet(name="Charlie")
}

# Routes
@app.route('/')
def index():
    return render_template('index.html', blockchain=blockchain, dag=dag, wallets=wallets)

@app.route('/blockchain')
def view_blockchain():
    blockchain_data = blockchain_visualizer.get_blockchain_data()
    return render_template('blockchain.html', blockchain=blockchain, blockchain_data=blockchain_data)

@app.route('/dag')
def view_dag():
    dag_data = dag_visualizer.get_dag_data()
    return render_template('dag.html', dag=dag, dag_data=dag_data)

@app.route('/transactions')
def view_transactions():
    all_transactions = []
    for block in blockchain.chain:
        for tx in block.transactions:
            tx_dict = tx.to_dict()
            tx_dict['block_id'] = block.index
            tx_dict['timestamp'] = block.timestamp
            all_transactions.append(tx_dict)
    
    # Also add pending transactions
    for tx in blockchain.pending_transactions:
        tx_dict = tx.to_dict()
        tx_dict['block_id'] = 'Pending'
        tx_dict['timestamp'] = 'Pending'
        all_transactions.append(tx_dict)
    
    return render_template('transactions.html', transactions=all_transactions)

@app.route('/wallets')
def view_wallets():
    wallet_balances = {}
    for name, wallet in wallets.items():
        wallet_balances[name] = blockchain.get_balance(wallet.address)
    
    return render_template('wallets.html', wallets=wallets, balances=wallet_balances)

@app.route('/create_transaction', methods=['POST'])
def create_transaction():
    try:
        sender = request.form.get('sender')
        recipient = request.form.get('recipient')
        amount = float(request.form.get('amount'))
        
        # Create and sign transaction
        sender_wallet = wallets[sender]
        transaction = Transaction(sender_wallet.address, wallets[recipient].address, amount)
        transaction.sign(sender_wallet.private_key)
        
        # Add to blockchain's pending transactions
        blockchain.add_transaction(transaction)
        
        # Add to DAG
        dag.add_transaction(transaction)
        
        flash("Transaction created successfully!", "success")
    except Exception as e:
        flash(f"Error creating transaction: {str(e)}", "danger")
        logger.error(f"Transaction creation error: {str(e)}")
    
    return redirect(url_for('view_transactions'))

@app.route('/mine_block', methods=['POST'])
def mine_block():
    try:
        miner = request.form.get('miner')
        miner_wallet = wallets[miner]
        
        # Create mining reward transaction
        reward_tx = Transaction("BLOCKCHAIN", miner_wallet.address, 1.0)
        blockchain.add_transaction(reward_tx)
        
        # Mine new block
        new_block = blockchain.mine_block(miner_wallet.address)
        
        # Update DAG with the new block transactions
        for tx in new_block.transactions:
            dag.add_transaction(tx)
        
        flash(f"Block #{new_block.index} mined successfully by {miner}!", "success")
    except Exception as e:
        flash(f"Error mining block: {str(e)}", "danger")
        logger.error(f"Block mining error: {str(e)}")
    
    return redirect(url_for('view_blockchain'))

@app.route('/visualization/blockchain')
def visualization_blockchain():
    return jsonify(blockchain_visualizer.get_blockchain_data())

@app.route('/visualization/dag')
def visualization_dag():
    return jsonify(dag_visualizer.get_dag_data())

@app.route('/api/blockchain')
def api_blockchain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.to_dict())
    return jsonify(chain_data)

@app.route('/api/validate_chain')
def api_validate_chain():
    is_valid = blockchain.is_chain_valid()
    return jsonify({
        "is_valid": is_valid,
        "message": "Blockchain is valid" if is_valid else "Blockchain is invalid"
    })

@app.route('/api/dag_graph')
def api_dag_graph():
    """
    API endpoint to get DAG data for D3.js visualization.
    Returns nodes and edges in the format expected by D3.js.
    """
    try:
        # Get all transactions from DAG
        nodes = []
        edges = []
        
        # Create nodes from transactions
        for tx_hash, dag_tx in dag.transactions.items():
            node = {
                "id": tx_hash,
                "hash": tx_hash,
                "is_tip": tx_hash in dag.tips,
                "weight": dag_tx.weight,
                "sender": dag_tx.transaction.sender,
                "recipient": dag_tx.transaction.recipient,
                "amount": dag_tx.transaction.amount
            }
            nodes.append(node)
        
        # Create edges from graph
        for edge in dag.graph.edges():
            source_hash, target_hash = edge
            # Get transaction amount for the edge
            edge_data = dag.graph.get_edge_data(source_hash, target_hash)
            amount = edge_data.get('amount', 0) if edge_data else 0
            
            edge_info = {
                "source": source_hash,
                "target": target_hash,
                "amount": amount
            }
            edges.append(edge_info)
        
        return jsonify({
            "nodes": nodes,
            "edges": edges,
            "stats": {
                "transaction_count": len(nodes),
                "tip_count": len(dag.tips),
                "edge_count": len(edges)
            }
        })
        
    except Exception as e:
        logger.error(f"Error generating DAG graph data: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
