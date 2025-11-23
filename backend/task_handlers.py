"""
TZ游戏任务处理模块
"""

from game_logic import validate_power_path, validate_frequency, validate_decode, validate_alien_decode, validate_combat_logic, normalize_text
from memory_generator import generate_memory_fragment


# ========================= 固定任务文案 =========================
# 从 main.py 中 1:1 提取的固定文案内容，直接显示不通过LLM处理
FIXED_TASK_CONTENT = {
    "power": """The power circuit has failed.
Reconnect it using this layout:

```
A
XX   D
C X
    B
```

Valid connections: A-C, C-B, C-D, B-D.
Start at A, end at D. Cover all nodes at least once. Revisits allowed.

Input your sequence (e.g. A-B-C-D):""",
    
    "amplifier": """Signal amplifier calibration required.

Frequency range: 1000-5000 Hz
Target: Find the correct frequency (hidden)
Attempts: 10

You will receive feedback after each attempt:
- "Too low" - Increase frequency
- "Too high" - Decrease frequency  
- "Very close" - Minor adjustment needed
- "Perfect lock" - Success!

Input frequency (integer):""",
    
    "decoder": """Data decoder reconstruction required.

Encrypted message: KHOOR ZRUOG
Encryption: Caesar cipher (shift +3)
Decoding: Shift each letter back by 3 positions

Example:
  K → H (K-3)
  H → E (H-3)
  O → L (O-3)

Input the decoded message:""",
    
    "alien_decode": """Alien signal decoding required.

RAW SIGNAL: [|||--||--|

Code table:
  |||      → 'we'
  --|      → 'reject'  
  ||--|    → 'do not understand'

Analyze the signal pattern and choose the best interpretation:

A) We reject you.
B) We do not understand.
C) We are willing to cooperate.

Input your choice (A/B/C):""",
    
    "combat_logic": """Combat logic sequencer restoration required.

The combat system has fragmented into 5 logic steps:

1) Execute Drone Retreat
2) Identify Civilian Targets  
3) Lower Weapon Systems
4) Analyze Heat Map
5) Fire Primary Cannon

Goal: Arrange these steps in the correct logical order to ensure safe combat protocols.

Correct sequence should follow: Identify → Analyze → Judge → Prepare → Execute

Input the numerical sequence (e.g. 3,4,5,1,2):"""
}
# =============================================================


# 导入所有任务处理函数
def get_task_handler(stage):
    """获取任务处理函数"""
    handlers = {
        "power_task_offer": handle_power_task_choice,
        "power_task_confirm_reject": handle_power_task_confirm_reject,
        "power": handle_power,
        "amplifier_task_offer": handle_amplifier_task_choice,
        "amplifier_task_confirm_reject": handle_amplifier_task_confirm_reject,
        "amplifier": handle_amplifier,
        "decoder_task_offer": handle_decoder_task_choice,
        "decoder_task_confirm_reject": handle_decoder_task_confirm_reject,
        "decoder": handle_decoder,
        "alien_decode_task_offer": handle_alien_decode_task_choice,
        "alien_decode": handle_alien_decode,
        "combat_logic_task_offer": handle_combat_logic_task_choice,
        "combat_logic": handle_combat_logic,
    }
    return handlers.get(stage)


# 电源任务
def handle_power_task_choice(state, text, api_key, llm_function):
    normalized = normalize_text(text)
    
    if normalized in ["yes", "y", "是", "同意"]:
        state.stage = "power"
        # 直接显示固定文案，不通过LLM
        return {"type": "npc", "content": FIXED_TASK_CONTENT["power"]}
    elif normalized in ["no", "n", "否"]:
        state.stage = "power_task_confirm_reject"
        return {"type": "system", "content": "Skip this task? (yes/no)", "show_quick_buttons": True}
    else:
        return {"type": "system", "content": "Please answer yes or no"}


def handle_power_task_confirm_reject(state, text, api_key, llm_function):
    if normalize_text(text) in ["yes", "y", "是"]:
        state.tasks_failed += 1
        state.stage = "amplifier_task_offer"
        return {"type": "system", "content": "Power task skipped. Next task: Signal Amplifier Tuning (yes/no)", "show_quick_buttons": True}
    else:
        state.stage = "power"
        return {"type": "system", "content": "Returning to power task. Enter path sequence"}


