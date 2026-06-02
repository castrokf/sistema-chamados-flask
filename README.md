# Nortia

Plataforma interna de atendimento, gestão de chamados e acompanhamento operacional.

A Nortia foi estruturada para representar um ambiente corporativo de service desk, onde usuários previamente cadastrados registram solicitações, acompanham prazos e interagem com a equipe responsável pelo atendimento. O acesso é controlado pela administração, sem cadastro público, reforçando a proposta de uso interno por organizações, setores, clientes cadastrados ou equipes de suporte.

## Ambiente Online

Aplicação publicada no Render:

```text
https://sistema-chamados-flask.onrender.com
```

Contas de acesso para avaliação dos perfis principais:

```text
Administrador: admin@nortia.internal
Suporte: marina.atendimento@nortia.internal
Usuário: ana.martins@nortia.internal
Senha: Nortia@2026
```

Conta adicional de suporte:

```text
rafael.operacoes@nortia.internal
```

Observação: por estar hospedada em plano gratuito, a primeira abertura pode levar alguns segundos quando o serviço estiver em repouso.

## Proposta

A Nortia centraliza solicitações internas em um fluxo controlado:

1. A administração cria os acessos autorizados.
2. O usuário acessa a plataforma com credenciais fornecidas pela organização.
3. O usuário abre uma solicitação com título, descrição, prioridade e anexo opcional.
4. A plataforma calcula o prazo de atendimento conforme a prioridade.
5. A equipe de suporte visualiza, filtra e assume atendimentos.
6. O responsável responde, comenta e altera o status do chamado.
7. O usuário acompanha a evolução pelo próprio painel.
8. Histórico, comentários, anexos e movimentações ficam registrados.

Esse fluxo aproxima a aplicação de uma operação corporativa real, com rastreabilidade, controle de acesso, separação por perfil e indicadores para tomada de decisão.

## Funcionalidades

- Autenticação com senha protegida por Argon2.
- Controle de sessão com Flask.
- Cadastro interno de acessos pelo administrador.
- Perfis de usuário, suporte e administrador.
- Cadastro público desativado.
- Abertura e acompanhamento de chamados.
- Prioridade baixa, média e alta.
- Cálculo automático de prazo de atendimento.
- Upload de anexos com suporte local e Cloudinary.
- Validação de extensão, MIME type, tamanho e nome seguro de anexos.
- Comentários entre usuário e equipe.
- Mensagens públicas e notas internas restritas à equipe.
- Histórico de movimentações por chamado.
- Atribuição de responsável.
- Fluxo para suporte assumir atendimento.
- Atualização de status e resposta administrativa.
- Painel administrativo com filtros.
- Painel de atendimentos atribuídos.
- Indicadores de volume, status, responsáveis e prazos.
- Gráficos operacionais concentrados em relatórios.
- Estrutura de SLA para primeira resposta, resolução e pausas.
- Central de Ajuda com artigos públicos e internos.
- Estrutura preparada para SMTP e webhooks operacionais.
- Recuperação de senha por token temporário.
- Proteção CSRF em formulários de alteração.
- Limite simples de tentativas de login.
- Estrutura multiempresa com isolamento por organização.
- Banco configurável por `DATABASE_URL`.
- Suporte a SQLite local e PostgreSQL em produção.
- Testes automatizados com Pytest.
- Deploy preparado para Render.

## Perfis

**Usuário**

Registra solicitações, acompanha os próprios atendimentos, comenta e acessa anexos dos chamados vinculados à sua conta.

**Suporte**

Visualiza chamados da organização, assume atendimentos, responde solicitações, altera status e acompanha os chamados atribuídos à própria conta.

**Administrador**

Gerencia acessos internos, altera perfis, visualiza todos os chamados, acompanha indicadores e supervisiona a operação de atendimento.

## Tecnologias

- Python
- Flask
- SQLite
- PostgreSQL
- SQLAlchemy Core
- Bootstrap
- Argon2
- Pytest
- Gunicorn
- Waitress
- Cloudinary
- Alembic
- Render

## Estrutura

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

Principais responsabilidades:

- `main.py`: inicialização da aplicação, rotas, segurança básica e criação das tabelas.
- `database.py`: acesso a dados com SQLAlchemy Core, compatível com SQLite e PostgreSQL.
- `seed_database.py`: criação da massa inicial de usuários e chamados para avaliação.
- `routes/`: autenticação, chamados, área administrativa e central de ajuda.
- `services/storage.py`: armazenamento e validação de anexos local ou via Cloudinary.
- `services/sla.py`: cálculo de prazos de primeira resposta e resolução.
- `services/email.py`: camada SMTP opcional.
- `services/notifications.py`: camada opcional de webhook.
- `migrations/`: migrações versionadas com Alembic.
- `templates/`: telas HTML renderizadas pelo Flask.
- `static/`: CSS, imagens e identidade visual.
- `tests/`: testes automatizados dos fluxos principais.

## Massa Inicial

Para criar uma base local com organização, equipe, usuários e chamados:

```bash
python seed_database.py
```

O script recria a base com:

- 1 organização.
- 1 administrador.
- 2 usuários de suporte.
- 20 usuários internos.
- 30 chamados.
- Comentários.
- Histórico de movimentações.

No Render, a variável abaixo permite criar essa base automaticamente quando o banco estiver vazio:

```text
AUTO_SEED_INITIAL_DATA=true
```

## Como Rodar Localmente

1. Clone o repositório:

```bash
git clone https://github.com/castrokf/sistema-chamados-flask.git
cd sistema-chamados-flask
```

