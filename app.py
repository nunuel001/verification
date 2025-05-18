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

# Zone cachée de déclenchement
trigger = st.text_area("Invisible trigger", value="", key="trigger", label_visibility="collapsed")

# Affichage du champ vocal
nom_reconnu = st.text_input("🧠 Nom détecté :", key="nom_vocal")

# Vérification automatique sur mise à jour
if st.session_state.nom_vocal:
    noms_bdd = df["Nom"].str.lower().str.strip()
    if st.session_state.nom_vocal.lower().strip() in noms_bdd.values:
        st.success(f"✅ {st.session_state.nom_vocal} est sur la liste des invités.")
    else:
        st.error(f"❌ {st.session_state.nom_vocal} n'est pas sur la liste.")

# Bouton vocal avec injection + trigger
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
                const inputs = iframe.querySelectorAll('input[data-testid="stTextInput"]');
                const triggers = iframe.querySelectorAll('textarea[data-testid="stTextArea"]');

                inputs.forEach(input => {
                    input.value = nom;
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                });

                triggers.forEach(trigger => {
                    trigger.value = "triggered";
                    trigger.dispatchEvent(new Event('input', { bubbles: true }));
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
