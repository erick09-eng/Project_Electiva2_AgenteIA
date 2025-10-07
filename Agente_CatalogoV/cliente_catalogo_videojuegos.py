import asyncio
import sys
import os

from dotenv import load_dotenv
load_dotenv()

from mirascope import llm, BaseTool
from pydantic import Field
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# --- 1. Definición de Herramientas para Videojuegos ---
class GetAllGames(BaseTool):
    """Utiliza esta herramienta para obtener todos los videojuegos del catálogo."""
    def call(self) -> str:
        return "Herramienta 'GetAllGames' seleccionada."

class GetGameById(BaseTool):
    """Utiliza esta herramienta para obtener un videojuego específico por su ID."""
    game_id: int = Field(..., description="El ID del videojuego a buscar")
    def call(self) -> str:
        return f"Herramienta 'GetGameById' seleccionada para el juego {self.game_id}."

class SearchGamesByTitle(BaseTool):
    """Utiliza esta herramienta para buscar videojuegos por título."""
    title: str = Field(..., description="Título o parte del título a buscar")
    def call(self) -> str:
        return f"Herramienta 'SearchGamesByTitle' seleccionada para '{self.title}'."

# --- 2. Mapeo de Herramientas ---
TOOL_NAME_MAP = {
    "GetAllGames": "get_all_games",
    "GetGameById": "get_game_by_id", 
    "SearchGamesByTitle": "search_games_by_title"
}

# --- 3. Función de llamada al LLM ---
@llm.call(
    "google",  # o "ollama" si prefieres
    model="gemini-2.0-flash",  # ajusta el modelo
    tools=[
        GetAllGames,
        GetGameById,
        SearchGamesByTitle
    ],
)
def get_user_intent(query: str):
    """
    ¡Eres un asistente especializado en videojuegos!
    1. Analiza la petición del usuario sobre videojuegos.
    2. Si la petición coincide con alguna herramienta disponible, llámala.
    3. Si NO es sobre videojuegos, responde: "Solo puedo ayudarte con información sobre videojuegos."
    
    Solicitud del usuario: "{query}"
    """
    return query

# --- 4. Lógica Principal del Cliente ---
async def main(prompt):
    server_params = StdioServerParameters(
        command=sys.executable, 
        args=["server_games.py"]
    )

    print("🎮 Cliente Videojuegos MCP iniciado")
    print("Ejemplos: 'lista todos los videojuegos', 'buscar juego Zelda', 'mostrar juego con id 5'")

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            try:
                response = get_user_intent(prompt)
                
                if tool := response.tool:
                    tool_call_info = tool.tool_call
                    tool_name = tool_call_info.name
                    tool_args = tool_call_info.args

                    tool_name_on_server = TOOL_NAME_MAP.get(tool_name)
                    
                    if not tool_name_on_server:
                        return f"Error: Herramienta desconocida: {tool_name}"

                    print(f"🕹️ LLM -> Herramienta: '{tool_name_on_server}', Args: {tool_args}")
                    
                    result = await session.call_tool(tool_name_on_server, arguments=tool_args)

                    if result.isError:
                        return f"Error del servidor: {result.content}"
                    elif result.structuredContent:
                        response_data = result.structuredContent
                        response_data["tool_used"] = tool_name_on_server
                        return response_data
                    else:
                        return result.content
                else:
                    return response.content
                    
            except Exception as e:
                return f"Error: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        result = asyncio.run(main(query))
        print(result)
    else:
        print("Usage: python client_games.py 'tu consulta sobre videojuegos'")