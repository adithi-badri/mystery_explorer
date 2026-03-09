"""
Mystery Explorer – text-based grid adventure game in Python.

Run with:

    cd /Users/adithibadrinarayanan/Desktop/projects/mystery_explorer
    python3 mystery_explorer.py

Controls:
  - w / a / s / d : move up / left / down / right
  - i            : show inventory and score
  - q            : quit

Legend on the map:
  ^ = You (player)
  # = Wall
  . = Floor / path
  K = Key
  C = Locked chest (needs key)
  ? = Puzzle tile
  G = Goal / exit
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

MapGrid = List[List[str]]
Position = Tuple[int, int]


BASE_MAP = [
    list("###########"),
    list("#@..?.K..G#"),
    list("#.###.###.#"),
    list("#...C....?#"),
    list("###########"),
]


PUZZLES = [
    {
        "question": "I speak without a mouth and hear without ears. I have nobody, but I come alive with wind. What am I?",
        "answer": "echo",
        "reward": ("crystal", 20),
    },
    {
        "question": "What has keys but can’t open locks?",
        "answer": "piano",
        "reward": ("coin", 10),
    },
]


@dataclass
class PlayerState:
    position: Position
    score: int = 0
    inventory: Dict[str, int] = field(default_factory=dict)
    solved_puzzles: int = 0
    opened_chest: bool = False


def find_player(grid: MapGrid) -> Position:
    for r, row in enumerate(grid):
        for c, ch in enumerate(row):
            if ch == "@":
                return r, c
    raise ValueError("Player start position not found.")


def print_map(grid: MapGrid, player: PlayerState) -> None:
    print("\nMap:")
    for r, row in enumerate(grid):
        line = []
        for c, ch in enumerate(row):
            if (r, c) == player.position:
                line.append("^")
            else:
                line.append(ch)
        print("".join(line))


def print_status(player: PlayerState) -> None:
    print("\nScore:", player.score)

    if player.inventory:
        print("Inventory:")
        for item in player.inventory:
            print(" -", item, player.inventory[item])
    else:
        print("Inventory: empty")


def add_item(player: PlayerState, item: str, score: int = 0) -> None:

    if item in player.inventory:
        player.inventory[item] = player.inventory[item] + 1
    else:
        player.inventory[item] = 1

    if score > 0:
        player.score = player.score + score
        print("\nYou obtained:", item, "+", score, "points")
    else:
        print("\nYou obtained:", item)


def handle_puzzle(player: PlayerState, puzzle_index: int) -> None:

    if puzzle_index >= len(PUZZLES):
        print("\nThe inscription is too faded to read.")
        return

    puzzle = PUZZLES[puzzle_index]

    print("\nPuzzle:")
    print(puzzle["question"])

    answer = input("Your answer: ").lower()

    if answer == puzzle["answer"]:

        reward = puzzle["reward"]

        name = reward[0]
        points = reward[1]

        print("Correct!")

        add_item(player, name, points)

        player.solved_puzzles = player.solved_puzzles + 1

    else:
        print("Incorrect.")


def try_move(grid: MapGrid, player: PlayerState, dr: int, dc: int) -> bool:

    r = player.position[0]
    c = player.position[1]

    nr = r + dr
    nc = c + dc

    if nr < 0 or nr >= len(grid):
        print("Edge of map.")
        return False

    if nc < 0 or nc >= len(grid[0]):
        print("Edge of map.")
        return False

    tile = grid[nr][nc]

    if tile == "#":
        print("Wall.")
        return False

    if tile == "K":

        add_item(player, "key", 5)

        grid[nr][nc] = "."

    elif tile == "?":

        handle_puzzle(player, player.solved_puzzles)

        grid[nr][nc] = "."

    elif tile == "C":

        if "key" in player.inventory and player.opened_chest == False:

            print("\nYou unlock the chest!")

            player.inventory["key"] = player.inventory["key"] - 1

            if player.inventory["key"] <= 0:
                del player.inventory["key"]

            add_item(player, "treasure", 50)

            player.opened_chest = True

            grid[nr][nc] = "."

        else:

            print("Chest is locked.")

    elif tile == "G":

        print("\nYou reach the exit!")

        player.position = (nr, nc)

        return True

    player.position = (nr, nc)

    return False


def main():

    print("Welcome to Mystery Explorer!")

    print("Reach G to escape.")

    grid = []

    for row in BASE_MAP:
        grid.append(row.copy())

    start = find_player(grid)

    grid[start[0]][start[1]] = "."

    player = PlayerState(start)

    while True:

        print_map(grid, player)

        print_status(player)

        cmd = input("\nMove (w/a/s/d), i=inventory, q=quit: ").lower()

        if cmd == "q":
            print("Goodbye.")
            break

        if cmd == "i":
            print_status(player)
            continue

        if cmd == "w":
            dr = -1
            dc = 0

        elif cmd == "s":
            dr = 1
            dc = 0

        elif cmd == "a":
            dr = 0
            dc = -1

        elif cmd == "d":
            dr = 0
            dc = 1

        else:
            print("Invalid command.")
            continue

        reached_goal = try_move(grid, player, dr, dc)

        if reached_goal:

            print_map(grid, player)

            print_status(player)

            print("\nYou escape the dungeon. Victory!")

            break


if __name__ == "__main__":
    main()
