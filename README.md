# NetHack Strategy API
## Overview
This repository builds upon the **NetPlay** repository by extending its capabilities with **strategy abstraction** for guiding agents through high-level gameplay objectives. The **Strategy API** enhances the existing framework by introducing reusable strategies to enable more effective exploration of NetHack's early game. Also building out a **Skill API** that is a wrapper for the RL environment, not fully completed.

---

## Available Strategies
The following early game strategies are available for guiding the agent:

- **`level_5`**: Reach experience level 5+ without descending past Dungeon Level 5.
- **`stash`**: Create a stash near a safe location (e.g., stairs or an altar).
- **`clear_minetown`**: Clear Minetown and benefit from its resources.
- **`clear_sobokan`**: Complete the Sokoban puzzle branch to obtain rewards.
- **`find_use_altars`**: Find and use an altar for identifying items and making sacrifices.
- **`clear_gnomish_mines`**: Safely clear the Gnomish Mines and retrieve key items.

Each strategy includes specific tasks and tips designed to help agents succeed in early game exploration and survival.

---

## Setup

Follow setup requirements in the following repositories:
- NetPlay
- NLE
- nle-language-wrapper

---

## Usage

**Examples:**
Run the LLM agent from NetPlay with default settings:

`python ./run_full_runs.py llm -agent_name "NetPlay_agent" -num_runs 1 -model "gpt-4o-mini" --use_guide --render`

Run the LLM agent with `stash` strategy (or any other) AND general prompt:

`python ./run_strategies.py llm -agent_name "stash" -strategy "stash" -num_runs 1 -model "gpt-4o-mini" --use_guide --render`

Run the LLM agent with `stash` strategy (or any other) ONLY (no general prompt):

`python ./run_strategies.py llm -agent_name "stash" -strategy "stash" -num_runs 1 -model "gpt-4o-mini" --render`

---

## Citations

1. Nikolaj Goodger, Peter Vamplew, Cameron Foale, and Richard Dazeley.  
   *A NetHack learning environment language wrapper for autonomous agents.*  
   Journal of Open Research Software, 11, June 2023.  

2. Dominik Jeurissen, Diego Perez-Liebana, Jeremy Gow, Duygu Cakmak, and James Kwan.  
   *Playing NetHack with LLMs: Potential & Limitations as Zero-Shot Agents.*  
   In *2024 IEEE Conference on Games (CoG)*, pages 1–8, 2024.  

3. Heinrich Küttler, Nantas Nardelli, Alexander H. Miller, Roberta Raileanu, Marco Selvatici, Edward Grefenstette, and Tim Rocktäschel.  
   *The NetHack Learning Environment.*  
   In *Proceedings of the Conference on Neural Information Processing Systems (NeurIPS)*, 2020.
