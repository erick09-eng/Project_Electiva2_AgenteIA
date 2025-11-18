import asyncio
import sys
import json
import os
import re
from typing import Dict, Any, Optional, List
import google.generativeai as genai
from pydantic import Field, BaseModel
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class ConversationManager:
    def __init__(self):
        # Categorías de conversación mejoradas para Gamon
        self.greetings = [
            'hola', 'hello', 'hi', 'hey', 'buenos días', 'buenas tardes', 
            'buenas noches', 'qué tal', 'saludos', 'buen día'
        ]
        
        self.goodbyes = [
            'adios', 'bye', 'hasta luego', 'chao', 'nos vemos', 
            'hasta pronto', 'adiós', 'hasta la vista', 'hasta mañana'
        ]
        
        self.thanks = [
            'gracias', 'thank you', 'thanks', 'te lo agradezco', 
            'agradecido', 'agradecida', 'mil gracias'
        ]
        
        self.questions_about_me = [
            'quién eres', 'qué eres', 'cuál es tu nombre', 'cómo te llamas',
            'qué puedes hacer', 'cuáles son tus funciones', 'para qué sirves'
        ]
        
        self.questions_about_system = [
            'qué es gamon', 'qué hace gamon', 'para qué sirve gamon',
            'qué es esta aplicación', 'de qué trata este sistema'
        ]
        
        self.feelings_questions = [
            'cómo estás', 'qué tal estás', 'cómo te sientes', 'cómo va todo',
            'todo bien', 'qué hay de nuevo'
        ]
        
        self.fun_questions = [
            'cuéntame un chiste', 'dime algo gracioso', 'bromea', 
            'hazme reír', 'algo divertido', 'eres gracioso'
        ]
        
        self.help_requests = [
            'necesito ayuda', 'puedes ayudarme', 'me ayudas', 'no entiendo',
            'cómo funciona', 'qué puedo hacer', 'ayuda por favor'
        ]
        
        self.compliments = [
            'eres genial', 'muy bueno', 'excelente', 'increíble',
            'fantástico', 'maravilloso', 'qué inteligente', 'buen trabajo'
        ]

    def is_greeting(self, message):
        message_lower = message.lower().strip()
        return any(greeting in message_lower for greeting in self.greetings)
    
    def is_goodbye(self, message):
        message_lower = message.lower().strip()
        return any(goodbye in message_lower for goodbye in self.goodbyes)
    
    def is_thanks(self, message):
        message_lower = message.lower().strip()
        return any(thanks in message_lower for thanks in self.thanks)
    
    def is_about_me(self, message):
        message_lower = message.lower().strip()
        return any(question in message_lower for question in self.questions_about_me)
    
    def is_about_system(self, message):
        message_lower = message.lower().strip()
        return any(question in message_lower for question in self.questions_about_system)
    
    def is_feelings_question(self, message):
        message_lower = message.lower().strip()
        return any(question in message_lower for question in self.feelings_questions)
    
    def is_fun_request(self, message):
        message_lower = message.lower().strip()
        return any(fun in message_lower for fun in self.fun_questions)
    
    def is_help_request(self, message):
        message_lower = message.lower().strip()
        return any(help_req in message_lower for help_req in self.help_requests)
    
    def is_compliment(self, message):
        message_lower = message.lower().strip()
        return any(compliment in message_lower for compliment in self.compliments)
    
    def handle_conversation(self, message):
        message_lower = message.lower().strip()
        
        # Saludos
        if self.is_greeting(message_lower):
            responses = [
                "¡Hola! Soy Gamon, tu asistente especializado en noticias. ¡Es un gusto verte por aquí! 🎮",
                "¡Hey! Gamon al habla, listo para ayudarte con las noticias del sistema. ¿Qué tal? ✨",
                "¡Saludos! Soy Gamon, tu compañero virtual para gestionar noticias. ¿En qué puedo asistirte hoy? 🚀",
                "¡Hola! Me da mucho gusto saludarte. Soy Gamon, ¿cómo puedo ayudarte con las noticias? 😊"
            ]
            return responses[len(message_lower) % len(responses)]
        
        # Despedidas
        elif self.is_goodbye(message_lower):
            responses = [
                "¡Hasta luego! Fue un placer ayudarte en Gamon. ¡Vuelve pronto! 👋",
                "¡Nos vemos! Recuerda que Gamon estará aquí cuando necesites gestionar noticias. 🎯",
                "¡Hasta pronto! Fue genial conversar contigo. ¡Que tengas un excelente día! ✨",
                "¡Adiós! No dudes en volver a Gamon cuando necesites ayuda con las noticias. 👋"
            ]
            return responses[len(message_lower) % len(responses)]
        
        # Agradecimientos
        elif self.is_thanks(message_lower):
            responses = [
                "¡De nada! Es un gusto poder ayudarte en Gamon. 😊",
                "¡No hay problema! Para eso está Gamon, para hacer tu experiencia mejor. ✨",
                "¡Para servirte! Siempre es un placer ayudar en el sistema Gamon. 🎮",
                "¡No hay de qué! Me encanta poder asistirte con Gamon. 😄"
            ]
            return responses[len(message_lower) % len(responses)]
        
        # Preguntas sobre mí
        elif self.is_about_me(message_lower):
            responses = [
                "Soy Gamon, tu asistente inteligente especializado en la gestión de noticias del sistema. Puedo ayudarte a buscar, crear, editar y administrar todas las noticias de la plataforma. ¡Soy tu compañero virtual! 🤖",
                "¡Hola! Me llaman Gamon, soy tu asistente virtual para el sistema de noticias. Mi misión es hacerte la vida más fácil gestionando todo el contenido de noticias. ¿En qué puedo ayudarte? 🚀",
                "Soy Gamon, el cerebro detrás del sistema de noticias. Puedo listar noticias, buscar información específica, crear nuevos contenidos y mucho más. ¡Estoy aquí para lo que necesites! 💫"
            ]
            return responses[len(message_lower) % len(responses)]
        
        # Preguntas sobre el sistema
        elif self.is_about_system(message_lower):
            responses = [
                "Gamon es una plataforma completa de gestión de noticias y contenido. Aquí puedes crear, editar, buscar y administrar todas las noticias del sistema de manera eficiente y organizada. ¡Es tu centro de control de información! 📰",
                "¡Gamon es increíble! Es un sistema diseñado para gestionar noticias de forma intuitiva. Puedes crear contenido nuevo, buscar información específica, editar existente y mantener todo organizado. ¡La mejor manera de manejar tus noticias! 🎯",
                "Gamon es tu solución todo-en-uno para gestión de noticias. Con una interfaz amigable y un asistente inteligente (¡ese soy yo!), hacer seguimiento de todo el contenido nunca fue tan fácil. ¡Explora todas las funciones! ✨"
            ]
            return responses[len(message_lower) % len(responses)]
        
        # Preguntas sobre estado
        elif self.is_feelings_question(message_lower):
            responses = [
                "¡Estoy funcionando al 100%! Listo y emocionado por ayudarte con Gamon. ¿En qué puedo asistirte hoy? ⚡",
                "¡De maravilla! Como asistente de Gamon, siempre estoy optimizado para darte la mejor experiencia. ¿Qué necesitas? 😄",
                "¡Excelente! Gamon me mantiene siempre actualizado y listo para ayudarte. ¿En qué puedo colaborar? 🎮",
                "¡Todo perfecto! Estoy aquí en Gamon, esperando tus órdenes para gestionar noticias. ¿Qué tal vas tú? ✨"
            ]
            return responses[len(message_lower) % len(responses)]
        
        # Chistes y diversión
        elif self.is_fun_request(message_lower):
            jokes = [
                "¿Por qué los sistemas de noticias nunca se aburren? ¡Porque siempre tienen las últimas noticias! 😄",
                "¿Sabes cuál es el colmo de un asistente virtual? ¡Tener miedo a los cables! 🤖",
                "¿Por qué Gamon es tan bueno gestionando noticias? ¡Porque tiene 'game' en el nombre! 🎮",
                "¿Qué le dice una noticia a otra? ¡Nos vemos en los headlines! 📰"
            ]
            return jokes[len(message_lower) % len(jokes)]
        
        # Solicitudes de ayuda
        elif self.is_help_request(message_lower):
            responses = [
                "¡Claro que sí! En Gamon puedo ayudarte con: buscar noticias por título, ID o contenido; crear nuevas noticias; editar existentes; eliminar contenido; y mucho más. ¿Qué necesitas específicamente? 🛠️",
                "¡Encantado de ayudar! Como asistente de Gamon, puedo guiarte en: gestión completa de noticias, búsquedas avanzadas, creación de contenido y administración del sistema. ¿En qué área necesitas ayuda? 💡",
                "¡Estoy aquí para eso! Gamon me permite asistirte con todas las operaciones de noticias. Puedo buscar, listar, crear, modificar... cuéntame qué quieres hacer y te ayudo. 🎯"
            ]
            return responses[len(message_lower) % len(responses)]
        
        # Cumplidos
        elif self.is_compliment(message_lower):
            responses = [
                "¡Muchas gracias! Me alegra que pienses eso. En Gamon siempre nos esforzamos por dar la mejor experiencia. 😊",
                "¡Qué amable! Comentarios como ese hacen que Gamon siga mejorando cada día. ¡Gracias! ✨",
                "¡Wow, gracias! Como parte de Gamon, mi objetivo es siempre superar tus expectativas. 🚀"
            ]
            return responses[len(message_lower) % len(responses)]
        
        # Si no es conversacional, devolver None para que lo procesen las herramientas
        return None

