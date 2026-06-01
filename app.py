import os
import time
import base64
from pathlib import Path
import streamlit as st
import plotly.graph_objects as go
from dotenv import load_dotenv

from database import (
    init_db, create_user, get_user_by_email, get_user_by_id,
    update_user, update_password, set_reset_code, validate_reset_code,
    is_blocked, register_failed_login, reset_login_attempts,
    count_today_generations, save_generation, list_generations,
    count_all_generations, most_used_subject, weekly_counts, find_similar_generation
)
from auth import hash_password, verify_password, valid_email, strong_password, generate_code
from ai_service import generate_with_ai
from pdf_utils import generate_pdf
from docx_utils import generate_docx

load_dotenv()
DAILY_LIMIT = 10
SESSION_TIMEOUT = 30 * 60
TIME_SAVED_PER_PLAN_MIN = 42

st.set_page_config(page_title='EduPlan IA', page_icon='📘', layout='wide')
init_db()


def b64(path):
    try:
        return base64.b64encode(Path(path).read_bytes()).decode()
    except Exception:
        return ''

LOGO = b64('assets/logo.png')

st.markdown('''
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
html, body, [class*="css"] {font-family: Inter, Arial, sans-serif;}
.stApp {background: radial-gradient(circle at top left, #EBF4FF 0, #F8FAFC 35%, #F9FAFB 100%);} 
.block-container {padding-top:0.6rem; max-width:1200px;}
[data-testid="stHeader"]{display:none!important;}
[data-testid="stToolbar"]{display:none!important;}
#MainMenu{visibility:hidden;} footer{visibility:hidden;}

h1,h2,h3,p,label,span,div {color:#0F172A;}
.logo-wrap img{width:330px;max-width:100%;height:auto;display:block;margin:0 0 16px 0;}
.sidebar-logo img{width:250px;max-width:100%;height:auto;display:block;margin:0 auto 16px auto;}
.hero{background:linear-gradient(135deg,#0B1220 0%,#1E3A8A 55%,#2563EB 100%);border-radius:30px;padding:34px;margin-bottom:22px;box-shadow:0 22px 48px rgba(30,58,138,.22);position:relative;overflow:hidden;}
.hero:after{content:"";position:absolute;right:-80px;top:-80px;width:220px;height:220px;background:rgba(56,189,248,.22);border-radius:999px;}
.hero h1{color:white!important;font-size:38px;line-height:1.08;margin:0;font-weight:900;letter-spacing:-.04em;}
.hero p{color:#DBEAFE!important;font-size:15px;margin-top:12px;max-width:780px;line-height:1.6;}
.glass-card{background:rgba(255,255,255,.92);border:1px solid #E2E8F0;border-radius:26px;padding:26px;box-shadow:0 16px 35px rgba(15,23,42,.06);margin-bottom:18px;}
.soft-card{background:#FFFFFF;border:1px solid #E5E7EB;border-radius:22px;padding:22px;box-shadow:0 10px 24px rgba(15,23,42,.045);margin-bottom:16px;}
.muted{color:#64748B!important;line-height:1.65;font-size:14px;}
.badge{display:inline-block;background:#DBEAFE;color:#1E3A8A!important;border:1px solid #BFDBFE;border-radius:999px;padding:7px 12px;font-weight:700;font-size:12px;margin-bottom:10px;}
.footer{text-align:center;font-size:12px;color:#64748B!important;border-top:1px solid #E5E7EB;padding:16px;margin-top:28px;}
.stTextInput input,.stTextArea textarea,.stNumberInput input{background:#FFFFFF!important;color:#111827!important;border:1px solid #CBD5E1!important;border-radius:14px!important;caret-color:#2563EB!important;box-shadow:none!important;}
.stTextInput input:focus,.stTextArea textarea:focus,.stNumberInput input:focus{border-color:#2563EB!important;box-shadow:0 0 0 3px rgba(37,99,235,.13)!important;}
div[data-baseweb="select"] > div{background:#FFFFFF!important;color:#111827!important;border:1px solid #CBD5E1!important;border-radius:14px!important;}
div[data-baseweb="popover"] ul, div[data-baseweb="popover"] li, div[data-baseweb="popover"] div{background:#FFFFFF!important;color:#111827!important;}
.stButton>button{border-radius:14px;font-weight:800;background:#2563EB;color:white;border:0;min-height:42px;box-shadow:0 10px 18px rgba(37,99,235,.18);}
.stButton>button:hover{background:#1D4ED8;color:white;}
.stDownloadButton>button{border-radius:14px;font-weight:800;background:#16A34A;color:white;border:0;min-height:42px;box-shadow:0 10px 18px rgba(22,163,74,.16);}
[data-testid="stSidebar"]{background:#FFFFFF;border-right:1px solid #E5E7EB;box-shadow:6px 0 30px rgba(15,23,42,.04);}
[data-testid="stSidebar"] *{color:#111827!important;}
[data-testid="stSidebar"] .stButton>button{background:#F8FAFC!important;color:#111827!important;border:1px solid #E5E7EB!important;box-shadow:none!important}[data-testid="stSidebar"] .stButton>button:hover{background:#EFF6FF!important;color:#1E3A8A!important;border-color:#BFDBFE!important}
[data-testid="stMetric"]{background:white;border:1px solid #E5E7EB;border-radius:22px;padding:18px;box-shadow:0 10px 22px rgba(15,23,42,.045);}
[data-testid="stMetric"] label{color:#64748B!important;font-weight:600!important;}
</style>
''', unsafe_allow_html=True)

