from type.process import Process
from type.SimpleLocking.lock import Lock
from type.SimpleLocking.transaction import Transaction

from typing import List
import copy


ABORTED = "ABORTED"
AVAILABLE = "AVAILABLE"
WAITING = "WAITING"
COMMITTED = "COMMITTED"

# diasumsikan selalu exclusive lock
class SimpleLockingManager:

    lock_list: List[Lock] = []
    transaction_list: List[Transaction] = []
    waiting_transactions: List[Transaction] = []
    timestamp: int = 1


# cek apakah transaksi ini udah pernah jalan dan apakah sudah aborted / waiting
    def check_waiting(self, process: Process):
        for transaction in self.transaction_list:
            if (transaction.id == process.transaction_id and (
                transaction.state == ABORTED or transaction.state == WAITING)):
                transaction.blocked_processes.append(process)
                return True
        
        return False

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

    def wound_wait(self, requesting: Transaction, locking: Transaction, process: Process):
        # kalo yang request mulai lebih dulu daripada yang locking, abort yang locking
        print(f'[WOUND-WAIT] Initiating wound-wait protocol')
        if (requesting.timestamp < locking.timestamp):
            requesting.state = WAITING
            locking.state = ABORTED

            if (process not in requesting.blocked_processes):
                requesting.blocked_processes.append(process)

            if (requesting not in self.waiting_transactions):
               self.waiting_transactions.append(requesting)

            if (locking in self.waiting_transactions):
                self.waiting_transactions.remove(locking) 

            print(f'[WOUND-WAIT] Aborting transaction {locking.id} due to wound-wait')
            self.unlock(locking.id)
        # kalo kebalikannya (requesting mulai setelah locking), kita tambahin yang request
        else:
            if (process not in requesting.blocked_processes):
                requesting.blocked_processes.append(process)
            
            requesting.state = WAITING
            if (requesting not in self.waiting_transactions):
                self.waiting_transactions.append(requesting)
            print(f'[WOUND-WAIT] Adding {process} to blocked list of transaction {requesting.id}')
            print(f'[WOUND-WAIT] Adding transaction {requesting.id} to waiting list')

    # unlock semua data item yang di lock oleh transaksi ini
    def unlock(self, locking_id: int):
        print(f'[UNLOCK] Unlocking all data items locked by transaction {locking_id}')
        for transaction in self.transaction_list:
            if (transaction.id == locking_id):
                # cek tiap data item yang di lock sama transaksi
                for locked_item in transaction.locked_items:
                    for lock in self.lock_list:
                        if (lock.data_item == locked_item):
                            print(f'[UNLOCK] Releasing lock on {locked_item} by transaction {locking_id}')
                            self.lock_list.remove(lock)
        

        # cek apakah ada transaksi yang bisa dilanjutin setelah unlock
        print(f'[UNLOCK] {"Checking if any waiting transaction can be resumed" if len(self.waiting_transactions) > 0 else "No waiting transaction"}')
        for transaction in self.waiting_transactions:
            temp = copy.copy(transaction.blocked_processes)

            for process in transaction.blocked_processes:
                print(f'Attempting to run {process}')
                transaction.state = AVAILABLE
                self.run(process)


                # kalo setelah run statusnya ga waiting, boleh di-remove aja 
                if (transaction.state != WAITING):
                    temp.remove(process)


            transaction.blocked_processes = temp
        # kalo semuanya berhasil dieksekusi, langsung remove transaction dari waiting list
            if (len(transaction.blocked_processes) == 0):
                print(f'[UNLOCK] Removing transaction {transaction.id} from waiting list (all operations has been executed)')
                self.waiting_transactions.remove(transaction)
            
    def read(self, process: Process):
        # cek apakah ada transaksi lain yang pegang lock
        print(f'[{process}] Initiating READ on data item {process.data_item} by transaction {process.transaction_id}')
        for lock in self.lock_list:
            if (lock.transaction_id != process.transaction_id and lock.data_item == process.data_item):
                print(f'[CONFLICT] Lock on {process.data_item} is being held by transaction {lock.transaction_id}')
                
                current_transaction: Transaction = self.find_transaction(process.transaction_id)
                locking_transaction: Transaction = self.find_transaction(lock.transaction_id)
                self.wound_wait(current_transaction, locking_transaction, process)


    def write(self, process: Process):
        print(f'[{process}] Initiating WRITE on data item {process.data_item} by transaction {process.transaction_id}')
        conflicting = False
        
        # kalo ada, cek lock tersebut
        for lock in self.lock_list:
            if lock.data_item == process.data_item and lock.transaction_id != process.transaction_id:
                conflicting = True
                break

        # langsung kasih lock kalo misalnya lock_list kosong / ga konflik
        if (len(self.lock_list) == 0 or not conflicting):
            print(f'[{process}] Locking {process.data_item} for transaction {process.transaction_id}')
            self.lock_list.append(Lock(process.data_item, process.transaction_id))

            for transaction in self.transaction_list:
                if (transaction.id == process.transaction_id):
                    transaction.locked_items.append(process.data_item)

        
        # kalo conflicting, jalanin wound wait nya
        if (conflicting):
            print(f'[CONFLICT] Lock on {process.data_item} is being held by transaction {lock.transaction_id}')
            current_transaction: Transaction = self.find_transaction(process.transaction_id)
            locking_transaction: Transaction = self.find_transaction(lock.transaction_id)
            self.wound_wait(current_transaction, locking_transaction, process)

            
    def commit(self, process: Process):
        print(f'[{process}] Committing transaction {process.transaction_id}')

        for transaction in self.transaction_list:
            if (transaction.id == process.transaction_id):
                transaction.state = COMMITTED

        self.unlock(process.transaction_id)

    def run(self, process: Process):
        waiting = self.check_waiting(process)
        if (not waiting):
            started = self.check_started(process)
            
            if (not started):
                print(f'[{process}] Starting transaction {process.transaction_id} on timestamp = {self.timestamp}')
                self.transaction_list.append(Transaction(process.transaction_id, AVAILABLE, self.timestamp))
                self.timestamp += 1

            if (process.action == 'R'):
                self.read(process)
            elif (process.action == 'W'):
                self.write(process)
            elif (process.action == 'C'):
                self.commit(process)
        

    def start(self, process_array: List[Process]):
        for process in process_array:
            print()
            self.run(process)
