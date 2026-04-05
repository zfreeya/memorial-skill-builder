# -*- coding: utf-8 -*-
"""
微信数据库读取器 - 读取解密后的 SQLite 数据库

核心功能：
1. 连接解密后的 .db 文件
2. 查询 MSG 表获取聊天记录
3. 查询 Contact 表获取联系人信息
4. 支持分页、筛选、排序

参考 PyWxDump/db/dbMSG.py
"""

import sqlite3
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ChatMessage:
    """聊天记录数据结构"""
    local_id: int
    msg_svr_id: str
    type: int
    sub_type: int
    create_time: int
    is_sender: bool
    talker: str  # 微信ID
    content: str
    display_content: str
    bytes_extra: Optional[bytes] = None
    
    @property
    def create_time_datetime(self) -> datetime:
        """转换为 datetime 对象"""
        return datetime.fromtimestamp(self.create_time)
    
    @property
    def create_time_str(self) -> str:
        """格式化时间字符串"""
        return self.create_time_datetime.strftime('%Y-%m-%d %H:%M:%S')


class WeChatDbReader:
    """微信数据库读取器"""
    
    # 消息类型常量
    TYPE_TEXT = 1  # 文本消息
    TYPE_IMAGE = 3  # 图片消息
    TYPE_VOICE = 34  # 语音消息
    TYPE_VIDEO = 43  # 视频消息
    TYPE_EMOJI = 47  # 表情消息
    TYPE_LOCATION = 48  # 位置消息
    TYPE_LINK = 49  # 链接消息
    TYPE_FILE = 6  # 文件消息
    
    def __init__(self, db_path: str):
        """
        Args:
            db_path: 解密后的数据库文件路径
        """
        self.db_path = db_path
        self.conn = None
        self._connect()
    
    def _connect(self):
        """连接数据库"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            logger.info(f"成功连接数据库: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"数据库连接失败: {e}")
            raise
    
    def _add_indexes(self):
        """添加索引提高查询性能"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_MSG_StrTalker ON MSG(StrTalker);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_MSG_CreateTime ON MSG(CreateTime);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_MSG_StrTalker_CreateTime ON MSG(StrTalker, CreateTime);")
            self.conn.commit()
            logger.info("数据库索引创建成功")
        except sqlite3.Error as e:
            logger.warning(f"索引创建失败（可能已存在）: {e}")
    
    def get_contact_list(self) -> List[Dict]:
        """获取联系人列表"""
        cursor = self.conn.cursor()
        
        # 尝试查询 Contact 表
        try:
            cursor.execute("""
                SELECT UserName, Alias, NickName, Remark, 
                       Type, VerifyFlag, ChatRoomData
                FROM Contact
                WHERE Type = 1 OR Type = 3
                LIMIT 1000
            """)
        except sqlite3.OperationalError:
            # 表不存在，返回空列表
            return []
        
        contacts = []
        for row in cursor.fetchall():
            contact = {
                'wxid': row['UserName'],
                'alias': row['Alias'],
                'nickname': row['NickName'],
                'remark': row['Remark'],
                'type': row['Type'],
                'is_chatroom': '@chatroom' in (row['UserName'] or '')
            }
            contacts.append(contact)
        
        logger.info(f"获取到 {len(contacts)} 个联系人")
        return contacts
    
    def get_chat_messages(self, talker_wxid: str, 
                       limit: int = 1000,
                       offset: int = 0,
                       msg_type: Optional[int] = None) -> List[ChatMessage]:
        """获取与特定联系人的聊天记录
        
        Args:
            talker_wxid: 联系人微信ID
            limit: 返回数量限制
            offset: 偏移量（分页）
            msg_type: 消息类型筛选（可选）
        
        Returns:
            聊天记录列表
        """
        cursor = self.conn.cursor()
        
        # 构建查询
        sql = """
            SELECT localId, MsgSvrID, Type, SubType, 
                   CreateTime, IsSender, StrTalker, 
                   StrContent, DisplayContent, BytesExtra
            FROM MSG
            WHERE StrTalker = ?
        """
        params = [talker_wxid]
        
        if msg_type:
            sql += " AND Type = ?"
            params.append(msg_type)
        
        sql += " ORDER BY CreateTime ASC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        try:
            cursor.execute(sql, params)
        except sqlite3.OperationalError as e:
            logger.error(f"查询失败: {e}")
            return []
        
        messages = []
        for row in cursor.fetchall():
            msg = ChatMessage(
                local_id=row['localId'],
                msg_svr_id=str(row['MsgSvrID']),
                type=row['Type'],
                sub_type=row['SubType'],
                create_time=row['CreateTime'],
                is_sender=bool(row['IsSender']),
                talker=row['StrTalker'] or '',
                content=row['StrContent'] or '',
                display_content=row['DisplayContent'] or '',
                bytes_extra=row['BytesExtra']
            )
            messages.append(msg)
        
        logger.info(f"获取到 {len(messages)} 条聊天记录")
        return messages
    
    def get_chat_count(self, talker_wxid: Optional[str] = None) -> Dict[str, int]:
        """获取聊天记录数量统计
        
        Args:
            talker_wxid: 联系人微信ID（None 则统计所有）
        
        Returns:
            {wxid: count} 或 {'total': total_count}
        """
        cursor = self.conn.cursor()
        
        if talker_wxid:
            cursor.execute("""
                SELECT StrTalker, COUNT(*) AS count
                FROM MSG
                WHERE StrTalker = ?
                GROUP BY StrTalker
            """, (talker_wxid,))
        else:
            cursor.execute("""
                SELECT StrTalker, COUNT(*) AS count
                FROM MSG
                GROUP BY StrTalker
                ORDER BY count DESC
            """)
        
        result = {}
        for row in cursor.fetchall():
            result[row['StrTalker']] = row['count']
        
        # 获取总数
        cursor.execute("SELECT COUNT(*) FROM MSG")
        result['total'] = cursor.fetchone()[0]
        
        return result
    
    def get_messages_by_keyword(self, keyword: str, limit: int = 100) -> List[ChatMessage]:
        """按关键词搜索消息
        
        Args:
            keyword: 搜索关键词
            limit: 返回数量限制
        
        Returns:
            匹配的消息列表
        """
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT localId, MsgSvrID, Type, SubType, 
                   CreateTime, IsSender, StrTalker, 
                   StrContent, DisplayContent, BytesExtra
            FROM MSG
            WHERE StrContent LIKE ?
            ORDER BY CreateTime DESC
            LIMIT ?
        """, (f'%{keyword}%', limit))
        
        messages = []
        for row in cursor.fetchall():
            msg = ChatMessage(
                local_id=row['localId'],
                msg_svr_id=str(row['MsgSvrID']),
                type=row['Type'],
                sub_type=row['SubType'],
                create_time=row['CreateTime'],
                is_sender=bool(row['IsSender']),
                talker=row['StrTalker'] or '',
                content=row['StrContent'] or '',
                display_content=row['DisplayContent'] or '',
                bytes_extra=row['BytesExtra']
            )
            messages.append(msg)
        
        logger.info(f"搜索关键词 '{keyword}' 找到 {len(messages)} 条消息")
        return messages
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            logger.info("数据库连接已关闭")
    
    def __enter__(self):
        """上下文管理器支持"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器支持"""
        self.close()
