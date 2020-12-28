# -*- coding: utf-8 -*-

"""Главный и единственный модуль в игре.

Игра специально написана в минималистичном стиле, мне
хотелось воплотить текстовый движок настолько лаконично,
насколько это вообще возможно.

Подкладывая этому скрипту различные json с метаданными, можно
запускать произвольные текстовые истории.
"""
import json
import os
import textwrap
from collections import defaultdict
from typing import Dict, Any, NewType

Context = NewType('Context', Dict[str, Any])
Location = NewType('Location', Dict[str, Any])
Locations = Dict[str, Location]


def clear_screen_windows() -> None:
    """Очистить содержимое экрана на Windows.
    """
    os.system('cls')


def clear_screen_nix() -> None:
    """Очистить содержимое экрана на *nix.
    """
    os.system('clear')


def get_locations() -> Locations:
    """Загрузить локации с жёсткого диска и вернуть в виде словаря.

    Пример данных на выходе:
    {
        'start':
        {
            'title': 'Стартовая локация',
            'options': ...,
        },
        ...
    }
    """
    locations = {}

    for path, dirs, filenames in os.walk(os.path.join('game', 'locations')):
        for filename in filenames:
            full_path = os.path.join(path, filename)

            with open(full_path, mode='r', encoding='utf-8') as file:
                contents = json.load(file)
                for name, content in contents.items():
                    locations[name] = Location(content)

    return locations


def get_context() -> Context:
    """Вернуть набор переменных игры.

    Здесь можно заполнить параметры по умолчанию.
    """
    return Context({
        'times_visited': defaultdict(int),
    })


def get_header(position: str, location: Location, context: Context) -> str:
    """Извлечь заголовок локации.

    Текст зависит от того, бывали ли мы тут раньше.
    """
    if all([context['times_visited'][position] == 0,
            'initial_header' in location]):
        return location['initial_header']
    return location['header']


def is_visible(option: dict, context: Context) -> bool:
    """Вернуть True если мы можем видеть эту позицию.
    """
    condition = option.get('condition')

    if condition is None:
        return True

    return bool(eval(condition, {}, context))


def get_input_from_user(variants: dict) -> str:
    """Получить от пользователя вариант ответа, который он хочет выбрать.
    """
    while True:
        variant = input('>')

        if variant.strip().lower() in variants:
            return variant

        print('Выберите один из предоставленных вариантов')


def apply_side_effect(chosen_option: dict, context: Context) -> None:
    """Применить побочныё эффект выбора.

    Мутируем переменные контекста, чтобы управлять логикой.
    Сами решения принимаются на этапе разработки JSON и в данном
    скрипте никак не представлены.
    """
    side_effect = chosen_option.get('side_effect')

    if side_effect:
        exec(side_effect, {}, context)


def enter_location(position: str, locations: Locations,
                   context: Context) -> Location:
    """Применить операции входа в новую локацию и вернуть её экземпляр.
    """
    clear_screen()
    location: Location = locations[position]
    output_location(position, location, context)
    context['times_visited'][position] += 1
    return location


def ask_user(location: Location, context: Context) -> dict:
    """Получить обратную связь от пользователя и вернуть экземпляр опции.

    Пример данных на выходе:
    {
        'condition': 'True',
        'label': 'Вариант 2',
        'goto': 'end',
        ...
    }

    Приходится использовать отдельную переменную number из-за
    невидимых вариантов в меню выбора опций. Без него нумерация
    будет не по порядку.
    """
    visible_choices = {}
    number = 0

    for option in location['options']:
        if is_visible(option, context):
            number += 1
            visible_choices[str(number)] = option

        print(f'[{number}] {option["label"]}')

    user_choice_number = get_input_from_user(visible_choices)
    chosen_option = visible_choices[user_choice_number]

    return chosen_option


def output_location(position: str, location: Location, context: Context,
                    terminal_width: int = 80) -> None:
    """Вывести на экран заголовок локации и краткое описание входа.
    """
    print('-' * terminal_width)

    header = get_header(position, location, context)

    for substring in header.split('\n'):
        if substring:
            lines = textwrap.wrap(text=substring,
                                  width=terminal_width)
            for line in lines:
                print(line)

    print('-' * terminal_width)


def main():
    """Главный событийный цикл игры.

    В бесконечном цикле крутит JSON-ы, пор пока игрок не нажмёт
    Ctrl+C или не доберётся до локации с именем end.
    """
    locations = get_locations()
    context = get_context()
    position = 'start'

    while True:
        location = enter_location(position, locations, context)
        option = ask_user(location, context)
        apply_side_effect(option, context)
        position = option.get('goto')

        if position == 'end' or not position:
            break

    print('Спасибо за игру!')


if __name__ == '__main__':

    if os.name == 'nt':
        clear_screen = clear_screen_windows
    else:
        clear_screen = clear_screen_nix

    try:
        main()
    except KeyboardInterrupt:
        print('Выход по команде с клавиатуры')
