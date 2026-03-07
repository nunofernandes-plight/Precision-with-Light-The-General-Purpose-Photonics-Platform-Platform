# Project Structure for pcf-api-demo

This setup allows an engineer or industry partner to interact with a "Software-Defined" fiber file in real-time. 
Instead of waiting for a batch of simulations to finish, they can adjust sliders for pitch or wavelength 
and see the optical response instantly.
```
/api
├── main.py            # FastAPI Application
├── schemas.py         # Data validation (Pydantic)
├── engine_wrapper.py  # Model loading and inference logic
├── /static            # HTML/JS for the Slider Dashboard
└── requirements.txt
```
