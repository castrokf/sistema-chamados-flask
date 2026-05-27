# Nortia

Sistema interno de atendimento e gestão de chamados.

Aplicação web desenvolvida como projeto pessoal de estudo, simulando um service desk interno para abertura, acompanhamento e gestão de solicitações de atendimento.

O projeto foi pensado para um cenário em que uma organização já possui usuários cadastrados em sua base e precisa oferecer um ambiente controlado para que essas pessoas registrem demandas, acompanhem prazos, consultem respostas e mantenham um histórico de atendimento.

Diferente de um site público aberto, este portal não permite cadastro livre. Os acessos são criados pela equipe administrativa, reforçando a ideia de um sistema interno usado por colaboradores, clientes cadastrados, alunos, setores ou usuários vinculados a uma organização.

## Demonstração Online

Aplicação publicada no Render:

```text
https://sistema-chamados-flask.onrender.com
```

Contas fictícias para testar os três perfis principais:

```text
Admin: admin@demo.com
Suporte: suporte1@demo.com
Usuário: ana.martins@demo.com
Senha: Demo@1234
```

Conta extra de suporte:

```text
suporte2@demo.com
```

Observação: por estar hospedado em um plano gratuito, o primeiro acesso pode demorar alguns segundos caso o serviço esteja em repouso.

## Ideia do Projeto

A proposta é representar uma central interna de atendimento, onde solicitações são registradas por usuários previamente cadastrados e tratadas por uma equipe de suporte.

O fluxo foi pensado assim:

1. A administração cadastra os usuários internos no portal.
2. O usuário recebe suas credenciais de acesso.
3. Após o login, ele pode abrir uma nova solicitação.
4. A solicitação recebe prioridade e prazo de atendimento.
5. A equipe de suporte visualiza as solicitações no painel interno.
6. Um atendente pode assumir, responder e alterar o status do atendimento.
7. O usuário acompanha tudo pelo próprio painel.
8. Comentários, anexos e histórico ficam registrados no chamado.

Essa escolha deixa o projeto mais próximo de um ambiente real de atendimento interno, onde controle de acesso, rastreabilidade e histórico individual são partes importantes da regra de negócio.

## Por Que Não Há Cadastro Público?

Em um portal interno, o cadastro livre poderia gerar usuários sem vínculo com a organização. Por isso, o fluxo foi ajustado para que apenas administradores criem novos acessos.

Essa decisão permite:

- identificar quem abriu cada solicitação;
- evitar cadastros externos não autorizados;
- manter histórico por usuário;
- controlar perfis de acesso;
- separar usuários comuns, suporte e administradores;
- simular melhor um ambiente corporativo, educacional ou administrativo.

Se alguém tentar acessar `/register`, será redirecionado para login com uma mensagem informando que o cadastro público está desativado.

## Funcionalidades Implementadas

- Login com senha protegida por Argon2.
- Sessão de usuário com Flask.
- Cadastro interno de usuários pelo administrador.
- Controle de acesso por perfil: usuário, suporte e administrador.
- Abertura de solicitações por usuários cadastrados.
- Definição de prioridade: baixa, média e alta.
- Cálculo automático de prazo de atendimento.
- Upload de anexos em solicitações.
- Painel do usuário para acompanhar as próprias solicitações.
- Painel da equipe para visualizar e filtrar atendimentos.
- Atribuição de responsável pelo atendimento.
- Função para suporte assumir uma solicitação.
- Atualização de status do chamado.
- Resposta administrativa.
- Comentários entre usuário e equipe.
- Histórico de movimentações por chamado.
- Indicadores de chamados abertos, em andamento, resolvidos, sem responsável e atrasados.
- Tela de gerenciamento de acessos internos.
- Recuperação de senha por token temporário.
- Proteção CSRF em formulários que alteram dados.
- Limite simples de tentativas de login por email e origem.
- Estrutura multiempresa com isolamento por organização.
- Banco configurável por `DATABASE_URL`, com suporte a PostgreSQL em produção.
- Acesso a dados por campos nomeados, como `chamado.status` e `usuario.email`.
- Armazenamento de anexos com suporte a Cloudinary para deploy gratuito.
- Base fictícia de demonstração.
- Testes automatizados com Pytest.
- Deploy online com Render.

