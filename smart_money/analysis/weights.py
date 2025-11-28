from typing import Dict


def dynamic_weight_adjustment(market_condition: str, volatility_level: str) -> Dict[str, float]:
    weights = {
        '13F機構持倉': 0.25,
        '內部人交易': 0.20,
        '成交量分析': 0.20,
        '技術分析': 0.15,
        'ETF流向': 0.10,
        '宏觀環境': 0.05,
        '加密鯨魚': 0.05,
    }

    if market_condition == '牛市':
        weights['成交量分析'] += 0.05
        weights['技術分析'] += 0.05
        weights['13F機構持倉'] -= 0.10
    elif market_condition == '熊市':
        weights['13F機構持倉'] += 0.10
        weights['內部人交易'] += 0.05
        weights['成交量分析'] -= 0.10
        weights['技術分析'] -= 0.05

    if volatility_level == '高波動':
        weights['技術分析'] -= 0.05
        weights['宏觀環境'] += 0.05

    # Normalize in case of drift
    total = sum(weights.values())
    if total != 1.0:
        weights = {k: v / total for k, v in weights.items()}

    return weights
