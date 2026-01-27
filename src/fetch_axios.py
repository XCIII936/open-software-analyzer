import sys
import os

# 获取当前脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

sys.path.append(PROJECT_ROOT)

# 导入必要的类
from src.data_fetcher import RepoDataFetcher

# 创建数据获取器，使用绝对路径
repo_path = os.path.join(PROJECT_ROOT, 'data', 'axios')
fetcher = RepoDataFetcher(repo_path=repo_path)

# 获取提交历史（限制1000条）
print("正在获取axios项目的提交历史...")
commit_df = fetcher.get_commit_history(limit=1000)

print(f"成功获取 {len(commit_df)} 条提交记录")

# 保存数据
filename = fetcher.save_commit_data(commit_df)
print(f"数据已保存到 {filename}")
