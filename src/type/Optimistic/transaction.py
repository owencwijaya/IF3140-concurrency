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
        if (len(self.write_set) > 0):
            self.validation_timestamp = timestamp

        if (data_item not in self.write_set):
            self.write_set.append(data_item)

        self.start_timestamp = min(self.start_timestamp, timestamp)
        return True

    def read(self, timestamp: int, data_item: str):
        if (data_item not in self.read_set):
            self.read_set.append(data_item)
        self.start_timestamp = min(self.start_timestamp, timestamp)
        return True

    def commit(self, timestamp: int, transaction_arr: List['Transaction']):
        self.finish_timestamp = timestamp

        success = False
        
        for transaction in transaction_arr:
            if (transaction.id == self.id or transaction.start_timestamp >= self.start_timestamp):
                continue
            
            # cek kondisi pertama, apakah waktu finish transaksi lain < waktu transaksi sendiri
            if (transaction.finish_timestamp < self.start_timestamp):
                success = True

            # cek kondisi kedua, apakah waktu finish transaksi lain di antara waktu start dan validasi
            # dan yang dibaca transaksi ini tidak ditulis transaksi lain
            if (not(success) and self.start_timestamp < transaction.finish_timestamp < self.validation_timestamp
            and set(self.read_set).isdisjoint(transaction.write_set)):
                success = True

            if (not success):
                break

        return success
    
    def __str__(self):
        return f'T{self.id} ({self.read_set} {self.write_set})'

            

