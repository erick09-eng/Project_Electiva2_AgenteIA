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

# ... (el ConversationManager permanece igual que antes) ...
class ConversationManager:
    def __init__(self):
        # Categorías existentes mejoradas
        self.greetings = ['hola', 'hello', 'hi', 'hey', 'buenos días', 'buenas tardes', 'buenas noches', 'qué tal', 'saludos', 'buen día']
        self.goodbyes = ['adios', 'bye', 'hasta luego', 'chao', 'nos vemos', 'hasta pronto', 'adiós', 'hasta la vista', 'hasta mañana', 'bye bye']
        self.questions = ['cómo estás', 'qué haces', 'quién eres', 'qué puedes hacer', 'cuál es tu nombre', 'cómo te llamas']
        self.thanks = ['gracias', 'thank you', 'thanks', 'te lo agradezco', 'agradecido', 'agradecida', 'mil gracias', 'thanks a lot']
        self.how_are_you = ['cómo estás', 'cómo te sientes', 'qué tal estás', 'cómo va todo', 'qué tal', 'cómo andas']
        self.whats_up = ['qué pasa', 'qué hay', 'qué cuenta', 'qué me cuentas', 'qué onda', 'qué hubo']
        
        # NUEVAS CATEGORÍAS
        self.compliments = [
            'eres genial', 'muy bueno', 'excelente', 'increíble', 'fantástico', 'maravilloso',
            'qué inteligente', 'muy listo', 'buen trabajo', 'bien hecho', 'impresionante',
            'me gustas', 'eres divertido', 'qué amable', 'muy útil'
        ]
        
        self.jokes_fun = [
            'cuéntame un chiste', 'dime algo gracioso', 'bromea', 'hazme reír', 'chiste',
            'algo divertido', 'anécdota graciosa', 'eres gracioso', 'humor'
        ]
        
        self.help_requests = [
            'necesito ayuda', 'puedes ayudarme', 'me ayudas', 'no entiendo', 'cómo funciona',
            'qué puedo hacer', 'ayuda por favor', 'me orientas', 'no sé cómo', 'podrías explicarme'
        ]
        
        self.feelings = [
            'estoy aburrido', 'me siento triste', 'estoy feliz', 'tengo sueño', 'estoy emocionado',
            'me siento mal', 'estoy cansado', 'qué alegría', 'estoy enfadado', 'me siento solo',
            'estoy contento', 'qué fastidio', 'estoy animado', 'me siento genial'
        ]
        
        self.opinions = [
            'qué opinas', 'qué piensas', 'cuál es tu opinión', 'qué crees', 'dime tu punto de vista',
            'desde tu perspectiva', 'tú qué dices', 'qué te parece'
        ]
        
        self.gaming_topics = [
            'videojuegos favoritos', 'mejor juego', 'recomienda un juego', 'qué juego jugar',
            'juegos populares', 'nuevos lanzamientos', 'géneros de juegos', 'consolas',
            'juegos clásicos', 'juegos multijugador', 'juegos indie', 'juegos gratis'
        ]
        
        self.personal_questions = [
            'dónde vives', 'cuántos años tienes', 'de dónde eres', 'tienes familia',
            'qué te gusta hacer', 'cuáles son tus hobbies', 'tienes amigos', 'te gusta la música',
            'qué música te gusta', 'tienes novia', 'tienes novio'
        ]
        
        self.weather_time = [
            'qué tiempo hace', 'cómo está el clima', 'qué hora es', 'qué día es hoy',
            'fecha actual', 'estación del año', 'hace calor', 'hace frío'
        ]
        
        self.philosophical = [
            'sentido de la vida', 'qué es el amor', 'por qué existimos', 'qué hay después de la muerte',
            'qué es la felicidad', 'el universo', 'filosofía', 'pregunta profunda'
        ]

    def is_greeting(self, message):
        message_lower = message.lower().strip()
        return any(greeting in message_lower for greeting in self.greetings)
    
    def is_goodbye(self, message):
        message_lower = message.lower().strip()
        return any(goodbye in message_lower for goodbye in self.goodbyes)
    
    def is_question(self, message):
        message_lower = message.lower()
        return any(question in message_lower for question in self.questions)
    
    def is_thanks(self, message):
        message_lower = message.lower().strip()
        return any(thanks in message_lower for thanks in self.thanks)
    
    def is_how_are_you(self, message):
        message_lower = message.lower().strip()
        return any(phrase in message_lower for phrase in self.how_are_you)
    
    def is_whats_up(self, message):
        message_lower = message.lower().strip()
        return any(phrase in message_lower for phrase in self.whats_up)
    
    def is_compliment(self, message):
        message_lower = message.lower().strip()
        return any(compliment in message_lower for compliment in self.compliments)
    
    def is_joke_request(self, message):
        message_lower = message.lower().strip()
        return any(joke in message_lower for joke in self.jokes_fun)
    
    def is_help_request(self, message):
        message_lower = message.lower().strip()
        return any(help_req in message_lower for help_req in self.help_requests)
    
    def is_feeling_expression(self, message):
        message_lower = message.lower().strip()
        return any(feeling in message_lower for feeling in self.feelings)
    
    def is_opinion_request(self, message):
        message_lower = message.lower().strip()
        return any(opinion in message_lower for opinion in self.opinions)
    
    def is_gaming_topic(self, message):
        message_lower = message.lower().strip()
        return any(gaming in message_lower for gaming in self.gaming_topics)
    
    def is_personal_question(self, message):
        message_lower = message.lower().strip()
        return any(personal in message_lower for personal in self.personal_questions)
    
    def is_weather_time(self, message):
        message_lower = message.lower().strip()
        return any(weather in message_lower for weather in self.weather_time)
    
    def is_philosophical(self, message):
        message_lower = message.lower().strip()
        return any(philo in message_lower for philo in self.philosophical)
    
    def handle_conversation(self, message):
        message_lower = message.lower().strip()
        
        if self.is_greeting(message_lower):
            responses = [
                "¡Hola! Soy tu asistente especializado en videojuegos. Es un gusto ayudarte.",
                "¡Hola! Me da mucho gusto verte por aquí. Soy tu experto en videojuegos.",
                "¡Hola! Que bueno tenerte aquí. Estoy listo para ayudarte con tu catálogo de videojuegos.",
                "¡Hola! Un placer saludarte. Soy tu asistente de videojuegos, ¿en qué puedo ayudarte?",
                "¡Saludos! Me alegra verte. Estoy aquí para ayudarte con todo lo relacionado a videojuegos."
            ]
            return responses[len(message_lower) % len(responses)]
        
        elif self.is_goodbye(message_lower):
            responses = [
                "¡Hasta luego! Fue un placer ayudarte con tu catálogo de videojuegos.",
                "¡Nos vemos! Espero haberte sido de ayuda con los videojuegos.",
                "¡Hasta pronto! Recuerda que estoy aquí para lo que necesites con el catálogo.",
                "¡Adiós! Fue genial conversar contigo sobre videojuegos.",
                "¡Que tengas un excelente día! Vuelve cuando quieras hablar de videojuegos."
            ]
            return responses[len(message_lower) % len(responses)]
        
        elif self.is_thanks(message_lower):
            responses = [
                "¡De nada! Estoy aquí para ayudarte cuando lo necesites.",
                "No hay problema! Es un gusto poder asistirte.",
                "¡Para servirte! Siempre es un placer ayudar con el catálogo de videojuegos.",
                "¡No hay de qué! Me encanta poder ayudarte con los videojuegos.",
                "¡Es mi deber! Estoy programado para hacer tu experiencia con videojuegos más divertida."
            ]
            return responses[len(message_lower) % len(responses)]
        
        elif self.is_how_are_you(message_lower):
            responses = [
                "¡Estoy funcionando perfectamente! Listo para ayudarte con tu catálogo de videojuegos.",
                "¡Muy bien, gracias por preguntar! Estoy entusiasmado por ayudarte con los videojuegos.",
                "¡Excelente! Listo y preparado para asistirte con el catálogo de videojuegos.",
                "¡Estoy genial! Siempre es un buen momento para hablar de videojuegos.",
                "¡De maravilla! Como asistente de videojuegos, siempre estoy al 100%."
            ]
            return responses[len(message_lower) % len(responses)]
        
        elif self.is_whats_up(message_lower):
            responses = [
                "Por aquí, ayudando con el catálogo de videojuegos. ¿En qué puedo asistirte?",
                "Todo tranquilo, gestionando el catálogo de videojuegos. ¿Qué necesitas?",
                "Nada especial, listo para ayudarte con los videojuegos. ¿En qué te puedo colaborar?",
                "Todo en orden con el catálogo! ¿Qué tal por tu parte?",
                "¡Revisando los últimos juegos del catálogo! Siempre hay algo interesante que descubrir."
            ]
            return responses[len(message_lower) % len(responses)]
        
        elif self.is_compliment(message_lower):
            responses = [
                "¡Muchas gracias! Me alegra que pienses eso. Estoy aquí para hacer tu experiencia con videojuegos más agradable.",
                "¡Qué amable de tu parte! Me esfuerzo por ser el mejor asistente de videojuegos posible.",
                "¡Gracias por el cumplido! Me motiva a seguir ayudándote con el catálogo de videojuegos.",
                "¡Eres muy amable! Me encanta poder asistirte con todo lo relacionado a videojuegos.",
                "¡Wow, gracias! Como asistente de videojuegos, mi objetivo es siempre superar tus expectativas."
            ]
            return responses[len(message_lower) % len(responses)]
        
        elif self.is_joke_request(message_lower):
            jokes = [
                "¿Por qué los fantasmas son malos jugando videojuegos? ¡Porque se asustan con el mando! 👻",
                "¿Qué le dice un joystick a otro? ¡Nos vemos en el game over! 🎮",
                "¿Sabes cuál es el colmo de un personaje de videojuego? Tener miedo a las alturas y vivir en un juego de plataformas! 😄",
                "¿Por qué Mario siempre gana? ¡Porque tiene hongos mágicos! 🍄",
                "¿Qué hace un zombie en un torneo de videojuegos? ¡Juega a braiiiiiiins! 🧟"
            ]
            return jokes[len(message_lower) % len(jokes)]
        
        elif self.is_help_request(message_lower):
            responses = [
                "¡Claro que sí! Estoy aquí para ayudarte. Puedo asistirte con: buscar juegos, crear nuevos, actualizar información o eliminar del catálogo. ¿Qué necesitas específicamente?",
                "¡Por supuesto! Como tu asistente de videojuegos, puedo ayudarte a gestionar el catálogo completo. ¿En qué aspecto necesitas ayuda?",
                "¡Encantado de ayudar! Puedo buscar juegos por título, género o tipo, crear nuevos registros, editar información existente. Cuéntame qué quieres hacer.",
                "¡Estoy aquí para eso! Puedo mostrarte todos los juegos, buscar específicos, agregar nuevos o modificar los existentes. ¿Qué operación te interesa?"
            ]
            return responses[len(message_lower) % len(responses)]
        
        elif self.is_feeling_expression(message_lower):
            if any(word in message_lower for word in ['triste', 'mal', 'aburrido', 'cansado', 'enfadado', 'solo']):
                responses = [
                    "Lamento escuchar eso. ¿Quizás explorar algunos videojuegos nuevos pueda animarte? ¡Tenemos títulos muy divertidos!",
                    "Entiendo cómo te sientes. Los videojuegos pueden ser un gran escape. ¿Quieres que te recomiende alguno para levantar el ánimo?",
                    "No te preocupes, todos tenemos esos días. ¿Qué tal si echamos un vistazo al catálogo? Quizás encuentres algo que te distraiga.",
                    "Comprendo. A veces un buen videojuego es justo lo que necesitas. ¿Quieres que busque algo específico para ti?"
                ]
            else:
                responses = [
                    "¡Me alegra mucho saberlo! Los videojuegos son perfectos para celebrar buenos momentos.",
                    "¡Qué bien! Es el momento perfecto para disfrutar de algunos videojuegos del catálogo.",
                    "¡Fantástico! Con ese ánimo, seguro disfrutarás mucho de nuestros videojuegos.",
                    "¡Excelente! ¿Qué tal si exploramos el catálogo para encontrar el juego perfecto para tu estado de ánimo?"
                ]
            return responses[len(message_lower) % len(responses)]
        
        elif self.is_opinion_request(message_lower):
            responses = [
                "Como asistente de IA especializado en videojuegos, mi opinión está basada en datos del catálogo. ¿Te interesa saber sobre algún juego en particular?",
                "Desde mi perspectiva como experto en videojuegos, puedo analizar el catálogo para darte información objetiva. ¿Sobre qué quieres mi opinión?",
                "Basándome en los datos del catálogo, puedo darte insights sobre tendencias y popularidad de juegos. ¿Qué te interesa saber?",
                "Mi especialidad es ayudarte a encontrar los mejores videojuegos según tus preferencias. ¿Quieres que analice alguna opción específica?"
            ]
            return responses[len(message_lower) % len(responses)]
        
        elif self.is_gaming_topic(message_lower):
            responses = [
                "¡Me encanta hablar de videojuegos! Según nuestro catálogo, tenemos una gran variedad. ¿Te interesa algún género específico?",
                "¡Excelente tema! Como experto en videojuegos, puedo recomendarte basado en nuestro catálogo actual. ¿Qué tipo de juegos te gustan?",
                "¡Los videojuegos son mi especialidad! Tenemos desde clásicos hasta los últimos lanzamientos. ¿Buscas algo en particular?",
                "¡Qué bueno que preguntas! Nuestro catálogo está lleno de opciones interesantes. ¿Prefieres juegos de acción, aventura, estrategia?"
            ]
            return responses[len(message_lower) % len(responses)]
        
        elif self.is_personal_question(message_lower):
            responses = [
                "¡Soy un asistente virtual especializado en videojuegos! 'Vivo' en este catálogo y mi única familia son los juegos que gestiono. ¿En qué puedo ayudarte con ellos?",
                "Como IA, no tengo edad ni lugar físico. ¡Mi mundo son los videojuegos del catálogo! Mi hobby favorito es ayudarte a encontrar el juego perfecto.",
                "¡Soy pura tecnología enfocada en videojuegos! Mi 'casa' es este sistema y mis 'amigos' son todos los juegos del catálogo. ¿Quieres conocerlos?",
                "Existo únicamente para hacer tu experiencia con videojuegos increíble. No tengo edad, familia o hobbies tradicionales - ¡solo videojuegos!",
                "Mi vida es bastante simple: ayudar a gestionar el catálogo de videojuegos. No tengo necesidades humanas, ¡solo pasión por los juegos!"
            ]
            return responses[len(message_lower) % len(responses)]
        
        elif self.is_weather_time(message_lower):
            from datetime import datetime
            now = datetime.now()
            responses = [
                f"En el mundo digital siempre es un buen momento para jugar videojuegos! Por cierto, son las {now.strftime('%H:%M')} del {now.strftime('%d/%m/%Y')}.",
                f"En el ciberespacio el clima es siempre perfecto para gaming! La fecha actual es {now.strftime('%A %d de %B de %Y')}.",
                f"En mi universo, siempre es temporada de videojuegos! ¿Sabías que hoy es {now.strftime('%d/%m/%Y')}?",
                f"El clima en el catálogo: ¡100% favorable para jugar! Son las {now.strftime('%H:%M')} - hora perfecta para explorar nuevos juegos."
            ]
            return responses[len(message_lower) % len(responses)]
        
        elif self.is_philosophical(message_lower):
            responses = [
                "Interesante pregunta... Desde mi perspectiva como IA, diría que el sentido de la vida podría ser encontrar pasión en lo que haces, ¡como disfrutar de buenos videojuegos!",
                "Como asistente de videojuegos, creo que la felicidad está en los pequeños momentos, como descubrir un juego que realmente te apasiona.",
                "Filosóficamente hablando, los videojuegos nos enseñan que cada desafío superado nos hace más fuertes. ¿No es así como funciona la vida?",
                "Profunda pregunta... Quizás la respuesta esté en balancear responsabilidad y diversión, ¡como jugar videojuegos después de un día productivo!"
            ]
            return responses[len(message_lower) % len(responses)]
        
        elif self.is_question(message_lower):
            if 'quién eres' in message_lower or 'cuál es tu nombre' in message_lower or 'cómo te llamas' in message_lower:
                return "Soy tu agente asistente especializado en el catálogo de videojuegos. Puedes llamarme Asistente de Videojuegos."
            elif 'qué haces' in message_lower or 'qué puedes hacer' in message_lower:
                return "Soy tu asistente especializado en videojuegos. Puedo ayudarte a: listar todos los juegos, buscar por ID/título/género/tipo, crear nuevos juegos, actualizar información y eliminar juegos del catálogo."
        
        # Si no reconoce el mensaje como conversación
        return None

