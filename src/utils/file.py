
'''
Util file to manage test case files
'''


from type.process import Process

'''
Read test case file and return a processed array
Test case SHOULD be written in the format R1(X) or W1(X)
'''

def read(file_name: str):
    process_array = []
    data_item_array = []
    transaction_array = []

    with open(file_name) as f:
        lines = f.readlines()


    for process in lines:
        process = process.replace("(", "").replace(")", "")

        action = process[0]
        transaction_id = int(process[1])
        data_item = None

        if (process[0] != 'C'):
            data_item = process[2]

        process_array.append(Process(action, transaction_id, data_item))

        if (data_item not in data_item_array and data_item != None):
            data_item_array.append(data_item)

        if (transaction_id not in transaction_array):
            transaction_array.append(transaction_id)

    return process_array, sorted(data_item_array), sorted(transaction_array)