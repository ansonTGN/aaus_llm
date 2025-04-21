import asyncio
import os
import logging
import aiohttp # Import needed for specific error handling

# --- Load environment variables from .env file ---
# Needs: pip install python-dotenv
from dotenv import load_dotenv
load_dotenv() # Looks for .env in the current dir or parent dirs
# --- END Load environment variables ---

# Import the function from the installed package
# Needs: pip install . (or -e .) from the package root directory
try:
    from aaus_llm import consultar_llm_async
except ImportError:
    logging.error("Failed to import aaus_llm. Make sure it's installed (pip install .)")
    # Provide a dummy function to avoid crashing later if import failed
    async def consultar_llm_async(*args, **kwargs):
        raise ImportError("aaus_llm package not found or not installed.")


# Configure logging for the example
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- CONFIGURATION (Now loaded from .env or system environment) ---
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY") # No default needed, check later
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")     # No default needed, check later

# Load image path from .env or use a default/None
DEFAULT_IMAGE_PATH = "image_not_set.jpg" # Or set to None if you prefer
IMAGE_PATH = os.environ.get("IMAGE_PATH", DEFAULT_IMAGE_PATH)

# Load Ollama URL from .env or use default
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

# Check if keys/paths seem valid
if not OPENAI_API_KEY:
    logging.warning("OPENAI_API_KEY not found in environment or .env file. OpenAI examples will fail.")
if not GROQ_API_KEY:
    logging.warning("GROQ_API_KEY not found in environment or .env file. Groq examples will fail.")
if IMAGE_PATH == DEFAULT_IMAGE_PATH:
     logging.warning(f"IMAGE_PATH not found in environment or .env file, using default: '{DEFAULT_IMAGE_PATH}'. Multimodal examples might fail if this file doesn't exist.")
elif not os.path.exists(IMAGE_PATH):
     logging.warning(f"IMAGE_PATH is set to '{IMAGE_PATH}', but the file does not exist. Multimodal examples will fail.")

# --- END CONFIGURATION ---


async def ejemplo_openai_texto():
    logging.info("\n--- Ejemplo OpenAI (Texto) ---")
    if not OPENAI_API_KEY:
        logging.warning("Skipping OpenAI Text: API Key missing.")
        return "Skipped: OpenAI Key missing"
    try:
        respuesta = await consultar_llm_async(
            prompt="¿Quién fue Marie Curie y cuáles fueron sus principales contribuciones?",
            proveedor="openai",
            modelo="gpt-4o",
            api_key=OPENAI_API_KEY,
            temperatura=0.5
        )
        logging.info(f"Respuesta OpenAI (Texto):\n{respuesta}")
        return respuesta
    except ImportError:
         logging.error("Skipping OpenAI Text: aaus_llm not installed.")
         return "Skipped: aaus_llm not installed."
    except Exception as e:
        logging.error(f"Error en ejemplo OpenAI (Texto): {e}")
        return f"Error: {e}"

async def ejemplo_openai_multimodal():
    logging.info("\n--- Ejemplo OpenAI (Multimodal) ---")
    if not OPENAI_API_KEY:
        logging.warning("Skipping OpenAI Multimodal: API Key missing.")
        return "Skipped: OpenAI Key missing"
    if not IMAGE_PATH or not os.path.exists(IMAGE_PATH):
        logging.warning(f"Skipping OpenAI Multimodal: Imagen no encontrada o no configurada ('{IMAGE_PATH}')")
        return f"Skipped: Image not found at '{IMAGE_PATH}'"
    try:
        respuesta = await consultar_llm_async(
            prompt="Describe detalladamente qué ves en esta imagen.",
            proveedor="openai",
            modelo="gpt-4o",
            api_key=OPENAI_API_KEY,
            imagen=IMAGE_PATH
        )
        logging.info(f"Respuesta OpenAI (Multimodal):\n{respuesta}")
        return respuesta
    except ImportError:
         logging.error("Skipping OpenAI Multimodal: aaus_llm not installed.")
         return "Skipped: aaus_llm not installed."
    except Exception as e:
        logging.error(f"Error en ejemplo OpenAI (Multimodal): {e}")
        return f"Error: {e}"

async def ejemplo_groq_texto():
    logging.info("\n--- Ejemplo Groq (Texto) ---")
    if not GROQ_API_KEY:
        logging.warning("Skipping Groq Text: API Key missing.")
        return "Skipped: Groq Key missing"
    try:
        respuesta = await consultar_llm_async(
            prompt="Explica el concepto de 'cloud computing' de forma sencilla usando una analogía.",
            proveedor="groq",
            modelo="llama3-8b-8192",
            api_key=GROQ_API_KEY
        )
        logging.info(f"Respuesta Groq (Texto):\n{respuesta}")
        return respuesta
    except ImportError:
         logging.error("Skipping Groq Text: aaus_llm not installed.")
         return "Skipped: aaus_llm not installed."
    except Exception as e:
        logging.error(f"Error en ejemplo Groq (Texto): {e}")
        return f"Error: {e}"

