# 前端通信服务架构

## 架构概述

系统采用了集中式通信架构，所有前端组件与后端的交互都通过唯一的通信Agent（comm_agent）进行。
这种架构确保了：

1. **所有与用户的交互均由comm_agent负责**
2. **前端只需对接comm_agent的API**
3. **功能性Agent专注于自己的业务领域**

## 通信流程

前端 -> 通信Agent -> 功能Agent -> 微服务API

## 服务说明

### commService.js

通信服务（commService）是前端与所有Agent交互的唯一入口点。它负责：

- 封装API请求
- 维护会话状态
- 处理认证
- 错误处理与恢复
- 路由请求到适当的领域Agent

### API端点

所有请求统一发送到：`http://localhost:8085/chat`

### 请求格式

```json
{
  "user_input": "用户输入消息",
  "session_id": "会话ID",
  "agent_type": "请求的服务类型（如shopping、order、payment等）",
  "action": "可选的具体操作"
}
```

### 功能划分

- **comm_agent**: 负责用户交互，请求路由，会话管理
- **shopping_agent**: 负责商品推荐
- **order_agent**: 负责订单管理
- **payment_agent**: 负责支付处理

## 开发指南

1. 所有新的功能性交互都应该通过commService进行
2. 不要直接与业务Agent通信
3. 在请求中通过agent_type参数指定需要的服务类型
4. 每个会话使用唯一的session_id
5. 实现合适的错误恢复机制

## 错误处理

系统实现了多层次的错误处理：

1. 通信级错误处理（网络问题，认证失败等）
2. 业务级错误处理（数据验证，业务规则等）
3. 优雅降级（当特定服务不可用时使用备用方案） 