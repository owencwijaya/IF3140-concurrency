from type.process import Process
from typing import List
import copy


ABORTED = "ABORTED"
AVAILABLE = "AVAILABLE"
WAITING = "WAITING"
COMMITTED = "COMMITTED"

# diasumsikan selalu exclusive lock
class Lock:
    def __init__(self, data_item, transaction_id):
        self.data_item = data_item
        self.transaction_id = transaction_id

    def __str__(self):
        print(f'Data item {self.data_item} is being locked by transaction {self.transaction_id}')

class Transaction:
    def __init__(self, transaction_id: int, transaction_state: str, timestamp: int):
        self.id: int = transaction_id
        self.state: str = transaction_state
        self.timestamp: int = timestamp
        self.locked_items: List[str] = []
        self.blocked_processes: List[Process] = []

lock_list: List[Lock] = []
transaction_list: List[Transaction] = []
waiting_transactions: List[Transaction] = []
timestamp: int = 1


# cek apakah transaksi ini udah pernah jalan dan apakah sudah aborted / waiting
def check_waiting(process: Process):
    for transaction in transaction_list:
        if (transaction.id == process.transaction_id and (
            transaction.state == ABORTED or transaction.state == WAITING)):
            print(transaction.state == ABORTED)
            print(transaction.state == WAITING)
            transaction.blocked_processes.append(process)
            return True
    
    return False

# cek apakah transaksi udah pernah jalan sebelumnya
def check_started(process: Process):
    for transactions in transaction_list:
        if (transactions.id == process.transaction_id):
            return True
    
    return False

def find_transaction(transaction_id: int):
    for transaction in transaction_list:
        if (transaction.id == transaction_id):
            return transaction

    return None

def wound_wait(requesting: Transaction, locking: Transaction, process: Process):
    # kalo yang request mulai lebih dulu daripada yang locking, abort yang locking
    print(f'[WOUND-WAIT] Initiating wound-wait protocol')
    if (requesting.timestamp < locking.timestamp):
        requesting.state = WAITING
        locking.state = ABORTED

        if (process not in requesting.blocked_processes):
            requesting.blocked_processes.append(process)

        if (requesting not in waiting_transactions):
            waiting_transactions.append(requesting)

        if (locking in waiting_transactions):
            waiting_transactions.remove(locking) 

        print(f'[WOUND-WAIT] Aborting transaction {locking.id} due to wound-wait')
        unlock(locking.id)
    # kalo kebalikannya (requesting mulai setelah locking), kita tambahin yang request
    else:
        if (process not in requesting.blocked_processes):
            requesting.blocked_processes.append(process)
        
        requesting.state = WAITING
        if (requesting not in waiting_transactions):
            waiting_transactions.append(requesting)
        print(f'[WOUND-WAIT] Adding {process} to blocked list of transaction {requesting.id}')
        print(f'[WOUND-WAIT] Adding transaction {requesting.id} to waiting list')

# unlock semua data item yang di lock oleh transaksi ini
def unlock(locking_id: int):
    print(f'[UNLOCK] Unlocking all data items locked by transaction {locking_id}')
    for transaction in transaction_list:
        if (transaction.id == locking_id):
            # cek tiap data item yang di lock sama transaksi
            for locked_item in transaction.locked_items:
                for lock in lock_list:
                    if (lock.data_item == locked_item):
                        print(f'[UNLOCK] Releasing lock on {locked_item} by transaction {locking_id}')
                        lock_list.remove(lock)
    

    # cek apakah ada transaksi yang bisa dilanjutin setelah unlock
    print(f'[UNLOCK] {"Checking if any waiting transaction can be resumed" if len(waiting_transactions) > 0 else "No waiting transaction"}')
    for transaction in waiting_transactions:
        temp = copy.copy(transaction.blocked_processes)

        for process in transaction.blocked_processes:
            print(f'Attempting to run {process}')
            transaction.state = AVAILABLE
            run(process)


            # kalo setelah run statusnya ga waiting, boleh di-remove aja 
            if (transaction.state != WAITING):
                temp.remove(process)


        transaction.blocked_processes = temp
    # kalo semuanya berhasil dieksekusi, langsung remove transaction dari waiting list
        if (len(transaction.blocked_processes) == 0):
            print(f'[UNLOCK] Removing transaction {transaction.id} from waiting list (all operations has been executed)')
            waiting_transactions.remove(transaction)
        
def read(process: Process):
    # cek apakah ada transaksi lain yang pegang lock
    print(f'[{process}] Initiating READ on data item {process.data_item} by transaction {process.transaction_id}')
    for lock in lock_list:
        if (lock.transaction_id != process.transaction_id and lock.data_item == process.data_item):
            print(f'[CONFLICT] Lock on {process.data_item} is being held by transaction {lock.transaction_id}')
            
            current_transaction: Transaction = find_transaction(process.transaction_id)
            locking_transaction: Transaction = find_transaction(lock.transaction_id)
            wound_wait(current_transaction, locking_transaction, process)


def write(process: Process):
    print(f'[{process}] Initiating WRITE on data item {process.data_item} by transaction {process.transaction_id}')
    conflicting = False
    
    # kalo ada, cek lock tersebut
    for lock in lock_list:
        if lock.data_item == process.data_item and lock.transaction_id != process.transaction_id:
            conflicting = True
            break

    # langsung kasih lock kalo misalnya lock_list kosong / ga konflik
    if (len(lock_list) == 0 or not conflicting):
        print(f'[{process}] Locking {process.data_item} for transaction {process.transaction_id}')
        lock_list.append(Lock(process.data_item, process.transaction_id))

        # current_transaction = find_transaction(process.transaction_id)
        # current_transaction.locked_items.append(process.data_item)

        # for transaction in transaction_list:
        #     if (transaction.id == current_transaction.id):
        #         transaction_list.remove(transaction)
        #         transaction_list.append(current_transaction)

        for transaction in transaction_list:
            if (transaction.id == process.transaction_id):
                transaction.locked_items.append(process.data_item)

    
    # kalo conflicting, jalanin wound wait nya
    if (conflicting):
        print(f'[CONFLICT] Lock on {process.data_item} is being held by transaction {lock.transaction_id}')
        current_transaction: Transaction = find_transaction(process.transaction_id)
        locking_transaction: Transaction = find_transaction(lock.transaction_id)
        wound_wait(current_transaction, locking_transaction, process)

        
def commit(process: Process):
    print(f'[{process}] Committing transaction {process.transaction_id}')

    for transaction in transaction_list:
        if (transaction.id == process.transaction_id):
            transaction.state = COMMITTED

    unlock(process.transaction_id)

def run(process: Process):
    global timestamp

    waiting = check_waiting(process)
    if (not waiting):
        started = check_started(process)
        
        if (not started):
            print(f'[{process}] Starting transaction {process.transaction_id} on timestamp = {timestamp}')
            transaction_list.append(Transaction(process.transaction_id, AVAILABLE, timestamp))
            timestamp += 1

        if (process.action == 'R'):
            read(process)
        elif (process.action == 'W'):
            write(process)
        elif (process.action == 'C'):
            commit(process)
    

def simple_locking(process_array: List[Process]):
    for process in process_array:
        print()
        run(process)
