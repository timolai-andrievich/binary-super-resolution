import torch
import torchmetrics
from nip import nip

from competition import dataloaders, tasks, tools
from competition.models import bnn, fp

nip(dataloaders)
nip(fp)
nip(bnn)
nip(tasks)
nip(tools)

# torch
nip(torch.optim)
nip(torch.optim.lr_scheduler)
nip(torch.nn)
nip(torchmetrics)
