import asyncio
import os
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncIterator, List, Optional, Dict, Any
from datetime import datetime

from pymongo import MongoClient
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP, Context

# --- 1. Modelos de Datos para Videojuegos ---
class Videojuego(BaseModel):
    id: int
    title: str
    content0: str
    fcdm: str
    precio: float = 0           
    disponible: bool = True  

# --- 2. Contexto y Conexión a MongoDB ---
@dataclass
class AppContext:
    mongo_client: MongoClient
    db: Any
    games_collection: Any

@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    print("Conectando a MongoDB...")
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["videojuegos"]
        games_collection = db["catalogo"]
        
        print("Conectado a MongoDB - videojuegos.catalogo")
        yield AppContext(
            mongo_client=client,
            db=db, 
            games_collection=games_collection
        )
    except Exception as e:
        print(f"Error conectando a MongoDB: {e}")
        raise
    finally:
        if 'client' in locals():
            client.close()
            print("🔌 Conexión a MongoDB cerrada.")

# --- 3. Creación del Servidor MCP ---
mcp = FastMCP("VideoGamesServer", lifespan=app_lifespan)

# --- 4. Herramientas para Videojuegos ---
@mcp.tool()
async def get_all_games(ctx: Context) -> List[Videojuego]:
    """
    Devuelve todos los videojuegos registrados en el catálogo.
    """
    collection = ctx.request_context.lifespan_context.games_collection
    games = []
    
    for document in collection.find():
        game = Videojuego(
            id=document.get("id", 0),
            title=document.get("titulo", ""),
            content0=document.get("descripcion", ""),
            fcdm=document.get("fecha_lanzamiento", ""),
            precio=document.get("precio", 0),              
            disponible=document.get("disponible", True)  
        )
        games.append(game)
    
    return games

@mcp.tool()
async def get_game_by_id(game_id: int, ctx: Context) -> List[Videojuego]:
    """
    Devuelve un videojuego específico por su ID.
    """
    collection = ctx.request_context.lifespan_context.games_collection
    games = []
    
    document = collection.find_one({"id": game_id})
    if document:
        game = Videojuego(
            id=document.get("id", 0),
            title=document.get("titulo", ""),
            content0=document.get("descripcion", ""),
            fcdm=document.get("fecha_lanzamiento", ""),
            precio=document.get("precio", 0),              
            disponible=document.get("disponible", True)  
        )
        games.append(game)
    
    return games

@mcp.tool()
async def search_games_by_title(title: str, ctx: Context) -> List[Videojuego]:
    """
    Busca videojuegos por título (búsqueda parcial).
    """
    collection = ctx.request_context.lifespan_context.games_collection
    games = []
    
    query = {"titulo": {"$regex": title, "$options": "i"}}
    
    for document in collection.find(query):
        game = Videojuego(
            id=document.get("id", 0),
            title=document.get("titulo", ""),
            content0=document.get("descripcion", ""),
            fcdm=document.get("fecha_lanzamiento", ""),
            precio=document.get("precio", 0),              
            disponible=document.get("disponible", True)  
        )
        games.append(game)
    
    return games

@mcp.tool()
async def create_game(titulo: str, descripcion: str, fecha_lanzamiento: str, precio: float, ctx: Context) -> str:
    """
    Crea un nuevo videojuego en el catálogo.
    """
    collection = ctx.request_context.lifespan_context.games_collection
    
    # Encontrar el próximo ID
    next_id = collection.count_documents({}) + 1
    
    nuevo_juego = {
        "id": next_id,
        "titulo": titulo,
        "descripcion": descripcion,
        "fecha_lanzamiento": fecha_lanzamiento,
        "precio": precio,
        "disponible": True
    }
    
    collection.insert_one(nuevo_juego)
    return f"Videojuego '{titulo}' creado con ID {next_id}"

# --- 5. Ejecución del Servidor ---
if __name__ == "__main__":
    print("🎮 Iniciando servidor MCP para Videojuegos...")
    mcp.run()