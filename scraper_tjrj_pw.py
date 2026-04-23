import asyncio
import re

from scraper import consultar_processo as consultar_cnj


DEFAULT_RESULT = {
    "movimentacao": "Sem movimentos",
    "data": None,
    "vara": "Nao identificada",
}


def _extract_from_text(content_text):
    vara = "Nao identificada"
    movimentacao = "Sem movimentos"
    data_mov = None

    vara_match = re.search(r"(?:Vara|Orgao Julgador)\s*:?\s*(.+)", content_text, re.IGNORECASE)
    if vara_match:
        vara = vara_match.group(1).split("\n")[0].strip()[:200]

    tipo_match = re.search(r"Tipo do Movimento\s*:?\s*(.*)", content_text, re.IGNORECASE)
    if tipo_match:
        movimentacao = tipo_match.group(1).split("\n")[0].strip()[:200]

    data_match = re.search(
        r"(?:Data da juntada|Data|Data do Movimento)\s*:?\s*(\d{2}/\d{2}/\d{4})",
        content_text,
        re.IGNORECASE,
    )
    if data_match:
        d, m, y = data_match.group(1).split("/")
        data_mov = f"{y}-{m}-{d}"

    if data_mov is None:
        dates = re.findall(r"(\d{2}/\d{2}/\d{4})", content_text)
        if dates:
            d, m, y = dates[0].split("/")
            data_mov = f"{y}-{m}-{d}"

    return {
        "movimentacao": movimentacao,
        "data": data_mov,
        "vara": vara,
    }


def _merge_results(primary, secondary):
    result = dict(DEFAULT_RESULT)
    if secondary:
        safe_secondary = dict(secondary)
        mov = safe_secondary.get("movimentacao")
        if isinstance(mov, str) and mov.lower().startswith("erro"):
            safe_secondary["movimentacao"] = None
        result.update({k: v for k, v in safe_secondary.items() if v})
    if primary:
        safe_primary = dict(primary)
        mov = safe_primary.get("movimentacao")
        if isinstance(mov, str) and mov.lower().startswith("erro"):
            safe_primary["movimentacao"] = None
        result.update({k: v for k, v in safe_primary.items() if v})
    return result


def _formatar_cnj(numero_limpo):
    if len(numero_limpo) == 20:
        return (
            f"{numero_limpo[:7]}-{numero_limpo[7:9]}.{numero_limpo[9:13]}."
            f"{numero_limpo[13:14]}.{numero_limpo[14:16]}.{numero_limpo[16:20]}"
        )
    return numero_limpo


def _normalizar_data(data_str):
    if not data_str or not isinstance(data_str, str):
        return None
    match = re.match(r"^(\d{2})/(\d{2})/(\d{4})$", data_str.strip())
    if not match:
        return None
    d, m, y = match.groups()
    return f"{y}-{m}-{d}"


def _consultar_tjrj_api_direta(numero_limpo):
    import requests

    codigo = _formatar_cnj(numero_limpo)
    session = requests.Session()
    home_headers = {"User-Agent": "Mozilla/5.0"}
    api_headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/json;charset=UTF-8",
        "Referer": "https://www3.tjrj.jus.br/consultaprocessual/",
        "Origin": "https://www3.tjrj.jus.br",
    }

    session.get("https://www3.tjrj.jus.br/consultaprocessual/", headers=home_headers, timeout=20)
    response = session.post(
        "https://www3.tjrj.jus.br/consultaprocessual/api/processos/por-numeracao-unica",
        headers=api_headers,
        json={"tipoProcesso": "1", "codigoProcesso": codigo},
        timeout=30,
    )
    if response.status_code != 200:
        return None

    payload = response.json()
    if not isinstance(payload, list) or not payload:
        return None

    proc = payload[0]
    codigo_antigo = proc.get("numProcesso")
    tipo_processo = proc.get("tipoProcesso")
    movimentacao = (proc.get("ultimoMovimento") or "Sem movimentos").strip()[:200]
    vara = (proc.get("descricaoServentia") or proc.get("nomeComarca") or "Nao identificada").strip()[:200]

    data_ultimo_mov = None
    if codigo_antigo and tipo_processo is not None:
        detalhe_payload = {
            "tipoProcesso": str(tipo_processo),
            "codigoProcesso": codigo_antigo,
            "rg": codigo_antigo,
            "numeroProcVep": codigo_antigo,
        }
        detalhe_response = session.post(
            "https://www3.tjrj.jus.br/consultaprocessual/api/processos/por-numero/publica",
            headers=api_headers,
            json=detalhe_payload,
            timeout=30,
        )
        if detalhe_response.status_code == 200:
            detalhe = detalhe_response.json()
            ultimo = detalhe.get("ultMovimentoProc") if isinstance(detalhe, dict) else None
            if isinstance(ultimo, dict):
                movimentacao = (
                    ultimo.get("descrMov")
                    or ultimo.get("descricao")
                    or movimentacao
                ).strip()[:200]
                data_ultimo_mov = _normalizar_data(
                    ultimo.get("dtMovimento") or ultimo.get("dtJuntada") or ultimo.get("dtAlt")
                )

    return {"movimentacao": movimentacao, "data": data_ultimo_mov, "vara": vara}

async def consultar_tjrj_pw(numero):
    numero_limpo = re.sub(r"[^0-9]", "", numero)
    url = f"https://www3.tjrj.jus.br/consultaprocessual/#/consultapublica?numProcessoCNJ={numero_limpo}"

    try:
        tjrj_api_result = await asyncio.to_thread(_consultar_tjrj_api_direta, numero_limpo)
        if tjrj_api_result:
            return _merge_results(tjrj_api_result, None)
    except Exception as e:
        print(f"Falha na API direta do TJRJ: {e}")

    pw_result = None

    try:
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled"],
            )
            context = await browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
                viewport={"width": 1920, "height": 1080},
                locale="pt-BR",
            )
            page = await context.new_page()

            print(f"Acessando TJRJ via Link Direto: {url}")
            await page.goto(url, wait_until="domcontentloaded", timeout=150000)
            await page.wait_for_timeout(15000)

            try:
                await page.click("text=OK", timeout=3000)
            except Exception:
                pass

            content_text = await page.evaluate("() => document.body.innerText")
            pw_result = _extract_from_text(content_text)
            await browser.close()

    except Exception as e:
        print(f"Erro no fluxo Playwright: {e}")

    if pw_result and (
        pw_result.get("movimentacao") != "Sem movimentos"
        or pw_result.get("data")
        or pw_result.get("vara") not in {None, "", "Nao identificada"}
    ):
        return _merge_results(pw_result, None)

    print("TJRJ bloqueou/nao retornou dados no Playwright. Usando fallback CNJ...")
    try:
        cnj_result = await asyncio.to_thread(consultar_cnj, numero)
        if cnj_result:
            return _merge_results(cnj_result, pw_result)
    except Exception as e:
        print(f"Erro no fallback CNJ: {e}")

    return _merge_results(pw_result, None)

if __name__ == "__main__":
    res = asyncio.run(consultar_tjrj_pw("0257058-08.2019.8.19.0001"))
    print(res)
