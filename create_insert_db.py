import sqlite3
import pandas as pd

conn = sqlite3.connect('telephone.db')

c = conn.cursor()

print('Creating table rta_telephone...')
c.execute('DROP TABLE IF EXISTS rta_telephone')
c.execute('''CREATE TABLE rta_telephone 
          ([id] INTEGER PRIMARY KEY AUTOINCREMENT, 
          [name] TEXT, 
          [rta_tel] TEXT,
          [rtaf_tel] TEXT,
          [tot_tel] TEXT,
          [direct_tel] TEXT)
          '''
)

print('Creating table mtb29_telephone...')
c.execute('DROP TABLE IF EXISTS mtb29_telephone')
c.execute(''' CREATE TABLE mtb29_telephone
          ([id] INTEGER PRIMARY KEY AUTOINCREMENT,
          [name] TEXT,
          [position] TEXT,
          [place] TEXT,
          [phone] TEXT)
          '''
)

print('Reading rta_telephone...')
rta = pd.read_csv('rta.csv', sep=',', header=0, encoding='utf-8')
print('Inserting rta_telephone...')
rta.to_sql('rta_telephone', conn, if_exists='append', index=False)

print('Reading mtb29_telephone...')
mtb29 = pd.read_csv('md29tel.csv', sep=',', header=0, encoding='utf-8')
print('Inserting mtb29_telephone...')
mtb29.to_sql('mtb29_telephone', conn, if_exists='append', index=False)

print("Done.")


conn.close()