# Smart Money Analyzer (七維度聰明資金策略)

一個以免費資料源為主的投資決策引擎，整合七個維度（13F、內部人、成交量、技術分析、ETF流向、宏觀、加密鯨魚），並提供動態權重、最終信號、估值與風險控管建議。

## 快速開始

### 環境
- 已預裝 Python 3.13（若使用其他版本也可）
- 不需要虛擬環境；如需自建，請使用對應系統套件啟用 `venv`

### 安裝依賴
```bash
python3 -m pip install --user -r requirements.txt
```

如需自訂 SEC 要求的 User-Agent：
```bash
export SEC_USER_AGENT="YourApp/1.0 (contact: you@example.com)"
```

### 執行分析（CLI）
```bash
python3 -m smart_money.cli AAPL --market 正常 --vol 中等
```
- `symbol`：股票代號（如 `AAPL`）
- `--market`：市場環境，可選 `牛市`/`熊市`/`正常`
- `--vol`：波動等級，可選 `高波動`/`中等`/`低波動`

### 主要輸出
- `scores`：七維度各自分數（0-100，50為中性）
- `weights`：動態權重
- `weighted_score`：以 50 為中心轉換後的加權總分（可正可負）
- `confidence`：信心度（基於一致性）
- `recommendation`：最終建議（強烈買進/標準買進/小幅買進/觀望/標準賣出/強烈賣出）
- `valuation`：估值與最佳買入價格建議
- `risk.suggested_position_risk_percent`：建議單一部位風險曝險上限（%）

## 專案結構
```
smart_money/
  analyzer.py                # 端到端分析整合
  cli.py                     # CLI 入口
  config.py                  # 設定與常數
  analysis/
    dimensions.py            # 七維度計分
    signals.py               # 信心度與最終信號
    weights.py               # 動態權重調整
  valuation/
    engine.py                # PE/PB/DCF/支撐位與目標價
  risk/
    manager.py               # 部位風險與動態停損
  data/
    collector.py             # 資料收集聚合
    sec.py                   # SEC 相關（簡化佔位）
    whale.py                 # 鯨魚交易（簡化佔位）
```

## 限制與後續規劃
- 目前 `SEC 13F/內部人/鯨魚` 為簡化佔位，供流程運轉；可逐步接入更完整解析與聚合。
- `yfinance` 回傳欄位在不同版/標的可能略有差異，已加上防呆，但仍建議加強資料驗證。
- 建議擴充：
  - 更精確的 13F 機構變化統計（新進/退出/集中度）
  - 內部人交易淨額、人數、時機的完整計分
  - 部門 ETF 流向與宏觀指標實數資料接入
  - 回測框架與績效追蹤（含交易成本）

## 授權
本專案供研究與教育使用，投資有風險，請審慎評估。
