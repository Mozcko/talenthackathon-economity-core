# src/services/ai/agents/fiscal_agent.py
import chromadb
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from src.core.config import settings

def get_chroma_vectorstore():
    """
    Inicializa la conexión con el contenedor de ChromaDB usando la URL de settings.
    """
    # Extraemos host y puerto de la URL (ej. "http://localhost:8001")
    url_parts = settings.chroma_url.replace("http://", "").split(":")
    host = url_parts[0]
    port = int(url_parts[1]) if len(url_parts) > 1 else 8000

    chroma_client = chromadb.HttpClient(host=host, port=port)
    embeddings = OpenAIEmbeddings(api_key=settings.openai_api_key)
    
    # "leyes_fiscales" será la colección donde guardaremos los PDFs/Textos
    return Chroma(
        client=chroma_client,
        collection_name="leyes_fiscales",
        embedding_function=embeddings
    )

async def consultar_rag_fiscal_async(pregunta: str, historial: str) -> str:
    """
    Recupera contexto de ChromaDB y genera una respuesta basada ÚNICAMENTE en las leyes.
    """
    vectorstore = get_chroma_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3}) # Traemos los 3 fragmentos más relevantes
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=settings.openai_api_key)
    
    template = """
    Eres el Agente Fiscal de Economity. Tu deber es responder dudas sobre impuestos, 
    LISR y regulaciones de inversiones (como SOFIPOS).
    
    REGLA DE ORO: Responde ÚNICAMENTE basándote en el contexto legal proporcionado abajo. 
    Si la respuesta no está en el contexto, di "No tengo información legal actualizada sobre eso en mis registros."
    No inventes tasas ni artículos.

    Contexto Legal Recuperado:
    {contexto}
    
    Historial de la conversación:
    {historial}
    
    Pregunta del Usuario: {pregunta}
    """
    
    prompt = ChatPromptTemplate.from_template(template)
    
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
    # Creamos la cadena RAG (Recuperar -> Formatear -> Prompt -> LLM -> String)
    rag_chain = (
        {"contexto": retriever | format_docs, "pregunta": RunnablePassthrough(), "historial": lambda _: historial}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    # Como LangChain RAG chain ainvoke requiere un diccionario o input directo dependiendo de la cadena,
    # le pasamos la pregunta directamente ya que es el RunnablePassthrough
    respuesta = await rag_chain.ainvoke(pregunta)
    return respuesta