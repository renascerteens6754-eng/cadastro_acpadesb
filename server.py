from flask import Flask, send_from_directory
from flask_cors import CORS
from blueprints.adolescentes import adolescentes_bp
from blueprints.congregacoes import congregacoes_bp
from blueprints.criancas import criancas_bp

app = Flask(__name__, static_folder="static")
CORS(app)

# Blueprint
app.register_blueprint(adolescentes_bp, url_prefix="/adolescentes")
app.register_blueprint(congregacoes_bp, url_prefix="/congregacoes")
app.register_blueprint(criancas_bp, url_prefix="/criancas")

# Rota principal → abre o index.html correto
@app.get("/")
def home():
    return send_from_directory("static", "index.html")


# Permite acessar arquivos da pasta static (js, css, imagens, etc)
@app.get("/static/<path:filename>")
def static_files(filename):
    return send_from_directory("static", filename)


if __name__ == "__main__":
    app.run(debug=True)
