import torch
from competition.evaluation import Evaluator
import argparse
import warnings

def parse_args():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-b", "--benchmarks", type=str, nargs='*', default=None)
    parser.add_argument("-m", "--model", type=str, required=True)
    parser.add_argument("-s", "--scale", type=int, default=2)

    args = parser.parse_args()
    return args

def main():
    warnings.simplefilter('ignore')
    args = parse_args()
    benchmarks = args.benchmarks
    if benchmarks == '':
        benchmarks = None
    model = torch.load(args.model)
    if args.scale == 2:
        Evaluator().evaluate(scalex2_model=model, benchmarks=benchmarks)
    elif args.scale == 4:
        Evaluator().evaluate(scalex4_model=model, benchmarks=benchmarks)
    else:
        print(f'Only scales 2 and 4 are supported, and scale {args.scale} was passed as an argument.')

if __name__ == '__main__':
    main()