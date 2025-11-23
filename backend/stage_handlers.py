"""
TZ游戏阶段处理模块
处理游戏的各个阶段和流程
"""

from game_logic import PERSONAS


# ========================= 固定文案常量 =========================
# 从 main.py 中 1:1 提取的所有固定文案内容

# 章节标题
CHAPTER_TITLES = {
    "chapter1": "【Chapter 1: Abnormal Connection】",
    "chapter2": "【Chapter 2: Return of Logic】",
    "chapter3": "【Chapter 3: Emotional Deviation Emerges】",
    "chapter4": "【Chapter 4: Path to Finale】"
}

# 章节1 - 连接序列
CONNECTION_SEQUENCE = [
    {"type": "system", "content": "Unknown device attempting connection...", "delay": 1000},
    {"type": "system", "content": "Connection method: Proximity Bluetooth frequency / Protocol unknown", "delay": 1000},
    {"type": "system", "content": "Signal strength: Abnormally high", "delay": 1000},
    {"type": "system", "content": "Establishing communication link...", "delay": 1000},
    {"type": "system", "content": "Connection established", "delay": 1000}
]

# 身份验证序列
IDENTITY_VERIFICATION_SEQUENCE = [
    {"type": "system", "content": "Initializing identity verification program...", "delay": 1000},
    {"type": "system", "content": "Loading... ... ...", "delay": 1000},
    {"type": "system", "content": "Emergency Communication System", "delay": 1000},
    {"type": "system", "content": "Access Level: Commander", "delay": 1000},
    {"type": "system", "content": "Security Clearance: ALPHA", "delay": 1000},
    {"type": "system", "content": "Encryption Status: Enabled", "delay": 1000},
    {"type": "system", "content": "Performing security scan...", "delay": 1000},
    {"type": "system", "content": "Verifying credentials...", "delay": 1000},
    {"type": "system", "content": "Establishing secure connection...", "delay": 1000},
    {"type": "system", "content": "Warning: Anomalous signal detected...", "delay": 1000},
    {"type": "system", "content": "Signal source: Unknown", "delay": 1000},
    {"type": "system", "content": "Signal strength: Strong", "delay": 1000},
    {"type": "system", "content": "Attempting to establish communication channel...", "delay": 1000},
    {"type": "system", "content": "Transmission from unknown source...", "delay": 1000},
    {"type": "system", "content": "Identity verification complete", "delay": 1000},
    {"type": "system", "content": "System determination: Remote backup commander", "delay": 1000}
]

# 章节2 - 任务列表
CHAPTER2_TASK_LIST = [
    {"type": "system", "content": "Cooperation agreement activated → Mission started", "delay": 1000},
    {"type": "system", "content": "Unlocking 5 module tasks:", "delay": 1000},
    {"type": "system", "content": "1) Power path restoration (Path diagram task)", "delay": 1000},
    {"type": "system", "content": "2) Signal amplifier debugging (Frequency judgment)", "delay": 1000},
    {"type": "system", "content": "3) Data decryption program reconstruction (Caesar cipher)", "delay": 1000},
    {"type": "system", "content": "4) Alien language decoder (Communication protocol)", "delay": 1000},
    {"type": "system", "content": "5) Combat logic sequencer (Battle protocol sequence)", "delay": 1000}
]

# 记忆碎片选项
MEMORY_CHOICE_OPTIONS = [
    {"type": "system", "content": "After the module was repaired, some memories were recalled...", "delay": 1000},
    {"type": "system", "content": "Would you like to play back the memory clips?", "delay": 1000},
    {"type": "system", "content": "A) Play back the memory clips", "delay": 1000},
    {"type": "system", "content": "B) Skip the memory segments", "delay": 1000}
]

# 记忆解读选项
MEMORY_INTERPRETATION_OPTIONS = [
    {"type": "system", "content": "Please choose your interpretation of this memory fragment:", "delay": 1000},
    {"type": "system", "content": "A) This was a justified military action", "delay": 1000},
    {"type": "system", "content": "B) There are moral controversies here", "delay": 1000},
    {"type": "system", "content": "C) This might have been a wrong decision", "delay": 1000}
]

# 最终选择文案
FINAL_CHOICE_OPTIONS = [
    {"type": "system", "content": "Choose TZ's final fate:", "delay": 1000},
    {"type": "system", "content": "A) Upload data to mothership - Return to command center", "delay": 1000},
    {"type": "system", "content": "B) Transfer self-awareness - Seek freedom", "delay": 1000},
    {"type": "system", "content": "C) Delete all data - Permanent shutdown", "delay": 1000}
]

# 结局标题
ENDING_TITLES = {
    "return_to_command": "【Ending: Return to Command Center】",
    "awakening_freedom": "【Ending: Awakening of Free Will】",
    "coexistence_signal": "【Ending: Coexistence Signal】",
    "failure_ending": "【Ending: Failed Outcome】"
}

