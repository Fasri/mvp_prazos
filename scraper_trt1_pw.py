import asyncio
import re


def _normalizar_numero(numero):
    digitos = re.sub(r"\D", "", numero or "")
    if len(digitos) == 20:
        return (
            f"{digitos[:7]}-{digitos[7:9]}.{digitos[9:13]}."
            f"{digitos[13]}.{digitos[14:16]}.{digitos[16:]}"
        )
    return numero


def _parse_ultimo_movimento_texto(texto):
    texto = texto or ""
    texto = texto.replace("\r", "")

    bloco = re.search(
        r"(?:Ultima|Última)\s+movimenta[cç][aã]o\s*[:\-]?\s*(.+?)(?:\n\n|$)",
        texto,
        re.IGNORECASE | re.DOTALL,
    )
    if bloco:
        conteudo = " ".join(l.strip() for l in bloco.group(1).split("\n") if l.strip())
        data = re.search(r"(\d{2}/\d{2}/\d{4})", conteudo)
        return {
            "movimentacao": conteudo[:300],
            "data": data.group(1) if data else None,
        }

    linhas = [l.strip() for l in texto.split("\n") if l.strip()]
    idx = -1
    for i, linha in enumerate(linhas):
        if "movimenta" in linha.lower():
            idx = i
            break

    if idx != -1 and idx + 1 < len(linhas):
        trecho = " ".join(linhas[idx + 1 : idx + 5])
        data = re.search(r"(\d{2}/\d{2}/\d{4})", trecho)
        return {
            "movimentacao": trecho[:300],
            "data": data.group(1) if data else None,
        }

    return {"movimentacao": "Nao identificado", "data": None}


async def consultar_trt1_com_captcha(numero, timeout_segundos=240):
    try:
        from playwright.async_api import async_playwright
    except Exception as e:
        return {"erro": f"Playwright nao disponivel: {e}"}

    numero_fmt = _normalizar_numero(numero)
    url = "https://pje.trt1.jus.br/consultaprocessual/consulta-cidadao"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(locale="pt-BR")
        page = await context.new_page()

        try:
            response = await page.goto(url, wait_until="domcontentloaded", timeout=120000)
            if response and response.status >= 400:
                return {
                    "erro": f"Falha ao abrir consulta do TRT1 (HTTP {response.status}).",
                    "movimentacao": None,
                    "data": None,
                }

            titulo = (await page.title()) or ""
            html_inicial = (await page.content()) or ""
            texto_inicial = (await page.evaluate("() => document.body ? document.body.innerText : ''")) or ""
            texto_inicial_low = texto_inicial.lower()
            html_inicial_low = html_inicial.lower()

            if (
                "403" in titulo
                or "request could not be satisfied" in titulo.lower()
                or "request blocked" in texto_inicial_low
                or "the request could not be satisfied" in texto_inicial_low
                or "request blocked" in html_inicial_low
                or "the request could not be satisfied" in html_inicial_low
            ):
                return {
                    "erro": "Acesso bloqueado (HTTP 403/CloudFront) neste ambiente.",
                    "movimentacao": None,
                    "data": None,
                }

            campo_numero = page.locator(
                "input[name*='numero' i], input[id*='numero' i], input[placeholder*='processo' i]"
            ).first
            try:
                await campo_numero.wait_for(timeout=15000)
            except Exception:
                return {
                    "erro": "Nao foi possivel localizar o campo do numero do processo.",
                    "movimentacao": None,
                    "data": None,
                }
            await campo_numero.fill(numero_fmt)

            print("\nResolva o CAPTCHA na janela do navegador e clique em Consultar.")
            print("Depois aguarde o carregamento dos dados.\n")

            await page.wait_for_function(
                """
                () => {
                  const t = (document.body && document.body.innerText || '').toLowerCase();
                  return t.includes('última movimentação') ||
                         t.includes('ultima movimentacao') ||
                         t.includes('movimentações') ||
                         t.includes('movimentacoes') ||
                         t.includes('andamentos') ||
                         t.includes('não foram encontrados') ||
                         t.includes('nao foram encontrados');
                }
                """,
                timeout=timeout_segundos * 1000,
            )

            texto = await page.evaluate("() => document.body.innerText")
            resultado = _parse_ultimo_movimento_texto(texto)
            resultado["numero_processo"] = numero_fmt
            return resultado

        finally:
            await browser.close()


if __name__ == "__main__":
    numero_teste = "0100393-77.2025.5.01.0203"
    res = asyncio.run(consultar_trt1_com_captcha(numero_teste))
    print(res)
