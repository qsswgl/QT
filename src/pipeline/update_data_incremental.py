"""
改进的数据更新脚本 - 处理Yahoo Finance频率限制

特点:
1. 只更新最近的数据(不是全量)
2. 更长的重试延迟
3. 失败时优雅退出
"""
import argparse
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.data.providers import DailyBarIngestor, YFinanceClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="更新股票数据 (增量更新)")
    parser.add_argument("symbol", help="股票代码")
    parser.add_argument("--days", type=int, default=30, help="更新最近N天的数据 (默认30天)")
    parser.add_argument("--output", help="输出文件路径")
    
    args = parser.parse_args()
    
    # 设置输出路径
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = project_root / "data" / f"sample_{args.symbol.lower()}.csv"
    
    # 默认起始日期
    start_date = datetime.now().date() - timedelta(days=args.days)
    
    # 检查现有数据
    if output_path.exists():
        import pandas as pd
        try:
            existing_data = pd.read_csv(output_path)
            if not existing_data.empty and 'Date' in existing_data.columns:
                last_date = pd.to_datetime(existing_data['Date'].iloc[-1]).date()
                days_since = (datetime.now().date() - last_date).days
                
                logger.info(f"现有数据最新日期: {last_date} ({days_since}天前)")
                
                if days_since <= 1:
                    logger.info("数据已是最新,无需更新")
                    print(f"✓ 数据已是最新 (最后更新: {last_date})")
                    return
                
                # 只更新缺失的天数
                start_date = last_date - timedelta(days=5)  # 多取5天避免遗漏
                logger.info(f"将从 {start_date} 开始增量更新")
        except Exception as e:
            logger.warning(f"无法读取现有数据: {e}")
    else:
        logger.info("首次下载,获取最近30天数据")
    
    # 执行数据更新
    try:
        logger.info(f"正在更新 {args.symbol} 数据...")
        
        client = YFinanceClient()
        ingestor = DailyBarIngestor(
            client=client,
            output_path=output_path
        )
        
        result = ingestor.run(
            symbol=args.symbol,
            start=start_date,
            end=None,
            period=None
        )
        
        if result:
            logger.info(f"✓ 数据更新成功: {output_path}")
            print(f"✓ 数据已更新到: {output_path}")
        else:
            logger.warning("数据更新返回空结果")
            print("⚠️ 数据更新失败,请稍后重试")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"数据更新失败: {e}")
        print(f"⚠️ 数据更新失败: {e}")
        print("💡 提示:")
        print("  1. 可能是Yahoo Finance的频率限制")
        print("  2. 请等待15-30分钟后重试")
        print("  3. 或继续使用现有数据")
        sys.exit(1)


if __name__ == "__main__":
    main()
