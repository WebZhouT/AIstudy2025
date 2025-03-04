package types

// * +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
// * Copyright 2023 The Geek-AI Authors. All rights reserved.
// * Use of this source code is governed by a Apache-2.0 license
// * that can be found in the LICENSE file.
// * @Author yangjian102621@163.com
// * +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

// ApiRequest API 请求实体
type ApiRequest struct {
	Model               string        `json:"model,omitempty"`
	Temperature         float32       `json:"temperature"`
	MaxTokens           int           `json:"max_tokens,omitempty"`
	MaxCompletionTokens int           `json:"max_completion_tokens,omitempty"` // 兼容GPT O1 模型
	Stream              bool          `json:"stream,omitempty"`
	Messages            []interface{} `json:"messages,omitempty"`
	Tools               []Tool        `json:"tools,omitempty"`
	Functions           []interface{} `json:"functions,omitempty"` // 兼容中转平台

	ToolChoice string `json:"tool_choice,omitempty"`

	Input      map[string]interface{} `json:"input,omitempty"`      //兼容阿里通义千问
	Parameters map[string]interface{} `json:"parameters,omitempty"` //兼容阿里通义千问
}

type Message struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

type ApiResponse struct {
	Choices []ChoiceItem `json:"choices"`
}

// ChoiceItem API 响应实体
type ChoiceItem struct {
	Delta        Delta  `json:"delta"`
	FinishReason string `json:"finish_reason"`
}

type Delta struct {
	Role         string      `json:"role"`
	Name         string      `json:"name"`
	Content      interface{} `json:"content"`
	ToolCalls    []ToolCall  `json:"tool_calls,omitempty"`
	FunctionCall struct {
		Name      string `json:"name,omitempty"`
		Arguments string `json:"arguments,omitempty"`
	} `json:"function_call,omitempty"`
}

// ChatSession 聊天会话对象
type ChatSession struct {
	UserId   uint      `json:"user_id"`
	ClientIP string    `json:"client_ip"` // 客户端 IP
	ChatId   string    `json:"chat_id"`   // 客户端聊天会话 ID, 多会话模式专用字段
	Model    ChatModel `json:"model"`     // GPT 模型
	Start    int64     `json:"start"`     // 开始请求时间戳
	Tools    []int     `json:"tools"`     // 工具函数列表
	Stream   bool      `json:"stream"`    // 是否采用流式输出
}

type ChatModel struct {
	Id          uint    `json:"id"`
	Name        string  `json:"name"`
	Value       string  `json:"value"`
	Power       int     `json:"power"`
	MaxTokens   int     `json:"max_tokens"`  // 最大响应长度
	MaxContext  int     `json:"max_context"` // 最大上下文长度
	Temperature float32 `json:"temperature"` // 模型温度
	KeyId       int     `json:"key_id"`      // 绑定 API KEY
}

type ApiError struct {
	Error struct {
		Message string
		Type    string
		Param   interface{}
		Code    string
	}
}

const PromptMsg = "prompt" // prompt message
const ReplyMsg = "reply"   // reply message

// PowerType 算力日志类型
type PowerType int

const (
	PowerRecharge = PowerType(1) // 充值
	PowerConsume  = PowerType(2) // 消费
	PowerRefund   = PowerType(3) // 任务（SD,MJ）执行失败，退款
	PowerInvite   = PowerType(4) // 邀请奖励
	PowerRedeem   = PowerType(5) // 众筹
	PowerGift     = PowerType(6) // 系统赠送
)

func (t PowerType) String() string {
	switch t {
	case PowerRecharge:
		return "充值"
	case PowerConsume:
		return "消费"
	case PowerRefund:
		return "退款"
	case PowerRedeem:
		return "兑换"

	}
	return "其他"
}

type PowerMark int

const (
	PowerSub = PowerMark(0)
	PowerAdd = PowerMark(1)
)
