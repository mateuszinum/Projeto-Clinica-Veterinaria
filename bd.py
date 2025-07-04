import sqlite3
import requests

conexao = sqlite3.connect('dados.db')
cursor = conexao.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Tutores (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Nome TEXT NOT NULL,
        Telefone TEXT NOT NULL,
        CPF TEXT NOT NULL,
        Foto_Path TEXT NOT NULL
        )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Racas (
        ID INTEGER PRIMARY KEY,
        Nome TEXT NOT NULL
        )
''')


cursor.execute('''
    CREATE TABLE IF NOT EXISTS Pets (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Nome TEXT NOT NULL,
        Peso TEXT NOT NULL,     
        Raca_ID INTEGER,
        Tutor_ID INTEGER,
        FOREIGN KEY (Tutor_ID) REFERENCES Tutores(ID),
        FOREIGN KEY (Raca_ID) REFERENCES Racas(ID)
        )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Relatorios (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Descricao TEXT NOT NULL
        )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Cargos (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Nome TEXT NOT NULL
        )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Permissoes (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Nome TEXT NOT NULL           
        )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Cargos_Permissoes (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Cargo_ID INTEGER,
        Permissao_ID INTEGER,
        FOREIGN KEY (Cargo_ID) REFERENCES Cargos(ID),
        FOREIGN KEY (Permissao_ID) REFERENCES Permissoes(ID)    
        )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Perfis (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Nome TEXT NOT NULL,
        Data_Nasc TEXT NOT NULL,
        CPF TEXT NOT NULL,
        Email TEXT NOT NULL,
        Senha_Hash BLOB NOT NULL,
        Cargo_ID INTEGER,
        FOREIGN KEY (Cargo_ID) REFERENCES Cargos(ID)
        )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Consultas (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Pet_ID INTEGER,
        Perfil_Medico_ID INTEGER,       
        Relatorio_ID INTEGER,
        Data TEXT NOT NULL,
        Horario TEXT NOT NULL,
        FOREIGN KEY (Pet_ID) REFERENCES Pets(ID),
        FOREIGN KEY (Perfil_Medico_ID) REFERENCES Perfil(ID),
        FOREIGN KEY (Relatorio_ID) REFERENCES Relatorios(ID)
        )
''')

conexao.commit()

cursor.execute(f'SELECT * FROM Cargos')

cargos_bd = cursor.fetchall()

if len(cargos_bd) == 0:
    cargos = ['Recepcionista', 'Médico_Veterinário']
    for cargo in cargos:
        cursor.execute('INSERT INTO Cargos (Nome) VALUES (?)', (cargo,))
    
    permissoes = ['ver_consultas', 'CRUD', 'add_diagnostico']
    for permissao in permissoes:
        cursor.execute('INSERT INTO Permissoes (Nome) VALUES (?)', (permissao,))
    
    cargos_permissoes = {
        'Recepcionista': ['ver_consultas', 'CRUD'],
        'Médico_Veterinário': ['ver_consultas', 'add_diagnostico']
    }

    conexao.commit()

    for cargo, permissoes in cargos_permissoes.items():
        cursor.execute('SELECT ID FROM Cargos WHERE Nome = ?', (cargo,))
        resultado = cursor.fetchone()
        cargo_id = resultado[0]

        for permissao in permissoes:
            cursor.execute('SELECT ID FROM Permissoes WHERE Nome = ?', (permissao,))
            resultado = cursor.fetchone()
            permissao_id = resultado[0]

            cursor.execute(f"INSERT INTO Cargos_Permissoes (Cargo_ID, Permissao_ID) VALUES (?, ?)", (cargo_id, permissao_id))

    conexao.commit()

cursor.execute(f'SELECT * FROM Racas')

racas_bd = cursor.fetchall()

if len(racas_bd) == 0:
    url = "https://api.thedogapi.com/v1/breeds"

    headers = {
        "x-api-key": "live_hYlHEKtJYMhiNhr8VUSrnT2wwx2paGOsLQ27NbZzbBpdMHDgqhWfswD8UgOvoBpK"  # substitua pela sua chave, se tiver
    }

    response = requests.get(url, headers=headers)

    breeds = response.json()
    for breed in breeds:
        cursor.execute("INSERT INTO Racas (Nome) VALUES (?)", (breed['name'],))
        conexao.commit()

cursor.execute("DELETE FROM Pets WHERE ID = ?", (2,))
conexao.commit()