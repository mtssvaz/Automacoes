"""
avisar_render.py
Monitora a renderização do Adobe Premiere Pro e envia uma mensagem
no Telegram quando o processo terminar.

── Configuração ──────────────────────────────────────────────────
1. Crie um bot no Telegram falando com @BotFather → /newbot
2. Copie o TOKEN gerado e cole em BOT_TOKEN abaixo
3. Inicie uma conversa com seu bot e acesse:
   https://api.telegram.org/bot<SEU_TOKEN>/getUpdates
   para pegar seu CHAT_ID
4. Cole o CHAT_ID abaixo e salve o arquivo
──────────────────────────────────────────────────────────────────
"""

import time
import requests
import psutil

# ── ⚙️  CONFIGURAÇÕES — edite aqui ───────────────────────────────
BOT_TOKEN = "SEU_TOKEN_AQUI"       # ex: 7412345678:AAFxxxxxx
CHAT_ID   = "SEU_CHAT_ID_AQUI"    # ex: 123456789

# Nome do processo do Premiere no Windows
PROCESSO_PREMIERE = "Adobe Premiere Pro.exe"

# Intervalo entre cada verificação (segundos)
INTERVALO_VERIFICACAO = 10

# Quantos segundos com CPU baixa para considerar que terminou
TEMPO_OCIOSO = 30

# Limite de CPU (%) abaixo do qual considera "ocioso"
LIMITE_CPU = 5.0
# ─────────────────────────────────────────────────────────────────


def enviar_telegram(mensagem: str):
    """Envia uma mensagem via Telegram Bot API."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensagem, "parse_mode": "Markdown"}
    try:
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
        print("✅ Mensagem enviada no Telegram!")
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem: {e}")


def premiere_esta_rodando() -> bool:
    """Retorna True se o processo do Premiere estiver ativo."""
    for proc in psutil.process_iter(["name"]):
        if proc.info["name"] == PROCESSO_PREMIERE:
            return True
    return False


def obter_cpu_premiere() -> float:
    """Retorna o uso de CPU (%) do processo do Premiere."""
    for proc in psutil.process_iter(["name", "cpu_percent"]):
        if proc.info["name"] == PROCESSO_PREMIERE:
            try:
                return proc.cpu_percent(interval=1)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                return 0.0
    return 0.0


def monitorar():
    print("🎬 Monitorando Adobe Premiere Pro...")
    print(f"   Verificando a cada {INTERVALO_VERIFICACAO}s | CPU ociosa < {LIMITE_CPU}% por {TEMPO_OCIOSO}s\n")

    # Aguarda o Premiere iniciar (caso rode o script antes de abrir)
    while not premiere_esta_rodando():
        print("⏳ Premiere não encontrado. Aguardando iniciar...")
        time.sleep(INTERVALO_VERIFICACAO)

    print("✔️  Premiere detectado! Aguardando renderização...\n")

    # Aguarda o Premiere ficar ocupado (renderizando)
    while obter_cpu_premiere() < LIMITE_CPU:
        print("⏳ Premiere aberto mas ainda não renderizando...")
        time.sleep(INTERVALO_VERIFICACAO)

    print("🔴 Renderização em andamento...\n")

    # Monitora até ficar ocioso
    tempo_ocioso_acumulado = 0

    while True:
        if not premiere_esta_rodando():
            enviar_telegram(
                "✅ *Renderização concluída!*\n"
                "O Adobe Premiere foi fechado. Seu vídeo está pronto! 🎉"
            )
            break

        cpu = obter_cpu_premiere()
        print(f"   CPU Premiere: {cpu:.1f}%")

        if cpu < LIMITE_CPU:
            tempo_ocioso_acumulado += INTERVALO_VERIFICACAO
            print(f"   ⚠️  CPU baixa há {tempo_ocioso_acumulado}s...")
        else:
            tempo_ocioso_acumulado = 0  # resetar se voltar a renderizar

        if tempo_ocioso_acumulado >= TEMPO_OCIOSO:
            enviar_telegram(
                "✅ *Renderização concluída!*\n"
                "O Adobe Premiere ficou ocioso. Seu vídeo provavelmente está pronto! 🎬"
            )
            break

        time.sleep(INTERVALO_VERIFICACAO)


if __name__ == "__main__":
    if BOT_TOKEN == "SEU_TOKEN_AQUI" or CHAT_ID == "SEU_CHAT_ID_AQUI":
        print("❌ Configure o BOT_TOKEN e o CHAT_ID no início do script antes de rodar!")
    else:
        monitorar()
