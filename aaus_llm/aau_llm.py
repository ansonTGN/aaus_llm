import aiohttp
import asyncio
import openai # Make sure this matches the version dependency in pyproject.toml
import base64
import logging
from typing import Optional # Good practice for type hints

# Configurar log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- IMPORTANT ---
# The OpenAI call below uses syntax for openai < 1.0.0
# If you install openai >= 1.0.0, you MUST refactor this part.
# Example refactor for OpenAI >= 1.0.0 is commented out below the original.

async def consultar_llm_async(
    prompt: str,
    proveedor: str,
    modelo: Optional[str] = None,
    temperatura: float = 0.7,
    api_key: Optional[str] = None,
    url_base: Optional[str] = None,
    imagen: Optional[str] = None,
    timeout: int = 30
    ) -> str:
    """
    Consulta un LLM de varios proveedores de forma asíncrona, soportando texto e imágenes.

    :param prompt: El texto o pregunta
    :param proveedor: "ollama", "groq" o "openai"
    :param modelo: Modelo a usar (opcional)
    :param temperatura: Creatividad de la respuesta
    :param api_key: Clave de API si aplica
    :param url_base: URL base para Ollama si aplica (default: http://localhost:11434)
    :param imagen: Ruta local a imagen para consultas multimodales
    :param timeout: Tiempo máximo de espera por consulta (en segundos)
    :return: Respuesta generada
    :raises ValueError: Si el proveedor no es soportado o falta API Key.
    :raises Exception: Si la consulta falla después de los reintentos.
    """
    retries = 3
    delay = 2  # segundos entre reintentos

    for intento in range(retries):
        try:
            logger.info(f"Intento {intento+1}/{retries} para proveedor '{proveedor}' con prompt: '{prompt[:50]}...'")

            if proveedor == "ollama":
                effective_url_base = url_base or "http://localhost:11434"
                effective_modelo = modelo or "llama3"
                logger.info(f"Usando Ollama: modelo={effective_modelo}, url={effective_url_base}")

                payload = {"model": effective_modelo, "prompt": prompt, "temperature": temperatura, "stream": False} # Ensure stream is False

                if imagen:
                    try:
                        with open(imagen, "rb") as f:
                            img_base64 = base64.b64encode(f.read()).decode('utf-8')
                        payload["images"] = [img_base64]
                        logger.info(f"Imagen {imagen} adjuntada para Ollama.")
                    except FileNotFoundError:
                        logger.error(f"Error: Archivo de imagen no encontrado en {imagen}")
                        raise FileNotFoundError(f"Archivo de imagen no encontrado: {imagen}")
                    except Exception as img_err:
                        logger.error(f"Error al procesar imagen {imagen}: {img_err}")
                        raise img_err

                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                    # Ollama generate endpoint is POST /api/generate
                    api_url = f"{effective_url_base.rstrip('/')}/api/generate"
                    logger.debug(f"Ollama request payload: {payload}")
                    async with session.post(api_url, json=payload) as resp:
                        resp.raise_for_status() # Raise exception for bad status codes (4xx or 5xx)
                        data = await resp.json()
                        logger.debug(f"Ollama raw response: {data}")
                        if "response" not in data:
                             # Handle potential error structure from Ollama
                             error_msg = data.get("error", "Respuesta inesperada de Ollama sin campo 'response'")
                             logger.error(f"Error de Ollama: {error_msg}")
                             raise ValueError(f"Error de Ollama: {error_msg}")
                        return data["response"].strip()


            elif proveedor == "groq":
                if not api_key:
                    raise ValueError("Se requiere API Key para Groq")

                effective_modelo = modelo or "llama3-8b-8192" # Use a common default like llama3
                logger.info(f"Usando Groq: modelo={effective_modelo}")

                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                message_content = [{"type": "text", "text": prompt}]

                if imagen:
                    # Groq currently does not support images via API, log warning
                    logger.warning(f"Proveedor 'groq' no soporta imágenes actualmente. La imagen '{imagen}' será ignorada.")
                    # Do not add image data to the payload

                payload = {
                    "model": effective_modelo,
                    "messages": [{"role": "user", "content": message_content[0]['text']}], # Groq expects simple text content here
                    "temperature": temperatura,
                    "stream": False,
                }

                api_url = "https://api.groq.com/openai/v1/chat/completions"

                async with aiohttp.ClientSession(headers=headers, timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                    logger.debug(f"Groq request payload: {payload}")
                    async with session.post(api_url, json=payload) as resp:
                        resp.raise_for_status()
                        data = await resp.json()
                        logger.debug(f"Groq raw response: {data}")
                        if not data.get("choices"):
                            error_msg = data.get("error", {}).get("message", "Respuesta inesperada de Groq sin 'choices'")
                            logger.error(f"Error de Groq: {error_msg}")
                            raise ValueError(f"Error de Groq: {error_msg}")
                        return data["choices"][0]["message"]["content"].strip()


            elif proveedor == "openai":
                if not api_key:
                    raise ValueError("Se requiere API Key para OpenAI")

                # === Código para openai < 1.0.0 ===
                openai.api_key = api_key
                effective_modelo = modelo or "gpt-4o" # Use gpt-4o as a modern default
                logger.info(f"Usando OpenAI: modelo={effective_modelo}")

                message_content = []
                message_content.append({"type": "text", "text": prompt})

                if imagen:
                    try:
                        with open(imagen, "rb") as f:
                            img_base64 = base64.b64encode(f.read()).decode('utf-8')
                        # Correct format for multimodal GPT-4 Turbo / GPT-4o
                        message_content.append({
                             "type": "image_url",
                             "image_url": {
                                 "url": f"data:image/jpeg;base64,{img_base64}" # Assuming jpeg/png common formats
                             }
                        })
                        logger.info(f"Imagen {imagen} adjuntada para OpenAI.")
                    except FileNotFoundError:
                         logger.error(f"Error: Archivo de imagen no encontrado en {imagen}")
                         raise FileNotFoundError(f"Archivo de imagen no encontrado: {imagen}")
                    except Exception as img_err:
                         logger.error(f"Error al procesar imagen {imagen}: {img_err}")
                         raise img_err
                else:
                     # If no image, use the simple string content format
                     message_content = prompt # Override list format

                messages = [{"role": "user", "content": message_content}]

                logger.debug(f"OpenAI request messages (content truncated if long): {[{'role': m['role'], 'content': str(m['content'])[:100]+'...' if isinstance(m['content'], str) and len(m['content'])>100 else m['content']} for m in messages]}")

                # Using the older <1.0.0 async call
                chat_completion = await openai.ChatCompletion.acreate(
                    model=effective_modelo,
                    messages=messages,
                    temperature=temperatura,
                    # max_tokens=1024, # Optional: limit response length
                    timeout=timeout # Pass timeout to the API call if supported
                )
                logger.debug(f"OpenAI raw response: {chat_completion}")
                if not chat_completion.choices:
                    logger.error("Respuesta inesperada de OpenAI sin 'choices'")
                    raise ValueError("Respuesta inesperada de OpenAI sin 'choices'")
                return chat_completion.choices[0].message['content'].strip() # Access content correctly

                # === FIN Código para openai < 1.0.0 ===

                # === Código para openai >= 1.0.0 (REFACTOR - uncomment y reemplaza lo anterior si usas >=1.0) ===
                # from openai import AsyncOpenAI # Import at top
                # client = AsyncOpenAI(api_key=api_key, timeout=timeout)
                # effective_modelo = modelo or "gpt-4o"
                # logger.info(f"Usando OpenAI (>=1.0): modelo={effective_modelo}")
                #
                # message_content = []
                # message_content.append({"type": "text", "text": prompt})
                #
                # if imagen:
                #     try:
                #         with open(imagen, "rb") as f:
                #              img_base64 = base64.b64encode(f.read()).decode('utf-8')
                #         # Correct format for multimodal GPT-4 Turbo / GPT-4o
                #         message_content.append({
                #              "type": "image_url",
                #              "image_url": {
                #                  # OpenAI prefers direct base64 for clarity
                #                  "url": f"data:image/jpeg;base64,{img_base64}" # Or detect image type
                #              }
                #         })
                #         logger.info(f"Imagen {imagen} adjuntada para OpenAI.")
                #     except FileNotFoundError:
                #          logger.error(f"Error: Archivo de imagen no encontrado en {imagen}")
                #          raise FileNotFoundError(f"Archivo de imagen no encontrado: {imagen}")
                #     except Exception as img_err:
                #          logger.error(f"Error al procesar imagen {imagen}: {img_err}")
                #          raise img_err
                #
                # messages = [{"role": "user", "content": message_content}]
                #
                # logger.debug(f"OpenAI request messages (content truncated if long): {[{'role': m['role'], 'content': str(m['content'])[:100]+'...' if isinstance(m['content'], list) else m['content']} for m in messages]}")
                #
                # chat_completion = await client.chat.completions.create(
                #     model=effective_modelo,
                #     messages=messages,
                #     temperature=temperatura,
                #     # max_tokens=1024, # Optional
                # )
                # logger.debug(f"OpenAI raw response: {chat_completion}")
                # if not chat_completion.choices:
                #      logger.error("Respuesta inesperada de OpenAI sin 'choices'")
                #      raise ValueError("Respuesta inesperada de OpenAI sin 'choices'")
                # return chat_completion.choices[0].message.content.strip()
                # === FIN Código para openai >= 1.0.0 ===

            else:
                raise ValueError(f"Proveedor '{proveedor}' no soportado. Use 'ollama', 'groq' o 'openai'.")

        except aiohttp.ClientResponseError as http_err:
            logger.error(f"Error HTTP en intento {intento+1}/{retries} para {proveedor}: {http_err.status} {http_err.message}")
            # Log response body if available for debugging
            try:
                error_body = await http_err.response.text()
                logger.error(f"Error Body: {error_body[:500]}") # Log first 500 chars
            except Exception:
                 logger.error("No se pudo leer el cuerpo del error HTTP.")

            if intento < retries - 1:
                logger.info(f"Reintentando en {delay} segundos...")
                await asyncio.sleep(delay)
            else:
                logger.error(f"Falló después de {retries} intentos para {proveedor}.")
                raise http_err # Re-raise the final HTTP error
        except aiohttp.ClientError as client_err: # Includes connection errors, timeouts
             logger.error(f"Error de Cliente/Red en intento {intento+1}/{retries} para {proveedor}: {client_err}")
             if intento < retries - 1:
                 logger.info(f"Reintentando en {delay} segundos...")
                 await asyncio.sleep(delay)
             else:
                 logger.error(f"Falló después de {retries} intentos para {proveedor}.")
                 raise client_err # Re-raise the final client error
        except ValueError as val_err: # Catch specific config errors like missing API keys
             logger.error(f"Error de configuración para {proveedor}: {val_err}")
             raise val_err # Do not retry configuration errors
        except FileNotFoundError as fnf_err: # Catch file not found for images
            logger.error(f"Error de archivo: {fnf_err}")
            raise fnf_err # Do not retry file not found errors
        except Exception as e:
            logger.error(f"Error inesperado en intento {intento+1}/{retries} para {proveedor}: {e.__class__.__name__}: {e}")
            if intento < retries - 1:
                logger.info(f"Reintentando en {delay} segundos...")
                await asyncio.sleep(delay)
            else:
                logger.error(f"Falló después de {retries} intentos para {proveedor}.")
                raise e # Re-raise the final unexpected error