import asyncio
import os
import logging

# Import the function from the installed package
from aaus_llm import consultar_llm_async

# Configure logging for the example
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- CONFIGURATION ---
# !! IMPORTANT: Set your API keys as environment variables or replace placeholders !!
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "TU_API_KEY_OPENAI")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "TU_API_KEY_GROQ")

# !! IMPORTANT: Set the correct path to your image file !!
IMAGE_PATH = "path/to/your/imagen.jpg" # Replace with actual path or None

# Check if keys are set (basic check)
if "TU_API_KEY" in OPENAI_API_KEY:
    logging.warning("OpenAI API Key not set. OpenAI examples will likely fail.")
if "TU_API_KEY" in GROQ_API_KEY:
    logging.warning("Groq API Key not set. Groq examples will likely fail.")
# --- END CONFIGURATION ---


async def ejemplo_openai_texto():
    logging.info("\n--- Ejemplo OpenAI (Texto) ---")
    if "TU_API_KEY" in OPENAI_API_KEY: return "Skipped: OpenAI Key missing"
    try:
        respuesta = await consultar_llm_async(
            prompt="¿Quién fue Marie Curie?",
            proveedor="openai",
            modelo="gpt-4o", # Or gpt-4, gpt-3.5-turbo etc.
            api_key=OPENAI_API_KEY,
            temperatura=0.5
        )
        logging.info(f"Respuesta OpenAI (Texto):\n{respuesta}")
        return respuesta
    except Exception as e:
        logging.error(f"Error en ejemplo OpenAI (Texto): {e}")
        return f"Error: {e}"

async def ejemplo_openai_multimodal():
    logging.info("\n--- Ejemplo OpenAI (Multimodal) ---")
    if "TU_API_KEY" in OPENAI_API_KEY: return "Skipped: OpenAI Key missing"
    if not IMAGE_PATH or not os.path.exists(IMAGE_PATH):
        logging.warning(f"Skipping OpenAI Multimodal: Imagen no encontrada en '{IMAGE_PATH}'")
        return "Skipped: Image not found"
    try:
        respuesta = await consultar_llm_async(
            prompt="Describe detalladamente qué ves en esta imagen.",
            proveedor="openai",
            modelo="gpt-4o", # gpt-4-vision-preview is older, gpt-4o is recommended
            api_key=OPENAI_API_KEY,
            imagen=IMAGE_PATH
        )
        logging.info(f"Respuesta OpenAI (Multimodal):\n{respuesta}")
        return respuesta
    except Exception as e:
        logging.error(f"Error en ejemplo OpenAI (Multimodal): {e}")
        return f"Error: {e}"

async def ejemplo_groq_texto():
    logging.info("\n--- Ejemplo Groq (Texto) ---")
    if "TU_API_KEY" in GROQ_API_KEY: return "Skipped: Groq Key missing"
    try:
        respuesta = await consultar_llm_async(
            prompt="Explica el concepto de 'cloud computing' de forma sencilla.",
            proveedor="groq",
            modelo="llama3-8b-8192", # Or mixtral-8x7b-32768
            api_key=GROQ_API_KEY
        )
        logging.info(f"Respuesta Groq (Texto):\n{respuesta}")
        return respuesta
    except Exception as e:
        logging.error(f"Error en ejemplo Groq (Texto): {e}")
        return f"Error: {e}"

async def ejemplo_ollama_texto():
    logging.info("\n--- Ejemplo Ollama (Texto Local) ---")
    # Assumes Ollama server is running at http://localhost:11434
    try:
        respuesta = await consultar_llm_async(
            prompt="¿Qué es Python?",
            proveedor="ollama",
            modelo="llama3", # Or another model you have pulled in Ollama
            # url_base="http://your-ollama-server:11434" # Optional: if not localhost
        )
        logging.info(f"Respuesta Ollama (Texto):\n{respuesta}")
        return respuesta
    except Exception as e:
        # Common error: Ollama server not running
        if isinstance(e, aiohttp.ClientConnectorError):
             logging.error("Error en ejemplo Ollama (Texto): No se pudo conectar a Ollama. ¿Está el servidor corriendo en http://localhost:11434?")
        else:
            logging.error(f"Error en ejemplo Ollama (Texto): {e}")
        return f"Error: {e}"

async def ejemplo_ollama_multimodal():
    logging.info("\n--- Ejemplo Ollama (Multimodal Local) ---")
    # Assumes Ollama server (>= v0.1.29) is running and has a multimodal model like llava
    if not IMAGE_PATH or not os.path.exists(IMAGE_PATH):
        logging.warning(f"Skipping Ollama Multimodal: Imagen no encontrada en '{IMAGE_PATH}'")
        return "Skipped: Image not found"
    try:
        respuesta = await consultar_llm_async(
            prompt="Describe la imagen.",
            proveedor="ollama",
            modelo="llava", # Make sure you have a multimodal model like 'llava' pulled
            imagen=IMAGE_PATH,
            # url_base="http://your-ollama-server:11434" # Optional
        )
        logging.info(f"Respuesta Ollama (Multimodal):\n{respuesta}")
        return respuesta
    except Exception as e:
        if isinstance(e, aiohttp.ClientConnectorError):
             logging.error("Error en ejemplo Ollama (Multimodal): No se pudo conectar a Ollama. ¿Está el servidor corriendo?")
        elif "model not found" in str(e).lower():
             logging.error("Error en ejemplo Ollama (Multimodal): Modelo multimodal (ej. 'llava') no encontrado. Asegúrate de haberlo descargado con 'ollama pull llava'.")
        else:
             logging.error(f"Error en ejemplo Ollama (Multimodal): {e}")
        return f"Error: {e}"


async def main():
    logging.info("Ejecutando ejemplos de aaus_llm...")

    # Run examples sequentially for clarity in logs
    # await ejemplo_openai_texto()
    # await ejemplo_openai_multimodal()
    # await ejemplo_groq_texto()
    await ejemplo_ollama_texto()
    # await ejemplo_ollama_multimodal()

    # Or run them in parallel (faster, logs might interleave)
    # print("\n--- Ejecutando tareas en paralelo ---")
    # tareas = [
    #     ejemplo_openai_texto(),
    #     ejemplo_openai_multimodal(),
    #     ejemplo_groq_texto(),
    #     ejemplo_ollama_texto(),
    #     ejemplo_ollama_multimodal(),
    # ]
    # resultados = await asyncio.gather(*tareas)
    # print("\n--- Resultados Paralelos ---")
    # for i, res in enumerate(resultados):
    #     print(f"Resultado Tarea {i+1}: {res[:100]}...") # Print truncated results

if __name__ == "__main__":
    # To run this example:
    # 1. Make sure you have installed the aaus_llm package (`pip install .` from the aaus_llm_package directory)
    # 2. Set Environment Variables OPENAI_API_KEY, GROQ_API_KEY (optional)
    # 3. Update IMAGE_PATH to a valid image file (optional, for multimodal tests)
    # 4. Ensure Ollama server is running (optional, for Ollama tests)
    # 5. Run this script: python usage_example.py
    asyncio.run(main())