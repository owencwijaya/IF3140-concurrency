from utils import file
from manager.SimpleLocking import SimpleLockingManager
from manager.Optimistic import OptimisticManager
import sys


def main():
    if (len(sys.argv) != 3):
        print('''
        Usage: python main.py [input file] [algorithm]
        
        [input file] nama file (beserta ekstensi) yang ingin dibaca
        [algorithm] mempunyai tiga opsi:
            - 'slock': algoritma Simple Locking (dengan exclusive locks)
            - 'socc' : algoritma Simple Optimistic Concurrency Control
            - 'mvcc' : algoritma Multiversion Concurrency Control
        ''')
        return

    file_path = sys.argv[1]
    algorithm = sys.argv[2].lower()

    process_array, data_item_array, transaction_array = file.read(file_path)

    if (algorithm == "slock"):
        manager = SimpleLockingManager(process_array)
        manager.start()
    elif (algorithm == "socc"):
        manager = OptimisticManager()
        manager.start(process_array)
    else:
        print("Algoritma belum diimplementasikan :(")

main()