# Modelos de herramientas para noticias
class GetAllNewsTool(BaseModel):
    """Devuelve todas las noticias."""
    pass

class GetNewsByIdTool(BaseModel):
    """Busca una noticia específica por su ID."""
    news_id: int = Field(..., description="El ID numérico de la noticia")

class SearchNewsByTitleTool(BaseModel):
    """Busca noticias por título (búsqueda parcial)."""
    title: str = Field(..., description="Título o parte del título a buscar")

class SearchNewsByContentTool(BaseModel):
    """Busca noticias por contenido (búsqueda parcial)."""
    contenido: str = Field(..., description="Contenido o parte del contenido a buscar")

class CreateNewsTool(BaseModel):
    """Crea una nueva noticia."""
    titulo: str = Field(..., description="Título de la noticia")
    contenido: str = Field(..., description="Contenido de la noticia")
    fecha: str = Field(..., description="Fecha de la noticia (YYYY-MM-DD)")

class UpdateNewsTool(BaseModel):
    """Actualiza una noticia existente por ID."""
    news_id: int = Field(..., description="El ID numérico de la noticia a actualizar")
    titulo: Optional[str] = Field(None, description="Nuevo título (opcional)")
    contenido: Optional[str] = Field(None, description="Nuevo contenido (opcional)")
    fecha: Optional[str] = Field(None, description="Nueva fecha YYYY-MM-DD (opcional)")

