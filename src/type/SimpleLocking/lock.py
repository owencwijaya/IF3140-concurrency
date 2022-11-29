class Lock:
    def __init__(self, data_item, transaction_id):
        self.data_item = data_item
        self.transaction_id = transaction_id

    def __str__(self):
        print(f'Data item {self.data_item} is being locked by transaction {self.transaction_id}')
