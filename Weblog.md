## Weblog – Iterative Development of *TZ – The Lost War Robot*

This weblog documents the iterative development of the project from the first classroom prototype to the current 1.0 packaged version.

---

### October 2024 – Initial NLP classroom prototype

- **Context**: This project started as a small in-class exercise for an NLP course.
- **Goal**: Experiment with basic chatbot behaviour and dialogue prompts.
- **Implementation**:
  - A single Python script with simple rule-based replies.
  - No external AI API, no task flow, no puzzle structure.
  - The “robot” character was only a loose idea; there was no clear narrative arc.
- **Reflection**:
  - The prototype proved that a conversational interface can be engaging even with very simple logic.
  - However, it also showed the limitations of a static rule-based chatbot in terms of narrative depth and replay value.

---

### June 2025 – Second version: adding AI API for story generation

- **Motivation**: I wanted the robot to feel less scripted and more reactive, so I introduced an LLM backend.
- **Key changes**:
  - Integrated an AI API to generate TZ’s responses and memory fragments.
  - Started to sketch a **loose story framework** about a damaged war robot trying to restore its systems.
  - Added simple “mission prompts” to shape the AI outputs (e.g. asking for technical explanations or emotional reflections).
- **Impact**:
  - The dialogue became more varied and surprising, creating a stronger sense of character.
  - At the same time, the lack of a clear task structure made the experience feel more like an open chat than a designed game.
- **Design learning**:
  - AI is powerful for content generation, but it needs a solid narrative and interaction structure to be meaningful for players.

---

### September 2025 – Third version: Tkinter UI and structured tasks

- **Motivation**: Turn the loose chatbot into a playable game with clear goals and feedback.
- **Key changes**:
  - Rebuilt the interface using **Tkinter** with chat bubbles, system messages and status hints.
  - Designed a **sequence of technical tasks**:
    - Power path restoration
    - Frequency calibration
    - Data decryption
    - Alien signal decoding
    - Combat logic reconstruction
  - Introduced a **deviation value** and multiple endings, so player choices had visible consequences.
- **Impact**:
  - The experience changed from “talking to a bot” to “playing through a story-driven puzzle sequence”.
  - The Tkinter UI made the conversation more readable and helped communicate system states clearly.
- **Challenges**:
  - All logic, UI code and API calls lived in one large `main.py`, which became hard to maintain and extend.
  - Timing of messages and error handling for the LLM sometimes broke the narrative flow.

---

### October–November 2025 – Version 1.0: Front–back separation and new UI

- **Motivation**: Improve user experience, make the project easier to maintain, and prepare it as a portfolio-ready artefact.
- **Architectural refactor**:
  - Split the monolithic script into **backend modules**:
    - `game_logic.py` – core state machine and game rules.
    - `task_handlers.py` – puzzle logic and task flow.
    - `memory_generator.py` – AI-assisted memory fragment generation.
    - `stage_handlers.py` & `tz_routes.py` – dialogue stages and HTTP routes for the frontend.
  - Introduced a **separate frontend** built with a modern web UI (React-style chat layout).
- **UX & visual design updates**:
  - Designed a brand-new cyber-themed interface with clearly distinguished system / player / NPC bubbles.
  - Added typing delays and message sequencing to preserve the storytelling rhythm from the Tkinter version.
  - Cleaned up redundant confirmations (e.g. memory playback choices) to reduce friction.
- **Stability & polish**:
  - Debugged puzzle logic so each task behaves consistently with the original single-file version.
  - Fixed subtle issues such as:
    - Repeated memory fragments when tasks were bypassed.
    - LLM prompts accidentally producing “invalid selection” messages before the player answered.
    - Timing issues where the next bubble appeared before the previous one finished “typing”.
  - Added a **packaged macOS build** (`dist/TZ_War_Robot.app`), so testers can run the game without installing Python or Node.

- **Reflection**:
  - The project evolved from a quick classroom demo into a fully packaged 1.0 game with a clear interaction flow.
  - Separating frontend and backend not only improved user experience, but also made it easier to reason about game state, debug logic and iterate on UI design.
  - This process highlighted the importance of balancing AI-generated content with hand-crafted structure to maintain narrative coherence.

---

### Next steps

- Explore richer branching in the narrative using the existing state machine.
- Experiment with additional personas or emotional profiles for TZ.
- Consider adding analytics hooks to better understand how players navigate the tasks and endings.
