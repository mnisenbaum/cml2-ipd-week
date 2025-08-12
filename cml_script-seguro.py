import requests
import json
import urllib3
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Suprime os warnings de SSL, apenas para ambientes de laboratório
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- Carrega as configurações do ambiente ---
CML_SERVER = os.getenv("CML_SERVER")
USERNAME = os.getenv("CML_USERNAME")
PASSWORD = os.getenv("CML_PASSWORD")

HEADERS = {'Content-Type': 'application/json'}

# --- Funções de API ---

def authenticate_cml():
    """Autentica no servidor CML2 e retorna o token de autenticação."""
    auth_url = f"{CML_SERVER}/authenticate"
    auth_payload = {"username": USERNAME, "password": PASSWORD}
    
    try:
        response = requests.post(auth_url, json=auth_payload, verify=False)
        response.raise_for_status()
        token = response.json()
        HEADERS['Authorization'] = f"Bearer {token}"
        print("Autenticação bem-sucedida. Token obtido.")
        return token
    except requests.exceptions.RequestException as e:
        print(f"ERRO: Falha na autenticação com o CML2. {e}")
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
        lab_id = lab_info['id']
        print(f"Laboratório '{lab_title}' criado. ID: {lab_id}")
        return lab_id
    except requests.exceptions.RequestException as e:
        print(f"ERRO: Falha ao criar o laboratório. {e}")
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
        node_id = node_info['id']
        print(f"Nó '{node_label}' adicionado. ID: {node_id}")
        return node_id
    except requests.exceptions.RequestException as e:
        print(f"ERRO: Falha ao adicionar o nó '{node_label}'. {e}")
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
                interface_id = iface['id']
                print(f"Interface '{interface_label}' encontrada. ID: {interface_id}")
                return interface_id
        print(f"ERRO: Interface '{interface_label}' não encontrada no nó {node_id}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"ERRO: Falha ao buscar interfaces. {e}")
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
        link_id = link_info['id']
        print(f"Link criado com sucesso. ID: {link_id}")
        return link_id
    except requests.exceptions.RequestException as e:
        print(f"ERRO: Falha ao criar o link. {e}")
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

# --- Lógica principal do script ---

def main():
    print("Iniciando a automação CML2...")
    
    # 1. Autenticar e obter o token
    token = authenticate_cml()
    if not token:
        print("Automação abortada.")
        return

    # 2. Criar o Lab
    lab_title = "Lab_API_Python"
    lab_id = create_lab(lab_title)
    if not lab_id:
        print("Automação abortada.")
        return
        
    # 3. Configurações e criação dos nós
    r1_config = """
hostname R1
interface Loopback0
 ip address 1.1.1.1 255.255.255.0
interface Ethernet0/0
 ip address 10.1.2.1 255.255.255.0
end
"""
    r2_config = """
hostname R2
interface Loopback0
 ip address 2.2.2.2 255.255.255.0
interface Ethernet0/0
 ip address 10.1.2.2 255.255.255.0
end
"""
    node_r1_id = create_node(lab_id, "R1", "iol-xe", r1_config, 100, 100)
    node_r2_id = create_node(lab_id, "R2", "iol-xe", r2_config, 400, 100)

    if not node_r1_id or not node_r2_id:
        print("Automação abortada.")
        return
        
    # 4. Encontrar as interfaces e criar o link
    interface_r1_id = find_node_interface(lab_id, node_r1_id, "Ethernet0/0")
    interface_r2_id = find_node_interface(lab_id, node_r2_id, "Ethernet0/0")

    if not interface_r1_id or not interface_r2_id:
        print("Automação abortada.")
        return

    create_link(lab_id, interface_r1_id, interface_r2_id)
    
    # 5. Ligar o laboratório
    start_lab(lab_id)

    print("\nProcesso de automação concluído com sucesso!")
    print(f"Verifique o novo laboratório no CML2 com o ID: {lab_id}")


if __name__ == "__main__":
    main()
