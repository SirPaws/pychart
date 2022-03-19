from typing import Any
from src.pychart._interpreter.callable import InputFunc, OrangeFunc, PrintFunc

from src.pychart._interpreter.environment import Environment
from ._interpreter.scanner import Scanner
from ._interpreter.pyparser import Parser


def run(source: str):
    scanner = Scanner(source)
    tokens = scanner.get_tokens()
    statements = Parser(tokens).parse()
    last_value: Any = None

    if statements is None:
        return None

    try:
        environment = Environment()
        environment.reverve("input", InputFunc())
        environment.reverve("print", PrintFunc())
        environment.reverve("orange", OrangeFunc())

        for statement in statements:
            last_value = statement(environment)
    except BaseException as err:
        print(f"Error: {err}")
        print("Exiting...")

    return last_value


def run_prompt():
    try:
        while True:
            line = input("$ : ")

            if line == ".exit":
                break

            result = run(line)
            if result:
                print(result)

    except KeyboardInterrupt:
        print("Keyboard Interrupt")
        exit()


def run_file(filename: str):
    with open(filename, "r", encoding="utf-8") as contents:
        run(contents.read())
