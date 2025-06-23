
import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

st.title("Envio de Mensagens a Parlamentares")

# Upload ou leitura local
uploaded_file = st.file_uploader("Envie a planilha de parlamentares (.csv)", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file, sep=";", encoding="utf-8")
else:
    st.stop()

# Filtros
cargo_selecionado = st.selectbox("Cargo", options=sorted(df["cargo"].dropna().unique()))
partido_selecionado = st.multiselect("Partido(s)", options=sorted(df["partido"].dropna().unique()))
estado_selecionado = st.multiselect("Estado(s)", options=sorted(df["uf"].dropna().unique()))

# Filtragem
filtro = df[df["cargo"] == cargo_selecionado]
if partido_selecionado:
    filtro = filtro[filtro["partido"].isin(partido_selecionado)]
if estado_selecionado:
    filtro = filtro[filtro["uf"].isin(estado_selecionado)]

# Checkbox com parlamentares
nomes_selecionados = st.multiselect("Selecione os parlamentares", options=filtro["nome"].tolist())

# Formulário do usuário
st.subheader("Informações do Cidadão")
remetente_nome = st.text_input("Seu nome")
remetente_email = st.text_input("Seu e-mail")
senha_app = st.text_input("Senha de aplicativo do Gmail", type="password")
assunto = st.text_input("Assunto do e-mail")
mensagem_base = st.text_area("Mensagem (o nome do parlamentar será adicionado automaticamente)", height=200)

# Botão de envio
if st.button("Enviar e-mails"):
    if not all([remetente_nome, remetente_email, senha_app, assunto, mensagem_base, nomes_selecionados]):
        st.warning("Por favor, preencha todos os campos e selecione pelo menos um parlamentar.")
    else:
        enviados = 0
        for _, linha in filtro.iterrows():
            if linha["nome"] not in nomes_selecionados:
                continue
            nome_dest = linha["nome"]
            email_dest = linha["email"]
            saudacao = f"Prezado(a) {nome_dest},\n\n"
            corpo = saudacao + mensagem_base + f"\n\nAtenciosamente,\n{remetente_nome}"

            msg = MIMEMultipart()
            msg["From"] = remetente_email
            msg["To"] = email_dest
            msg["Subject"] = assunto
            msg.attach(MIMEText(corpo, "plain"))

            try:
                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                    server.login(remetente_email, senha_app)
                    server.sendmail(remetente_email, email_dest, msg.as_string())
                enviados += 1
            except Exception as e:
                st.error(f"Erro ao enviar para {nome_dest}: {str(e)}")

        st.success(f"{enviados} e-mail(s) enviados com sucesso!")
