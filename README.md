# Sistema de Chamados

Projeto pessoal de uma central de atendimento desenvolvida com Flask e SQLite.
O sistema permite cadastrar usuarios, abrir chamados, acompanhar status, atribuir responsaveis, comentar atendimentos e anexar arquivos.

## Funcionalidades

- Cadastro e login de usuarios com senha protegida por Argon2.
- Abertura de chamados com prioridade, prazo automatico e anexo opcional.
- Painel do cliente para acompanhar os proprios chamados.
- Painel da equipe para visualizar, filtrar, assumir e atualizar atendimentos.
- Controle de perfis: cliente, suporte e admin.
- Historico de movimentacoes e comentarios por chamado.
- Listagem de chamados sem responsavel, meus atendimentos e chamados atrasados.

## Tecnologias

- Python
- Flask
- SQLite
- Bootstrap
- Argon2

## Como executar localmente

1. Crie e ative um ambiente virtual:

```bash
python -m venv venv
venv\Scripts\activate
```

2. Instale as dependencias:

```bash
pip install -r requirements.txt
```

3. Configure a chave da aplicacao:

```bash
copy .env.example .env
```

4. Crie dados ficticios para demonstracao:

```bash
python seed_database.py
```

5. Execute o projeto:

```bash
python main.py
```

6. Acesse no navegador:

```text
http://127.0.0.1:5000
```

## Acessos de demonstracao

Todos os usuarios ficticios usam a senha:

```text
Demo@1234
```

Contas principais:

```text
Admin: admin@demo.com
Suporte 1: suporte1@demo.com
Suporte 2: suporte2@demo.com
```

O script `seed_database.py` recria o banco `chamados.db` com 1 admin, 2 usuarios de suporte, 20 clientes ficticios, chamados, historicos e comentarios de exemplo.

## Testes automatizados

Execute a suite de testes com:

```bash
python -m pytest
```

Os testes usam um banco SQLite temporario e nao alteram o banco ficticio `chamados.db`.

## Observacoes

- O banco `chamados.db` e criado automaticamente na primeira execucao.
- Para recriar a base ficticia a qualquer momento, execute `python seed_database.py`.
- A pasta `uploads/` tambem e criada automaticamente para anexos.
- Arquivos locais como banco de dados, ambiente virtual, uploads e backups nao devem ser versionados.
- Novos cadastros entram como `cliente`.
