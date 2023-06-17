# sqlite-to-png
Converting an sqlite3 script (containing 'CREATE TABLE' statements) into a .png graph


This simple script allows converting any SQLite script into a diagram of the different tables. The parsing of the SQLite file is done using regular expressions, so it is not necessary to provide a clean file or even an .sql or .db file. Just looking for 'CREATE TABLE' statements

