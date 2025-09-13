# Autonomous CTF Solver

This project is an autonomous agent that solves Capture The Flag (CTF) challenges, specifically tailored for the OverTheWire Bandit wargame.

## Architecture

The agent follows a simple Observe-Think-Act loop:
1.  **Observe**: It captures the output from an SSH shell.
2.  **Think**: It uses a large language model (LLM) to decide the next command based on the current goal and the last output.
3.  **Act**: It executes the command on the remote machine.
4.  **Validate**: It checks the output for a flag pattern.

## How to Run

1.  **Dependencies**: Install the required Python packages from `requirements.txt`.
    ```bash
    pip install -r requirements.txt
    ```

2.  **API Key**: Set your Gemini API key as an environment variable. The agent will use placeholder logic if this is not set.
    ```bash
    # On Windows
    set GEMINI_API_KEY="YOUR_API_KEY"
    
    # On Linux/macOS
    export GEMINI_API_KEY="YOUR_API_KEY"
    ```

3.  **Run the Agent**: Start the solver from the project's root directory (`CTF`).
    ```bash
    python -m ctf_solver.main
    ```

The agent will log its progress and save any found flags to `ctf_solver/state.json`.

## Configuration

The CTF levels, credentials, and goals are defined in `ctf_solver/levels.yaml`. You can extend this file to add more levels.

## Safety

The agent operates under a strict command allow-list to prevent destructive or unsafe operations. See `policies.py` for the defined rules.
