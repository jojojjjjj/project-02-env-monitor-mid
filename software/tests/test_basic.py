# test_basic.py - 基础测试
# Basic Tests for Air Butler Project

import sys
import time

# 测试工具函数
def test_utils():
    """测试工具函数"""
    print("测试工具函数...")

    # 测试AQI计算
    from utils import AQICalculator

    calc = AQICalculator()
    aqi, level, color = calc.calculate_aqi(25)
    assert aqi < 50, "AQI计算错误"
    assert level == "优", "AQI等级错误"
    print(f"  ✓ AQI计算: PM2.5=25 → AQI={aqi}, {level}")

    # 测试环形缓冲区
    from utils import RingBuffer

    buf = RingBuffer(5)
    for i in range(7):
        buf.put(i)

    assert len(buf) == 5, "环形缓冲区大小错误"
    assert buf.peek() == 2, "环形缓冲区数据错误"
    print(f"  ✓ 环形缓冲区: 大小={len(buf)}, 首元素={buf.peek()}")

    print("工具函数测试通过!")


def test_data_validator():
    """测试数据验证器"""
    print("测试数据验证器...")

    from utils import DataValidator

    validator = DataValidator()

    # 测试温度验证
    assert validator.validate_temperature(25) == True
    assert validator.validate_temperature(100) == False
    print("  ✓ 温度验证通过")

    # 测试湿度验证
    assert validator.validate_humidity(50) == True
    assert validator.validate_humidity(150) == False
    print("  ✓ 湿度验证通过")

    print("数据验证器测试通过!")


def test_statistics():
    """测试统计计算器"""
    print("测试统计计算器...")

    from utils import StatisticsCalculator

    stats = StatisticsCalculator(max_samples=10)

    # 添加样本
    for i in range(5):
        stats.add_sample(20 + i)

    result = stats.get_stats()
    assert result['min'] == 20, "最小值错误"
    assert result['max'] == 24, "最大值错误"
    assert abs(result['avg'] - 22) < 0.1, "平均值错误"

    print(f"  ✓ 统计: min={result['min']}, max={result['max']}, avg={result['avg']:.1f}")
    print("统计计算器测试通过!")


def test_json_helper():
    """测试JSON辅助类"""
    print("测试JSON辅助类...")

    from utils import JSONHelper

    # 测试序列化
    obj = {"temp": 25.5, "hum": 60}
    json_str = JSONHelper.dumps(obj)
    assert "temp" in json_str, "JSON序列化错误"
    print(f"  ✓ 序列化: {json_str}")

    # 测试反序列化
    parsed = JSONHelper.loads(json_str)
    assert parsed['temp'] == 25.5, "JSON反序列化错误"
    print(f"  ✓ 反序列化: temp={parsed['temp']}")

    print("JSON辅助类测试通过!")


def test_sensor_reading():
    """测试传感器读数类"""
    print("测试传感器读数类...")

    try:
        from sensors import SensorReading

        reading = SensorReading()
        reading.temperature = 25.5
        reading.humidity = 60.0
        reading.pm25 = 45
        reading.valid = True

        # 测试to_dict
        data = reading.to_dict()
        assert data['temperature'] == 25.5, "to_dict错误"
        assert data['valid'] == True, "valid字段错误"

        print(f"  ✓ SensorReading: temp={reading.temperature}, pm25={reading.pm25}")
        print("传感器读数类测试通过!")

    except ImportError:
        print("  ⚠ SensorReading不可用(MicroPython模块)")


def test_calculations():
    """测试计算函数"""
    print("测试计算函数...")

    from utils import calculate_dew_point, calculate_heat_index

    # 测试露点计算
    dew_point = calculate_dew_point(25, 60)
    assert dew_point is not None, "露点计算错误"
    assert 15 <= dew_point <= 18, "露点值异常"
    print(f"  ✓ 露点: 25°C/60% → {dew_point:.1f}°C")

    # 测试体感温度
    heat_index = calculate_heat_index(30, 70)
    assert heat_index is not None, "体感温度计算错误"
    assert heat_index > 30, "体感温度应高于实际温度"
    print(f"  ✓ 体感温度: 30°C/70% → {heat_index:.1f}°C")

    print("计算函数测试通过!")


def run_all_tests():
    """运行所有测试"""
    print("=" * 50)
    print("Air Butler 基础测试")
    print("=" * 50)
    print()

    start_time = time.time()

    try:
        test_utils()
        test_data_validator()
        test_statistics()
        test_json_helper()
        test_sensor_reading()
        test_calculations()

        elapsed = time.time() - start_time
        print()
        print("=" * 50)
        print(f"所有测试通过! 耗时: {elapsed:.2f}秒")
        print("=" * 50)
        return 0

    except AssertionError as e:
        print()
        print("=" * 50)
        print(f"测试失败: {e}")
        print("=" * 50)
        return 1
    except Exception as e:
        print()
        print("=" * 50)
        print(f"测试错误: {e}")
        print("=" * 50)
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
