import os
import shutil
import oscar
from pathlib import Path

# 1. Znajdź gdzie Python zainstalował Oscara
oscar_root = Path(os.path.dirname(oscar.__file__))
print(f"DEBUG: Oscar zainstalowany w: {oscar_root}")

# 2. Ustal ścieżkę docelową (Twój projekt)
# Zakładamy, że uruchamiasz to z folderu 'proj', gdzie jest 'manage.py'
base_dir = Path.cwd()
project_app_name = 'akademickisklepzgadzetami'

apps_to_fix = ['basket', 'checkout']

print("-" * 50)

for app in apps_to_fix:
    # Ścieżka źródłowa (wewnątrz biblioteki Oscar)
    src_dir = oscar_root / 'apps' / app / 'migrations'

    # Ścieżka docelowa (u Ciebie w projekcie)
    dst_dir = base_dir / project_app_name / app / 'migrations'

    print(f"Naprawiam aplikację: {app}")

    # Sprawdź czy źródło istnieje
    if not src_dir.exists():
        print(f"BŁĄD: Nie znaleziono folderu źródłowego: {src_dir}")
        continue

    # Upewnij się, że cel istnieje
    if not dst_dir.exists():
        print(f"Tworzę folder docelowy: {dst_dir}")
        dst_dir.mkdir(parents=True, exist_ok=True)
        # Tworzymy __init__.py
        (dst_dir / '__init__.py').touch()

    # Kopiowanie plików
    count = 0
    for item in src_dir.iterdir():
        if item.is_file() and item.name.endswith('.py') and item.name != '__init__.py':
            shutil.copy2(item, dst_dir / item.name)
            count += 1

    print(f"-> Skopiowano {count} plików migracji do: {dst_dir}")
    print("-" * 50)

print("Gotowe. Teraz spróbuj: python manage.py migrate")