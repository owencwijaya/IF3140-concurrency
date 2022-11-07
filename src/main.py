from utils import file

import sys


def main():
    sys.path.append("/")
    process_array, data_item_array, transaction_array = file.read('case1.txt')
    print(process_array)
    print(data_item_array)
    print(transaction_array)

main()