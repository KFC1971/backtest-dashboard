from datetime import datetime
from typing import Dict, Any

from .data.collector import DataCollector
from .analysis.dimensions import (
    analyze_13f_holdings,
    analyze_insider_activity,
    analyze_volume_profile,
    analyze_technical_indicators,
    analyze_sector_flows,
    analyze_macro_environment,
    analyze_crypto_whales,
)
from .analysis.weights import dynamic_weight_adjustment
from .analysis.signals import generate_final_signal
from .valuation.engine import ValuationEngine
from .risk.manager import AdvancedRiskManager


class SmartMoneyAnalyzer:
    def __init__(self) -> None:
        self.data_collector = DataCollector()
        self.valuation_engine = ValuationEngine()
        self.risk_manager = AdvancedRiskManager()

    def comprehensive_analysis(self, symbol: str, market_condition: str = "正常", volatility_level: str = "中等") -> Dict[str, Any]:
        raw_data = self.data_collector.collect_all_data(symbol)

        scores: Dict[str, float] = {
            "13F機構持倉": analyze_13f_holdings(raw_data.get("13f_data")),
            "內部人交易": analyze_insider_activity(raw_data.get("insider_data")),
            "成交量分析": analyze_volume_profile(raw_data.get("price_volume")),
            "技術分析": analyze_technical_indicators(raw_data.get("price_volume")),
            "ETF流向": analyze_sector_flows(symbol),
            "宏觀環境": analyze_macro_environment(),
            "加密鯨魚": analyze_crypto_whales(raw_data.get("whale_data")),
        }

        weights = dynamic_weight_adjustment(market_condition, volatility_level)
        final_recommendation, weighted_score, confidence = generate_final_signal(scores, weights)

        valuation = self.valuation_engine.calculate_optimal_entry_price(symbol)

        # Risk sizing based on signal and volatility proxy (ATR-like from price data)
        price_df = raw_data.get("price_volume")
        if price_df is not None and not price_df.empty:
            recent_returns = price_df["Close"].pct_change().dropna()
            volatility = float(recent_returns.rolling(20).std().iloc[-1] or 0.02)
        else:
            volatility = 0.02

        strength_map = {
            "強烈買進": 80,
            "標準買進": 60,
            "小幅買進": 45,
            "觀望": 0,
            "標準賣出": 60,
            "強烈賣出": 80,
        }
        signal_strength = strength_map.get(final_recommendation, 0)

        position_risk = self.risk_manager.calculate_position_size(
            signal_strength=signal_strength,
            confidence=confidence,
            volatility=volatility,
            correlation_adj=0.1,
        )

        result = {
            "symbol": symbol,
            "analysis_date": datetime.now(),
            "scores": scores,
            "weights": weights,
            "weighted_score": round(weighted_score, 2),
            "confidence": round(confidence, 2),
            "recommendation": final_recommendation,
            "valuation": valuation,
            "risk": {
                "suggested_position_risk_percent": round(position_risk * 100, 2)
            },
        }
        return result
