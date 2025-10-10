from typing import Dict, Any, Tuple
import yfinance as yf
import numpy as np
import pandas as pd


class ValuationEngine:
    def __init__(self) -> None:
        pass

    def calculate_pe_valuation(self, symbol: str) -> Tuple[float, float, float]:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.get_info() or {}
        except Exception:
            info = {}
            ticker = yf.Ticker(symbol)
        current_pe = float(info.get("trailingPE") or 0) or 0.0
        eps_ttm = float(info.get("trailingEps") or 0) or 0.0
        try:
            hist = ticker.history(period="5y")
        except Exception:
            hist = pd.DataFrame()
        historical_pe_median = current_pe if current_pe > 0 else 20.0
        industry_pe_median = historical_pe_median
        fair_pe = historical_pe_median * 0.6 + industry_pe_median * 0.4
        last_close = float(hist["Close"].iloc[-1]) if not hist.empty else 0.0
        target_price = eps_ttm * fair_pe if eps_ttm > 0 else last_close
        return float(target_price), float(current_pe), float(fair_pe)

    def calculate_pb_valuation(self, symbol: str) -> Tuple[float, float, float]:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.get_info() or {}
        except Exception:
            info = {}
        current_pb = float(info.get("priceToBook") or 0) or 0.0
        roe = float(info.get("returnOnEquity") or 0)
        fair_pb = max(roe * 0.05, 1.0) if roe else 1.0
        book_value_per_share = float(info.get("bookValue") or 0) or 0.0
        target_price = book_value_per_share * fair_pb if book_value_per_share > 0 else 0.0
        return float(target_price), float(current_pb), float(fair_pb)

    def dcf_valuation(self, symbol: str) -> float:
        try:
            ticker = yf.Ticker(symbol)
            cf = ticker.cashflow
        except Exception:
            cf = None
        if cf is None or cf.empty:
            return 0.0
        # Attempt to get free cash flow series
        fcf_series = None
        for key in ("Free Cash Flow", "FreeCashFlow", "FreeCashFlowUSD"):
            if key in cf.index:
                fcf_series = cf.loc[key]
                break
        if fcf_series is None:
            return 0.0
        free_cash_flows = list(map(float, fcf_series.tail(5).values))
        if not free_cash_flows:
            return 0.0
        base_fcf = free_cash_flows[-1]
        revenue_growth = 0.08
        projected_fcf = []
        for year in range(1, 6):
            growth_rate = revenue_growth * (0.9 ** year)
            projected_fcf.append(base_fcf * (1 + growth_rate) ** year)
        terminal_growth = 0.025
        wacc = 0.09
        enterprise_value = sum([fcf / ((1 + wacc) ** i) for i, fcf in enumerate(projected_fcf, 1)])
        terminal_value = projected_fcf[-1] * (1 + terminal_growth) / (wacc - terminal_growth)
        enterprise_value += terminal_value / ((1 + wacc) ** 5)
        try:
            shares_outstanding = float((ticker.get_info() or {}).get("sharesOutstanding") or 0)
        except Exception:
            shares_outstanding = 0.0
        net_cash = 0.0
        if shares_outstanding <= 0:
            return 0.0
        intrinsic_value = (enterprise_value + net_cash) / shares_outstanding
        return float(intrinsic_value)

    def calculate_technical_support(self, symbol: str) -> float:
        data = yf.Ticker(symbol).history(period="2y")
        if data is None or data.empty:
            return 0.0
        rolling_min = data['Low'].rolling(window=20).min()
        support_levels = []
        for i in range(20, len(data)):
            if data['Low'].iloc[i] == rolling_min.iloc[i]:
                support_levels.append(float(data['Low'].iloc[i]))
        data['VWAP'] = (data['Volume'] * (data['High'] + data['Low'] + data['Close']) / 3).cumsum() / data['Volume'].cumsum()
        vwap_support = float(data['VWAP'].iloc[-60:].min()) if len(data) >= 60 else float(data['VWAP'].iloc[-1])
        ma200 = float(data['Close'].rolling(200).mean().iloc[-1]) if len(data) >= 200 else float(data['Close'].rolling(50).mean().iloc[-1])
        ma200_support = ma200 * 0.95
        support_levels.extend([vwap_support, ma200_support])
        current_price = float(data['Close'].iloc[-1])
        valid_supports = [s for s in support_levels if s < current_price and s > current_price * 0.8]
        return max(valid_supports) if valid_supports else current_price * 0.9

    def get_insider_average_purchase_price(self, symbol: str) -> float:
        # Placeholder: no insider price without premium data; return 0
        return 0.0

    def get_analyst_average_target(self, symbol: str) -> float:
        try:
            info = yf.Ticker(symbol).get_info() or {}
        except Exception:
            info = {}
        target = float(info.get("targetMeanPrice") or 0)
        return float(target)

    def get_current_price(self, symbol: str) -> float:
        try:
            hist = yf.Ticker(symbol).history(period="1d")
        except Exception:
            hist = pd.DataFrame()
        if hist is None or hist.empty:
            return 0.0
        return float(hist["Close"].iloc[-1])

    def get_value_recommendation(self, current_price: float, optimal_entry_price: float, fair_value: float) -> str:
        if current_price <= optimal_entry_price:
            return "估值吸引，可考慮買入"
        if current_price < fair_value:
            return "合理偏低，觀望待回調"
        return "估值偏高，耐心等待"

    def calculate_optimal_entry_price(self, symbol: str) -> Dict[str, Any]:
        pe_price, _, _ = self.calculate_pe_valuation(symbol)
        pb_price, _, _ = self.calculate_pb_valuation(symbol)
        dcf_price = self.dcf_valuation(symbol)
        support_price = self.calculate_technical_support(symbol)

        weights = {
            'pe': 0.20,
            'pb': 0.05,
            'dcf': 0.30,
            'support': 0.10,
            'insider_avg': 0.05,
            'analyst_target': 0.05,
            'margin_of_safety': 0.25,
        }

        insider_avg_price = self.get_insider_average_purchase_price(symbol)
        analyst_target = self.get_analyst_average_target(symbol)
        current_price = self.get_current_price(symbol)

        base_prices = {
            'pe': pe_price,
            'pb': pb_price,
            'dcf': dcf_price,
            'support': support_price,
            'insider_avg': insider_avg_price,
            'analyst_target': analyst_target,
        }

        numerator = sum(base_prices[k] * weights[k] for k in base_prices.keys())
        denom = max(1e-9, 1 - weights['margin_of_safety'])
        fair_value_estimate = numerator / denom
        optimal_entry_price = fair_value_estimate * (1 - weights['margin_of_safety'])

        valuation_result = {
            'current_price': current_price,
            'fair_value_estimate': float(fair_value_estimate),
            'optimal_entry_price': float(optimal_entry_price),
            'upside_potential': float(((fair_value_estimate / max(current_price, 1e-9)) - 1) * 100) if current_price else 0.0,
            'margin_of_safety': float((1 - current_price / max(fair_value_estimate, 1e-9)) * 100) if fair_value_estimate else 0.0,
            'component_prices': base_prices,
            'recommendation': self.get_value_recommendation(current_price, optimal_entry_price, fair_value_estimate),
        }
        return valuation_result
