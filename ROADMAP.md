To build a sleek, responsive interface in HTML, CSS, and TypeScript that rivals modern AI-dev tools, we will follow this high-velocity sequence:

Phase 1: The Workspace (HTML/CSS): * Implementing a Three-Pane Layout: (1) Left: Parameter Input/Chat Agent, (2) Center: Real-time 2D/3D WebGL Viewer for waveguides, (3) Right: GDSII/STL code preview.

Style: Dark mode "Foundry" aesthetic—high contrast, monospace fonts, and neon-glass accents.

Phase 2: The Logic (TypeScript):

Real-time Validation: Using TS to mirror our Pydantic schemas. If a user types "500nm etch" on a "220nm chip," the UI highlights the input in red before the API is even called.

Websocket Integration: Connecting the frontend to api/gateway_v2.py so the user can see the "Grader Node" and "Simulation Bridge" logs scrolling in real-time.

Phase 3: The Desktop Shell (Electron/Tauri):

Wrapping the web app into a desktop executable. This is critical for photonics engineers who often work in secure lab environments where they prefer local software over browser-based tools.

Phase 4: The Landing Page (The "Marketing" Face):

A high-converting professional homepage that highlights the DSR-CRAG reliability and the speed of the Generative Engine.
