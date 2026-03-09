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
  @ = You (player)
  # = Wall
  . = Floor / path
  K = Key
  C = Locked chest (needs key)
  ? = Puzzle tile
  G = Goal / exit
"""

from __future__ import annotations

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
    raise ValueError("Player start position (@) not found in map.")


def print_map(grid: MapGrid, player: PlayerState) -> None:
    print("\nMap:")
    for r, row in enumerate(grid):
        line = []
        for c, ch in enumerate(row):
            if (r, c) == player.position:
                line.append("@")
            else:
                line.append(ch)
        print("".join(line))


def print_status(player: PlayerState) -> None:
    print(f"\nScore: {player.score}")
    if player.inventory:
        print("Inventory:")
        for item, count in player.inventory.items():
            print(f"  - {item}: {count}")
    else:
        print("Inventory: (empty)")


def add_item(player: PlayerState, item: str, score: int = 0) -> None:
    player.inventory[item] = player.inventory.get(item, 0) + 1
    if score:
        player.score += score
    print(f"\nYou obtained: {item} (+{score} points)" if score else f"\nYou obtained: {item}")


def handle_puzzle(player: PlayerState, puzzle_index: int) -> None:
    if puzzle_index >= len(PUZZLES):
        print("\nYou find an old faded inscription, but it's unreadable.")
        return
    puzzle = PUZZLES[puzzle_index]
    print("\nYou encounter a mysterious inscription:")
    print(puzzle["question"])
    answer = input("Your answer: ").strip().lower()
    if answer == puzzle["answer"]:
        name, reward_score = puzzle["reward"]
        print("Correct! The riddle glows and reveals a reward.")
        add_item(player, name, reward_score)
        player.solved_puzzles += 1
    else:
        print("The inscription fades. Perhaps you can try another puzzle later.")


def try_move(grid: MapGrid, player: PlayerState, dr: int, dc: int) -> bool:
    r, c = player.position
    nr, nc = r + dr, c + dc

    if nr < 0 or nr >= len(grid) or nc < 0 or nc >= len(grid[0]):
        print("You bump into the edge of the world.")
        return False

    tile = grid[nr][nc]
    if tile == "#":
        print("A solid wall blocks your path.")
        return False

    # Interactions
    if tile == "K":
        add_item(player, "key", 5)
        grid[nr][nc] = "."
    elif tile == "?":
        handle_puzzle(player, player.solved_puzzles)
        grid[nr][nc] = "."
    elif tile == "C":
        if player.inventory.get("key", 0) > 0 and not player.opened_chest:
            print("\nYou unlock the chest with your key!")
            player.inventory["key"] -= 1
            if player.inventory["key"] <= 0:
                del player.inventory["key"]
            add_item(player, "treasure", 50)
            player.opened_chest = True
            grid[nr][nc] = "."
        else:
            print("\nThe chest is locked. You need a key.")
            # Allow standing on the chest tile even if not opened
    elif tile == "G":
        print("\nYou reach the glowing exit portal!")
        player.position = (nr, nc)
        return True

    player.position = (nr, nc)
    return False


def main() -> None:
    print("Welcome to Mystery Explorer!")
    print("Explore the map, solve puzzles, collect items, and find the goal (G).")
    print()
    print("Rules & controls:")
    print("  - You are '@' on the map. Use:")
    print("      w = up, a = left, s = down, d = right")
    print("      i = show your inventory and score")
    print("      q = quit the game")
    print("  - Symbols on the map:")
    print("      # = wall (you cannot move through)")
    print("      . = floor / open path")
    print("      K = key (pick it up by stepping on it)")
    print("      C = locked chest (needs a key; may contain treasure)")
    print("      ? = puzzle tile (step on it to answer a riddle)")
    print("      G = glowing exit (reach this to finish)")
    print()
    print("Goal: reach G. For maximum score, solve puzzles and open the chest before exiting.")

    grid: MapGrid = [row.copy() for row in BASE_MAP]
    start_pos = find_player(grid)
    # Remove the @ from the static map; player position is tracked separately
    grid[start_pos[0]][start_pos[1]] = "."
    player = PlayerState(position=start_pos)

    while True:
        print_map(grid, player)
        print_status(player)
        cmd = input("\nMove (w/a/s/d), i=inventory, q=quit: ").strip().lower()

        if cmd == "q":
            print("\nYou decide to end your exploration. Goodbye!")
            break
        if cmd == "i":
            print_status(player)
            continue

        moves = {"w": (-1, 0), "s": (1, 0), "a": (0, -1), "d": (0, 1)}
        if cmd not in moves:
            print("Unknown command. Use w/a/s/d to move, i for inventory, q to quit.")
            continue

        dr, dc = moves[cmd]
        reached_goal = try_move(grid, player, dr, dc)
        if reached_goal:
            print_map(grid, player)
            print_status(player)
            if player.opened_chest:
                print("\nYou escape with your treasure. Victory!")
            else:
                print("\nYou escape, but you feel you may have left something valuable behind…")
            break


if __name__ == "__main__":
    main()

