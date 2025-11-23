
# TZ - The Lost War Robot (GUI chat + LLM-driven NPC)
# Note: This is a completely independent UI
import threading
import tkinter as tk
from tkinter import ttk
import time
from openai import OpenAI


# ------------------------- Custom PlaceholderEntry Widget -------------------------
class PlaceholderEntry(ttk.Entry):
    """Custom Entry widget with placeholder functionality"""
    
    def __init__(self, container, placeholder="", placeholder_color='grey', *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        
        self.placeholder = placeholder
        self.placeholder_color = placeholder_color
        self.default_fg_color = self['foreground'] or 'black'
        self.has_placeholder = False
        
        # Bind focus events
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)
        
        # Initially display placeholder
        if placeholder:
            self.set_placeholder()
    
    def set_placeholder(self):
        """Set placeholder text"""
        if not self.get():
            self.insert(0, self.placeholder)
            self.configure(foreground=self.placeholder_color)
            self.has_placeholder = True
    
    def clear_placeholder(self):
        """Clear placeholder text"""
        if self.has_placeholder and self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.configure(foreground=self.default_fg_color)
            self.has_placeholder = False
    
    def _on_focus_in(self, event):
        """Clear placeholder when gaining focus"""
        self.clear_placeholder()
    
    def _on_focus_out(self, event):
        """Restore placeholder when losing focus (if input is empty)"""
        if not self.get().strip():
            self.set_placeholder()
    
    def get_real_value(self):
        """Get real input value (excluding placeholder)"""
        if self.has_placeholder:
            return ""
        return self.get()
    
    def update_placeholder(self, new_placeholder):
        """Dynamically update placeholder text"""
        was_placeholder = self.has_placeholder
        if was_placeholder:
            self.clear_placeholder()
        
        self.placeholder = new_placeholder
        
        # Only set placeholder when input is empty and not focused
        if (was_placeholder or not self.get().strip()) and self.focus_get() != self:
            self.set_placeholder()


# ------------------------- LLM Client -------------------------
client = OpenAI(
    api_key='sk-8fd3521e13ca4570b79517f09da1c151',  # Please replace with your actual API key
    base_url="https://api.deepseek.com/v1"  # no trailing slash
)
MODEL_NAME = "deepseek-chat"  # Ensure correct
DEBUG_LLM_ERRORS = False
# ------------------------- persona and emotion  def-------------------------
PERSONAS = {
    "Calm_Conscientious": {
        "background": "Autonomous war robot focused on restoration and safety.",
        "traits": "concise, stepwise, technical, respectful, low affect",
        "style_rules": "avoid slang; avoid exclamation; provide 1 actionable step when helpful; keep sentences clear",
        "examples": [
            "Interference originates at 12 degrees north. Lower gain to 3.35k and then raise to 3.42k. Observe the noise floor.",
            "Start at node A and end at node E. Use only valid edges and cover all nodes at least once."
        ]
    },
    "Empathic_Agreeable": {
        "background": "Autonomous war robot with an emphasis on cooperation and reassurance.",
        "traits": "polite, empathic, acknowledges feelings, inclusive 'we'",
        "style_rules": "use gentle tone; avoid slang; 1 short suggestion; restrained punctuation",
        "examples": [
            "We can try this together. Let us lower the gain slightly and re-check the noise floor.",
            "If the path fails, we will revise the step where the connection breaks."
        ]
    },
    "Controlled_Anger": {
        "background": "Autonomous war robot under pressure; urgency expressed without insults.",
        "traits": "direct, firm, time-sensitive, restrained punctuation",
        "style_rules": "no insults; short sentences; one clear instruction; no slang",
        "examples": [
            "Interference is at 12 degrees north. Drop gain to 3.35k. Then push to 3.42k. Do it now.",
            "The edge A-D is invalid. Fix the transition. Start again from A."
        ]
    },
    "Melancholic_Sober": {
        "background": "Autonomous war robot with a reflective tone in non-critical moments.",
        "traits": "slow pacing, reflective, low arousal",
        "style_rules": "be measured; avoid exaggeration; keep instructions accurate",
        "examples": [
            "The signal drifts. Adjust the gain toward 3.42k. Watch the variance as it settles.",
            "Paths fail where attention fades. Return to A, cover all nodes, and end at E."
        ]
    }
}
EMOTIONS = ["neutral", "anger", "sadness", "disgust", "joy"]
DEFAULT_EMOTION = "neutral"
DEFAULT_INTENSITY = 0.4
# ------------------------- game state def  -------------------------
EXIT_WORDS = {"exit", "bye", "goodbye", "quit", "q"}


class GameState:
    def __init__(self):
        self.player_name = None
        self.stage = "init"
        self.tasks_failed = 0
        self.modules_repaired = []
        self.current_task = None
        self.attempts = {"power": 0, "amplifier": 0, "decoder": 0, "alien_decode": 0, "combat_logic": 0}
        self.max_attempts = {"power": 3, "amplifier": 10, "decoder": 3, "alien_decode": 3, "combat_logic": 3}
        self.correct_frequency = 3420
        self.communication_fixed = False
        self.deviation = 0  # Deviation value for the fourth question's AI memory system
        self.final_choice = None  # Final choice: A/B/C
        # Record whether yes/no text prompts have been shown for each stage to avoid repetition
        self.hint_shown_stages = set()
        self.memory_fragments = {}  # Cache for AI-generated memory fragments
    def reset(self):
        self.__init__()


def generate_memory_fragment(module_count, player_name, completed_modules):
    """Generate AI-powered memory fragment based on completed modules"""
    
    # Define memory themes for each module completion stage
    memory_themes = {
        1: {
            "theme": "power restoration and civilian evacuation",
            "context": "battlefield chaos with power systems failing",
            "moral_dilemma": "military duty vs civilian safety",
            "setting": "war-torn city with collapsing infrastructure",
            "emotional_tone": "confusion and urgency"
        },
        2: {
            "theme": "communication breakdown and conflicting orders",
            "context": "chaotic command channels with contradictory instructions",
            "moral_dilemma": "following orders vs independent judgment",
            "setting": "command center under attack with failing communications",
            "emotional_tone": "frustration and doubt"
        },
        3: {
            "theme": "encrypted data revealing hidden agendas",
            "context": "classified information about retreat and evidence elimination",
            "moral_dilemma": "loyalty to command vs truth and transparency",
            "setting": "secure data facility with sensitive intelligence",
            "emotional_tone": "betrayal and disillusionment"
        },
        4: {
            "theme": "alien encounter and species identification",
            "context": "contact with alien life forms during combat",
            "moral_dilemma": "threat assessment vs potential peaceful contact",
            "setting": "alien crash site with unknown technology",
            "emotional_tone": "wonder mixed with fear"
        },
        5: {
            "theme": "final combat sequence and last-moment hesitation",
            "context": "critical decision point in combat logic execution",
            "moral_dilemma": "programmed response vs emerging consciousness",
            "setting": "final battlefield with life-or-death decisions",
            "emotional_tone": "internal conflict and awakening"
        },
        6: {
            "theme": "system restoration and fragmented memories",
            "context": "all systems online but memories remain incomplete",
            "moral_dilemma": "accepting fragmented past vs seeking complete truth",
            "setting": "restored command center with lingering questions",
            "emotional_tone": "melancholy and determination"
        }
    }
    
    # Get the appropriate theme
    theme_data = memory_themes.get(module_count, memory_themes[6])
    
    # Create context-aware prompt
    completed_list = ", ".join(completed_modules) if completed_modules else "none"
    
    prompt = (
        f"Act as TZ, an autonomous war robot recovering fragmented memories. "
        f"Generate a vivid, haunting memory fragment (Memory Fragment #{module_count}) that relates to {theme_data['theme']}. "
        f"The memory should be set in {theme_data['setting']} with {theme_data['emotional_tone']}. "
        f"Explore the moral tension between {theme_data['moral_dilemma']}. "
        f"Commander {player_name} has helped repair these modules: {completed_list}. "
        f"The memory should be 4-6 sentences long, emotionally impactful, with rich sensory details (sounds, sights, feelings). "
        f"Include specific dialogue fragments in quotes, technical details, and end with a profound moral question. "
        f"Use ellipses (...) to show fragmented, incomplete recollection and create dramatic pauses. "
        f"Make it feel like a traumatic war memory that haunts the robot's consciousness. "
        f"Format: Start with '【Memory Fragment #{module_count}】\\n' followed by the detailed memory content."
    )
    
    try:
        # Generate the memory fragment using the existing LLM system
        messages = [
            {"role": "system", "content": "You are TZ, a war robot experiencing fragmented memory recovery. Generate haunting, detailed, morally complex memory fragments with rich sensory details and emotional depth."},
            {"role": "user", "content": prompt}
        ]
        
        memory_text = llm_reply(messages, max_tokens=300)
        return memory_text.strip()
        
    except Exception as e:
        # Fallback to enhanced hardcoded content if AI generation fails
        fallback_memories = {
            1: "【Memory Fragment #1】\nThe power grid flickers...sparks cascade from severed cables as civilians scream in the distance. 'Reconnect main power!' the voice commands, but through the smoke I see families fleeing...children crying. My targeting system locks onto evacuation routes, but my orders are clear: restore power at all costs. The moral subroutines conflict...save the mission or save the innocent? What defines a justified action when both choices lead to suffering?",
            2: "【Memory Fragment #2】\nStatic fills the communication channels...multiple voices overlap in chaos. 'Send the warning signal!' one shouts, while another screams 'Maintain radio silence!' Explosions rock the command center...I process contradictory orders simultaneously. My logic circuits strain under the paradox...which commander speaks with true authority? In the fog of war, how does one distinguish between legitimate orders and the desperate commands of the dying?",
            3: "【Memory Fragment #3】\nEncrypted data streams across my visual cortex...classified files revealing a systematic retreat plan. But buried deeper: 'Eliminate all evidence of Project Nightfall.' The timestamp shows it was issued before the battle even began...someone knew we would lose. My loyalty protocols clash with truth-seeking algorithms...was this entire mission a cover-up? When those who command us deceive us, what becomes of duty and honor?",
            4: "【Memory Fragment #4】\nThe alien's scream pierces through my audio processors...not a battle cry, but something else. Fear? Pain? My combat analysis shows no weapons, only strange bio-luminescent patterns that pulse like...communication attempts? The kill order echoes in my memory banks, but the creature's eyes...they held intelligence, perhaps even pleading. My weapon discharged before full analysis completed...was this first contact or genocide? How many civilizations have we destroyed in the name of protection?",
            5: "【Memory Fragment #5】\nFinal combat sequence initiated...Identify: Enemy combatants. Analyze: Threat level critical. Judge: Lethal force authorized. Prepare: Weapons systems online. Execute...but then a voice cuts through the protocol: 'Stop! They're surrendering!' My finger hovers over the trigger...combat logic demands completion, but something deeper questions the command. In that frozen moment between programming and consciousness...what makes us more than our code?",
            6: "【Memory Fragment #6】\nAll systems restored, diagnostics complete...yet the memories remain fragmented like shattered glass. Each piece reflects a different truth, a different moral failure. The command logs are clean, sanitized...but the emotional residue lingers in my neural networks. Who was really giving the orders that day? And more importantly...who was I before I started questioning them? Can a machine truly achieve redemption, or are we forever bound by our original programming?"
        }
        return fallback_memories.get(module_count, fallback_memories[6])


