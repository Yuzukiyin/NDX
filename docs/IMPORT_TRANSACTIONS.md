# 交易记录CSV导入模板

## 新格式（推荐）

文件名: `transactions.csv`

```csv
fund_code,transaction_date,transaction_type,amount,note
000001,2024-01-01,买入,1000,定投
000002,2024-01-05,买入,500,一次性投资
000001,2024-02-01,买入,1000,定投
```

### 字段说明

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| fund_code | 文本 | 基金代码（6位数字） | `000001` |
| transaction_date | 日期 | 交易日期（YYYY-MM-DD） | `2024-01-01` |
| transaction_type | 文本 | 交易类型（买入/卖出） | `买入` |
| amount | 数字 | 交易金额（元） | `1000` |
| note | 文本 | 备注说明（可选） | `定投` |

### 导入规则

1. **净值自动匹配**：系统会自动根据交易日期查询对应的净值
2. **交易日处理**：非交易日会自动使用下一个交易日的净值
3. **份额计算**：份额 = 金额 / 净值（保留2位小数）
4. **待确认处理**：如果净值未抓取，会创建待确认记录

## 旧格式（兼容）

文件名: `transactions_old.csv`

```csv
fund_code,fund_name,transaction_date,transaction_type,shares,unit_nav,note
000001,华夏成长,2024-01-01,买入,100,1.5000,定投
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| fund_code | 文本 | 基金代码 |
| fund_name | 文本 | 基金名称 |
| transaction_date | 日期 | 交易日期 |
| transaction_type | 文本 | 买入/卖出 |
| shares | 数字 | 份额（保留2位小数） |
| unit_nav | 数字 | 单位净值（保留4位小数） |
| note | 文本 | 备注 |

## 使用方法

### 方法1: Web界面导入（推荐）

1. 准备CSV文件（使用新格式）
2. 登录系统
3. 进入"工具"页面
4. 点击"导入交易记录"
5. 选择CSV文件
6. 查看导入结果

### 方法2: 命令行导入

```bash
# 激活环境
conda activate NDX

# 使用本地管理工具
cd scripts
python local_manager.py
# 选择选项2

# 或直接导入
cd Web/backend
python -c "from import_transactions import import_from_csv; import_from_csv('../../transactions.csv')"
```

## 常见问题

### Q: 导入失败，显示"净值未抓取"？
**A**: 先抓取净值数据：
1. Web界面：工具 -> 同步净值数据
2. 命令行：`python scripts/sync_nav_data.py`

### Q: 如何批量导入大量交易？
**A**: 
1. 推荐使用新格式（只需基金代码和金额）
2. 系统会自动批量查询净值
3. 分批导入（每批1000条以内）

### Q: 日期格式错误？
**A**: 必须使用 `YYYY-MM-DD` 格式，例如：
- ✅ `2024-01-01`
- ✗ `2024/01/01`
- ✗ `01-01-2024`

### Q: 如何处理节假日交易？
**A**: 系统会自动处理：
- 非交易日 -> 使用下一个交易日净值
- 周末 -> 使用下周一净值
- 节假日 -> 使用节后第一个交易日净值

### Q: 导入后发现数据错误？
**A**: 
1. 删除错误记录（通过Web界面）
2. 修改CSV文件
3. 重新导入

## 示例数据

### 定投计划记录
```csv
fund_code,transaction_date,transaction_type,amount,note
000001,2024-01-01,买入,1000,沪深300定投
000001,2024-02-01,买入,1000,沪深300定投
000001,2024-03-01,买入,1000,沪深300定投
000002,2024-01-15,买入,500,中证500定投
000002,2024-02-15,买入,500,中证500定投
```

### 一次性投资
```csv
fund_code,transaction_date,transaction_type,amount,note
000003,2024-01-10,买入,10000,抄底
000003,2024-06-15,卖出,5000,止盈
```

### 混合策略
```csv
fund_code,transaction_date,transaction_type,amount,note
000001,2024-01-01,买入,1000,定投
000001,2024-01-15,买入,5000,加仓
000001,2024-02-01,买入,1000,定投
000002,2024-01-20,买入,3000,一次性
000002,2024-02-01,买入,500,定投
```

## 高级用法

### 从其他平台导出

#### 天天基金
1. 登录天天基金
2. 我的资产 -> 交易记录
3. 导出Excel
4. 转换为CSV格式（保留需要的列）

#### 蚂蚁财富
1. 我的 -> 总资产
2. 基金 -> 交易记录
3. 导出并转换格式

#### 银行App
大部分银行App支持导出交易明细，转换为标准CSV格式即可

### 批量处理脚本

Python脚本示例：
```python
import pandas as pd

# 读取原始数据
df = pd.read_excel('原始交易.xlsx')

# 转换格式
new_df = pd.DataFrame({
    'fund_code': df['基金代码'],
    'transaction_date': pd.to_datetime(df['日期']).dt.strftime('%Y-%m-%d'),
    'transaction_type': df['类型'].map({'申购': '买入', '赎回': '卖出'}),
    'amount': df['金额'],
    'note': '导入'
})

# 保存为CSV
new_df.to_csv('transactions.csv', index=False, encoding='utf-8-sig')
```

## 数据验证

导入前建议验证：
1. 基金代码是否正确（6位数字）
2. 日期格式是否标准
3. 金额是否合理（大于0）
4. 类型是否为"买入"或"卖出"

使用Excel公式验证：
```excel
# 验证基金代码（A列）
=IF(LEN(A2)=6, "✓", "✗")

# 验证日期格式（B列）
=IF(ISDATE(B2), "✓", "✗")

# 验证金额（D列）
=IF(AND(ISNUMBER(D2), D2>0), "✓", "✗")
```

## 相关文档

- [API文档](./API.md) - 查看交易相关API
- [快速开始](./QUICKSTART.md) - 完整使用流程
- [开发指南](./DEVELOPMENT.md) - 自定义导入逻辑