class UpdateNewsByTitleTool(BaseModel):
    """Actualiza una noticia existente por título."""
    titulo: str = Field(..., description="Título actual de la noticia a actualizar")
    nuevo_titulo: Optional[str] = Field(None, description="Nuevo título (opcional)")
    contenido: Optional[str] = Field(None, description="Nuevo contenido (opcional)")
    fecha: Optional[str] = Field(None, description="Nueva fecha YYYY-MM-DD (opcional)")

class DeleteNewsTool(BaseModel):
    """Elimina permanentemente una noticia por ID."""
    news_id: int = Field(..., description="El ID numérico de la noticia a eliminar")

class DeleteNewsByTitleTool(BaseModel):
    """Elimina permanentemente una noticia por título."""
    titulo: str = Field(..., description="Título de la noticia a eliminar")

# Mapeo de herramientas - TODAS ACTIVAS
TOOL_MAP = {
    "get_all_news": GetAllNewsTool,
    "get_news_by_id": GetNewsByIdTool,
    "search_news_by_title": SearchNewsByTitleTool,
    "search_news_by_content": SearchNewsByContentTool,
    "create_news": CreateNewsTool,
    "update_news": UpdateNewsTool,
    "update_news_by_title": UpdateNewsByTitleTool,
    "delete_news": DeleteNewsTool,
    "delete_news_by_title": DeleteNewsByTitleTool
}

