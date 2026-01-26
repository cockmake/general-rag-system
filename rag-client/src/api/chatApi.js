import commonApi from './commonApi'
import {API_BASE_URL} from "@/consts.js";
import {useUserStore} from "@/stores/user.js";
import {fetchEventSource} from "@microsoft/fetch-event-source"
import {message} from "ant-design-vue";

export function fetchAvailableModels() {
    return commonApi.get('/models/available')
}

export function startChat({modelId, question, kbId, options}) {
    return commonApi.post('/chat/start', {
        modelId,
        question,
        kbId,
        options
    })
}

export function fetchSessionMessages(sessionId) {
    return commonApi.get(`/chat/sessions/${sessionId}/messages`)
}

export function fetchSessions({lastActiveAt, lastId, pageSize = 20}) {
    return commonApi.post('/sessions/list', {
        lastActiveAt, lastId, pageSize
    })
}

export function searchSessions({keyword, limit, offset}) {
    return commonApi.post('/sessions/search', {
        keyword, limit, offset
    })
}

export function deleteSession(sessionId) {
    return commonApi.delete(`/sessions/${sessionId}`)
}

export function awaitSessionTitle(sessionId, onEvent) {
    console.log("awaitSessionTitle", sessionId)
    fetchEventSource(`${API_BASE_URL}/sessions/${sessionId}/title/await`, {
        headers: {
            Authorization: `Bearer ${useUserStore().token}`,
        },
        async onopen(response) {
            if (response.ok) {
                console.log('Session SSE connected')
                return
            }
            throw new Error(`Failed to connect: ${response.status}`)
        },
        onmessage(ev) {
            if (onEvent) {
                let {data, event} = ev
                const json = JSON.parse(data)
                onEvent(json.title || '新的对话')
            }
        },
        onclose() {
            console.log('Session SSE closed')
        },
        onerror(err) {
            console.error('Session SSE error', err)
        },
        openWhenHidden: true
    }).then()
}

export function startChatStream(sessionId, modelId, question, kbId, options, onOpen, onMessage, onError, onClose) {
    fetchEventSource(`${API_BASE_URL}/chat/stream`, {
        method: "POST",

        headers: {
            "Authorization": `Bearer ${useUserStore().token}`,
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            sessionId: sessionId,
            modelId: modelId,
            question: question,
            kbId: kbId,
            options: options
        }),

        onopen(response) {
            if (response.ok) {
                console.log("Chat SSE connected")
                if (onOpen) onOpen(response)
                return
            }
            throw new Error("Chat SSE Connection failed")
        },
        onmessage(ev) {
            let json = JSON.parse(ev.data)
            if (json.type === 'content') {
                // content字段直接使用，已在server端解析
                if (onMessage) onMessage({type: 'content', content: json.content})
            } else if (json.type === 'process') {
                // payload字段直接使用，已在server端解析
                if (onMessage) onMessage({type: 'process', payload: json.payload})
            } else if (json.type === 'done') {
                // 流完成事件，包含消息ID
                if (onMessage) onMessage({
                    type: 'done',
                    userMessageId: json.userMessageId,
                    assistantMessageId: json.assistantMessageId
                })
            } else if (json.type === "usage") {
                if (onMessage) onMessage({
                    type: 'usage',
                    payload: json.payload
                })
            }
        },
        onclose() {
            console.log("Chat SSE closed")
            if (onClose) onClose()
        },
        onerror(err) {
            console.error("chat stream error", err)
            if (onError) onError(err)
            throw err
        },
        openWhenHidden: true // 类 ChatGPT，切 tab 不断流
    }).then()
}

/**
 * 编辑最后一轮用户问题并重新生成回复
 */
export function editMessageStream(messageId, sessionId, modelId, kbId, newContent, options, onOpen, onMessage, onError, onClose) {
    fetchEventSource(`${API_BASE_URL}/chat/messages/${messageId}/edit`, {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${useUserStore().token}`,
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            sessionId: sessionId,
            modelId: modelId,
            kbId: kbId,
            newContent: newContent,
            options: options
        }),
        onopen(response) {
            if (response.ok) {
                console.log("Edit SSE connected")
                if (onOpen) onOpen(response)
                return
            }
            throw new Error("Edit SSE Connection failed")
        },
        onmessage(ev) {
            let json = JSON.parse(ev.data)
            if (json.type === 'content') {
                if (onMessage) onMessage({type: 'content', content: json.content})
            } else if (json.type === 'process') {
                if (onMessage) onMessage({type: 'process', payload: json.payload})
            } else if (json.type === 'done') {
                if (onMessage) onMessage({
                    type: 'done',
                    userMessageId: json.userMessageId,
                    assistantMessageId: json.assistantMessageId
                })
            } else if (json.type === "usage") {
                if (onMessage) onMessage({
                    type: 'usage',
                    payload: json.payload
                })
            }
        },
        onclose() {
            console.log("Edit SSE closed")
            if (onClose) onClose()
        },
        onerror(err) {
            console.error("edit stream error", err)
            if (onError) onError(err)
            throw err
        },
        openWhenHidden: true
    }).then()
}

/**
 * 重试最后一轮AI回复
 * @param userMessageId 最后一轮用户消息ID（用于定位需要重新生成回复的用户问题）
 */
export function retryMessageStream(userMessageId, sessionId, modelId, kbId, options, onOpen, onMessage, onError, onClose) {
    fetchEventSource(`${API_BASE_URL}/chat/messages/${userMessageId}/retry`, {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${useUserStore().token}`,
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            sessionId: sessionId,
            modelId: modelId,
            kbId: kbId,
            options: options
        }),
        onopen(response) {
            if (response.ok) {
                console.log("Retry SSE connected")
                if (onOpen) onOpen(response)
                return
            }
            throw new Error("Retry SSE Connection failed")
        },
        onmessage(ev) {
            let json = JSON.parse(ev.data)
            if (json.type === 'content') {
                if (onMessage) onMessage({type: 'content', content: json.content})
            } else if (json.type === 'process') {
                if (onMessage) onMessage({type: 'process', payload: json.payload})
            } else if (json.type === 'done') {
                if (onMessage) onMessage({
                    type: 'done',
                    userMessageId: json.userMessageId,
                    assistantMessageId: json.assistantMessageId
                })
            } else if (json.type === "usage") {
                if (onMessage) onMessage({
                    type: 'usage',
                    payload: json.payload
                })
            }
        },
        onclose() {
            console.log("Retry SSE closed")
            if (onClose) onClose()
        },
        onerror(err) {
            console.error("retry stream error", err)
            if (onError) onError(err)
            throw err
        },
        openWhenHidden: true
    }).then()
}