## Perfis de Acesso

**Usuário**

Representa a pessoa cadastrada na organização. Pode abrir solicitações, acompanhar os próprios atendimentos, comentar e visualizar anexos dos chamados vinculados ao seu acesso.

**Suporte**

Representa a equipe responsável pelo atendimento. Pode visualizar chamados, assumir atendimentos, responder solicitações, alterar status e acompanhar os chamados atribuídos à própria conta.

**Administrador**

Representa a equipe com permissão de gestão. Pode criar acessos internos, alterar perfis de usuários, visualizar todos os chamados e acompanhar a operação do portal.

## Tecnologias Utilizadas

- Python
- Flask
- SQLite para desenvolvimento local
- PostgreSQL para produção
- SQLAlchemy Core
- Bootstrap
- Argon2
- Pytest
- Gunicorn
- Waitress
- Cloudinary
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
    services/
    static/
    templates/
    tests/
```

Principais partes:

- `main.py`: inicialização da aplicação Flask, registro das rotas e criação das tabelas.
- `database.py`: camada de acesso a dados com SQLAlchemy Core, compatível com SQLite local e PostgreSQL em produção.
- `services/storage.py`: camada de armazenamento de anexos, com suporte local e Cloudinary.
- `routes/`: organização das rotas de autenticação, chamados e administração.
- `templates/`: páginas HTML renderizadas pelo Flask.
- `static/`: arquivos estáticos, como CSS e logo.
- `seed_database.py`: criação da base fictícia para demonstração.
- `tests/`: testes automatizados dos fluxos principais.

## Base Fictícia de Demonstração

Para facilitar a avaliação do projeto, existe um script de seed:

```bash
python seed_database.py
```

Esse script recria a base de demonstração com:

- 1 organização fictícia.
- 1 usuário administrador.
- 2 usuários de suporte.
- 20 usuários internos fictícios.
- 30 chamados fictícios.
- Comentários de exemplo.
- Histórico de movimentações.

Essa base permite testar o sistema sem cadastrar dados manualmente.

No deploy, a variável abaixo permite criar essa base automaticamente quando o banco estiver vazio:

```text
AUTO_SEED_DEMO=true
```

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

Execute os testes com:

```bash
python -m pytest
```

Os testes cobrem:

- Renderização das páginas públicas.
- Cadastro público desativado.
- Login com senha correta.
- Login com senha incorreta.
- Recuperação e redefinição de senha.
- Bloqueio de POST sem token CSRF.
- Redirecionamento de usuário não autenticado.
- Bloqueio de acesso de usuário comum ao painel administrativo.
- Acesso de admin ao painel.
- Criação de acesso interno por administrador.
- Bloqueio de acesso a chamado de outro usuário.
- Bloqueio de acesso a chamado de outra organização.
- Criação de chamado.
- Adição de comentário.
- Atualização de status por admin.
- Suporte assumindo chamado.

Os testes usam um banco SQLite temporário e não alteram o banco fictício `chamados.db`.

## Banco de Dados

O projeto usa SQLAlchemy Core para manter a camada de dados mais preparada para crescimento.

Por padrão, em desenvolvimento local, o sistema usa SQLite:

```text
sqlite:///chamados.db
```

Em produção, configure `DATABASE_URL` com a URL do PostgreSQL:

```text
DATABASE_URL=postgresql://usuario:senha@host:porta/banco
```

URLs no formato `postgres://`, comum em algumas plataformas, também são aceitas e convertidas automaticamente para o driver correto.

## Estrutura Multiempresa

A base possui uma tabela de organizações. Usuários e chamados pertencem a uma organização por meio de `organizacao_id`.

Isso permite evoluir o projeto para um cenário SaaS ou multiempresa, onde cada empresa acessa apenas seus próprios usuários, chamados, responsáveis e indicadores.

Na versão demo, todos os dados ficam vinculados à organização fictícia `Empresa Demo`.

## Recuperação de Senha

O portal possui um fluxo de recuperação de senha por token temporário.

No ambiente de demonstração, o link de redefinição pode ser exibido na própria tela de recuperação para facilitar testes:

```text
SHOW_RESET_LINK=true
```

