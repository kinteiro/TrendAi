import streamlit as st
import base64
from PIL import Image

def main():
    st.title("Aplicación de conversión de imágenes a base64")

    img_file = st.file_uploader("Sube una imagen", type=['png', 'jpg', 'jpeg'])

    if img_file is not None:
        img = Image.open(img_file)
        st.image(img, caption='Imagen subida.', use_column_width=True)

        # Convertir la imagen a base64
        img_format = img_file.type.split('/')[1]
        img_b64 = base64.b64encode(img_file.getvalue()).decode()

        # Mostrar la cadena base64
        st.text(f"La imagen en base64 es: \n\n{'data:image/'+img_format+';base64,'+img_b64}")

if __name__ == "__main__":
    main()