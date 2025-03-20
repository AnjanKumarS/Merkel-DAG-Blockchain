import hashlib
import json
import time
from typing import Dict, Any, Optional
import base64
import ecdsa

class Transaction:
    def __init__(self, sender: str, recipient: str, amount: float, timestamp: Optional[float] = None):
        """
        Initialize a transaction.
        
        Args:
            sender: Sender's address
            recipient: Recipient's address
            amount: Amount to transfer
            timestamp: Transaction timestamp (default: current time)
        """
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.timestamp = timestamp if timestamp else time.time()
        self.signature = None
    
    def calculate_hash(self) -> str:
        """Calculate transaction hash using SHA-256."""
        tx_string = json.dumps({
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "timestamp": self.timestamp
        }, sort_keys=True)
        
        return hashlib.sha256(tx_string.encode()).hexdigest()
    
    def get_hash(self) -> str:
        """Get transaction hash."""
        return self.calculate_hash()
    
    def sign(self, private_key: ecdsa.SigningKey) -> None:
        """
        Sign the transaction using the sender's private key.
        
        Args:
            private_key: ECDSA private key for signing
        """
        tx_hash = self.calculate_hash()
        self.signature = private_key.sign(tx_hash.encode())
    
    def verify_signature(self) -> bool:
        """
        Verify transaction signature.
        
        Returns:
            bool: True if signature is valid, False otherwise
        """
        # Skip verification for coinbase/genesis transactions
        if self.sender == "BLOCKCHAIN" or self.sender == "Genesis":
            return True
        
        if not self.signature:
            return False
        
        try:
            # Convert hex address to public key
            # In a real blockchain, addresses are derived from public keys
            # Here we're using a simplified approach for demonstration purposes
            public_key_bytes = bytes.fromhex(self.sender)
            public_key = ecdsa.VerifyingKey.from_string(
                public_key_bytes,
                curve=ecdsa.SECP256k1
            )
            
            tx_hash = self.calculate_hash()
            return public_key.verify(self.signature, tx_hash.encode())
        except Exception:
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert transaction to dictionary representation."""
        signature_hex = None
        if self.signature:
            signature_hex = self.signature.hex()
            
        return {
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "timestamp": self.timestamp,
            "signature": signature_hex,
            "hash": self.get_hash()
        }
    
    def __str__(self) -> str:
        return f"Transaction [From: {self.sender[:10]}..., To: {self.recipient[:10]}..., Amount: {self.amount}]"
