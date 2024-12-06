from flask import Flask, jsonify
import mysql.connector
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Adiciona suporte ao CORS caso necessário

# Configuração do Banco de Dados
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "1234",
    "database": "liciteaqui"
}

# Endpoint 1: Análise geral de licitações
@app.route('/analise_licitacoes', methods=['GET'])
def analise_licitacoes():
    # Conectar ao banco de dados
    connection = mysql.connector.connect(**db_config)
    
    # Carregar dados da tabela
    query = "SELECT status_licitacao FROM licitacoes"  # Ajuste 'licitacoes' ao nome real da sua tabela
    df = pd.read_sql(query, connection)
    connection.close()

    # Cálculos das métricas
    total_licitacoes = len(df)
    total_vencida = len(df[df['status_licitacao'] == 1])
    total_derrota = len(df[df['status_licitacao'] == 2])
    porcentagem_vencida = (total_vencida / total_licitacoes * 100) if total_licitacoes > 0 else 0

    # Criar dicionário com os resultados
    stats = {
        "total_licitacoes": total_licitacoes,
        "total_vencida": total_vencida,
        "total_derrota": total_derrota,
        "porcentagem_vencida": round(porcentagem_vencida, 2)
    }
    
    return jsonify(stats)

# Endpoint 2: Análise de licitações por estado
@app.route('/analise_licitacoes_estados', methods=['GET'])
def analise_licitacoes_estados():
    # Conectar ao banco de dados
    connection = mysql.connector.connect(**db_config)
    
    # Carregar dados da tabela
    query = "SELECT estado, status_licitacao FROM licitacoes" 
    df = pd.read_sql(query, connection)
    connection.close()

    # Calcular licitações ganhas e perdidas por estado
    estados_licitacoes = (
        df.groupby(['estado', 'status_licitacao'])
        .size()
        .unstack(fill_value=0)
        .reset_index()
        .rename(columns={1: 'total_vencida', 2: 'total_derrota'})
    )

    # Converter para dicionário
    resultados = estados_licitacoes.to_dict(orient='records')
    
    return jsonify(resultados)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