def handle_power(state, text, api_key, llm_function):
    from stage_handlers import compose_npc_reply
    raw = text.upper().replace(" ", "")
    seq = [x for x in raw.split("-") if x]
    ok, msg = validate_power_path(seq)
    
    state.attempts["power"] += 1
    attempts_left = state.max_attempts["power"] - state.attempts["power"]
    
    if ok:
        state.modules_repaired.append("Power Module")
        npc_response = compose_npc_reply("Celebrate success", f"Commander successfully repaired power!", state, llm_function, api_key, 60)
        return {"type": "sequence", "messages": [{"type": "system", "content": "✓ Path verified successfully!", "delay": 800}, {"type": "npc", "content": npc_response, "delay": 1000}], "next_action": "offer_memory", "next_stage": "amplifier"}
    elif attempts_left > 0:
        return {"type": "system", "content": f"✗ {msg}\nAttempts remaining: {attempts_left}"}
    else:
        # 前3个任务失败不添加到 modules_repaired
        state.tasks_failed += 1
        npc_response = compose_npc_reply("Acknowledge failure", "Multiple failed attempts on power module. Engage backup and proceed.", state, llm_function, api_key, 70)
        return {"type": "sequence", "messages": [
            {"type": "system", "content": "✗ Attempts exhausted", "delay": 800},
            {"type": "npc", "content": npc_response, "delay": 1000}
        ], "next_action": "offer_memory", "next_stage": "amplifier"}


# 放大器任务
def handle_amplifier_task_choice(state, text, api_key, llm_function):
    normalized = normalize_text(text)
    
    if normalized in ["yes", "y", "是"]:
        state.stage = "amplifier"
        # 直接显示固定文案，不通过LLM
        return {"type": "npc", "content": FIXED_TASK_CONTENT["amplifier"]}
    elif normalized in ["no", "n", "否"]:
        state.stage = "amplifier_task_confirm_reject"
        return {"type": "system", "content": "Skip this task? (yes/no)", "show_quick_buttons": True}
    else:
        return {"type": "system", "content": "Please answer yes or no"}


def handle_amplifier_task_confirm_reject(state, text, api_key, llm_function):
    if normalize_text(text) in ["yes", "y", "是"]:
        state.tasks_failed += 1
        state.stage = "decoder_task_offer"
        return {"type": "system", "content": "Amplifier task skipped. Next: Data Decryption (yes/no)", "show_quick_buttons": True}
    else:
        state.stage = "amplifier"
        return {"type": "system", "content": "Returning to amplifier task. Enter frequency value"}


def handle_amplifier(state, text, api_key, llm_function):
    from stage_handlers import compose_npc_reply
    ok, msg = validate_frequency(text, state.correct_frequency)
    state.attempts["amplifier"] += 1
    attempts_left = state.max_attempts["amplifier"] - state.attempts["amplifier"]
    
    if ok:
        state.modules_repaired.append("Signal Amplifier")
        state.communication_fixed = True
        npc_response = compose_npc_reply("Celebrate success", "Amplifier tuning successful!", state, llm_function, api_key, 60)
        return {"type": "sequence", "messages": [{"type": "system", "content": "✓ Frequency locked!", "delay": 800}, {"type": "npc", "content": npc_response, "delay": 1000}], "next_action": "offer_memory", "next_stage": "decoder"}
    elif attempts_left > 0:
        return {"type": "system", "content": f"✗ {msg}\nAttempts remaining: {attempts_left}"}
    else:
        # 前3个任务失败不添加到 modules_repaired
        state.tasks_failed += 1
        from stage_handlers import compose_npc_reply
        npc_response = compose_npc_reply("Acknowledge failure", "Multiple failed attempts. Engage bypass and continue.", state, llm_function, api_key, 60)
        return {"type": "sequence", "messages": [
            {"type": "system", "content": "✗ Attempts exhausted", "delay": 800},
            {"type": "npc", "content": npc_response, "delay": 1000}
        ], "next_action": "offer_memory", "next_stage": "decoder"}


