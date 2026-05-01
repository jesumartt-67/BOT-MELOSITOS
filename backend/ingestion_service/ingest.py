__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import shutil

# 1. Cargar solo archivos .txt
print("Leyendo archivos de texto...")
loader = DirectoryLoader("./data", glob="./*.txt", loader_cls=TextLoader)
documents = loader.load()

# 2. Dividir el texto
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
docs = text_splitter.split_documents(documents)

# 3. Embeddings y Limpieza Forzada
embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# BLOQUE TRY-EXCEPT PARA EVITAR EL ERROR "TEXT FILE BUSY"
try:
    if os.path.exists("./chroma_db"):
        shutil.rmtree("./chroma_db")
        print("Base de datos antigua eliminada correctamente.")
except Exception as e:
    print(f"Aviso: No se pudo borrar automáticamente la carpeta chroma_db: {e}")
    print("Intentando continuar con la actualización...")

# 4. Crear Base de Datos
# db = Chroma.from_documents(docs, embeddings, persist_directory="./chroma_db")
db = Chroma.from_documents(docs, embeddings, persist_directory="/home/vagrant/db_jardin")
db.persist()

print(f"¡Éxito! Ahora el bot conoce la información de Melositos a través de {len(docs)} fragmentos.")
print("Ya puedes ejecutar: python main.py")
