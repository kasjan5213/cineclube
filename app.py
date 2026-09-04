from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    make_response,
)
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config["SECRET_KEY"] = "troque-esta-chave-antes-de-publicar"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cineclube.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

GENEROS = [
    "Ação",
    "Aventura",
    "Comédia",
    "Drama",
    "Ficção científica",
    "Terror",
    "Animação",
    "Documentário",
    "Romance",
    "Outro",
]

STATUS_OPCOES = ["Quero assistir", "Assistindo", "Já assisti"]


class Filme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(120), nullable=False)
    diretor = db.Column(db.String(80), nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    genero = db.Column(db.String(40), nullable=False)
    status = db.Column(db.String(30), nullable=False, default="Quero assistir")
    nota = db.Column(db.Integer, nullable=True)
    sinopse = db.Column(db.Text, nullable=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Filme {self.titulo}>"


def validar_filme(dados):
    erros = []
    titulo = (dados.get("titulo") or "").strip()
    diretor = (dados.get("diretor") or "").strip()
    genero = (dados.get("genero") or "").strip()
    status = (dados.get("status") or "").strip()
    sinopse = (dados.get("sinopse") or "").strip()
    ano_bruto = (dados.get("ano") or "").strip()
    nota_bruta = (dados.get("nota") or "").strip()

    if len(titulo) < 2:
        erros.append("O título deve ter pelo menos 2 caracteres.")
    if len(diretor) < 2:
        erros.append("O nome do diretor deve ter pelo menos 2 caracteres.")

    ano = None
    try:
        ano = int(ano_bruto)
        atual = datetime.now().year
        if ano < 1888 or ano > atual + 1:
            erros.append(f"Informe um ano entre 1888 e {atual + 1}.")
    except ValueError:
        erros.append("O ano deve ser um número inteiro.")

    if genero not in GENEROS:
        erros.append("Selecione um gênero válido.")
    if status not in STATUS_OPCOES:
        erros.append("Selecione um status válido.")

    nota = None
    if nota_bruta:
        try:
            nota = int(nota_bruta)
            if nota < 0 or nota > 10:
                erros.append("A nota deve ficar entre 0 e 10.")
        except ValueError:
            erros.append("A nota deve ser um número inteiro.")

    return erros, {
        "titulo": titulo,
        "diretor": diretor,
        "ano": ano,
        "genero": genero,
        "status": status,
        "nota": nota,
        "sinopse": sinopse or None,
    }


def tema_atual():
    return request.cookies.get("tema", "claro")


def registrar_visita():
    session["visitas"] = session.get("visitas", 0) + 1
    session["ultimo_acesso"] = datetime.now().strftime("%d/%m/%Y %H:%M")


@app.context_processor
def utilidades():
    return {
        "tema": tema_atual(),
        "visitas": session.get("visitas", 0),
        "ultimo_acesso": session.get("ultimo_acesso"),
        "ultimo_filme": session.get("ultimo_filme"),
    }


@app.route("/")
def index():
    registrar_visita()
    total = Filme.query.count()
    recentes = Filme.query.order_by(Filme.id.desc()).limit(3).all()
    return render_template("index.html", total=total, recentes=recentes)


@app.route("/sobre")
def sobre():
    return render_template("sobre.html")


@app.route("/filmes")
def listar():
    busca = (request.args.get("q") or "").strip()
    consulta = Filme.query
    if busca:
        like = f"%{busca}%"
        consulta = consulta.filter(
            db.or_(Filme.titulo.ilike(like), Filme.diretor.ilike(like))
        )
    filmes = consulta.order_by(Filme.titulo.asc()).all()
    return render_template("listar.html", filmes=filmes, busca=busca)


@app.route("/filmes/<int:id>")
def detalhes(id):
    filme = Filme.query.get_or_404(id)
    session["ultimo_filme"] = filme.titulo
    return render_template("detalhes.html", filme=filme)


@app.route("/filmes/novo", methods=["GET", "POST"])
def novo():
    if request.method == "POST":
        erros, dados = validar_filme(request.form)
        if erros:
            for erro in erros:
                flash(erro, "erro")
            return render_template(
                "form.html",
                acao="Cadastrar",
                filme=dados,
                generos=GENEROS,
                status_opcoes=STATUS_OPCOES,
            )
        filme = Filme(**dados)
        db.session.add(filme)
        db.session.commit()
        flash(f'Filme "{filme.titulo}" cadastrado com sucesso.', "sucesso")
        return redirect(url_for("listar"))

    return render_template(
        "form.html",
        acao="Cadastrar",
        filme=None,
        generos=GENEROS,
        status_opcoes=STATUS_OPCOES,
    )


@app.route("/filmes/<int:id>/editar", methods=["GET", "POST"])
def editar(id):
    filme = Filme.query.get_or_404(id)
    if request.method == "POST":
        erros, dados = validar_filme(request.form)
        if erros:
            for erro in erros:
                flash(erro, "erro")
            return render_template(
                "form.html",
                acao="Salvar alterações",
                filme=dados | {"id": filme.id},
                generos=GENEROS,
                status_opcoes=STATUS_OPCOES,
            )
        filme.titulo = dados["titulo"]
        filme.diretor = dados["diretor"]
        filme.ano = dados["ano"]
        filme.genero = dados["genero"]
        filme.status = dados["status"]
        filme.nota = dados["nota"]
        filme.sinopse = dados["sinopse"]
        db.session.commit()
        flash(f'Filme "{filme.titulo}" atualizado.', "sucesso")
        return redirect(url_for("detalhes", id=filme.id))

    return render_template(
        "form.html",
        acao="Salvar alterações",
        filme=filme,
        generos=GENEROS,
        status_opcoes=STATUS_OPCOES,
    )


@app.route("/filmes/<int:id>/excluir", methods=["POST"])
def excluir(id):
    filme = Filme.query.get_or_404(id)
    titulo = filme.titulo
    db.session.delete(filme)
    db.session.commit()
    flash(f'Filme "{titulo}" removido da estante.', "sucesso")
    return redirect(url_for("listar"))


@app.route("/tema/<modo>")
def trocar_tema(modo):
    if modo not in ("claro", "escuro"):
        modo = "claro"
    destino = request.referrer or url_for("index")
    resposta = make_response(redirect(destino))
    resposta.set_cookie("tema", modo, max_age=60 * 60 * 24 * 30)
    flash(f"Tema {modo} ativado.", "sucesso")
    return resposta


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
