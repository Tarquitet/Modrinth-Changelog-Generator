import json
import zipfile
import requests
import io

def parse_mrpack_json(json_data):
    mods = {}
    for file in json_data.get('files', []):
        filename = file['path'].split('/')[-1].replace('.jar', '')
        mods[filename] = file.get('versionId', 'unknown')

    metadata = {
        "name": json_data.get("name", "Unknown"),
        "version": json_data.get("versionId", "Unknown"),
        "minecraft": json_data.get("dependencies", {}).get("minecraft", "Unknown")
    }
    
    return metadata, mods

def read_local_mrpack(path):
    with zipfile.ZipFile(path, 'r') as z:
        with z.open('modrinth.index.json') as f:
            index_data = json.loads(f.read().decode('utf-8'))
            return parse_mrpack_json(index_data)

def fetch_modrinth_versions(project_id):
    response = requests.get(f"https://api.modrinth.com/v2/project/{project_id}/version")
    response.raise_for_status()
    versions = response.json()
    
    if not versions:
        raise ValueError("El proyecto no tiene versiones publicadas.")

    valid_versions = []
    for v in versions:
        for file in v['files']:
            if file['filename'].endswith('.mrpack'):
                valid_versions.append({
                    'version_number': v['version_number'],
                    'name': v['name'],
                    'url': file['url']
                })
                break
                
    if not valid_versions:
        raise ValueError("No se encontraron archivos .mrpack en este proyecto.")
        
    return valid_versions

def download_specific_mrpack(url, version_number):
    response = requests.get(url)
    response.raise_for_status()
    
    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        with z.open('modrinth.index.json') as f:
            index_data = json.loads(f.read().decode('utf-8'))
            metadata, mods = parse_mrpack_json(index_data)
            
            # Asegurar que la version refleje la seleccionada en Modrinth
            metadata["version"] = version_number
            return metadata, mods