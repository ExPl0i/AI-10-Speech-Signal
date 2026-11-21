"""Перевод записей группы в одинаковый формат для занятия «Звук как сигнал».

Записи голоса – персональные данные: скрипт запускается на школьном компьютере, результат хранится
на школьном носителе и не выкладывается в открытый доступ.

Вход – папка с подпапками учеников, в каждой – записи с телефона в любом формате (m4a, mp3, ogg, opus, amr, wav),
имя файла начинается с команды: «вперед_01.m4a», «стоп 3.ogg», «Налево-7.mp3».
Выход – data/commands/<ученик>/<команда>_<номер>.wav: WAV, 16 000 Гц, моно, 16 бит.
Нужна программа ffmpeg (ffmpeg.org; в Colab уже установлена).

    python prepare_group.py путь/к/записям
"""
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

COMMANDS = ['вперед', 'стоп', 'налево', 'направо', 'быстрее', 'медленнее']
AUDIO = {'.wav', '.m4a', '.mp3', '.ogg', '.opus', '.amr', '.aac', '.3gp', '.flac', '.webm'}


def command_of(name):
    """Команда по началу имени файла: регистр и «ё» не важны."""
    word = re.split(r'[\s_\-.]+', name.lower().replace('ё', 'е'))[0]
    return word if word in COMMANDS else None


def convert(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-i', str(src), '-ac', '1', '-ar', '16000', '-sample_fmt', 's16', str(dst)]
    return subprocess.run(cmd).returncode == 0


def main(src_root, dst_root=Path('data') / 'commands'):
    if shutil.which('ffmpeg') is None:
        sys.exit('ffmpeg не найден: установите его (ffmpeg.org) и добавьте в PATH')
    stats, skipped = Counter(), []
    for student in sorted(p for p in Path(src_root).iterdir() if p.is_dir()):
        numbers = Counter()
        for f in sorted(student.iterdir()):
            if f.suffix.lower() not in AUDIO:
                continue
            cmd = command_of(f.stem)
            if cmd is None:
                skipped.append(str(f)); continue
            numbers[cmd] += 1
            if convert(f, Path(dst_root) / student.name / f'{cmd}_{numbers[cmd]:02d}.wav'):
                stats[cmd] += 1
            else:
                skipped.append(str(f))
        print(f'{student.name}: ' + ', '.join(f'{c} {numbers[c]}' for c in COMMANDS))
    print('всего:', dict(stats))
    if skipped:
        print('пропущены (имя не начинается с команды или файл не читается):', *skipped, sep='\n  ')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
