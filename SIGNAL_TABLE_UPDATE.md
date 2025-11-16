# 📋 策略信号详情表功能更新

## 更新时间
2025年11月15日

## 更新内容

### ✨ 新增功能
HTML报告中新增 **策略信号详情表**,显示最近30条策略执行信号的完整信息。

### 📊 表格内容

表格包含以下5列信息:

| 列名 | 说明 | 示例 |
|------|------|------|
| 日期 | 信号生成日期 | 2025-11-15 |
| 操作 | 交易动作(BUY/SELL) | 📈 BUY / 📉 SELL |
| 价格 | 建议交易价格 | $245.67 |
| 数量 | 建议交易数量 | 100 |
| 原因 | 策略触发原因 | 金叉买入信号 |

### 🎨 设计特点

1. **颜色区分**
   - BUY信号: 绿色背景 + 📈 图标
   - SELL信号: 红色背景 + 📉 图标

2. **表格样式**
   - 紫色渐变表头
   - 鼠标悬停高亮行
   - 圆角边框设计
   - 与整体报告风格统一

3. **数据展示**
   - 时间倒序排列(最新的在最前)
   - 最近30条信号
   - 价格格式化($XX.XX)
   - 清晰的文字说明

### 📁 修改文件

**k:\QT\src\visualization\quick_report.py**

#### 代码变更:

1. **数据准备部分** (第92-115行)
```python
# 准备信号表格数据 (最近30条)
recent_signals = signals.tail(30).copy()
recent_signals = recent_signals.sort_values('date', ascending=False)

# 格式化日期和价格
recent_signals['date_str'] = recent_signals['date'].dt.strftime('%Y-%m-%d')
recent_signals['price_str'] = recent_signals['price'].apply(lambda x: f'${x:.2f}')

# 生成信号表格HTML
signals_table_html = ""
for _, row in recent_signals.iterrows():
    action = row['action']
    action_class = 'buy-action' if action == 'BUY' else 'sell-action'
    action_icon = '📈' if action == 'BUY' else '📉'
    
    signals_table_html += f"""
    <tr>
        <td>{row['date_str']}</td>
        <td><span class="{action_class}">{action_icon} {action}</span></td>
        <td class="price-cell">{row['price_str']}</td>
        <td>{row['quantity']}</td>
        <td class="reason-cell">{row['reason']}</td>
    </tr>
    """
```

2. **CSS样式部分** (第162-214行)
```css
/* 信号表格样式 */
.signals-table {
    background: white;
    border-radius: 15px;
    padding: 30px;
    margin-bottom: 30px;
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}
.signals-table h2 {
    color: #333;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 3px solid #667eea;
}
table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
}
th {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 15px;
    text-align: left;
    font-weight: 600;
}
td {
    padding: 12px 15px;
    border-bottom: 1px solid #f0f0f0;
}
tr:hover {
    background: #f8f9fa;
}
.buy-action {
    color: #00CC96;
    font-weight: bold;
    padding: 5px 10px;
    background: rgba(0, 204, 150, 0.1);
    border-radius: 5px;
    display: inline-block;
}
.sell-action {
    color: #EF553B;
    font-weight: bold;
    padding: 5px 10px;
    background: rgba(239, 85, 59, 0.1);
    border-radius: 5px;
    display: inline-block;
}
.price-cell {
    font-weight: bold;
    color: #333;
    text-align: right;
}
.reason-cell {
    font-size: 0.9em;
    color: #666;
    max-width: 300px;
}
```

3. **HTML结构部分** (第268-285行)
```html
<div class="signals-table">
    <h2>📋 最近30条策略信号</h2>
    <table>
        <thead>
            <tr>
                <th>日期</th>
                <th>操作</th>
                <th>价格</th>
                <th>数量</th>
                <th>原因</th>
            </tr>
        </thead>
        <tbody>
            {signals_table_html}
        </tbody>
    </table>
</div>
```

### 🚀 使用方法

1. **生成报告**
```bash
generate_html_report.bat
```

或直接运行:
```bash
.\.venv\Scripts\python.exe src\visualization\quick_report.py
```

2. **查看结果**
- 报告会自动在浏览器中打开
- 滚动到底部查看 **"📋 最近30条策略信号"** 表格
- 可以看到每条信号的完整信息

### 📈 应用场景

1. **策略审计**: 查看具体每次信号的触发时间和原因
2. **信号验证**: 检查建议价格和数量是否合理
3. **决策回顾**: 分析历史信号的执行情况
4. **性能追踪**: 观察信号频率和交易模式

### 🎯 数据来源

- **信号数据**: `k:\QT\backtest_results\daily\signals_daily.csv`
- **总信号数**: 342条
- **显示范围**: 最近30条(按日期倒序)

### ⚙️ 技术细节

- **数据处理**: pandas DataFrame切片和排序
- **日期格式**: YYYY-MM-DD (易读格式)
- **价格格式**: $XXX.XX (美元格式,保留2位小数)
- **排序方式**: 日期降序(最新的在最上面)
- **表格容器**: 独立的白色卡片样式

### 🔄 后续优化建议

1. **分页功能**: 当前固定显示30条,可增加分页查看更多历史
2. **筛选功能**: 可按操作类型(BUY/SELL)筛选
3. **导出功能**: 添加导出为CSV/Excel的按钮
4. **搜索功能**: 按日期范围或原因搜索特定信号
5. **统计汇总**: 在表格底部添加BUY/SELL总数统计

## ✅ 测试结果

- ✅ 报告生成成功
- ✅ 表格正确显示30条信号
- ✅ 日期格式正确(YYYY-MM-DD)
- ✅ 价格格式正确($XXX.XX)
- ✅ BUY/SELL颜色区分清晰
- ✅ 鼠标悬停效果正常
- ✅ 样式与整体报告统一

## 📝 文件位置

**生成的报告**: `k:\QT\TSLA_report_YYYYMMDD_HHMMSS.html`

最新报告: `k:\QT\TSLA_report_20251115_100958.html`

---

**功能完成时间**: 2025年11月15日 10:09
**开发者**: GitHub Copilot
