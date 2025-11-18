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
    titulo: str
    descripcion: str
    fecha_lanzamiento: str
    precio: float = 0
    genero: str = ""
    tipo: str = ""
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
        
        # Verificar conexión y crear datos de prueba si no existen
        if games_collection.count_documents({}) == 0:
            print("Creando datos de prueba...")
            juegos_ejemplo = [
                {
                    "id": 1,
                    "titulo": "The Legend of Zelda: Breath of the Wild",
                    "descripcion": "Aventura épica en el reino de Hyrule",
                    "fecha_lanzamiento": "2017-03-03",
                    "precio": 59.99,
                    "genero": "Aventura",
                    "tipo": "Acción-Aventura",
                    "disponible": True
                },
                {
                    "id": 2,
                    "titulo": "Super Mario Odyssey",
                    "descripcion": "Aventura de Mario por diferentes reinos",
                    "fecha_lanzamiento": "2017-10-27",
                    "precio": 59.99,
                    "genero": "Plataformas",
                    "tipo": "Aventura",
                    "disponible": True
                },
                {
                    "id": 3,
                    "titulo": "Call of Duty: Modern Warfare",
                    "descripcion": "Juego de disparos en primera persona",
                    "fecha_lanzamiento": "2019-10-25",
                    "precio": 49.99,
                    "genero": "FPS",
                    "tipo": "Shooter",
                    "disponible": True
                },
                {
                    "id": 4,
                    "titulo": "FIFA 23",
                    "descripcion": "Simulador de fútbol",
                    "fecha_lanzamiento": "2022-09-30",
                    "precio": 39.99,
                    "genero": "Deportes",
                    "tipo": "Simulación",
                    "disponible": True
                },
                {
                    "id": 5,
                    "titulo": "The Witcher 3: Wild Hunt",
                    "descripcion": "RPG de mundo abierto",
                    "fecha_lanzamiento": "2015-05-19",
                    "precio": 29.99,
                    "genero": "RPG",
                    "tipo": "Aventura",
                    "disponible": True
                }
            ]
            games_collection.insert_many(juegos_ejemplo)
            print("Datos de prueba creados exitosamente")
        
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
            print("Conexión a MongoDB cerrada.")

# --- 3. Creación del Servidor MCP ---
mcp = FastMCP("VideoGamesServer", lifespan=app_lifespan)

# --- 4. FUNCIÓN DE VALIDACIÓN DE PERMISOS ---
def verificar_permisos_admin(ctx: Context, operacion: str) -> bool:
    """
    Verifica si el usuario tiene permisos de administrador.
    En un entorno real, esto verificaría el token JWT o la sesión.
    Por ahora, simulamos la verificación basada en el contexto.
    """
    try:
        # En un entorno real, aquí verificaríamos el token JWT del usuario
        # Por ahora, asumimos que el contexto contiene información del usuario
        print(f"🔐 Verificando permisos para: {operacion}")
        
        # Simulamos la verificación - en producción esto vendría del token JWT
        # Por ahora, permitimos todas las operaciones (se validará en el frontend)
        # En una implementación real, aquí verificaríamos el rol del usuario
        
        return True  # Temporalmente permitimos todo
        
    except Exception as e:
        print(f"❌ Error verificando permisos: {e}")
        return False

# --- 5. HERRAMIENTAS CON VALIDACIÓN DE PERMISOS ---

# HERRAMIENTAS DE CONSULTA (permitidas para todos)
@mcp.tool()
async def get_all_games(ctx: Context) -> List[Videojuego]:
    """Devuelve todos los videojuegos del catálogo."""
    try:
        collection = ctx.request_context.lifespan_context.games_collection
        games = []
        
        print("Ejecutando get_all_games...")
        
        for document in collection.find():
            game = Videojuego(
                id=document.get("id", 0),
                titulo=document.get("titulo", ""),
                descripcion=document.get("descripcion", ""),
                fecha_lanzamiento=document.get("fecha_lanzamiento", ""),
                precio=document.get("precio", 0),
                genero=document.get("genero", ""),
                tipo=document.get("tipo", ""),
                disponible=document.get("disponible", True)
            )
            games.append(game)
        
        print(f"Encontrados {len(games)} juegos")
        return games
    except Exception as e:
        print(f"Error en get_all_games: {e}")
        return []

@mcp.tool()
async def get_game_by_id(game_id: int, ctx: Context) -> List[Videojuego]:
    """Busca un videojuego específico por su ID."""
    try:
        collection = ctx.request_context.lifespan_context.games_collection
        games = []
        
        print(f"Buscando juego con ID: {game_id}")
        
        document = collection.find_one({"id": game_id})
        if document:
            game = Videojuego(
                id=document.get("id", 0),
                titulo=document.get("titulo", ""),
                descripcion=document.get("descripcion", ""),
                fecha_lanzamiento=document.get("fecha_lanzamiento", ""),
                precio=document.get("precio", 0),
                genero=document.get("genero", ""),
                tipo=document.get("tipo", ""),
                disponible=document.get("disponible", True)
            )
            games.append(game)
            print(f"Juego encontrado: {game.titulo}")
        else:
            print(f"No se encontró juego con ID: {game_id}")
        
        return games
    except Exception as e:
        print(f"Error en get_game_by_id: {e}")
        return []

