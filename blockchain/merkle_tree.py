import hashlib
from typing import List, Optional, Tuple

class MerkleTree:
    def __init__(self, leaves: List[str]):
        """
        Initialize a Merkle Tree with the given leaf nodes.
        
        Args:
            leaves: List of transaction hash strings
        """
        self.leaves = leaves
        self.layers = self._build_tree()
    
    def _hash_pair(self, left: str, right: str) -> str:
        """
        Hash two strings together.
        
        Args:
            left: Left string
            right: Right string
            
        Returns:
            str: Concatenated hash
        """
        data = left + right
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _build_tree(self) -> List[List[str]]:
        """
        Build the Merkle Tree from leaf nodes.
        
        Returns:
            List[List[str]]: Layers of the Merkle Tree
        """
        if not self.leaves:
            return [[]]
        
        # If odd number of leaves, duplicate the last one
        if len(self.leaves) % 2 == 1:
            self.leaves.append(self.leaves[-1])
        
        # Start with the leaf layer
        layers = [self.leaves]
        current_layer = self.leaves
        
        # Build tree upward until we reach the root
        while len(current_layer) > 1:
            new_layer = []
            
            # Process pairs of nodes
            for i in range(0, len(current_layer), 2):
                left = current_layer[i]
                right = current_layer[i+1] if i+1 < len(current_layer) else left
                new_layer.append(self._hash_pair(left, right))
            
            layers.append(new_layer)
            current_layer = new_layer
        
        return layers
    
    def get_root(self) -> str:
        """
        Get the Merkle root.
        
        Returns:
            str: Merkle root hash or empty string if tree is empty
        """
        if not self.layers or not self.layers[-1]:
            return ""
        
        return self.layers[-1][0]
    
    def get_proof(self, leaf_hash: str) -> List[Tuple[str, bool]]:
        """
        Generate a Merkle proof for a leaf node.
        
        Args:
            leaf_hash: Hash of the leaf to generate proof for
            
        Returns:
            List[Tuple[str, bool]]: List of (hash, is_right_node) tuples forming the proof
        """
        if not self.leaves:
            return []
        
        # Find the index of the leaf in the leaf layer
        try:
            index = self.leaves.index(leaf_hash)
        except ValueError:
            return []  # Leaf not found
        
        proof = []
        current_index = index
        
        # Go up through the layers
        for layer in self.layers[:-1]:  # Skip the root layer
            # Determine if this is a left or right node
            is_right_node = current_index % 2 == 0
            
            # Get the sibling index
            sibling_index = current_index - 1 if is_right_node else current_index + 1
            
            # Make sure sibling exists in the layer
            if sibling_index < len(layer):
                proof.append((layer[sibling_index], not is_right_node))
            
            # Move to the parent node in the next layer
            current_index = current_index // 2
        
        return proof
    
    def verify_proof(self, leaf_hash: str, merkle_root: str, proof: List[Tuple[str, bool]]) -> bool:
        """
        Verify a Merkle proof.
        
        Args:
            leaf_hash: Hash of the leaf node
            merkle_root: Expected Merkle root
            proof: Merkle proof as returned by get_proof()
            
        Returns:
            bool: True if proof is valid, False otherwise
        """
        if not proof:
            return leaf_hash == merkle_root
        
        current_hash = leaf_hash
        
        for sibling_hash, is_right_node in proof:
            if is_right_node:
                current_hash = self._hash_pair(current_hash, sibling_hash)
            else:
                current_hash = self._hash_pair(sibling_hash, current_hash)
        
        return current_hash == merkle_root
