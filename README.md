# Sistema de Chamados

Sistema web desenvolvido como projeto pessoal de estudo, com o objetivo de simular uma central de atendimento para abertura, acompanhamento e gestão de chamados.

A ideia do projeto foi construir uma aplicação completa, indo além de telas isoladas. Durante o desenvolvimento, trabalhei com autenticação, controle de permissões, banco de dados, organização de rotas, upload de arquivos, dados fictícios para demonstração, testes automatizados e deploy online.

## Demonstração Online

Aplicação publicada no Render:

```text
https://sistema-chamados-flask.onrender.com
```

Contas para teste:

```text
Admin: admin@demo.com
Suporte 1: suporte1@demo.com
Suporte 2: suporte2@demo.com
Senha: Demo@1234
```

Observação: por estar hospedado em um plano gratuito, o primeiro acesso pode demorar alguns segundos caso o serviço esteja em repouso.

## Sobre o Projeto

Este projeto representa uma central de atendimento simples, onde clientes podem abrir chamados e uma equipe de suporte pode acompanhar, assumir e atualizar esses atendimentos.

O fluxo principal foi pensado da seguinte forma:

1. Um cliente cria uma conta no sistema.
2. O cliente abre um chamado informando título, descrição, prioridade e, se necessário, um anexo.
3. O sistema calcula um prazo de atendimento com base na prioridade.
4. Usuários da equipe de suporte ou administradores visualizam os chamados no painel administrativo.
5. A equipe pode assumir atendimentos, responder, alterar status e acompanhar comentários.
6. Cada chamado mantém um histórico das principais movimentações.

O objetivo foi praticar a construção de um sistema com regras reais de uso, separação entre perfis e uma experiência próxima de uma aplicação administrativa.

## Funcionalidades Implementadas

- Cadastro de usuários.
- Login com senha protegida por Argon2.
- Sessão de usuário com Flask.
- Controle de acesso por perfil: cliente, suporte e administrador.
- Abertura de chamados por clientes.
- Definição de prioridade: baixa, média e alta.
- Cálculo automático de prazo de atendimento.
- Upload de anexos em chamados.
- Painel do cliente para acompanhar seus próprios chamados.
- Painel administrativo para visualizar e filtrar chamados.
- Atribuição de responsável pelo atendimento.
- Função para o suporte assumir um chamado.
- Atualização de status do chamado.
- Resposta administrativa.
- Comentários entre cliente e equipe.
- Histórico de movimentações por chamado.
- Indicadores de chamados abertos, em andamento, resolvidos, sem responsável e atrasados.
- Tela de gerenciamento de usuários para administradores.
- Base fictícia de demonstração com clientes, suportes, admin, chamados, comentários e históricos.
- Testes automatizados com Pytest.
- Deploy online com Render.

## Perfis de Acesso

O sistema trabalha com três tipos de usuário.

**Cliente**

Pode abrir chamados, acompanhar os próprios atendimentos, enviar comentários e visualizar anexos dos seus chamados.

**Suporte**

Pode acessar o painel de atendimentos, assumir chamados, responder solicitações, alterar status e acompanhar chamados atribuídos à própria conta.

**Administrador**

Tem acesso ao painel administrativo completo, pode gerenciar usuários, alterar tipos de conta e acompanhar todos os chamados.

## Tecnologias Utilizadas

- Python
- Flask
- SQLite
- Bootstrap
- Argon2
- Pytest
- Gunicorn
- Waitress
- Render

## Estrutura do Projeto

```text
sistema_chamados/
    main.py
    database.py
    seed_database.py
    requirements.txt
    Procfile
    routes/
    static/
    templates/
    tests/
```

Principais partes:

- `main.py`: inicialização da aplicação Flask, registro das rotas e criação das tabelas.
- `database.py`: funções de conexão, criação de tabelas e operações no SQLite.
- `routes/`: organização das rotas de autenticação, chamados e administração.
- `templates/`: páginas HTML renderizadas pelo Flask.
- `static/`: arquivos estáticos, como CSS e logo.
- `seed_database.py`: criação da base fictícia para demonstração.
- `tests/`: testes automatizados dos fluxos principais.

## Base Fictícia de Demonstração

Para facilitar a avaliação do projeto, criei um script de seed:

```bash
python seed_database.py
```

Esse script recria o banco `chamados.db` com:

