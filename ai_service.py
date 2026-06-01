import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_MODEL = 'gemini-2.5-flash'

SYSTEM_PROMPT = """
Você é o EduPlan IA, um assistente pedagógico especializado em educação brasileira.

Regras:
- Responda somente conteúdos pedagógicos.
- Use linguagem profissional, clara e aplicável em escola pública.
- Não use asteriscos.
- Não use campos entre colchetes.
- Use professor e escola reais somente na seção IDENTIFICAÇÃO. No restante do plano, escreva 'o professor' ou 'o docente', sem citar o nome próprio.
- Organize em seções curtas e bem nomeadas.
- Respeite o nível de detalhamento: Básico = direto e curto; Intermediário = equilíbrio entre detalhes e objetividade; Completo = mais detalhado, com etapas aula a aula e orientações pedagógicas.
- Distribua metodologia por aulas.
- Inclua avaliação, recursos e adaptação/inclusão.
- Destaque pontos importantes usando rótulos curtos seguidos de dois-pontos, por exemplo: PONTO IMPORTANTE: texto.
- Não invente dados sensíveis.
"""

BLOCKED_TERMS = ['jogo do brasil', 'placar', 'aposta', 'fofoca', 'futebol hoje', 'receita de bolo', 'celebridade', 'novela', 'cotação dólar', 'investimento']


def is_pedagogical_request(data):
    text = ' '.join(str(v).lower() for v in data.values())
    return not any(term in text for term in BLOCKED_TERMS)


def demo_plan(data):
    classes = int(data.get('classes_count') or 2)
    lesson_lines = []
    for i in range(1, classes + 1):
        lesson_lines.append(f'Aula {i}: desenvolver o tema com contextualização, atividade orientada, participação dos estudantes e registro final dos principais aprendizados.')
    return f'''# PLANO DE AULA

## IDENTIFICAÇÃO
Professor: {data.get('teacher') or 'Não informado'}
Escola: {data.get('school') or 'Não informada'}
Componente curricular: {data.get('subject')}
Ano/Série/Turma: {data.get('grade')}
Quantidade de aulas: {data.get('classes_count')}
Período de realização: {data.get('period') or 'A definir'}

## TEMA
{data.get('theme')}

## RESUMO PEDAGÓGICO
Este plano organiza uma sequência didática voltada ao tema informado, considerando a realidade da escola pública, o tempo disponível e a participação ativa dos estudantes.

## OBJETIVOS
- Compreender os principais conceitos relacionados ao tema.
- Aplicar os conhecimentos em situações práticas.
- Desenvolver participação, autonomia e pensamento crítico.
- Relacionar o conteúdo com situações do cotidiano.

## CONTEÚDOS
{data.get('content') or 'Conteúdos relacionados ao tema informado pelo professor.'}

## HABILIDADES
{data.get('skills') or 'Habilidades BNCC/Currículo Paulista devem ser revisadas e validadas pelo professor.'}

## METODOLOGIA / ESTRATÉGIAS / ETAPAS
Metodologia adotada: {data.get('methodology')}.
Nível de detalhamento: {data.get('detail_level')}.

{chr(10).join(lesson_lines)}

## RECURSOS DIDÁTICOS
{data.get('resources') or 'Lousa, projetor, caderno, material impresso e recursos digitais disponíveis.'}

## AVALIAÇÃO
- Participação nas atividades.
- Realização das tarefas propostas.
- Registro no caderno.
- Aplicação dos conceitos em exercícios ou produção final.
- Correção comentada e acompanhamento individual.

## ADAPTAÇÃO E INCLUSÃO
{data.get('inclusion') or 'As atividades poderão ser adaptadas com recursos visuais, mediação individual, flexibilização de tempo e apoio pedagógico conforme necessidade dos estudantes.'}

## OBSERVAÇÕES DO PROFESSOR
{data.get('notes') or 'Plano gerado como apoio pedagógico e sujeito à revisão do professor.'}
'''


def build_prompt(data):
    return f'''
{SYSTEM_PROMPT}

Crie um material pedagógico original, limpo, organizado e pronto para PDF e Word.

Dados reais:
Professor: {data.get('teacher')}
Escola: {data.get('school')}
Tipo de material: {data.get('material_type')}
Disciplina: {data.get('subject')}
Ano/Série/Turma: {data.get('grade')}
Quantidade de aulas: {data.get('classes_count')}
Período: {data.get('period')}
Tema: {data.get('theme')}
Metodologia desejada: {data.get('methodology')}
Nível de detalhamento: {data.get('detail_level')}

Atenção ao nível de detalhamento:
- Básico: responda com objetividade, evitando excesso de texto.
- Intermediário: use detalhes moderados.
- Completo: detalhe metodologia, avaliação e inclusão sem cortar a conclusão.

Conteúdos: {data.get('content')}
Habilidades/BNCC/Currículo Paulista: {data.get('skills')}
Recursos: {data.get('resources')}
Adaptação/inclusão: {data.get('inclusion')}
Observações: {data.get('notes')}

Formato obrigatório:
# PLANO DE AULA
## IDENTIFICAÇÃO
Professor:
Escola:
Componente curricular:
Ano/Série/Turma:
Quantidade de aulas:
Período de realização:

## TEMA
## RESUMO PEDAGÓGICO
## OBJETIVOS
## CONTEÚDOS
## HABILIDADES
## METODOLOGIA / ESTRATÉGIAS / ETAPAS
## RECURSOS DIDÁTICOS
## AVALIAÇÃO
## ADAPTAÇÃO E INCLUSÃO
## OBSERVAÇÕES DO PROFESSOR
'''


def generate_with_gemini(data):
    import google.generativeai as genai
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    model = genai.GenerativeModel(model_name=GEMINI_MODEL, generation_config={'temperature': 0.45, 'top_p': 0.9, 'max_output_tokens': 4096})
    response = model.generate_content(build_prompt(data))
    return response.text.replace('**', '').replace('* ', '- ')


def generate_with_ai(data):
    if not is_pedagogical_request(data):
        return 'Este assistente foi desenvolvido exclusivamente para criação de materiais pedagógicos. Reformule sua solicitação com foco educacional.'
    if not os.getenv('GEMINI_API_KEY'):
        return demo_plan(data)
    try:
        return generate_with_gemini(data)
    except Exception as e:
        return demo_plan(data) + f'\n\n## AVISO TÉCNICO\nNão foi possível conectar ao Gemini. O modo demonstração foi usado. Erro: {str(e)}'
