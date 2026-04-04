#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('Z:/Work/WorkDock/01_Active/autodocweb_v2/templates/dept_form.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix updateDynamicRequiredFields
old_func = '''function updateDynamicRequiredFields() {
            if (deptKey !== 'risk_compliance') return;

            const templateSelect = document.getElementById('templateSelect');
            if (!templateSelect) return;

            const templateKey = templateSelect.value;
            const config = RISK_TEMPLATE_REQUIRED[templateKey];'''

new_func = '''function updateDynamicRequiredFields() {
            if (deptKey !== 'risk_compliance') return;
            if (typeof RISK_TEMPLATE_REQUIRED === 'undefined') return;

            const templateSelect = document.getElementById('templateSelect');
            if (!templateSelect) return;

            const templateKey = templateSelect.value;
            const config = RISK_TEMPLATE_REQUIRED[templateKey];'''

if old_func in content:
    content = content.replace(old_func, new_func)
    print('Fixed updateDynamicRequiredFields')
else:
    print('Pattern not found for updateDynamicRequiredFields')

# Write back
with open('Z:/Work/WorkDock/01_Active/autodocweb_v2/templates/dept_form.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done')
