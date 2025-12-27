# 小红书商品信息提取 - 功能说明

## 更新内容

✅ **已实现小红书平台特定的商品信息提取流程**

### 新增功能

#### 1. 自动切换到"商品"标签页
- 在小红书搜索完成后，系统会自动识别并点击"商品"标签
- 确保进入商品列表而非笔记列表

#### 2. 真实的AI商品信息提取
- 使用 AutoGLM 的多模态视觉能力识别页面内容
- 自动提取：商品标题、店铺名称、价格、商品描述
- 支持 OCR 文本识别

#### 3. 智能解析模型响应
- 自动解析模型返回的 JSON 数据
- 支持多种 JSON 格式（纯JSON、代码块、嵌入式）
- 容错处理，提取失败时使用备用方案

## 工作流程

### 小红书平台完整流程

```
1. 启动小红书应用
   ↓
2. 输入关键词搜索
   ↓
3. 等待搜索结果加载
   ↓
4. 【新增】自动点击"商品"标签 ⭐
   ↓
5. 等待商品列表加载
   ↓
6. 循环检查每个商品:
   ├─ 点击进入商品详情页
   ├─ 【改进】使用AI视觉识别商品信息 ⭐
   │  ├─ 商品标题
   │  ├─ 店铺名称
   │  ├─ 价格
   │  └─ 商品描述/OCR文本
   ├─ 盗版检测
   ├─ 如果是盗版则举报
   └─ 返回列表继续
```

## 代码改进

### 1. 配置文件更新 (`config_anti_piracy.py`)

**新增提示词**：

```python
# 小红书专用 - 切换到商品标签
"switch_to_products_tab": """
当前在小红书搜索结果页面,请执行:
1. 查找页面顶部的标签栏
2. 点击"商品"标签
3. 等待商品列表加载完成
"""

# 从列表页批量提取商品信息（可选功能）
"extract_from_list": """
当前在商品列表页面,请识别并提取当前屏幕上所有可见商品的信息。
对于每个商品,请提取:
1. 商品标题(完整标题)
2. 价格(数字,如果有)
3. 店铺名称或卖家昵称
4. 商品在列表中的位置(第几个)

请以JSON数组格式返回...
"""
```

### 2. Agent 改进 (`anti_piracy_agent.py`)

#### A. 搜索后自动切换标签

```python
def _launch_and_search(self, keyword: str) -> bool:
    # ... 原有搜索逻辑 ...

    # 小红书特殊处理：切换到"商品"标签
    if self.platform == "xiaohongshu":
        print("\n📱 小红书平台：切换到商品标签...")
        switch_task = get_task_prompt("switch_to_products_tab")
        self.base_agent.run(switch_task)
```

#### B. AI信息提取实现

```python
def _extract_product_info(self, index: int = 0) -> Optional[ProductInfo]:
    # 1. 进入商品详情页
    self._enter_detail(index)

    # 2. 使用AI视觉模型识别页面
    task = get_task_prompt("extract_info")
    response = self.base_agent.run(task)

    # 3. 解析JSON响应
    parsed_data = self._parse_model_response(response)

    # 4. 提取并验证数据
    title = parsed_data.get('title') or parsed_data.get('商品标题')
    shop_name = parsed_data.get('shop_name') or parsed_data.get('店铺名称')
    price = extract_price(parsed_data.get('price'))

    # 5. 返回商品信息对象
    return ProductInfo(title, shop_name, price, ...)
```

#### C. 智能JSON解析

```python
def _parse_model_response(self, response: str) -> Optional[Dict]:
    # 方法1: 直接解析JSON
    # 方法2: 提取代码块中的JSON
    # 方法3: 查找嵌入的JSON对象
    # 容错处理
```

## 使用示例

### 测试小红书商品提取

```bash
cd /Users/Apple/Documents/GUI/anti_piracy_system
source venv/bin/activate

# 测试模式运行（推荐首次测试）
python main_anti_piracy.py \
    --base-url https://api-inference.modelscope.cn/v1 \
    --model "ZhipuAI/AutoGLM-Phone-9B" \
    --apikey "your-api-key" \
    --platform xiaohongshu \
    --keyword "得到" \
    --max-items 3 \
    --test-mode \
    --verbose
```

