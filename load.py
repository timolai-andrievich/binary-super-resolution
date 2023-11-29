import torch
from bbcu.models import build_model


def load_bbcu(model_path, scale, use_large=False):
    if model_path is None:
        return None
    opt = {}
    if scale in (2, 4):
        opt = {"name": "Test_x2",
               "model_type": "SRModel",
               "scale": scale,
               "num_gpu": 0,
               "manual_seed": 0,
               "is_train": False,
               "dist": False,
               "network_g":
                   {"type": "BBCUL" if use_large else "BBCUM",
                    "num_in_ch": 3,
                    "num_out_ch": 3,
                    "num_feat": 64,
                    "num_block": 16,
                    "upscale": scale,
                    "k": 0.46 if scale == 2 else 0.49,  # found experimentally
                    },
               "path": {"pretrain_network_g": model_path, "strict_load_g": True}
               }
    return build_model(opt).net_g


def load(model_path, scale, use_bbcu=False):
    if use_bbcu:
        return load_bbcu(model_path, scale)
    return torch.load(model_path, map_location=torch.device("cpu")) if model_path else None