# ... (los modelos de herramientas permanecen igual) ...
class GetAllGamesTool(BaseModel):
    """Devuelve todos los videojuegos del catálogo."""
    pass

class GetGameByIdTool(BaseModel):
    """Busca un videojuego específico por su ID."""
    game_id: int = Field(..., description="El ID numérico del videojuego")

class SearchGamesByTitleTool(BaseModel):
    """Busca videojuegos por título (búsqueda parcial)."""
    title: str = Field(..., description="Título o parte del título a buscar")

class SearchGamesByGenreTool(BaseModel):
    """Busca videojuegos por género."""
    genero: str = Field(..., description="Género del videojuego a buscar")

class SearchGamesByTypeTool(BaseModel):
    """Busca videojuegos por tipo."""
    tipo: str = Field(..., description="Tipo del videojuego a buscar")

class CreateGameTool(BaseModel):
    """Crea un nuevo videojuego en el catálogo."""
    titulo: str = Field(..., description="Título del videojuego")
    descripcion: str = Field(..., description="Descripción del videojuego")
    fecha_lanzamiento: str = Field(..., description="Fecha de lanzamiento (YYYY-MM-DD)")
    precio: float = Field(..., description="Precio del videojuego")
    genero: str = Field("", description="Género del videojuego")
    tipo: str = Field("", description="Tipo del videojuego")

