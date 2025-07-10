import {FlowDocumentJSON} from './typings';

export const initialData: FlowDocumentJSON={
  nodes: [
    // 输入节点
    {
      id: 'start_0',
      type: 'start',
      meta: {position: {x: 180,y: 100}},
      data: {
        title: '财经内容输入',
        outputs: {
          type: 'object',
          properties: {
            content: {
              type: 'string',
              default: '请输入财经内容...',
              description: '原始财经内容'
            }
          }
        }
      }
    },

    // DeepSeek处理节点
    {
      id: 'deepseek_processor',
      type: 'llm',
      meta: {position: {x: 500,y: 100}},
      data: {
        title: 'DeepSeek关键词提取',
        inputsValues: {
          modelName: {
            type: 'constant',
            content: 'deepseek-chat'
          },
          // 使用环境变量更安全
          apiKey: {
            type: 'env',
            content: 'DEEPSEEK_API_KEY'
          },
          apiHost: {
            type: 'constant',
            content: 'https://api.deepseek.com/v1'
          },
          temperature: {
            type: 'constant',
            content: 0.3  // 降低随机性
          },
          systemPrompt: {
            type: 'constant',
            content: '你是一名专业财经分析师，负责从文本中提取精确的搜索关键词。请严格遵循以下规则：'
          },
          prompt: {
            type: 'template',  // 使用模板引擎
            content: `
              根据以下规则处理用户输入：
              {{content}}
              
              处理规则：
              1. 提取热度TOP5板块
              2. 政策时效性：仅限T±2日内发布的政策
              3. 事件真实性：必须提供可验证来源
              4. 轮动安全：近5日涨幅＜10%
              5. 排除：证券/银行/黄金/高息股
              6. 传播验证：仅限官媒或上市公司公告
              7. 输出格式：政策文号+发布日期 (例：工信部〔2025〕78号)
              8. 核心事件：50字内+来源链接
              
              输出要求：
              - 仅返回关键词，不包含解释
              - 用逗号分隔关键词
              - 确保所有关键词可搜索验证
            `
          }
        },
        inputs: {
          type: 'object',
          required: ['modelName','apiKey','prompt'],
          properties: {
            modelName: {type: 'string'},
            apiKey: {type: 'string'},
            apiHost: {type: 'string'},
            systemPrompt: {type: 'string'},
            prompt: {type: 'string'}
          }
        },
        outputs: {
          type: 'object',
          properties: {
            result: {
              type: 'string',
              description: '生成的搜索关键词'
            }
          }
        }
      }
    },

    // 输出节点
    {
      id: 'output_display',
      type: 'text-output',
      meta: {position: {x: 800,y: 100}},
      data: {
        title: '关键词结果',
        content: {
          type: 'ref',
          content: ['deepseek_processor','result']
        }
      }
    }
  ],

  edges: [
    {
      sourceNodeID: 'start_0',
      targetNodeID: 'deepseek_processor',
      // 关键修复：明确指定数据传输
      dataMapping: {
        'content': 'prompt.content'  // 将输入内容注入模板
      }
    },
    {
      sourceNodeID: 'deepseek_processor',
      targetNodeID: 'output_display'
    }
  ]
};
