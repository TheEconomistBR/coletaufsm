from flask import Flask, render_template, request, redirect, url_for, Response
import csv
import io
import sqlite3
import os

app = Flask(__name__)

# Função para conectar ao banco de dados
def get_db_connection():
    conn = sqlite3.connect('banco_de_dados/mercado.db')
    conn.row_factory = sqlite3.Row
    return conn
    

# Função para inicializar o banco de dados
def init_db():
    if not os.path.exists('banco_de_dados/mercado.db'):
        conn = get_db_connection()
        conn.execute('''
        CREATE TABLE IF NOT EXISTS supermercados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL
        )
        ''')
        conn.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            tipo_cesta TEXT NOT NULL
        )
        ''')
        conn.execute('''
        CREATE TABLE IF NOT EXISTS preco_produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER,
            preco REAL NOT NULL,
            supermercado_id INTEGER,
            data_coleta DATE NOT NULL,
            FOREIGN KEY (produto_id) REFERENCES produtos(id),
            FOREIGN KEY (supermercado_id) REFERENCES supermercados(id)
        )
        ''')

        # Inserir supermercados
        supermercados = ['Supermercado {}'.format(i) for i in range(1, 11)]
        for supermercado in supermercados:
            conn.execute('INSERT INTO supermercados (nome) VALUES (?)', (supermercado,))

        # Inserir produtos para CBPM
        produtos_cbpm = ['Açúcar kg', 'Arroz kg', 'Banana kg', 'Batata kg', 'Café kg', 'Carne kg', 'FarTrigo kg', 
                        'Feijão kg', 'Leite lt', 'Margarina kg', 'Pão kg', 'Óleo lt', 'Tomate kg']
        for produto in produtos_cbpm:
            conn.execute('INSERT INTO produtos (nome, tipo_cesta) VALUES (?, ?)', (produto, 'CBPM'))

        # Inserir produtos para CIPM (adicionar produtos conforme necessário)
        produtos_cipm = ['𝐴𝑖𝑝𝑖𝑚 4.8 (1kg)', 'Alface 20.8 (1kg)', 'Alho 0.5 (100g)','Banana 16.5 (1kg)', 'Batata Doce 2.4(1kg)', 'Cebola 3.1 (1kg)', 'Cenoura 1.8 (1kg)',
                          'Couve 0.8 (maço)', 'Laranja² 5.3 (1kg)', 'Ovos³ 3.8 (1dz)', 'Repolho 2.0 (1unid)', 'Tomate4 3.5 (1kg)', 'Açucar 10.1 (kg)', 'Feijão 3.9 (1kg)',
                           'Arroz 9.4 (1kg)', 'Biscoito5 1.6 (1kg)', 'Café Moído 0.4 (500g)', '𝐶𝑎𝑓é 𝑆𝑜𝑙ú𝑣𝑒𝑙 2.6(unid 50g)', 'Caldo de Galinha 6.8 (unid)', 'Erva Mate 2.8 (1kg)',
                            'Far de Milho 4.8 (1kg)', 'Far de Trigo 17.6 (1kg)', '𝐹𝑒𝑟𝑚𝑒𝑛𝑡𝑜 de Pão 1 (unid)', 'Leite 𝑒𝑚 𝑃ó 1.1 (400g)', '𝐴𝑚𝑖𝑑𝑜 de Milho 0.8 (500g)', 'Margarina 1.6 (500g)',
                            'Massa com Ovos 3.1 (500g)', 'Extrato de Tomate 2.7 (300g)', 'Óleo de Soja 4.8 (900ml)', 'Pão Francês 1.5 (1kg)', 'Pó de Galinha 1.9 (unid)', 'Regrigerante de Cola6 5 (2 litros)',
                            'Sal de Cozinha 2 (kg)', 'Vinagre de Álcool 1.9 (750ml)', 'Açúcar Mascavo 0.8 (500g)', 'Banha de Porco 0.6 (1kg)', 'Carne Bovina 9.2 (1kg)', 'Carne de Frango7 7.4 (1kg)', 'Carne Suína8 3.1 (1kg)',
                            'Leite 15.6 (1litro)', 'Queijo Colonial 1.8 (1kg)', 'Ap. de Barbear 2.1 (2unid)', 'Papel Higiênico9 1(4unid)', 'Creme Dental 3.4 (90g)', 'Sabonete 4.5 (150g)', 'Xampú 1.7 (unid)'] 
         # Adicionar produtos do CIPM aqui
        for produto in produtos_cipm:
            conn.execute('INSERT INTO produtos (nome, tipo_cesta) VALUES (?, ?)', (produto, 'CIPM'))

        conn.commit()
        conn.close()

@app.route('/')
def index():
    return render_template('index.html')        

# Rota para a página inicial com o formulário
@app.route('/cbpm', methods=['GET', 'POST'])
def cbpm():
    conn = get_db_connection()
    supermercados = conn.execute('SELECT * FROM supermercados').fetchall()
    produtos_cbpm = conn.execute("SELECT * FROM produtos WHERE tipo_cesta='CBPM'").fetchall()

    if request.method == 'POST':
        produto_id = request.form['produto']
        preco = request.form['preco']
        supermercado_id = request.form['supermercado']
        data_coleta = request.form['data_coleta']

        conn.execute('''
        INSERT INTO preco_produtos (produto_id, preco, supermercado_id, data_coleta)
        VALUES (?, ?, ?, ?)
        ''', (produto_id, preco, supermercado_id, data_coleta))
        conn.commit()
        conn.close()

        return redirect(url_for('view_data'))

    conn.close()
    return render_template('cbpm.html', supermercados=supermercados, produtos=produtos_cbpm)


# Rota para visualizar os dados com filtro
@app.route('/view', methods=['GET', 'POST'])
def view_data():
    conn = get_db_connection()
    supermercados = conn.execute('SELECT * FROM supermercados').fetchall()

    query = '''
    SELECT pp.id, s.nome AS supermercado, p.nome AS produto, pp.preco, pp.data_coleta
    FROM preco_produtos pp
    JOIN supermercados s ON pp.supermercado_id = s.id
    JOIN produtos p ON pp.produto_id = p.id
    WHERE p.tipo_cesta = 'CBPM'
    '''
    params = []

    if request.method == 'POST':
        supermercado_id = request.form.get('supermercado')
        data_coleta = request.form.get('data_coleta')

        if supermercado_id:
            query += ' AND pp.supermercado_id = ?'
            params.append(supermercado_id)

        if data_coleta:
            query += ' AND pp.data_coleta = ?'
            params.append(data_coleta)

    data = conn.execute(query, params).fetchall()
    conn.close()
    return render_template('view_data.html', data=data, supermercados=supermercados)


@app.route('/cipm', methods=['GET', 'POST'])
def cipm():
    conn = get_db_connection()
    supermercados = conn.execute('SELECT * FROM supermercados').fetchall()
    produtos_cipm = conn.execute("SELECT * FROM produtos WHERE tipo_cesta='CIPM'").fetchall()

    if request.method == 'POST':
        produto_id = request.form['produto']
        preco = request.form['preco']
        supermercado_id = request.form['supermercado']
        data_coleta = request.form['data_coleta']

        conn.execute('''
        INSERT INTO preco_produtos (produto_id, preco, supermercado_id, data_coleta)
        VALUES (?, ?, ?, ?)
        ''', (produto_id, preco, supermercado_id, data_coleta))
        conn.commit()
        conn.close()

        return redirect(url_for('view_cipm'))

    conn.close()
    return render_template('cipm.html', supermercados=supermercados, produtos=produtos_cipm)

@app.route('/view_cipm', methods=['GET', 'POST'])
def view_cipm():
    conn = get_db_connection()
    supermercados = conn.execute('SELECT * FROM supermercados').fetchall()

    query = '''
    SELECT pp.id, s.nome AS supermercado, p.nome AS produto, pp.preco, pp.data_coleta
    FROM preco_produtos pp
    JOIN supermercados s ON pp.supermercado_id = s.id
    JOIN produtos p ON pp.produto_id = p.id
    WHERE p.tipo_cesta = 'CIPM'
    '''
    params = []

    if request.method == 'POST':
        supermercado_id = request.form.get('supermercado')
        data_coleta = request.form.get('data_coleta')

        if supermercado_id:
            query += ' AND pp.supermercado_id = ?'
            params.append(supermercado_id)

        if data_coleta:
            query += ' AND pp.data_coleta = ?'
            params.append(data_coleta)

    data = conn.execute(query, params).fetchall()
    conn.close()
    return render_template('view_cipm.html', data=data, supermercados=supermercados)


# Rota para baixar os dados em formato CSV
@app.route('/download_csv', methods=['POST'])
def download_csv():
    conn = get_db_connection()
    query = '''
    SELECT pp.id, s.nome AS supermercado, p.nome AS produto, pp.preco, pp.data_coleta
    FROM preco_produtos pp
    JOIN supermercados s ON pp.supermercado_id = s.id
    JOIN produtos p ON pp.produto_id = p.id
    WHERE 1=1
    '''
    params = []

    supermercado_id = request.form.get('supermercado')
    data_coleta = request.form.get('data_coleta')

    if supermercado_id:
        query += ' AND pp.supermercado_id = ?'
        params.append(supermercado_id)

    if data_coleta:
        query += ' AND pp.data_coleta = ?'
        params.append(data_coleta)

    data = conn.execute(query, params).fetchall()

    conn.close()

    # Preparando os dados para o CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Supermercado', 'Produto', 'Preço', 'Data de Coleta'])
    for row in data:
        writer.writerow([row['id'], row['supermercado'], row['produto'], row['preco'], row['data_coleta']])
    
    # Retornando o arquivo CSV como resposta
    output.seek(0)
    return Response(output, mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename=precos.csv'})



app.run(debug=True, host='0.0.0.0')