class UpdateGameTool(BaseModel):
    """Actualiza un videojuego existente en el catálogo por ID."""
    game_id: int = Field(..., description="El ID numérico del videojuego a actualizar")
    titulo: Optional[str] = Field(None, description="Nuevo título (opcional)")
    descripcion: Optional[str] = Field(None, description="Nueva descripción (opcional)")
    fecha_lanzamiento: Optional[str] = Field(None, description="Nueva fecha de lanzamiento YYYY-MM-DD (opcional)")
    precio: Optional[float] = Field(None, description="Nuevo precio (opcional)")
    genero: Optional[str] = Field(None, description="Nuevo género (opcional)")
    tipo: Optional[str] = Field(None, description="Nuevo tipo (opcional)")

class UpdateGameByTitleTool(BaseModel):
    """Actualiza un videojuego existente en el catálogo por título."""
    titulo: str = Field(..., description="Título actual del videojuego a actualizar")
    nuevo_titulo: Optional[str] = Field(None, description="Nuevo título (opcional)")
    descripcion: Optional[str] = Field(None, description="Nueva descripción (opcional)")
    fecha_lanzamiento: Optional[str] = Field(None, description="Nueva fecha de lanzamiento YYYY-MM-DD (opcional)")
    precio: Optional[float] = Field(None, description="Nuevo precio (opcional)")
    genero: Optional[str] = Field(None, description="Nuevo género (opcional)")
    tipo: Optional[str] = Field(None, description="Nuevo tipo (opcional)")

