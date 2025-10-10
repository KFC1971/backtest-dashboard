from typing import Any, Dict, List, Optional
import time
import requests

from ..config import SEC_HEADERS, REQUEST_TIMEOUT


class SECDataAPI:
    base = "https://data.sec.gov"

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        url = f"{self.base}{path}"
        try:
            resp = requests.get(url, headers=SEC_HEADERS, params=params, timeout=REQUEST_TIMEOUT)
            if resp.status_code == 200:
                return resp.json()
            return None
        except requests.RequestException:
            return None

    def _cik_from_symbol(self, symbol: str) -> Optional[str]:
        # Lightweight mapping endpoint
        data = self._get(f"/submissions/CIK{symbol}.json")
        if data and "cik" in data:
            return str(data.get("cik")).zfill(10)
        return None

    def get_13f_holdings(self, symbol: str) -> List[Dict[str, Any]]:
        # Placeholder: 13F requires manager filings; use submissions endpoint as proxy
        # Return minimal structure for scoring functions
        return []

    def get_insider_trading(self, symbol: str) -> List[Dict[str, Any]]:
        cik = self._cik_from_symbol(symbol)
        if not cik:
            return []
        data = self._get(f"/submissions/CIK{cik}.json")
        # Extract recent ownership forms 3/4/5 if present
        if not data:
            return []
        filings = data.get("filings", {}).get("recent", {})
        # This is a simplified placeholder transformation
        results: List[Dict[str, Any]] = []
        for i, form in enumerate(filings.get("form", [])):
            if form in ("3", "4", "5"):
                try:
                    value = float(filings.get("size", [0])[i]) if isinstance(filings.get("size"), list) else 0
                except Exception:
                    value = 0.0
                results.append({
                    "form": form,
                    "value": value,
                })
        return results
