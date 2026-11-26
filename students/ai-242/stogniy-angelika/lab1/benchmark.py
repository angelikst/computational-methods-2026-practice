import sys
import time
import statistics
import csv
from providers import make_client


def measure_once(client, model, prompt):
    t_start = time.perf_counter()
    first_token_at = None
    parts = []
    stream = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )
    for chunk in stream:
        if not chunk.choices:
            continue
        piece = chunk.choices[0].delta.content
        if piece:
            if first_token_at is None:
                first_token_at = time.perf_counter()
            parts.append(piece)
    t_end = time.perf_counter()
    text = "".join(parts)
    return {
        "ttft_s": round(first_token_at - t_start, 3),
        "total_s": round(t_end - t_start, 3),
        "chars": len(text),
        "chars_per_s": round(len(text) / (t_end - t_start), 1),
    }


def measure(client, model, prompt, attempts=6):
    time.sleep(4)  # пауза проти rate limit
    for i in range(attempts):
        try:
            return measure_once(client, model, prompt)
        except Exception as e:
            wait = 5 * (i + 1)
            print(f"  помилка: {type(e).__name__}, повтор через {wait} с...")
            time.sleep(wait)
    raise RuntimeError("сервер не відповів після кількох спроб")


PROMPTS = {
    "short": "Столиця Японії?",
    "medium": "Поясни в одному абзаці, що таке рекурсія.",
    "long": "Напиши інструкцію з 10 пунктів, як налаштувати робоче середовище розробника.",
}

providers = sys.argv[1:] or ["local", "cloud"]

for provider in providers:
    rows = []
    client, model = make_client(provider)
    measure(client, model, "розігрів")
    for name, prompt in PROMPTS.items():
        runs = [measure(client, model, prompt) for _ in range(3)]
        rows.append({
            "provider": provider,
            "model": model,
            "prompt": name,
            "ttft_s": statistics.median(r["ttft_s"] for r in runs),
            "total_s": statistics.median(r["total_s"] for r in runs),
            "chars_per_s": statistics.median(r["chars_per_s"] for r in runs),
        })
        print(rows[-1])
    with open(f"results_{provider}.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
