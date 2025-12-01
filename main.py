#!/usr/bin/env python3
import json
import os
import sys

GREEN = "\033[32m"
BLUE = "\033[34m"
RED = "\033[31m"
YELLOW = "\033[33m"
BOLD = "\033[1m"
RESET = "\033[0m"


# Пока не работает
def play_beep():
    try:
        result = os.system("which beep")
        print(result)

        if result == 0:
            os.system("beep -f 1000 -l 200")
        else:
            print(f"{YELLOW}Installing beep...{RESET}")
            os.system("pacman -S beep --noconfirm")
            os.system("beep -f 1000 -l 200")
    except:
        print('\a', end='', flush=True)


def load_steps(filename):
    with open(filename, "r") as f:
        return json.load(f)


def save_steps(filename, steps):
    with open(filename, "w") as f:
        json.dump(steps, f, indent=2, ensure_ascii=False)


def run_command(cmd, use_beep=False):
    print(f"\n{BLUE}>>> {cmd}{RESET}")
    print("-" * 60)

    return_code = os.system(cmd)

    print("-" * 60)

    if use_beep:
        play_beep()

    success = (return_code == 0)

    if success:
        print(f"{GREEN}SUCCESS: {RESET} {cmd}")
    else:
        print(f"{RED}ERROR {return_code}: {RESET} {cmd}")

    return success


def print_step(step, is_current=False):
    status = step["status"]

    if status == "done":
        color = GREEN
    elif status == "error":
        color = RED
    elif status == "skipped":
        color = YELLOW
    else:
        color = ""

    current_mark = f"{BLUE}<<<{RESET}" if is_current else ""
    print(f"{color}{step['id']:>3} | {step['command']} | {status}{RESET} {current_mark}")


def print_all_steps(steps, step_id):
    page_begin = 10 * ((step_id - 1) // 10)
    page_end = min(page_begin + 9, len(steps) - 1)
    for step in steps[page_begin: page_end + 1]:
        is_current = (step["id"] == step_id)
        print_step(step, is_current=is_current)


def menu():
    print("\nActions:")
    print("  [r] run")
    print("  [e] edit")
    print("  [n] next step")
    print("  [s] skip")
    print("  [j] jump to step ID")
    print("  [h] help")
    print("  [q] quit")
    return input("Choose action (Default is [r]): ").strip().lower()


def help():
    os.system("clear")
    print(BOLD + "Wi-Fi connection help (iwctl):" + RESET)
    print("""sudo iwctl
device list
station <device> scan
station <device> get-networks
station <device> connect <SSID>
exit
""")
    input("Press ENTER to return...")


def main():
    def new_index(step):
        return min(step["id"] + 1, len(steps))


    if len(sys.argv) < 2:
        print("Usage:")
        print("python3 installer.py <phase1.json>")
        print("\nThen run with phase2.json, then phase.json etc")
        return

    stage_file = sys.argv[1]

    if not os.path.exists(stage_file):
        print(f"Error: file '{stage_file}' not found!")
        return

    steps = load_steps(stage_file)
    step_id = 1

    while True:
        os.system("clear")
        step = next(s for s in steps if s["id"] == step_id)

        print_all_steps(steps, step_id)

        action = menu()

        if action == "q":
            save_steps(stage_file, steps)
            break
        elif action == "h":
            help()
        elif action == "r" or action == "":  # run
            print(f"RUNNING: {step["command"]}")
            ok = run_command(step["command"])
            if ok:
                step["status"] = "done"
                step_id = new_index(step)
            else:
                step["status"] = "error"

            save_steps(stage_file, steps)
            input("\nPress ENTER to continue...")
        elif action == "e":  # edit
            new_cmd = input("New command ('n' for cancel: ").strip()
            if new_cmd == 'n':
                continue
            step["command"] = new_cmd
            save_steps(stage_file, steps)
        elif action == "n":  # next
            step_id = new_index(step)
        elif action == "s":  # skip
            step["status"] = "skipped"
            save_steps(stage_file, steps)
            step_id = new_index(step)
        elif action == "j":  # jump
            try:
                input_id = int(input("Go to ID: "))
                if 1 <= input_id <= len(steps):
                    step_id = input_id
                else:
                    print("ID out of range")
            except ValueError:
                print("Invalid number")
        else:
            print("Unknown command")


if __name__ == "__main__":
    main()