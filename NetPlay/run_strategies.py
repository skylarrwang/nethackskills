import numpy as np

import sys
import os
import subprocess
import argparse
from warnings import warn

ALLOWED_ROLES = [
    "archeologist",
    "barbarian",
    "cavewoman",
    "caveman",
    "healer",
    "knight",
    "monk",
    "priest",
    "priestess",
    "ranger",
    "rogue",
    "samurai",
    "tourist",
    "valkyrie",
    "wizard"
]

AGENT_GUIDE = """Your task is to win the game. Tips:
- Stay on the first 2 levels (depth=1/2, dungeon number=0) until you reached level 8.
- You can kick open locked doors, but that usually requires multiple tries. Note WHAMM means its still closed.
- When your health gets low, run away before healing.
- Corpses in your inventory will rot, do not eat them. Only eat freshly killed corpses. Keep eating corpses until satiated, but do not keep eating.
- Do not eat kobolds, they are poisonous.
- Only pray every 500 turns to fix bad situations, for example low health or when you are fainting.
- Use the keys "ykulnjbh" for specifying the directions "n ne e se s sw w nw". For example press the key "y" to indicate north.
- The skill "type_text" can be used to press multiple alphanumeric keys, use it to navigate menus faster.
- To move onto a tile occupied by a friendly monster stand next to it and press "m". Use this for shopkeepers.
- Dip long swords into fountains as a lawful character at level 5 or higher to get excalibur.
- Sacrifice corpses at altars for a chance to get powerful artifacts.
- You will timeout if you do not make progress for a while. So if something doesn't work on the first try, shift your focus onto something else."""

CREATIVE_AGENT_GUIDE = """You are a creative agent, that is interested in exploring the game as much as possible."
Your goals are to find interesting interactions and to discover new areas to explore.
You despise dying, as it will reset your progress.
Here are some survival tips:
- You can kick open locked doors, but that usually requires multiple tries. Note WHAMM means its still closed.
- When your health gets low, run away before healing.
- Corpses in your inventory will rot, do not eat them. Only eat freshly killed corpses. Keep eating corpses until satiated, but avoid overeating.
- Do not eat kobolds, they are poisonous.
- Only pray every 500 turns to fix bad situations, for example low health or when you are fainting.
- The keys "ykulnjbh" correspond to the directions "n ne e se s sw w nw".
- The skill "type_text" can be used to press multiple alphanumeric keys, use it to navigate menus faster.
- To move onto a tile occupied by a friendly monster stand next to it and press "m". Use this for shopkeepers.
- You will timeout if you do not make progress for a while. So if something doesn't work on the first try, shift your focus onto something else.
"""

EARLY_GAME_STRATEGIES = {
    "level_5": '''Your task is to reach experience level 5 or higher without descending past Dungeon Level 5. Tips:
        - Fight monsters on the first 5 levels to safely gain experience. Avoid descending too quickly.
        - Stay on the stairs to escape if overwhelmed by monsters.
        - Avoid fighting groups of monsters unless you have an escape route planned.
        - Heal whenever your health drops below 50%.
        - Use ranged attacks or spells to deal with dangerous monsters from a safe distance.
        - Use the "search" command to locate hidden doors or traps when exploration seems blocked.
        - Avoid using spells or abilities that consume too much energy early on unless necessary for survival.''',
    "stash": '''Your task is to create a stash near a safe location, such as stairs or an altar. Tips:
        - Only store useful items like potions, scrolls, wands, or backup weapons. Avoid storing junk.
        - Use containers such as chests, large boxes, or bags to organize your stash.
        - Regularly return to your stash to drop unnecessary items and reduce weight.
        - Avoid carrying too much weight; if you become "burdened" or "stressed," prioritize storing heavy items.
        - Protect fragile items like potions or scrolls by storing them in a sack or bag.
        - Consider placing your stash near an altar if possible, to identify or bless items as needed.''',
    "clear_minetown": '''Your task is to clear Minetown and benefit from its resources. Tips:
        - Use the stairs in Dungeon Level 2-4 to access the Gnomish Mines and find Minetown.
        - When entering Minetown, stay near the stairs initially to safely deal with incoming monsters.
        - Use the shops in Minetown to identify items by checking prices. Avoid angering shopkeepers.
        - If there is an altar, use it to identify blessed, cursed, or uncursed items.
        - Minetown is a safe zone for exploration, but be cautious of thieves that may steal your items.
        - Do not descend further into the Mines until you are well-prepared with proper gear and resistances.''',
    "clear_sobokan": '''Your task is to complete the Sokoban puzzle branch. Tips:
        - Use the stairs below the Oracle (Dungeon Level 6-10) to access Sokoban.
        - Sokoban consists of four puzzle levels where you must push boulders into holes to progress.
        - Avoid stepping into pits or holes. Push boulders carefully to avoid getting stuck.
        - Do not attempt Sokoban puzzles if you are heavily burdened or without sufficient food.
        - At the top level of Sokoban, you will find either a Bag of Holding or an Amulet of Reflection. Prioritize completing this task to obtain these rewards.
        - Use Sokoban as an opportunity to gain experience and collect useful items along the way.''',
    "find_use_altars": '''Your task is to find and use an altar for identifying items and making sacrifices. Tips:
        - Use the "search" command to locate hidden altars or check Minetown for an altar.
        - Sacrifice corpses of monsters to the altar for a chance to receive blessings or artifacts.
        - Only sacrifice corpses that are compatible with your alignment. For example, avoid sacrificing peaceful creatures.
        - Use the altar to identify the status of items (blessed, cursed, or uncursed) before equipping or using them.
        - If you find multiple altars, prioritize the one closest to Dungeon Level 10 for easy access.
        - Use "altar camping" to stay near an altar and improve your chances of obtaining artifacts or blessings.''',
    "clear_gnomish_mines": '''Your task is to safely clear the Gnomish Mines and retrieve key items. Tips:
        - Explore the Mines cautiously, staying near the stairs when entering new levels to retreat if needed.
        - Beware of trapdoors that can drop you into unexplored levels. Use the "search" command frequently.
        - Do not wear your best armor unless you have polymorph control, as polymorph traps can destroy your gear.
        - Prioritize obtaining a Luckstone at the bottom of the Mines. Ensure it is blessed if possible.
        - Collect gems and useful gray stones, but avoid picking up cursed Lodestones.
        - Avoid fighting Mind Flayers unless you have sufficient experience (level 8 or higher), telepathy, and blindness methods.'''
}

