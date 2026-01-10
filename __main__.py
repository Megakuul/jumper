import jumper

help = """
jumper help

- ls
- info
- cd <Role>
- cd -
- exit
"""

with jumper.Client() as jp:
    while True:
        command = input("> ")
        blocks = command.strip().split(" ", 2)

        match blocks[0].strip():
            case "ls":
                jp.List()
            case "exit":
                print("bye")
                break
            case _:
                print(help)
