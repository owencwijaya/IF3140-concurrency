from typing import List

from type.process import Process

class Transaction:
    def __init__(self, transaction_id: int, transaction_state: str, timestamp: int):
        self.id: int = transaction_id
        self.state: str = transaction_state
        self.timestamp: int = timestamp
        self.locked_items: List[str] = []
        self.blocked_processes: List[Process] = []