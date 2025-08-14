# Projeto de Automação Cisco CML2 com IA Generativa

Este projeto demonstra a criação automatizada de uma topologia de rede no Cisco CML2, explorando três abordagens distintas para interação com sua API.

## Objetivo do Projeto

O objetivo principal é automatizar a criação de uma topologia de rede simples no CML2, consistindo em dois roteadores (`iol-xe`) conectados pela interface `Ethernet0/0`, com endereçamento IP básico:
* **R1 (e0/0):** `10.1.2.1/24`
* **R2 (e0/0):** `10.1.2.2/24`

---

## Pré-requisitos

* **Cisco CML2:** Acesso a um servidor CML2 (o projeto assume que o endereço do servidor será configurado no `.env`).
* **Postman:** Para a Etapa 1 (opcional, mas recomendado para testes manuais da API).
* **Python 3.x:** Ambiente de execução Python.
* **Bibliotecas Python:** `Flask`, `requests`, `python-dotenv`, `google-generativeai`.
* **Google AI Studio:** Uma conta e uma chave de API válida para a Etapa 3.

---

## Configuração Inicial

1.  **Clonar o Repositório:**
    ```bash
    git clone [https://github.com/mnisenbaum/cml2-ipd-week.git](https://github.com/mnisenbaum/cml2-ipd-week.git)
    cd cml2-ipd-week
    ```

2.  **Configurar o Ambiente Virtual:**
    ```bash
    python -m venv venv
    # No Windows:
    .\venv\Scripts\activate
    # No macOS/Linux:
    source venv/bin/activate
    ```

3.  **Instalar as Dependências Python:**
    ```bash
    pip install Flask requests python-dotenv google-generativeai
    ```

4.  **Configurar Credenciais Seguras (Arquivo `.env`):**
    Crie um arquivo chamado **`.env`** na raiz do projeto (no mesmo diretório que `app.py`). **Este arquivo NÃO deve ser versionado no Git!** Use o modelo `.env.example` como guia e preencha com suas credenciais e chaves:
    ```
    # Credenciais do CML2
    CML_SERVER=<ENDEREÇO_IP_DO_SEU_CML2>/api/v0
    CML_USERNAME=<SEU_USUARIO_CML2>
    CML_PASSWORD=<SUA_SENHA_CML2>

    # Chave da API do Google AI Studio
    AI_STUDIO_API_KEY=<SUA_CHAVE_API_GOOGLE_AI_STUDIO>
    ```

---

## Etapas de Automação

### Etapa 1: Criando uma Topologia no CML2 Usando Postman

Esta etapa demonstra como realizar cada chamada de API manualmente usando o Postman para criar a topologia.

1.  **Obter Token de Autenticação:**
    * **Método:** `POST`
    * **URL:** `<ENDEREÇO_IP_DO_SEU_CML2>/api/v0/authenticate`
    * **Headers:** `Content-Type: application/json`
    * **Body (raw/json):** `{ "username": "<SEU_USUARIO_CML2>", "password": "<SUA_SENHA_CML2>" }`
    * **Ação:** Copie o token JWT retornado no corpo da resposta.

2.  **Criar o Laboratório (Lab):**
    * **Método:** `POST`
    * **URL:** `<ENDEREÇO_IP_DO_SEU_CML2>/api/v0/labs`
    * **Headers:** `Authorization: Bearer <token_obtido>`, `Content-Type: application/json`
    * **Body (raw/json):** `{ "title": "LAB_POSTMAN", "description": "Criado via Postman" }`
    * **Ação:** Copie o `id` do laboratório retornado.

3.  **Criar os Nós (R1 e R2):**
    * **Método:** `POST`
    * **URL:** `<ENDEREÇO_IP_DO_SEU_CML2>/api/v0/labs/<lab_id>/nodes?populate_interfaces=true`
    * **Headers:** `Authorization: Bearer <token_obtido>`, `Content-Type: application/json`
    * **Body (raw/json - Exemplo para R1):**
        ```json
        {
          "label": "R1",
          "image_definition": "iol-xe",
          "node_definition": "iol-xe",
          "configuration": "hostname R1\ninterface Loopback0\n ip address 1.1.1.1 255.255.255.0\ninterface Ethernet0/0\n ip address 10.1.2.1 255.255.255.0\nend",
          "x": 100,
          "y": 100
        }
        ```
    * **Ação:** Repita para R2 e copie os `id`s dos nós R1 e R2.

4.  **Encontrar as Interfaces:**
    * **Método:** `GET`
    * **URL:** `<ENDEREÇO_IP_DO_SEU_CML2>/api/v0/labs/<lab_id>/nodes/<node_id>/interfaces?data=true`
    * **Headers:** `Authorization: Bearer <token_obtido>`
    * **Ação:** Na resposta JSON, encontre o `id` da interface `Ethernet0/0` para R1 e R2.

5.  **Criar o Link:**
    * **Método:** `POST`
    * **URL:** `<ENDEREÇO_IP_DO_SEU_CML2>/api/v0/labs/<lab_id>/links`
    * **Headers:** `Authorization: Bearer <token_obtido>`, `Content-Type: application/json`
    * **Body (raw/json):** `{ "src_int": "<id_r1_interface_e0/0>", "dst_int": "<id_r2_interface_e0/0>" }`

6.  **Iniciar o Laboratório:**
    * **Método:** `PUT`
    * **URL:** `<ENDEREÇO_IP_DO_SEU_CML2>/api/v0/labs/<lab_id>/start`
    * **Headers:** `Authorization: Bearer <token_obtido>`

---

### Etapa 2: Criando uma Topologia no CML2 Usando Python

Este script Python (`cml_script-seguro.py`) automatiza toda a sequência de chamadas da API do CML2 de forma autônoma.

1.  **Localização do Script:**
    * O script está localizado em: `cml_script-seguro.py`

2.  **Executar o Script:**
    * No terminal, execute o script:
        ```bash
        python3 cml_script-seguro.py
        ```
    * **Ação:** O script irá imprimir o progresso e o ID do laboratório criado. Verifique o CML2 para confirmar a criação e inicialização.

---

### Etapa 3: Criando uma Topologia no CML2 Usando IA Generativa

Esta aplicação web permite criar a topologia CML2 através de comandos em linguagem natural, utilizando um chatbot de IA.

1.  **Configurar o Google AI Studio:**
    * Acesse o [Google AI Studio](https://aistudio.google.com/).
    * Crie um novo "Prompt de Chat" ou use um existente.
    * Na seção **Tools** (Ferramentas), ative **Function calling** (Chamada de Função) e clique em **Edit** (Editar).
    * Cole o conteúdo do arquivo `modelos-gemini.py` na seção de "Function declarations" (Declarações de Função) e salve.

2.  **Localização dos Arquivos da Aplicação:**
    * **Backend:** `app.py`
    * **Frontend:** `templates/index.html`

3.  **Executar a Aplicação:**
    * No terminal, inicie o servidor Flask:
        ```bash
        python3 app.py
        ```
    * **Ação:** O servidor será iniciado e estará acessível via navegador.

4.  **Acessar e Testar o Chatbot:**
    * Abra seu navegador e acesse a URL: `http://127.0.0.1:5000`
    * No campo de chat, digite um comando como: `Crie um laboratório com R3 e R4`
    * **Ação:** O chatbot irá processar sua requisição, acionar a automação no CML2 e retornar uma mensagem de sucesso ou erro. Verifique o CML2 para ver a topologia criada.

---
