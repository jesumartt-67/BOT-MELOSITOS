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

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

os.environ["GROQ_API_KEY"] = "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"

embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
db = Chroma(persist_directory='chroma_db', embedding_function=embeddings)
llm = ChatGroq(temperature=0, model_name="llama-3.1-8b-instant")

template = """Eres el asistente oficial del Liceo Infantil Melositos. 
Tu objetivo es responder preguntas usando EXCLUSIVAMENTE el contexto proporcionado.

Contexto:
{context}

Instrucciones:
1. Si la pregunta es sobre costos, busca en las tablas de valores (Grado, Matrícula, Pensión).
2. Para el grado PARVULOS, el costo de matrícula es $ 580.000 y la pensión es $ 377.000.
3. Si no encuentras la respuesta exacta, di que estás consultando los archivos oficiales pero no inventes.

Pregunta: {question}
Respuesta:"""

PROMPT = PromptTemplate(template=template, input_variables=["context", "question"])

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=db.as_retriever(),
    chain_type_kwargs={"prompt": PROMPT}
)

class QueryRequest(BaseModel):
    question: str

@app.get("/")
def home():
    return {"status": "Servidor del Jardín Infantil Funcionando"}

@app.post("/ask")
def ask_question(request: QueryRequest):
    print(f"\n--- PREGUNTA RECIBIDA: {request.question} ---") # ESTO DEBE SALIR EN TU TERMINAL
    response = qa_chain.invoke({"query": request.question})
    print(f"--- RESPUESTA IA: {response['result']} ---\n") # ESTO TAMBIÉN
    return {"answer": response["result"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
