from enum import Enum

class Process:
    def __init__(self, action: str, transaction_id: int, data_item: str):
        self.action = action
        self.transaction_id = transaction_id
        self.data_item = data_item

    def __str__(self):
        return (f"{self.action}{self.transaction_id}({self.data_item})")