from prompt_toolkit import PromptSession
from prompt_toolkit.completion import FuzzyWordCompleter
from prompt_toolkit.history import InMemoryHistory

import jumper

help = """
jumper help

- ls
- info
- cd <Role>
- cd -
- exit
"""

if __name__ == "__main__":
    with jumper.Client() as jp:
        autocomplete = []
        current = ""
        session = PromptSession(history=InMemoryHistory())
        while True:
            try:
                autocomplete = jp.Autocomplete()
            except:
                autocomplete = []
            try:
                current = jp.Top()
            except:
                current = "undefined"

            try:
                command = session.prompt(
                    f"[{current}]# ",
                    completer=FuzzyWordCompleter(
                        autocomplete + ["ls", "info", "cd", "exit"]
                    ),
                    complete_while_typing=True,
                )
                blocks = command.strip().split(" ", 2)

                match blocks[0].strip():
                    case "ls":
                        print(jp.List())
                    case "info":
                        print(jp.Info())
                    case "cd":
                        if len(blocks) < 2:
                            print("usage: cd <Role>")
                        elif blocks[1] == "-":
                            print(jp.Pop())
                        else:
                            print(jp.Push(blocks[1]))
                    case "exit":
                        print("bye")
                        break
                    case _:
                        print(help)
            except Exception as e:
                print(f"\n{e}\n")
