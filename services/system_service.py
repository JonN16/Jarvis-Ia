"""
System service for Windows system control
"""

import psutil
import subprocess


def obter_info_sistema():
    """Get system information"""
    try:
        return {
            "cpu": psutil.cpu_percent(interval=1),
            "memoria": psutil.virtual_memory().percent,
            "disco": psutil.disk_usage('/').percent
        }
    except Exception as e:
        print(f"Erro ao obter info do sistema: {e}")
        return {}


def obter_processos_em_uso():
    """Get list of running processes"""
    try:
        processos = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                processos.append(proc.info['name'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return processos
    except Exception as e:
        print(f"Erro ao listar processos: {e}")
        return []


def encerrar_processo(nome):
    """Terminate a process by name"""
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'].lower() == nome.lower():
                    proc.terminate()
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return False
    except Exception as e:
        print(f"Erro ao encerrar processo: {e}")
        return False
