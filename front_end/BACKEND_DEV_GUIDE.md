
# 后端开发对接指南 (Backend Integration Guide)

本文档旨在说明如何将当前前端 Mock 逻辑替换为真实的生产环境 API。

## 1. 核心 API 接口设计建议

### A. 审计节点查询 (Merchant Audit)
- **Endpoint:** `GET /api/v1/audit/nodes`
- **Description:** 获取当前正在扫描或已扫描的商家节点列表。
- **Data Structure (TypeScript):** `Merchant[]`
- **关键字段:** 
  - `status`: `'official'` (合规) 或 `'pirated'` (违规)。
  - `reasoning`: AI 生成的判定理由。
  - `evidenceImages`: 存证截图 URL 数组。

### B. 实时日志流 (Log Stream)
- **Recommendation:** 建议使用 **WebSocket** 或 **SSE (Server-Sent Events)** 实现。
- **Topic:** `ws://server/logs/realtime`
- **Message Format:**
  ```json
  {
    "type": "info | action | performance",
    "timestamp": "HH:mm:ss",
    "message": "日志内容..."
  }
  ```

### C. 白名单同步 (Whitelist Management)
- **Endpoints:** 
  - `GET /api/v1/whitelist`
  - `POST /api/v1/whitelist/add`
  - `DELETE /api/v1/whitelist/:id`

### D. 报告生成与导出 (Reporting)
- **Logic:** 前端目前使用 `window.print()` 调用原生 PDF 驱动。后端可提供 `GET /api/v1/reports/export?format=pdf` 接口，利用无头浏览器 (Puppeteer) 在服务端生成更高质量的报告。

## 2. AI 逻辑集成
目前前端直接调用了 `gemini-3-flash-preview`。生产环境下，建议：
1. 前端向后端发送原始证据（HTML/截图）。
2. 后端调用大模型进行判定。
3. 后端持久化判定结果，并通过前述接口推送给前端。

## 3. 鉴权与安全
- 桌面应用建议通过 `Authorization: Bearer <JWT>` 进行接口鉴权。
- 考虑到桌面端安全性，敏感配置（如 API_KEY）应存储在后端的环境变量中，而非硬编码在前端。

## 4. 离线支持
前端已具备 `isOnline` 状态检测逻辑。后端接口应支持 ETag 缓存，以便在网络不稳时前端能展示最后一次有效的节点数据。