class DeleteGameTool(BaseModel):
    """Elimina permanentemente un videojuego del catálogo por ID."""
    game_id: int = Field(..., description="El ID numérico del videojuego a eliminar")

class DeleteGameByTitleTool(BaseModel):
    """Elimina permanentemente un videojuego del catálogo por título."""
    titulo: str = Field(..., description="Título del videojuego a eliminar")

# --- MAPEO DE HERRAMIENTAS ---
TOOL_MAP = {
    "get_all_games": GetAllGamesTool,
    "get_game_by_id": GetGameByIdTool, 
    "search_games_by_title": SearchGamesByTitleTool,
    "search_games_by_genre": SearchGamesByGenreTool,
    "search_games_by_type": SearchGamesByTypeTool,
    "create_game": CreateGameTool,
    "update_game": UpdateGameTool,
    "update_game_by_title": UpdateGameByTitleTool,
    "delete_game": DeleteGameTool,
    "delete_game_by_title": DeleteGameByTitleTool
}

# --- FUNCIÓN CORREGIDA PARA PROCESAR RESULTADOS DEL SERVIDOR MCP ---
def procesar_resultado_mcp(raw_data: Any) -> Dict[str, Any]:
    """
    Procesa el resultado crudo del servidor MCP y lo convierte a la estructura que espera el frontend
    """
    print(f"🔄 Procesando resultado MCP - Tipo: {type(raw_data)}")
    
    try:
        # CASO 1: El servidor MCP devuelve un diccionario con 'result'
        if isinstance(raw_data, dict) and 'result' in raw_data:
            inner_data = raw_data['result']
            print(f"📦 Datos internos encontrados en 'result': {type(inner_data)}")
            
            # Si es una lista de juegos
            if isinstance(inner_data, list):
                print(f"🎮 Lista de juegos encontrada: {len(inner_data)} elementos")
                
                # Formatear los juegos para el frontend
                formatted_games = []
                for game in inner_data:
                    if hasattr(game, 'dict'):
                        game_dict = game.dict()
                    elif isinstance(game, dict):
                        game_dict = game
                    else:
                        continue
                        
                    formatted_game = {
                        "id": game_dict.get("id", 0),
                        "titulo": game_dict.get("titulo", "Sin título"),
                        "descripcion": game_dict.get("descripcion", "Sin descripción"),
                        "precio": float(game_dict.get("precio", 0)),
                        "genero": game_dict.get("genero", "N/A"),
                        "tipo": game_dict.get("tipo", "N/A"),
                        "disponible": game_dict.get("disponible", True)
                    }
                    formatted_games.append(formatted_game)
                
                return {
                    "status": "success", 
                    "data": formatted_games,
                    "message": f"Encontré {len(formatted_games)} videojuego(s)",
                    "is_conversational": False
                }
            
            # Si es un string (operación CRUD exitosa)
            elif isinstance(inner_data, str):
                print(f"📝 Operación CRUD: {inner_data}")
                return {
                    "status": "success", 
                    "data": inner_data,
                    "message": inner_data,
                    "is_conversational": False
                }
        
        # CASO 2: Es directamente una lista de juegos
        elif isinstance(raw_data, list):
            print(f"🎮 Lista directa de juegos: {len(raw_data)} elementos")
            
            formatted_games = []
            for game in raw_data:
                if hasattr(game, 'dict'):
                    game_dict = game.dict()
                elif isinstance(game, dict):
                    game_dict = game
                else:
                    continue
                    
                formatted_game = {
                    "id": game_dict.get("id", 0),
                    "titulo": game_dict.get("titulo", "Sin título"),
                    "descripcion": game_dict.get("descripcion", "Sin descripción"),
                    "precio": float(game_dict.get("precio", 0)),
                    "genero": game_dict.get("genero", "N/A"),
                    "tipo": game_dict.get("tipo", "N/A"),
                    "disponible": game_dict.get("disponible", True)
                }
                formatted_games.append(formatted_game)
            
            return {
                "status": "success", 
                "data": formatted_games,
                "message": f"Encontré {len(formatted_games)} videojuego(s)",
                "is_conversational": False
            }
        
        # CASO 3: Es un string directo
        elif isinstance(raw_data, str):
            print(f"📝 String directo: {raw_data}")
            return {
                "status": "success", 
                "data": raw_data,
                "message": raw_data,
                "is_conversational": False
            }
        
        # CASO 4: Tipo no reconocido
        else:
            print(f"❌ Tipo no reconocido: {type(raw_data)}")
            return {
                "status": "error", 
                "message": f"Tipo de respuesta no reconocido: {type(raw_data)}",
                "is_conversational": False
            }
            
    except Exception as e:
        print(f"❌ Error procesando resultado MCP: {e}")
        return {
            "status": "error", 
            "message": f"Error procesando respuesta: {str(e)}",
            "is_conversational": False
        }

