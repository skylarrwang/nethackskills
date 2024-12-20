import gym
import nle
import os
from nle import nethack
from typing import Any, Dict, Tuple
from termcolor import colored

# Import the skills
# from netplay.nethack_agent.skills import *
from netplay.handcrafted_agent.agent import HandcraftedAgent
from netplay.nethack_utils.nle_wrapper import NethackGymnasiumWrapper
from netplay.logging.nethack_monitor import NethackH5PYMonitor
from nle_language_wrapper import NLELanguageWrapper


# Import Nethack Gymnasium Wrapper
from netplay.nethack_utils.nle_wrapper import NethackGymnasiumWrapper

## PATHS
LOG_FOLDER = "/Users/srwang/Documents/pathways_fall/logs/rl_skills"

## Initialize the environment
## Initialize the agent - use handcrafted agent, then we will call their skill methods

def skill_step(env, agent, skill, parameters=None):# -> Tuple[Dict[str, Any], float, bool]:
    obs, total_reward, done, info = env.reset(), 0, False, {}
    skill_map = {
            "fight": agent.fight,
            "explore": agent.explore,
            "eat": agent.try_eat,
            "heal": agent.try_heal,
            #"handle_popups": agent.handle_popups,
            "pickup": agent.try_pickup_useful_object
    }
    generator = skill_map[skill]
    action_gen = generator(**parameters) if parameters else generator()
    
    print(f"Executing skill: {skill}, {action_gen}")
    
    try:
        for step in action_gen:
            if step.executed_action():
                action_description = NLELanguageWrapper.all_nle_action_map[step.step_data.action][0]
                data = step.step_data
                obs, done, info = data.observation, data.done, data.info
                total_reward += data.reward
                parts = [f"Executed action '{action_description}'.", f"Thoughts: {step.thoughts}" if step.thoughts else None, f"Reward: {step.step_data.reward}" if step.step_data.reward else None]
                print(" ".join([p for p in parts if p]))
            if step.is_done():
                if step.has_failed():
                    print(f"Skill failed: {step.error}")
                    break
            elif step.thoughts:
                print(colored(f"Thinking: {step.thoughts}", "blue"))
    except KeyboardInterrupt:
        print(f"Aborting run.")
    return obs, total_reward, done, info


## Example: use the fighting skill in one step
if __name__ == "__main__":
    env = NethackGymnasiumWrapper(render_mode="human", autopickup=True)
    env = NethackH5PYMonitor(env, os.path.join(LOG_FOLDER, "trajectories.h5py"))

    agent = HandcraftedAgent(env, log_folder=LOG_FOLDER)
    agent.init()
    
    ## try the fighting skill
    skill = "fight"
    obs, reward, done, info = skill_step(env, agent, skill)
    print(f"Done with skill: {skill}, {reward}")
