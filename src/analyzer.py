import pandas as pd
import numpy as np
import nltk
from nltk.corpus import stopwords
from collections import Counter
from datetime import datetime

class RepoAnalyzer:
    """
    仓库数据分析器，用于对提交历史数据进行多维度分析
    """
    
    def __init__(self, commit_df):
        """
        初始化分析器
        
        Args:
            commit_df: 包含提交数据的DataFrame
        """
        self.commit_df = commit_df.copy()
        # 确保datetime列是datetime类型
        if not pd.api.types.is_datetime64_any_dtype(self.commit_df['datetime']):
            self.commit_df['datetime'] = pd.to_datetime(self.commit_df['datetime'])
    
    def analyze_commit_frequency(self, freq='D'):
        """
        分析提交频率
        
        Args:
            freq: 时间频率，如'D'（日）、'W'（周）、'M'（月）、'Y'（年）
            
        Returns:
            包含时间和对应提交数量的DataFrame
        """
        # 按指定频率重新采样
        freq_df = self.commit_df.resample(freq, on='datetime')['sha'].count().reset_index()
        freq_df.rename(columns={'sha': 'commit_count'}, inplace=True)
        return freq_df
    
    def analyze_developer_activity(self, top_n=10):
        """
        分析开发者活跃度
        
        Args:
            top_n: 返回前N个活跃开发者
            
        Returns:
            包含开发者和提交数量的DataFrame
        """
        activity = self.commit_df['author_name'].value_counts().reset_index()
        activity.columns = ['developer', 'commit_count']
        return activity.head(top_n)
    
    def analyze_commit_time_distribution(self, time_unit='hour'):
        """
        分析提交时间分布
        
        Args:
            time_unit: 时间单位，可选'hour'（小时）、'dayofweek'（星期几）、'month'（月份）
            
        Returns:
            包含时间单位和对应提交数量的DataFrame
        """
        if time_unit == 'hour':
            distribution = self.commit_df['datetime'].dt.hour.value_counts().sort_index().reset_index()
            distribution.columns = ['hour', 'commit_count']
        elif time_unit == 'dayofweek':
            distribution = self.commit_df['datetime'].dt.dayofweek.value_counts().sort_index().reset_index()
            distribution.columns = ['dayofweek', 'commit_count']
            # 将数字转换为星期几名称
            day_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
            distribution['dayofweek'] = distribution['dayofweek'].map(lambda x: day_names[x])
        elif time_unit == 'month':
            distribution = self.commit_df['datetime'].dt.month.value_counts().sort_index().reset_index()
            distribution.columns = ['month', 'commit_count']
            # 将数字转换为月份名称
            month_names = ['一月', '二月', '三月', '四月', '五月', '六月', 
                          '七月', '八月', '九月', '十月', '十一月', '十二月']
            distribution['month'] = distribution['month'].map(lambda x: month_names[x-1])
        else:
            raise ValueError(f"不支持的时间单位: {time_unit}")
            
        return distribution
    
    def analyze_commit_message_keywords(self, top_n=20):
        """
        分析提交消息中的关键词
        
        Args:
            top_n: 返回前N个关键词
            
        Returns:
            包含关键词和出现次数的DataFrame
        """
        stop_words = set(stopwords.words('english'))
        stop_words.update(['fix', 'bug', 'issue', 'update', 'add', 'remove'])
        
        all_words = []
        
        for message in self.commit_df['message']:
            # 分词
            words = nltk.word_tokenize(message.lower())
            # 过滤停用词和非字母词
            words = [word for word in words if word.isalpha() and word not in stop_words]
            all_words.extend(words)
        
        # 统计词频
        word_counts = Counter(all_words)
        keywords_df = pd.DataFrame(word_counts.most_common(top_n), columns=['keyword', 'count'])
        
        return keywords_df
    
    def analyze_file_changes(self):
        """
        分析文件修改情况
        
        Returns:
            包含修改类型统计的字典
        """
        # 统计添加、删除和修改的行数
        total_additions = self.commit_df['insertions'].sum()
        total_deletions = self.commit_df['deletions'].sum()
        total_files_changed = self.commit_df['files_changed'].sum()
        
        return {
            'total_commits': len(self.commit_df),
            'total_files_changed': total_files_changed,
            'total_additions': total_additions,
            'total_deletions': total_deletions,
            'avg_files_per_commit': total_files_changed / len(self.commit_df),
            'avg_additions_per_commit': total_additions / len(self.commit_df),
            'avg_deletions_per_commit': total_deletions / len(self.commit_df)
        }
    
    def get_developer_productivity(self, developer_name):
        """
        获取特定开发者的生产力指标
        
        Args:
            developer_name: 开发者名称
            
        Returns:
            包含开发者生产力指标的字典
        """
        dev_commits = self.commit_df[self.commit_df['author_name'] == developer_name]
        
        if len(dev_commits) == 0:
            return None
            
        total_additions = dev_commits['insertions'].sum()
        total_deletions = dev_commits['deletions'].sum()
        total_files_changed = dev_commits['files_changed'].sum()
        
        return {
            'developer': developer_name,
            'commit_count': len(dev_commits),
            'total_files_changed': total_files_changed,
            'total_additions': total_additions,
            'total_deletions': total_deletions,
            'avg_files_per_commit': total_files_changed / len(dev_commits),
            'avg_additions_per_commit': total_additions / len(dev_commits),
            'avg_deletions_per_commit': total_deletions / len(dev_commits)
        }

if __name__ == "__main__":
    # 示例使用
    import pandas as pd
    
    # 创建示例数据
    sample_data = {
        'sha': ['abc123', 'def456', 'ghi789'],
        'author_name': ['Alice', 'Bob', 'Alice'],
        'datetime': ['2023-01-01 10:00:00', '2023-01-02 15:30:00', '2023-01-03 09:15:00'],
        'message': ['Fix bug in login', 'Add new feature', 'Update documentation'],
        'stats': [{'insertions': 10, 'deletions': 5}, {'insertions': 20, 'deletions': 0}, {'insertions': 5, 'deletions': 2}],
        'files_changed': [2, 1, 3]
    }
    
    sample_df = pd.DataFrame(sample_data)
    sample_df['datetime'] = pd.to_datetime(sample_df['datetime'])
    
    analyzer = RepoAnalyzer(sample_df)
    
    # 测试各分析方法
    print("提交频率分析:")
    print(analyzer.analyze_commit_frequency(freq='D'))
    
    print("\n开发者活跃度分析:")
    print(analyzer.analyze_developer_activity())
    
    print("\n提交时间分布分析 (小时):")
    print(analyzer.analyze_commit_time_distribution(time_unit='hour'))