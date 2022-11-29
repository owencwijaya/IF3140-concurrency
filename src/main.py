from utils import file
from modules.SimpleLocking import simple_locking

import sys


def main():
    sys.path.append("/")
    process_array, data_item_array, transaction_array = file.read('case1.txt')

    simple_locking(process_array)

main()