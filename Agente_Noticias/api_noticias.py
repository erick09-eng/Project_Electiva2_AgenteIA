from flask import Flask, request, jsonify
from flask_cors import CORS
from agente_noticias import main as agent_main
import asyncio
import json

app = Flask(__name__)
CORS(app)

@app.route("/query", methods=["POST"])
def procesar_consulta():
    """
    Endpoint para procesar consultas sobre noticias
    """
    try:
        datos = request.get_json()
        if not datos or "consulta" not in datos:
            return jsonify({
                "error": "El cuerpo debe ser JSON con la clave 'consulta'"
            }), 400
        
        consulta = datos.get("consulta", "").strip()
        if not consulta:
            return jsonify({
                "error": "La consulta no puede estar vacía"
            }), 400
        
        # Ejecutar el agente de forma asíncrona
        resultado = asyncio.run(agent_main(consulta))
        
        return jsonify({
            "consulta_original": consulta,
            "resultado": resultado
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Error interno del servidor: {str(e)}"
        }), 500

@app.route("/health", methods=["GET"])
def health_check():
    """Endpoint para verificar que el servicio está funcionando"""
    return jsonify({
        "status": "ok",
        "servicio": "Agente de Noticias",
        "mensaje": "Servicio funcionando correctamente"
    })

@app.route("/", methods=["GET"])
def info():
    """Endpoint de información del servicio"""
    return jsonify({
        "servicio": "Agente de Noticias - API",
        "endpoints": {
            "POST /query": "Procesar consultas sobre noticias",
            "GET /health": "Verificar estado del servicio",
            "GET /": "Información del servicio"
        },
        "ejemplos_consulta": [
            "Mostrar todas las noticias",
            "Buscar noticias sobre tecnología",
            "Obtener la noticia con ID 1",
            "Crear noticia titulo 'Nueva noticia' contenido 'Texto' fecha '2024-10-05'"
        ]
    })

if __name__ == "__main__":
    print("API de Agente de Noticias iniciada")
    print("Endpoint principal: POST http://localhost:5001/query")  # Puerto diferente
    print("Health check: GET http://localhost:5001/health")
    app.run(debug=True, host="0.0.0.0", port=5001)  # Puerto 5001 para no conflictos