if 'user_id' not in st.session_state: st.session_state.user_id = None
if 'page' not in st.session_state: st.session_state.page = 'Dashboard'
if 'generated_content' not in st.session_state: st.session_state.generated_content = ''
if 'last_activity' not in st.session_state: st.session_state.last_activity = time.time()
if 'plan_timer_running' not in st.session_state: st.session_state.plan_timer_running = False
if 'plan_active_seconds' not in st.session_state: st.session_state.plan_active_seconds = 0.0
if 'plan_last_event' not in st.session_state: st.session_state.plan_last_event = None
if 'last_plan_duration' not in st.session_state: st.session_state.last_plan_duration = None


def check_session_timeout():
    if st.session_state.user_id and time.time() - st.session_state.last_activity > SESSION_TIMEOUT:
        st.session_state.user_id = None
        st.session_state.page = 'Dashboard'
        st.session_state.generated_content = ''
        st.warning('Sua sessão expirou por segurança. Faça login novamente.')
    st.session_state.last_activity = time.time()
check_session_timeout()


def logo_html(sidebar=False):
    klass = 'sidebar-logo' if sidebar else 'logo-wrap'
    if LOGO:
        st.markdown(f'<div class="{klass}"><img src="data:image/png;base64,{LOGO}"/></div>', unsafe_allow_html=True)
    else:
        st.title('EduPlan IA')