2. Crie e ative o ambiente virtual:

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

No mínimo, mantenha uma `FLASK_SECRET_KEY` local. Em produção essa variável é obrigatória.

5. Crie a base inicial:

```bash
python seed_database.py
```

6. Execute a aplicação:

```bash
python main.py
```

7. Acesse:

```text
http://127.0.0.1:5000
```

## Windows

O `gunicorn` é indicado para ambientes Linux, como Render. No Windows, use o servidor de desenvolvimento do Flask ou Waitress:

```bash
waitress-serve --listen=127.0.0.1:5000 main:app
```

ou:

```bash
python main.py
```

## Testes

Execute:

```bash
python -m pytest
```

Os testes cobrem autenticação, recuperação de senha, proteção CSRF, permissões por perfil, isolamento por organização, criação de chamados, comentários, atualização de status, atribuição de responsável, nota interna e upload seguro.

Os testes usam SQLite temporário e não alteram o banco local `chamados.db`.

## Banco de Dados

Em desenvolvimento local, a aplicação usa SQLite por padrão:

```text
sqlite:///chamados.db
```

Em produção, configure `DATABASE_URL` com PostgreSQL:

```text
DATABASE_URL=postgresql://usuario:senha@host:porta/banco
```

URLs no formato `postgres://` também são aceitas e convertidas automaticamente para o driver usado pela aplicação.

## Migrações

O projeto agora possui estrutura Alembic para evolução versionada do banco:

```bash
alembic upgrade head
```

Para criar uma nova versão:

```bash
alembic revision -m "descricao_da_mudanca"
```

Observação: para manter compatibilidade com a versão atual e não quebrar o Render, `database.py` ainda cria/ajusta tabelas mínimas durante a inicialização. A recomendação é migrar novas mudanças de schema para `migrations/` gradualmente.

## Multiempresa

A base possui tabela de organizações. Usuários e chamados pertencem a uma organização por meio de `organizacao_id`.

Essa estrutura permite evoluir a Nortia para um cenário SaaS, onde cada empresa visualiza apenas seus próprios acessos, chamados, responsáveis e indicadores.

## Recuperação de Senha

A recuperação usa token temporário, com expiração e uso único. Para facilitar validação em ambiente controlado, o link pode aparecer na própria tela quando esta variável estiver ativa:

```text
SHOW_RESET_LINK=true
```

Em produção, mantenha:

```text
SHOW_RESET_LINK=false
```

O próximo passo natural para produção é enviar esse token por email usando SMTP ou provedor transacional.

## Uploads

Em hospedagens gratuitas, arquivos salvos no disco do servidor podem ser perdidos após reinicializações. Por isso, a aplicação possui camada de armazenamento:

- localmente, salva em `uploads/`;
- em produção, se `CLOUDINARY_URL` existir, envia para Cloudinary.

O upload valida extensão, MIME type, tamanho máximo, nome seguro e gera um identificador único para evitar sobrescrita e path traversal.

Extensões permitidas:

```text
png, jpg, jpeg, pdf, txt, doc, docx, xls, xlsx
```

Variáveis opcionais:

```text
CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name
CLOUDINARY_FOLDER=nortia-atendimentos
```

## SMTP e Webhook

A camada de email fica pronta para uso real, mas não quebra a aplicação quando SMTP não está configurado:

```text
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=
SMTP_USE_TLS=true
```

Para alertas internos via Slack, Teams, Discord ou ferramenta equivalente:

```text
WEBHOOK_URL=
```

Sem `WEBHOOK_URL`, os alertas são ignorados com log informativo.

## Deploy no Render

Configuração principal:

```text
Build Command:
pip install -r requirements.txt

Start Command:
gunicorn main:app
```

Variáveis recomendadas:

```text
FLASK_ENV=production
FLASK_SECRET_KEY=defina-uma-chave-secreta
DATABASE_URL=use-a-url-real-do-postgresql
AUTO_SEED_INITIAL_DATA=true
SHOW_RESET_LINK=false
SESSION_COOKIE_SECURE=true
```

Variáveis opcionais para anexos:

```text
CLOUDINARY_URL=use-apenas-a-url-real-gerada-pelo-cloudinary
CLOUDINARY_FOLDER=nortia-atendimentos
```

O arquivo `Procfile` também informa o comando de inicialização:

```text
web: gunicorn main:app
```

## Evolução Recomendada

- Migrar gradualmente todo o schema manual de `database.py` para migrations Alembic completas.
- Ligar envio real de email nos fluxos de recuperação de senha, atribuição e SLA.
- Adicionar paginação na listagem de chamados.
- Criar exportação CSV nos relatórios.
- Expandir logs de auditoria para todos os eventos de SLA.
- Criar API REST para integrações externas.
- Expandir configurações por empresa.

## Observações

- O banco `chamados.db` é criado automaticamente na primeira execução local.
- `chamados.db`, `uploads/`, ambiente virtual e caches não devem ser versionados.
- Em produção, a aplicação falha se `FLASK_SECRET_KEY` não estiver definida.
- O cadastro público está desativado.
- Novos acessos devem ser criados pelo painel administrativo.
- Arquivos antigos de backup soltos na raiz foram removidos do projeto local.

## Status

Versão funcional com autenticação, gestão de acessos, abertura e acompanhamento de chamados, anexos seguros, recuperação de senha, dashboard operacional, relatórios, central de ajuda, estrutura multiempresa, base de SLA, PostgreSQL em produção, testes automatizados e deploy online.
