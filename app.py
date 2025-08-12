from flask import Flask, request, jsonify, render_template
import requests
import json
import os
import google.generativeai as genai
import urllib3
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)

# --- Carrega as credenciais do ambiente ---
CML_SERVER = os.getenv("CML_SERVER")
CML_USERNAME = os.getenv("CML_USERNAME")
CML_PASSWORD = os.getenv("CML_PASSWORD")
AI_STUDIO_API_KEY = os.getenv("AI_STUDIO_API_KEY")

# Configura o Google AI Studio com a chave carregada
genai.configure(api_key=AI_STUDIO_API_KEY)

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-latest",
    tools=[
        {
            "function_declarations": [
                {
                    "name": "create_lab_topology_two_routers",
                    "description": "Cria uma nova topologia no Cisco CML2 com dois roteadores (por exemplo, R1 e R2) da imagem iol-xe, conectados pela interface e0/0, e com endereçamento IP 10.1.2.1/24 no primeiro roteador e 10.1.2.2/24 no segundo. Os roteadores são configurados com as configurações básicas de hostname e IP nas interfaces e0/0.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "router1_name": {
                                "type": "string",
                                "description": "O nome do primeiro roteador, como R1."
                            },
                            "router2_name": {
                                "type": "string",
                                "description": "O nome do segundo roteador, como R2."
                            }
                        },
                        "required": ["router1_name", "router2_name"]
                    }
                }
            ]
        }
    ]
)

# Credenciais do CML2
HEADERS = {'Content-Type': 'application/json'}

def authenticate_cml():
    """Autentica no servidor CML2 e retorna o token de autenticação."""
    auth_url = f"{CML_SERVER}/authenticate"
    auth_payload = {"username": CML_USERNAME, "password": CML_PASSWORD}
    
    try:
        response = requests.post(auth_url, json=auth_payload, verify=False)
        response.raise_for_status()
        
        token = response.json()
        HEADERS['Authorization'] = f"Bearer {token}"
        return token
    except requests.exceptions.HTTPError as e:
        print(f"Erro HTTP na autenticação: {e}")
        print(f"Resposta do servidor: {response.text}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão na autenticação: {e}")
        return None
    except json.JSONDecodeError:
        print("A resposta do servidor não é um JSON válido.")
        print(f"Resposta do servidor: {response.text}")
        return None

def create_lab(lab_title):
    """Cria um novo laboratório no CML2 com o título especificado."""
    try:
        labs_url = f"{CML_SERVER}/labs"
        lab_payload = {
            "title": lab_title,
            "description": lab_title
        }
        response = requests.post(labs_url, headers=HEADERS, json=lab_payload, verify=False)
        response.raise_for_status()
        lab_info = response.json()
        print(f"Laboratório '{lab_title}' criado com sucesso. ID: {lab_info['id']}")
        return lab_info['id']
    except requests.exceptions.RequestException as e:
        print(f"Erro ao criar o laboratório: {e}")
        return None

def create_node(lab_id, node_label, image_definition, configuration, x_pos, y_pos):
    """Adiciona um nó (roteador) a um laboratório."""
    try:
        node_url = f"{CML_SERVER}/labs/{lab_id}/nodes?populate_interfaces=true"
        node_payload = {
            "label": node_label,
            "image_definition": image_definition,
            "node_definition": image_definition,
            "configuration": configuration,
            "x": x_pos,
            "y": y_pos
        }
        response = requests.post(node_url, headers=HEADERS, json=node_payload, verify=False)
        response.raise_for_status()
        node_info = response.json()
        print(f"Nó '{node_label}' adicionado. ID: {node_info['id']}")
        return node_info['id']
    except requests.exceptions.RequestException as e:
        print(f"Erro ao adicionar o nó '{node_label}': {e}")
        return None