- 1 usuário administrador.
- 2 usuários de suporte.
- 20 clientes fictícios.
- 30 chamados fictícios.
- Comentários de exemplo.
- Histórico de movimentações.

Essa base ajuda quem está avaliando o projeto a testar o sistema sem precisar cadastrar dados manualmente.

No deploy, também existe a variável:

```text
AUTO_SEED_DEMO=true
```

Quando essa variável está ativa e o banco está vazio, a aplicação cria automaticamente os dados fictícios.

## Como Executar Localmente

1. Clone o repositório:

```bash
git clone https://github.com/castrokf/sistema-chamados-flask.git
cd sistema-chamados-flask
```

2. Crie e ative um ambiente virtual:

```bash
python -m venv venv
venv\Scripts\activate
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:

```bash
copy .env.example .env
```

5. Crie a base fictícia:

```bash
python seed_database.py
```

6. Execute a aplicação:

```bash
python main.py
```

7. Acesse no navegador:

```text
http://127.0.0.1:5000
```

## Servidor Local no Windows

O `gunicorn` é indicado para ambientes Linux, como Render e Railway. No Windows, ele pode falhar por depender de recursos que não existem no sistema.

Para testar com um servidor WSGI local no Windows, use:

```bash
waitress-serve --listen=127.0.0.1:5000 main:app
```

Para desenvolvimento simples, também é possível usar:

```bash
python main.py
```

## Testes Automatizados

O projeto possui testes automatizados para validar os fluxos principais da aplicação.

Execute com:

```bash
python -m pytest
```

Os testes cobrem:

- Renderização das páginas públicas.
- Cadastro de cliente.
- Login com senha correta.
- Login com senha incorreta.
- Redirecionamento de usuário não autenticado.
- Bloqueio de acesso de cliente ao painel administrativo.
- Acesso de admin ao painel.
- Bloqueio de acesso a chamado de outro cliente.
- Criação de chamado.
- Adição de comentário.
- Atualização de status por admin.
- Suporte assumindo chamado.

Os testes usam um banco SQLite temporário e não alteram o banco fictício `chamados.db`.

## Deploy

O projeto foi preparado para deploy no Render.

Configuração utilizada:

```text
Build Command:
pip install -r requirements.txt

Start Command:
gunicorn main:app
```

Variáveis de ambiente:

```text
FLASK_SECRET_KEY=defina-uma-chave-secreta
AUTO_SEED_DEMO=true
```

O arquivo `Procfile` também informa o comando de inicialização:

```text
web: gunicorn main:app
```

## Aprendizados

Durante o desenvolvimento deste projeto, pratiquei conceitos importantes para construção de aplicações web com Python:

- Organização de uma aplicação Flask em módulos.
- Uso de Blueprints para separar responsabilidades.
- Criação e consulta de tabelas com SQLite.
- Controle de sessão de usuário.
- Autenticação com hash de senha.
- Restrições de acesso por tipo de usuário.
- Criação de fluxos diferentes para cliente, suporte e administrador.
- Upload e acesso controlado a anexos.
- Registro de histórico de eventos.
- Criação de dados fictícios para demonstração.
- Testes automatizados com Pytest.
- Preparação de aplicação Flask para deploy.
- Diferença entre ambiente local Windows e ambiente Linux de hospedagem.

## Melhorias Futuras

Algumas melhorias que podem ser feitas em versões futuras:

- Migrar o banco de SQLite para PostgreSQL.
- Substituir retornos por tuplas por estruturas mais legíveis, como dicionários ou modelos.
- Adicionar paginação na listagem de chamados.
- Criar recuperação de senha.
- Adicionar confirmação por email no cadastro.
- Criar filtros por período de abertura.
- Melhorar dashboard com gráficos.
- Adicionar logs de auditoria mais detalhados.
- Separar configurações por ambiente.
- Criar uma API REST para integração futura.

## Observações

- O banco `chamados.db` é criado automaticamente na primeira execução.
- O arquivo `chamados.db` não é versionado no Git.
- A pasta `uploads/` também não é versionada.
- Arquivos locais como ambiente virtual, banco de dados, uploads e caches ficam fora do repositório.
- Novos cadastros entram inicialmente como cliente.

## Status

Projeto concluído como versão de demonstração e portfólio, com aplicação online, base fictícia, autenticação, painel administrativo, testes automatizados e instruções de execução.