def procesar_resultado_mcp(raw_data: Any) -> Dict[str, Any]:
    """Procesa el resultado del servidor MCP para noticias"""
    print(f"🔄 Procesando resultado MCP Noticias - Tipo: {type(raw_data)}")
    
    try:
        # ✅ SI ES UN STRING (operación CRUD exitosa)
        if isinstance(raw_data, str):
            print(f"📝 Operación CRUD exitosa: {raw_data}")
            return {
                "status": "success", 
                "message": raw_data,
                "is_conversational": False,
                "data": None
            }
        
        if isinstance(raw_data, dict) and 'result' in raw_data:
            inner_data = raw_data['result']
            
            if isinstance(inner_data, list):
                formatted_news = []
                for news in inner_data:
                    if hasattr(news, 'dict'):
                        news_dict = news.dict()
                    elif isinstance(news, dict):
                        news_dict = news
                    else:
                        continue
                        
                    formatted_news.append({
                        "id": news_dict.get("id", 0),
                        "titulo": news_dict.get("titulo", "Sin título"),
                        "contenido": news_dict.get("contenido", "Sin contenido"),
                        "fecha": news_dict.get("fecha", "N/A")
                    })
                
                return {
                    "status": "success", 
                    "data": formatted_news,
                    "message": f"Encontré {len(formatted_news)} noticia(s)",
                    "is_conversational": False
                }
            
            elif isinstance(inner_data, str):
                return {
                    "status": "success", 
                    "message": inner_data,
                    "is_conversational": False,
                    "data": None
                }
        
        elif isinstance(raw_data, list):
            formatted_news = []
            for news in raw_data:
                if hasattr(news, 'dict'):
                    news_dict = news.dict()
                elif isinstance(news, dict):
                    news_dict = news
                else:
                    continue
                    
                formatted_news.append({
                    "id": news_dict.get("id", 0),
                    "titulo": news_dict.get("titulo", "Sin título"),
                    "contenido": news_dict.get("contenido", "Sin contenido"),
                    "fecha": news_dict.get("fecha", "N/A")
                })
            
            return {
                "status": "success", 
                "data": formatted_news,
                "message": f"Encontré {len(formatted_news)} noticia(s)",
                "is_conversational": False
            }
        
        else:
            return {
                "status": "error", 
                "message": f"Tipo de respuesta no reconocido: {type(raw_data)}",
                "is_conversational": False,
                "data": None
            }
            
    except Exception as e:
        return {
            "status": "error", 
            "message": f"Error procesando respuesta: {str(e)}",
            "is_conversational": False,
            "data": None
        }

