# 股票数据本地服务

## 功能简介
- 每天定时（默认17:00）从yfinance抓取目标股票的日线数据，存入本地数据库
- 提供RESTful API供本地回测程序查询股票数据
- 支持Docker一键部署

## 目录结构
```
app/
  db.py         # 数据库操作
  fetcher.py    # yfinance数据抓取
  scheduler.py  # 定时任务
  main.py       # FastAPI主入口
requirements.txt
Dockerfile
README.md
```

## 安装与运行

### 1. 本地运行
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 2. Docker 部署
```bash
docker build -t stock-data-svr .
docker run -d -p 8000:8000 --name stock-data-svr stock-data-svr
```

## API 示例

- 查询某只股票区间K线：
  - `GET /stocks/688041.SS?start=2025-05-01&end=2025-05-08`
- 查询最新价格：
  - `GET /stocks/688041.SS/latest`
- 手动触发数据抓取：
  - `POST /stocks/stocks/688041.SS/fetch`
- 手动触发数据抓取（指定日期）：
  - `POST /stocks/stocks/688041.SS/fetch?start=2025-01-01&end=2025-05-08`
- 手动触发定时任务（更新所有目标股票）：
  - `POST /scheduler/trigger`

## 使用curl示例

```bash
# 查询股票K线数据
curl "http://localhost:8000/stocks/688041.SS?start=2025-05-01&end=2025-05-08"

# 查询最新价格
curl "http://localhost:8000/stocks/688041.SS/latest"

# 手动触发数据抓取指定股票最近30天的数据
curl -X POST "http://localhost:8000/stocks/688041.SS/fetch"

# 抓取指定股票特定日期范围的数据
curl -X POST "http://localhost:8000/stocks/688041.SS/fetch?start=2025-01-01&end=2025-05-08"

# 手动触发定时任务，更新所有目标股票数据
curl -X POST "http://localhost:8000/scheduler/trigger"

## 配置
- 目标股票列表可在 `app/scheduler.py` 的 `TARGET_SYMBOLS` 修改
- 数据库存储路径可通过环境变量 `DB_PATH` 设置，默认为 `stock_data.db` 