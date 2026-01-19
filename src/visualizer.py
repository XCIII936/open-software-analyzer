import matplotlib.pyplot as plt
import matplotlib
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']  # 支持中文显示
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

class RepoVisualizer:
    """
    仓库数据可视化器，用于将分析结果生成可视化图表
    """
    
    def __init__(self, output_dir='data/plots'):
        """
        初始化可视化器
        
        Args:
            output_dir: 图表输出目录
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def plot_commit_frequency(self, freq_df, title='提交频率趋势', filename='commit_frequency.png'):
        """
        绘制提交频率趋势图
        
        Args:
            freq_df: 包含时间和提交数量的DataFrame
            title: 图表标题
            filename: 保存文件名
            
        Returns:
            图表对象
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(freq_df['datetime'], freq_df['commit_count'], marker='o', linewidth=2)
        ax.set_title(title, fontsize=16)
        ax.set_xlabel('时间', fontsize=12)
        ax.set_ylabel('提交数量', fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.7)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # 保存图表
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300)
        plt.close()
        
        return fig
    
    def plot_developer_activity(self, activity_df, title='开发者活跃度排名', filename='developer_activity.png'):
        """
        绘制开发者活跃度柱状图
        
        Args:
            activity_df: 包含开发者和提交数量的DataFrame
            title: 图表标题
            filename: 保存文件名
            
        Returns:
            图表对象
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.bar(activity_df['developer'], activity_df['commit_count'], color='skyblue')
        ax.set_title(title, fontsize=16)
        ax.set_xlabel('开发者', fontsize=12)
        ax.set_ylabel('提交数量', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # 添加数据标签
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')
        
        # 保存图表
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300)
        plt.close()
        
        return fig
    
    def plot_commit_time_distribution(self, dist_df, time_unit='hour', title=None, filename=None):
        """
        绘制提交时间分布图
        
        Args:
            dist_df: 包含时间单位和提交数量的DataFrame
            time_unit: 时间单位，可选'hour'（小时）、'dayofweek'（星期几）、'month'（月份）
            title: 图表标题
            filename: 保存文件名
            
        Returns:
            图表对象
        """
        if title is None:
            if time_unit == 'hour':
                title = '提交时间分布（小时）'
            elif time_unit == 'dayofweek':
                title = '提交时间分布（星期几）'
            elif time_unit == 'month':
                title = '提交时间分布（月份）'
        
        if filename is None:
            filename = f'commit_time_{time_unit}.png'
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        if time_unit == 'hour':
            bars = ax.bar(dist_df['hour'], dist_df['commit_count'], color='orange')
            ax.set_xlabel('小时', fontsize=12)
        elif time_unit == 'dayofweek':
            bars = ax.bar(dist_df['dayofweek'], dist_df['commit_count'], color='green')
            ax.set_xlabel('星期几', fontsize=12)
        elif time_unit == 'month':
            bars = ax.bar(dist_df['month'], dist_df['commit_count'], color='purple')
            ax.set_xlabel('月份', fontsize=12)
        
        ax.set_title(title, fontsize=16)
        ax.set_ylabel('提交数量', fontsize=12)
        plt.tight_layout()
        
        # 添加数据标签
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom')
        
        # 保存图表
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300)
        plt.close()
        
        return fig
    
    def plot_keyword_cloud(self, keywords_df, title='提交消息关键词', filename='keyword_cloud.png'):
        """
        绘制关键词云图
        
        Args:
            keywords_df: 包含关键词和出现次数的DataFrame
            title: 图表标题
            filename: 保存文件名
            
        Returns:
            图表对象
        """
        try:
            from wordcloud import WordCloud
        except ImportError:
            print("wordcloud库未安装，无法生成词云图。请安装：pip install wordcloud")
            return None
        
        # 创建词云
        wordcloud = WordCloud(width=800, height=400, background_color='white', 
                             colormap='viridis', max_words=50).generate_from_frequencies(
            dict(zip(keywords_df['keyword'], keywords_df['count']))
        )
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        try:
            # 尝试使用直接显示方式
            ax.imshow(wordcloud, interpolation='bilinear')
        except TypeError:
            # 如果出现copy参数错误，使用变通方法
            img = wordcloud.to_image()
            ax.imshow(img, interpolation='bilinear')
        
        ax.set_title(title, fontsize=16)
        ax.axis('off')
        plt.tight_layout()
        
        # 保存图表
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300)
        plt.close()
        
        return fig
    
    def plot_file_changes_summary(self, file_changes, title='文件修改统计', filename='file_changes_summary.png'):
        """
        绘制文件修改统计饼图
        
        Args:
            file_changes: 包含修改类型统计的字典
            title: 图表标题
            filename: 保存文件名
            
        Returns:
            图表对象
        """
        labels = ['添加行数', '删除行数']
        sizes = [file_changes['total_additions'], file_changes['total_deletions']]
        colors = ['lightgreen', 'lightcoral']
        explode = (0.1, 0)  # 突出显示添加行数
        
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # 检查是否有有效数据
        total_size = sum(sizes)
        if total_size == 0:
            # 所有值都是0，绘制一个特殊的图表
            ax.text(0.5, 0.5, '没有可用的修改数据', ha='center', va='center', fontsize=14)
            ax.axis('off')
        else:
            # 正常绘制饼图
            ax.pie(sizes, explode=explode, labels=labels, colors=colors,
                  autopct='%1.1f%%', shadow=True, startangle=90)
            ax.axis('equal')  # 保证饼图是圆形
        
        ax.set_title(title, fontsize=16)
        plt.tight_layout()
        
        # 保存图表
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300)
        plt.close()
        
        return fig
    
    def create_interactive_dashboard(self, analysis_results, filename='analysis_dashboard.html'):
        """
        创建交互式仪表盘
        
        Args:
            analysis_results: 包含各种分析结果的字典
            filename: 保存文件名
            
        Returns:
            仪表盘HTML文件路径
        """
        from plotly.subplots import make_subplots
        
        # 创建子图布局
        fig = make_subplots(rows=2, cols=2, subplot_titles=(
            '提交频率趋势', '开发者活跃度', '提交时间分布（小时）', '提交时间分布（星期几）'
        ))
        
        # 添加提交频率趋势图
        if 'commit_frequency' in analysis_results:
            freq_df = analysis_results['commit_frequency']
            fig.add_trace(
                go.Scatter(x=freq_df['datetime'], y=freq_df['commit_count'], 
                          mode='lines+markers', name='提交频率'),
                row=1, col=1
            )
        
        # 添加开发者活跃度图
        if 'developer_activity' in analysis_results:
            activity_df = analysis_results['developer_activity']
            fig.add_trace(
                go.Bar(x=activity_df['developer'], y=activity_df['commit_count'], 
                      name='开发者活跃度'),
                row=1, col=2
            )
        
        # 添加提交时间分布（小时）
        if 'commit_time_hour' in analysis_results:
            hour_df = analysis_results['commit_time_hour']
            fig.add_trace(
                go.Bar(x=hour_df['hour'], y=hour_df['commit_count'], 
                      name='小时分布'),
                row=2, col=1
            )
        
        # 添加提交时间分布（星期几）
        if 'commit_time_dayofweek' in analysis_results:
            day_df = analysis_results['commit_time_dayofweek']
            fig.add_trace(
                go.Bar(x=day_df['dayofweek'], y=day_df['commit_count'], 
                      name='星期分布'),
                row=2, col=2
            )
        
        # 更新布局
        fig.update_layout(height=800, width=1200, title_text="开源仓库分析仪表盘",
                         showlegend=False)
        
        # 保存仪表盘
        filepath = os.path.join(self.output_dir, filename)
        fig.write_html(filepath)
        
        return filepath

if __name__ == "__main__":
    # 示例使用
    import pandas as pd
    from datetime import datetime, timedelta
    
    # 创建示例数据
    dates = [datetime(2023, 1, i) for i in range(1, 31)]
    commit_counts = [5, 3, 8, 2, 6, 4, 7, 9, 3, 5, 6, 4, 8, 7, 5, 3, 6, 4, 9, 8, 5, 3, 7, 6, 4, 5, 8, 6, 4, 7]
    
    freq_df = pd.DataFrame({'datetime': dates, 'commit_count': commit_counts})
    
    activity_df = pd.DataFrame({
        'developer': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
        'commit_count': [50, 42, 35, 28, 20]
    })
    
    hour_df = pd.DataFrame({
        'hour': list(range(24)),
        'commit_count': [2, 1, 0, 0, 1, 3, 8, 15, 25, 30, 35, 38, 40, 42, 45, 50, 48, 45, 40, 35, 30, 25, 18, 10]
    })
    
    # 创建可视化器
    visualizer = RepoVisualizer()
    
    # 测试可视化方法
    visualizer.plot_commit_frequency(freq_df)
    visualizer.plot_developer_activity(activity_df)
    visualizer.plot_commit_time_distribution(hour_df, time_unit='hour')
    
    print("示例图表已生成")