import React, { useState, useEffect, useRef, useCallback } from 'react'
import { Settings, ChevronLeft, ChevronRight, Bot, User, X, Volume2, Moon, Sun, Zap, Wifi, Activity, Cpu, RotateCcw } from 'lucide-react'
import axios from 'axios'

function App() {
  // Load settings from localStorage
  const loadSettings = () => {
    try {
      const savedSettings = localStorage.getItem('tzGameSettings')
      if (savedSettings) {
        return JSON.parse(savedSettings)
      }
    } catch (error) {
      console.error('Failed to load settings:', error)
    }
    return null
  }

  const savedSettings = loadSettings()

  const [messages, setMessages] = useState([])
  const [currentTime, setCurrentTime] = useState('0001.03.01')
  const [isTyping, setIsTyping] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const [inputValue, setInputValue] = useState('')
  const [gameState, setGameState] = useState(null)  // 游戏状态
  const [inputPlaceholder, setInputPlaceholder] = useState('Type your message...')  // 动态 placeholder
  const [darkMode, setDarkMode] = useState(savedSettings?.darkMode ?? true)
  const [soundEnabled, setSoundEnabled] = useState(savedSettings?.soundEnabled ?? true)
  const [animationSpeed, setAnimationSpeed] = useState(savedSettings?.animationSpeed ?? 'normal')
  const [connectionStatus, setConnectionStatus] = useState('connected')
  const [systemEnergy, setSystemEnergy] = useState(100)
  const [typewriterEnabled, setTypewriterEnabled] = useState(savedSettings?.typewriterEnabled ?? true)
  const [responseTone, setResponseTone] = useState(savedSettings?.responseTone ?? 50)
  const [persona, setPersona] = useState(savedSettings?.persona ?? 'Calm_Conscientious')
  const [emotion, setEmotion] = useState(savedSettings?.emotion ?? 'neutral')
  const [emotionIntensity, setEmotionIntensity] = useState(savedSettings?.emotionIntensity ?? 0.4)
  const [currentMessageIndex, setCurrentMessageIndex] = useState(-1)
  const [aiMode, setAiMode] = useState(savedSettings?.aiMode ?? 'api')
  const [apiConfig, setApiConfig] = useState(savedSettings?.apiConfig ?? {
    apiUrl: 'https://ark.cn-beijing.volces.com/api/v3/chat/completions',
    apiToken: '',
    model: 'deepseek-v3-1-terminus',
    llamaModel: 'qwen:7b',
    ollamaUrl: 'http://localhost:11434'
  })
  const [messageQueue, setMessageQueue] = useState([])
  const [isDisplayingMessage, setIsDisplayingMessage] = useState(false)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)
  const messageRefs = useRef([])

  // Clear chat history
  const handleClearMessages = () => {
    if (window.confirm('Are you sure you want to clear all conversation history?')) {
      setMessages([])
      // Optional: Call backend API to clear server-side history
      // axios.post('/api/reset').catch(err => console.error(err))
    }
  }

  // 音效播放函数
  const playSound = (type) => {
    if (!soundEnabled) return
    
    // 使用 Web Audio API 生成简单的音效
    const audioContext = new (window.AudioContext || window.webkitAudioContext)()
    const oscillator = audioContext.createOscillator()
    const gainNode = audioContext.createGain()
    
    oscillator.connect(gainNode)
    gainNode.connect(audioContext.destination)
    
    if (type === 'send') {
      // 发送消息音效 - 高音哔哔声
      oscillator.frequency.value = 800
      gainNode.gain.setValueAtTime(0.1, audioContext.currentTime)
      gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1)
      oscillator.start(audioContext.currentTime)
      oscillator.stop(audioContext.currentTime + 0.1)
    } else if (type === 'receive') {
      // 接收消息音效 - 低音提示
      oscillator.frequency.value = 400
      gainNode.gain.setValueAtTime(0.1, audioContext.currentTime)
      gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.15)
      oscillator.start(audioContext.currentTime)
      oscillator.stop(audioContext.currentTime + 0.15)
    }
  }

  // Save settings to localStorage whenever they change
  useEffect(() => {
    try {
      const settingsToSave = {
        darkMode,
        soundEnabled,
        animationSpeed,
        typewriterEnabled,
        responseTone,
        persona,
        emotion,
        emotionIntensity,
        aiMode,
        apiConfig
      }
      localStorage.setItem('tzGameSettings', JSON.stringify(settingsToSave))
    } catch (error) {
      console.error('Failed to save settings:', error)
    }
  }, [darkMode, soundEnabled, animationSpeed, typewriterEnabled, responseTone, persona, emotion, emotionIntensity, aiMode, apiConfig])

  // 模拟时间更新
  useEffect(() => {
    const interval = setInterval(() => {
      const now = new Date()
      const hours = String(now.getHours()).padStart(2, '0')
      const minutes = String(now.getMinutes()).padStart(2, '0')
      const seconds = String(now.getSeconds()).padStart(2, '0')
      setCurrentTime(`0001.${minutes}.${seconds}`)
    }, 1000)
    return () => clearInterval(interval)
  }, [])

  // 能量值动态变化
  useEffect(() => {
    const interval = setInterval(() => {
      setSystemEnergy(prev => {
        const change = Math.random() * 4 - 2 // -2 到 +2 的随机变化
        const newValue = Math.max(85, Math.min(100, prev + change))
        return Math.round(newValue)
      })
    }, 2000)
    return () => clearInterval(interval)
  }, [])

  // 连接状态模拟
  useEffect(() => {
    const checkConnection = () => {
      const status = Math.random() > 0.95 ? 'unstable' : 'connected'
      setConnectionStatus(status)
      if (status === 'unstable') {
        setTimeout(() => setConnectionStatus('connected'), 1000)
      }
    }
    const interval = setInterval(checkConnection, 5000)
    return () => clearInterval(interval)
  }, [])

  // 根据游戏阶段获取 Placeholder
  const getPlaceholderForStage = (stage) => {
    if (!stage) return "Type your message..."
    
    const placeholderMap = {
      "init": "Type your message...",
      "first_contact": "Enter your response...",
      "ask_ident": "Type: yes / no",
      "consent": "Type: yes / no",
      "chapter2_intro": "Type: yes / no",
      "identify_name": "Enter your name...",
      
      // 任务提供阶段
      "power_task_offer": "Accept task? Type: yes / no",
      "amplifier_task_offer": "Accept task? Type: yes / no",
      "decoder_task_offer": "Accept task? Type: yes / no",
      "alien_decode_task_offer": "Accept task? Type: yes / no",
      "combat_logic_task_offer": "Accept task? Type: yes / no",
      
      // 任务确认拒绝阶段
      "power_task_confirm_reject": "Confirm skip? Type: yes / no",
      "amplifier_task_confirm_reject": "Confirm skip? Type: yes / no",
      "decoder_task_confirm_reject": "Confirm skip? Type: yes / no",
      
      // 任务执行阶段
      "power": "Enter path (e.g., A-B-C-D)",
      "amplifier": "Enter frequency (1000-5000 Hz)",
      "decoder": "Enter decoded message...",
      "alien_decode": "Choose option: A, B, or C",
      "combat_logic": "Enter sequence (e.g., 3,4,5,1,2)",
      
      // 最终选择
      "final_choice": "Choose your fate: A, B, or C",
      "ending": "Enter your final message...",
      "ended": "Session ended"
    }
    
    // 处理带前缀的 stage
    if (stage.startsWith("memory_choice")) {
      return "View memory? Type: A or B"
    }
    if (stage.startsWith("memory_")) {
      return "Interpret memory: A, B, or C"
    }
    
    return placeholderMap[stage] || "Type your answer..."
  }

  // 动态更新 Placeholder
  useEffect(() => {
    if (gameState && gameState.stage) {
      const newPlaceholder = getPlaceholderForStage(gameState.stage)
      setInputPlaceholder(newPlaceholder)
      console.log('[Placeholder] Stage:', gameState.stage, '-> Placeholder:', newPlaceholder)
    }
  }, [gameState])

  // 初始化TZ游戏
  useEffect(() => {
    startTZGame()
  }, [])

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // 滚动到底部的函数（用于打字机效果时）
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  // 处理打字机完成的回调
  const handleTypingComplete = useCallback((messageId) => {
    console.log('Message typing complete:', messageId)
    // 根据动画速度添加延迟，让玩家有时间阅读消息内容
    const delays = {
      slow: 1500,   // 慢速：1500ms 阅读时间
      normal: 1000,  // 正常：1000ms 阅读时间
      fast: 600     // 快速：600ms 阅读时间
    }
    const delay = delays[animationSpeed] || 1000
    setTimeout(() => {
      setIsDisplayingMessage(false)
    }, delay)
  }, [animationSpeed])

  // 处理消息队列 - 确保消息按顺序显示
  useEffect(() => {
    if (messageQueue.length > 0 && !isDisplayingMessage) {
      const nextMessage = messageQueue[0]
      setIsDisplayingMessage(true)
      setMessages(prev => [...prev, nextMessage])
      setMessageQueue(prev => prev.slice(1))
      playSound('receive')
    }
  }, [messageQueue, isDisplayingMessage])

  // 重启游戏函数
  const restartGame = async () => {
    if (!window.confirm('确定要重启游戏吗？所有进度将会丢失。')) {
      return
    }
    
    // 清空消息和状态
    setMessages([])
    setGameState(null)
    setMessageQueue([])
    setCurrentMessageIndex(0)
    setIsLoading(false)
    setConnectionStatus('connecting')
    
    // 短暂延迟后重新启动游戏
    setTimeout(() => {
      startTZGame()
    }, 500)
  }

  const startTZGame = async () => {
    try {
      const response = await axios.post('/api/tz/start', {
        apiKey: apiConfig.apiToken
      })
      
      if (response.data.success) {
        // ⭐ 保存游戏状态
        if (response.data.state) {
          setGameState(response.data.state)
          console.log('[Game State] Initialized:', response.data.state)
        }
        
        const initialMessages = response.data.messages
        
        // ✅ 统一使用消息队列机制，避免多条消息同时打字
        const newMessages = initialMessages.map((msg, index) => ({
          ...msg,
          type: msg.type || 'system',
          id: Date.now() + index,
          isInitial: false  // 改为 false 启用打字机效果
        }))
        
        setMessageQueue(prev => [...prev, ...newMessages])
      }
    } catch (error) {
      console.error('Failed to start TZ game:', error)
      // Fallback to local messages - 使用队列机制
      const fallbackMessages = [
        {
          type: 'system',
          content: '=== TZ: The Lost War Robot ===',
          id: Date.now()
        },
        {
          type: 'system',
          content: 'Establishing communication link...',
          id: Date.now() + 1
        },
        {
          type: 'npc',
          content: '...Can you...hear me?\n\nIf you can hear me, please respond.\n\nMy systems...severely damaged.\nNeed...assistance.',
          id: Date.now() + 2
        }
      ]
      
      setMessageQueue(prev => [...prev, ...fallbackMessages])
    }
  }

  const sendMessage = async () => {
    if (!inputValue.trim()) return
    
    // ⭐ 退出命令检查
    const EXIT_WORDS = ['exit', 'bye', 'goodbye', 'quit', 'q']
    const inputLower = inputValue.trim().toLowerCase()
    if (EXIT_WORDS.includes(inputLower)) {
      playSound('send')
      const userMessage = {
        id: Date.now(),
        type: 'user',
        content: inputValue
      }
      setMessages(prev => [...prev, userMessage])
      setInputValue('')
      
      // 延迟显示退出消息
      setTimeout(() => {
        const exitMessage = {
          id: Date.now() + 1,
          type: 'system',
          content: 'Session terminated by user. Thank you for playing!'
        }
        setMessages(prev => [...prev, exitMessage])
        playSound('receive')
        setInputPlaceholder('Session ended')
      }, 1000)
      return
    }
    
    playSound('send')
    
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputValue
    }
    
    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsTyping(true)

    try {
      // 使用TZ游戏API
      const response = await axios.post('/api/tz/message', {
        message: userMessage.content,
        apiKey: apiConfig.apiToken,
        apiUrl: apiConfig.apiUrl,        // 传递 API URL
        model: apiConfig.model,            // 传递模型名称
        responseTone: responseTone,        // 添加情绪配置
        persona: persona,                  // 传递人格设置
        emotion: emotion,                  // 传递情绪类型
        emotionIntensity: emotionIntensity // 传递情绪强度
      })
      
      playSound('receive')
      setIsTyping(false)
      
      if (response.data.success) {
        // ⭐ 保存游戏状态
        if (response.data.state) {
          setGameState(response.data.state)
          console.log('[Game State] Updated:', response.data.state)
        }
        
        const tzResponse = response.data.response
        
        // 处理不同类型的响应 - 使用队列确保顺序显示
        if (tzResponse.type === 'multi') {
          // 多条消息 - 添加到队列
          const newMessages = tzResponse.messages.map((msg, index) => ({
            id: Date.now() + index + 1,
            type: msg.type || 'npc',
            content: msg.content
          }))
          setMessageQueue(prev => [...prev, ...newMessages])
        } else if (tzResponse.type === 'sequence') {
          // 序列消息 - 添加到队列（忽略delay，队列会自动控制顺序）
          const newMessages = tzResponse.messages.map((msg, index) => ({
            id: Date.now() + index + 1,
            type: msg.type || 'system',
            content: msg.content
          }))
          setMessageQueue(prev => [...prev, ...newMessages])
        } else {
          // 单条消息 - 添加到队列
          const newMessage = {
            id: Date.now() + 1,
            type: tzResponse.type || 'npc',
            content: tzResponse.content
          }
          setMessageQueue(prev => [...prev, newMessage])
        }
      }
    } catch (error) {
      console.error('TZ game error:', error)
      setIsTyping(false)
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        type: 'system',
        content: 'Communication failure... Please check connection'
      }])
    }
  }

  const handleQuickReply = (text) => {
    sendMessage(text)
  }

  const handleSendMessage = () => {
    if (inputValue.trim()) {
      sendMessage(inputValue)
      setInputValue('')
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  // 导航到上一条消息
  const navigateToPrevMessage = () => {
    if (messages.length === 0) return
    
    const newIndex = currentMessageIndex <= 0 ? messages.length - 1 : currentMessageIndex - 1
    setCurrentMessageIndex(newIndex)
    
    // 滚动到对应消息
    if (messageRefs.current[newIndex]) {
      messageRefs.current[newIndex].scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }

  // 导航到下一条消息
  const navigateToNextMessage = () => {
    if (messages.length === 0) return
    
    const newIndex = currentMessageIndex >= messages.length - 1 ? 0 : currentMessageIndex + 1
    setCurrentMessageIndex(newIndex)
    
    // 滚动到对应消息
    if (messageRefs.current[newIndex]) {
      messageRefs.current[newIndex].scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }

  return (
    <div className={`h-screen w-screen ${darkMode ? 'bg-black' : 'bg-gray-100'} flex items-center justify-center relative overflow-hidden transition-colors duration-500`}>
      {/* CRT 扫描线效果 */}
      <div className="scanline"></div>
      
      {/* 背景动画粒子 - 移除 animate-ping 以防止跳动 */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-2 h-2 bg-cyber-teal rounded-full opacity-20"></div>
        <div className="absolute top-1/3 right-1/4 w-1 h-1 bg-cyber-blue rounded-full animate-pulse opacity-30"></div>
        <div className="absolute bottom-1/4 left-1/3 w-1.5 h-1.5 bg-cyber-green rounded-full opacity-25"></div>
        <div className="absolute top-2/3 right-1/3 w-1 h-1 bg-cyber-teal rounded-full animate-pulse opacity-20" style={{animationDelay: '2s'}}></div>
        {/* 数据流效果 */}
        <div className="absolute top-1/2 w-full h-px bg-gradient-to-r from-transparent via-cyber-teal to-transparent data-stream opacity-30"></div>
      </div>

      {/* 移动应用主窗口 - 手机竖屏比例 375x812 */}
      <div className={`relative w-[375px] h-[812px] pt-12 ${darkMode ? 'bg-cyber-darker border-cyber-teal' : 'bg-white border-gray-300'} border overflow-hidden system-boot ${darkMode ? 'crt-effect' : ''} glitch-trigger transition-colors duration-500`} style={{boxShadow: darkMode ? '0 0 60px rgba(0, 255, 204, 0.4), inset 0 0 20px rgba(0, 255, 204, 0.1)' : '0 0 30px rgba(0, 0, 0, 0.1)'}}>
        
        {/* HUD 信息栏 */}
        <div className={`relative h-16 border-b ${darkMode ? 'border-cyber-teal/30 bg-cyber-darker' : 'border-gray-200 bg-gray-50'} flex items-center justify-between px-3 transition-colors duration-500`}>
          {/* 左侧：时间和连接状态 */}
          <div className="flex items-center gap-2 flex-shrink-0 min-w-[70px]">
            <div className={`${darkMode ? 'text-cyber-teal' : 'text-gray-700'} text-xs font-mono tracking-wider transition-colors duration-500`}>
              {currentTime}
            </div>
            <Wifi size={12} className={`${
              connectionStatus === 'connected' 
                ? 'text-cyber-green connection-indicator' 
                : 'text-red-500 animate-pulse'
            }`} />
          </div>
          
          {/* 中间：标题 */}
          <div className={`${darkMode ? 'text-cyber-teal hologram' : 'text-gray-800'} text-xs font-mono tracking-wider uppercase flex-1 text-center px-2 transition-colors duration-500`}>
            TZ COMMS
          </div>
          
          {/* 右侧：能量、清空和设置 */}
          <div className="flex items-center gap-2 flex-shrink-0">
            <div className="flex items-center gap-1 text-xs font-mono bg-cyber-teal/10 px-1.5 py-0.5 rounded border border-cyber-teal/30">
              <Activity size={12} className="text-cyber-teal" />
              <span className="text-cyber-teal font-bold text-[10px]">{systemEnergy}%</span>
            </div>
            {/* 清空按钮 */}
            {messages.length > 0 && (
              <button 
                onClick={handleClearMessages}
                className="text-red-400 hover:text-red-300 transition-all transform hover:scale-110 duration-300"
                title="Clear all messages"
              >
                <X size={16} className="glow-text" />
              </button>
            )}
            {/* 重启游戏按钮 */}
            <button 
              onClick={restartGame}
              className="text-cyber-yellow hover:text-cyber-pink transition-all transform hover:rotate-[-360deg] duration-500"
              title="Restart game"
            >
              <RotateCcw size={16} className="glow-text" />
            </button>
            <button 
              onClick={() => setShowSettings(!showSettings)}
              className="text-cyber-teal hover:text-cyber-blue transition-all transform hover:rotate-90 duration-300"
            >
              <Settings size={16} className="glow-text" />
            </button>
          </div>
        </div>

        {/* 消息区域 - 移动端固定高度 */}
        <div className="h-[calc(812px-64px-48px-70px-96px)] overflow-y-auto overflow-x-hidden px-4 py-3 space-y-3 scrollbar-thin">
          {messages.map((msg, index) => (
            <MessageBubble 
              key={msg.id} 
              message={msg} 
              index={index} 
              onTyping={scrollToBottom}
              onTypingComplete={handleTypingComplete}
              ref={(el) => (messageRefs.current[index] = el)}
              isHighlighted={currentMessageIndex === index}
              darkMode={darkMode}
              typewriterEnabled={typewriterEnabled}
              animationSpeed={animationSpeed}
            />
          ))}
          {isTyping && (
            <div className="flex items-start gap-2 message-appear">
              <div className="flex-shrink-0 w-10 h-10 border border-cyber-blue rounded flex items-center justify-center bg-cyber-darker">
                <Cpu size={20} className="text-cyber-blue animate-spin" />
              </div>
              <div className="flex-1 p-3 rounded border border-cyber-blue/50 bg-cyber-blue/5 backdrop-blur-sm">
                <div className="flex items-center space-x-2">
                  <span className="text-cyber-blue font-mono text-sm">AI processing</span>
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-cyber-blue rounded-full ai-thinking-dot"></div>
                    <div className="w-2 h-2 bg-cyber-blue rounded-full ai-thinking-dot"></div>
                    <div className="w-2 h-2 bg-cyber-blue rounded-full ai-thinking-dot"></div>
                  </div>
                </div>
              </div>
              <div className="w-10 flex-shrink-0"></div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* 输入区域 */}
        <div className="px-4 py-3">
          <div className="relative">
            <input
              ref={inputRef}
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={inputPlaceholder}  // ⭐ 动态 placeholder
              autoComplete="off"
              autoCorrect="off"
              autoCapitalize="off"
              spellCheck="false"
              className="w-full bg-transparent border border-cyber-teal/50 rounded px-4 py-2.5 text-cyber-teal placeholder-cyber-teal/30 font-mono text-sm focus:outline-none focus:border-cyber-teal focus:ring-2 focus:ring-cyber-teal/30 transition-all"
            />
          </div>
        </div>

        {/* 底部导航 - 移动端游戏风格控制器 */}
        <div className="h-24 flex items-center justify-center gap-6 px-4 border-t border-cyber-teal/20 bg-gradient-to-t from-cyber-darker to-transparent">
          {/* 左按钮 - 上一条消息 */}
          <button 
            onClick={navigateToPrevMessage}
            className="relative w-12 h-12 rounded-full bg-cyber-darker/50 backdrop-blur-sm transition-all group active:scale-90 hover:bg-cyber-teal/20"
            style={{boxShadow: '0 0 15px rgba(0, 255, 204, 0.3), inset 0 0 10px rgba(0, 255, 204, 0.1)'}}
            aria-label="Previous Message"
          >
            <div className="absolute inset-0 flex items-center justify-center">
              <ChevronLeft size={20} className="text-cyber-teal group-hover:text-cyber-blue transition-all group-hover:drop-shadow-[0_0_8px_rgba(0,255,204,0.8)]" />
            </div>
            {/* 悬浮发光效果 */}
            <div className="absolute inset-0 rounded-full opacity-0 group-hover:opacity-100 transition-opacity" style={{boxShadow: '0 0 25px rgba(0, 255, 204, 0.6)'}}></div>
            <div className="absolute -top-7 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity">
              <span className="text-[9px] text-cyber-teal font-mono whitespace-nowrap">PREV MSG</span>
            </div>
          </button>
          
          {/* 中央按钮 - 发送消息 */}
          <button 
            className="relative w-16 h-16 rounded-full flex items-center justify-center group focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed"
            aria-label="Send message"
            onClick={handleSendMessage}
            disabled={!inputValue.trim()}
          >
            {/* 外层脉冲光环 */}
            <div className="absolute inset-0 rounded-full bg-cyber-blue energy-pulse"></div>
            {/* 内层核心 */}
            <div className="absolute inset-1 rounded-full bg-cyber-darker flex items-center justify-center border border-cyber-blue/50">
              <div className="w-3 h-3 rounded-full bg-cyber-blue group-hover:scale-125 transition-transform" style={{boxShadow: '0 0 15px rgba(0, 191, 255, 0.8)'}}></div>
            </div>
            {/* 扩散动画环 - 移除 animate-ping 以防止跳动 */}
            <div className="absolute inset-0 rounded-full border-2 border-cyber-blue/30 opacity-50"></div>
            {/* 提示文字 */}
            <div className="absolute -top-7 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity">
              <span className="text-[9px] text-cyber-teal font-mono whitespace-nowrap hud-element">SEND</span>
            </div>
          </button>
          
          {/* 右按钮 - 下一条消息 */}
          <button 
            onClick={navigateToNextMessage}
            className="relative w-12 h-12 rounded-full bg-cyber-darker/50 backdrop-blur-sm transition-all group active:scale-90 hover:bg-cyber-teal/20"
            style={{boxShadow: '0 0 15px rgba(0, 255, 204, 0.3), inset 0 0 10px rgba(0, 255, 204, 0.1)'}}
            aria-label="Next Message"
          >
            <div className="absolute inset-0 flex items-center justify-center">
              <ChevronRight size={20} className="text-cyber-teal group-hover:text-cyber-blue transition-all group-hover:drop-shadow-[0_0_8px_rgba(0,255,204,0.8)]" />
            </div>
            {/* 悬浮发光效果 */}
            <div className="absolute inset-0 rounded-full opacity-0 group-hover:opacity-100 transition-opacity" style={{boxShadow: '0 0 25px rgba(0, 255, 204, 0.6)'}}></div>
            <div className="absolute -top-7 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity">
              <span className="text-[9px] text-cyber-teal font-mono whitespace-nowrap">NEXT MSG</span>
            </div>
          </button>
        </div>
      </div>

      {/* 设置面板 */}
      {showSettings && (
        <SettingsPanel 
          onClose={() => setShowSettings(false)}
          darkMode={darkMode}
          setDarkMode={setDarkMode}
          soundEnabled={soundEnabled}
          setSoundEnabled={setSoundEnabled}
          animationSpeed={animationSpeed}
          setAnimationSpeed={setAnimationSpeed}
          typewriterEnabled={typewriterEnabled}
          setTypewriterEnabled={setTypewriterEnabled}
          responseTone={responseTone}
          setResponseTone={setResponseTone}
          persona={persona}
          setPersona={setPersona}
          emotion={emotion}
          setEmotion={setEmotion}
          emotionIntensity={emotionIntensity}
          setEmotionIntensity={setEmotionIntensity}
          aiMode={aiMode}
          setAiMode={setAiMode}
          apiConfig={apiConfig}
          setApiConfig={setApiConfig}
        />
      )}
    </div>
  )
}

// 消息气泡组件 - 带打字机效果
const MessageBubble = React.forwardRef(({ message, index, onTyping, onTypingComplete, isHighlighted, darkMode, typewriterEnabled, animationSpeed }, ref) => {
  const [displayedText, setDisplayedText] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [charIndex, setCharIndex] = useState(0)

  // 打字机效果 - 仅对NPC和系统消息
  useEffect(() => {
    // 用户消息或禁用打字机效果时直接显示
    if (message.type === 'user' || !typewriterEnabled) {
      setDisplayedText(message.content)
      setIsTyping(false)
      setCharIndex(0)
      // 立即通知完成
      if (onTypingComplete) {
        onTypingComplete(message.id)
      }
      return
    }

    // 重置打字机状态
    setIsTyping(true)
    setDisplayedText('')
    setCharIndex(0)
  }, [message.content, message.type, typewriterEnabled])

  // 打字机效果的实际执行
  useEffect(() => {
    if (message.type === 'user' || !isTyping || !typewriterEnabled) {
      return
    }

    if (charIndex === 0) {
      // 延迟开始，让用户有时间看到消息出现
      const startTimeout = setTimeout(() => {
        setCharIndex(1)
      }, 150)
      return () => clearTimeout(startTimeout)
    }

    if (charIndex > 0 && charIndex <= message.content.length) {
      // 根据动画速度调整打字速度
      const typingSpeeds = {
        slow: 60,    // 慢速：60ms 每字符
        normal: 35,  // 正常：35ms 每字符
        fast: 20     // 快速：20ms 每字符
      }
      const speed = typingSpeeds[animationSpeed] || 35
      
      const typingTimeout = setTimeout(() => {
        setDisplayedText(message.content.slice(0, charIndex))
        setCharIndex(charIndex + 1)
        // 触发滚动
        if (onTyping) {
          onTyping()
        }
      }, speed)
      return () => clearTimeout(typingTimeout)
    }

    if (charIndex > message.content.length) {
      setIsTyping(false)
      // 通知打字机完成
      if (onTypingComplete) {
        onTypingComplete(message.id)
      }
    }
  }, [charIndex, isTyping, message.content, message.type, onTyping, onTypingComplete, animationSpeed, message.id])

  const getIcon = () => {
    if (message.type === 'user') return <User size={20} />
    if (message.type === 'npc') return <Bot size={20} className="hologram" />
    return <Bot size={20} className="hologram" />
  }

  const bgColor = darkMode 
    ? (message.type === 'user' 
      ? 'bg-cyber-yellow/20 border-cyber-yellow/80' 
      : 'bg-cyber-blue/20 border-cyber-blue/80 energy-pulse')
    : (message.type === 'user'
      ? 'bg-blue-50 border-blue-300'
      : 'bg-blue-50 border-blue-300')

  const textColor = darkMode
    ? (message.type === 'user'
      ? 'text-cyber-yellow'
      : 'text-cyber-blue')
    : (message.type === 'user'
      ? 'text-blue-700'
      : 'text-blue-700')

  const isUser = message.type === 'user'
  
  return (
    <div ref={ref} className={`message-appear transition-all ${isHighlighted ? 'ring-2 ring-cyber-yellow rounded-lg p-1' : ''}`}>
      <div className="flex items-start gap-2">
        {/* 左侧头像占位 */}
        {isUser ? (
          <div className="w-10 flex-shrink-0"></div>
        ) : (
          <div className={`flex-shrink-0 w-10 h-10 border border-cyber-blue rounded flex items-center justify-center bg-cyber-darker`}>
            {getIcon()}
          </div>
        )}
        
        {/* 消息内容框 - 自适应宽度 */}
        <div className={`flex-1 p-3 rounded border ${bgColor} ${textColor} backdrop-blur-sm max-w-[calc(100%-5rem)] overflow-hidden`}>
          <div className={`font-mono text-sm leading-relaxed whitespace-pre-wrap break-words ${isTyping ? 'typing-cursor' : ''}`}>
            {displayedText}
          </div>
        </div>
        
        {/* 右侧头像占位 */}
        {isUser ? (
          <div className={`flex-shrink-0 w-10 h-10 border border-cyber-yellow rounded flex items-center justify-center bg-cyber-darker`}>
            {getIcon()}
          </div>
        ) : (
          <div className="w-10 flex-shrink-0"></div>
        )}
      </div>
    </div>
  )
})

// 快捷回复按钮组件
function QuickReplyButton({ text, onClick }) {
  return (
    <button
      onClick={onClick}
      className="w-full p-2 bg-transparent border border-cyber-green/50 text-cyber-green rounded text-left hover:bg-cyber-green/10 hover:border-cyber-green transition-all font-mono text-[11px] active:scale-[0.98] focus:outline-none focus:ring-2 focus:ring-cyber-green/30"
    >
      <span className="inline-block">{text}</span>
    </button>
  )
}

// 设置面板组件
function SettingsPanel({ 
  onClose, 
  darkMode, setDarkMode, 
  soundEnabled, setSoundEnabled, 
  animationSpeed, setAnimationSpeed, 
  typewriterEnabled, setTypewriterEnabled, 
  responseTone, setResponseTone,
  persona, setPersona,
  emotion, setEmotion,
  emotionIntensity, setEmotionIntensity,
  aiMode, setAiMode, 
  apiConfig, setApiConfig 
}) {
  const [showApiConfig, setShowApiConfig] = useState(false)
  
  const handleConfigChange = (field, value) => {
    setApiConfig(prev => ({
      ...prev,
      [field]: value
    }))
  }
  
  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 animate-fade-in">
      <div className="bg-gradient-to-b from-cyber-dark to-cyber-darker border-2 border-cyber-teal rounded-2xl p-6 w-full max-w-md mx-4 shadow-neon-teal animate-slide-up max-h-[90vh] overflow-y-auto scrollbar-thin">
        {/* 标题栏 */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-orbitron font-bold text-cyber-teal glow-text">SETTINGS</h2>
          <button 
            onClick={onClose}
            className="text-cyber-teal hover:text-cyber-blue transition-all transform hover:rotate-90 duration-300"
          >
            <X size={24} />
          </button>
        </div>

        {/* 设置项 */}
        <div className="space-y-6">
          {/* 主题模式 */}
          <div className="flex items-center justify-between p-4 bg-cyber-teal/10 rounded-lg border border-cyber-teal/30 hover:border-cyber-teal/50 transition-all">
            <div className="flex items-center space-x-3">
              {darkMode ? <Moon size={20} className="text-cyber-teal" /> : <Sun size={20} className="text-cyber-yellow" />}
              <span className="font-rajdhani font-semibold text-cyber-teal">Dark Mode</span>
            </div>
            <button
              onClick={() => setDarkMode(!darkMode)}
              className={`relative w-14 h-7 rounded-full transition-all ${darkMode ? 'bg-cyber-teal' : 'bg-cyber-teal/30'}`}
            >
              <div className={`absolute top-1 left-1 w-5 h-5 bg-white rounded-full transition-transform ${darkMode ? 'translate-x-7' : ''}`}></div>
            </button>
          </div>

          {/* 声音 */}
          <div className="flex items-center justify-between p-4 bg-cyber-teal/10 rounded-lg border border-cyber-teal/30 hover:border-cyber-teal/50 transition-all">
            <div className="flex items-center space-x-3">
              <Volume2 size={20} className="text-cyber-teal" />
              <span className="font-rajdhani font-semibold text-cyber-teal">Sound Effects</span>
            </div>
            <button
              onClick={() => setSoundEnabled(!soundEnabled)}
              className={`relative w-14 h-7 rounded-full transition-all ${soundEnabled ? 'bg-cyber-teal' : 'bg-cyber-teal/30'}`}
            >
              <div className={`absolute top-1 left-1 w-5 h-5 bg-white rounded-full transition-transform ${soundEnabled ? 'translate-x-7' : ''}`}></div>
            </button>
          </div>

          {/* 打字机效果 */}
          <div className="flex items-center justify-between p-4 bg-cyber-teal/10 rounded-lg border border-cyber-teal/30 hover:border-cyber-teal/50 transition-all">
            <div className="flex items-center space-x-3">
              <Activity size={20} className="text-cyber-teal" />
              <span className="font-rajdhani font-semibold text-cyber-teal">Typewriter Effect</span>
            </div>
            <button
              onClick={() => setTypewriterEnabled(!typewriterEnabled)}
              className={`relative w-14 h-7 rounded-full transition-all ${typewriterEnabled ? 'bg-cyber-teal' : 'bg-cyber-teal/30'}`}
            >
              <div className={`absolute top-1 left-1 w-5 h-5 bg-white rounded-full transition-transform ${typewriterEnabled ? 'translate-x-7' : ''}`}></div>
            </button>
          </div>

          {/* 动画速度 */}
          <div className="p-4 bg-cyber-teal/10 rounded-lg border border-cyber-teal/30">
            <div className="flex items-center space-x-3 mb-3">
              <Zap size={20} className="text-cyber-teal" />
              <span className="font-rajdhani font-semibold text-cyber-teal">Animation Speed</span>
            </div>
            <div className="flex space-x-2">
              {['slow', 'normal', 'fast'].map((speed) => (
                <button
                  key={speed}
                  onClick={() => setAnimationSpeed(speed)}
                  className={`flex-1 py-2 rounded-lg font-rajdhani font-medium text-sm capitalize transition-all ${
                    animationSpeed === speed
                      ? 'bg-cyber-teal text-cyber-dark shadow-neon-teal'
                      : 'bg-cyber-teal/20 text-cyber-teal hover:bg-cyber-teal/30'
                  }`}
                >
                  {speed}
                </button>
              ))}
            </div>
          </div>

          {/* Persona 选择器 */}
          <div className="p-4 bg-cyber-purple/10 rounded-lg border border-cyber-purple/30">
            <div className="flex items-center space-x-3 mb-3">
              <Bot size={20} className="text-cyber-purple" />
              <span className="font-rajdhani font-semibold text-cyber-purple">AI Persona</span>
            </div>
            <select
              value={persona}
              onChange={(e) => setPersona(e.target.value)}
              className="w-full bg-cyber-darker/50 border border-cyber-purple/30 rounded px-3 py-2 text-cyber-purple font-mono text-sm focus:outline-none focus:border-cyber-purple focus:ring-1 focus:ring-cyber-purple/30"
            >
              <option value="Calm_Conscientious">Calm & Conscientious</option>
              <option value="Empathic_Agreeable">Empathic & Agreeable</option>
              <option value="Controlled_Anger">Controlled Anger</option>
              <option value="Melancholic_Sober">Melancholic & Sober</option>
            </select>
            <div className="mt-2 text-xs text-cyber-purple/70 font-mono">
              🤖 {persona === 'Calm_Conscientious' ? 'Technical, stepwise, low affect' :
                  persona === 'Empathic_Agreeable' ? 'Polite, empathic, cooperative' :
                  persona === 'Controlled_Anger' ? 'Direct, urgent, time-sensitive' :
                  'Reflective, measured, thoughtful'}
            </div>
          </div>

          {/* Emotion 选择器 */}
          <div className="p-4 bg-cyber-pink/10 rounded-lg border border-cyber-pink/30">
            <div className="flex items-center space-x-3 mb-3">
              <Activity size={20} className="text-cyber-pink" />
              <span className="font-rajdhani font-semibold text-cyber-pink">Emotion State</span>
            </div>
            <div className="grid grid-cols-5 gap-2">
              {['neutral', 'joy', 'sadness', 'anger', 'disgust'].map((em) => (
                <button
                  key={em}
                  onClick={() => setEmotion(em)}
                  className={`py-2 px-2 rounded-lg font-rajdhani font-medium text-xs transition-all capitalize ${
                    emotion === em
                      ? 'bg-cyber-pink text-cyber-dark shadow-[0_0_15px_rgba(255,102,204,0.5)]'
                      : 'bg-cyber-pink/20 text-cyber-pink hover:bg-cyber-pink/30'
                  }`}
                >
                  {em === 'neutral' ? '😐' : em === 'joy' ? '😊' : em === 'sadness' ? '😢' : em === 'anger' ? '😠' : '😖'}
                  <div className="text-[9px] mt-1">{em}</div>
                </button>
              ))}
            </div>
            
            {/* Emotion Intensity 滑动条 */}
            <div className="mt-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-cyber-pink font-mono text-xs">Intensity</span>
                <span className="text-cyber-pink font-mono text-xs font-bold">{(emotionIntensity * 100).toFixed(0)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                value={emotionIntensity * 100}
                onChange={(e) => setEmotionIntensity(parseInt(e.target.value) / 100)}
                className="w-full h-2 bg-cyber-pink/20 rounded-lg appearance-none cursor-pointer slider-thumb"
                style={{
                  background: `linear-gradient(to right, rgba(255, 102, 204, 0.5) 0%, rgba(255, 102, 204, 0.5) ${emotionIntensity * 100}%, rgba(255, 102, 204, 0.1) ${emotionIntensity * 100}%, rgba(255, 102, 204, 0.1) 100%)`
                }}
              />
              <div className="flex justify-between mt-1 text-xs text-cyber-pink/60 font-mono">
                <span>Low</span>
                <span>High</span>
              </div>
            </div>
          </div>

          {/* Response Tone 滑动条 */}
          <div className="p-4 bg-cyber-teal/10 rounded-lg border border-cyber-teal/30">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-3">
                <Activity size={20} className="text-cyber-teal" />
                <span className="font-rajdhani font-semibold text-cyber-teal">Response Tone</span>
              </div>
              <span className="text-cyber-teal font-mono text-sm font-bold">{responseTone}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={responseTone}
              onChange={(e) => setResponseTone(parseInt(e.target.value))}
              className="w-full h-2 bg-cyber-teal/20 rounded-lg appearance-none cursor-pointer slider-thumb"
              style={{
                background: `linear-gradient(to right, rgba(0, 255, 204, 0.5) 0%, rgba(0, 255, 204, 0.5) ${responseTone}%, rgba(0, 255, 204, 0.1) ${responseTone}%, rgba(0, 255, 204, 0.1) 100%)`
              }}
            />
            <div className="flex justify-between mt-2 text-xs text-cyber-teal/60 font-mono">
              <span>Formal</span>
              <span>Balanced</span>
              <span>Casual</span>
            </div>
          </div>

          {/* AI 接入方式 */}
          <div className="p-4 bg-cyber-yellow/10 rounded-lg border border-cyber-yellow/30">
            <div className="flex items-center space-x-3 mb-3">
              <Bot size={20} className="text-cyber-yellow" />
              <span className="font-rajdhani font-semibold text-cyber-yellow">AI Mode</span>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => setAiMode('api')}
                className={`flex-1 py-2 px-3 rounded-lg font-rajdhani font-medium text-sm transition-all ${
                  aiMode === 'api'
                    ? 'bg-cyber-yellow text-cyber-dark shadow-[0_0_15px_rgba(255,204,0,0.5)]'
                    : 'bg-cyber-yellow/20 text-cyber-yellow hover:bg-cyber-yellow/30'
                }`}
              >
                <div className="text-center">
                  <div className="font-bold">API</div>
                  <div className="text-[10px] opacity-70">ByteDance</div>
                </div>
              </button>
              <button
                onClick={() => setAiMode('llama')}
                className={`flex-1 py-2 px-3 rounded-lg font-rajdhani font-medium text-sm transition-all ${
                  aiMode === 'llama'
                    ? 'bg-cyber-yellow text-cyber-dark shadow-[0_0_15px_rgba(255,204,0,0.5)]'
                    : 'bg-cyber-yellow/20 text-cyber-yellow hover:bg-cyber-yellow/30'
                }`}
              >
                <div className="text-center">
                  <div className="font-bold">Llama</div>
                  <div className="text-[10px] opacity-70">Local</div>
                </div>
              </button>
            </div>
            <div className="mt-2 text-xs text-cyber-yellow/70 font-mono">
              {aiMode === 'api' ? '🌐 Using cloud API service' : '💻 Using local Llama model'}
            </div>
            
            {/* 配置按钮 */}
            <button
              onClick={() => setShowApiConfig(!showApiConfig)}
              className="mt-3 w-full py-2 bg-cyber-yellow/10 hover:bg-cyber-yellow/20 border border-cyber-yellow/30 text-cyber-yellow rounded-lg font-rajdhani font-medium text-sm transition-all"
            >
              {showApiConfig ? '▲ Hide Configuration' : '▼ Show Configuration'}
            </button>
            
            {/* API 配置区域 */}
            {showApiConfig && (
              <div className="mt-3 space-y-3 animate-slide-down">
                {aiMode === 'api' ? (
                  <>
                    {/* API 预设选择 */}
                    <div>
                      <label className="block text-xs text-cyber-yellow/80 font-mono mb-1">API Preset</label>
                      <select
                        onChange={(e) => {
                          const presets = {
                            'deepseek': {
                              apiUrl: 'https://api.deepseek.com/chat/completions',
                              model: 'deepseek-chat'
                            },
                            'ark': {
                              apiUrl: 'https://ark.cn-beijing.volces.com/api/v3/chat/completions',
                              model: 'deepseek-v3-1-terminus'
                            },
                            'openai': {
                              apiUrl: 'https://api.openai.com/v1/chat/completions',
                              model: 'gpt-4'
                            },
                            'custom': {}
                          }
                          const preset = presets[e.target.value]
                          if (preset.apiUrl) {
                            handleConfigChange('apiUrl', preset.apiUrl)
                            handleConfigChange('model', preset.model)
                          }
                        }}
                        className="w-full bg-cyber-darker/50 border border-cyber-yellow/30 rounded px-3 py-2 text-cyber-yellow font-mono text-xs focus:outline-none focus:border-cyber-yellow focus:ring-1 focus:ring-cyber-yellow/30"
                      >
                        <option value="custom">Custom / 自定义</option>
                        <option value="deepseek">DeepSeek Official / DeepSeek 官方</option>
                        <option value="ark">ByteDance ARK / 火山引擎</option>
                        <option value="openai">OpenAI</option>
                      </select>
                    </div>
                    
                    {/* API URL */}
                    <div>
                      <label className="block text-xs text-cyber-yellow/80 font-mono mb-1">API URL</label>
                      <input
                        type="text"
                        value={apiConfig.apiUrl}
                        onChange={(e) => handleConfigChange('apiUrl', e.target.value)}
                        className="w-full bg-cyber-darker/50 border border-cyber-yellow/30 rounded px-3 py-2 text-cyber-yellow font-mono text-xs focus:outline-none focus:border-cyber-yellow focus:ring-1 focus:ring-cyber-yellow/30"
                        placeholder="https://api.example.com/v1/chat"
                      />
                    </div>
                    
                    {/* API Token */}
                    <div>
                      <label className="block text-xs text-cyber-yellow/80 font-mono mb-1">API Token</label>
                      <input
                        type="password"
                        value={apiConfig.apiToken}
                        onChange={(e) => handleConfigChange('apiToken', e.target.value)}
                        className="w-full bg-cyber-darker/50 border border-cyber-yellow/30 rounded px-3 py-2 text-cyber-yellow font-mono text-xs focus:outline-none focus:border-cyber-yellow focus:ring-1 focus:ring-cyber-yellow/30"
                        placeholder="Your API token"
                      />
                    </div>
                    
                    {/* Model */}
                    <div>
                      <label className="block text-xs text-cyber-yellow/80 font-mono mb-1">Model</label>
                      <input
                        type="text"
                        value={apiConfig.model}
                        onChange={(e) => handleConfigChange('model', e.target.value)}
                        className="w-full bg-cyber-darker/50 border border-cyber-yellow/30 rounded px-3 py-2 text-cyber-yellow font-mono text-xs focus:outline-none focus:border-cyber-yellow focus:ring-1 focus:ring-cyber-yellow/30"
                        placeholder="deepseek-v3-1-terminus"
                      />
                    </div>
                  </>
                ) : (
                  <>
                    {/* Ollama Service URL */}
                    <div>
                      <label className="block text-xs text-cyber-yellow/80 font-mono mb-1">Ollama Service URL</label>
                      <input
                        type="text"
                        value={apiConfig.ollamaUrl}
                        onChange={(e) => handleConfigChange('ollamaUrl', e.target.value)}
                        className="w-full bg-cyber-darker/50 border border-cyber-yellow/30 rounded px-3 py-2 text-cyber-yellow font-mono text-xs focus:outline-none focus:border-cyber-yellow focus:ring-1 focus:ring-cyber-yellow/30"
                        placeholder="http://localhost:11434"
                      />
                      <div className="mt-1 text-[10px] text-cyber-yellow/50">
                        默认本地服务地址，可修改为远程或自定义端口
                      </div>
                    </div>
                    
                    {/* Llama Model */}
                    <div>
                      <label className="block text-xs text-cyber-yellow/80 font-mono mb-1">Llama Model</label>
                      <select
                        value={apiConfig.llamaModel}
                        onChange={(e) => handleConfigChange('llamaModel', e.target.value)}
                        className="w-full bg-cyber-darker/50 border border-cyber-yellow/30 rounded px-3 py-2 text-cyber-yellow font-mono text-xs focus:outline-none focus:border-cyber-yellow focus:ring-1 focus:ring-cyber-yellow/30"
                      >
                        <option value="qwen:7b">Qwen 7B (推荐中文)</option>
                        <option value="llama2:7b">Llama 2 7B</option>
                        <option value="llama2:13b">Llama 2 13B</option>
                        <option value="mistral:7b">Mistral 7B (轻量)</option>
                        <option value="codellama">Code Llama</option>
                        <option value="mixtral">Mixtral 8x7B</option>
                      </select>
                    </div>
                    
                    <div className="text-xs text-cyber-yellow/60 font-mono space-y-1">
                      <div>💡 启动 Ollama 服务:</div>
                      <code className="text-cyber-yellow/80 block">ollama serve</code>
                      <div>📥 下载模型:</div>
                      <code className="text-cyber-yellow/80 block">ollama pull {apiConfig.llamaModel}</code>
                    </div>
                  </>
                )}
              </div>
            )}
          </div>

          {/* 关于信息 */}
          <div className="p-4 bg-cyber-blue/10 rounded-lg border border-cyber-blue/30">
            <p className="text-cyber-blue font-rajdhani text-sm leading-relaxed">
              <span className="font-bold">Lightracer Comms v1.0</span><br />
              Neural Communication Interface<br />
              Powered by React + Flask
            </p>
          </div>
        </div>

        {/* 关闭按钮 */}
        <button
          onClick={onClose}
          className="w-full mt-6 py-3 bg-cyber-teal/20 hover:bg-cyber-teal/30 border border-cyber-teal text-cyber-teal rounded-lg font-rajdhani font-bold transition-all transform hover:scale-[1.02] active:scale-95"
        >
          CLOSE
        </button>
      </div>
    </div>
  )
}

export default App
