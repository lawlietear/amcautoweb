# -*- coding: utf-8 -*-
"""
格式化工具类
整合金额、日期等格式化功能
"""

import datetime
import pandas as pd


class FormatUtils:
    """格式化工具类"""
    
    @staticmethod
    def amount_to_chinese(amount):
        """
        金额转中文大写（完整修复版）
        支持到万亿级别
        """
        if amount is None or amount == '':
            return ''
        
        try:
            # 移除千分位逗号
            amount_str = str(amount).replace(',', '').replace(' ', '')
            amount_float = float(amount_str)
            
            # 处理负数
            if amount_float < 0:
                return '负' + FormatUtils.amount_to_chinese(-amount_float)
            
            # 整数和小数部分
            integer_part = int(amount_float)
            decimal_part = round((amount_float - integer_part) * 100)
            
            if integer_part == 0:
                result = '零元'
            else:
                result = FormatUtils._int_to_chinese(integer_part)
            
            # 处理小数部分
            num_cn = ['零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖']
            jiao = decimal_part // 10
            fen = decimal_part % 10
            
            if jiao == 0 and fen == 0:
                result += '整'
            else:
                if jiao > 0:
                    result += num_cn[jiao] + '角'
                elif integer_part > 0 and fen > 0:
                    # 有分无角且整数部分非零时补零
                    result += '零'
                if fen > 0:
                    result += num_cn[fen] + '分'
            
            return result
        except:
            return ''
    
    @staticmethod
    def _int_to_chinese(n):
        """
        将整数转换为中文大写（支持万、亿）
        """
        if n == 0:
            return '零元'
        
        num_cn = ['零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖']
        units = ['', '拾', '佰', '仟']
        big_units = ['', '万', '亿', '万亿']
        
        # 按4位分组处理
        groups = []
        while n > 0:
            groups.append(n % 10000)
            n //= 10000
        
        result = ''
        for i, group in enumerate(groups):
            if group > 0:
                group_str = FormatUtils._four_digit_to_chinese(group, num_cn, units)
                if result:
                    # 判断是否需要补零：低位有空缺分组、低位不足4位，
                    # 或紧邻的个位组为1000但缺佰拾个位
                    if (groups[i-1] == 0 or
                        (0 < groups[i-1] < 1000)):
                        result = group_str + big_units[i] + '零' + result
                    else:
                        result = group_str + big_units[i] + result
                else:
                    result = group_str + big_units[i] + result

        # 清理连续零
        result = result.replace('零零', '零')
        
        return result + '元'
    
    @staticmethod
    def _four_digit_to_chinese(n, num_cn, units):
        """
        将4位以内数字转换为中文
        """
        if n == 0:
            return ''
        
        result = ''
        zero_flag = False
        
        for i in range(3, -1, -1):
            divisor = 10 ** i
            digit = n // divisor
            n %= divisor
            
            if digit == 0:
                if not zero_flag and result:
                    zero_flag = True
            else:
                if zero_flag:
                    result += '零'
                    zero_flag = False
                result += num_cn[digit] + units[i]
        
        return result
    
    @staticmethod
    def format_thousand(num):
        """
        格式化为千分位（保留2位小数）
        """
        if not num or num == '':
            return '0.00'
        try:
            num_float = float(str(num).replace(',', ''))
            return "{:,.2f}".format(num_float)
        except:
            return str(num)
    
    @staticmethod
    def excel_date_to_str(excel_date):
        """
        Excel日期序列号或datetime转YYYY年MM月DD日格式
        """
        if pd.isna(excel_date) or excel_date == "":
            return ""
        
        try:
            # 如果是数字（Excel序列号，如45827）
            if isinstance(excel_date, (int, float)):
                delta = datetime.timedelta(days=int(excel_date))
                date_obj = datetime.datetime(1899, 12, 30) + delta
                return date_obj.strftime("%Y年%m月%d日")
            
            # 如果是datetime对象或pandas Timestamp
            elif isinstance(excel_date, (datetime.datetime, pd.Timestamp)):
                return excel_date.strftime("%Y年%m月%d日")
            
            # 如果是字符串
            elif isinstance(excel_date, str):
                if '年' in excel_date:
                    return excel_date  # 已经是中文格式则保留
                # 尝试解析 2026-01-12 格式
                try:
                    dt = datetime.datetime.strptime(excel_date.split()[0], "%Y-%m-%d")
                    return dt.strftime("%Y年%m月%d日")
                except:
                    return excel_date
            else:
                return str(excel_date)
                
        except Exception as e:
            print(f"日期转换警告: {excel_date} -> {e}")
            return str(excel_date)
    
    @staticmethod
    def safe_filename(filename):
        """
        清理文件名中的非法字符
        """
        import re
        return re.sub(r'[<>:"/\\|?*]', '', filename)
    
    @staticmethod
    def meeting_seq_to_str(meeting_seq_val):
        """
        会议次数处理：强制转为纯阿拉伯数字（2.0 -> 2）
        """
        try:
            # 先转float去掉小数，再转int，再转str
            return str(int(float(meeting_seq_val)))
        except:
            return str(meeting_seq_val)
