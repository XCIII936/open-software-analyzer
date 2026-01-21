import requests
import pandas as pd
import pytz
from datetime import datetime
import os

# 获取当前脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

# 使用GitHub API获取axios项目的提交记录
def fetch_commits_from_github_api(owner='axios', repo='axios', per_page=100, max_pages=5):
    """使用GitHub API获取提交记录"""
    
    commits = []
    url = f'https://api.github.com/repos/{owner}/{repo}/commits'
    headers = {
        'Accept': 'application/vnd.github.v3+json'
    }
    
    print(f"正在从GitHub API获取{owner}/{repo}的提交记录...")
    
    for page in range(1, max_pages + 1):
        params = {
            'per_page': per_page,
            'page': page
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()  # 检查请求是否成功
            
            page_commits = response.json()
            if not page_commits:
                break  # 没有更多提交了
                
            for commit in page_commits:
                try:
                    # 转换时间格式
                    commit_date_str = commit['commit']['committer']['date']
                    commit_datetime = datetime.strptime(commit_date_str, '%Y-%m-%dT%H:%M:%SZ')
                    utc_datetime = commit_datetime.replace(tzinfo=pytz.UTC)
                    datetime_without_tz = utc_datetime.replace(tzinfo=None)
                    
                    # 构建提交数据
                    commit_data = {
                        'sha': commit['sha'],
                        'author_name': commit['commit']['author']['name'],
                        'author_email': commit['commit']['author']['email'],
                        'committer_name': commit['commit']['committer']['name'],
                        'committer_email': commit['commit']['committer']['email'],
                        'datetime': datetime_without_tz,
                        'message': commit['commit']['message'].strip(),
                        'insertions': commit.get('stats', {}).get('additions', 0),
                        'deletions': commit.get('stats', {}).get('deletions', 0),
                        'lines_changed': commit.get('stats', {}).get('total', 0),
                        'files_changed': len(commit.get('files', [])),
                        'parents': len(commit.get('parents', []))
                    }
                    
                    commits.append(commit_data)
                    
                except Exception as e:
                    print(f"处理API返回的提交 {commit['sha']} 时出错：{e}")
                    continue
            
            print(f"已获取第 {page} 页，共 {len(commits)} 条提交记录")
            
        except requests.exceptions.RequestException as e:
            print(f"API请求出错：{e}")
            break
    
    return commits

# 主函数
if __name__ == "__main__":
    try:
        # 从GitHub API获取提交记录
        commits = fetch_commits_from_github_api(owner='axios', repo='axios', per_page=100, max_pages=10)
        
        print(f"\n成功获取 {len(commits)} 条提交记录")
        
        if commits:
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
