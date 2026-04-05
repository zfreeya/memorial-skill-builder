# -*- coding: utf-8 -*-
"""
微信数据导出器 - 将微信数据导出为 memorial skill 可用格式

支持格式：
- JSON: 用于 memory extraction
- CSV: 用于数据分析和备份
- Markdown: 用于文档展示
- 自定义格式: 根据 memory prompt 需求定制
"""

import json
import csv
import logging
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime

from .db_reader import ChatMessage

logger = logging.getLogger(__name__)


class WeChatDataExporter:
    """微信数据导出器"""
    
    def __init__(self, output_dir: str):
        """
        Args:
            output_dir: 输出目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export_messages_to_json(self, messages: List[ChatMessage], 
                                filename: str = "messages.json") -> str:
        """导出消息为 JSON 格式
        
        Args:
            messages: 聊天记录列表
            filename: 输出文件名
        
        Returns:
            输出文件路径
        """
        output_path = self.output_dir / filename
        
        data = {
            'export_time': datetime.now().isoformat(),
            'total_count': len(messages),
            'messages': []
        }
        
        for msg in messages:
            msg_dict = {
                'local_id': msg.local_id,
                'msg_svr_id': msg.msg_svr_id,
                'type': msg.type,
                'sub_type': msg.sub_type,
                'create_time': msg.create_time,
                'create_time_str': msg.create_time_str,
                'is_sender': msg.is_sender,
                'talker': msg.talker,
                'content': msg.content,
                'display_content': msg.display_content
            }
            data['messages'].append(msg_dict)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"成功导出 {len(messages)} 条消息到 {output_path}")
        return str(output_path)
    
    def export_messages_to_csv(self, messages: List[ChatMessage],
                               filename: str = "messages.csv") -> str:
        """导出消息为 CSV 格式
        
        Args:
            messages: 聊天记录列表
            filename: 输出文件名
        
        Returns:
            输出文件路径
        """
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            
            # 写入表头
            writer.writerow([
                '时间', '发送者', '内容', '消息类型',
                '是否本人发送', '消息ID'
            ])
            
            # 写入数据
            for msg in messages:
                writer.writerow([
                    msg.create_time_str,
                    '我' if msg.is_sender else msg.talker,
                    msg.content,
                    self._get_type_name(msg.type),
                    '是' if msg.is_sender else '否',
                    msg.msg_svr_id
                ])
        
        logger.info(f"成功导出 {len(messages)} 条消息到 {output_path}")
        return str(output_path)
    
    def export_messages_to_markdown(self, messages: List[ChatMessage],
                                    filename: str = "messages.md",
                                    title: str = "聊天记录") -> str:
        """导出消息为 Markdown 格式
        
        Args:
            messages: 聊天记录列表
            filename: 输出文件名
            title: 文档标题
        
        Returns:
            输出文件路径
        """
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n\n")
            f.write(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"消息数量: {len(messages)}\n\n")
            f.write("---\n\n")
            
            # 按时间分组
            current_date = None
            for msg in messages:
                msg_date = msg.create_time_datetime.date()
                
                # 日期标题
                if current_date != msg_date:
                    current_date = msg_date
                    f.write(f"\n## {current_date}\n\n")
                
                # 消息内容
                sender = '我' if msg.is_sender else msg.talker
                f.write(f"### [{msg.create_time_str}] {sender}\n\n")
                f.write(f"{msg.content}\n\n")
                f.write("---\n\n")
        
        logger.info(f"成功导出 {len(messages)} 条消息到 {output_path}")
        return str(output_path)
    
    def export_for_memory_extraction(self, messages: List[ChatMessage],
                                    filename: str = "memory_input.txt") -> str:
        """导出为 memory extraction 专用格式
        
        Args:
            messages: 聊天记录列表
            filename: 输出文件名
        
        Returns:
            输出文件路径
        """
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# 聊天记录用于 Memory Extraction\n\n")
            f.write(f"# 导出时间: {datetime.now().isoformat()}\n")
            f.write(f"# 总消息数: {len(messages)}\n\n")
            
            for msg in messages:
                # 简洁格式，适合 AI 提取 memory
                sender = '我' if msg.is_sender else msg.talker
                f.write(f"[{msg.create_time_str}] {sender}: {msg.content}\n")
        
        logger.info(f"成功导出 {len(messages)} 条消息到 {output_path}")
        return str(output_path)
    
    def export_contact_list(self, contacts: List[Dict],
                           filename: str = "contacts.json") -> str:
        """导出联系人列表
        
        Args:
            contacts: 联系人列表
            filename: 输出文件名
        
        Returns:
            输出文件路径
        """
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(contacts, f, ensure_ascii=False, indent=2)
        
        logger.info(f"成功导出 {len(contacts)} 个联系人到 {output_path}")
        return str(output_path)
    
    def _get_type_name(self, msg_type: int) -> str:
        """获取消息类型名称"""
        type_map = {
            1: '文本',
            3: '图片',
            34: '语音',
            43: '视频',
            47: '表情',
            48: '位置',
            49: '链接',
            6: '文件'
        }
        return type_map.get(msg_type, f'未知({msg_type})')
