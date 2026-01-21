import sys
import os

# 获取当前脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

# 添加src目录到Python路径（如果需要）
sys.path.append(PROJECT_ROOT)

import git
import pandas as pd
import pytz
from datetime import datetime

try:
    # 直接使用git库获取提交记录，使用绝对路径
    repo_path = os.path.join(PROJECT_ROOT, 'data', 'axios')
    repo = git.Repo(repo_path)
    
    commits = []
    count = 0
    limit = 500  # 减少获取数量
    
    print("正在快速获取axios项目的提交记录（只获取基本信息）...")
    
    # 使用GitPython的快速迭代方式
    for commit in repo.iter_commits():
        if count >= limit:
            break
            
        try:
            # 转换时间格式
            utc_datetime = commit.committed_datetime.astimezone(pytz.UTC)
            datetime_without_tz = utc_datetime.replace(tzinfo=None)
            
            # 只获取绝对必要的基本信息
            commit_data = {
                'sha': commit.hexsha,
                'author_name': commit.author.name,
                'author_email': commit.author.email,
                'datetime': datetime_without_tz,
                'message': commit.message.strip(),
                'insertions': 0,
                'deletions': 0,
                'lines_changed': 0,
                'files_changed': 0,
                'parents': len(commit.parents)
            }
            
            commits.append(commit_data)
            count += 1
            
            if count % 100 == 0:
                print(f"已获取 {count} 条提交记录")
                
        except Exception as e:
            print(f"处理提交 {commit.hexsha} 时出错：{e}")
            continue
    
    print(f"成功获取 {len(commits)} 条提交记录")
    
    # 转换为DataFrame
    commit_df = pd.DataFrame(commits)
    
    # 保存到CSV
    repo_name = 'axios'
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(PROJECT_ROOT, 'data', f'{repo_name}_commits_{timestamp}.csv')
    
    commit_df.to_csv(filename, index=False)
    print(f"提交数据已保存到 {filename}")
    
    # 立即进行分析
    print("\n开始分析提交记录...")
    os.system(f'python -m src.cli analyze "{filename}"')
    
except Exception as e:
    print(f"获取数据时出错：{e}")
    import traceback
    traceback.print_exc()
