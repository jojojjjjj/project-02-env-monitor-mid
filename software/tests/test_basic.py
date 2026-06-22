#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_basic.py — 温湿度网络时钟 串口集成测试
WiFi Temp/Humidity Network Clock — Serial Integration Test

功能 (What it does):
  连接时钟的调试串口 (USART1, PA9/PA10, 115200 8N1), 读取 N 行输出,
  断言里面包含温度 (°C)、湿度 (%RH)、时间 (HH:MM:SS) 三类信息。

  这是真实串口测试 (NOT a mock) —— 需要时钟固件已烧录运行, 并用 USB 转串口
  (或 ST-Link 虚拟串口) 连到 STM32 的 PA9(TX)/PA10(RX)。

用法 (Usage):
  python tests/test_basic.py --port COM3
  python tests/test_basic.py --port /dev/ttyUSB0 --baud 115200 --lines 20

依赖 (Deps):
  pip install pyserial

通过判据 (Pass criteria):
  采集到的行中, 至少有 1 行同时命中 温度 / 湿度 / 时间 三个正则。
  (固件每秒会打印一行 [CLK] YYYY-MM-DD HH:MM:SS ... T:xx.xx H:xx.xx)
"""
import argparse
import re
import sys
import time

try:
    import serial
except ImportError:
    print("[FAIL] 缺少 pyserial, 请先: pip install pyserial")
    sys.exit(2)


# === 期望的输出行正则 (match firmware printf in main.c) ===
# 固件每秒打印: [CLK] 2026-06-22 12:00:00 OK | T:23.45 H:56.78
RE_TIME = re.compile(r"\b(\d{2}):(\d{2}):(\d{2})\b")            # HH:MM:SS
RE_TEMP = re.compile(r"T[:：]\s*(-?\d+(?:\.\d+)?)\s*C", re.IGNORECASE)   # T:23.45C
RE_HUMI = re.compile(r"H[:：]\s*(-?\d+(?:\.\d+)?)\s*%", re.IGNORECASE)   # H:56.78%


def read_lines(port, baud, n_lines, timeout):
    """打开串口, 读取 n_lines 行, 返回行列表。"""
    lines = []
    try:
        with serial.Serial(port, baud, timeout=1) as ser:
            print(f"[INFO] 已连接 {port} @ {baud}bps, 采集 {n_lines} 行 (超时 {timeout}s)...")
            start = time.time()
            while len(lines) < n_lines and (time.time() - start) < timeout:
                raw = ser.readline()
                if not raw:
                    continue
                try:
                    line = raw.decode("utf-8", errors="replace").strip()
                except Exception:
                    line = str(raw)
                if line:
                    print(f"  > {line}")
                    lines.append(line)
    except serial.SerialException as e:
        print(f"[FAIL] 串口打开失败: {e}")
        print("       检查: 端口号是否正确? 是否被其他串口软件占用? 驱动装了吗?")
        sys.exit(2)
    return lines


def evaluate(lines):
    """检查行列表是否命中时间/温度/湿度三类。返回 (pass, 详情)。"""
    found_time = []
    found_temp = []
    found_humi = []

    for ln in lines:
        if RE_TIME.search(ln):
            found_time.append(ln)
        m_t = RE_TEMP.search(ln)
        if m_t:
            found_temp.append((ln, float(m_t.group(1))))
        m_h = RE_HUMI.search(ln)
        if m_h:
            found_humi.append((ln, float(m_h.group(1))))

    ok = bool(found_time) and bool(found_temp) and bool(found_humi)
    return ok, found_time, found_temp, found_humi


def main():
    ap = argparse.ArgumentParser(description="温湿度网络时钟 串口集成测试")
    ap.add_argument("--port", required=True, help="串口号, 如 COM3 / /dev/ttyUSB0")
    ap.add_argument("--baud", type=int, default=115200, help="波特率 (默认 115200)")
    ap.add_argument("--lines", type=int, default=20, help="采集行数 (默认 20)")
    ap.add_argument("--timeout", type=int, default=30, help="整体超时秒数 (默认 30)")
    args = ap.parse_args()

    print("=" * 60)
    print("温湿度网络时钟 串口集成测试  (BV1tb4y1U7Du)")
    print("=" * 60)

    lines = read_lines(args.port, args.baud, args.lines, args.timeout)

    if not lines:
        print("[FAIL] 未读到任何行。检查固件是否已烧录运行、串口接线 (PA9/PA10)。")
        sys.exit(1)

    ok, t, tp, h = evaluate(lines)

    print("-" * 60)
    print(f"时间行 (time)   : {len(t)} 条")
    print(f"温度行 (temp °C): {len(tp)} 条" + (f"  (示例: {tp[0][1]}°C)" if tp else ""))
    print(f"湿度行 (humi %) : {len(h)} 条" + (f"  (示例: {h[0][1]}%)" if h else ""))
    print("=" * 60)

    if ok:
        print("[PASS] 时钟串口输出正常: 时间 + 温度 + 湿度 三类信息齐全。")
        sys.exit(0)
    else:
        missing = []
        if not t:  missing.append("时间 HH:MM:SS")
        if not tp: missing.append("温度 T:xx.xx C")
        if not h:  missing.append("湿度 H:xx.xx %")
        print(f"[FAIL] 缺少: {', '.join(missing)}")
        print("       可能原因: SHT31 未接线/地址错; WiFi 未连上时钟走 SysTick (仍有时间);")
        print("       或固件未正常运行。检查接线与 hardware/troubleshooting.md。")
        sys.exit(1)


if __name__ == "__main__":
    main()
