def select_options(
    options: list, answers: list, startMsg="", answersCallable=False
):
    while True:
        if startMsg != "":
            print(startMsg)
        for idx, option in enumerate(options):
            print(f"  {idx+1}. {option}")
        inp = input("> ")
        if inp == "q" or inp == "quit":
            return None
        if not inp.isdigit():
            print("input is not digit")
            continue
        n = int(inp)
        if n < 1 or n > len(options):
            print("Input out of range")
            continue
        if answersCallable:
            answers[n - 1]()
            return None
        else:
            return answers[n - 1]