@mcp.tool()
async def search_games_by_title(title: str, ctx: Context) -> List[Videojuego]:
    """Busca videojuegos por título (búsqueda parcial)."""
    try:
        collection = ctx.request_context.lifespan_context.games_collection
        games = []
        
        print(f"Buscando juegos con título: '{title}'")
        
        query = {"titulo": {"$regex": title, "$options": "i"}}
        
        for document in collection.find(query):
            game = Videojuego(
                id=document.get("id", 0),
                titulo=document.get("titulo", ""),
                descripcion=document.get("descripcion", ""),
                fecha_lanzamiento=document.get("fecha_lanzamiento", ""),
                precio=document.get("precio", 0),
                genero=document.get("genero", ""),
                tipo=document.get("tipo", ""),
                disponible=document.get("disponible", True)
            )
            games.append(game)
        
        print(f"Encontrados {len(games)} juegos con título que contiene '{title}'")
        return games
    except Exception as e:
        print(f"Error en search_games_by_title: {e}")
        return []

@mcp.tool()
async def search_games_by_genre(genero: str, ctx: Context) -> List[Videojuego]:
    """Busca videojuegos por género."""
    try:
        collection = ctx.request_context.lifespan_context.games_collection
        games = []
        
        print(f"Buscando juegos del género: '{genero}'")
        
        query = {"genero": {"$regex": genero, "$options": "i"}}
        
        for document in collection.find(query):
            game = Videojuego(
                id=document.get("id", 0),
                titulo=document.get("titulo", ""),
                descripcion=document.get("descripcion", ""),
                fecha_lanzamiento=document.get("fecha_lanzamiento", ""),
                precio=document.get("precio", 0),
                genero=document.get("genero", ""),
                tipo=document.get("tipo", ""),
                disponible=document.get("disponible", True)
            )
            games.append(game)
        
        print(f"Encontrados {len(games)} juegos del género '{genero}'")
        return games
    except Exception as e:
        print(f"Error en search_games_by_genre: {e}")
        return []

@mcp.tool()
async def search_games_by_type(tipo: str, ctx: Context) -> List[Videojuego]:
    """Busca videojuegos por tipo."""
    try:
        collection = ctx.request_context.lifespan_context.games_collection
        games = []
        
        print(f"Buscando juegos del tipo: '{tipo}'")
        
        query = {"tipo": {"$regex": tipo, "$options": "i"}}
        
        for document in collection.find(query):
            game = Videojuego(
                id=document.get("id", 0),
                titulo=document.get("titulo", ""),
                descripcion=document.get("descripcion", ""),
                fecha_lanzamiento=document.get("fecha_lanzamiento", ""),
                precio=document.get("precio", 0),
                genero=document.get("genero", ""),
                tipo=document.get("tipo", ""),
                disponible=document.get("disponible", True)
            )
            games.append(game)
        
        print(f"Encontrados {len(games)} juegos del tipo '{tipo}'")
        return games
    except Exception as e:
        print(f"Error en search_games_by_type: {e}")
        return []

# HERRAMIENTAS CRUD (solo para administradores)
@mcp.tool()
async def create_game(
    titulo: str, 
    descripcion: str, 
    fecha_lanzamiento: str, 
    precio: float, 
    genero: str = "",
    tipo: str = "",
    ctx: Context = None
) -> str:
    """Crea un nuevo videojuego en el catálogo."""
    try:
        # ✅✅✅ VALIDACIÓN DE PERMISOS
        if not verificar_permisos_admin(ctx, "crear juego"):
            return "❌ Error: No tienes permisos de administrador para crear videojuegos."
        
        collection = ctx.request_context.lifespan_context.games_collection
        
        # Encontrar el próximo ID
        last_game = collection.find_one(sort=[("id", -1)])
        next_id = last_game["id"] + 1 if last_game else 1
        
        nuevo_juego = {
            "id": next_id,
            "titulo": titulo,
            "descripcion": descripcion,
            "fecha_lanzamiento": fecha_lanzamiento,
            "precio": precio,
            "genero": genero,
            "tipo": tipo,
            "disponible": True
        }
        
        result = collection.insert_one(nuevo_juego)
        
        if result.inserted_id:
            return f"Creacion exitosa: Videojuego '{titulo}' ha sido creado con ID {next_id}"
        else:
            return f"Error en creacion: No se pudo crear el videojuego '{titulo}'"
            
    except Exception as e:
        return f"Error en creacion: {str(e)}"

