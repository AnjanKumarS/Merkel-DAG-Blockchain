import hashlib
import ecdsa
import base64
import binascii
from typing import Dict, Any, Tuple

class Wallet:
    def __init__(self, private_key: ecdsa.SigningKey = None, name: str = None):
        """
        Initialize a wallet with a private key or generate a new one.
        
        Args:
            private_key: Existing private key (default: None, generates new key)
            name: Human-readable name for the wallet (default: None)
        """
        self.name = name
        
        # Generate new keys if none provided
        if not private_key:
            self.private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
        else:
            self.private_key = private_key
            
        self.public_key = self.private_key.get_verifying_key()
        self.address = self._generate_address()
    
    def _generate_address(self) -> str:
        """
        Generate a wallet address from the public key.
        
        Returns:
            str: Wallet address
        """
        # Get the public key as bytes
        public_key_bytes = self.public_key.to_string()
        
        # Hash the public key using SHA-256
        sha256_hash = hashlib.sha256(public_key_bytes).digest()
        
        # Further hash with RIPEMD-160 (using double SHA-256 as alternative)
        ripemd160_hash = hashlib.new('sha256', sha256_hash).digest()
        
        # Convert to hexadecimal string for easy display
        return binascii.hexlify(public_key_bytes).decode('utf-8')
    
    def sign_transaction(self, transaction_hash: str) -> bytes:
        """
        Sign a transaction hash with the private key.
        
        Args:
            transaction_hash: Hash of the transaction to sign
            
        Returns:
            bytes: Signature
        """
        return self.private_key.sign(transaction_hash.encode())
    
    def get_keys(self) -> Tuple[str, str]:
        """
        Get the private and public keys as hex strings.
        
        Returns:
            Tuple[str, str]: (private_key_hex, public_key_hex)
        """
        private_key_hex = self.private_key.to_string().hex()
        public_key_hex = self.public_key.to_string().hex()
        return private_key_hex, public_key_hex
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert wallet to dictionary representation."""
        private_key_hex, public_key_hex = self.get_keys()
        return {
            "name": self.name,
            "address": self.address,
            "public_key": public_key_hex,
            # Private key would normally not be included in a real application
            "private_key": private_key_hex
        }
