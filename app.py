
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

        st.success("✅ Liste chargée. Utilisez le micro pour vérifier les invités.")

        if 'Nom' not in df.columns:
            st.error("❌ Le fichier doit contenir une colonne intitulée exactement 'Nom'.")
            st.stop()

    except Exception as e:
        st.error(f"Erreur de lecture : {e}")
        st.stop()
else:
    st.info("💡 Veuillez d'abord téléverser une liste d'invités.")
    st.stop()

# Affichage du champ vocal
st.markdown("## 🧠 Nom détecté par la voix")
nom_reconnu = st.text_input("Nom reconnu :", key="nom_vocal")

# Vérification automatique
if nom_reconnu:
    noms_bdd = df["Nom"].str.lower().str.strip()
    if nom_reconnu.lower().strip() in noms_bdd.values:
        st.success(f"✅ {nom_reconnu} est sur la liste des invités.")
    else:
        st.error(f"❌ {nom_reconnu} n'est pas sur la liste.")

# Bouton vocal maintenu
st.markdown("## 🎙️ Maintenez le bouton pour parler")

components.html(
    """
    <button id="speakBtn" onmousedown="startRecognition()" onmouseup="stopRecognition()"
        style="padding: 12px 25px; font-size: 18px; border-radius: 8px; background-color: #4CAF50; color: white; border: none;">
        🎤 Maintenir pour parler
    </button>

    <script>
        let recognition;
        function startRecognition() {
            recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = "fr-FR";
            recognition.interimResults = false;
            recognition.maxAlternatives = 1;
            recognition.start();

            recognition.onresult = function(event) {
                const nom = event.results[0][0].transcript;

                const iframe = window.parent.document;
                const inputs = iframe.querySelectorAll('input[type="text"]');
                inputs.forEach(input => {
                    input.value = nom;
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                });
            };
        }

        function stopRecognition() {
            if (recognition) {
                recognition.stop();
            }
        }
    </script>
    """,
    height=150,
)
