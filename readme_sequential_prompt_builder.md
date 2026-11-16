# Technical Reference: ComfyUI Sequential Storyboarding & Prompt Automation Pipeline

This document details the lightweight, deterministic prompt automation system designed to orchestrate sequential storytelling layouts (multi-panel comics, animation keyframes, or concept sequences). It dynamically maps properties from a localized relational trait database, injects synchronized runtime variables into a ComfyUI graph canvas, and blasts continuous rendering streams to a local server API socket.

---

## 🧭 1. High-Level Architectural Overview

The system operates as a zero-dependency, local automation pipeline capable of generating single structural frames or multiple sequentially linked frames in a single processing thread:

[ prompts_data.json ]
│
(Reads Global Scoped Elements)
▼
[ prompt_builder.py ]
│
(Iterates prompt_list Loop Stream)
- Evaluates Fresh Seed per panel
- Evaluates Fresh Timestamp per panel
- Cleans and Clones Memory Workspaces
▼
[ workflow_api_template.json ]
│
(Injected Dynamic Parameters)
│
(HTTP POST /prompt)
▼
[ ComfyUI Local Server ]

### 🔁 The Execution Lifecycle:
1. **Global Element Locking (Narrative Consistency):** The script parses a local JSON database and extracts baseline environment parameters (Artistic Styles, Core Actors/Characters, and Object Props) **once** at global script initialization scope. This guarantees visual continuity across arbitrary rendering lengths.
2. **Explicit Panel Storyboarding:** Individual scene descriptions are mapped inside a variable-length list array. Characters and props are dynamically referenced inside explicit text templates, allowing for complex narrative beat structuring.
3. **Automated Loop Scaling:** The script counts and iterates through the defined panels. It requires zero configuration modifications to scale from generating 1 image to 100 images.
4. **Runtime Workspace Sandboxing:** On every loop iteration, the script calculates a unique 15-digit random seed and a local hardware clock timestamp down to the exact second. It deep-clones a raw memory copy of the ComfyUI API template to prevent attribute bleeding between frames.
5. **API Queue Bombardment:** The unique panel dictionary payloads are packaged and sequentially targeted at ComfyUI's backend endpoint (`/prompt`) via HTTP network requests, filling the server's render queue in milliseconds.

---

## 📦 2. Component Layout & Data Schemas

### A. The Input Database (`prompts_data.json`)
The source data uses an object root housing isolated, uniform arrays. This keeps data human-editable while remaining simple for Python to query.
* **`meta_data`**: Houses complex parameters controlling render fidelity, aspect ratios, engine keywords, and primary aesthetic styles.
* **`Character`**: Structured object lists containing detailed semantic descriptions of actors/subjects using an explicitly capitalized `"Description"` property key.
* **`prop`**: Lightweight string values representing items interacting with characters.

### B. The Workflow Template (`workflow_api_template.json`)
Unlike standard UI workspace saves (which contain frontend render vectors, box colours, and link logic), this template is exported via ComfyUI's **Developer Mode API Format**. It represents a flat dictionary mapping node configurations directly as executable instructions for the server engine.

---

## ⚙️ 3. Deep Dive: Major Script Functions & Logic

The entire runtime pipeline is executed inside `prompt_builder.py` and relies entirely on Python standard libraries (`json`, `random`, `sys`, `urllib.request`, `datetime`, `time`). It breaks down into four operational stages:

### Stage 1: Explicit Multi-Line String Assembly
* **Mechanism:** To keep ultra-long prompts completely readable and easily editable inside text editors like VS Code, the script utilizes **implicit string literal concatenation combined with parentheses bundling**.
* **Formatting Logic:** Individual prompt snippets are split across multiple editor rows bounded by `f"..."` quotes, with standard `\n\n` newlines explicitly forcing crisp paragraph separation inside the ComfyUI nodes upon execution.

### Stage 2: Sandbox Dictionary Deep Clones
* **Mechanism:** Modifying nested Python dictionaries by reference causes changes made in one step to overwrite data across all steps. To prevent panel context mixing, the script handles the template graph via a native serialization clone technique:
  ```python
  temp_workflow = json.loads(json.dumps(api_workflow_base))
  ```
* **Result:** This constructs a sterile memory snapshot for every individual panel iteration, ensuring fresh graph generation.

### Stage 3: Dynamic Node Targeting
Instead of referencing volatile, hardcoded node IDs (which shuffle whenever blocks are connected or disconnected in the UI), the script scans the top-level keys of the API layout and maps parameters matching structural conditions:

| Targeted Node Field | Filtering Condition | Modification Target |
| :--- | :--- | :--- |
| **Positive Prompt Node** | `class_type == "CLIPTextEncode"` **AND** `_meta["title"] == "Positive Prompt"` | Overwrites `node_data["inputs"]["text"]` with active panel text prompt. |
| **Sampler Node** | `class_type == "KSampler"` | Overwrites `node_data["inputs"]["seed"]` with calculated 15-digit int. |
| **Output Image Node** | `class_type == "SaveImage"` | Overwrites `node_data["inputs"]["filename_prefix"]` with unique timestamp and structural index (`_panel{i}_moss`). |

### Stage 4: Network Stream Execution & Time Syncing
* **Serialization:** The sandboxed data is encapsulated under a root `"prompt"` payload key, encoded into a standard byte stream, and piped using `urllib.request.Request` directly to `http://127.0.0`.
* **Clocks Synchronization Guard:** High-speed computer processors can compile and send jobs within microseconds. Because filenames are stamped using date-time parameters down to the single second (`%Y%m%d_%H%M%S`), firing requests too quickly would cause filenames to collide and overwrite on your local drive. The engine implements a strict `time.sleep(1)` loop threshold step to force the system clock to safely step forward before queueing subsequent panels.

---

## 🛠️ 4. Advanced Production Customizations (Next Phase Reference)

The multi-character narrative loop framework serves as a modular production core. Future scaling expansions can be built using these integration targets:

* **Variable Cast Scaling:** Adding positional character arrays inside `prompts_data.json` to handle multi-actor tracking panels (e.g., dynamically calling a 3rd or 4th distinct character description file via index array querying).
* **Automatic Sub-directory Structuring:** Modifying the `filename_string` path assignment to create automated chapter or scene sorting folders inside your ComfyUI outputs directory (e.g., setting `filename_prefix` to `my_comic/chapter_1/timestamp_panel1`).
* **External Command Arguments:** Integrating Python's `argparse` standard library to execute whole pipeline tasks via shell commands, such as forcing a specific prompt database configuration selection directly from your terminal.
