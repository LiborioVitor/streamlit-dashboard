from sqlalchemy import create_engine, text
import pandas as pd

def criar_conexao(database):
    # cria o engine da conexao com o banco
    try:

        host = 'datasales-crm-db-serverless-prd-new-dalben.mysql.database.azure.com'
        user = "vitor.liborio"
        password = "c080bc13-e852-4dee-bed9-6ffeef171344"
        port = 3306

        # Criar a string de conexão do banco de dados
        connection_str = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"

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


def executar_sql(sql, engine):
    """
    Executa um comando SQL no banco de dados.

    Parâmetros:
    sql (str): O comando SQL a ser executado.
    engine: A conexão com o banco de dados.

    Retorna:
    None
    """
    try:
        with engine.connect() as conn:
            conn.execute(text(sql))  # Executa o comando SQL
            conn.commit()

    except Exception as error:
        print(f"Erro ao tentar executar o comando SQL: {error}")