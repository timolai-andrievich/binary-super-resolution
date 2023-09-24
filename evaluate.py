import torch
from competition.evaluation import Evaluator
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--benchmarks", type=str, nargs='*', default=None)
    parser.add_argument("--model", type=str, required=True)

    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    benchmarks = args.benchmarks
    if benchmarks == '':
        benchmarks = None
    scalex2_model = torch.load(args.model)
    Evaluator().evaluate(scalex2_model=scalex2_model, benchmarks=benchmarks)

if __name__ == '__main__':
    main()