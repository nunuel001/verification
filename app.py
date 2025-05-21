import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

st.set_page_config(page_title="Vérification Invités", layout="centered")
st.markdown("<h1 style='text-align: center;'>🎤 Vérification vocale des invités</h1>", unsafe_allow_html=True)
# 📎 Lien Drive (format CSV exporté)
st.markdown("### 🔗 Lien Google Sheets (format CSV publié)")
sheet_url = st.text_input("Collez ici le lien du fichier Google Sheets (CSV partagé)", placeholder="https://docs.google.com/spreadsheets/d/...")


# Chargement depuis Google Sheets (CSV public)
sheet_url = st.secrets.get("SHEET_CSV_URL", "")
if not sheet_url:
    st.warning("Aucune URL de liste d'invités n'est configurée.")
    st.stop()

if not sheet_url:
    st.info("Veuillez coller un lien Google Sheets publié en CSV.")
    st.stop()

try:
    df = pd.read_csv(sheet_url)
    if 'Nom' not in df.columns or 'Prénoms' not in df.columns:
        st.error("❌ Le fichier doit contenir les colonnes 'Nom' et 'Prénoms'.")
        st.stop()
    st.success("✅ Liste chargée depuis Google Sheets.")
except Exception as e:
    st.error(f"Erreur lors du chargement du fichier : {e}")
    st.stop()

# Zone d'entrée + bouton vocal
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

# Vérification par nom complet
if st.session_state.nom_vocal:
    nom_reconnu_complet = st.session_state.nom_vocal.strip().lower()
    df['full_name'] = (df['Prénoms'].astype(str) + " " + df['Nom'].astype(str)).str.lower().str.strip()
    match = df[df['full_name'] == nom_reconnu_complet]

    if not match.empty:
        st.success(f"✅ {nom_reconnu_complet.title()} est sur la liste des invités.")
        st.markdown("### 📋 Détails du profil :")
        st.dataframe(match.drop(columns=["full_name"]))
    else:
        st.error(f"❌ {nom_reconnu_complet.title()} n'est pas sur la liste.")

# JS : reconnaissance vocale
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
