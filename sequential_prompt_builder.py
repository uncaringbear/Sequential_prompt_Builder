import json
import random
import sys
import time
import urllib.request
from datetime import datetime

COMFYUI_SERVER_URL = "http://127.0.0.1:8188"

# ==========================================
# 1. LOAD THE TEMPLATE & DATA
# ==========================================
try:
    with open('prompts_data.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    with open('workflow_api_template.json', 'r', encoding='utf-8') as file:
        api_workflow_base = json.load(file)
except Exception as e:
    print(f"❌ Error loading starter files: {e}")
    sys.exit(1)


# ==========================================
# 2. GLOBAL SELECTIONS (Enforces Narrative Consistency)
# ==========================================
# These are picked ONCE. They stay the same across all 3 panels.
selected_style = random.choice(data['meta_data'])['style']

# Grab two character dictionaries
char_data1 = random.choice(data['Character'])
char_data2 = random.choice(data['Character'])

# Extract just their descriptions for the prompt text
char1 = char_data1['Description']
char2 = char_data2['Description']

# Pick a single prop that travels through the story
selected_prop = random.choice(data['prop'])['item']


# ==========================================
# 3. EXPLICIT PANEL SCRIPTING
# ==========================================
# We construct your 3 distinct narrative beats using the global elements
prompt_list = [
    # Panel 1: The hand-off
    (
        f"{selected_style}\n\n"
        f"A scene featuring two people: first character is a {char1}. "
        f"Second character is a {char2}. "
        f"The first character is carefully handing the second character a {selected_prop}."
    ),
    
    # Panel 2: The close-up / reaction
    (
        f"{selected_style}\n\n"
        f"A dramatic close-up shot of a {char2}. "
        f"They are holding a {selected_prop} and looking down at it with a puzzled expression."
    ),
    
    # Panel 3: The punchline
    (
        f"{selected_style}\n\n"
        f"A two-shot scene: the first character ({char1}) is pointing and laughing hysterically. "
        f"The second character ({char2}) is holding a {selected_prop} and looking directly at them with an annoyed expression."
    )
]


# ==========================================
# 4. LOOP AND BLAST JOBS TO COMFYUI
# ==========================================
print("🎭 Comic Pipeline Initialized!", flush=True)
print(f"👥 Cast: {char_data1['Name']} & {char_data2['Name']}")
print(f"📦 Object: {selected_prop}\n", flush=True)

for i, active_prompt in enumerate(prompt_list, start=1):
    print(f"--- [Job {i}/{len(prompt_list)}] Processing Panel {i} ---", flush=True)
    
    # 🎲 Unique seed and clean runtime timestamp suffix per panel iteration
    current_seed = random.randint(100000000000000, 999999999999999)
    current_time_suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename_string = f"{current_time_suffix}_panel{i}_moss"

    # Deep clone a clean layout copy of the base workflow dictionary
    temp_workflow = json.loads(json.dumps(api_workflow_base))

    # Inspect and update the dynamic graph entries
    for node_id, node_data in temp_workflow.items():
        if isinstance(node_data, dict):
            class_type = node_data.get("class_type")
            meta_title = node_data.get("_meta", {}).get("title", "")
            inputs = node_data.get("inputs", {})

            if class_type == "CLIPTextEncode" and meta_title == "Positive Prompt":
                inputs["text"] = active_prompt
            elif class_type == "KSampler":
                inputs["seed"] = current_seed
            elif class_type == "SaveImage" and "filename_prefix" in inputs:
                inputs["filename_prefix"] = filename_string

    # Frame execution payload structure and pipe to server socket
    try:
        payload = {"prompt": temp_workflow}
        json_data = json.dumps(payload).encode('utf-8')
        
        req = urllib.request.Request(
            f"{COMFYUI_SERVER_URL}/prompt", 
            data=json_data, 
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req) as response:
            server_resp = json.loads(response.read().decode('utf-8'))
        
        print(f"🚀 Queued successfully! ID: {server_resp.get('prompt_id')}")
        print(f"📁 Saving to disk as: {filename_string}\n", flush=True)

    except Exception as e:
        print(f"❌ Failed to send Panel {i}: {e}\n", flush=True)

    # ⏳ Brief sleep step so file headers never collide clocks on fast systems
    time.sleep(1)

print("=== 🏁 Comic Generation Queue Complete! ===")