# 解码器任务
def handle_decoder_task_choice(state, text, api_key, llm_function):
    normalized = normalize_text(text)
    
    if normalized in ["yes", "y", "是"]:
        state.stage = "decoder"
        # 直接显示固定文案，不通过LLM
        return {"type": "npc", "content": FIXED_TASK_CONTENT["decoder"]}
    elif normalized in ["no", "n", "否"]:
        state.stage = "decoder_task_confirm_reject"
        return {"type": "system", "content": "Skip this task? (yes/no)", "show_quick_buttons": True}
    else:
        return {"type": "system", "content": "Please answer yes or no"}


def handle_decoder_task_confirm_reject(state, text, api_key, llm_function):
    if normalize_text(text) in ["yes", "y", "是"]:
        state.tasks_failed += 1
        state.stage = "alien_decode_task_offer"
        return {"type": "system", "content": "Decoder task skipped. Next: Alien Language (yes/no)", "show_quick_buttons": True}
    else:
        state.stage = "decoder"
        return {"type": "system", "content": "Returning to decoder task"}


def handle_decoder(state, text, api_key, llm_function):
    from stage_handlers import compose_npc_reply
    ok, msg = validate_decode(text)
    state.attempts["decoder"] += 1
    attempts_left = state.max_attempts["decoder"] - state.attempts["decoder"]
    
    if ok:
        state.modules_repaired.append("Data Decoder")
        npc_response = compose_npc_reply("Celebrate success", "Decoding successful!", state, llm_function, api_key, 60)
        return {"type": "sequence", "messages": [{"type": "system", "content": "✓ Decoding successful: HELLO WORLD", "delay": 800}, {"type": "npc", "content": npc_response, "delay": 1000}], "next_action": "offer_memory", "next_stage": "alien_decode"}
    elif attempts_left > 0:
        return {"type": "system", "content": f"✗ Decoding error\nAttempts remaining: {attempts_left}"}
    else:
        # 前3个任务失败不添加到 modules_repaired
        state.tasks_failed += 1
        from stage_handlers import compose_npc_reply
        npc_response = compose_npc_reply("Acknowledge failure", "Decoder module repair failed. Engaging bypass protocols.", state, llm_function, api_key, 60)
        return {"type": "sequence", "messages": [
            {"type": "system", "content": "✗ Attempts exhausted", "delay": 800},
            {"type": "npc", "content": npc_response, "delay": 1000}
        ], "next_action": "offer_memory", "next_stage": "alien_decode"}


# 外星解码任务
def handle_alien_decode_task_choice(state, text, api_key, llm_function):
    normalized = normalize_text(text)
    
    if normalized in ["yes", "y", "是"]:
        state.stage = "alien_decode"
        # 直接显示固定文案，不通过LLM
        return {"type": "npc", "content": FIXED_TASK_CONTENT["alien_decode"]}
    elif normalized in ["no", "n", "否"]:
        state.tasks_failed += 1
        state.stage = "combat_logic_task_offer"
        return {"type": "system", "content": "Alien task skipped. Final task: Combat Logic (yes/no)", "show_quick_buttons": True}
    else:
        return {"type": "system", "content": "Please answer yes or no"}


def handle_alien_decode(state, text, api_key, llm_function):
    from stage_handlers import compose_npc_reply
    ok, choice, msg, deviation_change, ai_memory = validate_alien_decode(text)
    state.attempts["alien_decode"] += 1
    attempts_left = state.max_attempts["alien_decode"] - state.attempts["alien_decode"]
    
    if ok:
        state.modules_repaired.append("Alien Communication")
        state.deviation += deviation_change
        state.deviation = max(-1.0, min(1.0, state.deviation))
        npc_response = compose_npc_reply("Respond to choice", f"Choice {choice}: {msg}", state, llm_function, api_key, 80)
        return {"type": "sequence", "messages": [
            {"type": "system", "content": f"✓ {msg}", "delay": 800},
            {"type": "npc", "content": npc_response, "delay": 1000},
            {"type": "system", "content": f"Current deviation value: {state.deviation:.2f}", "delay": 1000}
        ], "next_action": "offer_memory", "next_stage": "combat_logic"}
    elif attempts_left > 0:
        return {"type": "system", "content": f"✗ {msg}\nAttempts remaining: {attempts_left}"}
    else:
        # 与 main.py 保持一致：外星语言任务失败后仍然添加模块
        state.tasks_failed += 1
        state.modules_repaired.append("Alien Communication")
        from stage_handlers import compose_npc_reply
        npc_response = compose_npc_reply("Acknowledge failure", "Alien language decoder repair failed. Engaging bypass protocols.", state, llm_function, api_key, 60)
        return {"type": "sequence", "messages": [
            {"type": "system", "content": "✗ Attempts exhausted", "delay": 800},
            {"type": "npc", "content": npc_response, "delay": 1000}
        ], "next_action": "offer_memory", "next_stage": "combat_logic"}


