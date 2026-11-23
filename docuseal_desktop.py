import os
import sys
import time
import socket
import subprocess
from pathlib import Path
import webview


def pasta_base():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def porta_livre(porta_inicial=3000):
    for porta in range(porta_inicial, porta_inicial + 50):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", porta)) != 0:
                return porta
    return 3000


def aguardar_servidor(porta, timeout=45):
    inicio = time.time()
    while time.time() - inicio < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", porta)) == 0:
                return True
        time.sleep(0.4)
    return False


def main():
    base = pasta_base()
    interno = Path(getattr(sys, "_MEIPASS", base))
    app_dir = interno / "docuseal_app"
    ruby_dir = interno / "ruby_runtime"

    dados_dir = Path(os.environ.get("LOCALAPPDATA", base)) / "DocuSealDesktop"
    dados_dir.mkdir(parents=True, exist_ok=True)

    porta = porta_livre(3000)

    env = os.environ.copy()
    env["PATH"] = f"{ruby_dir / 'bin'};{ruby_dir / 'msys64' / 'usr' / 'bin'};{env.get('PATH', '')}"
    env["RAILS_ENV"] = "production"
    env["SECRET_KEY_BASE"] = "docuseal_desktop_nativo_windows_2026_artur"
    env["DATABASE_URL"] = f"sqlite3:{(dados_dir / 'docuseal.sqlite3').as_posix()}"
    env["STORAGE_PATH"] = str(dados_dir / "storage")
    env["PORT"] = str(porta)
    env["RAILS_SERVE_STATIC_FILES"] = "true"
    env["RAILS_LOG_TO_STDOUT"] = "true"

    bundle_cmd = str(ruby_dir / "bin" / "bundle.bat")
    flags_ocultas = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0

    subprocess.run(
        [bundle_cmd, "exec", "rails", "db:prepare"],
        cwd=str(app_dir),
        env=env,
        creationflags=flags_ocultas,
        check=True
    )

    servidor = subprocess.Popen(
        [bundle_cmd, "exec", "puma", "-C", "config/puma.rb"],
        cwd=str(app_dir),
        env=env,
        creationflags=flags_ocultas
    )

    try:
        aguardar_servidor(porta)
        webview.create_window(
            "DocuSeal - Assinatura Eletrônica",
            f"http://127.0.0.1:{porta}",
            width=1280,
            height=820,
            min_size=(960, 640)
        )
        webview.start()
    finally:
        servidor.terminate()
        try:
            servidor.wait(timeout=5)
        except subprocess.TimeoutExpired:
            servidor.kill()


if __name__ == "__main__":
    main()