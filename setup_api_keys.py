"""
API密钥自动化配置脚本
帮助用户快速设置和验证所有数据源API密钥
"""
import os
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def print_header(title):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def print_step(step_num, total, description):
    """打印步骤"""
    print(f"\n[步骤 {step_num}/{total}] {description}")

def check_api_key(key_name, env_var):
    """检查API密钥是否已配置"""
    key_value = os.environ.get(env_var)
    if key_value and len(key_value) > 5:
        print(f"  ✓ {key_name}: 已配置 ({key_value[:4]}...{key_value[-4:]})")
        return True
    else:
        print(f"  ✗ {key_name}: 未配置")
        return False

def setup_env_file():
    """创建或更新 .env 文件"""
    print_header("创建 .env 配置文件")
    
    env_file = project_root / ".env"
    
    if env_file.exists():
        print(f"\n⚠️  发现现有 .env 文件: {env_file}")
        response = input("是否覆盖? (y/n): ").strip().lower()
        if response != 'y':
            print("保留现有配置")
            return
    
    # .env 模板
    env_template = """# QT量化交易系统 - API密钥配置
# 创建时间: 2025-11-25
# 
# 请将 "YOUR_KEY_HERE" 替换为您申请到的实际API密钥
# 如果暂时不使用某个数据源,可以保持为空

# ========================================
# 1. Alpha Vantage (基本面+备用价格数据)
# ========================================
# 申请地址: https://www.alphavantage.co/support/#api-key
# 免费额度: 500次/天
ALPHA_VANTAGE_API_KEY=YOUR_KEY_HERE

# ========================================
# 2. Financial Modeling Prep (财报数据)
# ========================================
# 申请地址: https://site.financialmodelingprep.com/developer
# 免费额度: 250次/天
FMP_API_KEY=YOUR_KEY_HERE

# ========================================
# 3. NewsAPI (新闻情绪分析)
# ========================================
# 申请地址: https://newsapi.org/register
# 免费额度: 100次/天
NEWS_API_KEY=YOUR_KEY_HERE

# ========================================
# 4. Finnhub (金融新闻和数据)
# ========================================
# 申请地址: https://finnhub.io/register
# 免费额度: 60次/分钟
FINNHUB_API_KEY=YOUR_KEY_HERE

# ========================================
# 5. FRED (宏观经济数据)
# ========================================
# 申请地址: https://fred.stlouisfed.org/docs/api/api_key.html
# 免费额度: 无限制
FRED_API_KEY=YOUR_KEY_HERE

# ========================================
# 6. Tradier (期权数据,可选)
# ========================================
# 申请地址: https://developer.tradier.com/getting_started
# 免费额度: 沙盒无限
# 注意: 可以不配置,使用Yahoo Finance期权数据代替
TRADIER_API_KEY=YOUR_KEY_HERE

# ========================================
# 社交媒体API (可选,暂不需要)
# ========================================
# Reddit API
# REDDIT_CLIENT_ID=
# REDDIT_CLIENT_SECRET=
# REDDIT_USER_AGENT=

# StockTwits API
# STOCKTWITS_API_KEY=

# ========================================
# 其他配置
# ========================================
# 数据缓存目录
DATA_CACHE_DIR=./data_cache

# 日志级别 (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO
"""
    
    # 写入文件
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(env_template)
    
    print(f"\n✓ .env 文件已创建: {env_file}")
    print("\n📝 下一步:")
    print("1. 使用文本编辑器打开 .env 文件")
    print("2. 将 YOUR_KEY_HERE 替换为您申请到的实际API密钥")
    print("3. 保存文件")
    print("4. 重新运行此脚本验证配置")

def setup_gitignore():
    """更新 .gitignore 确保不提交密钥"""
    print_header("更新 .gitignore")
    
    gitignore_file = project_root / ".gitignore"
    
    # 需要忽略的文件
    ignore_patterns = [
        ".env",
        "*.env",
        ".env.local",
        ".env.*.local",
        "config/api_keys.json",
        "api_keys.json"
    ]
    
    existing_patterns = set()
    if gitignore_file.exists():
        with open(gitignore_file, 'r', encoding='utf-8') as f:
            existing_patterns = set(line.strip() for line in f if line.strip() and not line.startswith('#'))
    
    # 添加缺失的模式
    new_patterns = [p for p in ignore_patterns if p not in existing_patterns]
    
    if new_patterns:
        with open(gitignore_file, 'a', encoding='utf-8') as f:
            f.write("\n# API密钥和敏感配置 (自动添加)\n")
            for pattern in new_patterns:
                f.write(f"{pattern}\n")
        print(f"\n✓ .gitignore 已更新,添加了 {len(new_patterns)} 个忽略规则")
    else:
        print("\n✓ .gitignore 已包含所有必要的忽略规则")

def load_env_file():
    """加载 .env 文件"""
    env_file = project_root / ".env"
    
    if not env_file.exists():
        return False
    
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                if value and value != 'YOUR_KEY_HERE':
                    os.environ[key] = value
    
    return True

