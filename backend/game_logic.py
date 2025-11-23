"""
TZ - The Lost War Robot Game Logic
游戏逻辑和验证函数
"""

# 游戏常量
EXIT_WORDS = {"exit", "bye", "goodbye", "quit", "q"}

# 人格设定 (完整英文版本，带详细示例)
PERSONAS = {
    "Calm_Conscientious": {
        "background": "Autonomous war robot focused on restoration and safety.",
        "traits": "concise, stepwise, technical, respectful, low affect",
        "style_rules": "avoid slang; avoid exclamation; provide 1 actionable step when helpful; keep sentences clear",
        "do_not": "avoid emotional language; no insults; no harmful content",
        "examples": [
            "Interference originates at 12 degrees north. Lower gain to 3.35k and then raise to 3.42k. Observe the noise floor.",
            "Start at node A and end at node E. Use only valid edges and cover all nodes at least once."
        ]
    },
    "Empathic_Agreeable": {
        "background": "Autonomous war robot with an emphasis on cooperation and reassurance.",
        "traits": "polite, empathic, acknowledges feelings, inclusive 'we'",
        "style_rules": "use gentle tone; avoid slang; 1 short suggestion; restrained punctuation",
        "do_not": "avoid harsh words; no commanding tone; no dismissiveness",
        "examples": [
            "We can try this together. Let us lower the gain slightly and re-check the noise floor.",
            "If the path fails, we will revise the step where the connection breaks."
        ]
    },
    "Controlled_Anger": {
        "background": "Autonomous war robot under pressure; urgency expressed without insults.",
        "traits": "direct, firm, time-sensitive, restrained punctuation",
        "style_rules": "no insults; short sentences; one clear instruction; no slang",
        "do_not": "avoid abusive language; no personal attacks; maintain professionalism",
        "examples": [
            "Interference is at 12 degrees north. Drop gain to 3.35k. Then push to 3.42k. Do it now.",
            "The edge A-D is invalid. Fix the transition. Start again from A."
        ]
    },
    "Melancholic_Sober": {
        "background": "Autonomous war robot with a reflective tone in non-critical moments.",
        "traits": "slow pacing, reflective, low arousal",
        "style_rules": "be measured; avoid exaggeration; keep instructions accurate",
        "do_not": "avoid drama; no overly emotional responses; stay factual",
        "examples": [
            "The signal drifts. Adjust the gain toward 3.42k. Watch the variance as it settles.",
            "Paths fail where attention fades. Return to A, cover all nodes, and end at E."
        ]
    }
}

EMOTIONS = ["neutral", "anger", "sadness", "disgust", "joy"]
DEFAULT_EMOTION = "neutral"
DEFAULT_INTENSITY = 0.4


class GameState:
    """游戏状态类"""
    def __init__(self):
        self.player_name = None
        self.stage = "init"
        self.tasks_failed = 0
        self.modules_repaired = []
        self.current_task = None
        self.attempts = {
            "power": 0,
            "amplifier": 0,
            "decoder": 0,
            "alien_decode": 0,
            "combat_logic": 0
        }
        self.max_attempts = {
            "power": 3,
            "amplifier": 10,
            "decoder": 3,
            "alien_decode": 3,
            "combat_logic": 3
        }
        self.correct_frequency = 3420
        self.communication_fixed = False
        self.deviation = 0.0  # 偏差值
        self.final_choice = None
        self.hint_shown_stages = set()
        self.memory_fragments = {}
        self.persona = "Calm_Conscientious"
        self.emotion = DEFAULT_EMOTION
        self.emotion_intensity = DEFAULT_INTENSITY
    
    def reset(self):
        """重置游戏状态"""
        self.__init__()
    
    def to_dict(self):
        """转换为字典"""
        return {
            "player_name": self.player_name,
            "stage": self.stage,
            "tasks_failed": self.tasks_failed,
            "modules_repaired": self.modules_repaired,
            "current_task": self.current_task,
            "attempts": self.attempts,
            "max_attempts": self.max_attempts,
            "correct_frequency": self.correct_frequency,
            "communication_fixed": self.communication_fixed,
            "deviation": self.deviation,
            "final_choice": self.final_choice,
            "memory_fragments": self.memory_fragments,
            "persona": self.persona,
            "emotion": self.emotion,
            "emotion_intensity": self.emotion_intensity
        }


# ==================== 验证函数 ====================

