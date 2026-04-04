#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Read file
with open('Z:/Work/WorkDock/01_Active/autodocweb_v2/templates/dept_form_fixed.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add version marker
content = content.replace('<head>', '<head>\n    <!-- FILE_VERSION: 2025-04-04-FIXED -->', 1)

# 2. Replace the required statistics section
old_line = "const requiredVariables = variables.filter(v => v.required && shouldCountField(v.key));"

new_code = """// Get dynamic required config for risk_compliance
            let dynamicRequiredConfig = null;
            if (deptKey === 'risk_compliance') {
                const templateSelect = document.getElementById('templateSelect');
                if (templateSelect) {
                    dynamicRequiredConfig = RISK_TEMPLATE_REQUIRED[templateSelect.value];
                }
            }

            // Check if field is required
            function isFieldRequired(v) {
                if (deptKey === 'risk_compliance' && dynamicRequiredConfig && dynamicRequiredConfig.hasOwnProperty(v.key)) {
                    return dynamicRequiredConfig[v.key];
                }
                return v.required;
            }

            const requiredVariables = variables.filter(v => isFieldRequired(v) && shouldCountField(v.key));"""

content = content.replace(old_line, new_code)

# Write back
with open('Z:/Work/WorkDock/01_Active/autodocweb_v2/templates/dept_form_fixed.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
print("Has FILE_VERSION:", "FILE_VERSION: 2025-04-04-FIXED" in content)
print("Has isFieldRequired:", "function isFieldRequired" in content)
