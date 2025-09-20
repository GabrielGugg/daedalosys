from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Configuração da aplicação Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///daedalosys.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Definição do Banco de Dados ---

# Tabela para os Chamados
class Chamado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    cliente = db.Column(db.String(100), nullable=False)
    solicitante = db.Column(db.String(100), nullable=False)
    contrato = db.Column(db.String(100), default='Avulso')
    status = db.Column(db.String(20), default='Novo')
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

# Tabela para os Registros Financeiros (Custos e Lucros)
class Financeiro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(200), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    tipo = db.Column(db.String(10), nullable=False) # 'custo' ou 'lucro'
    data_registro = db.Column(db.DateTime, default=datetime.utcnow)

# --- Rotas da Aplicação ---

# Rota principal para exibir os chamados
@app.route('/')
def index():
    return "Hello World! O sistema está funcionando!"

# --- Criação do Banco de Dados ---
# Este bloco só será executado a primeira vez que você rodar o script
# e criará o arquivo 'daedalosys.db' e as tabelas dentro dele.
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)