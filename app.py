from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import urllib.parse

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave-secreta-mvp-ods8'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    estoque = db.Column(db.Integer, nullable=False)

with app.app_context():
    db.create_all()
    if not Produto.query.first():
        db.session.add_all([
            Produto(nome="Martelo De Carpinteiro", categoria="Ferramentas", preco=12.50, estoque=24),
            Produto(nome="Berbequim Com Percussão", categoria="Ferramentas", preco=89.90, estoque=3),
            Produto(nome="Lanterna LED", categoria="Iluminação", preco=8.50, estoque=12)
        ])
        db.session.commit()

@app.route('/')
def catalogo():
    produtos = Produto.query.all()
    return render_template('catalogo.html', produtos=produtos)

@app.route('/carrinho')
def carrinho():
    itens = [
        {"nome": "Berbequim Com Percussão", "qtd": 1, "preco": 89.90},
        {"nome": "Martelo De Carpinteiro", "qtd": 2, "preco": 12.50}
    ]
    subtotal = sum(item['preco'] * item['qtd'] for item in itens)
    
    mensagem = "Olá! Gostaria de fazer o seguinte pedido:\n"
    for item in itens:
        mensagem += f"- {item['qtd']}x {item['nome']} (R$ {item['preco']:.2f})\n"
    mensagem += f"\nTotal: R$ {subtotal:.2f}"
    
    whatsapp_url = f"https://wa.me/5511999999999?text={urllib.parse.quote(mensagem)}"
    
    return render_template('carrinho.html', itens=itens, total=subtotal, whatsapp_url=whatsapp_url)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    alerta_mensagem = None
    if request.method == 'POST':
        nome = request.form.get('nome')
        categoria = request.form.get('categoria')
        preco = float(request.form.get('preco'))
        estoque = int(request.form.get('estoque'))
        
        novo_p = Produto(nome=nome, categoria=categoria, preco=preco, estoque=estoque)
        db.session.add(novo_p)
        db.session.commit()
        return redirect(url_for('admin'))

    produtos = Produto.query.all()
    criticos = [p for p in produtos if p.estoque <= 5]
    if criticos:
        alerta_mensagem = f"Alerta: {len(criticos)} produto(s) com stock crítico!"

    return render_template('admin.html', produtos=produtos, alerta=alerta_mensagem)

if __name__ == '__main__':
    app.run(debug=True)