import asyncio
import os
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncIterator, List, Optional, Dict, Any
from datetime import datetime

from pymongo import MongoClient
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP, Context

# --- 1. Modelos de Datos para Noticias ---
class Noticia(BaseModel):
    id: int
    titulo: str
    contenido: str
    fecha: str

# --- 2. Contexto y Conexión a MongoDB ---
@dataclass
class AppContext:
    mongo_client: MongoClient
    db: Any
    noticias_collection: Any

@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    print("Conectando a MongoDB para Noticias...")
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["noticiasdb"]  
        noticias_collection = db["noticias"]  

        print("Conectado a MongoDB - noticiasdb.noticias")
        yield AppContext(
            mongo_client=client,
            db=db, 
            noticias_collection=noticias_collection
        )
    except Exception as e:
        print(f"Error conectando a MongoDB: {e}")
        raise
    finally:
        if 'client' in locals():
            client.close()
            print("Conexión a MongoDB cerrada.")

# --- 3. Creación del Servidor MCP ---
mcp = FastMCP("NewsServer", lifespan=app_lifespan)

# --- 4. Herramientas para Noticias ---
@mcp.tool()
async def get_all_news(ctx: Context) -> List[Noticia]:
    """
    Devuelve todas las noticias registradas.
    """
    collection = ctx.request_context.lifespan_context.noticias_collection
    noticias = []
    
    for document in collection.find():
        noticia = Noticia(
            id=document.get("id", 0),
            titulo=document.get("titulo", ""),
            contenido=document.get("contenido", ""),
            fecha=document.get("fecha", "")
        )
        noticias.append(noticia)
    
    return noticias

@mcp.tool()
async def get_news_by_id(news_id: int, ctx: Context) -> List[Noticia]:
    """
    Devuelve una noticia específica por su ID.
    """
    collection = ctx.request_context.lifespan_context.noticias_collection
    noticias = []
    
    document = collection.find_one({"id": news_id})
    if document:
        noticia = Noticia(
            id=document.get("id", 0),
            titulo=document.get("titulo", ""),
            contenido=document.get("contenido", ""),
            fecha=document.get("fecha", "")
        )
        noticias.append(noticia)
    
    return noticias

@mcp.tool()
async def search_news_by_title(title: str, ctx: Context) -> List[Noticia]:
    """
    Busca noticias por título (búsqueda parcial).
    """
    collection = ctx.request_context.lifespan_context.noticias_collection
    noticias = []
    
    query = {"titulo": {"$regex": title, "$options": "i"}}
    
    for document in collection.find(query):
        noticia = Noticia(
            id=document.get("id", 0),
            titulo=document.get("titulo", ""),
            contenido=document.get("contenido", ""),
            fecha=document.get("fecha", "")
        )
        noticias.append(noticia)
    
    return noticias

@mcp.tool()
async def create_news(titulo: str, contenido: str, fecha: str, ctx: Context) -> str:
    """
    Crea una nueva noticia.
    """
    collection = ctx.request_context.lifespan_context.noticias_collection
    
    # Encontrar el próximo ID
    next_id = collection.count_documents({}) + 1
    
    nueva_noticia = {
        "id": next_id,
        "titulo": titulo,
        "contenido": contenido,
        "fecha": fecha
    }
    
    collection.insert_one(nueva_noticia)
    return f"Noticia '{titulo}' creada con ID {next_id}"

# --- 5. Ejecución del Servidor ---
if __name__ == "__main__":
    print("Iniciando servidor MCP para Noticias...")
    mcp.run()