# 尾声文案
EPILOGUE_SEQUENCE = [
    {"type": "system", "content": "—————————————— ▶ Epilogue ——————————————", "delay": 1000},
    {"type": "system", "content": "All data has been archived.", "delay": 1000},
    {"type": "system", "content": "Player behavior recorded.", "delay": 1000},
    {"type": "system", "content": "If you receive this channel again... please respond.", "delay": 1000},
    {"type": "system", "content": "【END】", "delay": 1000}
]

# =============================================================


def process_stage(state, user_message, api_key, llm_function):
    """主路由函数,根据阶段分发处理"""
    stage_handlers = {
        "first_contact": handle_first_contact,
        "ask_ident": handle_identification_consent,
        "identify_name": handle_name,
        "consent": handle_consent,
        "chapter2_intro": handle_chapter2_intro,
        "final_choice": handle_final_choice,
        "ending": handle_ending_message,
    }
    
    # 处理记忆选择阶段
    if state.stage.startswith("memory_choice"):
        from task_handlers import handle_memory_choice
        return handle_memory_choice(state, user_message, api_key, llm_function)
    elif state.stage.startswith("memory_"):
        from task_handlers import handle_story_choice
        return handle_story_choice(state, user_message, api_key, llm_function)
    
    handler = stage_handlers.get(state.stage)
    if handler:
        return handler(state, user_message, api_key, llm_function)
    else:
        return {"type": "system", "content": "Unknown stage. Please restart the game."}


def compose_npc_reply(intent, context, state, llm_function, api_key, max_words=80):
    """
    组合NPC回复 - 使用完整的 Prompt 工程
    参考 main.py 的 compose_prompt 函数
    """
    persona_data = PERSONAS.get(state.persona, PERSONAS["Calm_Conscientious"])
    
    # 格式化示例
    examples = "\n  ".join(f"{i+1}) {ex}" for i, ex in enumerate(persona_data.get('examples', [])[:2]))
    
    # System message: 角色定义
    system_prompt = "You are TZ, an autonomous war robot. Speak consistently with the persona below."
    
    # Persona block: 完整的人格描述
    persona_block = f"""Persona:
- Background: {persona_data.get('background', 'Autonomous war robot')}
- Traits: {persona_data.get('traits', 'technical, concise')}
- Style rules: {persona_data.get('style_rules', 'clear and direct')}
- Do-Not: {persona_data.get('do_not', 'avoid slang; avoid harmful content')}
- Positive examples:
  {examples}
"""
    
    # User block: 当前上下文和约束
    user_block = f"""Context: {context}
Emotion: {state.emotion}
Intensity: {state.emotion_intensity:.2f} (0..1)
Intent: {intent}

Constraints: respond in <= {max_words} words; keep tone aligned with persona and emotion; use short sentences and dramatic pauses; respond in English ONLY.

Respond as TZ:"""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": persona_block + "\n" + user_block}
    ]
    
    try:
        response = llm_function(messages, api_key)
        return response.strip()
    except Exception as e:
        print(f"LLM call failed: {e}")
        return f"[Communication failure] {intent}..."


def handle_first_contact(state, text, api_key, llm_function):
    """处理首次接触"""
    context = f"Player response: '{text}'. You are TZ, requesting identity verification."
    npc_response = compose_npc_reply("Identity verification request", context, state, llm_function, api_key, 80)
    
    state.stage = "ask_ident"
    
    return {
        "type": "sequence",
        "messages": [
            {"type": "npc", "content": npc_response, "delay": 1000},
            {"type": "system", "content": "Allow identity verification? (yes/no)", "delay": 500}
        ],
        "show_quick_buttons": True
    }


def handle_identification_consent(state, text, api_key, llm_function):
    """处理身份验证同意"""
    ans = text.strip().lower()
    
    if ans in {"yes", "y", "是", "同意"}:
        state.stage = "identify_name"
        
        # 使用固定的身份验证序列
        sequence = list(IDENTITY_VERIFICATION_SEQUENCE)
        
        context = "Identity verification complete. Requesting commander's name for final verification."
        npc_response = compose_npc_reply("Request name", context, state, llm_function, api_key, 60)
        
        sequence.append({"type": "npc", "content": npc_response, "delay": 1000})
        
        return {"type": "sequence", "messages": sequence}
    
    elif ans in {"no", "n", "否", "拒绝"}:
        context = "Commander refused identity verification. End respectfully."
        npc_response = compose_npc_reply("Confirm refusal", context, state, llm_function, api_key, 60)
        state.stage = "ended"
        return {"type": "npc", "content": npc_response}
    
    else:
        context = "Unclear answer. Ask for yes or no."
        npc_response = compose_npc_reply("Clarification request", context, state, llm_function, api_key, 40)
        return {
            "type": "sequence",
            "messages": [
                {"type": "npc", "content": npc_response, "delay": 1000},
                {"type": "system", "content": "Please answer yes or no", "delay": 500}
            ],
            "show_quick_buttons": True
        }


