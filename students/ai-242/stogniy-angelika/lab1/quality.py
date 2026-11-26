from providers import make_client
import json

TEXT = """Київський метрополітен відкрився 6 листопада 1960 року. Перша ділянка мала п'ять станцій: від «Вокзальної» до «Дніпра». Її довжина становила 5,24 км. Сьогодні метро має 3 діючі лінії та 52 станції. Загальна довжина маршрутів становить близько 67,6 км. За даними 2016 року, щодня метро перевозило приблизно 1,32 млн пасажирів."""

TASKS = {
    "1_fact": "Рік відкриття Київського метрополітену. Відповідай лише роком.",
    "2_format": "JSON: city, year, lines_count для Київського метро. Без пояснень, без markdown, лише JSON.",
    "3_summary": "Стисни наступний текст до двох речень, збережи всі числа:\n\n" + TEXT,
    "4_code": "total_weight(items) — сума ваг зі списку словників. Лише код.",
    "5_logic": "120 ящиків: 45 по 8 кг, решта по 12 кг. Вантажівка тримає 1200 кг. Скільки рейсів? Покажи хід розв'язання.",
    "6_language": "Чим контейнерне перевезення відрізняється від навалочного? Поясни українською, два абзаци.",
}

results = {}
for provider in ["local"]:
    client, model = make_client(provider)
    results[model] = {}
    for task_id, prompt in TASKS.items():
        answers = []
        for attempt in range(2):  # два прогони на завдання
            r = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            answers.append(r.choices[0].message.content)
        results[model][task_id] = answers
        print(f"{model} / {task_id} — готово")

with open("quality.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
