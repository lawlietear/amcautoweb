# -*- coding: utf-8 -*-
"""
文档生成核心模块
纯文本填充模式，保留模板原格式
"""

import os
import datetime
from docxtpl import DocxTemplate

from .format_utils import FormatUtils


class DocumentGenerator:
    """
    文档生成器 - 纯文本填充
    只替换模板变量，完全保留模板原有格式
    """
    
    def __init__(self, template_path, output_dir):
        self.template_path = template_path
        self.output_dir = output_dir
        self.generated_cache = set()
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
    
    def generate(self, context, filename_pattern=None):
        """
        生成文档 - 纯文本填充模式
        
        只替换模板中的 {{ 变量 }} 为对应值，完全保留模板原有格式
        
        Args:
            context: 模板变量字典，如 {'doc_full_no': 'xxx', 'debtor_name': 'yyy'}
            filename_pattern: 文件名模板，如 "批复_{doc_full_no}.docx"
        
        Returns:
            (file_path, filename) 或 (None, error_msg)
        """
        try:
            # 检查模板
            print(f"[DocumentGenerator] 检查模板: {self.template_path}")
            if not os.path.exists(self.template_path):
                return None, f"模板文件不存在：{self.template_path}"
            print(f"[DocumentGenerator] 模板存在")
            
            # 检查缓存防重（使用多个可能的唯一标识字段）
            # 风险合规部使用 approval_no + project_name
            # 业务部使用 doc_full_no + debtor_name 或 contract_no + party_b_name
            cache_key_parts = []
            
            # 尝试各种可能的唯一标识字段
            if context.get('approval_no'):
                cache_key_parts.append(str(context.get('approval_no')))
            elif context.get('doc_full_no'):
                cache_key_parts.append(str(context.get('doc_full_no')))
            elif context.get('contract_no'):
                cache_key_parts.append(str(context.get('contract_no')))
            
            if context.get('project_name'):
                cache_key_parts.append(str(context.get('project_name')))
            elif context.get('debtor_name'):
                cache_key_parts.append(str(context.get('debtor_name')))
            elif context.get('party_b_name'):
                cache_key_parts.append(str(context.get('party_b_name')))
            
            cache_key = '_'.join(cache_key_parts) if cache_key_parts else f"default_{datetime.datetime.now().timestamp()}"
            print(f"[DocumentGenerator] cache_key: {cache_key}")
            
            if cache_key in self.generated_cache:
                return None, "已在本批次生成，跳过"
            
            # 加载模板
            print(f"[DocumentGenerator] 加载模板...")
            doc = DocxTemplate(self.template_path)
            print(f"[DocumentGenerator] 模板加载成功")
            
            # 渲染：纯文本替换，保留原格式
            print(f"[DocumentGenerator] 开始渲染...")
            doc.render(context)
            print(f"[DocumentGenerator] 渲染成功")
            
            # 生成文件名
            print(f"[DocumentGenerator] 生成文件名，pattern: {filename_pattern}")
            if filename_pattern:
                filename = self._generate_filename(filename_pattern, context)
            else:
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"批复_{timestamp}.docx"
            
            output_path = os.path.join(self.output_dir, filename)
            print(f"[DocumentGenerator] 输出路径: {output_path}")
            print(f"[DocumentGenerator] 输出目录存在: {os.path.exists(self.output_dir)}")
            
            print(f"[DocumentGenerator] 保存文档...")
            doc.save(output_path)
            print(f"[DocumentGenerator] 保存成功")
            
            self.generated_cache.add(cache_key)
            return output_path, filename
            
        except Exception as e:
            import traceback
            error_msg = f"渲染失败：{str(e)}\n{traceback.format_exc()}"
            print(f"[DocumentGenerator] {error_msg}")
            return None, f"渲染失败：{str(e)}"
    
    def _generate_filename(self, pattern, context):
        """
        根据模板生成文件名 - 简化版
        使用 str.format() 替代手动替换
        """
        from .format_utils import FormatUtils
        import logging
        logger = logging.getLogger('autodocweb')

        filename = pattern

        # 处理特殊占位符 {timestamp}
        if '{timestamp}' in filename:
            filename = filename.replace('{timestamp}', datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))

        # 清理 context 值，确保文件名安全
        safe_context = {}
        for k, v in context.items():
            if v:
                safe_value = str(v)
                # 移除文件名中的非法字符
                safe_value = safe_value.replace('/', '_').replace('\\', '_').replace(':', '_')
                safe_value = safe_value.replace('〔', '').replace('〕', '').replace('号', '')
                safe_context[k] = safe_value
            else:
                safe_context[k] = ''

        try:
            filename = filename.format(**safe_context)
        except KeyError as e:
            logger.warning(f"文件名模板缺少变量: {e}")
        except Exception as e:
            logger.warning(f"文件名模板渲染失败: {e}")

        # 清理非法字符并确保后缀
        filename = FormatUtils.safe_filename(filename)
        return filename if filename.endswith('.docx') else filename + '.docx'
