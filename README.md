```markdown
# 📘 aaus_llm SDK Documentation

`aaus_llm` is a lightweight, asynchronous, and extensible SDK designed to interact with Large Language Models (LLMs) from three different providers: **OpenAI**, **Groq**, and **Ollama**. It supports both text-only and multimodal (text + image) queries.

---

## 🧠 Core Function: `consultar_llm_async`

This asynchronous function allows you to send a query to your chosen LLM provider and receive an AI-generated response.

### 📄 Signature

```python
from typing import Optional

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
    # ... implementation ...
```

### 🚀 Parameters

| Parámetro     | Tipo            | Requerido        | Descripción                                                                     |
| :------------ | :-------------- | :--------------- | :------------------------------------------------------------------------------ |
| `prompt`      | `str`           | ✅ Sí            | The message or question sent to the model.                                      |
| `proveedor`   | `str`           | ✅ Sí            | One of: `"openai"`, `"groq"`, `"ollama"`.                                       |
| `modelo`      | `str`           | Opcional         | Name of the specific model. If omitted, a default is used per provider.       |
| `temperatura` | `float`         | Opcional         | Controls model creativity (0.0 = deterministic, 1.0 = more random). Default: 0.7. |
| `api_key`     | `str`           | Solo si aplica   | Required for OpenAI and Groq. Not needed for local Ollama.                      |
| `url_base`    | `str`           | Solo para Ollama | Base URL for the Ollama server (default: `http://localhost:11434`).             |
| `imagen`      | `str`           | Opcional         | Path to the image file (only supported by OpenAI and Ollama).                 |
| `timeout`     | `int`           | Opcional         | Maximum wait time (in seconds) for the response. Default: 30.                   |

---

## 🧠 Supported Providers

| Provider | Recommended Models        | Image Support?              | API Key Required?      |
| :------- | :------------------------ | :-------------------------- | :--------------------- |
| `openai` | `gpt-4`, `gpt-4o`         | ✅ Yes                      | ✅ Yes                 |
| `groq`   | `mixtral-8x7b-32768`, `llama3-8b-8192` | ❌ No                       | ✅ Yes                 |
| `ollama` | `llama3`, `mistral`, `llava`, etc. | ✅ Yes (Ollama >= v0.1.29) | ❌ No (if local)     |

*Note: Default models may change. Refer to the code or provider documentation for current defaults.*

---

## 🧪 Examples

### 🔹 Basic Multimodal Query (OpenAI)

```python
import asyncio
import aaus_llm
import os

# Assumes OPENAI_API_KEY environment variable is set
# Assumes 'foto.jpg' exists in the same directory

async def main():
    try:
        respuesta = await aaus_llm.consultar_llm_async(
            prompt="¿Qué ves en esta imagen?",
            proveedor="openai",
            modelo="gpt-4o", # Use gpt-4o for best multimodal capability
            api_key=os.environ.get("OPENAI_API_KEY"),
            imagen="foto.jpg"
        )
        print("OpenAI Response:", respuesta)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 🔹 Multiple Parallel Queries (Mixed Providers)

```python
import asyncio
import aaus_llm
import os

# Assumes OPENAI_API_KEY and GROQ_API_KEY environment variables are set
# Assumes 'foto.png' exists
# Assumes Ollama server is running locally with 'llama3' model pulled

async def main():
    openai_key = os.environ.get("OPENAI_API_KEY")
    groq_key = os.environ.get("GROQ_API_KEY")

    tareas = []
    # Task 1: Ollama (local, no key needed)
    tareas.append(
        aaus_llm.consultar_llm_async("Define IA en una frase", proveedor="ollama", modelo="llama3")
    )
    # Task 2: Groq (requires key)
    if groq_key:
        tareas.append(
            aaus_llm.consultar_llm_async("Resume el concepto de computación cuántica", proveedor="groq", modelo="llama3-8b-8192", api_key=groq_key)
        )
    else:
        print("Skipping Groq task: GROQ_API_KEY not set.")

    # Task 3: OpenAI Multimodal (requires key)
    if openai_key:
        tareas.append(
            aaus_llm.consultar_llm_async("Describe esta imagen brevemente", proveedor="openai", modelo="gpt-4o", api_key=openai_key, imagen="foto.png")
        )
    else:
        print("Skipping OpenAI task: OPENAI_API_KEY not set.")

    if tareas:
        print(f"Running {len(tareas)} tasks in parallel...")
        try:
            respuestas = await asyncio.gather(*tareas)
            print("\n--- Respuestas ---")
            for i, respuesta in enumerate(respuestas):
                print(f"Respuesta Tarea {i+1}:\n{respuesta}\n--------------------")
        except Exception as e:
            print(f"An error occurred during parallel execution: {e}")
    else:
        print("No tasks to run (check API Key availability).")


if __name__ == "__main__":
    asyncio.run(main())

```

---

## ⚠️ Error Handling

*   **Automatic Retries:** The SDK attempts up to 3 retries with a 2-second delay between attempts for network-related errors.
*   **Logging:** Errors encountered during requests (including retries) are logged using Python's `logging` module. Configure logging in your application to see these messages.
*   **Exceptions:** If a request fails after all retry attempts, the underlying exception (e.g., `aiohttp.ClientError`, `ValueError`) is raised.

---

## 🔌 Dependencies

This SDK requires the following Python libraries:

*   `aiohttp`: For making asynchronous HTTP requests.
*   `openai`: The official OpenAI Python client library (specifically version <1.0.0 for the current implementation, unless refactored).

These dependencies are automatically handled when you install the package using `pip` as described below.

---

## 🧩 Installation

You can install this package directly using `pip`.

1.  **Navigate** to the root directory of the package (the one containing the `pyproject.toml` file) in your terminal.
2.  **Install** the package:

    *   For standard usage:
        ```bash
        pip install .
        ```
    *   For development (allows editing the source code without reinstalling):
        ```bash
        pip install -e .
        ```

After installation, you can import the main function in your Python scripts:

```python
import aaus_llm

# Now you can use aaus_llm.consultar_llm_async(...)
```

## Instalación desde GitHub

Puedes instalar la última versión directamente desde GitHub usando pip:

```bash
pip install git+https://github.com/ansonTGN/aaus_llm.git
```