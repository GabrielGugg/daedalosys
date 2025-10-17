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

# Rota para exibir o formulário de cadastro de cliente e processar os dados
@app.route('/clientes/novo', methods=['GET', 'POST'])
def novo_cliente():
    if request.method == 'POST':
        # Pegar os dados do formulário
        razao_social = request.form['razao_social']
        nome_fantasia = request.form['nome_fantasia']
        cnpj_cpf = request.form['cnpj_cpf']
        inscricao_estadual = request.form['inscricao_estadual']
        telefone = request.form['telefone']
        email = request.form['email']
        logradouro = request.form['logradouro']
        numero = request.form['numero']
        bairro = request.form['bairro']
        cidade = request.form['cidade']
        uf = request.form['uf']
        responsavel = request.form['responsavel']
        fornecedor = 'fornecedor' in request.form # Retorna True ou False se a caixa estiver marcada

        # Criar um novo objeto Cliente com os dados
        novo_cliente_db = Cliente(
            razao_social=razao_social,
            nome_fantasia=nome_fantasia,
            cnpj_cpf=cnpj_cpf,
            inscricao_estadual=inscricao_estadual,
            telefone=telefone,
            email=email,
            logradouro=logradouro,
            numero=numero,
            bairro=bairro,
            cidade=cidade,
            uf=uf,
            responsavel=responsavel,
            fornecedor=fornecedor
        )

        # Adicionar ao banco de dados e salvar
        db.session.add(novo_cliente_db)
        db.session.commit()

        # Redirecionar para a página principal após o cadastro
        return redirect(url_for('index'))

    # Se o método for GET, renderizar a página do formulário
    return render_template('cliente_cadastro.html')

# Rota para exibir a lista de clientes
@app.route('/clientes/lista')
def lista_clientes():
    clientes = Cliente.query.order_by(Cliente.razao_social).all()
    return render_template('cliente_lista.html', clientes=clientes)

# Rota para editar um cliente existente
@app.route('/clientes/editar/<int:id>', methods=['GET', 'POST'])
def editar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    if request.method == 'POST':
        cliente.razao_social = request.form['razao_social']
        cliente.nome_fantasia = request.form['nome_fantasia']
        cliente.cnpj_cpf = request.form['cnpj_cpf']
        cliente.inscricao_estadual = request.form['inscricao_estadual']
        cliente.telefone = request.form['telefone']
        cliente.email = request.form['email']
        cliente.logradouro = request.form['logradouro']
        cliente.numero = request.form['numero']
        cliente.bairro = request.form['bairro']
        cliente.cidade = request.form['cidade']
        cliente.uf = request.form['uf']
        cliente.responsavel = request.form['responsavel']
        cliente.fornecedor = 'fornecedor' in request.form
        
        db.session.commit()
        return redirect(url_for('lista_clientes'))
    
    return render_template('cliente_editar.html', cliente=cliente)

# Rota para excluir um cliente
@app.route('/clientes/excluir/<int:id>', methods=['GET', 'POST'])
def excluir_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    db.session.delete(cliente)
    db.session.commit()
    return redirect(url_for('lista_clientes'))

# Rota para cadastras novo Técnico
@app.route('/tecnico/novo', methods=['GET', 'POST'])
def novo_tecnico():
    if request.method == 'POST':
        # Pegar os dados do formulário
        nome = request.form['nome']
        cpf = request.form['cpf']
        email = request.form['email']
        cargo = request.form['cargo']

        # Criar um novo objeto Tecnico com os dados
        novo_tecnico_db = Tecnico(
            nome=nome,
            cpf=cpf,
            email=email,
            cargo=cargo
        )

        # Adicionar ao banco de dados e salvar
        db.session.add(novo_tecnico_db)
        db.session.commit()

        # Redirecionar para a página principal após o cadastro
        return redirect(url_for('index'))

    # Se o método for GET, renderizar a página do formulário
    return render_template('tecnico_cadastro.html')

# Rota para exibir a lista de tecnicos
@app.route('/tecnico/lista')
def lista_tecnico():
    tecnicos = Tecnico.query.order_by(Tecnico.id).all()
    return render_template('tecnico_lista.html', tecnicos=tecnicos)

# Rota para editar um técnico existente
@app.route('/tecnico/editar/<int:id>', methods=['GET', 'POST'])
def editar_tecnico(id):
    tecnico = Tecnico.query.get_or_404(id)
    if request.method == 'POST':
        tecnico.nome = request.form['nome']
        tecnico.nome = request.form['nome']
        tecnico.cpf = request.form['cpf']
        tecnico.email = request.form['email']
        tecnico.cargo = request.form['cargo']
        
        db.session.commit()
        return redirect(url_for('lista_tecnico'))
    
    return render_template('tecnico_editar.html', tecnico=tecnico)

# Rota para excluir um tecnico
@app.route('/tecnico/excluir/<int:id>', methods=['GET', 'POST'])
def excluir_tecnico(id):
    tecnico = Tecnico.query.get_or_404(id)
    db.session.delete(tecnico)
    db.session.commit()
    return redirect(url_for('lista_tecnico'))

