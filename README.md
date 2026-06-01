# EduPlan IA

## Descrição do Projeto

O EduPlan IA é uma plataforma web desenvolvida para auxiliar professores da rede pública de ensino na criação de planos de aula e materiais pedagógicos utilizando Inteligência Artificial.

O projeto foi desenvolvido como parte do Projeto de Extensão Curricularizada (PEC) do curso de Análise e Desenvolvimento de Sistemas da UNIFECAF, tendo como comunidade beneficiada uma escola pública estadual localizada no município de Vargem Grande Paulista– SP.

O sistema busca reduzir o tempo gasto pelos docentes na elaboração de planos de aula, provas, atividades e materiais pedagógicos, permitindo que o professor concentre seus esforços na prática educacional e no acompanhamento dos alunos.

---

## Objetivo

Automatizar e otimizar o processo de planejamento pedagógico por meio da Inteligência Artificial, contribuindo para a melhoria da qualidade da educação pública.

---

## Temática do Projeto

### Temática 1 – Digitalização e Automação de Processos Sociais

O projeto enquadra-se nesta temática por automatizar um processo que atualmente é realizado manualmente pelos professores: a elaboração de planos de aula e materiais educacionais.

---

## ODS Atendida

ODS 4 – Educação de Qualidade

Garantir educação inclusiva, equitativa e de qualidade, promovendo oportunidades de aprendizagem para todos.

---

## Funcionalidades

### Autenticação

* Cadastro de professores
* Login seguro
* Recuperação de senha
* Alteração de senha
* Controle de acesso

### Inteligência Artificial

* Geração automática de planos de aula
* Geração de provas
* Geração de atividades
* Geração de projetos pedagógicos
* Sugestões metodológicas

### Personalização

* Seleção da disciplina
* Ano/Série
* Quantidade de aulas
* Metodologia desejada
* Nível de detalhamento (Básico, Intermediário e Completo)

### Exportação

* PDF profissional
* Documento Word (.docx)

### Dashboard

* Histórico de materiais
* Estatísticas de uso
* Tempo economizado
* Disciplinas mais utilizadas

---

## Tecnologias Utilizadas

* Python 3.13
* Streamlit
* SQLite
* Gemini API
* ReportLab
* Python-docx
* Pandas
* Plotly

---

## Como Executar o Projeto

### Instalar dependências

```bash
pip install -r requirements.txt
```

### Executar o sistema

```bash
streamlit run app.py
```

### Acessar

```text
http://localhost:8501
```

---

## Estrutura do Projeto

```text
eduplan_ia/
│
├── app.py
├── ai_service.py
├── auth.py
├── database.py
├── pdf_utils.py
├── requirements.txt
├── README.md
├── eduplan.db
├── docx_utils.py
│
├── exports/
└── assets/
```

---

## Autor

Lucas Lopes Silva

Aluno de Análise e Desenvolvimento de Sistemas (ADS EAD)

UNIFECAF

Projeto desenvolvido para fins acadêmicos e sociais.

# Licença

Este projeto foi desenvolvido para fins acadêmicos e sociais como parte do Projeto de Extensão Curricularizada (PEC) da UNIFECAF.

O código-fonte está disponibilizado sob a licença MIT.

Copyright © 2026 Lucas Lopes Silva.