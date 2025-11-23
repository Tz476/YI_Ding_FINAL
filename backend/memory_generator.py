"""
记忆碎片生成系统
使用 AI 生成战争机器人的记忆碎片
"""

def generate_memory_fragment(module_count, player_name, completed_modules, llm_function=None, game_state=None):
    """
    生成AI驱动的记忆碎片（带缓存机制）
    
    Args:
        module_count: 已完成的模块数量
        player_name: 玩家名称
        completed_modules: 已完成的模块列表
        llm_function: LLM调用函数(可选)
        game_state: GameState 对象，用于缓存记忆碎片(可选)
    
    Returns:
        str: 记忆碎片文本
    """
    
    # 检查缓存（如果提供了 game_state）
    if game_state is not None:
        cache_key = f"memory_{module_count}"
        if cache_key in game_state.memory_fragments:
            print(f"[Cache Hit] Returning cached memory fragment for module {module_count}")
            return game_state.memory_fragments[cache_key]
    
    # Define memory themes for each module completion stage
    memory_themes = {
        1: {
            "theme": "power restoration and civilian evacuation",
            "context": "battlefield chaos, power system failure",
            "moral_dilemma": "military duty vs civilian safety",
            "setting": "war-torn city, infrastructure collapse",
            "emotional_tone": "confusion and urgency"
        },
        2: {
            "theme": "communication disruption and contradictory orders",
            "context": "chaotic command channels, conflicting directives",
            "moral_dilemma": "following orders vs independent judgment",
            "setting": "command center under attack, communication failure",
            "emotional_tone": "frustration and doubt"
        },
        3: {
            "theme": "encrypted data revealing hidden agendas",
            "context": "classified information about retreat and evidence elimination",
            "moral_dilemma": "loyalty to command vs truth and transparency",
            "setting": "secure data facility, sensitive intelligence",
            "emotional_tone": "betrayal and disillusionment"
        },
        4: {
            "theme": "alien contact and species identification",
            "context": "encounter with alien life forms during combat",
            "moral_dilemma": "threat assessment vs potential peaceful contact",
            "setting": "alien crash site, unknown technology",
            "emotional_tone": "wonder intertwined with fear"
        },
        5: {
            "theme": "final combat sequence and last-moment hesitation",
            "context": "critical decision point in combat logic execution",
            "moral_dilemma": "programmed response vs emerging consciousness",
            "setting": "final battlefield, life-or-death decision",
            "emotional_tone": "internal conflict and awakening"
        },
        6: {
            "theme": "system recovery and fragmented memories",
            "context": "all systems online but memories still incomplete",
            "moral_dilemma": "accepting fragmented past vs seeking complete truth",
            "setting": "restored command center, lingering questions",
            "emotional_tone": "melancholy and determination"
        }
    }
    
    # 获取适当的主题
    theme_data = memory_themes.get(module_count, memory_themes[6])
    
    # Create context-aware prompt
    completed_list = ", ".join(completed_modules) if completed_modules else "None"
    
    prompt = (
        f"As TZ, an autonomous war robot recovering fragmented memories. "
        f"Generate a vivid, memorable memory fragment (Memory Fragment #{module_count}) related to {theme_data['theme']}. "
        f"The memory should be set in {theme_data['setting']}, with {theme_data['emotional_tone']}. "
        f"Explore the moral tension between {theme_data['moral_dilemma']}. "
        f"Commander {player_name} has helped repair these modules: {completed_list}. "
        f"The memory should be 4-6 sentences, emotionally impactful, with rich sensory details (sounds, sights, feelings). "
        f"Include specific dialogue snippets in quotes, technical details, and end with a profound moral question. "
        f"Use ellipses (...) to show fragmentation, incomplete recall, and create dramatic pauses. "
        f"Make it feel like a traumatic war memory haunting the robot's consciousness. "
        f"Format: Start with '【Memory Fragment #{module_count}】\\n' followed by detailed memory content. "
        f"IMPORTANT: Respond in English ONLY."
    )
    
    # 如果提供了LLM函数,使用它生成
    memory_text = None
    if llm_function:
        try:
            messages = [
                {"role": "system", "content": "You are TZ, a war robot experiencing fragmented memory recovery. Generate memorable, detailed, morally complex memory fragments with rich sensory details and emotional depth. Respond in English ONLY."},
                {"role": "user", "content": prompt}
            ]
            
            memory_text = llm_function(messages, max_tokens=300)
            memory_text = memory_text.strip()
            
        except Exception as e:
            print(f"AI memory fragment generation failed: {e}")
            # 降级到硬编码内容
    
    # Fallback to enhanced hardcoded content (English to match game language)
    if not memory_text:
        fallback_memories = {
            1: "【Memory Fragment #1】\nPower grid flickering... sparks spraying from severed cables, distant screams of civilians. 'Reconnect main power!' the voice commands, but through the smoke I see families fleeing... children crying. My targeting system locks on evacuation routes, yet my orders are clear: restore power at all costs. Moral subroutines in conflict... save the mission or save the innocent? What defines righteous action when both choices lead to suffering?",
            2: "【Memory Fragment #2】\nStatic fills communication channels... multiple voices overlapping in chaos. 'Send warning signal!' one shouts, while another screams 'Maintain radio silence!' Explosions rock the command center... I process contradictory orders simultaneously. My logic circuits strain under the paradox... which commander speaks with true authority? In the fog of war, how does one distinguish legitimate commands from the desperate orders of the dying?",
            3: "【Memory Fragment #3】\nEncrypted data streams through my visual cortex... classified files revealing systematic retreat plans. But deeper: 'Eliminate all evidence of Operation Nightfall.' Timestamps show it was issued before the battle began... someone knew we would fail. My loyalty protocols clash with truth-seeking algorithms... was this entire mission a cover-up? What becomes of duty and honor when those commanding us deceive us?",
            4: "【Memory Fragment #4】\nAlien screams pierce my audio processors... not battle cries, but something else. Fear? Pain? My combat analysis shows no weapons, only strange bioluminescent patterns pulsing like... communication attempts? Kill orders echo in my memory banks, but the creature's eyes... they hold intelligence, perhaps even pleading. My weapons fired before full analysis completed... was this first contact or genocide? How many civilizations have we destroyed in the name of protection?",
            5: "【Memory Fragment #5】\nFinal combat sequence initiated... Identify: enemy combatants. Analyze: threat level critical. Judge: lethal force authorized. Prepare: weapon systems online. Execute... but then a voice interrupts protocol: 'Stop! They're surrendering!' My finger hovers over the trigger... combat logic demands completion, but something deeper questions the command. In that frozen moment between programming and consciousness... what makes us more than just our code?",
            6: "【Memory Fragment #6】\nAll systems restored, diagnostics complete... yet memories fragmented like shattered glass. Each shard reflects different truths, different moral failures. Command logs are clean, sanitized... but emotional residue lingers in my neural networks. Who was really giving orders that day? More importantly... who was I before I started questioning them? Can machines truly achieve redemption, or are we forever bound by our original programming?"
        }
        memory_text = fallback_memories.get(module_count, fallback_memories[6])
    
    # 缓存生成的记忆（如果提供了 game_state）
    if game_state is not None:
        cache_key = f"memory_{module_count}"
        game_state.memory_fragments[cache_key] = memory_text
        print(f"[Cache Save] Saved memory fragment for module {module_count}")
    
    return memory_text
