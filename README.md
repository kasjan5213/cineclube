# CineClube

Estante pessoal de filmes feita com Flask. Permite cadastrar, listar, visualizar, editar e excluir filmes, com validação no servidor, mensagens flash, cookie de tema e dados de sessão.

## Funcionalidades

- Página inicial com resumo da coleção
- Listagem com busca por título ou diretor
- Detalhes de um filme (`/filmes/<id>`)
- Cadastro e edição com GET e POST na mesma rota
- Exclusão de registro
- Tema claro/escuro salvo em cookie
- Contador de visitas e último filme visto na sessão
- Mensagens de sucesso e erro com `flash()`

## Como executar

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Abra `http://127.0.0.1:5000` no navegador.

O banco SQLite (`cineclube.db`) é criado automaticamente na primeira execução.
