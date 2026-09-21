# -*- coding: utf-8 -*-
"""Разбор обращений: категория по ключевым словам + черновик вежливого ответа.

Без внешних библиотек, без LLM и без API-ключей.
Запуск: python triage.py [путь_к_файлу]
"""

import sys
from pathlib import Path

# Ключевые слова заданы корнями (без окончаний), сравнение по подстроке.
RULES = [
    ("справка", ["справк", "выписк", "документ о", "подтверждени"]),
    ("жалоба", ["очеред", "холодн", "пропал", "пропала", "не работает",
                "сломал", "грязн", "шум", "хамств", "задержк", "течет", "течёт"]),
]

# Тематические подсказки: попали в текст -> конкретная фраза для черновика.
TOPICS = [
    (["справк", "мест", "учёб", "учеб"], "справки о месте учёбы"),
    (["столов", "еда", "обед", "питани"], "работы столовой"),
    (["wi-fi", "wifi", "интернет", "сет"], "доступа к сети Wi-Fi"),
    (["консультац", "записат", "приём", "прием"], "записи на консультацию"),
    (["парков", "машин", "автомоб"], "парковки для гостей"),
]

TEMPLATES = {
    "справка": (
        "Здравствуйте! По вашему вопросу {topic} сообщаем: заявку можно оформить "
        "в деканате или через личный кабинет, при себе достаточно студенческого билета. "
        "Документ готовится в течение 3 рабочих дней, о готовности мы сообщим дополнительно."
    ),
    "жалоба": (
        "Здравствуйте! Спасибо, что сообщили о проблеме — мы зафиксировали обращение "
        "по поводу {topic}. Информация уже передана в ответственную службу, ситуацию проверяем. "
        "О принятых мерах сообщим вам в течение 2 рабочих дней."
    ),
    "другое": (
        "Здравствуйте! Благодарим за обращение по вопросу {topic}. "
        "Мы уточняем детали у профильного подразделения и вернёмся с ответом в ближайшее время. "
        "Если вопрос срочный, пожалуйста, напишите нам дополнительно."
    ),
}


def classify(text):
    """Вернуть (категория, сработавшее ключевое слово или None)."""
    low = text.lower()
    for category, keywords in RULES:
        for kw in keywords:
            if kw in low:
                return category, kw
    return "другое", None


def detect_topic(text):
    """Подобрать конкретную формулировку темы обращения."""
    low = text.lower()
    for keywords, topic in TOPICS:
        if any(kw in low for kw in keywords):
            return topic
    # Запасной вариант: цитируем само обращение.
    return "«%s»" % text.rstrip(" .?!")


def make_draft(category, text):
    return TEMPLATES[category].format(topic=detect_topic(text))


def main():
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "messages.txt")
    if not path.exists():
        print("Файл не найден: %s" % path)
        return 1

    lines = [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines()]
    messages = [ln for ln in lines if ln]

    print("Обработка файла: %s (обращений: %d)" % (path.name, len(messages)))
    print("=" * 70)

    counts = {}
    for i, text in enumerate(messages, 1):
        category, kw = classify(text)
        counts[category] = counts.get(category, 0) + 1
        reason = ("ключевое слово: «%s»" % kw) if kw else "ключевые слова не найдены"
        print()
        print("Обращение №%d: %s" % (i, text))
        print("Категория: %s (%s)" % (category, reason))
        print("Черновик ответа: %s" % make_draft(category, text))

    print()
    print("=" * 70)
    summary = ", ".join("%s — %d" % (k, v) for k, v in sorted(counts.items()))
    print("Итого: %s" % summary)
    return 0


if __name__ == "__main__":
    # UTF-8 в консоли Windows, иначе русский текст ломается.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    sys.exit(main())