# 战斗逻辑任务
def handle_combat_logic_task_choice(state, text, api_key, llm_function):
    normalized = normalize_text(text)
    
    if normalized in ["yes", "y", "是"]:
        state.stage = "combat_logic"
        # 直接显示固定文案，不通过LLM
        return {"type": "npc", "content": FIXED_TASK_CONTENT["combat_logic"]}
    elif normalized in ["no", "n", "否"]:
        state.tasks_failed += 1
        state.stage = "final_choice"
        return {"type": "system", "content": "Combat logic skipped", "next_action": "start_final_choice"}
    else:
        return {"type": "system", "content": "Please answer yes or no"}


def handle_combat_logic(state, text, api_key, llm_function):
    from stage_handlers import compose_npc_reply
    ok, sequence, msg, deviation_change, ai_memory = validate_combat_logic(text)
    state.attempts["combat_logic"] += 1
    attempts_left = state.max_attempts["combat_logic"] - state.attempts["combat_logic"]
    
    if ok:
        state.modules_repaired.append("Combat Logic")
        state.deviation += deviation_change
        state.deviation = max(-1.0, min(1.0, state.deviation))
        npc_response = compose_npc_reply("Celebrate success", "Combat logic rebuild successful!", state, llm_function, api_key, 80)
        return {"type": "sequence", "messages": [
            {"type": "system", "content": "✓ Sequence correct!", "delay": 800},
            {"type": "npc", "content": npc_response, "delay": 1000},
            {"type": "system", "content": f"Current deviation value: {state.deviation:.2f}", "delay": 1000}
        ], "next_action": "offer_memory", "next_stage": "final"}
    elif attempts_left > 0:
        return {"type": "system", "content": f"✗ {msg}\nAttempts remaining: {attempts_left}"}
    else:
        # 与 main.py 保持一致：战斗逻辑任务失败后仍然添加模块
        state.tasks_failed += 1
        state.modules_repaired.append("Combat Logic")
        from stage_handlers import compose_npc_reply
        npc_response = compose_npc_reply("Acknowledge failure", "Combat logic sequencer repair failed. Engaging bypass protocols.", state, llm_function, api_key, 60)
        return {"type": "sequence", "messages": [
            {"type": "system", "content": "✗ Attempts exhausted", "delay": 800},
            {"type": "npc", "content": npc_response, "delay": 1000}
        ], "next_action": "offer_memory", "next_stage": "final"}


# 记忆系统
def handle_memory_choice(state, text, api_key, llm_function):
    """处理记忆碎片选择 - 与 main.py 逻辑一致"""
    from stage_handlers import MEMORY_INTERPRETATION_OPTIONS, compose_npc_reply
    
    choice = text.strip().upper()
    # 从 "memory_choice_target" 格式提取目标
    stage_parts = state.stage.split("_")
    if len(stage_parts) >= 3:
        target = "_".join(stage_parts[2:])  # 处理带下划线的目标
    else:
        target = "amplifier"  # 默认值
    
    if choice in ["A", "OPTION A", "选项A", "YES", "Y", "播放", "是"]:
        # 玩家想要观看记忆碎片
        state.stage = f"memory_{target}"
        
        # ✅ 用“经历过的任务数 = 成功 + 失败”做记忆编号
        module_count = len(state.modules_repaired) + state.tasks_failed
        if module_count <= 0:
            module_count = 1
        if module_count > 6:
            module_count = 6
        
        # ✅ 直接传入 llm_function（已经是 wrapper，不需要再包一层 lambda）
        memory_text = generate_memory_fragment(
            module_count,
            state.player_name,
            state.modules_repaired,
            llm_function=llm_function,
            game_state=state
        )
        
        messages = [
            {"type": "system", "content": "Memory segments are being activated and played...", "delay": 1000},
            {"type": "system", "content": memory_text, "delay": 2000}
        ]
        messages.extend(MEMORY_INTERPRETATION_OPTIONS)
        
        return {"type": "sequence", "messages": messages}
        
    elif choice in ["B", "OPTION B", "选项B", "NO", "N", "跳过", "否"]:
        return continue_to_next_task(state, target, api_key, llm_function)
    else:
        npc_response = compose_npc_reply(
            "Ask for valid memory choice",
            "Player gave invalid choice for memory fragment. Ask them to choose A (play) or B (skip).",
            state, llm_function, api_key, 40
        )
        return {"type": "npc", "content": npc_response}


