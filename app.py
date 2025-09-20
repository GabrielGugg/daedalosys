from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

# Configuração da aplicação Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///daedalosys.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Definição do Banco de Dados ---

class Cliente(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True)
    razao_social = db.Column(db.String(200), nullable=False)
    nome_fantasia = db.Column(db.String(200))
    cnpj_cpf = db.Column(db.String(20), unique=True, nullable=False)
    inscricao_estadual = db.Column(db.String(50))
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    logradouro = db.Column(db.String(200))
    numero = db.Column(db.String(10))
    bairro = db.Column(db.String(100))
    cidade = db.Column(db.String(100))
    uf = db.Column(db.String(2))
    responsavel = db.Column(db.String(100))
    data_cadastro = db.Column(db.Date, default=date.today)
    fornecedor = db.Column(db.Boolean, default=False)
    
    # Relacionamentos
    contratos = db.relationship('Contrato', backref='cliente', lazy=True)
    chamados = db.relationship('Chamado', backref='cliente', lazy=True)
    orcamentos = db.relationship('Orcamento', backref='cliente', lazy=True)
    faturamentos = db.relationship('Faturamento', backref='cliente', lazy=True)
    custos = db.relationship('Custo', backref='cliente', lazy=True)

class Contrato(db.Model):
    __tablename__ = 'contratos'
    id = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    tipo_contrato = db.Column(db.Integer)
    data_inicio = db.Column(db.Date, nullable=False)
    data_fim = db.Column(db.Date, nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    status_contrato = db.Column(db.Integer)
    
    # Relacionamentos
    faturamentos = db.relationship('Faturamento', backref='contrato', lazy=True)

class Tecnico(db.Model):
    __tablename__ = 'tecnicos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True)
    cargo = db.Column(db.String(50))
    
    # Relacionamentos
    chamados = db.relationship('Chamado', backref='tecnico', lazy=True)

class Chamado(db.Model):
    __tablename__ = 'chamados'
    id = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    id_contrato = db.Column(db.Integer, db.ForeignKey('contratos.id'), nullable=True) # Pode não ter contrato
    id_tecnico = db.Column(db.Integer, db.ForeignKey('tecnicos.id'), nullable=True) # Pode ser atribuído depois
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    prioridade = db.Column(db.Integer)
    status = db.Column(db.Integer)
    data_abertura = db.Column(db.DateTime, default=datetime.utcnow)
    data_fechamento = db.Column(db.DateTime)
    tempo_gasto = db.Column(db.Numeric(5, 2))

class Servico(db.Model):
    __tablename__ = 'servicos'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(200), nullable=False)
    preco_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    custo_base = db.Column(db.Numeric(10, 2))

class Orcamento(db.Model):
    __tablename__ = 'orcamento'
    id = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    data = db.Column(db.Date, default=date.today)
    valor_total = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.Integer)
    
    # Relacionamentos
    itens = db.relationship('OrcamentoItem', backref='orcamento', lazy=True)
    faturamentos = db.relationship('Faturamento', backref='orcamento', lazy=True)

class OrcamentoItem(db.Model):
    __tablename__ = 'orcamento_itens'
    id = db.Column(db.Integer, primary_key=True)
    id_orcamento = db.Column(db.Integer, db.ForeignKey('orcamento.id'), nullable=False)
    nome = db.Column(db.String(200), nullable=False)
    quantidade = db.Column(db.Float, nullable=False)
    valor_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    valor_total = db.Column(db.Numeric(10, 2), nullable=False)

class Faturamento(db.Model):
    __tablename__ = 'faturamentos'
    id = db.Column(db.Integer, primary_key=True)
    id_orcamento = db.Column(db.Integer, db.ForeignKey('orcamento.id'), nullable=True) # Relaciona com orcamento
    id_cliente = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    id_contrato = db.Column(db.Integer, db.ForeignKey('contratos.id'), nullable=True) # Relaciona com contratos
    data_emissao = db.Column(db.Date, default=date.today)
    data_vencimento = db.Column(db.Date, nullable=False)
    valor_total = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.Integer)

class Custo(db.Model):
    __tablename__ = 'custos'
    id = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=True) # O custo pode não ser de um cliente específico
    descricao = db.Column(db.String(200), nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    tipo = db.Column(db.Integer)
    data = db.Column(db.Date, default=date.today)

# --- Rotas da Aplicação ---

# Rota principal para exibir os chamados
@app.route('/')
def index():
    return render_template('index.html')

# --- Criação do Banco de Dados ---
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)