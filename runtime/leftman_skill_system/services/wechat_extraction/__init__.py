# -*- coding: utf-8 -*-
"""
微信数据提取服务 - 集成 PyWxDump 能力

技术原理：
1. 内存注入：从微信进程内存读取 32 字节 AES 密钥
2. SQLCipher 解密：使用密钥解密加密的 .db 文件
3. 数据查询：直接读取 MSG 表获取聊天记录

依赖项：
- pycryptodomex: AES 解密
- pywin32: Windows API 调用（ReadProcessMemory）
- psutil: 进程管理

警告：
- 仅用于合法的数据提取（已故人物的纪念技能创建）
- 需要用户明确授权
- 不违反任何隐私法律法规
"""

from .key_extractor import WeChatKeyExtractor
from .db_reader import WeChatDbReader
from .exporter import WeChatDataExporter

__all__ = ['WeChatKeyExtractor', 'WeChatDbReader', 'WeChatDataExporter']
