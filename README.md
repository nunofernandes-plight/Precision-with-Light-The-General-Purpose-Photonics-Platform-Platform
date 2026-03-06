# Project: AI-Optics-PCF-Regressor  

 ## An Ultra-Fast Neural Network Proxy for Photonic Crystal Fiber Design.

## 1. Overview
This repository provides a machine-learning-based surrogate model for characterizing Specialty Optical Fibers. By training on high-fidelity FEM data, the engine predicts the Complex Effective Index ($n_{eff}$) and Dispersion ($D$) without the need for intensive Maxwell solvers.

## 2. Installation 

#### Clone the repository
```bash
git clone https://github.com/your-org/pcf-regressor-ai-optics.git
cd ai-optics-pcf-regressor
```

#### Install dependencies
```bash
pip install -r requirements.txt
```

## 3. Configuration & Software Scripts


```bash
numpy>=1.24.0
pandas>=2.0.0
scikit-learn>=1.3.0
joblib>=1.3.0
matplotlib>=3.7.0
PyTorch 2.60.0 latest version
```

[![PyTorch Version](https://img.shields.io)](https://pytorch.org/blog/pytorch2-6/)



### YAML Configuration:

```
simulation:
  wavelength_range: [1.3, 1.6] # Microns
  pitch_range: [1.5, 4.0]
  max_iter= 20000
```

```Python
from setuptools import setup, find_packages

setup(
    name="pcf-regressor-ai-optics",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'numpy', 'pandas', 'scikit-learn', 'joblib'
    ],
    author="Precision with Light Team",
    description="ML-Accelerated Specialty Fiber Design Engine",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Physics",
    ],
)
```

## 4. Traning & Inference

If you have a dataset from Lumerical or COMSOL, you can retrain the engine:
```
python main.py --mode train --data data/experimental_results.csv
```
To run an instant prediction:

```
python main.py --mode predict --params "[2.3, 0.5, 1.55]"
```
