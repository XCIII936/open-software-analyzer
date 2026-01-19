import os
import git
import pandas as pd
import pytz
from datetime import datetime

class RepoDataFetcher:
    """
    仓库数据获取器，用于获取GitHub仓库的提交历史数据
    """
    
    def __init__(self, repo_path=None):
        """
        初始化数据获取器
        
        Args:
            repo_path: 本地仓库路径，如果为None，则需要通过clone获取
        """
        self.repo_path = repo_path
        self.repo = None
        
    def clone_repo(self, repo_url, target_dir=None):
        """
        从GitHub克隆仓库
        
        Args:
            repo_url: GitHub仓库URL
            target_dir: 克隆目标目录
            
        Returns:
            仓库路径
        """
        if target_dir is None:
            # 使用仓库名作为目录名
            repo_name = repo_url.split('/')[-1].replace('.git', '')
            target_dir = os.path.join('data', repo_name)
        elif os.path.isdir(target_dir) and not os.path.isdir(os.path.join(target_dir, '.git')):
            # 如果target_dir是目录但不是git仓库，将其作为父目录
            repo_name = repo_url.split('/')[-1].replace('.git', '')
            target_dir = os.path.join(target_dir, repo_name)
            
        os.makedirs(target_dir, exist_ok=True)
        
        if not os.path.exists(os.path.join(target_dir, '.git')):
            print(f"正在克隆仓库到 {target_dir}...")
            git.Repo.clone_from(repo_url, target_dir)
        else:
            print(f"仓库已存在于 {target_dir}，跳过克隆")
            
        self.repo_path = target_dir
        return target_dir
    
    def open_repo(self):
        """
        打开本地仓库
        
        Returns:
            Git仓库对象
        """
        if not self.repo_path:
            raise ValueError("仓库路径未设置")
            
        if not self.repo:
            self.repo = git.Repo(self.repo_path)
            
        return self.repo
    
    def get_commit_history(self, limit=None):
        """
        获取仓库的提交历史
        
        Args:
            limit: 限制返回的提交数量，None表示获取所有提交
            
        Returns:
            pandas DataFrame，包含提交历史数据
        """
        repo = self.open_repo()
        
        commits = []
        count = 0
        
        for commit in repo.iter_commits():
            if limit and count >= limit:
                break
                
            stats = commit.stats.total
            # 将带有时区的时间转换为UTC时间，并移除时区信息
            utc_datetime = commit.committed_datetime.astimezone(pytz.UTC)
            datetime_without_tz = utc_datetime.replace(tzinfo=None)
            
            commit_data = {
                'sha': commit.hexsha,
                'author_name': commit.author.name,
                'author_email': commit.author.email,
                'committer_name': commit.committer.name,
                'committer_email': commit.committer.email,
                'datetime': datetime_without_tz,
                'message': commit.message.strip(),
                'insertions': stats.get('insertions', 0),
                'deletions': stats.get('deletions', 0),
                'lines_changed': stats.get('lines', 0),
                'files_changed': len(commit.stats.files),
                'parents': len(commit.parents)
            }
            
            commits.append(commit_data)
            count += 1
            
        return pd.DataFrame(commits)
    
    def save_commit_data(self, commit_df, filename=None):
        """
        保存提交数据到CSV文件
        
        Args:
            commit_df: 包含提交数据的DataFrame
            filename: 保存文件名，None时自动生成
        """
        if filename is None:
            repo_name = os.path.basename(self.repo_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join('data', f'{repo_name}_commits_{timestamp}.csv')
            
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        commit_df.to_csv(filename, index=False)
        print(f"提交数据已保存到 {filename}")
        return filename
    
    def load_commit_data(self, filename):
        """
        从CSV文件加载提交数据
        
        Args:
            filename: 数据文件名
            
        Returns:
            pandas DataFrame，包含提交历史数据
        """
        return pd.read_csv(filename, parse_dates=['datetime'])

if __name__ == "__main__":
    # 示例使用
    fetcher = RepoDataFetcher()
    
    # 克隆仓库
    repo_path = fetcher.clone_repo("https://github.com/python/cpython", target_dir="data/cpython")
    
    # 获取提交历史
    commit_df = fetcher.get_commit_history(limit=100)
    print(f"获取到 {len(commit_df)} 条提交记录")
    print(commit_df.head())
    
    # 保存数据
    fetcher.save_commit_data(commit_df)