Em um ambiente real, mantenha `SHOW_RESET_LINK=false`. O token deveria ser enviado por email usando um serviço SMTP ou provedor transacional. A estrutura do fluxo já está preparada para isso: o token expira, só pode ser usado uma vez e redefine a senha com hash Argon2.

Além disso, o login possui limite simples de tentativas e as mensagens foram padronizadas para evitar indicar se o email existe ou não.

## Uploads em Deploy Gratuito

Hospedagens gratuitas como Render podem usar armazenamento temporário. Isso significa que arquivos salvos diretamente no disco do servidor podem ser perdidos quando o serviço reinicia.

Para evitar esse problema, o projeto agora possui uma camada de armazenamento de anexos:

- localmente, salva arquivos na pasta `uploads/`;
- em produção, se `CLOUDINARY_URL` estiver configurado, envia os anexos para Cloudinary.

Variáveis opcionais para anexos em nuvem:

```text
CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name
CLOUDINARY_FOLDER=portal-interno-atendimento
```

Sem `CLOUDINARY_URL`, o sistema continua usando armazenamento local.

## Deploy

O projeto foi preparado para deploy no Render.

Configuração utilizada:

```text
Build Command:
pip install -r requirements.txt

Start Command:
gunicorn main:app
```

Variáveis de ambiente principais:

```text
FLASK_SECRET_KEY=defina-uma-chave-secreta
DATABASE_URL=use-a-url-real-do-postgresql
AUTO_SEED_DEMO=true
SHOW_RESET_LINK=false
SESSION_COOKIE_SECURE=true
```

Variáveis opcionais para anexos no Cloudinary:

```text
CLOUDINARY_URL=use-apenas-a-url-real-gerada-pelo-cloudinary
CLOUDINARY_FOLDER=portal-interno-atendimento
```

Se você ainda não configurou o Cloudinary, deixe `CLOUDINARY_URL` sem cadastrar no Render. Não use o texto de exemplo como valor real.

O arquivo `Procfile` também informa o comando de inicialização:

```text
web: gunicorn main:app
```

## Aprendizados

Durante o desenvolvimento deste projeto, pratiquei conceitos importantes para construção de aplicações web com Python:

- Organização de uma aplicação Flask em módulos.
- Uso de Blueprints para separar responsabilidades.
- Criação e consulta de tabelas com SQLAlchemy Core.
- Configuração de banco por ambiente com suporte a PostgreSQL.
- Modelagem inicial multiempresa com isolamento por organização.
- Uso de linhas nomeadas no acesso ao banco, reduzindo dependência de índices numéricos.
- Controle de sessão de usuário.
- Autenticação com hash de senha.
- Proteção CSRF em formulários POST.
- Restrições de acesso por tipo de usuário.
- Criação de fluxo interno de acessos.
- Separação entre usuários comuns, suporte e administração.
- Upload e acesso controlado a anexos.
- Persistência de anexos em armazenamento externo para ambiente gratuito.
- Recuperação de senha com token temporário.
- Registro de histórico de eventos.
- Criação de dados fictícios para demonstração.
- Testes automatizados com Pytest.
- Preparação de aplicação Flask para deploy.
- Diferença entre ambiente local Windows e ambiente Linux de hospedagem.

## Melhorias Futuras

Algumas melhorias que podem ser feitas em versões futuras:

- Criar migrations versionadas com Alembic.
- Adicionar paginação na listagem de chamados.
- Enviar links de recuperação por email usando provedor SMTP.
- Adicionar filtros por período de abertura.
- Melhorar dashboard com gráficos.
- Adicionar logs de auditoria mais detalhados.
- Criar uma API REST para integração futura.

## Observações

- O banco `chamados.db` é criado automaticamente na primeira execução.
- O arquivo `chamados.db` não é versionado no Git.
- A pasta `uploads/` também não é versionada.
- Arquivos locais como ambiente virtual, banco de dados, uploads e caches ficam fora do repositório.
- O cadastro público está desativado.
- Novos acessos devem ser criados pelo painel administrativo.

## Status

Projeto concluído como versão de demonstração e portfólio, com aplicação online, base fictícia, autenticação, painel administrativo, criação interna de acessos, testes automatizados e instruções de execução.
