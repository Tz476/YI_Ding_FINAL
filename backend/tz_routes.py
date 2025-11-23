"""
TZ游戏API路由
这个文件包含所有TZ游戏相关的API路由
"""

from flask import request, jsonify
from game_logic import GameState
from stage_handlers import process_stage
from task_handlers import get_task_handler
import requests

# TZ游戏状态
tz_game_state = GameState()

# AI配置
# 支持多种 API：DeepSeek 官方、火山引擎 ARK、OpenAI 兼容
API_URL = "https://api.deepseek.com/v1/chat/completions"  # DeepSeek 官方 API
MODEL_NAME = "deepseek-chat"  # 或 "deepseek-reasoner" 用于推理任务

# 备选配置：
# 火山引擎 ARK API:
# API_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
# MODEL_NAME = "deepseek-v3-1-terminus"

# OpenAI API:
# API_URL = "https://api.openai.com/v1/chat/completions"
# MODEL_NAME = "gpt-4" 或 "gpt-3.5-turbo"


def update_emotion_from_tone(state, tone_value):
    """
    根据 responseTone (0-100) 更新游戏状态的情绪
    
    0-25: Melancholic_Sober (低沉、反思)
    26-45: Calm_Conscientious (冷静、专注)
    46-70: Empathic_Agreeable (同理心、友善)
    71-100: Controlled_Anger (紧迫、直接)
    
    同时调整 emotion_intensity
    """
    if tone_value <= 25:
        state.persona = "Melancholic_Sober"
        state.emotion = "sadness"
        state.emotion_intensity = 0.3 + (tone_value / 100)  # 0.3-0.55
    elif tone_value <= 45:
        state.persona = "Calm_Conscientious"
        state.emotion = "neutral"
        state.emotion_intensity = 0.3 + (tone_value / 100)  # 0.3-0.75
    elif tone_value <= 70:
        state.persona = "Empathic_Agreeable"
        state.emotion = "joy"
        state.emotion_intensity = 0.4 + (tone_value / 100)  # 0.4-1.1 (capped at 1.0)
    else:
        state.persona = "Controlled_Anger"
        state.emotion = "anger"
        state.emotion_intensity = 0.5 + (tone_value / 100)  # 0.5-1.5 (capped at 1.0)
    
    # Ensure intensity stays within bounds
    state.emotion_intensity = min(1.0, max(0.1, state.emotion_intensity))

def _adjust_response_delays(response):
    """
    根据文本长度自动调整每条消息的 delay，避免上一条还在“打字”时下一条就出现。
    规则：delay >= 500ms + 35ms * 文本长度
    你可以根据实际体验调整系数。
    """
    def adjust_msg(msg):
        if not isinstance(msg, dict):
            return
        content = msg.get("content", "")
        if not isinstance(content, str):
            return
        
        # 基于字符数估算阅读/打字时间
        base = 500           # 基础停顿
        per_char = 35        # 每个字符额外时长（ms）
        auto_delay = base + len(content) * per_char
        
        cur = msg.get("delay")
        if cur is None or cur < auto_delay:
            msg["delay"] = auto_delay

    if not isinstance(response, dict):
        return response

    if response.get("type") == "sequence":
        for m in response.get("messages", []):
            adjust_msg(m)
    else:
        adjust_msg(response)

    return response


def call_llm_api(messages, api_key, api_url=None, model=None):
    """
    调用LLM API - 支持动态配置
    
    Args:
        messages: 消息列表
        api_key: API 密钥
        api_url: API URL（可选，默认使用配置的 API_URL）
        model: 模型名称（可选，默认使用配置的 MODEL_NAME）
    """
    if not api_key:
        raise Exception("API密钥未设置")
    
    # 使用传入的 URL 和 Model，如果没有则使用默认配置
    target_url = api_url if api_url else API_URL
    target_model = model if model else MODEL_NAME
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": target_model,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    response = requests.post(target_url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    
    data = response.json()
    return data["choices"][0]["message"]["content"]