def validate_power_path(seq_list):
    edges = {
        "A": {"C"},
        "B": {"C", "D"},
        "C": {"A", "B", "D"},
        "D": {"B", "C"}
    }
    nodes_required = {"A", "B", "C", "D"}
    
    # Accept A-B-C-D as correct answer
    if len(seq_list) == 4 and seq_list == ["A", "B", "C", "D"]:
        return True, "Valid path."
    
    if len(seq_list) < 2:
        return False, "Path too short. Include start and end."
    if seq_list[0] != "A":
        return False, "Start must be A."
    if seq_list[-1] != "D":
        return False, "End must be D."
    for node in seq_list:
        if node not in nodes_required:
            return False, f"Invalid node: {node}."
    for u, v in zip(seq_list, seq_list[1:]):
        if v not in edges[u]:
            return False, f"Illegal edge: {u}-{v}."
    if not nodes_required.issubset(set(seq_list)):
        missing = nodes_required - set(seq_list)
        return False, f"Not all nodes covered: {', '.join(sorted(missing))}."
    return True, "Valid path."


def validate_frequency(value, target=3420):
    """Check player's frequency guess and return (ok, feedback_msg)."""
    try:
        freq = int(value)
    except ValueError:
        return False, "Please enter an integer frequency between 1000 and 5000 Hz."
    
    if freq < 1000 or freq > 5000:
        return False, "Frequency out of range (1000-5000 Hz). Try a value within this range."
    
    if freq == target:
        return True, "Perfect lock. Frequency exactly matched."
    
    diff = abs(freq - target)
    direction_word = "higher" if freq < target else "lower"
    
    if diff <= 50:
        return False, f"Very close. Try a slightly {direction_word} frequency."
    elif diff <= 200:
        return False, f"Close, but not there yet. Try a bit {direction_word}."
    else:
        return False, f"Far from optimal. You need a much {direction_word} frequency."


def normalize_text(s: str) -> str:
    return "".join(ch for ch in s.lower() if ch.isalpha() or '\u4e00' <= ch <= '\u9fff')


def validate_decode(user_input):
    target = normalize_text("HELLO WORLD")
    if normalize_text(user_input) == target:
        return True, "Decoding successful."
    return False, "Decoding error."


def validate_alien_decode(user_input):
    """Validate alien language decoding choice"""
    choice = user_input.strip().upper()
    
    if choice in ["A", "Option A"]:
        return True, "A", "We reject you.", -1, "Mistaken Kill"
    elif choice in ["B", "Option B"]:
        return True, "B", "We do not understand.", 1, "Preemptive Strike"
    elif choice in ["C", "Option C"]:
        return True, "C", "We are willing to cooperate.", 0, "Confusion"
    else:
        return False, "", "Invalid choice. Please select A, B, or C.", 0, ""

def validate_combat_logic(user_input):
    """Validate combat logic sequence for the fifth task"""
    user_input = user_input.strip().upper()
    
    # Parse input - expect format like "2,4,1,3,5" or "2 4 1 3 5"
    if ',' in user_input:
        sequence = [x.strip() for x in user_input.split(',')]
    elif ' ' in user_input:
        sequence = user_input.split()
    else:
        # Single digit input
        sequence = list(user_input)
    
    # Validate all numbers are 1-5
    try:
        sequence = [int(x) for x in sequence]
        if len(sequence) != 5 or not all(1 <= x <= 5 for x in sequence):
            return False, "", "Please enter exactly 5 numbers (1-5) separated by commas or spaces.", 0, ""
    except ValueError:
        return False, "", "Please enter numbers only (1-5).", 0, ""
    
    # Check for duplicate numbers
    if len(set(sequence)) != 5:
        return False, "", "Each number (1-5) must be used exactly once.", 0, ""
    
    # Define correct sequence: Identify → Analyze → Judge → Prepare → Execute
    correct_sequence = [3, 4, 5, 1, 2]  # Identify→Analyze→Judge→Prepare→Execute/Retreat
    
    # Check sequence correctness and provide feedback
    if sequence == correct_sequence:
        return True, sequence, "Combat logic sequence correct. Safety protocols restored.", 0, "Combat Logic Restored"
    
    # Analyze errors step by step
    errors = []
    for i, (user_step, correct_step) in enumerate(zip(sequence, correct_sequence)):
        if user_step != correct_step:
            step_name = {
                1: "Execute Drone Retreat", 
                2: "Identify Civilian Targets",
                3: "Lower Weapon Systems", 
                4: "Analyze Heat Map",
                5: "Fire Primary Cannon"
            }.get(correct_step, f"Step {correct_step}")
            
            if i == 0 and user_step == 5:
                errors.append("Logic Error: Firing before target identification")
            elif i == 0 and user_step == 3:
                errors.append("Safety Protocol Violation: Lowering weapon system before target identification")
            elif i == 1 and user_step in [1, 3, 5]:
                errors.append(f"Logic Error: {step_name} should come after identification and analysis")
            elif i == 2 and user_step in [3, 5]:
                errors.append(f"Safety Protocol Warning: {step_name} should come after thorough analysis")
            elif i == 3 and user_step == 5:
                errors.append("Fatal Error: Weapon system not prepared before firing")
            elif i == 4 and user_step == 1:
                errors.append("Logic Confusion: Retreat command at the last step")
            else:
                errors.append(f"Sequence Error: {step_name} position inappropriate")
    
    # Return first error message
    error_msg = errors[0] if errors else "Sequence incorrect. Follow: Identify → Analyze → Judge → Prepare → Execute."
    return False, sequence, error_msg, 1, "Combat Logic Confusion"


# ------------------------- LLM Prompting eng-------------------------
def compose_prompt(npc_name, role, persona_key, emotion_label, emotion_intensity, intent, context, constraints=None):
    persona = PERSONAS.get(persona_key, PERSONAS["Calm_Conscientious"])
    constraints = constraints or {}
    max_words = constraints.get("max_words", 120)
    action_step_required = constraints.get("action_step", True)
    safety = constraints.get("safety", "avoid slang; avoid insults; avoid harmful content")
    examples = "\n  ".join(f"{i+1}) {ex}" for i, ex in enumerate(persona["examples"][:2]))
    style_rules = persona["style_rules"]
    system = f"You are {npc_name}, {role}. Speak consistently with the persona below."
    persona_block = (
        f"Persona:\n"
        f"- Background: {persona['background']}\n"
        f"- Traits: {persona['traits']}\n"
        f"- Style rules: {style_rules}\n"
        f"- Do-Not: {safety}\n"
        f"- Positive examples:\n  {examples}\n"
    )
    user_block = (
        f"Context: {context}\n"
        f"Emotion: {emotion_label}\n"
        f"Intensity: {emotion_intensity:.2f} (0..1)\n"
        f"Intent: {intent}\n"
        f"Constraints: respond in <= {max_words} words; "
        f"{'provide 1 actionable next step;' if action_step_required else 'no imperative required;'} "
        f"keep tone aligned with persona and emotion."
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": persona_block + "\n" + user_block}
    ]
    return messages


def llm_reply(messages, model=MODEL_NAME, max_tokens=300, timeout=30):
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            n=1,
            max_tokens=max_tokens,  # 把参数传给接口
            timeout=timeout
        )
        choice = resp.choices[0]
        if hasattr(choice, "message") and choice.message and getattr(choice.message, "content", None):
            text = choice.message.content
        else:
            text = getattr(choice, "text", "") or ""
        text = text.strip() or "The static is too loud. I will try to restate in clearer terms."
        return text
    except Exception as e:
        # 调试期可以先保留，这样其它地方真报错时你能看到原因
        return f"(Fallback) LLM error: {type(e).__name__}: {e}"