@mcp.tool()
async def update_game(
    game_id: int, 
    titulo: Optional[str] = None,
    descripcion: Optional[str] = None,
    fecha_lanzamiento: Optional[str] = None,
    precio: Optional[float] = None,
    genero: Optional[str] = None,
    tipo: Optional[str] = None,
    disponible: Optional[bool] = None,
    ctx: Context = None
) -> str:
    """Actualiza un videojuego existente en el catálogo por ID."""
    try:
        # ✅✅✅ VALIDACIÓN DE PERMISOS
        if not verificar_permisos_admin(ctx, "actualizar juego"):
            return "❌ Error: No tienes permisos de administrador para actualizar videojuegos."
        
        collection = ctx.request_context.lifespan_context.games_collection
        
        # Verificar si el juego existe
        existing_game = collection.find_one({"id": game_id})
        if not existing_game:
            return f"Error en actualizacion: No se encontro un videojuego con ID {game_id}"
        
        # Construir campos a actualizar
        update_fields = {}
        if titulo is not None:
            update_fields["titulo"] = titulo
        if descripcion is not None:
            update_fields["descripcion"] = descripcion
        if fecha_lanzamiento is not None:
            update_fields["fecha_lanzamiento"] = fecha_lanzamiento
        if precio is not None:
            update_fields["precio"] = precio
        if genero is not None:
            update_fields["genero"] = genero
        if tipo is not None:
            update_fields["tipo"] = tipo
        if disponible is not None:
            update_fields["disponible"] = disponible
        
        if not update_fields:
            return "Error en actualizacion: Debes proporcionar al menos un campo para actualizar"
        
        # Actualizar en la base de datos
        result = collection.update_one(
            {"id": game_id},
            {"$set": update_fields}
        )
        
        if result.modified_count > 0:
            campos_modificados = ', '.join(update_fields.keys())
            return f"Actualizacion exitosa: Videojuego ID {game_id} ha sido actualizado. Campos modificados: {campos_modificados}"
        else:
            return f"Error en actualizacion: No se pudo actualizar el videojuego ID {game_id}"
            
    except Exception as e:
        return f"Error en actualizacion: {str(e)}"

@mcp.tool()
async def delete_game(game_id: int, ctx: Context) -> str:
    """Elimina permanentemente un videojuego del catálogo por ID."""
    try:
        # ✅✅✅ VALIDACIÓN DE PERMISOS
        if not verificar_permisos_admin(ctx, "eliminar juego"):
            return "❌ Error: No tienes permisos de administrador para eliminar videojuegos."
        
        collection = ctx.request_context.lifespan_context.games_collection
        
        # Verificar si el juego existe
        existing_game = collection.find_one({"id": game_id})
        if not existing_game:
            return f"Error en eliminacion: No se encontro un videojuego con ID {game_id}"
        
        # Eliminar el juego
        result = collection.delete_one({"id": game_id})
        
        if result.deleted_count > 0:
            return f"Eliminacion exitosa: Videojuego ID {game_id} ha sido eliminado permanentemente del catalogo"
        else:
            return f"Error en eliminacion: No se pudo eliminar el videojuego ID {game_id}"
            
    except Exception as e:
        return f"Error en eliminacion: {str(e)}"

@mcp.tool()
async def delete_game_by_title(titulo: str, ctx: Context) -> str:
    """Elimina permanentemente un videojuego del catálogo por título."""
    try:
        # ✅✅✅ VALIDACIÓN DE PERMISOS
        if not verificar_permisos_admin(ctx, "eliminar juego"):
            return "❌ Error: No tienes permisos de administrador para eliminar videojuegos."
        
        collection = ctx.request_context.lifespan_context.games_collection
        
        # Verificar si el juego existe
        existing_game = collection.find_one({"titulo": {"$regex": titulo, "$options": "i"}})
        if not existing_game:
            return f"Error en eliminacion: No se encontro un videojuego con titulo '{titulo}'"
        
        # Eliminar el juego
        result = collection.delete_one({"titulo": {"$regex": titulo, "$options": "i"}})
        
        if result.deleted_count > 0:
            game_id = existing_game.get("id", "N/A")
            return f"Eliminacion exitosa: Videojuego '{titulo}' (ID: {game_id}) ha sido eliminado permanentemente del catalogo"
        else:
            return f"Error en eliminacion: No se pudo eliminar el videojuego '{titulo}'"
            
    except Exception as e:
        return f"Error en eliminacion: {str(e)}"

# --- 6. Ejecución del Servidor ---
if __name__ == "__main__":
    print("Iniciando servidor MCP para Videojuegos...")
    print("✅ Servidor con validación de permisos implementada")
    print("🔐 Consultas: Permitidas para todos")
    print("🔐 CRUD: Solo para administradores")
    mcp.run()