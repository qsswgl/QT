# 架构设计概览

## 系统分层
1. **数据层（Data Layer）**
   - 行情数据：历史、实时、日内数据。
   - 补充因子：财报、期权链、新闻情绪等。
   - 数据仓储：云存储（S3/OSS）+ 列式格式（Parquet/Iceberg），定时增量更新。
   - 初版实现：`YFinanceClient` + `DailyBarIngestor` 拉取 TSLA 日线数据并去重写入本地 CSV，作为后续扩展的雏形。

2. **研究与信号层（Research & Alpha）**
   - 特征工程：技术指标、统计特征、情绪指标。
   - 策略模型：量价动量、机器学习、风险模型。
   - 回测框架：支持事件驱动、滑点/手续费建模、蒙特卡洛压力测试。

3. **执行与风险层（Execution & Risk Management）**
   - 订单管理：下单、监控、失败重试、成交跟踪。
   - 风险控制：头寸限制、止损、仓位调整、杠杆管理。
   - 券商适配：IBKR、Alpaca、TradeStation 等。

4. **监控与运维层（Monitoring & Ops）**
   - 指标监控：收益、回撤、成交、延迟。
   - 告警通道：Slack、邮件、短信。
   - 报告体系：日报、周报、月度总结。

## 数据流
```
数据源 → ETL/清洗 → 特征工程 → 策略信号 → 风险调整 → 订单生成 → 券商执行 → 反馈数据/日志
```

## 关键设计原则
- **模块化**：数据、信号、执行、风险彼此解耦，支持独立迭代。
- **可测试**：每个模块提供单元/集成测试用例。
- **可观测**：统一日志、指标与告警标准。
- **安全与合规**：访问控制、密钥管理、审计追踪。

## 技术栈建议（初版）
| 领域 | 可选技术 |
| --- | --- |
| 语言/框架 | Python 3.11+, FastAPI, Poetry/Pipenv |
| 数据处理 | Pandas, Polars, SQLAlchemy |
| 特征/模型 | NumPy, SciPy, scikit-learn, PyTorch（可选） |
| 回测 | Backtrader, Zipline, QuantConnect Lean |
| 执行 | ib-insync、alpaca-trade-api、自研 FIX 适配器 |
| 调度 | Prefect, Airflow, APScheduler |
| 监控 | Prometheus + Grafana, Sentry |

## 安全与合规要点
- API Key/密钥集中管理（AWS Secrets Manager、HashiCorp Vault）。
- 策略版本管理，重大更改需双人复核。
- 按监管要求保留交易记录与系统日志。

## 扩展方向
- 多策略组合、风险平衡引擎。
- 机器学习模型上线与模型监控（Model Drift）。
- 分布式回测与超参数寻优。
- 期权/期货对冲与风险中性策略。