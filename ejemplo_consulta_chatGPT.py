import pandas as pd
import os
import openai
from dotenv import load_dotenv
import sys


'''
Comentarios Sara:

Primero tienes que cargar tu api key de openai (línea 33)

Lo que hace esta parte es cargar un fichero excel, filtrar los datos de la tabla (porque para el modelo gpt-3.5 hay mayor limitación de tokens)
y después pasarle ese tabla para que haga un análisis.

Si quieres cambiar el modelo -> línea 54

Veras que en la parte de la llamada a chatgpt, cuando hago la llamada le mando dos mensajes.
Esto es porque con el mensaje con role "system" guías  su comportamiento, en este ejemplo le digo que actúe como un analista de datos.
Y en el role "user" le solicito ya lo que quiero que haga y le paso la tabla.
La salida la ves en la línea 90.

Espero que te ayude :)
'''


# Current route
cwd = os.getcwd()
root_path = cwd + '\\..\\'

# API KEY
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Paths to folders
path_data = root_path + '\\data\\'

# Data file
file_name = 'data.xlsx'

# Load excel file
data = pd.read_excel(path_data + file_name)

# DataFrame display behavior configuration
num_rows = data.shape[0]
pd.options.display.max_rows = num_rows

# Filtered data
df_filtrado = data[ (data['AÑO']==2022)]
df_filtrado.reset_index(inplace=True,drop=True)

# Model
model_id = "gpt-3.5-turbo"


# User message
user_message = f"""Te doy la tabla {df_filtrado}. Tu tarea es analizarla y extraer los datos de la tabla que te indique. Escribe en presente y de forma impersonal. 
                Información general sobre la tabla: ocupación en campings para la provincia de Asturias sobre viajeros residentes en España y en el extranjero.

                Información que debe haber en el resumen:
                  - Residentes en España:
                    - Cuál es el menor número de viajeros que se ha registrado (consulta la columna viajeros). ¿En qué mes y año ocurre?
                    - Cuál es el mayor número de viajeros que se ha registrado (consulta la columna viajeros). ¿En qué mes y año ocurre?   
                    - Análisis por estaciones.
                  - Residentes en el extranjero:
                    - Cuál es el menor número de viajeros que se ha registrado (consulta la columna viajeros). ¿En qué mes y año ocurre?
                    - Cuál es el mayor número de viajeros que se ha registrado (consulta la columna viajeros). ¿En qué mes y año ocurre?   
                    - Análisis por estaciones.
                  - Comparación resultados para residentes en España y en el extranjero.
                  """

# Message to the system
system_message = """Eres el mejor analista de datos y matemático."""

# API Request
completion = openai.ChatCompletion.create(
  model=model_id,
  messages=[
    {"role": "system",
     "content": system_message
     },
    {"role": "user",
     "content": user_message
     }
    ]
)

# Printing ChatGPT output
print(completion.choices[0].message.content)