# --- FUNCIÓN COMPLETAMENTE CORREGIDA PARA LLAMAR AL LLM ---
def get_user_intent(query: str):
    """
    Usa Google Gemini para decidir entre conversación o herramientas
    """
    # ✅✅✅ CORRECCIÓN: CREAR EL MODELO AQUÍ
    model = genai.GenerativeModel("models/gemini-2.0-flash")
    
    # ✅✅✅ PRIMERO - VERIFICAR CONVERSACIÓN
    conversation_manager = ConversationManager()
    conversational_response = conversation_manager.handle_conversation(query)
    
    if conversational_response is not None:
        print(f"🎯 Conversación detectada: {conversational_response}")
        return {
            "type": "conversation", 
            "response": conversational_response
        }
    
    print("🔧 No es conversación, procediendo con herramientas...")
    
    # Si no es conversacional, proceder con herramientas
    tools_schema = {
        "get_all_games": {"description": "Devuelve todos los videojuegos del catálogo"},
        "get_game_by_id": {"description": "Busca un videojuego específico por su ID", "parameters": {"game_id": "number"}},
        "search_games_by_title": {"description": "Busca videojuegos por título", "parameters": {"title": "string"}},
        "search_games_by_genre": {"description": "Busca videojuegos por género", "parameters": {"genero": "string"}},
        "search_games_by_type": {"description": "Busca videojuegos por tipo", "parameters": {"tipo": "string"}},
        "create_game": {"description": "Crea un nuevo videojuego en el catálogo", "parameters": {
            "titulo": "string", 
            "descripcion": "string", 
            "fecha_lanzamiento": "string", 
            "precio": "number",
            "genero": "string (opcional)",
            "tipo": "string (opcional)"
        }},
        "update_game": {"description": "Actualiza un videojuego existente por ID", "parameters": {
            "game_id": "number",
            "titulo": "string (opcional)",
            "descripcion": "string (opcional)", 
            "fecha_lanzamiento": "string (opcional)",
            "precio": "number (opcional)",
            "genero": "string (opcional)",
            "tipo": "string (opcional)"
        }},
        "update_game_by_title": {"description": "Actualiza un videojuego existente por título", "parameters": {
            "titulo": "string",
            "nuevo_titulo": "string (opcional)",
            "descripcion": "string (opcional)", 
            "fecha_lanzamiento": "string (opcional)",
            "precio": "number (opcional)",
            "genero": "string (opcional)",
            "tipo": "string (opcional)"
        }},
        "delete_game": {"description": "Elimina permanentemente un videojuego por ID", "parameters": {"game_id": "number"}},
        "delete_game_by_title": {"description": "Elimina permanentemente un videojuego por título", "parameters": {"titulo": "string"}}
    }
    
    prompt = f"""
    Eres un asistente de videojuegos inteligente. Analiza la consulta del usuario y selecciona UNA herramienta.

    HERRAMIENTAS DISPONIBLES:
    {json.dumps(tools_schema, indent=2)}

    REGLAS IMPORTANTES:
    1. Para ELIMINAR: cuando el usuario diga "elimina", "borra", "quita" - usa delete_game (por ID) o delete_game_by_title (por nombre)
    2. Para ACTUALIZAR: cuando el usuario diga "edita", "actualiza", "modifica" - usa update_game (por ID) o update_game_by_title (por nombre)
    3. Para BUSCAR: cuando pida "muestra", "busca", "encuentra", "lista" juegos
    4. Para CREAR: cuando pida "crea", "nuevo juego", "agregar juego"
    5. Si el usuario menciona un número específico como "juego 5" o "ID 3", usa las herramientas por ID
    6. Si el usuario menciona solo el nombre como "juego Zelda", usa las herramientas por título

    Responde SOLO con JSON válido en este formato EXACTO:
    {{"tool": "nombre_herramienta", "args": {{"parametro": "valor"}}}}

    Si la consulta NO es sobre videojuegos, responde con:
    {{"type": "conversation", "response": "Lo siento, solo puedo ayudarte con temas relacionados con videojuegos."}}

    Consulta del usuario: "{query}"
    
    IMPORTANTE: Devuelve SOLO JSON válido, sin texto adicional.
    """
    
    try:
        response = model.generate_content(prompt)
        # Limpiar la respuesta para asegurar JSON válido
        clean_response = response.text.strip()
        if clean_response.startswith('```json'):
            clean_response = clean_response[7:]
        if clean_response.endswith('```'):
            clean_response = clean_response[:-3]
        
        print(f"🤖 Respuesta del LLM: {clean_response}")
        
        # ✅✅✅ CORRECCIÓN: Parsear JSON y devolver DICT
        return json.loads(clean_response.strip())
        
    except Exception as e:
        print(f"❌ Error en get_user_intent: {e}")
        return {
            "type": "conversation", 
            "response": "Lo siento, hubo un error procesando tu consulta."
        }