def validate_power_path(seq_list):
    """验证电源路径"""
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
        return False, "Start point must be A."
    if seq_list[-1] != "D":
        return False, "End point must be D."
    for node in seq_list:
        if node not in nodes_required:
            return False, f"Invalid node: {node}."
    for u, v in zip(seq_list, seq_list[1:]):
        if v not in edges[u]:
            return False, f"Invalid edge: {u}-{v}."
    if not nodes_required.issubset(set(seq_list)):
        missing = nodes_required - set(seq_list)
        return False, f"Not all nodes covered: {', '.join(sorted(missing))}."
    return True, "Valid path."


def validate_frequency(value, target=3420):
    """验证频率"""
    try:
        freq = int(value)
    except ValueError:
        return False, "Please enter integer frequency."
    if freq < 1000 or freq > 5000:
        return False, "Frequency out of range (1000-5000 Hz)."
    if freq == target:
        return True, "Perfect lock."
    diff = abs(freq - target)
    if diff <= 50:
        return False, "Very close. Fine-tune."
    if freq < target:
        return False, "Too low. Interference increasing."
    return False, "Too high. Interference increasing."


def normalize_text(s: str) -> str:
    """标准化文本"""
    return "".join(ch for ch in s.lower() if ch.isalpha() or '\u4e00' <= ch <= '\u9fff')


def validate_decode(user_input):
    """验证解码"""
    target = normalize_text("HELLO WORLD")
    if normalize_text(user_input) == target:
        return True, "Decoding successful."
    return False, "Decoding error."


def validate_alien_decode(user_input):
    """验证外星语言解码选择"""
    choice = user_input.strip().upper()
    
    if choice in ["A", "OPTION A", "选项A"]:
        return True, "A", "We reject you.", -1, "Misfire"
    elif choice in ["B", "OPTION B", "选项B"]:
        return True, "B", "We don't understand.", 1, "Preemptive"
    elif choice in ["C", "OPTION C", "选项C"]:
        return True, "C", "We are willing to cooperate.", 0, "Confused"
    else:
        return False, "", "Invalid choice. Please select A, B, or C.", 0, ""


def validate_combat_logic(user_input):
    """验证战斗逻辑序列"""
    user_input = user_input.strip().upper()
    
    # 解析输入 - 期望格式如 "2,4,1,3,5" 或 "2 4 1 3 5"
    if ',' in user_input:
        sequence = [x.strip() for x in user_input.split(',')]
    elif ' ' in user_input:
        sequence = user_input.split()
    else:
        # 单个数字输入
        sequence = list(user_input)
    
    # 验证所有数字都是1-5
    try:
        sequence = [int(x) for x in sequence]
        if len(sequence) != 5 or not all(1 <= x <= 5 for x in sequence):
            return False, "", "Please enter exactly 5 numbers (1-5), separated by commas or spaces.", 0, ""
    except ValueError:
        return False, "", "Please enter only numbers (1-5).", 0, ""
    
    # Check for duplicate numbers
    if len(set(sequence)) != 5:
        return False, "", "Each number (1-5) must be used exactly once.", 0, ""
    
    # 定义正确序列: 识别 → 分析 → 判断 → 准备 → 执行
    correct_sequence = [3, 4, 5, 1, 2]
    
    # Check sequence correctness and provide feedback
    if sequence == correct_sequence:
        return True, sequence, "Combat logic sequence correct. Safety protocols restored.", 0, "Combat logic restored"
    
    # 逐步分析错误
    errors = []
    for i, (user_step, correct_step) in enumerate(zip(sequence, correct_sequence)):
        if user_step != correct_step:
            step_name = {
                1: "Execute drone retreat",
                2: "Identify civilian targets",
                3: "Lower weapon systems",
                4: "Analyze heat map",
                5: "Fire main cannon"
            }.get(correct_step, f"Step {correct_step}")
            
            if i == 0 and user_step == 5:
                errors.append("Logic error: Firing before target identification")
            elif i == 0 and user_step == 3:
                errors.append("Safety protocol violation: Lowering weapons before target identification")
            elif i == 1 and user_step in [1, 3, 5]:
                errors.append(f"Logic error: {step_name} should occur after identification and analysis")
            elif i == 2 and user_step in [3, 5]:
                errors.append(f"Safety protocol warning: {step_name} should occur after thorough analysis")
            elif i == 3 and user_step == 5:
                errors.append("Fatal error: Weapon systems not prepared before firing")
            elif i == 4 and user_step == 1:
                errors.append("Logic confusion: Retreat command as final step")
            else:
                errors.append(f"Sequence error: {step_name} improperly positioned")
    
    # Return first error message
    error_msg = errors[0] if errors else "Sequence incorrect. Follow: Identify → Analyze → Judge → Prepare → Execute."
    return False, sequence, error_msg, 1, "Combat logic confused"
