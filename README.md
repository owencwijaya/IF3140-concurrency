# mbd-concurrency
A repository for concurrency simulation using Python (for IF3140 Database Management course)


## How to Run
From the root folder, run:
```
python src/main.py [path to file] [algorithm]

# example: run the test/case1.txt file with SOCC algorithm
python src/main.py test/case1.txt socc
```
where [path to file] specifies the path to the file test (check `test` folder for file test examples) and [algorithm]refers to the implemented algorithms:
- 'sloc' refers to the simple locking algorithm
- 'socc' refers to simple optimistic concurrency control
- 'mvcc' refers to multiversion concurrency control
