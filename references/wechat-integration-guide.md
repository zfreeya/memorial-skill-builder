# 微信数据集成指南

本文档说明如何使用 memorial-skill-builder 集成的 PyWxDump 能力自动提取微信数据。

## 核心技术

### 1. 密钥提取原理

微信数据库使用 SQLCipher 加密，密钥存储在进程内存中。

**提取流程：**
1. 搜索微信进程（WeChat.exe）
2. 使用 Windows API（ReadProcessMemory）读取进程内存
3. 搜索特征字符串定位密钥地址
4. 读取 32 字节 AES 密钥

**特征字符串：**
- `\Msg\FTSContact` - 联系人全文搜索
- `\Msg\MicroMsg.db` - 微信消息数据库路径
- `\Msg\MSG0.db` - 聊天记录数据库

### 2. 数据库解密

**加密格式：**
- 算法：AES-256-CBC
- 页大小：4096 字节
- 每页结构：
  - 4048 字节加密数据
  - 16 字节 IV（初始化向量）
  - 20 字节 HMAC-SHA1
  - 12 字节填充

**解密步骤：**
1. 使用 PBKDF2-HMAC-SHA1 从密钥派生密钥
2. 验证 HMAC
3. 使用 AES-CBC 逐页解密
4. 写入标准 SQLite 文件头

### 3. 数据库结构

**MSG 表（核心表）：**
- `localId`: 本地消息ID
- `MsgSvrID`: 服务器消息ID
- `Type`: 消息类型（1=文本, 3=图片, 34=语音等）
- `SubType`: 消息子类型
- `CreateTime`: 创建时间（Unix 时间戳）
- `IsSender`: 是否为发送者（1=我, 0=对方）
- `StrTalker`: 聊天对象微信ID
- `StrContent`: 消息内容
- `DisplayContent`: 显示内容
- `BytesExtra`: 额外数据（图片、语音等）

**Contact 表：**
- `UserName`: 微信ID
- `Alias`: 别名
- `NickName`: 昵称
- `Remark`: 备注名
- `Type`: 类型（1=好友, 3=群聊, 4=公众号）

## 使用方法

### 方案 A：自动提取（推荐）

**前提条件：**
1. 微信正在运行
2. 以管理员身份运行脚本
3. 微信数据目录可访问

**执行步骤：**

```bash
# 进入 memorial skill 目录
cd "C:\Users\33303\.agents\skills\memorial-skill-builder\data\skills\Freyaaaaaa"

# 运行自动提取脚本
python import_wechat_data_auto.py
```

**输出结果：**
- `manual_input/extracted/messages.json` - JSON 格式聊天记录
- `manual_input/extracted/messages.csv` - CSV 格式（可 Excel 打开）
- `manual_input/extracted/Fragrance__Yao_messages.md` - Markdown 格式（可读性好）
- `manual_input/extracted/memory_input.txt` - Memory Extraction 专用格式
- `manual_input/extracted/analysis_report.md` - 统计分析报告

### 方案 B：手动解密（备选）

如果自动密钥提取失败，使用 PyWxDump 手动解密：

```bash
# 克隆 PyWxDump
git clone https://github.com/Aeron1-bit/PyWxDump.git
cd PyWxDump

# 安装依赖
pip install -r requirements.txt

# 提取密钥和解密数据库
python pywxdump/wx_core/wx_info.py  # 提取密钥
python pywxdump/wx_core/decryption.py  # 解密数据库
```

**解密后：**
1. 将解密后的 `de_MSG.db` 复制到 memorial skill 目录
2. 运行 `import_wechat_data_auto.py` 脚本
3. 脚本会检测到已解密的数据库并直接读取

## 依赖安装

```bash
# 安装必需依赖
pip install pycryptodomex pywin32 psutil

# 可选：SQLCipher 支持（用于数据库解密）
pip install pysqlcipher3
```

## 数据导出格式

### JSON 格式

用于程序化处理：

```json
{
  "export_time": "2026-04-05T20:00:00",
  "total_count": 1500,
  "messages": [
    {
      "local_id": 1,
      "msg_svr_id": "1234567890",
      "type": 1,
      "sub_type": 0,
      "create_time": 1712345678,
      "create_time_str": "2024-04-05 12:34:56",
      "is_sender": false,
      "talker": "Fragrance__Yao",
      "content": "你好",
      "display_content": "你好"
    }
  ]
}
```

### CSV 格式

用于数据分析和备份：

| 时间 | 发送者 | 内容 | 消息类型 | 是否本人发送 | 消息ID |
|------|--------|------|----------|-------------|----------|
| 2024-04-05 12:34:56 | Fragrance__Yao | 你好 | 文本 | 否 | 1234567890 |

### Markdown 格式

用于文档展示和人工阅读：

```markdown
# 与 Fragrance__Yao 的聊天记录

导出时间: 2026-04-05 20:00:00
消息数量: 1500

---

## 2024-04-05

### [12:34:56] Fragrance__Yao

你好

---

### [12:35:01] 我

你好呀
```

### Memory Input 格式

简化格式，适合 AI 提取特征：

```
[2024-04-05 12:34:56] Fragrance__Yao: 你好
[2024-04-05 12:35:01] 我: 你好呀
```

## 安全与法律警告

### 使用场景限制

**✅ 合法用途：**
- 为已故亲友创建 memorial skill（ memorial-skill-builder 核心场景）
- 个人数据备份
- 数据分析研究

**❌ 违法用途：**
- 未经授权访问他人数据
- 商业间谍
- 侵犯隐私
- 违反微信服务条款

### 授权要求

1. **死者数据**：需要家属书面授权
2. **本人数据**：仅限创建 memorial skill
3. **他人数据**：严格禁止

### 隐私保护

- 提取的数据仅用于 memorial skill 创建
- 不上传到第三方服务器
- 支持彻底删除（Hard Boundary 3）

## 故障排查

### 密钥提取失败

**原因：**
- 微信未运行
- 权限不足（需要管理员）
- 微信版本不兼容

**解决方案：**
1. 启动微信
2. 右键"以管理员身份运行"脚本
3. 使用手动解密方案

### 数据库读取失败

**原因：**
- 数据库未解密
- 数据库路径错误
- 数据库损坏

**解决方案：**
1. 检查 `de_MSG.db` 是否存在
2. 验证数据库文件头是否为 `SQLite format 3`
3. 使用 PyWxDump 重新解密

### 找不到联系人

**原因：**
- 微信ID拼写错误
- 联系人不在当前数据库
- 群聊和私聊混用

**解决方案：**
1. 确认微信ID（在微信中查看）
2. 导出联系人列表检查
3. 分别查询私聊和群聊

## 下一步

数据提取成功后：

1. **查看分析报告** - 了解聊天统计
2. **人工筛选** - 选择有代表性的消息（至少 50 条）
3. **收集照片** - 保存相关图片到 `manual_input/screenshots/`
4. **运行 Memory Extraction** - 提取人物特征
5. **填充 Persona Prompt** - 根据分析结果生成
6. **测试对话** - 验证模拟效果

## 技术支持

- PyWxDump: https://github.com/Aeron1-bit/PyWxDump
- SQLCipher: https://www.zetetic.net/sqlcipher/
- Memorial Skill Builder: `references/repo-map.md`