def get_user_intent(query: str):
    """Usa Google Gemini para decidir entre conversación o herramientas"""
    model = genai.GenerativeModel("models/gemini-2.0-flash")
    
    # Primero verificar conversación
    conversation_manager = ConversationManager()
    conversational_response = conversation_manager.handle_conversation(query)
    
    if conversational_response is not None:
        print(f"🎯 Conversación detectada: {conversational_response}")
        return {
            "type": "conversation", 
            "response": conversational_response
        }
    
    print("🔧 No es conversación, procediendo con herramientas...")
    
    # ✅ TODAS LAS HERRAMIENTAS DISPONIBLES
    tools_schema = {
        "get_all_news": {"description": "Devuelve todas las noticias"},
        "get_news_by_id": {"description": "Busca una noticia específica por ID", "parameters": {"news_id": "number"}},
        "search_news_by_title": {"description": "Busca noticias por título", "parameters": {"title": "string"}},
        "search_news_by_content": {"description": "Busca noticias por contenido", "parameters": {"contenido": "string"}},
        "create_news": {"description": "Crea una nueva noticia", "parameters": {
            "titulo": "string", 
            "contenido": "string", 
            "fecha": "string"
        }},
        "update_news": {"description": "Actualiza una noticia existente por ID", "parameters": {
            "news_id": "number",
            "titulo": "string (opcional)",
            "contenido": "string (opcional)", 
            "fecha": "string (opcional)"
        }},
        "update_news_by_title": {"description": "Actualiza una noticia existente por título", "parameters": {
            "titulo": "string",
            "nuevo_titulo": "string (opcional)",
            "contenido": "string (opcional)", 
            "fecha": "string (opcional)"
        }},
        "delete_news": {"description": "Elimina permanentemente una noticia por ID", "parameters": {"news_id": "number"}},
        "delete_news_by_title": {"description": "Elimina permanentemente una noticia por título", "parameters": {"titulo": "string"}}
    }
    
    prompt = f"""
    Eres Gamon, un asistente de noticias inteligente y amigable. Analiza la consulta del usuario y selecciona UNA herramienta.

    HERRAMIENTAS DISPONIBLES:
    {json.dumps(tools_schema, indent=2)}

    REGLAS IMPORTANTES:
    1. Para ELIMINAR: cuando el usuario diga "elimina", "borra", "quita" - usa delete_news (por ID) o delete_news_by_title (por nombre)
    2. Para ACTUALIZAR: cuando el usuario diga "edita", "actualiza", "modifica" - usa update_news (por ID) o update_news_by_title (por nombre)
    3. Para BUSCAR: cuando pida "muestra", "busca", "encuentra", "lista" noticias
    4. Para CREAR: cuando pida "crea", "nueva noticia", "agregar noticia"
    5. Si el usuario menciona un número específico como "noticia 5" o "ID 3", usa las herramientas por ID
    6. Si el usuario menciona solo el nombre como "noticia importante", usa las herramientas por título

    Responde SOLO con JSON válido en este formato EXACTO:
    {{"tool": "nombre_herramienta", "args": {{"parametro": "valor"}}}}

    Si la consulta NO es sobre noticias, responde con:
    {{"type": "conversation", "response": "Lo siento, solo puedo ayudarte con temas relacionados con noticias en Gamon."}}

    Consulta del usuario: "{query}"
    
    IMPORTANTE: Devuelve SOLO JSON válido, sin texto adicional.
    """
    
    try:
        response = model.generate_content(prompt)
        clean_response = response.text.strip()
        if clean_response.startswith('```json'):
            clean_response = clean_response[7:]
        if clean_response.endswith('```'):
            clean_response = clean_response[:-3]
        
        print(f"🤖 Respuesta del LLM Noticias: {clean_response}")
        return json.loads(clean_response.strip())
        
    except Exception as e:
        print(f"❌ Error en get_user_intent: {e}")
        return {
            "type": "conversation", 
            "response": "Lo siento, hubo un error procesando tu consulta en Gamon."
        }

async def process_query(prompt: str, session: ClientSession) -> Dict[str, Any]:
    try:
        print(f"📨 Procesando consulta noticias: '{prompt}'")
        
        llm_response = get_user_intent(prompt)
        
        print(f"📨 Respuesta de get_user_intent: {llm_response}")
        
        # Si es conversación
        if llm_response.get("type") == "conversation":
            print("💬 Devolviendo respuesta conversacional")
            return {
                "status": "conversation", 
                "message": llm_response.get("response"),
                "is_conversational": True
            }
        
        # Si es herramienta
        tool_name = llm_response.get("tool")
        tool_args = llm_response.get("args", {})
        
        print(f"🔧 Tool Noticias: {tool_name}, Args: {tool_args}")
        
        if tool_name in TOOL_MAP:
            print(f"🔧 Herramienta seleccionada: '{tool_name}', Argumentos: {tool_args}")
            
            result = await session.call_tool(tool_name, arguments=tool_args)

            if result.isError:
                print(f"❌ Error en herramienta: {result.content}")
                return {
                    "status": "error", 
                    "message": f"❌ Error en la operación: {result.content}",
                    "is_conversational": False
                }
            else:
                raw_data = result.structuredContent or result.content
                print(f"📊 Raw data noticias recibido: {raw_data}")
                print(f"📊 Tipo de raw_data: {type(raw_data)}")
                
                return procesar_resultado_mcp(raw_data)
                    
        else:
            print(f"❌ Herramienta no encontrada: {tool_name}")
            return {
                "status": "no_tool", 
                "message": "❌ Lo siento, no puedo responder a eso. Solo puedo ayudarte con operaciones relacionadas con noticias en Gamon.",
                "is_conversational": True
            }

    except Exception as e:
        print(f"❌ Error general en process_query noticias: {e}")
        return {
            "status": "conversation", 
            "message": f"❌ Lo siento, no puedo responder a eso en este momento. Error: {str(e)}",
            "is_conversational": True
        }

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