# QuantPro OKX（Hummingbot 级架构）

Python 3.9+ / PyQt5 / OKX v5 REST（官方签名：ISO8601 + Base64 HMAC）。

## 目录

- `main.py` — 入口  
- `core/` — OKX API、引擎、订单、风控、行情缓存、日志  
- `strategies/` — PMM / PMM+ / PMM-NEURAL / AI-LIVE / TWAP 可运行；网格 / DCA / 套利 / 趋势（骨架可扩展）  
- `ui/` — 顶栏、左策略、中 K 线文本、右盘口与下单、底日志  
- `config/.env` — 密钥与风控（勿提交仓库）  
- `monitor/dashboard.py` — 打印最近日志  

## 安装

```bash
cd QuantPro_Hummingbot_OKX
pip install -r requirements.txt
copy config\.env.example config\.env
```

K 线蜡烛图依赖 **PyQtChart**（已写入 `requirements.txt`）。若未安装，中央区会退化为文本列表。

编辑 `config/.env`：填写 `OKX_*`，国内建议配置 `PROXY_HOST`/`PROXY_PORT` 或 `PROXY_URL`。

## 运行

```bash
python main.py
```

```bash
python monitor/dashboard.py
```

## 说明

- **模拟交易**：`OKX_TESTNET=True` 时发送 `x-simulated-trading: 1`（欧易 v5 文档）。  
- **1:1 Hummingbot** 为产品与工程目标；策略逻辑当前为**可运行骨架**，需在 `strategies/` 内按业务补全。  
- 签名实现已按官方 v5，**不使用**错误示例中的 `hexdigest` 时间戳。
