#!/usr/bin/env python

import sys
sys.path.insert(0, '../')#这是从script脚本文件向上走一个文件到mall
sys.path.insert(0, '../apps')

import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'mall.settings'

 # 让django进行初始化设置
import django
django.setup()

from contents.cons import generate_static_index_html


if __name__ == '__main__':
    generate_static_index_html()