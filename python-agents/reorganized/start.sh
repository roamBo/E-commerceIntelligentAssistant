#!/bin/bash
python agent-service.py &     # 后台运行
python main.py                # 前台运行
wait                          # 等待所有后台进程结束
