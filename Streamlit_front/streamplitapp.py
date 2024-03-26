import streamlit as st
import base64
from PIL import Image
from datetime import datetime
from OpenAiPromptAPI_GPT4_Vision import text_output
from OpenAiTaggingPrompt_GPT4_Vision import compute

opciones = ['Primavera - verano', 'Otoño - invierno']

# Variable global para almacenar el base64 de la imagen
img_b64 = None

def main():
    curr_year = datetime.now().year
    st.title("Descripción de imágenes con OpenAI GPT-4 Vision.")
    year = st.number_input("Año de la imagen", min_value=1930, max_value=int(curr_year + 1), value=curr_year)
    designer = st.text_input("Diseñador de la imagen", "Diseñador")
    temporada = st.selectbox("Temporada de la imagen", opciones)
    img_file = st.file_uploader("Sube una imagen", type=['png', 'jpg', 'jpeg'])

    global img_b64  

    if img_file is not None:
        img = Image.open(img_file)
        st.image(img, caption='Imagen subida.', use_column_width=True)
        img_b64 = base64.b64encode(img_file.getvalue()).decode()

    if st.button("Describir imagen como texto"):
        if img_b64 is not None: 
            with st.spinner('Analizando imagen...'):
                text = text_output(img_b64)
            st.text_area("Texto resultante:", text, height=400)

    if st.button("Guardar tags en S3"):
        if img_b64 is not None: 
            with st.spinner('Guardando en S3...'):
                compute_text = compute(img_b64, year, designer, temporada)
                st.write(compute_text)

if __name__ == "__main__":
    main()
