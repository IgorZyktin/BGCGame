# -*- coding: utf-8 -*-

"""Игра.
"""
import json
import os
from typing import Dict, Any, Callable


def get_locations() -> Dict[str, dict]:
    """Загрузить локации с жёсткого диска и вернуть в виде словаря.
    """
    locations = {}
    for each_file in os.listdir('locations'):
        path = os.path.join('locations', each_file)
        with open(path, mode='r', encoding='utf-8') as file:
            locations.update(json.load(file))

    return locations


def get_context() -> Dict[str, Any]:
    """Вернуть набор переменных игры.

    Здесь можно заполнить параметры по умолчанию.
    """
    return {}


def is_visible(option: dict, context: dict) -> bool:
    """Вернуть True если мы можем видеть эту позицию.
    """
    condition = option.get('condition')

    if condition is None:
        return True

    return bool(eval(condition, {}, context))


def ask_user(variants: dict) -> str:
    """Получить от пользователя вариант ответа, который он хочет выбрать.
    """
    while True:
        variant = input('>')

        if variant.strip().lower() in variants:
            return variant

        print('Выберите один из предоставленных вариантов')


def apply_side_effect(chosen_option: dict, context: dict) -> None:
    """Применить побочный эффект выбора.

    Некоторые действия могут оказывать влияние на переменные в игре.
    """
    side_effect = chosen_option.get('side_effect')

    if side_effect:
        exec(side_effect, {}, context)


def output_title(title: str, callback: Callable = print) -> None:
    """Вывести на экран заголовок локации и краткое описание входа.
    """
    callback(title)


def main():
    """Точка входа.
    """
    locations = get_locations()
    context = get_context()
    current_location = 'start'

    while True:
        os.system('cls')
        location = locations[current_location]
        output_title(location['title'])

        variants = {}
        number = 0
        for option in location['options']:
            if is_visible(option, context):
                number += 1
                variants[str(number)] = option

            print(f'[{number}] {option["label"]}')

        variant = ask_user(variants)
        chosen_option = variants[variant]
        apply_side_effect(chosen_option, context)
        current_location = chosen_option['goto']

        if current_location == 'end':
            break

    print('Спасибо за игру!')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Выход по команде с клавиатуры')
