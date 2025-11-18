from flask import Flask, request, jsonify
from agente_noticias import main as agent_main
import asyncio
import json

app = Flask(__name__)

@app.route("/query", methods=["POST"])
@app.route("/agente/noticias/query", methods=["POST"])
def procesar_consulta():
    """
    Endpoint para procesar consultas sobre noticias - SIN VERIFICACIÓN DE ADMIN
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
        
        print(f"📩 Consulta recibida: {consulta}")
        
        # ✅ EJECUTAR AGENTE SIN VERIFICAR PERMISOS DE ADMIN
        resultado = asyncio.run(agent_main(consulta))
        
        print(f"✅ Resultado generado")
        
        return jsonify({
            "consulta_original": consulta,
            "resultado": resultado
        })
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({
            "error": f"Error interno del servidor: {str(e)}"
        }), 500

@app.route("/health", methods=["GET"])
@app.route("/agente/noticias/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "servicio": "Agente de Noticias",
        "mensaje": "Servicio funcionando correctamente"
    })

@app.route("/", methods=["GET"])
@app.route("/agente/noticias", methods=["GET"])
def info():
    return jsonify({
        "servicio": "Agente de Noticias - API",
        "endpoints": {
            "POST /query": "Procesar consultas sobre noticias",
            "GET /health": "Verificar estado del servicio",
            "GET /": "Información del servicio"
        }
    })

if __name__ == "__main__":
    print("API de Agente de Noticias iniciada - TODAS LAS HERRAMIENTAS ACTIVAS")
    app.run(debug=True, host="0.0.0.0", port=5001)