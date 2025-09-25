#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os

# Windows 환경에서 UTF-8 강제 설정
if sys.platform.startswith('win'):
    import io
    import codecs
    
    # stdout, stderr을 UTF-8로 재설정
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    # 환경변수 설정
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# 메인 애플리케이션 실행
from main import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)