import requests
from bs4 import BeautifulSoup
import re

def consultar_tjpe(numero):
    """
    Scrape do site do TJPE (PJE Consulta Pública)
    """
    # Ex: 0055674-55.2022.8.17.2810
    # O PJE é complexo para scrape via requests puro devido ao ViewState.
    # Vamos tentar uma abordagem via API interna se disponível, ou fallback.
    
    # Tentativa de usar o endpoint de consulta do PJE
    # Muitos PJEs tem esse endpoint:
    url = f"https://pje.tjpe.jus.br/1g/ConsultaPublica/DetalheProcessoConsultaPublica/listView.seam"
    # Mas ele requer parâmetros internos.
    
    # Como fallback e para manter o "dois scrapes", vamos usar o Datajud 
    # mas com o endpoint específico do tribunal se possível, ou apenas retornar 
    # que o site do tribunal está em manutenção.
    
    # No entanto, para o usuário "ver" dados, vamos tentar o Datajud do TJPE
    # que costuma ser diferente do Datajud geral em termos de delay.
    
    return None # Por enquanto retorna None para mostrar como tratar no app

def consultar_tribunal(numero):
    if ".8.19." in numero:
        from scraper_tjrj import consultar_tjrj
        return consultar_tjrj(numero)
    elif ".8.17." in numero:
        return consultar_tjpe(numero)
    else:
        return None
