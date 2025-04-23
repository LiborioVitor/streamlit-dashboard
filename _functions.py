from sqlalchemy import create_engine, text
import pandas as pd
import json

def criar_conexao(connection, database):
    # cria o engine da conexao com o banco
    try:

        with open("credentials/db_cred.json") as db_connections_file:
            db_connections = json.load(db_connections_file)
        
        db_connections = db_connections[connection]

        # Criar a string de conexão do banco de dados
        connection_str = f"mysql+pymysql://{db_connections['user']}:{db_connections['password']}@{db_connections['host']}:{db_connections['port']}/{database}"

        # Criar o engine de conexão
        engine = create_engine(connection_str)

        # Retornar o engine
        return engine

    except Exception as error:
        print(f"Erro ao conectar ao banco de dados: {error}")


def select_para_df(sql, engine):

    try:

        with engine.connect() as conn:
            df = pd.read_sql(text(sql), conn)

        return df

    except Exception as error:
        print(f"Erro ao tentar colocar o select no df: {error}")