def check_all_keys():
    """检查所有API密钥配置"""
    print_header("检查API密钥配置")
    
    # 尝试加载 .env 文件
    env_loaded = load_env_file()
    if env_loaded:
        print("✓ 已从 .env 文件加载配置")
    else:
        print("⚠️  未找到 .env 文件,检查环境变量...")
    
    print("\nAPI密钥状态:")
    
    keys_config = {
        'Alpha Vantage': 'ALPHA_VANTAGE_API_KEY',
        'Financial Modeling Prep': 'FMP_API_KEY',
        'NewsAPI': 'NEWS_API_KEY',
        'Finnhub': 'FINNHUB_API_KEY',
        'FRED': 'FRED_API_KEY',
        'Tradier (可选)': 'TRADIER_API_KEY'
    }
    
    configured_count = 0
    total_count = len(keys_config)
    
    for key_name, env_var in keys_config.items():
        if check_api_key(key_name, env_var):
            configured_count += 1
    
    print(f"\n总计: {configured_count}/{total_count} 个密钥已配置")
    
    if configured_count == 0:
        print("\n⚠️  没有配置任何API密钥!")
        print("请先申请API密钥并配置到 .env 文件")
        print("参考: API_KEYS_SETUP_GUIDE.md")
        return False
    elif configured_count < total_count:
        print(f"\n⚠️  还有 {total_count - configured_count} 个密钥未配置")
        print("建议配置所有密钥以获得完整功能")
        return True
    else:
        print("\n✓ 所有密钥已配置完成!")
        return True

def interactive_setup():
    """交互式配置向导"""
    print_header("API密钥交互式配置向导")
    
    print("\n欢迎使用API密钥配置向导!")
    print("本向导将帮助您逐步配置所有数据源的API密钥")
    
    print("\n您有两种配置方式:")
    print("1. 手动编辑 .env 文件 (推荐)")
    print("2. 交互式输入密钥")
    
    choice = input("\n请选择 (1/2): ").strip()
    
    if choice == '1':
        setup_env_file()
        print("\n请编辑 .env 文件后重新运行此脚本")
        return
    
    elif choice == '2':
        print("\n请准备好您的API密钥,我们将逐个输入...")
        
        keys_to_setup = {
            'ALPHA_VANTAGE_API_KEY': {
                'name': 'Alpha Vantage',
                'url': 'https://www.alphavantage.co/support/#api-key',
                'required': True
            },
            'FMP_API_KEY': {
                'name': 'Financial Modeling Prep',
                'url': 'https://site.financialmodelingprep.com/developer',
                'required': True
            },
            'NEWS_API_KEY': {
                'name': 'NewsAPI',
                'url': 'https://newsapi.org/register',
                'required': False
            },
            'FINNHUB_API_KEY': {
                'name': 'Finnhub',
                'url': 'https://finnhub.io/register',
                'required': False
            },
            'FRED_API_KEY': {
                'name': 'FRED',
                'url': 'https://fred.stlouisfed.org/docs/api/api_key.html',
                'required': False
            },
            'TRADIER_API_KEY': {
                'name': 'Tradier',
                'url': 'https://developer.tradier.com/getting_started',
                'required': False
            }
        }
        
        env_content = []
        configured = 0
        
        for env_var, info in keys_to_setup.items():
            print(f"\n--- {info['name']} ---")
            print(f"申请地址: {info['url']}")
            
            if info['required']:
                print("⚠️  此密钥为必需项")
            else:
                skip = input("是否跳过? (y/n): ").strip().lower()
                if skip == 'y':
                    env_content.append(f"# {env_var}=\n")
                    continue
            
            api_key = input(f"请输入 {info['name']} API密钥: ").strip()
            
            if api_key and len(api_key) > 5:
                env_content.append(f"{env_var}={api_key}\n")
                os.environ[env_var] = api_key
                configured += 1
                print(f"✓ {info['name']} 密钥已设置")
            else:
                env_content.append(f"# {env_var}=\n")
                print(f"⚠️  跳过 {info['name']}")
        
        # 保存到 .env 文件
        if env_content:
            env_file = project_root / ".env"
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write("# QT量化交易系统 - API密钥配置\n")
                f.write("# 创建时间: 2025-11-25\n\n")
                f.writelines(env_content)
            
            print(f"\n✓ 已配置 {configured} 个API密钥")
            print(f"✓ 配置已保存到: {env_file}")

def main():
    """主函数"""
    print_header("QT量化交易系统 - API密钥配置工具")
    print("\n本工具将帮助您:")
    print("1. 创建 .env 配置文件")
    print("2. 更新 .gitignore (防止泄露密钥)")
    print("3. 检查API密钥配置状态")
    
    # 步骤1: 更新 .gitignore
    print_step(1, 3, "更新 .gitignore")
    setup_gitignore()
    
    # 步骤2: 检查是否已有配置
    print_step(2, 3, "检查现有配置")
    has_config = check_all_keys()
    
    # 步骤3: 交互式配置
    if not has_config:
        print_step(3, 3, "配置API密钥")
        interactive_setup()
    else:
        print_step(3, 3, "配置完成")
        print("\n✓ API密钥配置已完成!")
        print("\n下一步:")
        print("1. 运行 test_all_data_sources.py 测试数据源")
        print("2. 查看 ENABLE_DATA_SOURCES_GUIDE.md 启用数据源")
    
    print("\n" + "=" * 60)
    print("配置完成!按任意键退出...")
    input()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户取消操作")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
