import os
import unittest
import shutil
import pandas as pd
from src.data_fetcher import RepoDataFetcher

class TestRepoDataFetcher(unittest.TestCase):
    """
    测试RepoDataFetcher类的功能
    """
    
    @classmethod
    def setUpClass(cls):
        """
        测试前的准备工作
        """
        cls.test_dir = 'test_repo'
        os.makedirs(cls.test_dir, exist_ok=True)
    
    @classmethod
    def tearDownClass(cls):
        """
        测试后的清理工作
        """
        shutil.rmtree(cls.test_dir)
    
    def test_clone_repo(self):
        """
        测试克隆仓库功能
        """
        fetcher = RepoDataFetcher()
        
        # 使用一个小型仓库进行测试
        repo_url = 'https://github.com/hello-world/hello-world.git'
        repo_path = fetcher.clone_repo(repo_url, self.test_dir)
        
        # 检查仓库是否成功克隆
        self.assertTrue(os.path.exists(repo_path))
        self.assertTrue(os.path.exists(os.path.join(repo_path, '.git')))
    
    def test_get_commit_history(self):
        """
        测试获取提交历史功能
        """
        fetcher = RepoDataFetcher()
        
        # 使用一个小型仓库进行测试
        repo_url = 'https://github.com/hello-world/hello-world.git'
        repo_path = fetcher.clone_repo(repo_url, self.test_dir)
        
        # 打开仓库并获取提交历史
        fetcher.open_repo()
        commit_df = fetcher.get_commit_history(limit=5)
        
        # 检查返回的数据格式
        self.assertIsInstance(commit_df, pd.DataFrame)
        self.assertIn('sha', commit_df.columns)
        self.assertIn('author_name', commit_df.columns)
        self.assertIn('datetime', commit_df.columns)
        self.assertIn('message', commit_df.columns)
        
        # 检查提交数量
        self.assertLessEqual(len(commit_df), 5)
    
    def test_save_and_load_commit_data(self):
        """
        测试保存和加载提交数据功能
        """
        fetcher = RepoDataFetcher()
        
        # 创建测试数据
        test_data = {
            'sha': ['abc123', 'def456'],
            'author_name': ['Test User', 'Another User'],
            'datetime': ['2023-01-01 10:00:00', '2023-01-02 15:30:00'],
            'message': ['Test commit 1', 'Test commit 2'],
            'stats': [{'insertions': 10, 'deletions': 5}, {'insertions': 20, 'deletions': 0}],
            'files_changed': [2, 1]
        }
        
        test_df = pd.DataFrame(test_data)
        test_df['datetime'] = pd.to_datetime(test_df['datetime'])
        
        # 保存数据
        save_path = os.path.join(self.test_dir, 'test_commits.csv')
        fetcher.save_commit_data(test_df, save_path)
        
        # 检查文件是否存在
        self.assertTrue(os.path.exists(save_path))
        
        # 加载数据
        loaded_df = fetcher.load_commit_data(save_path)
        
        # 检查加载的数据是否与原始数据一致
        self.assertEqual(len(loaded_df), len(test_df))
        self.assertEqual(list(loaded_df.columns), list(test_df.columns))

if __name__ == '__main__':
    unittest.main()