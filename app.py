import streamlit as st
import pandas as pd
import speech_recognition as sr

st.set_page_config(page_title="Vérification Invités", page_icon="✅", layout="centered")

st.title("🎤 Vérification des invités par la voix")

uploaded_file = st.file_uploader("📁 Téléversez votre fichier CSV d'invités", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("✅ Liste chargée avec succès.")
        st.dataframe(df.head())
    except Exception as e:
        st.error(f"Erreur de chargement : {e}")
        st.stop()
else:
    st.warning("Veuillez téléverser une liste avant de continuer.")
    st.stop()

recognizer = sr.Recognizer()

def reconnaitre_nom():
    with sr.Microphone() as source:
        st.info("🎙️ Parlez maintenant...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source, phrase_time_limit=5)
    try:
        nom = recognizer.recognize_google(audio, language="fr-FR")
        return nom
    except:
        return None

if st.button("🔍 Parler pour vérifier"):
    with st.spinner("Écoute..."):
        nom = reconnaitre_nom()
        if nom:
            st.write(f"🗣️ Vous avez dit : **{nom}**")
            noms_invites = df['Nom'].str.lower().str.strip()
            if nom.lower().strip() in noms_invites.values:
                st.success(f"✅ {nom} est invité.")
            else:
                st.error(f"❌ {nom} n'est pas dans la liste.")
        else:
            st.warning("Nom non reconnu. Veuillez réessayer.")
