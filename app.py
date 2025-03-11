from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agenda.db'
db = SQLAlchemy(app)

class Compromisso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    data_hora = db.Column(db.DateTime, nullable=False)

def processar_comando(comando):
    """Interpreta comandos e cadastra compromissos."""
    try:
        # Expressão regular para capturar 'Título em DD/MM/AAAA HH:MM'
        match = re.search(r'(.+)\s+em\s+(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2})', comando)
        
        if not match:
            return "Formato inválido! Use: 'Título do compromisso em DD/MM/AAAA HH:MM'"
        
        titulo = match.group(1).strip()
        data_hora_str = match.group(2).strip()
        data_hora = datetime.strptime(data_hora_str, "%d/%m/%Y %H:%M")
        
        novo_compromisso = Compromisso(titulo=titulo, data_hora=data_hora)
        db.session.add(novo_compromisso)
        db.session.commit()
        return "Compromisso registrado com sucesso!"
    except ValueError:
        return "Erro ao interpretar a data/hora! Use o formato: DD/MM/AAAA HH:MM"
    except Exception as e:
        return f"Erro ao registrar compromisso: {str(e)}"

@app.route('/')
def index():
    compromissos = Compromisso.query.all()
    return render_template('index.html', compromissos=compromissos)

@app.route('/adicionar', methods=['POST'])
def adicionar():
    dados = request.get_json()
    resposta = processar_comando(dados['comando'])
    return jsonify({'mensagem': resposta})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)

# Frontend (index.html)
# Salvar este arquivo como templates/index.html

index_html = '''
<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agenda de Compromissos</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: url('/static/notebook-background.jpg') no-repeat center center fixed;
            background-size: cover;
            text-align: center;
            margin: 20px;
        }
        .container {
            max-width: 600px;
            background: rgba(255, 255, 255, 0.8);
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
            margin: auto;
        }
        ul {
            list-style: none;
            padding: 0;
        }
        li {
            background: #e3e3e3;
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
        }
        input, button {
            padding: 10px;
            margin: 10px 0;
            width: 80%;
        }
        button {
            background: #007bff;
            color: white;
            border: none;
            cursor: pointer;
        }
        button:hover {
            background: #0056b3;
        }
    </style>
    <script>
        function adicionarCompromisso() {
            let comando = document.getElementById("comando").value;
            fetch("/adicionar", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ comando: comando })
            })
            .then(response => response.json())
            .then(data => {
                alert(data.mensagem);
                location.reload();
            });
        }
    </script>
</head>
<body>
    <div class="container">
        <h1>Agenda de Compromissos</h1>
        <ul>
            {% for compromisso in compromissos %}
                <li>{{ compromisso.titulo }} - {{ compromisso.data_hora.strftime('%d/%m/%Y %H:%M') }}</li>
            {% endfor %}
        </ul>
        <h2>Adicionar Compromisso</h2>
        <input type="text" id="comando" placeholder="Digite o compromisso (ex: Reunião em 10/03/2025 14:00)">
        <button onclick="adicionarCompromisso()">Adicionar</button>
    </div>
</body>
</html>
'''

# Criar diretório static para armazenar imagens
static_dir = "static"
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

# Baixar e salvar imagem de fundo
import requests
img_url = "https://images.unsplash.com/photo-1524578271613-d550eacf6091"
img_path = os.path.join(static_dir, "notebook-background.jpg")
if not os.path.exists(img_path):
    img_data = requests.get(img_url).content
    with open(img_path, "wb") as img_file:
        img_file.write(img_data)

# Salvar index.html no diretório templates
templates_dir = "templates"
if not os.path.exists(templates_dir):
    os.makedirs(templates_dir)
with open(os.path.join(templates_dir, "index.html"), "w", encoding="utf-8") as f:
    f.write(index_html)