def hero(title, subtitle):
    st.markdown(f'<div class="hero"><span class="badge">Educação pública • ODS 4</span><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)


def footer():
    st.markdown('<div class="footer">Desenvolvido por <strong>Lucas Lopes</strong> • Aluno de ADS EAD • UNIFECAF</div>', unsafe_allow_html=True)


def current_user():
    return get_user_by_id(st.session_state.user_id) if st.session_state.user_id else None


def logout():
    st.session_state.user_id = None
    st.session_state.page = 'Dashboard'
    st.session_state.generated_content = ''
    st.rerun()




def reset_plan_timer():
    st.session_state.plan_timer_running = True
    st.session_state.plan_active_seconds = 0.0
    st.session_state.plan_last_event = time.time()


def touch_plan_timer():
    if not st.session_state.get('plan_timer_running'):
        return
    now = time.time()
    last = st.session_state.get('plan_last_event') or now
    delta = now - last
    # Se o professor ficou mais de 2 minutos sem interação, considera pausa.
    if 0 <= delta <= 120:
        st.session_state.plan_active_seconds += delta
    st.session_state.plan_last_event = now


def finish_plan_timer():
    touch_plan_timer()
    duration = int(st.session_state.get('plan_active_seconds', 0))
    st.session_state.last_plan_duration = duration
    st.session_state.plan_timer_running = False
    return duration


def format_duration(seconds):
    if seconds is None:
        return '—'
    seconds = int(seconds)
    m, s = divmod(seconds, 60)
    if m <= 0:
        return f'{s}s'
    return f'{m}min {s}s'

def login_page():
    col1, col2 = st.columns([1.05, .95], gap='large')
    with col1:
        logo_html()
        hero('Planejamento pedagógico com IA', 'Crie planos de aula e materiais educacionais com rapidez, organização e foco pedagógico, mantendo a revisão final nas mãos do professor.')
        st.markdown('<div class="glass-card"><h3>Assistente para escola pública</h3><p class="muted">Ferramenta criada para reduzir burocracia, apoiar professores e fortalecer a qualidade do planejamento pedagógico.</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader('Acesso do professor')
        tab1, tab2, tab3 = st.tabs(['Entrar', 'Cadastrar', 'Recuperar senha'])
        with tab1:
            email = st.text_input('E-mail', key='login_email')
            password = st.text_input('Senha', type='password', key='login_password')
            if st.button('Entrar', use_container_width=True):
                blocked, until = is_blocked(email)
                if blocked:
                    st.error(f'Muitas tentativas. Tente novamente após {until.strftime("%H:%M")}.')
                else:
                    user = get_user_by_email(email)
                    if user and verify_password(password, user['password_hash']):
                        reset_login_attempts(email)
                        st.session_state.user_id = user['id']
                        st.session_state.page = 'Dashboard'
                        st.rerun()
                    else:
                        attempts, blocked_until = register_failed_login(email)
                        if blocked_until:
                            st.error('Login bloqueado por 5 minutos após muitas tentativas incorretas.')
                        else:
                            st.error(f'Senha incorreta ou e-mail não encontrado. Tentativa {attempts}/5.')
        with tab2:
            name = st.text_input('Nome completo', key='reg_name')
            email = st.text_input('E-mail de cadastro', key='reg_email')
            school = st.text_input('Escola', key='reg_school')
            main_subject = st.text_input('Disciplina principal', key='reg_subject')
            password = st.text_input('Senha', type='password', key='reg_pass')
            confirm = st.text_input('Confirmar senha', type='password', key='reg_confirm')
            st.caption('Senha: mínimo 8 caracteres, com letra maiúscula, minúscula e número.')
            if st.button('Criar conta', use_container_width=True):
                ok, msg = strong_password(password)
                if not name or not valid_email(email): st.error('Preencha nome e e-mail válido.')
                elif not ok: st.error(msg)
                elif password != confirm: st.error('As senhas não coincidem.')
                elif get_user_by_email(email): st.error('Este e-mail já está cadastrado.')
                else:
                    create_user(name, email, hash_password(password), school, main_subject)
                    st.success('Conta criada com sucesso. Faça login para continuar.')
        with tab3:
            st.info('Código temporário exibido na tela para o MVP acadêmico. Em produção, pode ser enviado por e-mail.')

            email = st.text_input('E-mail cadastrado', key='reset_email')

            if st.session_state.get('codigo_recuperacao'):
                st.info(f"Código gerado anteriormente: {st.session_state['codigo_recuperacao']}")

            if st.button('Gerar código de recuperação'):
                user = get_user_by_email(email)
                if not user:
                    st.error('E-mail não encontrado.')
                else:
                    code = generate_code()
                    set_reset_code(email, code)
                    st.session_state['email_recuperacao'] = email
                    st.session_state['codigo_recuperacao'] = code
                    st.success(f'Código válido por 10 minutos: {code}')

            code = st.text_input('Código recebido', key='reset_code')
            new_pass = st.text_input('Nova senha', type='password', key='reset_new_pass')
            confirm_pass = st.text_input('Confirmar nova senha', type='password', key='reset_confirm_pass')

            if st.button('Alterar senha'):
                email_recuperacao = st.session_state.get('email_recuperacao', email)
                ok, msg = strong_password(new_pass)
                user = get_user_by_email(email_recuperacao)

                if not ok:
                    st.error(msg)
                elif new_pass != confirm_pass:
                    st.error('As senhas não coincidem.')
                elif user and validate_reset_code(email_recuperacao, code):
                    update_password(user['id'], hash_password(new_pass))
                    reset_login_attempts(email_recuperacao)
                    st.session_state.pop('email_recuperacao', None)
                    st.session_state.pop('codigo_recuperacao', None)
                    st.success('Senha alterada com sucesso. Entre novamente com a nova senha.')
                else:
                    st.error('Código inválido ou expirado.')
        st.markdown('</div>', unsafe_allow_html=True)
    footer()


def sidebar():
    user = current_user()
    with st.sidebar:
        logo_html(True)
        st.markdown(f'<div class="soft-card"><b>{user["name"]}</b><br><span class="muted">Escola: {user.get("school") or "Não informada"}</span><br><span class="muted">Disciplina: {user.get("main_subject") or "Não informada"}</span></div>', unsafe_allow_html=True)
        if st.button('Dashboard', use_container_width=True):
            st.session_state.page = 'Dashboard'; st.rerun()
        if st.button('Criar material', use_container_width=True):
            st.session_state.generated_content = ''
            reset_plan_timer()
            st.session_state.page = 'Criar material'; st.rerun()
        if st.button('Histórico', use_container_width=True):
            st.session_state.page = 'Histórico'; st.rerun()
        if st.button('Perfil', use_container_width=True):
            st.session_state.page = 'Perfil'; st.rerun()
        st.divider()
        if st.button('Sair', use_container_width=True): logout()

def dashboard_page():
    user = current_user(); total = count_all_generations(user['id']); used = count_today_generations(user['id']); remaining = max(DAILY_LIMIT - used, 0)
    saved = round(total * TIME_SAVED_PER_PLAN_MIN / 60, 1); fav = most_used_subject(user['id'])
    hero(f'Bem-vindo, {user["name"].split()[0]}', 'Acompanhe seus materiais, produtividade e impacto pedagógico.')
    st.info('Gemini IA ativo' if os.getenv('GEMINI_API_KEY') else 'Modo demonstração dinâmico — configure GEMINI_API_KEY')
    c1,c2,c3,c4 = st.columns(4)
    c1.metric('Materiais gerados', total); c2.metric('Hoje', used); c3.metric('Restantes', remaining); c4.metric('Horas economizadas', saved)
    colA, colB = st.columns([.9,1.1])
    with colA:
        last_time = format_duration(st.session_state.get('last_plan_duration'))
        st.markdown(f'<div class="glass-card"><h3>Tempo do último plano</h3><p class="muted">{last_time}</p><p class="muted">O cronômetro pausa automaticamente quando não há interação por mais de 2 minutos.</p></div>', unsafe_allow_html=True)
    with colB:
        st.markdown('<div class="glass-card"><h3>Impacto estimado</h3><p class="muted">Meta do MVP: reduzir o planejamento manual de cerca de 50 minutos para poucos minutos com apoio da IA, mantendo a revisão final nas mãos do professor.</p></div>', unsafe_allow_html=True)
    if st.button('Criar novo material pedagógico', use_container_width=True):
        st.session_state.generated_content = ''
        reset_plan_timer()
        st.session_state.page = 'Criar material'; st.rerun()
    footer()


def create_page():
    user = current_user(); used = count_today_generations(user['id'])
    if not st.session_state.get('plan_timer_running') and not st.session_state.get('generated_content'):
        reset_plan_timer()
    touch_plan_timer()
    hero('Criar material pedagógico', 'Gere planos de aula com IA, revise o conteúdo e exporte em PDF ou Word.')
    if used >= DAILY_LIMIT: st.error('Você atingiu o limite diário de 10 gerações.'); footer(); return
    with st.form('plan_form'):
        st.subheader('Dados principais')
        col1,col2 = st.columns(2)
        material_type = col1.selectbox('Tipo de material', ['Plano de aula','Atividade','Prova','Trabalho','Ideias de aula','Projeto interdisciplinar'])
        subject = col2.text_input('Componente curricular', value=user.get('main_subject') or '')
        col3,col4 = st.columns(2)
        grade = col3.text_input('Ano/Série/Turma', placeholder='Ex: 6º ano A')
        classes_count = col4.number_input('Quantidade de aulas', min_value=1, max_value=30, value=2)
        period = st.text_input('Período de realização', placeholder='Ex: 03/06/2026 a 12/06/2026')
        theme = st.text_area('Tema', placeholder='Ex: Cartografia, orientação espacial e representação do espaço geográfico')
        st.subheader('Configuração pedagógica')
        col5,col6 = st.columns(2)
        methodology = col5.selectbox('Metodologia desejada', ['Metodologia ativa','Tradicional','Sala invertida','Gamificação','Aprendizagem baseada em projetos','STEAM','Debate guiado','Estudo de caso'])
        detail_level = col6.selectbox('Nível de detalhamento', ['Completo','Intermediário','Básico'])
        st.subheader('Informações pedagógicas')
        content = st.text_area('Conteúdos', placeholder='Informe os conteúdos principais.')
        skills = st.text_area('Habilidades/BNCC/Currículo Paulista', placeholder='Ex: EF06GE08, EF06GE20')
        resources = st.text_area('Recursos didáticos', placeholder='Ex: projetor, lousa, mapas impressos')
        inclusion = st.text_area('Adaptação/inclusão', placeholder='Ex: mapas ampliados, apoio visual, mediação individual')
        notes = st.text_area('Observações adicionais', placeholder='Ex: dividir em 4 aulas, incluir atividade em grupo e avaliação final')
        submitted = st.form_submit_button('Gerar com IA')
    if submitted:
        if not subject or not grade or not theme: st.error('Preencha componente curricular, série/turma e tema.')
        else:
            if find_similar_generation(user['id'], subject, grade, theme): st.warning('Já existe material semelhante no histórico.')
            data = {'teacher':user.get('name'), 'school':user.get('school'), 'material_type':material_type, 'subject':subject, 'grade':grade, 'classes_count':classes_count, 'period':period, 'theme':theme, 'methodology':methodology, 'detail_level':detail_level, 'content':content, 'skills':skills, 'resources':resources, 'inclusion':inclusion, 'notes':notes}
            with st.spinner('Gerando material pedagógico...'):
                generated = generate_with_ai(data)
            duration = finish_plan_timer()
            st.session_state.generated_content = generated; save_generation(user['id'], material_type, subject, grade, theme, generated, duration_seconds=duration); st.success(f'Material gerado com sucesso! Tempo ativo: {format_duration(duration)}')
    if st.session_state.generated_content:
        st.subheader('Revisar e editar antes de exportar')
        edited = st.text_area('Conteúdo gerado', value=st.session_state.generated_content, height=560, key='editor_content')
        st.session_state.generated_content = edited
        col1,col2 = st.columns(2)
        meta = {'teacher':user.get('name'), 'school':user.get('school'), 'subject':subject, 'grade':grade, 'theme':theme}
        with col1:
            pdf = generate_pdf(f'{subject or "Material"} - {theme or "Plano"}', edited, meta)
            with open(pdf,'rb') as f: st.download_button('Baixar PDF premium', f, file_name=Path(pdf).name, mime='application/pdf', use_container_width=True)
        with col2:
            docx = generate_docx(f'{subject or "Material"} - {theme or "Plano"}', edited, meta)
            with open(docx,'rb') as f: st.download_button('Baixar Word editável', f, file_name=Path(docx).name, mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document', use_container_width=True)
    footer()


def history_page():
    user = current_user(); hero('Histórico', 'Consulte materiais já gerados e exporte novamente.')
    rows = list_generations(user['id'])
    if not rows: st.info('Nenhum material gerado ainda.')
    for row in rows:
        with st.expander(f'{row["material_type"]} | {row["subject"]} | {row["theme"]}'):
            st.caption(f'Criado em: {row["created_at"]}'); st.markdown(row['content'])
            meta = {'teacher':user.get('name'), 'school':user.get('school'), 'subject':row['subject'], 'grade':row['grade'], 'theme':row['theme']}
            c1,c2 = st.columns(2)
            with c1:
                pdf = generate_pdf(f'{row["material_type"]} - {row["subject"]} - {row["theme"]}', row['content'], meta)
                with open(pdf,'rb') as f: st.download_button('Baixar PDF', f, file_name=Path(pdf).name, mime='application/pdf', key=f'pdf_{row["id"]}')
            with c2:
                docx = generate_docx(f'{row["material_type"]} - {row["subject"]} - {row["theme"]}', row['content'], meta)
                with open(docx,'rb') as f: st.download_button('Baixar Word', f, file_name=Path(docx).name, mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document', key=f'docx_{row["id"]}')
    footer()


def profile_page():
    user = current_user(); hero('Perfil', 'Atualize suas informações e credenciais.')
    with st.form('profile_form'):
        name = st.text_input('Nome', value=user.get('name') or '')
        school = st.text_input('Escola', value=user.get('school') or '')
        main_subject = st.text_input('Disciplina principal', value=user.get('main_subject') or '')
        submitted = st.form_submit_button('Salvar alterações')
    if submitted: update_user(user['id'], name, school, main_subject); st.success('Perfil atualizado.')
    st.divider(); st.subheader('Alterar senha')
    current = st.text_input('Senha atual', type='password')
    new_password = st.text_input('Nova senha', type='password')
    confirm = st.text_input('Confirmar nova senha', type='password')
    if st.button('Atualizar senha'):
        ok, msg = strong_password(new_password)
        if not verify_password(current, user['password_hash']): st.error('Senha atual incorreta.')
        elif not ok: st.error(msg)
        elif new_password != confirm: st.error('As senhas não coincidem.')
        else: update_password(user['id'], hash_password(new_password)); st.success('Senha atualizada.')
    footer()

if st.session_state.user_id is None:
    login_page()
else:
    sidebar()
    if st.session_state.page == 'Dashboard': dashboard_page()
    elif st.session_state.page == 'Criar material': create_page()
    elif st.session_state.page == 'Histórico': history_page()
    elif st.session_state.page == 'Perfil': profile_page()
