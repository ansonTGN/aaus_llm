Okay, here is a Markdown file (`INSTALL_AND_USAGE.md`) optimized for clarity based on your provided text:

```markdown
# ⚙️ Instalación y Uso Básico de `aaus_llm`

Esta guía te mostrará cómo instalar y empezar a usar la biblioteca `aaus_llm` en tus propios scripts de Python.

## 1. Instalación

Para instalar la biblioteca, primero necesitas navegar a la carpeta raíz del paquete (la que contiene el archivo `pyproject.toml`).

*   **Abre tu terminal o línea de comandos.**
*   **Navega al directorio `aaus_llm_package`**:
    ```bash
    cd ruta/a/tu/aaus_llm_package
    ```
    *(Reemplaza `ruta/a/tu/` con la ruta real)*

Luego, tienes dos opciones para la instalación:

*   **Instalación estándar:** Ideal para usar la biblioteca tal como está.
    ```bash
    pip install .
    ```

*   **Instalación en modo editable:** Recomendada si planeas modificar el código fuente de `aaus_llm`. Los cambios que hagas se reflejarán inmediatamente sin necesidad de reinstalar.
    ```bash
    pip install -e .
    ```

## 2. Uso Básico en un Script Python

Una vez instalada, puedes importar y usar la función `consultar_llm_async` en cualquier script Python.

**Prerrequisitos para el ejemplo:**

*   Asegúrate de que la biblioteca `aaus_llm` esté instalada (ver paso 1).
*   **Para OpenAI/Groq:** Necesitarás una API Key. Es recomendable configurarla como variable de entorno (ej., `OPENAI_API_KEY`).
*   **Para Ollama:** Asegúrate de que el servidor de Ollama esté corriendo localmente (usualmente en `http://localhost:11434`).
*   **Para ejemplos multimodales:** Ten a mano la ruta a un archivo de imagen.

**Ejemplo de Script (`mi_script.py`):**

```python
import asyncio
import aaus_llm  # Importa la biblioteca instalada
import os      # Para leer variables de entorno (API Keys)
import logging # Para ver los logs del SDK

# Configurar logging para ver info y errores
logging.basicConfig(level=logging.INFO)

async def run_llm_queries():
    """
    Función asíncrona para realizar consultas a los LLMs.
    """
    print("--- Iniciando consultas LLM ---")

    try:
        # --- Ejemplo 1: Consulta a Ollama (local) ---
        # Asegúrate de que Ollama esté corriendo y tenga el modelo 'llama3'
        print("\n[1] Consultando Ollama...")
        respuesta_ollama = await aaus_llm.consultar_llm_async(
            prompt="Explica qué es la recursividad en programación con un ejemplo simple.",
            proveedor="ollama",
            modelo="llama3" # Asegúrate de tener este modelo con 'ollama pull llama3'
            # url_base="http://mi-ollama-server:11434" # Descomenta si Ollama no está en localhost
        )
        print("\n✅ Respuesta de Ollama:")
        print(respuesta_ollama)

    except Exception as e:
        logging.error(f"❌ Error consultando Ollama: {e}")
        print("\n❌ Falló la consulta a Ollama. Asegúrate de que el servidor esté activo y el modelo exista.")

    try:
        # --- Ejemplo 2: Consulta a OpenAI ---
        # Requiere la API Key de OpenAI (preferiblemente como variable de entorno)
        print("\n[2] Consultando OpenAI...")
        openai_key = os.environ.get("OPENAI_API_KEY")

        if openai_key:
            respuesta_openai = await aaus_llm.consultar_llm_async(
                prompt="Dame 3 ideas creativas para un nombre de una cafetería temática de gatos.",
                proveedor="openai",
                api_key=openai_key,
                modelo="gpt-4o", # Modelo recomendado actualmente
                temperatura=0.8 # Un poco más creativo
            )
            print("\n✅ Respuesta de OpenAI:")
            print(respuesta_openai)
        else:
            print("\n⚠️ Saltando ejemplo OpenAI: Variable de entorno OPENAI_API_KEY no encontrada.")
            logging.warning("Variable de entorno OPENAI_API_KEY no configurada.")

    except Exception as e:
        logging.error(f"❌ Error consultando OpenAI: {e}")
        print("\n❌ Falló la consulta a OpenAI.")

    # --- Ejemplo 3: Consulta multimodal con OpenAI (Opcional) ---
    # try:
    #     print("\n[3] Consultando OpenAI con imagen...")
    #     openai_key = os.environ.get("OPENAI_API_KEY")
    #     image_file = "ruta/a/tu/imagen.jpg" # <-- ¡Actualiza esta ruta!

    #     if openai_key and os.path.exists(image_file):
    #         respuesta_multimodal = await aaus_llm.consultar_llm_async(
    #             prompt="Describe la escena principal en esta imagen.",
    #             proveedor="openai",
    #             api_key=openai_key,
    #             modelo="gpt-4o",
    #             imagen=image_file
    #         )
    #         print("\n✅ Respuesta Multimodal de OpenAI:")
    #         print(respuesta_multimodal)
    #     elif not openai_key:
    #          print("\n⚠️ Saltando ejemplo OpenAI Multimodal: Variable de entorno OPENAI_API_KEY no encontrada.")
    #     else:
    #          print(f"\n⚠️ Saltando ejemplo OpenAI Multimodal: Archivo de imagen no encontrado en '{image_file}'.")
    #          logging.warning(f"Archivo de imagen no encontrado: {image_file}")

    # except Exception as e:
    #      logging.error(f"❌ Error consultando OpenAI con imagen: {e}")
    #      print("\n❌ Falló la consulta multimodal a OpenAI.")


    print("\n--- Consultas finalizadas ---")

# --- Punto de entrada principal ---
if __name__ == "__main__":
    # Ejecuta la función asíncrona principal
    try:
        asyncio.run(run_llm_queries())
    except KeyboardInterrupt:
        print("\nEjecución interrumpida por el usuario.")
```

**Para ejecutar el script:**

1.  Guarda el código anterior como un archivo Python (e.g., `mi_script.py`).
2.  **Opcional:** Configura las variables de entorno `OPENAI_API_KEY` y/o `GROQ_API_KEY` si vas a usar esos proveedores.
3.  **Opcional:** Si usas Ollama, asegúrate de que el servidor esté activo (`ollama serve`).
4.  **Opcional:** Si pruebas el ejemplo multimodal, actualiza `ruta/a/tu/imagen.jpg` a la ruta real de tu imagen.
5.  Ejecuta el script desde tu terminal:
    ```bash
    python mi_script.py
    ```

---

¡Listo! Ahora tienes un paquete Python estándar `aaus_llm` instalado y listo para ser utilizado en tus proyectos. Recuerda gestionar tus API Keys de forma segura y asegurarte de que los servicios como Ollama estén disponibles cuando los necesites.
```