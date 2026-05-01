__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Carga las variables del archivo .env si existe (Para local)
load_dotenv()

app = FastAPI(title="Jardín Infantil")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CONFIGURACIÓN DE IA ---
# Debes obtener una API KEY gratuita en https://console.groq.com/
# os.environ["GROQ_API_KEY"] = "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"
api_key = os.getenv("GROQ_API_KEY")

# persist_directory = 'chroma_db'
persist_directory="/home/vagrant/db_jardin"
embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
db = Chroma(persist_directory=persist_directory, embedding_function=embeddings)

# Configuración del Modelo de Lenguaje (LLM)
llm = ChatGroq(temperature=0, model_name="llama-3.1-8b-instant")

# --- EL TEMPLATE QUE SOLUCIONA TU PROBLEMA ---
template = """Eres el asistente virtual del Jardín Infantil Melositos.
Usa ÚNICAMENTE los siguientes fragmentos de contexto para responder la pregunta del usuario.
Si no encuentras la respuesta específica en el contexto, intenta dar la información más cercana relacionada.

Contexto: {context}

Pregunta: {question}

Respuesta útil en español:"""


PROMPT = PromptTemplate(
    template=template, input_variables=["context", "question"]
)

# Crear la cadena de respuesta inteligente
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=db.as_retriever(search_kwargs={"k": 1}),
    chain_type_kwargs={"prompt": PROMPT}
)

class QueryRequest(BaseModel):
    question: str

@app.get("/")
#def read_root():
def home():
    return {"status": "Servidor del Jardín Infantil Funcionando"}

@app.post("/ask")
def ask_question(request: QueryRequest):
    try:
        # Esto imprimirá la pregunta que llega desde el navegador
        print(f"\n--- PREGUNTA RECIBIDA: {request.question} ---")
        response = qa_chain.invoke({"query": request.question})
        # Esto imprimirá lo que la IA (Groq) responde
        print(f"--- RESPUESTA IA: {response['result']} ---\n")

        return {
            "question": request.question,
            "answer": response["result"]
        }
    except Exception as e:
        print(f"!!! ERROR: {str(e)} !!!")
        return {"question": request.question, "answer": "Error interno del servidor"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