### 预期输出

```
🚀 启动 小红书 并搜索'得到'...
✅ 应用启动和搜索完成

📱 小红书平台：切换到商品标签...
✅ 已切换到商品标签

--- 检查第 1/3 个商品 ---
📋 提取第 1 个商品信息...
   使用AI视觉模型识别页面内容...
   模型响应: {"title": "薛兆丰经济学讲义", "shop_name": "某店铺", "price": "29.9"}...
✅ 成功提取商品信息:
   标题: 薛兆丰经济学讲义
   店铺: 某店铺
   价格: ¥29.9

🔍 检测商品: 薛兆丰经济学讲义
❌ 检测到疑似盗版! (置信度: 85%)
   判定依据:
   - 价格为¥29.9，仅为官方价格¥199.0的15%
   - 店铺"某店铺"不在官方授权列表中
```

## 关键改进点

### ✅ 符合小红书实际流程
- 搜索后自动切换到"商品"标签
- 确保浏览的是商品而非笔记

### ✅ 真实信息提取
- 不再返回模拟数据
- 使用 AutoGLM 多模态能力识别页面
- 支持中英文字段映射

### ✅ 鲁棒性提升
- 多种JSON解析策略
- 提取失败时的备用方案
- 详细的日志输出便于调试

### ✅ 价格处理优化
- 自动移除货币符号（¥、元）
- 正则提取数字部分
- 类型转换错误处理

## 提示词工程技巧

为了让模型更好地提取信息，可以优化提示词：

```python
# 更明确的提取指令
"extract_info": """
当前在商品详情页,请识别并提取以下信息:

**必需字段**:
1. 商品标题 (title): 页面顶部的商品名称
2. 店铺名称 (shop_name): 卖家或店铺的名称
3. 商品价格 (price): 数字金额,不包含货币符号

**可选字段**:
4. 商品描述 (description): 详细的商品说明
5. OCR文本 (all_text): 页面上的所有可见文字

请严格按以下JSON格式返回:
{
  "title": "商品标题",
  "shop_name": "店铺名称",
  "price": "99.9",
  "description": "商品描述",
  "all_text": "所有文本"
}
"""
```

## 故障排查

### 问题1: 无法切换到商品标签

**可能原因**:
- 小红书UI更新，标签名称或位置变化
- 加载时间不足

**解决方案**:
1. 增加等待时间: `time.sleep(3)`
2. 更新提示词中的标签描述
3. 使用更通用的描述（如"购物袋图标"）

### 问题2: 模型无法返回JSON

**可能原因**:
- 提示词不够明确
- 模型理解能力限制

**解决方案**:
1. 在提示词中明确要求JSON格式
2. 提供JSON示例
3. 使用多次尝试策略

### 问题3: 提取的价格为0

**可能原因**:
- 页面未显示价格
- 价格格式特殊

**解决方案**:
1. 检查是否真的有价格显示
2. 改进正则表达式匹配
3. 允许价格为空/0的情况

## 后续优化方向

### 1. 列表页批量提取（提升效率）
- 不逐个点击商品
- 直接在列表页识别所有可见商品
- 使用 `extract_from_list` 提示词

### 2. 缓存和去重
- 避免重复检查同一商品
- 记录已检查的商品ID/URL

### 3. 多平台适配
- 闲鱼、淘宝的特定流程
- 统一的接口，平台特定的实现

### 4. 提取准确率优化
- 多次提取取平均值
- 使用更强的视觉模型
- 结合OCR专用库

## 总结

现在系统已经能够：
- ✅ 自动处理小红书的"商品"标签切换
- ✅ 使用AI视觉模型提取真实的商品信息
- ✅ 智能解析多种格式的模型响应
- ✅ 提供详细的调试日志

可以直接运行测试，观察实际效果！
