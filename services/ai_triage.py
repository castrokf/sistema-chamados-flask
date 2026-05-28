def texto_ticket(ticket):
    return f"{ticket.get('titulo', '')} {ticket.get('descricao', '')}".lower()


def suggest_category(ticket, messages=None):
    texto = texto_ticket(ticket)

    if any(palavra in texto for palavra in ["senha", "login", "acesso", "permiss"]):
        return "Acesso e Permissões"

    if any(palavra in texto for palavra in ["lento", "lentidão", "travando", "performance"]):
        return "Suporte de TI"

    if any(palavra in texto for palavra in ["cadastro", "alteração", "solicitação", "troca"]):
        return "Solicitações"

    return "Outros"


def suggest_priority(ticket, messages=None):
    texto = texto_ticket(ticket)

    criticas = [
        "sistema indisponível",
        "todos os usuários",
        "operação parada",
        "financeiro parado",
        "atendimento ao cliente parado",
        "paralisação",
        "critica",
        "crítica"
    ]

    altas = [
        "setor inteiro",
        "impacto direto",
        "sem alternativa",
        "urgente",
        "erro ao acessar"
    ]

    baixas = [
        "dúvida",
        "melhoria",
        "sugestão"
    ]

    if any(termo in texto for termo in criticas):
        return "Crítica"

    if any(termo in texto for termo in altas):
        return "Alta"

    if any(termo in texto for termo in baixas):
        return "Baixa"

    return "Média"


def generate_ai_triage_questions(ticket):
    texto = texto_ticket(ticket)

    if any(palavra in texto for palavra in ["senha", "login", "acesso"]):
        return [
            "Qual mensagem de erro aparece?",
            "O problema afeta apenas você ou outros usuários também?",
            "Você já tentou redefinir a senha?",
            "Pode enviar um print da tela?"
        ]

    if any(palavra in texto for palavra in ["lento", "lentidão", "travando"]):
        return [
            "Qual tela está lenta?",
            "Desde quando percebeu a lentidão?",
            "Isso acontece com todos os usuários?",
            "O problema ocorre em horários específicos?"
        ]

    return [
        "Qual alteração precisa ser feita?",
        "Quem deve ser impactado?",
        "Existe prazo?",
        "Há autorização de algum responsável?"
    ]


def generate_ai_summary(ticket, messages=None):
    categoria = suggest_category(ticket, messages)
    prioridade = suggest_priority(ticket, messages)

    return (
        f"Chamado classificado inicialmente como {categoria}. "
        f"Prioridade sugerida pela IA: {prioridade}. "
        "Resumo gerado por regras locais para agilizar a análise do suporte."
    )