# Rota para exibir o formulário de cadastro de chamado
@app.route('/chamados/novo', methods=['GET', 'POST'])
def novo_chamado():
    if request.method == 'POST':
        # 1. Obter dados do formulário
        id_cliente = request.form['id_cliente']
        id_tecnico = request.form.get('id_tecnico') # Usar .get() para permitir valor nulo
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        prioridade = request.form['prioridade']
        status = request.form['status']
        # Contrato é opcional, vamos ignorar por enquanto para simplificar o início

        # 2. Criar novo objeto Chamado
        novo_chamado_db = Chamado(
            id_cliente=id_cliente,
            id_tecnico=id_tecnico if id_tecnico else None, # Salva None se o campo vier vazio
            titulo=titulo,
            descricao=descricao,
            prioridade=prioridade,
            status=status,
            # data_abertura é preenchida automaticamente
        )

        # 3. Adicionar e salvar
        db.session.add(novo_chamado_db)
        db.session.commit()

        # 4. Redirecionar para a lista de chamados (que criaremos em seguida)
        return redirect(url_for('lista_chamados')) 

    # Se for GET, busca os dados necessários para o formulário
    clientes = Cliente.query.order_by(Cliente.razao_social).all()
    tecnicos = Tecnico.query.order_by(Tecnico.nome).all()
    
    # Valores fixos para campos de seleção
    PRIORIDADES = [1, 2, 3, 4, 5] # 1 é a mais alta
    STATUS_INICIAL = {
        1: 'Aberto',
        2: 'Em Andamento',
        3: 'Aguardando Cliente'
    }

    return render_template('chamado_cadastro.html', 
                           clientes=clientes, 
                           tecnicos=tecnicos,
                           prioridades=PRIORIDADES,
                           status_opcoes=STATUS_INICIAL)

# Rota para exibir a lista de chamados
@app.route('/chamados/lista')
def lista_chamados():
    # Busca todos os chamados, ordenados do mais recente para o mais antigo
    chamados = Chamado.query.order_by(Chamado.data_abertura.desc()).all()
    
    # Mapa para traduzir o código do status (int) para o texto
    STATUS_MAP = {
        1: 'Aberto',
        2: 'Em Andamento',
        3: 'Aguardando Cliente',
        4: 'Fechado/Resolvido',
        5: 'Cancelado'
    }

    return render_template('chamado_lista.html', 
                           chamados=chamados,
                           status_map=STATUS_MAP)

# Rota para editar um chamado existente
@app.route('/chamados/editar/<int:id>', methods=['GET', 'POST'])
def editar_chamado(id):
    chamado = Chamado.query.get_or_404(id)
    clientes = Cliente.query.order_by(Cliente.razao_social).all()
    tecnicos = Tecnico.query.order_by(Tecnico.nome).all()

    # Opções para os campos de seleção
    PRIORIDADES = [1, 2, 3, 4, 5]
    STATUS_OPCOES = {
        1: 'Aberto',
        2: 'Em Andamento',
        3: 'Aguardando Cliente',
        4: 'Fechado/Resolvido',
        5: 'Cancelado'
    }

    if request.method == 'POST':
        # 1. Atualizar dados do chamado com os valores do formulário
        chamado.id_cliente = request.form['id_cliente']
        
        # O campo id_tecnico pode vir vazio, então tratamos para salvar 'None'
        id_tecnico = request.form.get('id_tecnico')
        chamado.id_tecnico = id_tecnico if id_tecnico else None
        
        chamado.titulo = request.form['titulo']
        chamado.descricao = request.form['descricao']
        chamado.prioridade = request.form['prioridade']
        
        novo_status = int(request.form['status'])
        
        # Lógica para registrar o fechamento do chamado
        if (chamado.status != 4 and novo_status == 4) or \
           (chamado.status != 5 and novo_status == 5):
            # Se o status anterior não era Fechado/Cancelado e o novo é, registra a data de fechamento
            chamado.data_fechamento = datetime.utcnow()
        elif novo_status < 4 and chamado.data_fechamento is not None:
            # Se o status foi reaberto, limpamos a data de fechamento
            chamado.data_fechamento = None
            
        chamado.status = novo_status
        
        # Tempo Gasto
        tempo_gasto_str = request.form.get('tempo_gasto', '0.0') # Pega o valor ou usa '0.0' se for nulo
        try:
            chamado.tempo_gasto = float(tempo_gasto_str)
        except ValueError:
            # Caso o valor não seja um número (Tratamento de erro simples)
            pass

        # 2. Salvar as alterações
        db.session.commit()
        return redirect(url_for('lista_chamados'))

    # Se for GET, renderizar o formulário de edição
    return render_template('chamado_editar.html', 
                           chamado=chamado, 
                           clientes=clientes, 
                           tecnicos=tecnicos,
                           prioridades=PRIORIDADES,
                           status_opcoes=STATUS_OPCOES)

# Rota para excluir um chamado
@app.route('/chamados/excluir/<int:id>', methods=['POST'])
def excluir_chamado(id):
    chamado = Chamado.query.get_or_404(id)
    db.session.delete(chamado)
    db.session.commit()
    # Redireciona de volta para a lista de chamados
    return redirect(url_for('lista_chamados'))

# --- Criação do Banco de Dados ---
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)