def find_node_interface(lab_id, node_id, interface_label):
    """Encontra o ID de uma interface específica em um nó."""
    try:
        interfaces_url = f"{CML_SERVER}/labs/{lab_id}/nodes/{node_id}/interfaces?data=true"
        response = requests.get(interfaces_url, headers=HEADERS, verify=False)
        response.raise_for_status()
        interfaces = response.json()
        for iface in interfaces:
            if iface['label'] == interface_label:
                return iface['id']
        print(f"Interface '{interface_label}' não encontrada no nó {node_id}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar interfaces: {e}")
        return None

def create_link(lab_id, interface1_id, interface2_id):
    """Cria um link entre duas interfaces."""
    try:
        link_url = f"{CML_SERVER}/labs/{lab_id}/links"
        link_payload = {
            "src_int": interface1_id,
            "dst_int": interface2_id
        }
        response = requests.post(link_url, headers=HEADERS, json=link_payload, verify=False)
        response.raise_for_status()
        link_info = response.json()
        print(f"Link criado com sucesso. ID: {link_info['id']}")
        return link_info['id']
    except requests.exceptions.RequestException as e:
        print(f"Erro ao criar o link: {e}")
        return None

def start_lab(lab_id):
    """Inicia um laboratório."""
    try:
        start_url = f"{CML_SERVER}/labs/{lab_id}/start"
        response = requests.put(start_url, headers=HEADERS, verify=False)
        response.raise_for_status()
        print(f"Laboratório ID: {lab_id} iniciado com sucesso.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"ERRO: Falha ao iniciar o laboratório. {e}")
        return False

# Função principal de automação do CML2, agora genérica
def create_lab_topology_two_routers(router1_name, router2_name):
    """
    Cria um laboratório com dois roteadores genéricos,
    conectados pela interface Ethernet0/0.
    """
    if not authenticate_cml():
        return "Falha na autenticação com o CML2."

    lab_id = create_lab(f"LAB_{router1_name}_{router2_name}_Automated")
    if not lab_id:
        return "Falha ao criar o laboratório."

    r1_config = f"""
hostname {router1_name}
interface Loopback0
 ip address 1.1.1.1 255.255.255.0
interface Ethernet0/0
 ip address 10.1.2.1 255.255.255.0
end
"""
    r2_config = f"""
hostname {router2_name}
interface Loopback0
 ip address 2.2.2.2 255.255.255.0
interface Ethernet0/0
 ip address 10.1.2.2 255.255.255.0
end
"""
    
    node_r1_id = create_node(lab_id, router1_name, "iol-xe", r1_config, 100, 100)
    node_r2_id = create_node(lab_id, router2_name, "iol-xe", r2_config, 400, 100)

    if not node_r1_id or not node_r2_id:
        return "Falha ao criar os roteadores."
        
    interface_r1_id = find_node_interface(lab_id, node_r1_id, "Ethernet0/0")
    interface_r2_id = find_node_interface(lab_id, node_r2_id, "Ethernet0/0")

    if not interface_r1_id or not interface_r2_id:
        return "Falha ao encontrar as interfaces dos roteadores."

    create_link(lab_id, interface_r1_id, interface_r2_id)
    
    start_lab(lab_id)

    return f"Laboratório '{router1_name} e {router2_name}' criado e iniciado com sucesso! ID: {lab_id}. Verifique o CML2."

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    try:
        response = model.generate_content(user_message)
        tool_calls = response.candidates[0].content.parts
        
        if tool_calls:
            first_tool_call = tool_calls[0].function_call
            function_name = first_tool_call.name
            
            if function_name == "create_lab_topology_two_routers":
                args = first_tool_call.args
                response_text = create_lab_topology_two_routers(
                    router1_name=args['router1_name'],
                    router2_name=args['router2_name']
                )
            else:
                response_text = "Desculpe, não entendi a sua requisição. Por favor, tente algo como 'Crie um laboratório com R1 e R2'."
        else:
            response_text = "Desculpe, não entendi a sua requisição. Por favor, tente algo como 'Crie um laboratório com R1 e R2'."
            
        return jsonify({"response": response_text})

    except Exception as e:
        print(f"Erro no processamento do chat: {e}")
        return jsonify({"response": "Erro ao se comunicar com o backend."})

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    app.run(debug=True)
