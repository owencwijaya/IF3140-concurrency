from type.Optimistic.transaction import Transaction
from type.process import Process

from typing import List


class OptimisticManager():
    transaction_list: List[Transaction] = []
    timestamp: int = 1

    # cek apakah transaksi udah pernah jalan sebelumnya
    def check_started(self, process: Process):
        for transactions in self.transaction_list:
            if (transactions.id == process.transaction_id):
                return True
        
        return False

    def find_transaction(self, transaction_id: int):
        for transaction in self.transaction_list:
            if (transaction.id == transaction_id):
                return transaction

        return None

    def run(self, process: Process):
        started = self.check_started(process)
        
        if (not started):
            print(f'[{process}] Starting transaction {process.transaction_id} on timestamp = {self.timestamp}')
            self.transaction_list.append(Transaction(process.transaction_id))

        success = False

        current_transaction = self.find_transaction(process.transaction_id)

        if process.action == 'R':
            print(f'[{process}] Initiating READ on data item {process.data_item} by transaction {process.transaction_id}')
            success = current_transaction.read(self.timestamp, process.data_item)

        if process.action == 'W':
            print(f'[{process}] Initiating WRITE on data item {process.data_item} by transaction {process.transaction_id}')
            success = current_transaction.write(self.timestamp, process.data_item)

        if process.action == 'C':
            print(f'[{process}] Initiating COMMIT on transaction {process.transaction_id}')
            success = current_transaction.commit(self.timestamp, self.transaction_list)
        
        for i in range(len(self.transaction_list)):
            if self.transaction_list[i].id == current_transaction.id:
                self.transaction_list[i] = current_transaction
                
        self.timestamp += 1

        for transaction in self.transaction_list:
            print(transaction)

        if (not success):
            print(f'[{process}] Transaction failed at transaction {process.transaction_id}, aborting....')
        return success


    def start(self, process_array: List[Process]):
        for process in process_array:
            print()
            self.run(process)
