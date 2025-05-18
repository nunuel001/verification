import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import os

st.set_page_config(page_title="Vérification Invités", layout="centered")
st.markdown("<h1 style='text-align: center;'>🎤 Vérification vocale des invités</h1>", unsafe_allow_html=True)

# Section upload
with st.expander("📂 Téléversement de la liste des invités (.csv ou .xlsx)"):
    uploaded_file = st.file_uploader("Chargez votre fichier", type=["csv", "xlsx"])

# Chargement du fichier
if uploaded_file is not None:
    filename = uploaded_file.name
    extension = os.path.splitext(filename)[1]

    try:
        if extension == ".csv":
            df = pd.read_csv(uploaded_file)
        elif extension in [".xlsx", ".xls"]:
            df = pd.read_excel(uploaded_file)
        else:
            st.error("❌ Format de fichier non pris en charge.")
            st.stop()

        if 'Nom' not in df.columns:
            st.error("❌ Le fichier doit contenir une colonne intitulée exactement 'Nom'.")
            st.stop()

        st.success("✅ Liste chargée. Utilisez le micro pour vérifier les invités.")

    except Exception as e:
        st.error(f"Erreur de lecture : {e}")
        st.stop()
else:
    st.info("💡 Veuillez d'abord téléverser une liste d'invités.")
    st.stop()

# Création d'une colonne pour le champ de texte et le bouton
col1, col2 = st.columns([3, 1])

with col1:
    nom_reconnu = st.text_input("🧠 Nom détecté :", key="nom_vocal", label_visibility="visible")

with col2:
    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <button id="speakBtn" onmousedown="startRecognition()" onmouseup="stopRecognition()"
        style="padding: 12px 15px; font-size: 16px; border-radius: 8px; background-color: #4CAF50; color: white; border: none; width: 100%; height: 53px;">
        🎤 Maintenir
    </button>
    """, unsafe_allow_html=True)

# Vérification automatique
if st.session_state.nom_vocal:
    noms_bdd = df["Nom"].str.lower().str.strip()
    if st.session_state.nom_vocal.lower().strip() in noms_bdd.values:
        st.success(f"✅ {st.session_state.nom_vocal} est sur la liste des invités.")
    else:
        st.error(f"❌ {st.session_state.nom_vocal} n'est pas sur la liste.")

# JavaScript pour la reconnaissance vocale
components.html(
    """
    <script>
        let recognition;
        function startRecognition() {
            recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = "fr-FR";
            recognition.interimResults = false;
            recognition.maxAlternatives = 1;
            
            recognition.onresult = function(event) {
                const nom = event.results[0][0].transcript;
                const input = window.parent.document.querySelector('input[data-testid="stTextInput"]');
                if (input) {
                    input.value = nom;
                    const event = new Event('input', { bubbles: true });
                    input.dispatchEvent(event);
                }
            };
            
            recognition.start();
        }

        function stopRecognition() {
            if (recognition) {
                recognition.stop();
            }
        }
    </script>
    """,
    height=0
)