async def ejemplo_ollama_texto():
    logging.info("\n--- Ejemplo Ollama (Texto Local) ---")
    try:
        respuesta = await consultar_llm_async(
            prompt="¿Qué es Python y para qué se usa principalmente?",
            proveedor="ollama",
            modelo="llama3", # Ensure this model is pulled in Ollama
            url_base=OLLAMA_BASE_URL
        )
        logging.info(f"Respuesta Ollama (Texto):\n{respuesta}")
        return respuesta
    except ImportError:
         logging.error("Skipping Ollama Text: aaus_llm not installed.")
         return "Skipped: aaus_llm not installed."
    except Exception as e:
        if isinstance(e, aiohttp.ClientConnectorError):
             logging.error(f"Error en ejemplo Ollama (Texto): No se pudo conectar a Ollama en '{OLLAMA_BASE_URL}'. ¿Está el servidor corriendo?")
        else:
            logging.error(f"Error en ejemplo Ollama (Texto): {e}")
        return f"Error: {e}"

async def ejemplo_ollama_multimodal():
    logging.info("\n--- Ejemplo Ollama (Multimodal Local) ---")
    # Assumes Ollama server (>= v0.1.29) is running and has a multimodal model
    if not IMAGE_PATH or not os.path.exists(IMAGE_PATH):
        logging.warning(f"Skipping Ollama Multimodal: Imagen no encontrada o no configurada ('{IMAGE_PATH}')")
        return f"Skipped: Image not found at '{IMAGE_PATH}'"
    try:
        respuesta = await consultar_llm_async(
            prompt="Describe la imagen.",
            proveedor="ollama",
            modelo="llava", # Ensure this model is pulled: ollama pull llava
            imagen=IMAGE_PATH,
            url_base=OLLAMA_BASE_URL
        )
        logging.info(f"Respuesta Ollama (Multimodal):\n{respuesta}")
        return respuesta
    except ImportError:
         logging.error("Skipping Ollama Multimodal: aaus_llm not installed.")
         return "Skipped: aaus_llm not installed."
    except Exception as e:
        if isinstance(e, aiohttp.ClientConnectorError):
             logging.error(f"Error en ejemplo Ollama (Multimodal): No se pudo conectar a Ollama en '{OLLAMA_BASE_URL}'. ¿Está el servidor corriendo?")
        elif "model not found" in str(e).lower() or ('parameters' in str(e).lower() and 'images' in str(e).lower()):
             logging.error("Error en ejemplo Ollama (Multimodal): Modelo 'llava' no encontrado o versión de Ollama no soporta imágenes. Asegúrate de tener 'llava' (`ollama pull llava`) y Ollama >= v0.1.29.")
        else:
             logging.error(f"Error en ejemplo Ollama (Multimodal): {e}")
        return f"Error: {e}"


async def main():
    logging.info("Ejecutando ejemplos de aaus_llm (cargando config desde .env)...")

    # Run examples sequentially for clarity in logs
    # Comment/uncomment the examples you want to run:
    await ejemplo_ollama_texto()
    # await ejemplo_ollama_multimodal() # Needs 'llava' model & valid IMAGE_PATH
    # await ejemplo_groq_texto()        # Needs GROQ_API_KEY
    # await ejemplo_openai_texto()      # Needs OPENAI_API_KEY
    # await ejemplo_openai_multimodal() # Needs OPENAI_API_KEY & valid IMAGE_PATH


    # Example of running them in parallel (uncomment to try)
    # logging.info("\n--- Ejecutando tareas en paralelo ---")
    # tareas = []
    # if os.path.exists(IMAGE_PATH): # Only add multimodal if image exists
    #      if OPENAI_API_KEY:
    #         tareas.append(ejemplo_openai_multimodal())
    #      tareas.append(ejemplo_ollama_multimodal())
    # else:
    #      logging.warning("Skipping parallel multimodal tasks due to missing image.")

    # if OPENAI_API_KEY:
    #     tareas.append(ejemplo_openai_texto())
    # if GROQ_API_KEY:
    #     tareas.append(ejemplo_groq_texto())
    # tareas.append(ejemplo_ollama_texto())

    # if tareas:
    #      resultados = await asyncio.gather(*tareas, return_exceptions=True) # Capture exceptions too
    #      logging.info("\n--- Resultados Paralelos ---")
    #      for i, res in enumerate(resultados):
    #          if isinstance(res, Exception):
    #              logging.error(f"Tarea paralela {i+1} falló: {res}")
    #          else:
    #              logging.info(f"Resultado Tarea paralela {i+1}: {str(res)[:150]}...") # Print truncated results
    # else:
    #      logging.warning("No tasks were added for parallel execution (check API keys/image path).")

if __name__ == "__main__":
    # To run this example:
    # 1. Install the aaus_llm package (`pip install .` or `pip install -e .`)
    # 2. Install python-dotenv (`pip install python-dotenv`)
    # 3. Create a .env file in this directory with your API Keys (OPENAI_API_KEY, GROQ_API_KEY)
    #    and optionally IMAGE_PATH and OLLAMA_BASE_URL.
    # 4. Ensure Ollama server is running (for Ollama tests) and models are pulled (`ollama pull llama3`, `ollama pull llava`).
    # 5. Run this script: python usage_example.py
    asyncio.run(main())