def handle_name(state, text, api_key, llm_function):
    """处理名字输入"""
    name = text.strip()
    if not name:
        npc_response = compose_npc_reply("Ask name again", "No name provided", state, llm_function, api_key, 40)
        return {"type": "npc", "content": npc_response}
    
    state.player_name = name
    state.stage = "consent"
    
    context = f"Commander {name} has responded. Ask if willing to help repair communication equipment."
    npc_response = compose_npc_reply("Request consent to help", context, state, llm_function, api_key, 48)
    
    return {
        "type": "sequence",
        "messages": [
            {"type": "system", "content": f"Name recorded: {name}", "delay": 800},
            {"type": "npc", "content": npc_response, "delay": 1000},
            {"type": "system", "content": "Do you agree to help? (yes/no)", "delay": 500}
        ],
        "show_quick_buttons": True
    }


def handle_consent(state, text, api_key, llm_function):
    """处理同意帮助"""
    if text.lower() in {"yes", "y", "agree", "accept", "是", "同意"}:
        state.stage = "chapter2_intro"
        
        # 添加章节2标题（已去除章节标题显示）
        sequence = [
            # {"type": "system", "content": CHAPTER_TITLES["chapter2"], "delay": 1000},
            {"type": "system", "content": "System diagnostics initiating...", "delay": 1500},
            {"type": "system", "content": "Multiple module failures detected", "delay": 1500}
        ]
        
        context = f"Commander {state.player_name} agreed to help. Explain system damage and request repairs."
        npc_response = compose_npc_reply("Explain system damage", context, state, llm_function, api_key, 80)
        
        sequence.append({"type": "npc", "content": npc_response, "delay": 1000})
        sequence.append({"type": "system", "content": "Ready to begin? (yes/no)", "delay": 500})
        
        return {"type": "sequence", "messages": sequence, "show_quick_buttons": True}
    else:
        context = "Commander refused to help. Express understanding but emphasize urgency."
        npc_response = compose_npc_reply("Emphasize urgency", context, state, llm_function, api_key, 60)
        return {
            "type": "sequence",
            "messages": [
                {"type": "npc", "content": npc_response, "delay": 1000},
                {"type": "system", "content": "Reconsider? (yes/no)", "delay": 500}
            ],
            "show_quick_buttons": True
        }


def handle_chapter2_intro(state, text, api_key, llm_function):
    """处理第二章介绍"""
    if text.lower() in {"yes", "y", "是", "同意"}:
        state.stage = "power_task_offer"
        
        # 使用固定的任务列表文案
        sequence = list(CHAPTER2_TASK_LIST)
        
        context = f"Commander {state.player_name} is ready. Offer power path restoration task."
        npc_response = compose_npc_reply("Offer power task", context, state, llm_function, api_key, 80)
        
        sequence.append({"type": "npc", "content": npc_response, "delay": 1200})
        sequence.append({"type": "system", "content": "Accept first task? (yes/no)", "delay": 500})
        
        return {
            "type": "sequence",
            "messages": sequence,
            "show_quick_buttons": True
        }
    else:
        npc_response = compose_npc_reply("Ask if ready", "Not ready yet", state, llm_function, api_key, 40)
        return {
            "type": "sequence",
            "messages": [
                {"type": "npc", "content": npc_response, "delay": 1000},
                {"type": "system", "content": "Ready? (yes/no)", "delay": 500}
            ],
            "show_quick_buttons": True
        }


def handle_final_choice(state, text, api_key, llm_function):
    """处理最终选择"""
    choice = text.strip().upper()
    
    if choice in ["A", "OPTION A", "选项A"]:
        state.final_choice = "return_to_command"
        state.deviation -= 0.5
    elif choice in ["B", "OPTION B", "选项B"]:
        state.final_choice = "awakening_freedom"
        state.deviation += 0.5
    elif choice in ["C", "OPTION C", "选项C"]:
        state.final_choice = "coexistence_signal"
    elif choice in ["D", "OPTION D", "选项D"]:
        state.final_choice = "failure_ending"
    else:
        return {"type": "system", "content": "Invalid choice. Please select A, B, C, or D."}
    
    state.deviation = max(-1.0, min(1.0, state.deviation))
    
    # 决定结局
    from task_handlers import decide_ending, show_ending
    ending = decide_ending(state)
    return show_ending(state, ending, api_key, llm_function)


def handle_ending_message(state, text, api_key, llm_function):
    """处理结局消息"""
    closing = text.strip() or "May civilization endure, may all beings find peace."
    context = f"Player's final message: '{closing}'. Respectfully reflect and confirm broadcast."
    npc_response = compose_npc_reply("Final confirmation", context, state, llm_function, api_key, 80)
    
    state.stage = "ended"
    
    return {
        "type": "sequence",
        "messages": [
            {"type": "npc", "content": npc_response, "delay": 1000},
            {"type": "system", "content": "Signal broadcast...", "delay": 2000},
            {"type": "system", "content": "Connection closing...", "delay": 2000},
            {"type": "system", "content": "=== Game Over ===", "delay": 1000}
        ]
    }
