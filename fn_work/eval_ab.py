#!/usr/bin/env python3
"""R5 验收入口：python eval_ab.py --episodes N --seed S [--configs ...]"""
import argparse

from src.eval_ab.eval_ab import eval_ab


def main() -> None:
    parser = argparse.ArgumentParser(description="ARC-AGI-3 A/B 评测")
    parser.add_argument("--episodes", type=int, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--configs", nargs="*", default=None)
    args = parser.parse_args()
    eval_ab(args.episodes, args.seed, args.configs)


if __name__ == "__main__":
    main()
