import os
import signal
import subprocess
import threading
from django.core.management.commands.runserver import Command as RunserverCommand

class Command(RunserverCommand):
    processes = []  # Lista para armazenar processos

    def handle(self, *args, **options):
        if os.environ.get("RUN_MAIN") != "true":  # Evita rodar duas vezes
            self.stdout.write(self.style.SUCCESS("🚀 Iniciando processos auxiliares..."))

            # Inicia "npm run watch"
            npm_process = subprocess.Popen(
                ["npm", "run", "watch"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            self.processes.append(npm_process)
            threading.Thread(target=self.stream_output, args=(npm_process, "NPM"), daemon=True).start()

            # Inicia "manage.py tailwind start"
            tailwind_process = subprocess.Popen(
                ["python", "manage.py", "tailwind", "start"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            self.processes.append(tailwind_process)
            threading.Thread(target=self.stream_output, args=(tailwind_process, "TAILWIND"), daemon=True).start()

            # Captura sinais de encerramento para matar os processos corretamente
            signal.signal(signal.SIGINT, self.terminate_processes)
            signal.signal(signal.SIGTERM, self.terminate_processes)

        super().handle(*args, **options)

    def stream_output(self, process, name):
        """Função para exibir logs dos processos em tempo real."""
        for line in process.stdout:
            self.stdout.write(self.style.NOTICE(f"[{name}] {line.strip()}"))

    def terminate_processes(self, signum=None, frame=None):
        """Encerra todos os processos iniciados ao desligar o Django."""
        self.stdout.write(self.style.WARNING("\n🛑 Encerrando processos auxiliares..."))
        for process in self.processes:
            process.terminate()  # Tenta encerrar educadamente
            try:
                process.wait(timeout=5)  # Aguarda 5s antes de forçar
            except subprocess.TimeoutExpired:
                process.kill()  # Mata o processo se ele não encerrar
        self.stdout.write(self.style.SUCCESS("✅ Todos os processos foram encerrados!"))
