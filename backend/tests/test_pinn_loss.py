"""
Tests for Physics-Informed Neural Network loss functions.
Validates Helmholtz residual, ARROW condition, and multi-level PINN decomposition.
"""
import pytest
import torch
import torch.nn as nn
import numpy as np
 
 
class TestPINNLossHelholtz:
    """Tests for the Helmholtz equation residual loss (fiber mode solver)."""
 
    def test_loss_zero_for_exact_solution(self, device):
        """
        A field that exactly satisfies the Helmholtz equation should
        produce zero physics residual loss.
        """
        from backend._2_generative_engine.pinn_loss import HelmholtzResidualLoss
 
        loss_fn = HelmholtzResidualLoss(lambda_phys=1.0)
 
        # Plane wave: E(x) = exp(i*k*x), n_eff = k/k0 = n_silica = 1.444
        k0 = 2 * np.pi / (1.064e-6)  # Wavenumber at 1064nm
        n_eff = torch.tensor(1.444, requires_grad=True)
        n_silica = 1.444
 
        # For a uniform medium, the plane wave satisfies Helmholtz exactly
        # Loss_phys = ||∇²E + k0²(n²-n_eff²)E||² → 0
        loss = loss_fn.physics_residual(n_eff, torch.tensor(n_silica))
        assert loss.item() < 1e-6
 
    def test_loss_nonzero_for_unphysical_solution(self, device):
        """
        A predicted n_eff above the core index must produce nonzero physics loss.
        """
        from backend._2_generative_engine.pinn_loss import HelmholtzResidualLoss
 
        loss_fn = HelmholtzResidualLoss(lambda_phys=1.0)
 
        # n_eff > n_silica is physically impossible for a guided mode
        n_eff_unphysical = torch.tensor(1.500, requires_grad=True)
        n_silica = 1.444
 
        loss = loss_fn.physics_residual(n_eff_unphysical, torch.tensor(n_silica))
        assert loss.item() > 0.0
 
    def test_total_loss_weighted_sum(self, device):
        """L_total = w1*L_data + w2*L_physics."""
        from backend._2_generative_engine.pinn_loss import PINNLoss
 
        loss_fn = PINNLoss(lambda_phys=0.1)
 
        pred_neff   = torch.tensor([[1.440]], dtype=torch.float32)
        target_neff = torch.tensor([[1.445]], dtype=torch.float32)
        geometry    = torch.zeros(1, 3)  # [pitch, d/pitch, wavelength]
 
        total_loss = loss_fn(pred_neff, target_neff, geometry)
        assert total_loss.item() > 0.0
        assert isinstance(total_loss, torch.Tensor)
 
    def test_lambda_phys_zero_equals_mse(self, device):
        """With lambda_phys=0, total loss should equal pure MSE loss."""
        from backend._2_generative_engine.pinn_loss import PINNLoss
 
        loss_fn_pinn = PINNLoss(lambda_phys=0.0)
        loss_fn_mse  = nn.MSELoss()
 
        pred   = torch.tensor([[1.440]])
        target = torch.tensor([[1.445]])
        geo    = torch.zeros(1, 3)
 
        pinn_loss = loss_fn_pinn(pred, target, geo)
        mse_loss  = loss_fn_mse(pred, target)
        assert abs(pinn_loss.item() - mse_loss.item()) < 1e-6
 
 
class TestARROWConditionLoss:
    """Tests for Anti-Resonant Reflecting Optical Waveguide constraint."""
 
    def test_arrow_condition_satisfied(self):
        """
        At ARROW wavelength, tube wall transmission loss should be minimised.
        t = mλ / 2√(n²-1) → loss minimum.
        """
        from backend._2_generative_engine.pinn_loss import ARROWConditionLoss
 
        # For t=0.42µm, n=1.444: λ_AR = 2*0.42*√(1.444²-1) ≈ 895nm
        t = 0.42e-6
        n_glass = 1.444
        lambda_ar = 2 * t * np.sqrt(n_glass**2 - 1)  # ≈ 895nm
 
        loss_fn   = ARROWConditionLoss()
        wall_t    = torch.tensor(t * 1e6)     # convert to µm
        wavelength = torch.tensor(lambda_ar * 1e9)  # convert to nm
 
        residual = loss_fn(wall_t, wavelength, n_glass=n_glass, order=1)
        assert residual.item() < 1e-4
 
    def test_arrow_condition_violated(self):
        """At resonance wavelength (halfway between AR orders), loss is high."""
        from backend._2_generative_engine.pinn_loss import ARROWConditionLoss
 
        t = 0.42e-6
        n_glass = 1.444
        lambda_ar = 2 * t * np.sqrt(n_glass**2 - 1)
        # Resonance wavelength is half of AR wavelength
        lambda_res = lambda_ar / 2
 
        loss_fn    = ARROWConditionLoss()
        wall_t     = torch.tensor(t * 1e6)
        wavelength = torch.tensor(lambda_res * 1e9)
 
        residual = loss_fn(wall_t, wavelength, n_glass=n_glass, order=1)
        assert residual.item() > 0.01   # Non-trivial violation
 
 
class TestMultiLevelPINN:
    """
    Tests for Multi-Level PINN framework (Nature Communications 2024 architecture).
    Decomposes fourth-order PDE into coupled first/second-order sub-networks.
    """
 
    def test_multilevel_network_initialises(self, device):
        from backend._2_generative_engine.multi_level_pinn import MultiLevelPINN
 
        model = MultiLevelPINN(
            input_dim=3,        # [pitch, d/pitch, wavelength]
            hidden_dim=128,
            num_levels=2        # Geometric + Electromagnetic sub-networks
        ).to(device)
 
        assert model is not None
        param_count = sum(p.numel() for p in model.parameters())
        assert param_count > 0
 
    def test_multilevel_output_shape(self, device):
        from backend._2_generative_engine.multi_level_pinn import MultiLevelPINN
 
        model = MultiLevelPINN(input_dim=3, hidden_dim=128, num_levels=2).to(device)
        x = torch.randn(16, 3).to(device)   # Batch of 16 design points
        # Output: [n_eff_real, n_eff_imag, mode_area, confinement_loss]
        output = model(x)
        assert output.shape == (16, 4)
 
    def test_multilevel_loss_decomposition(self, device):
        """Each level's loss should be independently computable."""
        from backend._2_generative_engine.multi_level_pinn import MultiLevelPINN
        from backend._2_generative_engine.pinn_loss import MultiLevelPINNLoss
 
        model   = MultiLevelPINN(input_dim=3, hidden_dim=128, num_levels=2).to(device)
        loss_fn = MultiLevelPINNLoss(level_weights=[0.5, 0.5])
        x       = torch.randn(8, 3).to(device)
        target  = torch.randn(8, 4).to(device)
 
        pred        = model(x)
        level_preds = model.get_level_outputs(x)   # List of per-level predictions
        total_loss  = loss_fn(pred, target, level_preds)
 
        assert total_loss.item() > 0.0
        assert not torch.isnan(total_loss)


