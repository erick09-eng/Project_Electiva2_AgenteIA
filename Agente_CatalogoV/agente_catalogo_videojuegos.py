import asyncio
import sys
import json
import os
from typing import Dict, Any
import google.generativeai as genai
from pydantic import Field, BaseModel
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# --- 1. Modelos para herramientas ---
class GetAllGamesTool(BaseModel):
    """Devuelve todos los videojuegos del catálogo."""
    pass

class GetGameByIdTool(BaseModel):
    """Busca un videojuego específico por su ID."""
    game_id: int = Field(..., description="El ID numérico del videojuego")

class SearchGamesByTitleTool(BaseModel):
    """Busca videojuegos por título (búsqueda parcial)."""
    title: str = Field(..., description="Título o parte del título a buscar")

class CreateGameTool(BaseModel):
    """Crea un nuevo videojuego en el catálogo."""
    titulo: str = Field(..., description="Título del videojuego")
    descripcion: str = Field(..., description="Descripción del videojuego")
    fecha_lanzamiento: str = Field(..., description="Fecha de lanzamiento (YYYY-MM-DD)")
    precio: float = Field(..., description="Precio del videojuego")

# --- 2. Mapeo de Herramientas ---
TOOL_MAP = {
    "get_all_games": GetAllGamesTool,
    "get_game_by_id": GetGameByIdTool, 
    "search_games_by_title": SearchGamesByTitleTool,
    "create_game": CreateGameTool  # ✅ NUEVA HERRAMIENTA
}

# --- 3. Función para llamar al LLM ---
def get_user_intent(query: str):
    """
    Usa Google Gemini directamente para decidir la herramienta
    """
    model = genai.GenerativeModel("models/gemini-2.0-flash")
    
    tools_schema = {
        "get_all_games": {"description": "Devuelve todos los videojuegos del catálogo"},
        "get_game_by_id": {"description": "Busca un videojuego específico por su ID", "parameters": {"game_id": "number"}},
        "search_games_by_title": {"description": "Busca videojuegos por título", "parameters": {"title": "string"}},
        "create_game": {"description": "Crea un nuevo videojuego en el catálogo", "parameters": {
            "titulo": "string", 
            "descripcion": "string", 
            "fecha_lanzamiento": "string", 
            "precio": "number"
        }}
    }
    
    prompt = f"""
    Eres un asistente de videojuegos. Selecciona UNA de estas herramientas basado en la consulta:
    
    HERRAMIENTAS DISPONIBLES:
    {json.dumps(tools_schema, indent=2)}
    
    Responde SOLO con JSON: {{"tool": "nombre_herramienta", "args": {{argumentos}}}}
    
    Consulta: "{query}"
    """
    
    response = model.generate_content(prompt)
    return response.text

# --- 4. Función Principal ---
async def process_query(prompt: str, session: ClientSession) -> Dict[str, Any]:
    try:
        llm_response = get_user_intent(prompt)
        
        # Parsear respuesta del LLM
        try:
            # LIMPIAR respuesta - quitar markdown si existe
            clean_response = llm_response.strip().replace('```json', '').replace('```', '')
            tool_data = json.loads(clean_response)
            
            tool_name = tool_data.get("tool")
            tool_args = tool_data.get("args", {})
            
            if tool_name in TOOL_MAP:
                print(f"🎮 LLM -> Herramienta: '{tool_name}', Args: {tool_args}")
                
                result = await session.call_tool(tool_name, arguments=tool_args)

                if result.isError:
                    return {"status": "error", "message": f"Error del servidor: {result.content}"}
                else:
                    return {"status": "success", "data": result.structuredContent or result.content}
            else:
                return {"status": "no_tool", "message": f"Herramienta no reconocida: {tool_name}"}
                
        except json.JSONDecodeError:
            return {"status": "error", "message": f"LLM no devolvió JSON válido: {llm_response}"}

    except Exception as e:
        return {"status": "error", "message": f"Error: {str(e)}"}

# --- 5. Función principal ---
async def main(prompt: str):
    server_params = StdioServerParameters(
        command=sys.executable, 
        args=["server_mcp_catalogo_videojuegos.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await process_query(prompt, session)
            return result

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        result = asyncio.run(main(query))
        print(json.dumps(result, indent=2))
    else:
        print("Usage: python agente_catalogo_videojuegos.py 'tu consulta'")