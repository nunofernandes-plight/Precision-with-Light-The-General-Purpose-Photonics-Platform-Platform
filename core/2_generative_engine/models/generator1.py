# pcf_generative_engine.py
import torch.nn as nn

class FiberGenerator(nn.Module):
    def __init__(self, target_dim=3, output_dim=64*64):
        super(FiberGenerator, self).__init__()
        # Input: Target Dispersion, n_eff, Mode Area
        # Output: A 64x64 pixel 'map' of the fiber cross-section
        self.model = nn.Sequential(
            nn.Linear(target_dim, 256),
            nn.LeakyReLU(0.2),
            nn.Linear(256, 1024),
            nn.Linear(1024, output_dim),
            nn.Tanh()
        )

    def forward(self, targets):
        return self.model(targets).view(-1, 1, 64, 64)
