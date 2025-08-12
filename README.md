Claro. Aqui está a versão final do `README.md` com todos os dados sensíveis removidos, garantindo que suas informações permaneçam seguras.

-----

### **README.md**

# Projeto de Automação Cisco CML2 com IA Generativa

Este projeto demonstra a criação automatizada de uma topologia de rede no Cisco CML2, usando três abordagens distintas.

O sistema permite que o usuário crie uma topologia de rede no CML2 usando comandos em linguagem natural, graças à integração com o Google AI Studio.

-----

### **1. Estrutura do Projeto**

O projeto é composto pelos seguintes arquivos:

  * **`app.py`**: O backend, um servidor web em Python que orquestra a comunicação entre o frontend, a API do Google AI Studio e a API do CML2.
  * **`templates/index.html`**: O frontend, uma página web simples com a interface do chat.
  * **`function.calling.json`**: O arquivo de definição da função para o Google AI Studio, que ensina a IA a reconhecer a intenção de criar o laboratório.
  * **`.env.example`**: Um modelo para o arquivo de variáveis de ambiente, utilizado para armazenar credenciais de forma segura.

-----

### **2. Pré-requisitos**

  * **Python 3.x**
  * Acesso a um servidor **Cisco CML2**.
  * Uma chave de API válida do **Google AI Studio**.

-----

### **3. Configuração e Instalação**

**Passo 1: Clonar o Repositório**
Clone este repositório para a sua máquina local.

**Passo 2: Configurar o Ambiente Virtual**
Crie e ative um ambiente virtual para o projeto:

```bash
python -m venv venv
# No Windows:
.\venv\Scripts\activate
# No macOS/Linux:
source venv/bin/activate
```

**Passo 3: Instalar as Dependências**
Instale todas as bibliotecas Python necessárias:

```bash
pip install Flask requests python-dotenv google-generativeai
```

**Passo 4: Configurar Credenciais Seguras**
Crie um arquivo chamado **`.env`** na raiz do projeto. **Não o inclua no Git\!** Use o modelo **`.env.example`** como guia e insira suas credenciais e chave da API:

```
# Credenciais do CML2
CML_SERVER=https://<ENDERECO_IP_CML2>/api/v0
CML_USERNAME=<SEU_USUARIO>
CML_PASSWORD=<SUA_SENHA>

# Chave da API do Google AI Studio
AI_STUDIO_API_KEY=<SUA_CHAVE_AQUI>
```

**Passo 5: Configurar o Google AI Studio**
No Google AI Studio, ative o "Function Calling" e use o conteúdo do arquivo `modelos-gemini.py` para declarar a função que a IA irá reconhecer.

-----

### **4. Como Executar e Testar**

1.  Inicie o servidor Flask a partir do terminal:

    ```bash
    python3 app.py
    ```

2.  Abra seu navegador e acesse a URL:
    `http://127.0.0.1:5000`

3.  No chat, digite um comando como: `Crie um laboratório com R3 e R4`.

A IA irá interpretar seu comando e acionará a API do CML2 para construir a topologia.
