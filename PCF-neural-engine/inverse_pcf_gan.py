import torch
import torch.nn as nn

# 1. The Generator (The Synthesis Engine)
class PCFGenerator(nn.Module):
    def __init__(self, latent_dim, target_dim, output_dim):
        super(PCFGenerator, self).__init__()
        # Takes (Noise + Target n_eff) -> Outputs (Pitch, d/L)
        self.model = nn.Sequential(
            nn.Linear(latent_dim + target_dim, 128),
            nn.LeakyReLU(0.2),
            nn.Linear(128, 256),
            nn.BatchNorm1d(256),
            nn.Linear(256, output_dim),
            nn.Sigmoid() # Constrains output to [0, 1] for normalization
        )

# 2. The Discriminator (The Physics Critic)
class PCFDiscriminator(nn.Module):
    def __init__(self, input_dim, target_dim):
        super(PCFDiscriminator, self).__init__()
        # Checks if the Geometry + Target pair is 'Physically Realistic'
        self.model = nn.Sequential(
            nn.Linear(input_dim + target_dim, 256),
            nn.LeakyReLU(0.2),
            nn.Linear(256, 1),
            nn.Sigmoid()
        )


