import asyncio
import sys
import json
import os
import re
from typing import Dict, Any
import google.generativeai as genai
from pydantic import Field, BaseModel
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class ConversationManager:
    def __init__(self):
        self.greetings = ['hola', 'hello', 'hi', 'hey', 'buenos días', 'buenas tardes', 'qué tal', 'gracias']
        self.goodbyes = ['adios', 'bye', 'hasta luego', 'chao', 'nos vemos', 'hasta pronto']
        self.questions = ['cómo estás', 'qué haces', 'quién eres', 'qué puedes hacer']
        
    def is_greeting(self, message):
        message_lower = message.lower().strip()
        return any(greeting in message_lower for greeting in self.greetings)
    
    def is_goodbye(self, message):
        message_lower = message.lower().strip()
        return any(goodbye in message_lower for goodbye in self.goodbyes)
    
    def is_question(self, message):
        message_lower = message.lower()
        return any(question in message_lower for question in self.questions)
    
    def handle_conversation(self, message):
        message_lower = message.lower().strip()
        
        if self.is_greeting(message_lower):
            return "¡Hola! Soy tu asistente especializado en noticias. ¿En qué puedo ayudarte? Puedo listar noticias, buscar por ID o título, y crear nuevas noticias."
        
        elif self.is_goodbye(message_lower):
            return "¡Hasta luego! Fue un gusto ayudarte con las noticias."
        
        elif self.is_question(message_lower):
            if 'cómo estás' in message_lower:
                return "¡Estoy funcionando perfectamente! Listo para ayudarte con tu gestión de noticias."
            elif 'qué haces' in message_lower or 'qué puedes hacer' in message_lower:
                return "Soy un asistente de noticias. Puedo: listar todas las noticias, buscar por ID, buscar por título y crear nuevas noticias en la base de datos."
            elif 'quién eres' in message_lower:
                return "Soy tu agente asistente especializado en gestión de noticias."
        
        # Si no es conversacional, devolver None para que lo procesen las herramientas
        return None

# --- 1. Modelos para herramientas ---
class GetAllNewsTool(BaseModel):
    """Devuelve todas las noticias."""
    pass

class GetNewsByIdTool(BaseModel):
    """Busca una noticia específica por su ID."""
    news_id: int = Field(..., description="El ID numérico de la noticia")

class SearchNewsByTitleTool(BaseModel):
    """Busca noticias por título (búsqueda parcial)."""
    title: str = Field(..., description="Título o parte del título a buscar")

class CreateNewsTool(BaseModel):
    """Crea una nueva noticia."""
    titulo: str = Field(..., description="Título de la noticia")
    contenido: str = Field(..., description="Contenido de la noticia")
    fecha: str = Field(..., description="Fecha de la noticia (YYYY-MM-DD)")

# --- 2. Mapeo de Herramientas ---
TOOL_MAP = {
    "get_all_news": GetAllNewsTool,
    "get_news_by_id": GetNewsByIdTool, 
    "search_news_by_title": SearchNewsByTitleTool,
    "create_news": CreateNewsTool
}

# --- 3. Función MEJORADA para llamar al LLM ---
def get_user_intent(query: str):
    """
    Usa Google Gemini para decidir entre conversación o herramientas
    """
    model = genai.GenerativeModel("models/gemini-2.0-flash")
    
    # Primero verificar si es conversacional
    conversation_manager = ConversationManager()
    conversational_response = conversation_manager.handle_conversation(query)
    
    if conversational_response is not None:
        return json.dumps({"type": "conversation", "response": conversational_response})
    
    # Si no es conversacional, proceder con herramientas
    tools_schema = {
        "get_all_news": {"description": "Devuelve todas las noticias"},
        "get_news_by_id": {"description": "Busca una noticia específica por su ID", "parameters": {"news_id": "number"}},
        "search_news_by_title": {"description": "Busca noticias por título", "parameters": {"title": "string"}},
        "create_news": {"description": "Crea una nueva noticia", "parameters": {
            "titulo": "string", 
            "contenido": "string", 
            "fecha": "string"
        }}
    }
    
    prompt = f"""
    Eres un asistente de noticias. Selecciona UNA de estas herramientas basado en la consulta:
    
    HERRAMIENTAS DISPONIBLES:
    {json.dumps(tools_schema, indent=2)}
    
    Responde SOLO con JSON: {{"tool": "nombre_herramienta", "args": {{argumentos}}}}
    
    Si la consulta NO es sobre noticias o no coincide con las herramientas, responde con:
    {{"type": "conversation", "response": "Lo siento, solo puedo ayudarte con operaciones de noticias: listar, buscar o crear noticias en el sistema."}}
    
    Consulta: "{query}"
    """
    
    response = model.generate_content(prompt)
    return response.text

# --- 4. Función Principal MEJORADA ---
async def process_query(prompt: str, session: ClientSession) -> Dict[str, Any]:
    try:
        llm_response = get_user_intent(prompt)
        
        # Parsear respuesta del LLM
        try:
            clean_response = llm_response.strip().replace('```json', '').replace('```', '')
            response_data = json.loads(clean_response)
            
            # Si es conversación
            if response_data.get("type") == "conversation":
                return {
                    "status": "conversation", 
                    "message": response_data.get("response"),
                    "is_conversational": True
                }
            
            # Si es herramienta
            tool_name = response_data.get("tool")
            tool_args = response_data.get("args", {})
            
            if tool_name in TOOL_MAP:
                print(f"LLM -> Herramienta: '{tool_name}', Args: {tool_args}")
                
                result = await session.call_tool(tool_name, arguments=tool_args)

                if result.isError:
                    return {
                        "status": "error", 
                        "message": f"Error del servidor: {result.content}",
                        "is_conversational": False
                    }
                else:
                    return {
                        "status": "success", 
                        "data": result.structuredContent or result.content,
                        "is_conversational": False
                    }
            else:
                return {
                    "status": "no_tool", 
                    "message": f"No puedo procesar esa solicitud. Solo manejo operaciones de noticias.",
                    "is_conversational": True
                }
                
        except json.JSONDecodeError:
            return {
                "status": "error", 
                "message": f"Error procesando la respuesta: {llm_response}",
                "is_conversational": False
            }

    except Exception as e:
        return {
            "status": "error", 
            "message": f"Error: {str(e)}",
            "is_conversational": False
        }

# --- 5. Función principal (sin cambios) ---
async def main(prompt: str):
    server_params = StdioServerParameters(
        command=sys.executable, 
        args=["server_mcp_noticias.py"]
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
        print("Usage: python agente_noticias.py 'tu consulta sobre noticias'")