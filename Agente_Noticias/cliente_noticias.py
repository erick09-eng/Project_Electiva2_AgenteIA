import asyncio
import sys
import os

from dotenv import load_dotenv
load_dotenv()

from mirascope import llm, BaseTool
from pydantic import Field
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# --- 1. Definición de Herramientas para Noticias ---
class GetAllNews(BaseTool):
    """Utiliza esta herramienta para obtener todas las noticias."""
    def call(self) -> str:
        return "Herramienta 'GetAllNews' seleccionada."

class GetNewsById(BaseTool):
    """Utiliza esta herramienta para obtener una noticia específica por su ID."""
    news_id: int = Field(..., description="El ID de la noticia a buscar")
    def call(self) -> str:
        return f"Herramienta 'GetNewsById' seleccionada para la noticia {self.news_id}."

class SearchNewsByTitle(BaseTool):
    """Utiliza esta herramienta para buscar noticias por título."""
    title: str = Field(..., description="Título o parte del título a buscar")
    def call(self) -> str:
        return f"Herramienta 'SearchNewsByTitle' seleccionada para '{self.title}'."

class CreateNews(BaseTool):
    """Utiliza esta herramienta para crear una nueva noticia."""
    titulo: str = Field(..., description="Título de la noticia")
    contenido: str = Field(..., description="Contenido de la noticia")
    fecha: str = Field(..., description="Fecha de la noticia (YYYY-MM-DD)")
    def call(self) -> str:
        return f"Herramienta 'CreateNews' seleccionada para '{self.titulo}'."

# --- 2. Mapeo de Herramientas ---
TOOL_NAME_MAP = {
    "GetAllNews": "get_all_news",
    "GetNewsById": "get_news_by_id",
    "SearchNewsByTitle": "search_news_by_title",
    "CreateNews": "create_news"
}

# --- 3. Función de llamada al LLM ---
@llm.call(
    "google",
    model="gemini-2.0-flash",
    tools=[
        GetAllNews,
        GetNewsById,
        SearchNewsByTitle,
        CreateNews
    ],
)
def get_user_intent(query: str):
    """
    ¡Eres un asistente especializado en noticias!
    1. Analiza la petición del usuario sobre noticias.
    2. Si la petición coincide con alguna herramienta disponible, llámala.
    3. Si NO es sobre noticias, responde: "Solo puedo ayudarte con información sobre noticias."
    
    Solicitud del usuario: "{query}"
    """
    return query

# --- 4. Lógica Principal del Cliente ---
async def main(prompt):
    server_params = StdioServerParameters(
        command=sys.executable, 
        args=["server_mcp_noticias.py"]
    )

    print("📰 Cliente Noticias MCP iniciado")
    print("Ejemplos: 'lista todas las noticias', 'buscar noticias tecnología', 'mostrar noticia con id 1'")

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

                    print(f"📰 LLM -> Herramienta: '{tool_name_on_server}', Args: {tool_args}")
                    
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
        print("Usage: python cliente_noticias.py 'tu consulta sobre noticias'")