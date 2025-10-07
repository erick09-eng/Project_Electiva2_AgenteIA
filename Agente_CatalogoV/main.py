import asyncio
import sys
from agente_catalogo_videojuegos import main

def ejecutar_agente():
    """
    Punto de entrada principal para el agente de videojuegos
    """
    print("🎮 Agente de Videojuegos - Modo Consola")
    print("========================================")
    print("Comandos:")
    print("  - Escribe tu consulta sobre videojuegos")
    print("  - 'salir' para terminar")
    print("  - 'api' para iniciar el servidor API")
    print()
    
    if len(sys.argv) > 1:
        # Modo comando único
        query = " ".join(sys.argv[1:])
        print(f"🔍 Consulta: {query}")
        resultado = asyncio.run(main(query))
        print("📦 Resultado:")
        print(resultado)
        return
    
    # Modo interactivo
    while True:
        try:
            consulta = input("\n🎯 Tu consulta: ").strip()
            
            if consulta.lower() in ['salir', 'exit', 'quit']:
                print("👋 ¡Hasta luego!")
                break
            elif consulta.lower() == 'api':
                print("🚀 Iniciando servidor API...")
                from api_catalogo_videojuegos import app
                app.run(debug=True, host="0.0.0.0", port=5000)
                break
            elif consulta:
                print("⏳ Procesando...")
                resultado = asyncio.run(main(consulta))
                print("📦 Resultado:")
                print(resultado)
            else:
                print("❌ Por favor, escribe una consulta válida")
                
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    ejecutar_agente()