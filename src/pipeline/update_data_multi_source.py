"""
增量更新数据 - 使用多数据源系统
自动尝试多个免费数据源，相互补充
"""
import argparse
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.data.multi_providers import create_multi_source_client
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="更新股票数据 (多数据源增量更新)")
    parser.add_argument("symbol", help="股票代码 (例如: TSLA)")
    parser.add_argument("--days", type=int, default=30, help="更新最近N天的数据 (默认30天)")
    parser.add_argument("--output", help="输出文件路径")
    
    args = parser.parse_args()
    
    # 设置输出路径
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = project_root / "data" / f"sample_{args.symbol.lower()}.csv"
    
    logger.info("=" * 70)
    logger.info(f"📊 更新 {args.symbol} 数据 (多数据源模式)")
    logger.info("=" * 70)
    
    # 确定更新的日期范围
    start_date = None
    end_date = datetime.now().date()
    
    if output_path.exists():
        try:
            existing_data = pd.read_csv(output_path)
            if not existing_data.empty:
                # 获取最后日期
                last_date_str = existing_data.iloc[-1]['date']
                last_date = datetime.strptime(last_date_str, '%Y-%m-%d').date()
                days_since = (end_date - last_date).days
                
                logger.info(f"📂 现有数据最新日期: {last_date} ({days_since}天前)")
                
                if days_since <= 1:
                    logger.info("✓ 数据已是最新,无需更新")
                    print("\n✓ 数据已是最新!")
                    return
                
                # 从最后日期的后一天开始更新
                start_date = last_date + timedelta(days=1)
                logger.info(f"📅 增量更新: {start_date} 至 {end_date}")
        except Exception as e:
            logger.warning(f"⚠️ 无法读取现有数据: {e}")
            start_date = end_date - timedelta(days=args.days)
    else:
        # 首次下载
        start_date = end_date - timedelta(days=args.days)
        logger.info(f"📅 首次下载最近 {args.days} 天数据")
    
    # 检查是否需要更新
    if start_date > end_date:
        logger.info("✓ 数据已是最新，无需更新")
        print("\n✓ 数据已是最新!")
        return
    
    logger.info("")
    logger.info("🌐 使用多数据源系统获取数据")
    logger.info("   将自动尝试: Yahoo Finance → Alpha Vantage → Twelve Data")
    logger.info("")
    
    # 获取数据
    try:
        client = create_multi_source_client()
        fetched = client.fetch_daily_history(
            symbol=args.symbol,
            start=start_date,
            end=end_date
        )
        
        if fetched.empty:
            logger.error("❌ 未获取到任何数据")
            print("\n❌ 数据获取失败，未获取到任何数据")
            sys.exit(1)
        
        # 标准化格式
        fetched['date'] = fetched['date'].astype(str)
        fetched[['open', 'high', 'low', 'close']] = fetched[['open', 'high', 'low', 'close']].astype(float)
        fetched['volume'] = fetched['volume'].astype(int)
        
        logger.info(f"✓ 成功获取 {len(fetched)} 条新数据")
        logger.info(f"  日期范围: {fetched.iloc[0]['date']} 至 {fetched.iloc[-1]['date']}")
        
        # 合并数据
        if output_path.exists():
            existing = pd.read_csv(output_path)
            combined = pd.concat([existing, fetched], ignore_index=True)
            logger.info(f"  合并前: {len(existing)} 条")
        else:
            combined = fetched
            logger.info("  新建数据文件")
        
        # 去重并排序
        combined.drop_duplicates(subset='date', keep='last', inplace=True)
        combined.sort_values(by='date', inplace=True)
        
        # 保存
        output_path.parent.mkdir(parents=True, exist_ok=True)
        combined.to_csv(output_path, index=False)
        
        logger.info("")
        logger.info("=" * 70)
        logger.info("✅ 数据更新完成!")
        logger.info(f"   总行数: {len(combined)}")
        logger.info(f"   日期范围: {combined.iloc[0]['date']} 至 {combined.iloc[-1]['date']}")
        logger.info(f"   保存路径: {output_path}")
        logger.info("=" * 70)
        
        print(f"\n✅ 数据已更新到: {output_path}")
        print(f"   总行数: {len(combined)}")
        print(f"   最新日期: {combined.iloc[-1]['date']}")
        
    except Exception as e:
        logger.error(f"❌ 数据更新失败: {e}")
        print(f"\n❌ 数据更新失败: {e}")
        print("\n💡 提示:")
        print("  1. 检查网络连接")
        print("  2. 如果所有数据源都失败，可能遇到API频率限制")
        print("  3. 可以配置备用数据源的API密钥:")
        print("     - Alpha Vantage: https://www.alphavantage.co/support/#api-key")
        print("     - Twelve Data: https://twelvedata.com/pricing")
        print("  4. 设置环境变量:")
        print("     $env:ALPHA_VANTAGE_API_KEY = 'your_key'")
        print("     $env:TWELVE_DATA_API_KEY = 'your_key'")
        sys.exit(1)


if __name__ == "__main__":
    main()