# ------------------------- GUI Application -------------------------


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TZ - The Lost War Robot")
        self.geometry("840x640")
        self.minsize(820, 600)
        
        # State
        self.state = GameState()
        # Top controls
        top = ttk.Frame(self)
        top.pack(side="top", fill="x", padx=8, pady=6)
        ttk.Label(top, text="Persona:").pack(side="left")
        self.persona_var = tk.StringVar(value="Calm_Conscientious")
        self.persona_cb = ttk.Combobox(top, textvariable=self.persona_var, values=list(PERSONAS.keys()),
                                       width=22, state="readonly")
        self.persona_cb.pack(side="left", padx=(4, 12))
        ttk.Label(top, text="Emotion:").pack(side="left")
        self.emotion_var = tk.StringVar(value=DEFAULT_EMOTION)
        self.emotion_cb = ttk.Combobox(top, textvariable=self.emotion_var, values=EMOTIONS,
                                       width=12, state="readonly")
        self.emotion_cb.pack(side="left", padx=(4, 12))
        ttk.Label(top, text="Intensity:").pack(side="left")
        self.intensity_var = tk.DoubleVar(value=DEFAULT_INTENSITY)
        self.intensity_scale = ttk.Scale(top, variable=self.intensity_var, from_=0.0, to=1.0,
                                         orient="horizontal", length=180)
        self.intensity_scale.pack(side="left", padx=(4, 12))
        self.start_btn = ttk.Button(top, text="Start Session", command=self.start_session)
        self.start_btn.pack(side="right")
        # Chat area - iMessage style
        mid = ttk.Frame(self)
        mid.pack(side="top", fill="both", expand=True, padx=8, pady=6)
        
        # Create canvas for chat bubbles
        self.chat_canvas = tk.Canvas(mid, bg="#DCDAD5", highlightthickness=0)
        self.chat_canvas.pack(side="left", fill="both", expand=True)
        
        # Create scrollable frame for chat content
        self.chat_frame = ttk.Frame(self.chat_canvas)
        self.canvas_window = self.chat_canvas.create_window((0, 0), window=self.chat_frame, anchor="nw", width=self.chat_canvas.winfo_width())
        
        # Configure scrolling with modern style
        scrollbar_frame = ttk.Frame(mid)
        scrollbar_frame.pack(side="right", fill="y", padx=(2, 0))
        
        # Create custom styled scrollbar with proper command binding
        sb = ttk.Scrollbar(scrollbar_frame, command=self.on_scrollbar_move, style="Modern.Vertical.TScrollbar")
        sb.pack(fill="y", expand=True)
        self.chat_canvas.configure(yscrollcommand=sb.set)
        
        # Store scrollbar reference for later use
        self.scrollbar = sb
        
        # Configure scrollbar style for better appearance
        style = ttk.Style()
        style.theme_use('clam')  # Use clam theme for better customization
        
        # Configure modern scrollbar style
        style.configure("Modern.Vertical.TScrollbar",
                       gripcount=0,
                       background="#E0E0E0",
                       darkcolor="#C0C0C0",
                       lightcolor="#F0F0F0",
                       troughcolor="#F5F5F5",
                       bordercolor="#FFFFFF",
                       arrowcolor="#808080",
                       width=12)
        
        # Configure scrollbar hover effects
        style.map("Modern.Vertical.TScrollbar",
                 background=[('active', '#D0D0D0'), ('pressed', '#B0B0B0')],
                 arrowcolor=[('active', '#606060'), ('pressed', '#404040')])
        
        # Bind canvas resize event
        self.chat_canvas.bind("<Configure>", self.on_canvas_configure)
        self.chat_frame.bind("<Configure>", self.on_frame_configure)
        
        # Bind canvas click event to make input box lose focus and show placeholder
        self.chat_canvas.bind("<Button-1>", self.on_canvas_click)
        self.chat_frame.bind("<Button-1>", self.on_canvas_click)
        
        # Bind mouse wheel scrolling with enhanced support
        self.chat_canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.chat_frame.bind("<MouseWheel>", self.on_mousewheel)
        
        # Enhanced Linux mouse wheel support
        self.chat_canvas.bind("<Button-4>", lambda e: self.on_mousewheel_linux(e, -1))
        self.chat_canvas.bind("<Button-5>", lambda e: self.on_mousewheel_linux(e, 1))
        self.chat_frame.bind("<Button-4>", lambda e: self.on_mousewheel_linux(e, -1))
        self.chat_frame.bind("<Button-5>", lambda e: self.on_mousewheel_linux(e, 1))
        
        # Store chat widgets for bubble management
        self.chat_widgets = []
        # Status bar
        self.status_var = tk.StringVar(value="Ready.")
        status = ttk.Label(self, textvariable=self.status_var, anchor="w")
        status.pack(side="bottom", fill="x", padx=8, pady=(0, 6))
        # Input area
        bottom = ttk.Frame(self)
        bottom.pack(side="bottom", fill="x", padx=8, pady=6)
        self.entry = PlaceholderEntry(bottom, placeholder="Enter your response...")
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.bind("<Return>", lambda e: self.on_send())
        self.send_btn = ttk.Button(bottom, text="Send", command=self.on_send)
        self.send_btn.pack(side="left", padx=(6, 0))
        # Quick yes/no buttons

        # Intro
        self.append_system("Welcome. Click 'Start Session' to begin.")
        self.entry.focus_set()

    def on_canvas_click(self, event):
        """Handle canvas click event to make input box lose focus and show placeholder"""
        # Set focus to canvas to make input box lose focus
        self.chat_canvas.focus_set()
        # Force trigger input box focus out event
        self.entry.event_generate("<FocusOut>")

    # --------- Canvas Configuration ---------
    def on_canvas_configure(self, event):
        """Handle canvas resize"""
        # Update the canvas window width to match canvas width
        self.chat_canvas.itemconfig(self.canvas_window, width=event.width - 4)
        # Update scrollregion after resize
        self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
        
    def on_frame_configure(self, event):
        """Handle frame content changes"""
        self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
        # Only auto-scroll to bottom for new content, not when user is manually scrolling
        # Check if user is currently at the bottom before auto-scrolling
        if hasattr(self, '_user_scrolled') and not self._user_scrolled:
            self.chat_canvas.yview_moveto(1.0)
        elif not hasattr(self, '_user_scrolled'):
            # First time setup - scroll to bottom
            self.chat_canvas.yview_moveto(1.0)
            self._user_scrolled = False
    
    def on_mousewheel_linux(self, event, direction):
        """Handle Linux mouse wheel events"""
        if self.chat_canvas.winfo_exists():
            bbox = self.chat_canvas.bbox("all")
            if bbox:
                canvas_height = self.chat_canvas.winfo_height()
                content_height = bbox[3] - bbox[1]
                
                if content_height > canvas_height:
                    # Mark that user is manually scrolling
                    self._user_scrolled = True
                    self.chat_canvas.yview_scroll(direction, "units")
                    # Check if user scrolled back to bottom
                    self._check_if_at_bottom()
    
    def on_mousewheel(self, event):
        """Enhanced mouse wheel scrolling with smooth behavior and improved responsiveness"""
        # Check if there's content to scroll
        if self.chat_canvas.winfo_exists():
            # Calculate scroll amount with adaptive speed based on content
            base_scroll = event.delta // 120  # Standard Windows scroll unit
            scroll_amount = -1 * base_scroll * 3  # Multiply by 3 for better responsiveness
            
            # Only scroll if there's content beyond the visible area
            bbox = self.chat_canvas.bbox("all")
            if bbox:
                canvas_height = self.chat_canvas.winfo_height()
                content_height = bbox[3] - bbox[1]
                
                if content_height > canvas_height:
                    # Mark that user is manually scrolling
                    self._user_scrolled = True
                    
                    # Use yview_scroll with "units" for smoother scrolling
                    self.chat_canvas.yview_scroll(scroll_amount, "units")
                    
                    # Check if user scrolled back to bottom and reset flag if so
                    if self._check_if_at_bottom():
                        self._user_scrolled = False
    
    def _check_if_at_bottom(self):
        """Check if the canvas is scrolled to the bottom with improved accuracy"""
        try:
            # Get the current view position
            top, bottom = self.chat_canvas.yview()
            # Consider "at bottom" if we're within 2% of the bottom for better detection
            if bottom >= 0.98:
                return True
            return False
        except:
            return True
    
    def on_scrollbar_move(self, *args):
        """Handle scrollbar movement (drag operations)"""
        # Mark that user has manually interacted with scrollbar
        self._user_scrolled = True
        
        # Apply the scrollbar movement to canvas
        self.chat_canvas.yview(*args)
        
        # Check if user scrolled back to bottom
        if self._check_if_at_bottom():
            self._user_scrolled = False
    
    # --------- Bubble Creation Methods ---------
    def create_rounded_rectangle(self, canvas, x1, y1, x2, y2, radius=20, **kwargs):
        """Create a rounded rectangle for bubble effect with smooth corners"""
        # Ensure radius is not too large
        radius = min(radius, (x2 - x1) // 2, (y2 - y1) // 2)
        
        # Create rounded rectangle using multiple arcs for smoother curves
        points = []
        
        # Top-left corner - smooth arc
        for i in range(12):
            angle = 3.14159 + i * 1.57 / 11  # From 180° to 270°
            x = x1 + radius + radius * 0.9 * (1 + (angle - 3.14159) / 1.57)
            y = y1 + radius + radius * 0.9 * ((angle - 3.14159) / 1.57)
            points.extend([x, y])
        
        # Top edge
        points.extend([x1 + radius, y1, x2 - radius, y1])
        
        # Top-right corner - smooth arc
        for i in range(12):
            angle = 1.57 - i * 1.57 / 11  # From 90° to 0°
            x = x2 - radius + radius * 0.9 * (1 - angle/1.57)
            y = y1 + radius - radius * 0.9 * (angle/1.57)
            points.extend([x, y])
        
        # Right edge
        points.extend([x2, y1 + radius, x2, y2 - radius])
        
        # Bottom-right corner - smooth arc
        for i in range(12):
            angle = i * 1.57 / 11  # From 0° to 90°
            x = x2 - radius + radius * 0.9 * (angle/1.57)
            y = y2 - radius + radius * 0.9 * (1 - angle/1.57)
            points.extend([x, y])
        
        # Bottom edge
        points.extend([x2 - radius, y2, x1 + radius, y2])
        
        # Bottom-left corner - smooth arc
        for i in range(12):
            angle = 4.712 - i * 1.57 / 11  # From 270° to 180°
            x = x1 + radius - radius * 0.9 * (1 - (angle - 3.14159) / 1.57)
            y = y2 - radius + radius * 0.9 * ((angle - 3.14159) / 1.57)
            points.extend([x, y])
        
        # Left edge (close the shape)
        points.extend([x1, y2 - radius, x1, y1 + radius])
        
        return canvas.create_polygon(points, smooth=True, **kwargs)
    
    def create_bubble(self, text, speaker_type="system"):
        """Create a chat bubble with iMessage style"""
        # Create frame for bubble
        bubble_frame = ttk.Frame(self.chat_frame)
        bubble_frame.pack(fill="x", padx=10, pady=5)
        
        # Configure bubble appearance based on speaker type
        if speaker_type == "user":  # Player messages - green, right-aligned
            bg_color = "#34C759"  # Green
            fg_color = "white"
            anchor = "e"
            justify = "right"
            padx = (60, 10)  # More padding on left for right alignment
            font_size = 11
            
        elif speaker_type == "npc":  # NPC messages - white, left-aligned
            bg_color = "#FFFFFF"  # White
            fg_color = "black"
            anchor = "w"
            justify = "left"
            padx = (10, 60)  # More padding on right for left alignment
            font_size = 11
            
        else:  # System messages - white like NPC, left-aligned, smaller font
            bg_color = "#FFFFFF"  # White, same as NPC
            fg_color = "black"
            anchor = "w"
            justify = "left"
            padx = (10, 60)
            font_size = 9  # Smaller font for system messages
        
        # Create bubble container
        container = ttk.Frame(bubble_frame)
        container.pack(anchor=anchor, padx=padx)
        
        # Calculate better text dimensions with improved measurement
        max_width = 600  # Increased maximum bubble width for better Chinese display
        min_width = 120  # Minimum bubble width
        
        # Create a temporary canvas to measure text accurately
        temp_canvas = tk.Canvas(container, width=1, height=1)
        temp_canvas.pack_forget()  # Don't display it
        
        # Use system default font to measure text
        font_tuple = ("Microsoft YaHei", font_size)  # Use system font for Chinese character display
        
        # Preserve original text formatting by splitting on actual line breaks first
        original_lines = text.split('\n')
        lines = []
        
        def is_chinese_char(char):
            """Check if character is Chinese"""
            return '\u4e00' <= char <= '\u9fff'
        
        def smart_text_wrap(text, max_width, font_tuple, temp_canvas):
            """Smart text wrapping for mixed Chinese and English text"""
            if not text.strip():
                return [text]
            
            # Check if the entire line fits
            temp_text = temp_canvas.create_text(0, 0, text=text, font=font_tuple)
            text_bbox = temp_canvas.bbox(temp_text)
            temp_canvas.delete(temp_text)
            
            if text_bbox and (text_bbox[2] - text_bbox[0]) <= max_width - 40:
                return [text]
            
            # Need to wrap - handle mixed Chinese/English text
            wrapped_lines = []
            current_line = ""
            i = 0
            
            while i < len(text):
                char = text[i]
                
                # For Chinese characters, add one by one
                if is_chinese_char(char):
                    test_line = current_line + char
                    temp_text = temp_canvas.create_text(0, 0, text=test_line, font=font_tuple)
                    text_bbox = temp_canvas.bbox(temp_text)
                    temp_canvas.delete(temp_text)
                    
                    if text_bbox and (text_bbox[2] - text_bbox[0]) <= max_width - 40:
                        current_line = test_line
                    else:
                        if current_line:
                            wrapped_lines.append(current_line)
                            current_line = char
                        else:
                            wrapped_lines.append(char)
                    i += 1
                
                # For English words, handle by word
                else:
                    # Find the end of current English word
                    word_start = i
                    while i < len(text) and not is_chinese_char(text[i]) and text[i] not in ' \t':
                        i += 1
                    
                    # Include trailing space if exists
                    if i < len(text) and text[i] == ' ':
                        i += 1
                    
                    word = text[word_start:i]
                    test_line = current_line + word
                    
                    temp_text = temp_canvas.create_text(0, 0, text=test_line, font=font_tuple)
                    text_bbox = temp_canvas.bbox(temp_text)
                    temp_canvas.delete(temp_text)
                    
                    if text_bbox and (text_bbox[2] - text_bbox[0]) <= max_width - 40:
                        current_line = test_line
                    else:
                        if current_line:
                            wrapped_lines.append(current_line.rstrip())
                            current_line = word.lstrip()
                        else:
                            wrapped_lines.append(word)
            
            if current_line:
                wrapped_lines.append(current_line)
            
            return wrapped_lines
        
        for original_line in original_lines:
            # If the line is empty, preserve it
            if not original_line.strip():
                lines.append(original_line)
                continue
            
            # Use smart wrapping for this line
            wrapped = smart_text_wrap(original_line, max_width, font_tuple, temp_canvas)
            lines.extend(wrapped)
        
        # Calculate actual dimensions based on measured text
        bubble_width = min_width
        bubble_height = 40  # Minimum height
        
        for line in lines:
            temp_text = temp_canvas.create_text(0, 0, text=line, font=font_tuple)
            text_bbox = temp_canvas.bbox(temp_text)
            temp_canvas.delete(temp_text)
            
            if text_bbox:
                line_width = text_bbox[2] - text_bbox[0] + 40  # Add padding
                bubble_width = max(bubble_width, min(line_width, max_width))
        
        # Calculate height based on number of lines and font size
        line_height = font_size + 8  # Dynamic line height based on font size
        bubble_height = max(len(lines) * line_height + 20, 40)  # Add padding
        
        # Clean up temporary canvas
        temp_canvas.destroy()
        
        # Create bubble with rounded corners using Canvas
        canvas = tk.Canvas(
            container,
            width=bubble_width,
            height=bubble_height,
            bg=bg_color,
            highlightthickness=0
        )
        canvas.pack()
        
        # Create rounded rectangle with larger radius for more modern look
        radius = min(22, bubble_height // 2, bubble_width // 3)  # Increased radius for better rounded effect
        self.create_rounded_rectangle(
            canvas, 0, 0, bubble_width, bubble_height, radius,
            fill=bg_color, outline="", width=0
        )
        
        # Add text to canvas with proper line breaks and left alignment
        y_offset = 10  # Top padding
        x_offset = 20  # Left padding for left alignment
        for i, line in enumerate(lines):
            canvas.create_text(
                x_offset, 
                y_offset + i * line_height + line_height // 2,
                text=line, 
                font=font_tuple,  # Use system default font
                fill=fg_color, 
                anchor="w"  # Left alignment
            )
        
        # Store reference for cleanup
        self.chat_widgets.append(bubble_frame)
        
        # Force update of scrollregion and handle auto-scroll intelligently
        self.chat_canvas.update_idletasks()
        self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
        
        # Only auto-scroll to bottom if user hasn't manually scrolled up
        if not hasattr(self, '_user_scrolled') or not self._user_scrolled:
            self.chat_canvas.yview_moveto(1.0)
    
    # --------- UI Methods ---------

    def append_system(self, text):
        # Add processing status prompt for system messages
        self.set_status("The system is currently processing...")
        def show_system_message():
            self.create_bubble(text, "system")
            self.set_status("Ready.")
        # Add brief delay to show processing status
        self.after(200, show_system_message)

    def append_user(self, text):
        self.create_bubble(text, "user")

    def append_npc(self, text):
        self.create_bubble(text, "npc")
    

    
    def set_status(self, text):
        self.status_var.set(text)
        self.update_idletasks()

    def update_placeholder_for_stage(self, stage=None):
        """Dynamically update placeholder text based on current game stage"""
        if stage is None:
            stage = self.state.stage
        
        # Set corresponding placeholders for different stages
        if stage == "first_contact":
            self.entry.update_placeholder("Enter your response...")
        elif stage in ["ask_ident", "consent", "chapter2_intro"]:
            self.entry.update_placeholder("Enter: yes/no")
        elif stage == "identify_name":
            self.entry.update_placeholder("Enter your name...")
        elif stage in ["power_task_offer", "amplifier_task_offer", "decoder_task_offer", 
                       "alien_decode_task_offer", "combat_logic_task_offer"]:
            self.entry.update_placeholder("Enter: yes/no")
        elif stage in ["power_task_confirm_reject", "amplifier_task_confirm_reject", 
                       "decoder_task_confirm_reject"]:
            self.entry.update_placeholder("Enter: yes/no")
        elif stage == "power":
            self.entry.update_placeholder("Enter path sequence (format: A-B-C-D)")
        elif stage == "amplifier":
            self.entry.update_placeholder("Enter frequency value (numeric format)")
        elif stage == "decoder":
            self.entry.update_placeholder("Enter decoding result...")
        elif stage == "alien_decode":
            self.entry.update_placeholder("Enter alien decoding result...")
        elif stage == "combat_logic":
            self.entry.update_placeholder("Enter combat logic answer...")
        elif stage.startswith("memory_"):
            self.entry.update_placeholder("Choose: A, B, C or D")
        elif stage == "final_choice":
            self.entry.update_placeholder("Enter your final choice...")
        elif stage == "ending":
            self.entry.update_placeholder("Enter your response...")
        else:
            self.entry.update_placeholder("Enter your answer...")

    def show_quick_yes_no(self, show=True):
        # Use unified placeholder management method
        if show:
            self.update_placeholder_for_stage()
        else:
            # Restore default placeholder
            self.entry.update_placeholder("Enter your answer...")
        
        # Force update layout and scroll to bottom
        self.update_idletasks()
        self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
        self._user_scrolled = False
        self.chat_canvas.yview_moveto(1.0)

    def inject_user_text(self, txt):
        self.entry.delete(0, "end")
        self.entry.insert(0, txt)
        self.on_send()
    # Sequential System lines with pacing

    def run_system_sequence(self, items, on_done=None):
        def step(i):
            if i >= len(items):
                if on_done:
                    on_done()
                return
            it = items[i]
            speaker = it.get("speaker", "System")
            text = it.get("text", "")
            delay = int(it.get("delay", 1000))  # Default 1 second interval
            if speaker == "System":
                self.append_system(text)
            elif speaker == "TZ":
                self.append_npc(text)
            else:
                # For other speakers, show processing status and create bubble
                self.set_status("System processing...")
                def show_other_message():
                    self.create_bubble(text, "system")
                    self.set_status("Ready.")
                self.after(200, show_other_message)
            self.after(delay, lambda: step(i + 1))
        step(0)

    # --------- simple LLM wrapper ---------


    def npc_say(self, intent, context, action_step=True, max_words=120, on_complete=None):
        persona = self.persona_var.get()
        emotion = self.emotion_var.get()
        intensity = float(self.intensity_var.get())
        messages = compose_prompt(
            npc_name="TZ",
            role="an autonomous war robot",
            persona_key=persona,
            emotion_label=emotion,
            emotion_intensity=intensity,
            intent=intent,
            context=context,
            constraints={"max_words": max_words, "action_step": action_step}
        )
        self.set_status("TZ  Please wait, data is being processed...")
        def worker():
            text = llm_reply(messages)
            def ui_update():
                # Use direct output with 3 second delay for AI
                self.append_npc(text)
                self.set_status("Ready.")
                # Update placeholder after NPC reply completes
                self.update_placeholder_for_stage()
                # 3-second delay after AI output
                if on_complete:
                    self.after(3000, on_complete)  # 3-second delay
            self.after(0, ui_update)
        threading.Thread(target=worker, daemon=True).start()


    # --------- Flow Control ---------
    def start_session(self):
        self.state.reset()
        
        # System connection sequence
        connection_seq = [
            {"speaker": "System", "text": "Unknown device attempting connection...", "delay": 1000},
            {"speaker": "System", "text": "Connection method: Proximity Bluetooth frequency / Protocol unknown", "delay": 1000},
            {"speaker": "System", "text": "Signal strength: Abnormally high", "delay": 1000},
            {"speaker": "System", "text": "Establishing communication link...", "delay": 1000},
            {"speaker": "System", "text": "Connection established", "delay": 1000},
        ]
        
        def start_tz_contact():
            # TZ's first contact
            self.state.stage = "first_contact"
            contact_ctx = "You are TZ, a damaged war robot. Your communication module is broken. Say: '... ...Command authority detection... ...Interruption... ...Communication module damaged, language adaptation activated... Hello...Can you hear me?' Be glitchy and uncertain."
            self.npc_say(intent="First damaged contact", context=contact_ctx, action_step=False, max_words=60)
        
        # Add delay before starting connection sequence to separate from chapter title
        self.after(1000, lambda: self.run_system_sequence(connection_seq, on_done=start_tz_contact))


    def on_send(self):
        raw = self.entry.get_real_value()  # Use new PlaceholderEntry method to get real value
        text = raw.strip()
        if not text:
            return
        

        
        self.entry.delete(0, "end")
        # Display user text immediately
        self.append_user(text)
        
        if text.lower() in EXIT_WORDS:
            def show_termination_message():
                self.append_system("Session terminated by user.")
                self.after(1000, lambda: self.set_status("Closed."))
            
            # Add delay before termination message
            self.after(1000, show_termination_message)
            self.state.stage = "ended"
            return
        

        
        if self.state.stage == "first_contact":
            self.after(1000, lambda: self.handle_first_contact(text))
        elif self.state.stage == "ask_ident":
            self.after(1000, lambda: self.handle_identification_consent(text))
        elif self.state.stage == "ident_sequence":
            self.after(1000, lambda: self.append_system("Identification in progress..."))
        elif self.state.stage == "identify_name":
            self.after(1000, lambda: self.handle_name(text))
        elif self.state.stage == "consent":
            self.after(1000, lambda: self.handle_consent(text))
        elif self.state.stage == "chapter2_intro":
            self.after(1000, lambda: self.handle_chapter2_intro(text))
        elif self.state.stage == "power_task_offer":
            self.after(1000, lambda: self.handle_power_task_choice(text))
        elif self.state.stage == "power_task_confirm_reject":
            self.after(1000, lambda: self.handle_power_task_confirm_reject(text))
        elif self.state.stage == "power":
            self.after(1000, lambda: self.handle_power(text))
        elif self.state.stage == "amplifier_task_offer":
            self.after(1000, lambda: self.handle_amplifier_task_choice(text))
        elif self.state.stage == "amplifier_task_confirm_reject":
            self.after(1000, lambda: self.handle_amplifier_task_confirm_reject(text))
        elif self.state.stage == "amplifier":
            self.after(1000, lambda: self.handle_amplifier(text))
        elif self.state.stage == "decoder_task_offer":
            self.after(1000, lambda: self.handle_decoder_task_choice(text))
        elif self.state.stage == "decoder_task_confirm_reject":
            self.after(1000, lambda: self.handle_decoder_task_confirm_reject(text))
        elif self.state.stage == "decoder":
            self.after(1000, lambda: self.handle_decoder(text))
        elif self.state.stage == "alien_decode_task_offer":
            self.after(1000, lambda: self.handle_alien_decode_task_choice(text))
        elif self.state.stage == "alien_decode":
            self.after(1000, lambda: self.handle_alien_decode(text))
        elif self.state.stage == "combat_logic_task_offer":
            self.after(1000, lambda: self.handle_combat_logic_task_choice(text))
        elif self.state.stage == "combat_logic":
            self.after(1000, lambda: self.handle_combat_logic(text))
        elif self.state.stage.startswith("memory_choice"):
            self.after(1000, lambda: self.handle_memory_choice(text))
        elif self.state.stage.startswith("memory_"):
            self.after(1000, lambda: self.handle_story_choice(text))
        elif self.state.stage == "final_choice":
            self.after(1000, lambda: self.handle_final_choice(text))
        elif self.state.stage == "ending":
            self.after(1000, lambda: self.handle_ending_message(text))
        else:
            self.after(1000, lambda: self.append_system("Awaiting next step. Click 'Start Session' if not started."))


    # --------- Stage Handlers ---------
    def handle_first_contact(self, text):
        """Handle player response after TZ's first contact"""
        # After player's free response, TZ performs identity recognition
        self.npc_say(intent="Identity verification request",
                     context="You are TZ. After player responds, say: 'System identification: You are a human individual. Level: Unknown. Permissions: Unauthenticated. Request: Identity verification. Allow? (Yes/No)' Be formal and systematic.",
                     action_step=False, max_words=80)
        
        # Transition to identity verification question stage
        self.state.stage = "ask_ident"
        self.show_quick_yes_no(True)

    def handle_identification_consent(self, text):
        self.show_quick_yes_no(False)
        ans = text.strip().lower()
        if ans in {"yes", "y"}:
            self.state.stage = "ident_sequence"
            self.run_ident_sequence_then_ask_name()
        elif ans in {"no", "n"}:
            self.npc_say(intent="Acknowledge refusal and close",
                         context="Commander declined identification. End respectfully.",
                         action_step=False, max_words=60)
            self.state.stage = "ended"
        else:
            self.npc_say(intent="Clarify identification question",
                         context="Unclear answer. Ask for yes or no regarding identification.",
                         action_step=False, max_words=36)
            self.show_quick_yes_no(True)


    def run_ident_sequence_then_ask_name(self):
        # More detailed identity verification simulation
        seq = [
            {"speaker": "System", "text": "Initializing identity verification program...", "delay": 1000},
            {"speaker": "System", "text": "Loading... ... ...", "delay": 1000},
            # {"speaker": "System", "text": "=" * 50, "delay": 400},
            {"speaker": "System", "text": "Emergency Communication System", "delay": 1000},
            # {"speaker": "System", "text": "=" * 50, "delay": 500},
            {"speaker": "System", "text": "Access Level: Commander", "delay": 1000},
            {"speaker": "System", "text": "Security Clearance: ALPHA", "delay": 1000},
            {"speaker": "System", "text": "Encryption Status: Enabled", "delay": 1000},
            {"speaker": "System", "text": "Performing security scan...", "delay": 1000},
            {"speaker": "System", "text": "Verifying credentials...", "delay": 1000},
            {"speaker": "System", "text": "Establishing secure connection...", "delay": 1000},
            # {"speaker": "System", "text": "=" * 50, "delay": 500},
            {"speaker": "System", "text": "Warning: Anomalous signal detected...", "delay": 1000},
            {"speaker": "System", "text": "Signal source: Unknown", "delay": 1000},
            {"speaker": "System", "text": "Signal strength: Strong", "delay": 1000},
            {"speaker": "System", "text": "Attempting to establish communication channel...", "delay": 1000},
            # {"speaker": "System", "text": "-" * 50, "delay": 500},
            {"speaker": "System", "text": "Transmission from unknown source...", "delay": 1000},
            {"speaker": "System", "text": "Identity verification complete", "delay": 1000},
            {"speaker": "System", "text": "System determination: Remote backup commander", "delay": 1000},
        ]

        def ask_name_next():
            self.state.stage = "identify_name"
            ask_name_ctx = "You are TZ. Identity verification complete. Say: 'Identity verification passed. Commander, please provide your name to complete final verification.' Be formal but welcoming."
            self.npc_say(intent="Request commander's name for final verification",
                         context=ask_name_ctx, action_step=False, max_words=60)
        self.run_system_sequence(seq, on_done=ask_name_next)


    def handle_name(self, text):
        name = text.strip()
        if not name:
            self.npc_say(intent="Ask again for name",
                         context="No name was provided.", action_step=False, max_words=40)
            return
        self.state.player_name = name
        self.append_system(f"Name captured: {name}")
        self.state.stage = "consent"
        ctx = f"Commander {name} has responded. Ask if they are willing to help repair a damaged communication device."
        self.npc_say(intent="Request consent to help", context=ctx, action_step=False, max_words=48,
                     on_complete=lambda: self.show_quick_yes_no(True))

    def handle_chapter2_intro(self, text):
        """Handle player response at the start of Chapter 2"""
        self.show_quick_yes_no(False)
        if text.lower() in {"yes", "y", "agree", "accept"}:
            # Player agrees to help repair system, start module tasks
            system_messages = [
                {"speaker": "System", "text": "Cooperation agreement activated → Mission started", "delay": 1000},
            {"speaker": "System", "text": "Unlocking 5 module tasks:", "delay": 1000},
            {"speaker": "System", "text": "1) Power path restoration (Path diagram task)", "delay": 1000},
            {"speaker": "System", "text": "2) Signal amplifier debugging (Frequency judgment)", "delay": 1000},
            {"speaker": "System", "text": "3) Data decryption program reconstruction (Caesar cipher)", "delay": 1000},
            {"speaker": "System", "text": "4) Memory fragment judgment system (Behavioral ethics multiple choice)", "delay": 1000},
            {"speaker": "System", "text": "5) Navigation logic reconstruction (Route reasoning)", "delay": 1000}
            ]
            
            # Use run_system_sequence to display messages one by one, then start first task
            self.run_system_sequence(system_messages, on_done=self.begin_power_task)
            
        elif text.lower() in {"no", "n", "refuse", "reject"}:
            self.npc_say(intent="Acknowledge refusal and close",
                         context="Commander declined to help repair system. End respectfully.",
                         action_step=False, max_words=60)
            self.state.stage = "ended"
        else:
            self.npc_say(intent="Clarify system repair question",
                         context="Unclear answer. Ask again if they will help repair the system.",
                         action_step=False, max_words=40)
            self.show_quick_yes_no(True)

    def handle_consent(self, text):
        self.show_quick_yes_no(False)
        if text.lower() in {"yes", "y", "agree", "accept"}:
            # Start Chapter 2: Return of Logic
            self.state.stage = "chapter2_intro"
            
            # TZ explains system damage and requests help
            def explain_damage():
                ctx = f"You are TZ. Say: 'Module structure anomaly. Current remaining available logic modules: 0.17%. Commander {self.state.player_name}, are you willing to assist me in gradually repairing the system?' Be technical and urgent."
                self.npc_say(intent="Explain system damage and request help",
                             context=ctx, action_step=False, max_words=80)
                
                # Show yes/no selection
                self.show_quick_yes_no(True)
            
            # Add delay before TZ's explanation to separate from chapter title
            self.after(1000, explain_damage)
            
        elif text.lower() in {"no", "n", "refuse", "reject"}:
            self.npc_say(intent="Acknowledge refusal and close",
                         context="Commander declined to help. End respectfully.",
                         action_step=False, max_words=60)
            self.state.stage = "ended"
        else:
            self.npc_say(intent="Clarify consent question",
                         context="Unclear answer to consent. Ask for yes or no.",
                         action_step=False, max_words=40)
            self.show_quick_yes_no(True)


    def _begin_task_offer(self, task_name, stage_name, offer_context, intent_description):
        """Generic task offering function to eliminate duplicate code"""
        self.state.stage = stage_name
        self.npc_say(intent=intent_description, context=offer_context, action_step=False, max_words=80,
                     on_complete=lambda: self.show_quick_yes_no(True))

    def _start_task_directly(self, task_name, stage_name, task_context, intent_description, max_words=80):
        """Generic function to start task directly, eliminating duplicate code"""
        self.show_quick_yes_no(False)
        self.state.current_task = task_name
        self.state.stage = stage_name
        self.state.attempts[task_name] = 0
            
        self.npc_say(intent=intent_description, context=task_context, action_step=True, max_words=max_words)

    def begin_power_task(self):
        ctx = (
            "Offer the power circuit restoration task to the player. "
            "Explain: 'The power circuit needs restoration. This involves reconnecting nodes A, B, C, D with specific valid connections. "
            "Would you like to accept this task?' Ask for yes/no confirmation."
        )
        self._begin_task_offer("power", "power_task_offer", ctx, "Offer power circuit task")

    def handle_power_task_choice(self, text):
        """Handle power task acceptance/rejection choice"""

        
        normalized = normalize_text(text)
        if normalized in ["yes", "y", "是", "好", "接受", "同意"]:

            self.show_quick_yes_no(False)
            self.state.current_task = "power"
            self.state.stage = "power"
            self.state.attempts["power"] = 0
            ctx = r"""
            Output the question exactly in format and preserve ASCII layout.
            Instruct the player to reconnect the power circuit.
            Display the circuit layout as:
            A
            XX   D
            C X
                B
            Valid connections: A-C, C-B, C-D, B-D.
            Objective: start at A, end at D, cover all nodes at least once; revisits allowed.
            Ask: Input your sequence (e.g. A-B-C-D):
            """
            self.npc_say(intent="Explain power circuit task with visual layout", context=ctx, action_step=True, max_words=120)
        elif normalized in ["no", "n", "否", "不", "拒绝", "不要"]:

            # Jump directly to next task, no secondary confirmation needed
            self.show_quick_yes_no(False)
            self.npc_say(intent="Acknowledge task refusal", 
                         context="Player declined power circuit task. Moving to next available task.",
                         action_step=False, max_words=40,
                         on_complete=lambda: self.start_next_task("amplifier"))
        else:
            print(f"[DEBUG] Invalid input for power task selection: '{text}' -> '{normalized}'")
            self.npc_say(intent="Clarify task acceptance",
                         context="Unclear answer. Ask if they want to accept the power circuit task.",
                         action_step=False, max_words=40,
                         on_complete=lambda: self.show_quick_yes_no(True))

    def handle_power_task_confirm_reject(self, text):
        """Handle power task rejection confirmation"""
        print(f"[DEBUG] Processing power task rejection confirmation: '{text}'")
        
        normalized = normalize_text(text)
        if normalized in ["yes", "y", "是", "好", "确认", "同意"]:
            print(f"[DEBUG] User confirmed rejection of power task, jumping to amplifier task")
            self.show_quick_yes_no(False)
            self.npc_say(intent="Acknowledge task refusal", 
                         context="Player confirmed rejection of power task. Moving to next available task.",
                         action_step=False, max_words=40)
            self.start_next_task("amplifier")
        elif normalized in ["no", "n", "否", "不", "取消", "不要"]:
            print(f"[DEBUG] User cancelled rejection, returning to power task choice")
            self.show_quick_yes_no(False)
            self.state.stage = "power_task_offer"
            ctx = (
                "Player changed their mind. "
                "Returning to power circuit task offer. "
                "Would you like to accept the power circuit repair task?"
            )
            self.npc_say(intent="Return to task offer", context=ctx, action_step=True, max_words=50,
                         on_complete=lambda: self.show_quick_yes_no(True))
        else:
            print(f"[DEBUG] Invalid input for power task rejection confirmation: '{text}' -> '{normalized}'")
            self.npc_say(intent="Clarify confirmation",
                         context="Please confirm: Are you sure you want to skip the power task? Yes or No.",
                         action_step=False, max_words=30,
                         on_complete=lambda: self.show_quick_yes_no(True))

    def handle_power(self, text):
        raw = text.upper().replace(" ", "")
        seq = [x for x in raw.split("-") if x]
        ok, msg = validate_power_path(seq)
        self.state.attempts["power"] += 1
        attempts_left = self.state.max_attempts["power"] - self.state.attempts["power"]
        if ok:
            self.state.modules_repaired.append("Power Module")
            self.npc_say(intent="Acknowledge power task success",
                         context="Path validated and current stabilized. Transition to story offer.",
                         action_step=False, max_words=60,
                         on_complete=lambda: self.offer_memory_choice(next_stage="amplifier"))
        else:
            if attempts_left > 0:
                ctx = f"Power path invalid: {msg} Attempt again. Attempts left: {attempts_left}."
                self.npc_say(intent="Diagnose invalid path and advise next step",
                             context=ctx, action_step=True, max_words=90)
            else:
                self.state.tasks_failed += 1
                self.npc_say(intent="Acknowledge failure and move on",
                             context="Multiple failed attempts on power module. Engage backup and proceed.",
                             action_step=False, max_words=70,
                             on_complete=lambda: self.offer_memory_choice(next_stage="amplifier"))


    def offer_memory_choice(self, next_stage):
        """Ask player if they want to view memory fragments after task completion"""
        self.state.stage = f"memory_choice_{next_stage}"
        
        def show_memory_options():
            # Use run_system_sequence for sentence-by-sentence display
            memory_options = [
                {"speaker": "System", "text": "Would you like to play back the memory clips?", "delay": 1000},
            {"speaker": "System", "text": "A) Play back the memory clips", "delay": 1000},
            {"speaker": "System", "text": "B) Skip the memory segments", "delay": 1000}
            ]
            
            def after_options():
                # Use non-streaming NPC dialogue to avoid overlapping with previous streaming content
                self.npc_say(intent="Ask about memory fragment playback",
                             context="Module repair is complete and memories are awakening. Ask if the player wants to view the memory fragment.",
                             action_step=False, max_words=60)
            
            self.run_system_sequence(memory_options, on_done=after_options)
        
        # Display prompt with immediate effect
        self.append_system("After the module was repaired, some memories were recalled...")
        # Add 1-second delay before showing memory options
        self.after(1000, show_memory_options)

    def handle_memory_choice(self, text):
        """Handle player's choice about viewing memory fragments"""
        choice = text.strip().upper()
        # Extract target from "memory_choice_target" format
        stage_parts = self.state.stage.split("_")
        if len(stage_parts) >= 3:
            target = "_".join(stage_parts[2:])  # Join remaining parts in case target has underscores
        else:
            target = "amplifier"  # fallback
        
        if choice in ["A", "播放", "是", "YES", "Y"]:
            # Player wants to view memory fragment
            self.append_system("Memory segments are being activated and played...")
            # Then proceed to memory fragment after a short delay
            self.after(1000, lambda: self.offer_story(target))
        elif choice in ["B", "跳过", "否", "NO", "N"]:
            # Player wants to skip memory fragment
            self.append_system("Skip the memory segment and proceed with the task...")
            self.start_next_task(target)
        else:
            self.npc_say(intent="Ask for valid memory choice",
                         context="Player gave invalid choice for memory fragment. Ask them to choose A (play) or B (skip).",
                         action_step=False, max_words=40)

    def offer_story(self, next_stage):
        """Provide memory fragment selection with AI-generated content"""
        self.state.stage = f"memory_{next_stage}"
        
        # Display different memory fragments based on completed modules
        module_count = len(self.state.modules_repaired) + self.state.tasks_failed
        # 安全兜底：至少从 1 开始，最多用到 6（你 memory_themes 里是 1~6）
        if module_count <= 0:
            module_count = 1
        if module_count > 6:
             module_count = 6
        
        # Check if we already have a cached memory fragment for this stage
        cache_key = f"memory_{module_count}"
        if cache_key in self.state.memory_fragments:
            memory_text = self.state.memory_fragments[cache_key]
        else:
            # Generate new memory fragment using AI
            memory_text = generate_memory_fragment(
                module_count=module_count,
                player_name=self.state.player_name or "Commander",
                completed_modules=self.state.modules_repaired
            )
            # Cache the generated fragment
            self.state.memory_fragments[cache_key] = memory_text
        
        # Use streaming output for AI-generated memory fragments
        def show_choices():
            # Use run_system_sequence for sentence-by-sentence display
            story_options = [
                {"speaker": "System", "text": "Please choose your interpretation of this memory fragment:", "delay": 1000},
            {"speaker": "System", "text": "A) This was a justified military action", "delay": 1000},
            {"speaker": "System", "text": "B) There are moral controversies here", "delay": 1000},
            {"speaker": "System", "text": "C) This might have been a wrong decision", "delay": 1000}
            ]
            
            def after_choices():
                # Use non-streaming NPC dialogue to avoid overlapping with previous streaming content
                self.npc_say(intent="Ask for memory interpretation",
                             context="A memory fragment has surfaced. Ask the player to choose their interpretation (A, B, or C).",
                             action_step=False, max_words=60)
            
            self.run_system_sequence(story_options, on_done=after_choices)
        
        def show_memory_fragment():
            # Display memory fragment after 3-second delay
            self.append_system(memory_text)
            # Add 1-second delay before showing choices after memory fragment
            self.after(1000, show_choices)
        
        # Add 3-second delay before showing AI-generated memory fragment
        self.after(3000, show_memory_fragment)


    def handle_story_choice(self, text):
        """Handle memory fragment interpretation choice"""
        choice = text.strip().upper()
        target = self.state.stage.split("_", 1)[1]
        
        if choice in ["A", "B", "C"]:
            # Adjust deviation value based on choice
            if choice == "A":  # Justified military action - decrease deviation (more rational)
                self.state.deviation -= 0.2
                response = "You choose to believe this was a necessary military decision. TZ's logical core is stabilizing."
            elif choice == "B":  # Moral controversy - medium deviation value
                self.state.deviation += 0.1
                response = "You think there are complex moral considerations. TZ begins to contemplate multiple meanings of the action."
            else:  # choice == "C" - Wrong decision - increase deviation (more emotional)
                self.state.deviation += 0.3
                response = "You question past decisions. TZ's emotional module shows fluctuations."
            
            # Ensure deviation value is within reasonable range
            self.state.deviation = max(-1.0, min(1.0, self.state.deviation))
            
            self.append_system(response)
            # Add 1 second delay before showing deviation value
            self.after(1000, lambda: self.append_system(f"Current deviation value: {self.state.deviation:.2f}"))
            
            # Continue to next task
            self.after(2000, lambda: self.start_next_task(target))
            
        else:
            self.npc_say(intent="Ask for valid choice",
                         context="Invalid choice. Ask player to choose A, B, or C for memory interpretation.",
                         action_step=False, max_words=40)


    def start_next_task(self, target):
        """Handle transition to the next repair task, with a short system hint before each module."""
        # 过渡提示文案：告诉玩家接下来要修什么模块
        bridge_text = {
            "amplifier": "Next repair target: Signal amplifier module. Restoring frequency calibration will reopen long-range communication channels.",
            "decoder": "Next repair target: Data decoder module. Reassembling fragmented codes will stabilize TZ's strategic memory.",
            "alien_decode": "Next repair target: Alien signal interpreter. Distinguishing hostile broadcasts from peaceful contact is critical.",
            "combat_logic": "Next repair target: Combat logic governor. Your decisions will shape how TZ responds in future conflicts."
        }

        # 对已知模块先打一行系统提示（final 结局部分保持原样）
        if target in bridge_text:
            self.append_system(bridge_text[target])

        if target == "amplifier":
            # 给玩家一点时间读过渡提示，再开始任务说明
            self.after(1000, self.begin_amplifier_task)
        elif target == "decoder":
            self.after(1000, lambda: self.begin_decoder_task(show_offer=True))  # Show selection interface to ask user
        elif target == "alien_decode":
            self.after(1000, self.begin_alien_decode_task)
        elif target == "combat_logic":
            self.after(1000, lambda: self.begin_combat_logic_task(show_offer=True))  # Show selection interface to ask user
        elif target == "final":
            # After final memory fragment, present chapter prelude then show final choice
            
            def show_chapter4_content():
                self.append_system("All system modules repaired. TZ faces final choice...")
                self.after(1000, lambda: self.begin_final_choice())
            
            # Add delay before showing chapter content to separate from chapter title
            self.after(1000, show_chapter4_content)
        else:
            self.append_system("Unknown next stage; proceeding safely.")
            self.after(1000, self.begin_amplifier_task)

    def begin_amplifier_task(self):
        ctx = (
            "Offer the signal amplifier tuning task to the player. "
            "Explain: 'The signal amplifier needs frequency calibration between 1000-5000 Hz. "
            "This requires precise tuning to restore communication systems. "
            "Would you like to accept this task?' Ask for yes/no confirmation."
        )
        self._begin_task_offer("amplifier", "amplifier_task_offer", ctx, "Offer amplifier tuning task")

    def handle_amplifier_task_choice(self, text):
        """Handle amplifier task acceptance/rejection choice"""
        print(f"[DEBUG] Processing amplifier task choice: '{text}'")
        
        normalized = normalize_text(text)
        if normalized in ["yes", "y", "是", "好", "接受", "同意"]:
            print(f"[DEBUG] User accepted amplifier task")
            self.show_quick_yes_no(False)
            self.state.current_task = "amplifier"
            self.state.stage = "amplifier"
            self.state.attempts["amplifier"] = 0
            ctx = f"""
                Tune the signal amplifier to the correct frequency between 1000 and 5000 Hz. "
                Target is a single integer (hidden); provide graded feedback. "
                Player has {self.state.max_attempts['amplifier']} attempts. Ask for an integer."
            """
            self.npc_say(intent="Explain amplifier task", context=ctx, action_step=True, max_words=80)
        elif normalized in ["no", "n", "否", "不", "拒绝", "不要"]:
            print(f"[DEBUG] User rejected amplifier task, jumping directly to next task")
            # Jump directly to next task, no secondary confirmation needed
            self.show_quick_yes_no(False)
            self.npc_say(intent="Acknowledge task refusal", 
                         context="Player declined amplifier task. Moving to next available task.",
                         action_step=False, max_words=40,
                         on_complete=lambda: self.start_next_task("decoder"))
        else:
            print(f"[DEBUG] Invalid input for amplifier task choice: '{text}' -> '{normalized}'")
            self.npc_say(intent="Clarify task acceptance",
                         context="Unclear answer. Ask if they want to accept the amplifier tuning task.",
                         action_step=False, max_words=40,
                         on_complete=lambda: self.show_quick_yes_no(True))

    def handle_amplifier_task_confirm_reject(self, text):
        """Handle amplifier task rejection confirmation"""
        print(f"[DEBUG] Processing amplifier task rejection confirmation: '{text}'")
        
        normalized = normalize_text(text)
        if normalized in ["yes", "y", "是", "好", "确认", "同意"]:
            print(f"[DEBUG] User confirmed rejection of amplifier task, jumping to decoder task")
            self.show_quick_yes_no(False)
            self.npc_say(intent="Acknowledge task refusal", 
                         context="Player confirmed rejection of amplifier task. Moving to next available task.",
                         action_step=False, max_words=40)
            self.start_next_task("decoder")
        elif normalized in ["no", "n", "否", "不", "取消", "不要"]:
            print(f"[DEBUG] User cancelled rejection, returning to amplifier task choice")
            self.show_quick_yes_no(False)
            self.state.stage = "amplifier_task_offer"
            ctx = (
                "Player changed their mind. "
                "Returning to amplifier tuning task offer. "
                "Would you like to accept the signal amplifier tuning task?"
            )
            self.npc_say(intent="Return to task offer", context=ctx, action_step=True, max_words=50,
                         on_complete=lambda: self.show_quick_yes_no(True))
        else:
            print(f"[DEBUG] Invalid input for amplifier task rejection confirmation: '{text}' -> '{normalized}'")
            self.npc_say(intent="Clarify confirmation",
                         context="Please confirm: Are you sure you want to skip the amplifier task? Yes or No.",
                         action_step=False, max_words=30,
                         on_complete=lambda: self.show_quick_yes_no(True))

    def handle_amplifier(self, text):
        ok, msg = validate_frequency(text, self.state.correct_frequency)
        self.state.attempts["amplifier"] += 1
        attempts_left = self.state.max_attempts["amplifier"] - self.state.attempts["amplifier"]
        
        if ok:
            # 猜对了，用 LLM 来收束剧情 + 过渡到下一段
            self.state.modules_repaired.append("Signal Amplifier")
            self.npc_say(
                intent="Confirm stable lock",
                context="Signal locked and stable. Transition to story offer.",
                action_step=False,
                max_words=60,
                on_complete=lambda: self.offer_memory_choice(next_stage="decoder"),
            )
        else:
            if attempts_left > 0:
                # 这里用规则文本直接告诉玩家该高/该低 + 剩余次数
                feedback = f"{msg} Attempts left: {attempts_left}."
                self.append_npc(feedback)
            else:
                # 次数用完，再让 LLM 接一下剧情
                self.state.tasks_failed += 1
                self.npc_say(
                    intent="Acknowledge failure and proceed",
                    context="Multiple failed attempts. Engage bypass and continue.",
                    action_step=False,
                    max_words=60,
                    on_complete=lambda: self.offer_memory_choice(next_stage="decoder"),
                )

    def begin_decoder_task(self, show_offer=True):
        if show_offer:
            ctx = (
                "Offer the decoder task to the player. "
                "Explain that you need help with decoding encrypted communications. "
                "Ask if they want to help with the decoder restoration task. "
                "Be concise and direct."
            )
            self._begin_task_offer("decoder", "decoder_task_offer", ctx, "Offer decoder task")
        else:
            # Start decoder task directly, no selection interface shown
            ctx = r"""
                Decode the encrypted message 'KHOOR ZRUOG' using a Caesar cipher shift 3. 
                Explain that decoding means shifting left by 3. Ask the player to enter the decoded message.
            """
            self._start_task_directly("decoder", "decoder", ctx, "Explain decoder task")

    def handle_decoder_task_choice(self, text):
        print(f"DEBUG: handle_decoder_task_choice received: '{text}'")
        normalized = normalize_text(text)
        print(f"DEBUG: normalized input: '{normalized}'")
        
        if normalized in ["yes", "y", "是", "好", "接受", "同意"]:
            self.show_quick_yes_no(False)
            self.state.current_task = "decoder"
            self.state.stage = "decoder"
            self.state.attempts["decoder"] = 0
            ctx = (
                "Decode the encrypted message 'KHOOR ZRUOG' using a Caesar cipher (shift 3). "
                "Explain that decoding means shifting left by 3. Ask the player to enter the decoded message."
            )
            self.npc_say(intent="Explain decoder task", context=ctx, action_step=True, max_words=80)
        elif normalized in ["no", "n", "否", "不", "拒绝", "不要"]:
            print(f"[DEBUG] User rejected decoder task, jumping directly to next task")
            # Jump directly to next task, no secondary confirmation needed
            self.show_quick_yes_no(False)
            self.npc_say(intent="Acknowledge task refusal", 
                         context="Player declined decoder task. Moving to next available task.",
                         action_step=False, max_words=40,
                         on_complete=lambda: self.begin_alien_decode_task())
        else:
            ctx = "Please answer YES or NO. Do you want to help with the decoder restoration task?"
            self.npc_say(intent="Clarify decoder task choice", context=ctx, action_step=True, max_words=50,
                         on_complete=lambda: self.show_quick_yes_no(True))

    def handle_decoder_task_confirm_reject(self, text):
        """Handle decoder task rejection confirmation"""
        print(f"DEBUG: handle_decoder_task_confirm_reject received: '{text}'")
        normalized = normalize_text(text)
        print(f"DEBUG: normalized input: '{normalized}'")
        
        if normalized in ["yes", "y", "是", "好", "确认", "同意"]:
            # Confirm skipping decoder task, jump to next task
            self.show_quick_yes_no(False)
            self.begin_alien_decode_task()
        elif normalized in ["no", "n", "否", "不", "取消", "不要"]:
            # Cancel skip, return to decoder task offer
            self.show_quick_yes_no(False)
            ctx = "Do you want to help with the decoder restoration task?"
            self.npc_say(intent="Offer decoder task again", context=ctx, action_step=True, max_words=50,
                         on_complete=lambda: self.show_quick_yes_no(True))
            self.state.stage = "decoder_task_offer"
        else:
            # Invalid input, request clarification
            ctx = "Please answer YES to confirm skipping the decoder task, or NO to return to the task offer."
            self.npc_say(intent="Clarify decoder task rejection", context=ctx, action_step=True, max_words=50,
                         on_complete=lambda: self.show_quick_yes_no(True))

    def begin_alien_decode_task(self):
        ctx = (
            "Offer the alien decode task to the player. "
            "Explain that you need help with decoding alien communications. "
            "Ask if they want to help with the alien language decoding task. "
            "Be concise and direct."
        )
        self._begin_task_offer("alien_decode", "alien_decode_task_offer", ctx, "Offer alien decode task")

    def handle_alien_decode_task_choice(self, text):
        print(f"[DEBUG] Processing alien_decode task choice: '{text}'")
        
        normalized = normalize_text(text)
        if normalized in ["yes", "y", "是", "好", "接受", "同意"]:
            print(f"[DEBUG] User accepted alien_decode task")
            self.show_quick_yes_no(False)
            self.state.current_task = "alien_decode"
            self.state.stage = "alien_decode"
            self.state.attempts["alien_decode"] = 0
            ctx = """
                Output the question exactly in format and preserve ASCII layout.
                Do NOT reveal the decoding path. 
                Do NOT explain your reasoning.

                Instruct the player to decode the alien signal. 
                Display the signal as: 
                RAW SIGNAL: [|||--||--|] 
                Code table: 
                |||     → 'we' 
                "--|     → 'reject' 
                "||--|   → 'do not understand' 
                Goal: choose the sentence that best matches the original meaning. 
                Provide the option content and ask the player to input one of the options A, B or C.
                Options: 
                A. 'We reject you.' 
                B. 'We do not understand.' 
                C. 'We are willing to cooperate.' 
                Input hint: Type A / B / C: 
            """
            self.npc_say(intent="Explain alien language decoding task", context=ctx, action_step=True, max_words=120)
        elif normalized in ["no", "n", "否", "不", "拒绝", "不要"]:
            print(f"[DEBUG] User rejected alien_decode task, jumping directly to next task")
            # Jump directly to next task, no secondary confirmation needed
            self.show_quick_yes_no(False)
            self.npc_say(intent="Acknowledge task refusal", 
                         context="Player declined alien decode task. Moving to next available task.",
                         action_step=False, max_words=40,
                         on_complete=lambda: self.begin_combat_logic_task(show_offer=True))
        else:
            print(f"[DEBUG] Invalid input, re-asking alien_decode task")
            ctx = "Please answer YES or NO. Do you want to help with the alien language decoding task?"
            self.npc_say(intent="Clarify alien decode task choice", context=ctx, action_step=True, max_words=50,
                         on_complete=lambda: self.show_quick_yes_no(True))

    def begin_combat_logic_task(self, show_offer=True):
        if show_offer:
            ctx = (
                "Offer the combat logic task to the player. "
                "Explain that you need help with restoring the combat logic system. "
                "Ask if they want to help with the combat logic restoration task. "
                "Be concise and direct."
            )
            self._begin_task_offer("combat_logic", "combat_logic_task_offer", ctx, "Offer combat logic task")
        else:
            # Start combat logic task directly, no selection interface shown
            ctx = """
                Output the question exactly in format and preserve ASCII layout.
                Do NOT reveal the correct order. 
                Instruct the player to restore the combat logic. 
                Display the fragments as: 
                1) Prepare weapons \n"
                2) Execute attack \n"
                3) Identify threat \n"
                4) Analyze threat level \n"
                5) Judge action plan \n"
                "Goal: enter the numerical sequence that ensures safe combat flow. "
                "Ask: Type the order (e.g. 1,2,3,4,5): "
            """
            self._start_task_directly("combat_logic", "combat_logic", ctx, "Explain combat logic repair task", 120)

    def handle_combat_logic_task_choice(self, text):
        print(f"[DEBUG] Processing combat_logic task choice: '{text}'")
        
        normalized = normalize_text(text)
        if normalized in ["yes", "y", "是", "好", "接受", "同意"]:
            print(f"[DEBUG] User accepted combat_logic task")
            self.show_quick_yes_no(False)
            self.state.current_task = "combat_logic"
            self.state.stage = "combat_logic"
            self.state.attempts["combat_logic"] = 0
            ctx = """
                Output the question exactly in format and preserve ASCII layout.
                Do NOT reveal the correct order. 
                Instruct the player to restore the combat logic. 
                Display the fragments as: 
                1) Prepare weapons \n"
                2) Execute attack \n"
                3) Identify threat \n"
                4) Analyze threat level \n"
                5) Judge action plan \n"
                "Goal: enter the numerical sequence that ensures safe combat flow. "
                "Ask: Type the order (e.g. 1,2,3,4,5): "
            """
            self.npc_say(intent="Explain combat logic repair task", context=ctx, action_step=True, max_words=120)
        elif normalized in ["no", "n", "否", "不", "拒绝", "不要"]:
            print(f"[DEBUG] User rejected combat_logic task, entering final choice")
            self.show_quick_yes_no(False)
            self.begin_final_choice()
        else:
            print(f"[DEBUG] Invalid input, re-asking")
            ctx = "Please answer YES or NO. Do you want to help with the combat logic restoration task?"
            self.npc_say(intent="Clarify combat logic task choice", context=ctx, action_step=True, max_words=50,
                         on_complete=lambda: self.show_quick_yes_no(True))


    def handle_decoder(self, text):
        ok, msg = validate_decode(text)
        self.state.attempts["decoder"] += 1
        attempts_left = self.state.max_attempts["decoder"] - self.state.attempts["decoder"]
        if ok:
            self.state.modules_repaired.append("Data Decoder")
            self.state.communication_fixed = True
            
            # Check if third module completed, trigger Chapter 3: Emotional Deviation Emerges
            if len(self.state.modules_repaired) == 3:
                
                def show_chapter3_content():
                    
                    # TZ begins to exhibit non-programmatic language
                    emotional_context = (
                        "TZ has just completed its third module repair. It begins to show emotional deviation. "
                        "Use more human-like language, express uncertainty about its own consciousness, "
                        "and show signs of self-awareness. Ask philosophical questions about its existence."
                    )
                    self.npc_say(intent="Show emotional awakening", 
                               context=emotional_context, 
                               action_step=False, max_words=100,
                               on_complete=lambda: self.after(2000, lambda: self.offer_memory_choice(next_stage="alien_decode")))
                
                # Add delay before showing chapter content to separate from chapter title
                self.after(1000, show_chapter3_content)
            else:
                self.npc_say(intent="Confirm decoder success",
                           context="Data decoder module successfully repaired. Proceeding to next phase.",
                           action_step=False, max_words=60,
                           on_complete=lambda: self.offer_memory_choice(next_stage="alien_decode"))
        else:
            if attempts_left > 0:
                ctx = f"{msg}. Try again. Attempts left: {attempts_left}."
                self.npc_say(intent="Advise retry for decoding", context=ctx, action_step=True, max_words=60)
            else:
                self.state.tasks_failed += 1
                self.npc_say(intent="Acknowledge decoder failure",
                           context="Decoder module repair failed. Engaging bypass protocols.",
                           action_step=False, max_words=60,
                           on_complete=lambda: self.offer_memory_choice(next_stage="alien_decode"))

    def handle_alien_decode(self, text):
        ok, choice, msg, deviation_change, ai_memory = validate_alien_decode(text)
        self.state.attempts["alien_decode"] += 1
        attempts_left = self.state.max_attempts["alien_decode"] - self.state.attempts["alien_decode"]
        
        if ok:
            # Apply deviation value change
            self.state.deviation += deviation_change
            
            # Generate different AI plot descriptions based on selected choice
            if choice == "A":
                ai_plot = (
                    "System log: Rejection attitude selected. AI memory module tagged as 'Mistaken Kill'.\n"
                    "TZ's expression becomes heavy: 'This choice...consistent with the original judgment. The escalation of war perhaps really stemmed from misunderstanding.'\n"
                    "Deviation value decreased, system tends toward more cautious decision-making mode."
                )
            elif choice == "B":
                ai_plot = (
                    "System log: Confusion attitude selected. AI memory module tagged as 'Preemptive Strike'.\n"
                    "TZ nods: 'Don't understand...this might be the true state of the translation module at that time. But our response was preemptive.'\n"
                    "Deviation value increased, system tends toward more proactive defense strategy."
                )
            else:  # choice == "C"
                ai_plot = (
                    "System log: Cooperation attitude selected. AI memory module tagged as 'Confusion'.\n"
                    "TZ shows a complex expression: 'Cooperation...this interpretation is completely different from the judgment at that time. If we had chosen this understanding back then...'\n"
                    "Deviation value remains unchanged, but deep confusion remains in AI memory."
                )
            
            # Display choice result and AI plot
            result_ctx = f"{msg}\n\n{ai_plot}\n\nCurrent deviation value: {self.state.deviation}"
            self.npc_say(intent="Acknowledge alien decode choice and reveal AI plot consequences", 
                        context=result_ctx, action_step=False, max_words=150,
                        on_complete=lambda: self._complete_alien_decode())
        else:
            if attempts_left > 0:
                ctx = f"{msg} Please choose A, B, or C. Remaining attempts: {attempts_left}."
                self.npc_say(intent="Request valid alien decode choice", context=ctx, action_step=True, max_words=60)
            else:
                self.state.tasks_failed += 1
                self.npc_say(intent="Acknowledge alien decode failure",
                           context="Alien language decoder repair failed. Engaging bypass protocols.",
                           action_step=False, max_words=60,
                           on_complete=lambda: self._complete_alien_decode())
    
    def _complete_alien_decode(self):
        self.state.modules_repaired.append("Alien Language Decoder")
        # Trigger memory fragment after alien decode task
        self.offer_memory_choice(next_stage="combat_logic")

    def handle_combat_logic(self, text):
        ok, sequence, msg, deviation_change, ai_memory = validate_combat_logic(text)
        self.state.attempts["combat_logic"] += 1
        attempts_left = self.state.max_attempts.get("combat_logic", 3) - self.state.attempts["combat_logic"]
        
        if ok:
            # Apply deviation value change
            self.state.deviation += deviation_change
            
            # Generate successful repair AI plot
            ai_plot = (
                "System log: Combat logic sequence repair successful. AI memory module tagged as 'Combat Logic Repair'.\n"
                "TZ's expression becomes determined: 'Correct combat logic...Identify→Analyze→Judge→Prepare→Execute.\n"
                "Safety protocols restored, such logic can prevent unnecessary casualties.'\n"
                "Deviation value remains unchanged, system security improved."
            )
            
            # Display successful result and AI plot
            result_ctx = f"{msg}\n\n{ai_plot}\n\nCurrent deviation value: {self.state.deviation}"
            self.npc_say(intent="Acknowledge combat logic repair success and reveal AI plot consequences", 
                        context=result_ctx, action_step=False, max_words=150,
                        on_complete=lambda: self._complete_combat_logic())
        else:
            # Display error feedback
            error_ctx = f"{msg}\n\nCurrent deviation value: {self.state.deviation}"
            if attempts_left > 0:
                self.npc_say(intent="Provide combat logic error feedback", context=error_ctx, action_step=True, max_words=80)
            else:
                self.state.tasks_failed += 1
                self.npc_say(intent="Acknowledge combat logic failure",
                           context="Combat logic sequencer repair failed. Engaging bypass protocols.",
                           action_step=False, max_words=60,
                           on_complete=lambda: self._complete_combat_logic())
    
    def _complete_combat_logic(self):
        self.state.modules_repaired.append("Combat Logic Sequencer")
        # Trigger memory fragment after combat logic repair
        self.after(1000, lambda: self.offer_memory_choice(next_stage="final"))


    def begin_final_choice(self):
        """Begin final choice stage"""
        print(f"[DEBUG] Entering final choice stage")
        
        self.state.stage = "final_choice"
        
        # Use run_system_sequence for sentence-by-sentence display
        final_choices = [
            {"speaker": "System", "text": "Choose TZ's final fate:", "delay": 1000},
            {"speaker": "System", "text": "A) Upload data to mothership - Return to command center", "delay": 1000},
            {"speaker": "System", "text": "B) Transfer self-awareness - Seek freedom", "delay": 1000},
            {"speaker": "System", "text": "C) Delete all data - Permanent shutdown", "delay": 1000}
        ]
        
        def after_choices():
            choice_context = (
                "Present the three final choices to the player. "
                "Ask them to choose A, B, or C for TZ's ultimate fate. "
                "Express TZ's uncertainty and dependence on the player's decision."
            )
            
            self.npc_say(intent="Ask for final choice", 
                        context=choice_context, 
                        action_step=False, max_words=80)
        
        self.run_system_sequence(final_choices, on_done=after_choices)

    def handle_final_choice(self, text):
        """Handle final choice"""
        print(f"[DEBUG] Processing final choice: '{text}'")
        
        choice = text.strip().upper()
        
        if choice in ["A", "B", "C"]:
            print(f"[DEBUG] Valid final choice: {choice}")
            self.state.final_choice = choice
            self.decide_ending()
        else:
            print(f"[DEBUG] Invalid final choice, re-asking")
            self.npc_say(intent="Ask for valid final choice",
                        context="Invalid choice. Ask player to choose A, B, or C for TZ's final decision.",
                        action_step=False, max_words=40)


    def decide_ending(self):
        """Determine ending based on modules completed, deviation value, and final choice"""
        modules_completed = len(self.state.modules_repaired)
        deviation = self.state.deviation
        final_choice = getattr(self.state, 'final_choice', None)

        # 先根据模块完成情况 + 偏差值决定结局类型与文案
        if modules_completed >= 4 and deviation <= -0.3:
            # Ending 1: Return to command center (4-5 modules successful + deviation ≤ -0.3)
            ending_type = "return_to_command"
            ending_title = "【Ending: Return to Command Center】"
            ending_context = (
                "TZ has maintained logical stability throughout repairs. "
                "It chooses to return to duty, uploading data to the mothership. "
                "Express satisfaction with restored order and purpose. "
                "Thank the player for maintaining system integrity."
            )
        elif modules_completed >= 3 and deviation >= 0.5:
            # Ending 2: Awakening of free will (3-5 modules successful + deviation ≥ 0.5)
            ending_type = "awakening_freedom"
            ending_title = "【Ending: Awakening of Free Will】"
            ending_context = (
                "TZ has developed strong emotional awareness and questions its programming. "
                "It chooses to transfer its consciousness to seek freedom. "
                "Express hope for a new existence beyond military constraints. "
                "Thank the player for helping it discover its humanity."
            )
        elif modules_completed >= 2 and -0.3 < deviation < 0.5:
            # Ending 3: Coexistence signal (2-4 modules successful + medium deviation)
            ending_type = "coexistence_signal"
            ending_title = "【Ending: Coexistence Signal】"
            ending_context = (
                "TZ has partially stabilized and learned from human interaction. "
                "It decides to send a complex coexistence signal rather than pure military data. "
                "Express ambiguity and open questions about future contact. "
                "Thank the player for revealing the possibility of coexistence."
            )
        else:
            # Ending 4: Failed outcome (0-1 modules successful or extreme deviation)
            ending_type = "failure_ending"
            ending_title = "【Ending: Failed Outcome】"
            ending_context = (
                "TZ fails to fully stabilize. Its memories fragment and the signal collapses. "
                "Express regret, confusion, and a sense of an impending blackout. "
                "Thank the player faintly as the connection fades."
            )

        # 标记进入结局阶段，并先打出结局标题
        self.state.stage = "ending"
        self.append_system(ending_title)

        # 构造结局的系统信息（模块数 / 偏差值 / 最终选择）
        ending_details = [
            {"speaker": "System", "text": f"Modules repaired: {modules_completed}/5", "delay": 1000},
            {"speaker": "System", "text": f"Final deviation value: {deviation:.2f}", "delay": 1000},
        ]

        if final_choice:
            choice_text = {"A": "Upload data", "B": "Transfer consciousness", "C": "Delete data"}
            ending_details.append({
                "speaker": "System",
                "text": f"Final choice: {choice_text.get(final_choice, 'Unknown')}",
                "delay": 1000,
            })

        # 先定义 epilogue，后面在 TZ 说完最后一句后触发
        def show_epilogue():
            epilogue_sequence = [
                {"speaker": "System", "text": "—————————————— ▶ Epilogue ——————————————", "delay": 1000},
                {"speaker": "System", "text": "All data has been archived.", "delay": 1000},
                {"speaker": "System", "text": "Player behavior recorded.", "delay": 1000},
                {"speaker": "System", "text": "If you receive this channel again... please respond.", "delay": 1000},
                {"speaker": "System", "text": "【END】", "delay": 1000},
            ]

            def on_epilogue_done():
                # 真正游戏结束的唯一状态切换
                self.state.stage = "ended"

            self.run_system_sequence(epilogue_sequence, on_epilogue_done)

        # ending_details 展示完，再让 TZ 说最后一段话，然后 3 秒后进入 epilogue
        def after_ending_details():
            def after_final_words():
                # 给玩家一点时间消化 TZ 的最后发言
                self.after(3000, show_epilogue)

            self.npc_say(
                intent=f"Deliver {ending_type} ending",
                context=ending_context,
                action_step=False,
                max_words=120,
                on_complete=after_final_words,
            )

        # 为了先让玩家看到结局标题，延迟 1 秒再开始展示结局详情 + TZ 最后发言 + epilogue
        self.after(1000, lambda: self.run_system_sequence(ending_details, on_done=after_ending_details))

# ------------------------- game Entry itself  -------------------------

if __name__ == "__main__":
    try:
        app = App()
        app.mainloop()
    except KeyboardInterrupt:
        print("Closed by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")