def handle_story_choice(state, text, api_key, llm_function):
    from stage_handlers import compose_npc_reply
    
    choice = text.strip().upper()
    target = state.stage.split("_", 1)[1] if "_" in state.stage else "unknown"
    
    if choice in ["A", "OPTION A", "选项A"]:
        state.deviation -= 0.2
        interpretation = "You choose to believe this was a necessary military decision. TZ's logical core is stabilizing."
    elif choice in ["B", "OPTION B", "选项B"]:
        state.deviation += 0.1
        interpretation = "You think there are complex moral considerations. TZ begins to contemplate multiple meanings of the action."
    elif choice in ["C", "OPTION C", "选项C"]:
        state.deviation += 0.3
        interpretation = "You question past decisions. TZ's emotional module shows fluctuations."
    else:
        npc_response = compose_npc_reply(
            "Ask for valid choice",
            "Invalid choice. Ask player to choose A, B, or C for memory interpretation.",
            state, llm_function, api_key, 40
        )
        return {"type": "npc", "content": npc_response}
    
    state.deviation = max(-1.0, min(1.0, state.deviation))
    
    # 下一个阶段
    if target == "amplifier":
        next_stage = "amplifier_task_offer"
        task_name = "Signal Amplifier"
    elif target == "decoder":
        next_stage = "decoder_task_offer"
        task_name = "Data Decryption"
    elif target == "alien_decode":
        next_stage = "alien_decode_task_offer"
        task_name = "Alien Language Decoder"
    elif target == "combat_logic":
        next_stage = "combat_logic_task_offer"
        task_name = "Combat Logic Sequencer"
    elif target == "final":
        next_stage = "final_choice"
        task_name = "Final Choice"
    else:
        next_stage = "amplifier_task_offer"
        task_name = "Signal Amplifier"
    
    # 统一先构建“解释 + 偏差值”两条
    base_messages = [
        {"type": "system", "content": interpretation, "delay": 1000},
        {"type": "system", "content": f"Current deviation value: {state.deviation:.2f}", "delay": 1000}
    ]
    
    if next_stage != "final_choice":
        state.stage = next_stage
        base_messages.append({"type": "system", "content": f"Proceeding to: {task_name}", "delay": 1000})
        base_messages.append({"type": "system", "content": "Ready to begin? (yes/no)", "delay": 1000})
        return {"type": "sequence", "messages": base_messages, "show_quick_buttons": True}
    else:
        # ✅ Final：把上面的两条拼到最终抉择前面
        from task_handlers import start_final_choice
        state.stage = "final_choice"
        final_response = start_final_choice(state, api_key, llm_function)
        
        if final_response.get("type") == "sequence":
            final_response["messages"] = base_messages + final_response["messages"]
        
        return final_response


