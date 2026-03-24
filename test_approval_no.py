# -*- coding: utf-8 -*-
"""
测试批复编号解析功能
"""
import re

def parse_approval_no(approval_no):
    """
    解析批复编号
    输入: 〔2026〕007
    输出: {'year': '2026', 'seq': '007', 'full': '鲁金资管审复〔2026〕007号'}
    """
    approval_no = approval_no.strip()
    
    # 解析格式：〔2026〕007
    match = re.search(r'〔(\d{4})〕(\d+)', approval_no)
    if match:
        year = match.group(1)
        seq = match.group(2).zfill(3)  # 确保3位
        return {
            'approval_year': year,
            'approval_seq': seq,
            'doc_full_no': f"鲁金资管审复〔{year}〕{seq}号"
        }
    return None

# 测试用例
test_cases = [
    "〔2026〕007",
    "〔2025〕042",
    "〔2024〕1",
    "〔2023〕999",
]

print("=" * 60)
print("批复编号解析测试")
print("=" * 60)

for test in test_cases:
    result = parse_approval_no(test)
    if result:
        print(f"\n输入: {test}")
        print(f"  年份: {result['approval_year']}")
        print(f"  序号: {result['approval_seq']}")
        print(f"  完整文号: {result['doc_full_no']}")
    else:
        print(f"\n输入: {test}")
        print(f"  ❌ 解析失败")

print("\n" + "=" * 60)
print("测试完成")
