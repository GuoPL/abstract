# -*- coding: utf-8 -*-
import re
s = '井号也常出现在一行的开头，或者位于完整指令之后，这类情况表示符号后面的是注解文字，不会被执行。 '
r=re.split('，',s)

print ' '.join(r)