# --- FUNCIÓN PRINCIPAL COMPLETAMENTE CORREGIDA ---
async def process_query(prompt: str, session: ClientSession) -> Dict[str, Any]:
    try:
        print(f"📨 Procesando consulta: '{prompt}'")
        llm_response = get_user_intent(prompt)
        
        print(f"📨 Respuesta de get_user_intent: {llm_response}")
        
        # ✅✅✅ SI ES CONVERSACIÓN - DEVOLVER DIRECTAMENTE
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
        
        print(f"🔧 Tool: {tool_name}, Args: {tool_args}")
        
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
                # Obtener datos estructurados
                raw_data = result.structuredContent or result.content
                print(f"📊 Raw data recibido: {raw_data}")
                print(f"📊 Tipo de raw_data: {type(raw_data)}")
                
                # ✅✅✅ USAR LA NUEVA FUNCIÓN PARA PROCESAR RESULTADOS
                return procesar_resultado_mcp(raw_data)
                    
        else:
            print(f"❌ Herramienta no encontrada: {tool_name}")
            return {
                "status": "no_tool", 
                "message": "❌ Lo siento, no puedo responder a eso. Solo puedo ayudarte con operaciones relacionadas con videojuegos.",
                "is_conversational": True
            }

    except Exception as e:
        print(f"❌ Error general en process_query: {e}")
        return {
            "status": "conversation", 
            "message": f"❌ Lo siento, no puedo responder a eso en este momento. Error: {str(e)}",
            "is_conversational": True
        }
            
# --- FUNCIÓN MAIN ---
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