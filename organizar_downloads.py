"""
organizar_downloads.py
Organiza a pasta de Downloads criando subpastas por extensão de arquivo.
"""

import os
import shutil
import sys
from pathlib import Path
from collections import defaultdict


# ── Mapeamento de extensões → nome amigável da pasta ──────────────────────────
CATEGORIAS = {
    # Imagens
    ".jpg": "Imagens", ".jpeg": "Imagens", ".png": "Imagens",
    ".gif": "Imagens", ".bmp": "Imagens", ".svg": "Imagens",
    ".webp": "Imagens", ".heic": "Imagens", ".ico": "Imagens",
    # Vídeos
    ".mp4": "Videos", ".mkv": "Videos", ".avi": "Videos",
    ".mov": "Videos", ".wmv": "Videos", ".flv": "Videos",
    ".webm": "Videos", ".m4v": "Videos",
    # Áudios
    ".mp3": "Audios", ".wav": "Audios", ".flac": "Audios",
    ".aac": "Audios", ".ogg": "Audios", ".m4a": "Audios", ".wma": "Audios",
    # Documentos
    ".pdf": "PDF", ".doc": "Word", ".docx": "Word",
    ".xls": "Excel", ".xlsx": "Excel", ".csv": "Excel",
    ".ppt": "PowerPoint", ".pptx": "PowerPoint",
    ".txt": "Textos", ".md": "Textos", ".rtf": "Textos",
    # Compactados
    ".zip": "Compactados", ".rar": "Compactados", ".7z": "Compactados",
    ".tar": "Compactados", ".gz": "Compactados", ".bz2": "Compactados",
    # Código / Dev
    ".py": "Codigo", ".js": "Codigo", ".ts": "Codigo", ".html": "Codigo",
    ".css": "Codigo", ".json": "Codigo", ".xml": "Codigo",
    ".sql": "Codigo", ".sh": "Codigo", ".bat": "Codigo",
    # Executáveis / Instaladores
    ".exe": "Executaveis", ".msi": "Executaveis", ".dmg": "Executaveis",
    ".pkg": "Executaveis", ".deb": "Executaveis", ".rpm": "Executaveis",
    ".apk": "Executaveis",
    # Fontes
    ".ttf": "Fontes", ".otf": "Fontes", ".woff": "Fontes", ".woff2": "Fontes",
}


def obter_pasta_downloads() -> Path:
    """Retorna o caminho padrão da pasta Downloads do usuário."""
    return Path.home() / "Downloads"


def organizar(pasta: Path, modo_seco: bool = False) -> dict:
    """
    Move os arquivos da *pasta* para subpastas por extensão.

    Parâmetros
    ----------
    pasta     : diretório a organizar
    modo_seco : se True, apenas simula sem mover nada (dry-run)

    Retorna um dicionário com o resumo das movimentações.
    """
    if not pasta.exists():
        raise FileNotFoundError(f"Pasta não encontrada: {pasta}")

    resumo = defaultdict(list)
    ignorados = []

    # Itera apenas sobre arquivos (não entra em subpastas)
    for arquivo in sorted(pasta.iterdir()):
        if not arquivo.is_file():
            continue  # pula subpastas e links

        ext = arquivo.suffix.lower()
        if not ext:
            ignorados.append(arquivo.name)
            continue

        # Decide o nome da subpasta
        nome_subpasta = CATEGORIAS.get(ext, ext.lstrip(".").upper())
        destino_dir = pasta / nome_subpasta
        destino = destino_dir / arquivo.name

        # Evita sobrescrever: acrescenta sufixo numérico se necessário
        contador = 1
        while destino.exists():
            stem = arquivo.stem
            destino = destino_dir / f"{stem}_{contador}{ext}"
            contador += 1

        if not modo_seco:
            destino_dir.mkdir(exist_ok=True)
            shutil.move(str(arquivo), str(destino))

        resumo[nome_subpasta].append(arquivo.name)

    return dict(resumo), ignorados


def imprimir_resumo(resumo: dict, ignorados: list, modo_seco: bool):
    prefixo = "[SIMULAÇÃO] " if modo_seco else ""
    total = sum(len(v) for v in resumo.values())

    print(f"\n{'='*55}")
    print(f"  {prefixo}Organização concluída — {total} arquivo(s) movido(s)")
    print(f"{'='*55}")

    for pasta_nome, arquivos in sorted(resumo.items()):
        print(f"\n📁 {pasta_nome}/ ({len(arquivos)} arquivo(s))")
        for nome in arquivos:
            print(f"   • {nome}")

    if ignorados:
        print(f"\n⚠️  Ignorados (sem extensão): {len(ignorados)}")
        for nome in ignorados:
            print(f"   • {nome}")

    print()


# ── Ponto de entrada ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Organiza a pasta de Downloads por extensão de arquivo."
    )
    parser.add_argument(
        "pasta",
        nargs="?",
        default=None,
        help="Caminho da pasta a organizar (padrão: ~/Downloads)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simula a organização sem mover nenhum arquivo",
    )
    args = parser.parse_args()

    pasta_alvo = Path(args.pasta) if args.pasta else obter_pasta_downloads()

    print(f"\n📂 Pasta alvo : {pasta_alvo}")
    if args.dry_run:
        print("🔍 Modo simulação ativado — nenhum arquivo será movido.\n")

    try:
        resumo, ignorados = organizar(pasta_alvo, modo_seco=args.dry_run)
        imprimir_resumo(resumo, ignorados, modo_seco=args.dry_run)
    except FileNotFoundError as e:
        print(f"\n❌ Erro: {e}")
        sys.exit(1)
