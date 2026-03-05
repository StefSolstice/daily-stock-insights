#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技术指标计算模块
"""

from typing import List, Dict, Tuple
import math


def calculate_rsi(prices: List[float], period: int = 14) -> float:
    """计算 RSI 相对强弱指标
    
    Args:
        prices: 收盘价列表（从旧到新）
        period: 计算周期，默认14天
    
    Returns:
        RSI 值 (0-100)
    """
    if len(prices) < period + 1:
        return 0
    
    gains = []
    losses = []
    
    for i in range(1, len(prices)):
        change = prices[i] - prices[i-1]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))
    
    # 计算平均涨幅和跌幅
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    if avg_loss == 0:
        return 100
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return round(rsi, 2)


def calculate_macd(prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
    """计算 MACD 指数平滑异同移动平均线
    
    Args:
        prices: 收盘价列表
        fast: 快线周期
        slow: 慢线周期
        signal: 信号线周期
    
    Returns:
        包含 MACD, signal, histogram 的字典
    """
    if len(prices) < slow + signal:
        return {"macd": 0, "signal": 0, "histogram": 0}
    
    # 计算 EMA
    def calc_ema(data: List[float], period: int) -> List[float]:
        ema = [data[0]]
        multiplier = 2 / (period + 1)
        for price in data[1:]:
            ema.append((price - ema[-1]) * multiplier + ema[-1])
        return ema
    
    ema_fast = calc_ema(prices, fast)
    ema_slow = calc_ema(prices, slow)
    
    # 计算 MACD 线
    macd_line = [ema_fast[i] - ema_slow[i] for i in range(len(ema_fast))]
    
    # 计算信号线
    signal_line = calc_ema(macd_line[-slow:], signal)
    
    # 计算柱状图
    histogram = macd_line[-1] - signal_line[-1]
    
    return {
        "macd": round(macd_line[-1], 4),
        "signal": round(signal_line[-1], 4),
        "histogram": round(histogram, 4)
    }


def calculate_bollinger_bands(prices: List[float], period: int = 20, std_dev: int = 2) -> Dict:
    """计算布林带
    
    Args:
        prices: 收盘价列表
        period: 移动平均周期
        std_dev: 标准差倍数
    
    Returns:
        包含 upper, middle, lower 的字典
    """
    if len(prices) < period:
        return {"upper": 0, "middle": 0, "lower": 0}
    
    recent_prices = prices[-period:]
    
    # 计算中轨（20日均线）
    middle = sum(recent_prices) / period
    
    # 计算标准差
    variance = sum((p - middle) ** 2 for p in recent_prices) / period
    std = variance ** 0.5
    
    # 计算上轨和下轨
    upper = middle + (std_dev * std)
    lower = middle - (std_dev * std)
    
    return {
        "upper": round(upper, 2),
        "middle": round(middle, 2),
        "lower": round(lower, 2),
        "bandwidth": round((upper - lower) / middle * 100, 2)
    }


def calculate_kdj(highs: List[float], lows: List[float], closes: List[float], period: int = 9) -> Dict:
    """计算 KDJ 随机指标
    
    Args:
        highs: 最高价列表
        lows: 最低价列表
        closes: 收盘价列表
        period: 计算周期
    
    Returns:
        包含 K, D, J 的字典
    """
    if len(closes) < period:
        return {"k": 50, "d": 50, "j": 50}
    
    # 计算 RSV
    recent_highs = highs[-period:]
    recent_lows = lows[-period:]
    recent_closes = closes[-period:]
    
    highest = max(recent_highs)
    lowest = min(recent_lows)
    
    if highest == lowest:
        rsv = 50
    else:
        rsv = (recent_closes[-1] - lowest) / (highest - lowest) * 100
    
    # 计算 K, D, J 值（简化版）
    k = rsv
    d = k * 0.5 + 50 * 0.5  # 简化计算
    j = 3 * k - 2 * d
    
    return {
        "k": round(k, 2),
        "d": round(d, 2),
        "j": round(j, 2)
    }


def calculate_atr(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> float:
    """计算 ATR 平均真实波幅
    
    Args:
        highs: 最高价列表
        lows: 最低价列表
        closes: 收盘价列表
        period: 计算周期
    
    Returns:
        ATR 值
    """
    if len(closes) < period + 1:
        return 0
    
    true_ranges = []
    for i in range(1, len(closes)):
        high_low = highs[i] - lows[i]
        high_close = abs(highs[i] - closes[i-1])
        low_close = abs(lows[i] - closes[i-1])
        true_range = max(high_low, high_close, low_close)
        true_ranges.append(true_range)
    
    atr = sum(true_ranges[-period:]) / period
    return round(atr, 2)


def calculate_obv(closes: List[float], volumes: List[float]) -> float:
    """计算 OBV 能量潮
    
    Args:
        closes: 收盘价列表
        volumes: 成交量列表
    
    Returns:
        OBV 值
    """
    if len(closes) != len(volumes) or len(closes) < 2:
        return 0
    
    obv = 0
    for i in range(1, len(closes)):
        if closes[i] > closes[i-1]:
            obv += volumes[i]
        elif closes[i] < closes[i-1]:
            obv -= volumes[i]
    
    return round(obv, 2)


def get_technical_indicators(data: List[Dict]) -> Dict:
    """获取完整的技术指标分析
    
    Args:
        data: 股票数据列表
    
    Returns:
        技术指标分析结果
    """
    if not data:
        return {}
    
    # 提取数据
    closes = [float(d.get('close', 0)) for d in data]
    highs = [float(d.get('high', 0)) for d in data]
    lows = [float(d.get('low', 0)) for d in data]
    vols = [float(d.get('vol', 0)) for d in data]
    
    # 反转顺序（从旧到新）
    closes = list(reversed(closes))
    highs = list(reversed(highs))
    lows = list(reversed(lows))
    vols = list(reversed(vols))
    
    # 计算各项指标
    result = {}
    
    # RSI
    result['rsi'] = calculate_rsi(closes)
    result['rsi_status'] = "超买" if result['rsi'] > 70 else "超卖" if result['rsi'] < 30 else "正常"
    
    # MACD
    macd = calculate_macd(closes)
    result['macd'] = macd['macd']
    result['macd_signal'] = macd['signal']
    result['macd_histogram'] = macd['histogram']
    result['macd_status'] = "金叉" if macd['histogram'] > 0 else "死叉"
    
    # 布林带
    bb = calculate_bollinger_bands(closes)
    result['bollinger_upper'] = bb['upper']
    result['bollinger_middle'] = bb['middle']
    result['bollinger_lower'] = bb['lower']
    result['bollinger_bandwidth'] = bb['bandwidth']
    
    # KDJ
    kdj = calculate_kdj(highs, lows, closes)
    result['kdj_k'] = kdj['k']
    result['kdj_d'] = kdj['d']
    result['kdj_j'] = kdj['j']
    
    # ATR
    result['atr'] = calculate_atr(highs, lows, closes)
    
    # OBV
    result['obv'] = calculate_obv(closes, vols)
    
    return result


def generate_technical_report(data: List[Dict], symbol: str) -> str:
    """生成技术分析报告
    
    Args:
        data: 股票数据
        symbol: 股票代码
    
    Returns:
        报告文本
    """
    indicators = get_technical_indicators(data)
    
    if not indicators:
        return "数据不足，无法进行分析"
    
    report = f"""
