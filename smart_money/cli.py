import argparse
import json
from datetime import datetime

from .analyzer import SmartMoneyAnalyzer


def main():
    parser = argparse.ArgumentParser(description="Smart Money Analyzer CLI")
    parser.add_argument("symbol", type=str, help="Ticker symbol, e.g. AAPL")
    parser.add_argument("--market", type=str, default="正常", help="Market condition: 牛市/熊市/正常")
    parser.add_argument("--vol", type=str, default="中等", help="Volatility level: 高波動/中等/低波動")
    args = parser.parse_args()

    analyzer = SmartMoneyAnalyzer()
    result = analyzer.comprehensive_analysis(args.symbol, market_condition=args.market, volatility_level=args.vol)

    def default_serializer(obj):
        if isinstance(obj, (datetime,)):
            return obj.isoformat()
        return str(obj)

    print(json.dumps(result, ensure_ascii=False, indent=2, default=default_serializer))


if __name__ == "__main__":
    main()
