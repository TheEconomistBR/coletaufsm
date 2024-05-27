import sqlite3

# Conectando ao banco de dados
conn = sqlite3.connect('C:/Users/User/OneDrive/app_cesta/mercado.db')

# Criando um cursor
cursor = conn.cursor()

# Lista todas as tabelas no banco de dados
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

# Itera sobre todas as tabelas e exclui todas as linhas
for table in tables:
    cursor.execute(f"DELETE FROM {table[0]};")

# Confirma a exclusão
conn.commit()

# Fecha a conexão
conn.close()

print("Todos os dados foram excluídos do banco de dados.")
