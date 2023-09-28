
import torch
from competition.evaluation import Evaluator
from competition.estimators import ComplexityEstimator
from competition.models import bnn
import argparse
from prettytable import PrettyTable
import warnings

def parse_args():
    parser = argparse.ArgumentParser(description="")
    args = parser.parse_args()
    return args

def main():
    # TODO evaluate confings instead of all models
    warnings.simplefilter('ignore')
    args = parse_args()
    dummy_inputs = torch.zeros((1, 3, 96, 96), dtype=torch.float32)
    table = PrettyTable(['Model', 'Complexity'])
    for model_name in bnn.__all__:
        model = bnn.__getattribute__(model_name)().to('cpu')
        dummy_outputs = model(dummy_inputs)
        scale = dummy_outputs.shape[-1] // dummy_inputs.shape[-1]
        if scale not in [2, 4]:
            print(f'Unsupported scaling factor for model {model_name}: {scale}.')
            return
        complexity = ComplexityEstimator().estimate(model, dummy_inputs, "scalex2_model" if scale == 2 else "scalex4_model")
        table.add_row([model_name, f'{complexity:.5f}'])
    print(table)

if __name__ == '__main__':
    main()