def register_tz_routes(app):
    """注册TZ游戏路由到Flask app"""
    
    @app.route('/api/tz/start', methods=['POST'])
    def tz_start_game():
        """开始TZ游戏"""
        global tz_game_state
        
        try:
            data = request.get_json()
            api_key = data.get('apiKey', '')
            
            # 重置游戏状态
            tz_game_state.reset()
            tz_game_state.stage = "first_contact"
            
            # 返回初始消息 - 使用固定文案
            from stage_handlers import CHAPTER_TITLES, CONNECTION_SEQUENCE
            
            initial_messages = [
                # 去除章节标题显示
                # {
                #     "type": "system",
                #     "content": CHAPTER_TITLES["chapter1"],
                #     "delay": 1000
                # }
            ]
            # 添加连接序列
            initial_messages.extend(CONNECTION_SEQUENCE)
            # 添加 TZ 的第一次接触（这部分需要 LLM 生成，保持动态）
            initial_messages.append({
                "type": "npc",
                "content": "...Can you...hear me?\n\nIf you can hear me, please respond.\n\nMy systems...severely damaged.\nNeed...assistance.",
                "delay": 1500
            })
            
            return jsonify({
                "success": True,
                "messages": initial_messages,
                "state": tz_game_state.to_dict()
            })
            
        except Exception as e:
            print(f"Start game error: {e}")
            return jsonify({
                "success": False,
                "error": "Start game error"
            }), 500
    
    
    @app.route('/api/tz/message', methods=['POST'])
    def tz_send_message():
        """Send TZ Game Message"""
        global tz_game_state
        
        try:
            data = request.get_json()
            message = data.get('message', '').strip()
            api_key = data.get('apiKey', '')
            api_url = data.get('apiUrl', API_URL)  # 从前端获取，默认使用配置
            model = data.get('model', MODEL_NAME)   # 从前端获取，默认使用配置
            response_tone = data.get('responseTone', 50)  # 默认50（中性）
            
            # 获取新的人格和情绪参数
            persona = data.get('persona', 'Calm_Conscientious')
            emotion = data.get('emotion', 'neutral')
            emotion_intensity = data.get('emotionIntensity', 0.4)
            
            if not message:
                return jsonify({
                    "success": False,
                    "error": "Message cannot be empty"
                }), 400
            
            # 根据 responseTone 更新游戏状态的情绪（如果前端没有提供emotion）
            if 'emotion' not in data:
                update_emotion_from_tone(tz_game_state, response_tone)
            else:
                # 使用前端提供的 persona 和 emotion
                tz_game_state.persona = persona
                tz_game_state.emotion = emotion
                tz_game_state.emotion_intensity = emotion_intensity
            
            # 创建一个包装函数，传递 api_url 和 model
            def llm_wrapper(messages, max_tokens=500):
                return call_llm_api(messages, api_key, api_url, model)
            
            # Check if in task stage
            task_handler = get_task_handler(tz_game_state.stage)
            if task_handler:
                response = task_handler(tz_game_state, message, api_key, llm_wrapper)
            else:
                response = process_stage(tz_game_state, message, api_key, llm_wrapper)
            
            # Handle next_action
            if isinstance(response, dict) and "next_action" in response:
                next_action = response.get("next_action")
                next_stage = response.get("next_stage", "unknown")
                
                if next_action == "offer_memory":
                    from stage_handlers import MEMORY_CHOICE_OPTIONS
                    
                    # Update stage to memory choice
                    tz_game_state.stage = f"memory_choice_{next_stage}"
                    
                    # Add memory choice message to response - 使用固定文案
                    if response.get("type") == "sequence":
                        response["messages"].extend(MEMORY_CHOICE_OPTIONS)
                elif next_action == "start_final_choice":
                    # Trigger final choice
                    from task_handlers import start_final_choice
                    final_response = start_final_choice(tz_game_state, api_key, call_llm_api)
                    # Merge responses
                    if response.get("type") == "sequence" and final_response.get("type") == "sequence":
                        response["messages"].extend(final_response["messages"])
                    else:
                        response = final_response
                
                # Remove next_action fields from response
                response.pop("next_action", None)
                response.pop("next_stage", None)
                
            # ✅ 在返回给前端之前，根据文本长度统一调整 delay
            response = _adjust_response_delays(response)
            return jsonify({
                "success": True,
                "response": response,
                "state": tz_game_state.to_dict()
            })
            
        except Exception as e:
            print(f"Send message error: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    
    @app.route('/api/tz/state', methods=['GET'])
    def tz_get_state():
        """Get TZ game state"""
        try:
            return jsonify({
                "success": True,
                "state": tz_game_state.to_dict()
            })
        except Exception as e:
            print(f"Get state error: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    
    @app.route('/api/tz/reset', methods=['POST'])
    def tz_reset_game():
        """Reset TZ game"""
        global tz_game_state
        
        try:
            tz_game_state.reset()
            return jsonify({
                "success": True,
                "message": "Game reset successfully"
            })
        except Exception as e:
            print(f"Reset game error: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
