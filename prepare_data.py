"""Подготовка запасного набора для занятия «Звук как сигнал» (запускать на компьютере с интернетом).

Скачивает архив Google Speech Commands v2 (около 2,3 ГБ, лицензия CC BY 4.0) потоком, не сохраняя его целиком,
и оставляет в data/reserve фоновые шумы и по 800 записей на каждую из шести команд, по одной записи на диктора:
    вперед – forward, стоп – stop, налево – left, направо – right, быстрее – up, медленнее – down.
Результат – около 160 МБ. Запуск:
    python prepare_data.py
"""
import tarfile
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

SC_URL = 'https://storage.googleapis.com/download.tensorflow.org/data/speech_commands_v0.02.tar.gz'
RESERVE_WORDS = {'вперед': 'forward', 'стоп': 'stop', 'налево': 'left', 'направо': 'right', 'быстрее': 'up', 'медленнее': 'down'}


def build_reserve(per_class=800, root=Path(__file__).parent / 'data' / 'reserve'):
    want = {eng: rus for rus, eng in RESERVE_WORDS.items()}
    counts, speakers, n_noise = Counter(), defaultdict(set), 0
    print('скачиваю архив Speech Commands v2 и выбираю записи ...')
    with urllib.request.urlopen(SC_URL) as resp, tarfile.open(fileobj=resp, mode='r|gz') as tar:
        for m in tar:
            parts = m.name.split('/')
            if not m.isfile() or not m.name.endswith('.wav') or len(parts) < 2:
                continue
            word, fname = parts[-2], parts[-1]
            if word == '_background_noise_':
                dst = root / '_noise' / fname; n_noise += 1
            elif word in want and counts[word] < per_class and fname.split('_')[0] not in speakers[word]:
                speakers[word].add(fname.split('_')[0]); counts[word] += 1
                dst = root / want[word] / fname
            else:
                continue
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(tar.extractfile(m).read())
            if n_noise >= 6 and all(counts[w] >= per_class for w in want):
                break
    print('готово:', {want[w]: counts[w] for w in want}, '| шумов:', n_noise)


if __name__ == '__main__':
    build_reserve()