class StrategyConfig:
    def __init__(self, strategy: str, include_main: bool=True, include_creative: bool=False):
        self.strategy = EARLY_GAME_STRATEGIES[strategy]
        
        if include_main and include_creative:
            raise ValueError("Cannot include both main and creative strategies.")
        
        self.general = AGENT_GUIDE if include_main else CREATIVE_AGENT_GUIDE if include_creative else None
        self.specific_prompt = f"Here is your current specific task: {self.strategy}"
        self.general_prompt = f"Here is general advice: {self.strategy}" if self.general else None
    
    def __str__(self):
        return self.specific_prompt + "\n" + self.general_prompt if self.general_prompt else ""

RUN_PY = "/Users/srwang/Documents/pathways_fall/NetPlay/run.py"
LOG_FOLDER = "/Users/srwang/Documents/pathways_fall/logs"

if __name__ == "__main__":
    # Parse args
    parser = argparse.ArgumentParser(
        prog = 'Runs the LLM agent on NetHack with a specific role.'
    )
    parser.add_argument('agent', type=str, default="llm", help="Choose which agent to run (handcrafted or llm).")
    parser.add_argument('-strategy', type=str, default="level_5", help="Choose which *early game* strategy to run.")
    parser.add_argument('-agent_name', type=str, default="agent", help="A name for the agent for logging purposes.")
    parser.add_argument('-seeds', nargs="+", type=int, default=None, help="Specify a list of integer seeds for each run.")
    parser.add_argument('-num_runs', nargs="+", type=int, default=30, help="Specify how many runs to run. Will be ignored if -seeds is set.")
    parser.add_argument('-role', type=str, default="valkyrie", choices=ALLOWED_ROLES, help="The role the agent will use.")
    parser.add_argument('-model', type=str, default="gpt-4o-mini", help="Choose the OpenAI language model to use.")
    parser.add_argument('--censor_nethack_context', action='store_true', help="Censors any mentions of the word 'NetHack' before passing prompts to the LLM.")
    parser.add_argument('--render', default=False, action='store_true', help="Renders each run in an window.")
    parser.add_argument('--use_guide', default=False, action='store_true', help="When set the agent gets access to a guide for playing the game.")
    parser.add_argument('--use_creative_guide', default=False, action='store_true', help="When set the agent will be tasked to act creative.")
    parser.add_argument('--update_hidden_objects', action='store_true', help="Enable to fix a bug where removed objects would still show up in the environment description.")
    args = parser.parse_args()
    if args.seeds:
        print("-seeds was set, ignoring -num_runs.")
        seeds = args.seeds
        args.num_runs = len(args.seeds)
    else:
        seeds = np.random.randint(1000000, size=args.num_runs)

    if args.role.lower() not in ALLOWED_ROLES:
        print(f"The role {args.role} is not valid. Make sure to write the full role name and lookout for typos.")
        exit()

    if args.strategy not in EARLY_GAME_STRATEGIES:
        print(f"The strategy {args.strategy} is not valid. Make sure to write the full strategy name and lookout for typos.")
        exit()

    if args.use_guide and args.use_creative_guide:
        print("Both flags --use_guide and --use_creative_guide have been set. Only use one.")
        exit()
                
    for seed in seeds:
        log_folder = os.path.join(LOG_FOLDER, args.agent_name, args.role, str(seed))
        if os.path.exists(log_folder):
            print(f"Skipping seed {seed} because the folder {log_folder} already exists. Delete it to re-run this seed.")
            continue

        print(f"Running {args.agent_name} with seed {seed}.")
        try:
            os.makedirs(log_folder, exist_ok=True) 

            process_args = [
                args.agent,
                "-task", StrategyConfig(args.strategy, include_main=args.use_guide, include_creative=args.use_creative_guide).__str__(),
                "-log_folder", log_folder,
                "-seed", str(seed),
                "-character", args.role,
                "-model", args.model,
                "--keep_log_folder",
                "--disable_finish_task_skill"
            ]
            if args.censor_nethack_context:
                process_args.append("--censor_nethack_context")
            if args.update_hidden_objects:
                process_args.append("--update_hidden_objects")
            if args.render:
                process_args.append("--render")

            with open(os.path.join(log_folder, "out.txt"), "w") as out_file:
                subprocess.run(["python", RUN_PY, *process_args], stdout=out_file)
        except Exception as e:
            warn(f"Running {args.agent_name} with seed {seed} failed:\n{e}")
    