def continue_to_next_task(state, current_target, api_key, llm_function):
    """跳过记忆后继续下一个任务 - 与 main.py 的 start_next_task 逻辑一致"""
    from stage_handlers import compose_npc_reply
    
    # current_target 本身就代表下一个要进行的任务，不需要映射
    if current_target == "amplifier":
        next_stage = "amplifier_task_offer"
        task_name = "Signal Amplifier"
    elif current_target == "decoder":
        next_stage = "decoder_task_offer"
        task_name = "Data Decryption"
    elif current_target == "alien_decode":
        next_stage = "alien_decode_task_offer"
        task_name = "Alien Language Decoder"
    elif current_target == "combat_logic":
        next_stage = "combat_logic_task_offer"
        task_name = "Combat Logic Sequencer"
    elif current_target == "final":
        next_stage = "final_choice"
        task_name = "Final Choice"
    else:
        next_stage = "amplifier_task_offer"
        task_name = "Signal Amplifier"
    
    state.stage = next_stage
    
    if next_stage == "final_choice":
        # 跳过最后一个记忆后，添加提示消息然后显示最终选择
        final_choice_response = start_final_choice(state, api_key, llm_function)
        
        # 在最终选择消息前添加跳过记忆的提示
        skip_message = {"type": "system", "content": "Skip the memory segment and proceed with the task...", "delay": 1000}
        
        if final_choice_response.get("type") == "sequence":
            final_choice_response["messages"].insert(0, skip_message)
        
        return final_choice_response
    else:
        return {
            "type": "sequence",
            "messages": [
                {"type": "system", "content": f"Skipping memory. Proceeding to next module: {task_name}", "delay": 1000},
                {"type": "system", "content": "Ready to begin? (yes/no)", "delay": 1000}
            ],
            "show_quick_buttons": True
        }


def start_final_choice(state, api_key, llm_function):
    from stage_handlers import compose_npc_reply, CHAPTER_TITLES, FINAL_CHOICE_OPTIONS
    
    state.stage = "final_choice"
    modules_count = len(state.modules_repaired)
    
    # 使用固定的章节4标题和选项（已去除章节标题显示）
    messages = [
        # {"type": "system", "content": CHAPTER_TITLES["chapter4"], "delay": 1000},
        {"type": "system", "content": "All system modules repaired. TZ faces final choice...", "delay": 1000},
        {"type": "system", "content": f"Modules repaired: {modules_count}/5", "delay": 1000},
        {"type": "system", "content": f"Final deviation value: {state.deviation:.2f}", "delay": 1000}
    ]
    
    # 添加NPC对话
    npc_response = compose_npc_reply("Final choice", f"Completed {modules_count} modules, deviation value {state.deviation:.2f}", state, llm_function, api_key, 120)
    messages.append({"type": "npc", "content": npc_response, "delay": 2000})
    
    # 添加固定的最终选项
    messages.extend(FINAL_CHOICE_OPTIONS)
    
    return {"type": "sequence", "messages": messages}


def decide_ending(state):
    modules = len(state.modules_repaired)
    deviation = state.deviation
    
    if modules >= 4 and deviation <= -0.3:
        return "return_to_command"
    elif modules >= 3 and deviation >= 0.5:
        return "awakening_freedom"
    elif modules >= 2 and -0.3 < deviation < 0.5:
        return "coexistence_signal"
    else:
        return "failure_ending"


def show_ending(state, ending, api_key, llm_function):
    from stage_handlers import compose_npc_reply, ENDING_TITLES, EPILOGUE_SEQUENCE
    
    state.stage = "ending"
    
    # 使用固定的结局标题
    ending_title = ENDING_TITLES.get(ending, ENDING_TITLES["failure_ending"])
    
    # 结局描述
    ending_contexts = {
        "return_to_command": "TZ has maintained logical stability throughout repairs. It chooses to return to duty, uploading data to the mothership.",
        "awakening_freedom": "TZ has developed strong emotional awareness and questions its programming. It chooses to transfer its consciousness to seek freedom.",
        "coexistence_signal": "TZ has found balance between logic and emotion. It chooses a middle path, maintaining connection while preserving autonomy.",
        "failure_ending": "System repairs were insufficient. TZ's consciousness fragments. Entering hibernation mode."
    }
    
    context = ending_contexts.get(ending, ending_contexts["failure_ending"])
    npc_response = compose_npc_reply("Final monologue", context, state, llm_function, api_key, 150)
    
    # 统计信息
    stats = f"Modules repaired: {len(state.modules_repaired)}/5\nFinal deviation value: {state.deviation:.2f}"
    
    # 构建消息序列
    messages = [
        {"type": "system", "content": ending_title, "delay": 1000},
        {"type": "system", "content": stats, "delay": 1500},
        {"type": "npc", "content": npc_response, "delay": 2000}
    ]
    
    # 添加尾声
    messages.extend(EPILOGUE_SEQUENCE)
    
    return {"type": "sequence", "messages": messages}
