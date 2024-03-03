import streamlit as st
import base64
from PIL import Image
from OpenAiPromptAPI_GPT4_Vision import text_output

def main():
    st.title("Descripción de imágenes con OpenAI GPT-4 Vision.")

    img_file = st.file_uploader("Sube una imagen", type=['png', 'jpg', 'jpeg'])

    if img_file is not None:
        img = Image.open(img_file)
        st.image(img, caption='Imagen subida.', use_column_width=True)

        # Convertir la imagen a base64
        img_b64 = base64.b64encode(img_file.getvalue()).decode()
        with st.spinner('Cargando texto...'):
            # Obtener el texto de la imagen usando la API de OpenAI
            text = text_output(img_b64)
        st.text_area("Texto resultante:", text, height=600)
        return img_b64

if __name__ == "__main__":
    main()
