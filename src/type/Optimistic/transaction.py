from typing import List

class Transaction():
    def __init__(self, id: int):
        self.id: int = id
        self.write_set: List[str] = []
        self.read_set: List[str] = []
        self.start_timestamp: int = 10e10
        self.validation_timestamp: int = 10e10
        self.finish_timestamp: int = 10e10

    def write(self, timestamp: int, data_item: str):
        if (len(self.write_set) == 0):
            self.validation_timestamp = timestamp

        if (len(self.read_set) == 0):
            self.start_timestamp = timestamp

        if (data_item not in self.write_set):
            print(f'Transaction {self.id} writes data item {data_item}')
            print(f'Current write set = {self.write_set}')
            self.write_set.append(data_item)

        self.start_timestamp = min(self.start_timestamp, timestamp)
        return True

    def read(self, timestamp: int, data_item: str):
        if (data_item not in self.read_set):
            self.read_set.append(data_item)
        print(f'Transaction {self.id} reads data item {data_item}')
        print(f'Current read set = {self.read_set}')

        self.start_timestamp = min(self.start_timestamp, timestamp)
        return True

    def commit(self, timestamp: int, transaction_arr: List['Transaction']):
        print()
        self.finish_timestamp = timestamp
        print(f'Transaction {self.id} commits, updating finish timestamp to {timestamp}')

        fail = True

        if (len(transaction_arr) == 1 and transaction_arr[0].id == self.id):
            fail = False

        for transaction in transaction_arr:
            if (transaction.id == self.id):
                fail = False
                continue

            print(f'Comparing with transaction {transaction.id}')

            if (transaction.start_timestamp >= self.start_timestamp):
                print(f'Compared transaction starts after this transaction, no conflict')
                fail = False
                continue
            
            # cek kondisi pertama, apakah waktu finish transaksi lain < waktu transaksi sendiri
            if (transaction.finish_timestamp < self.start_timestamp):
                print(f'Compared transaction finishes before current transactionbegins, can be committed')
                fail = False
                continue
            else:
                print(f'Compared transaction finishes after current transaction begins, needs further examination')


            # cek kondisi kedua, apakah waktu finish transaksi lain di antara waktu start dan validasi
            # dan yang dibaca transaksi ini tidak ditulis transaksi lain
            if (fail and self.start_timestamp < transaction.finish_timestamp < self.validation_timestamp):
                print(f'Compared transaction finishes between current transaction start and validation')
                if (set(self.read_set).isdisjoint(transaction.write_set)):
                    print(f'Disjoint between read set and write set of compared transaction, can be committed')
                    fail = False
                    continue
                else:
                    print(f'Intersect between read set and write set of compared transaction, cannot be committed')
            else:
                print(f'Compared transaction doesn\'t finish between current transaction start timestamp and validation timestamp, cannot be committed')


            if (fail):
                break

        if (not fail):
            print(f'Successfully committed transaction {self.id}!')
        else:
            print(f'Failed to commit transaction {self.id}!')
        print()
        return not fail
    
    def __str__(self):
        return f'T{self.id} ({self.read_set} {self.write_set})'

            