📊 技术分析报告 - {symbol}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 RSI 相对强弱指标
   数值: {indicators.get('rsi', 0)}
   状态: {indicators.get('rsi_status', 'N/A')}

📉 MACD 指数平滑异同移动平均线
   MACD: {indicators.get('macd', 0)}
   Signal: {indicators.get('macd_signal', 0)}
   Histogram: {indicators.get('macd_histogram', 0)}
   状态: {indicators.get('macd_status', 'N/A')}

📐 布林带 (Bollinger Bands)
   上轨: {indicators.get('bollinger_upper', 0)}
   中轨: {indicators.get('bollinger_middle', 0)}
   下轨: {indicators.get('bollinger_lower', 0)}
   带宽: {indicators.get('bollinger_bandwidth', 0)}%

🎯 KDJ 随机指标
   K: {indicators.get('kdj_k', 0)}
   D: {indicators.get('kdj_d', 0)}
   J: {indicators.get('kdj_j', 0)}

📊 ATR 平均真实波幅
   数值: {indicators.get('atr', 0)}

🔊 OBV 能量潮
   数值: {indicators.get('obv', 0)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 建议:
"""
    
    # 生成建议
    rsi = indicators.get('rsi', 50)
    macd_hist = indicators.get('macd_histogram', 0)
    kdj_k = indicators.get('kdj_k', 50)
    
    if rsi > 70:
        report += "   • RSI 超买区域，注意回调风险\n"
    elif rsi < 30:
        report += "   • RSI 超卖区域，可能存在反弹机会\n"
    
    if macd_hist > 0:
        report += "   • MACD 金叉，短期看涨\n"
    else:
        report += "   • MACD 死叉，短期看跌\n"
    
    if kdj_k > 80:
        report += "   • KDJ 超买区域\n"
    elif kdj_k < 20:
        report += "   • KDJ 超卖区域\n"
    
    return report


if __name__ == "__main__":
    # 测试
    test_data = [
        {"trade_date": "20260227", "close": 10.90, "high": 10.92, "low": 10.84, "vol": 612227.96},
        {"trade_date": "20260226", "close": 10.87, "high": 10.91, "low": 10.80, "vol": 712730.19},
        {"trade_date": "20260225", "close": 10.86, "high": 10.95, "low": 10.78, "vol": 1063134.87},
        {"trade_date": "20260224", "close": 10.91, "high": 10.95, "low": 10.88, "vol": 602512.40},
        {"trade_date": "20260213", "close": 10.91, "high": 10.99, "low": 10.90, "vol": 555047.36},
    ]
    
    print(generate_technical_report(test_data, "000001.SZ"))