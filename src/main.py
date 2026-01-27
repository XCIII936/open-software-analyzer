
"""
直接运行分析已下载的axios数据集的脚本
功能与执行 "python -m src.cli analyze data\axios_commits_20260119_123619.csv" 相同
"""

import sys
import os
import pandas as pd

# 获取当前脚本所在目录
sCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(sCRIPT_DIR)

# 添加项目根目录到Python路径，确保能导入其他模块
sys.path.append(PROJECT_ROOT)

from analyzer import RepoAnalyzer
from visualizer import RepoVisualizer

def analyze_axios_data(data_file=None, output_dir='data', format='png'):

    output_dir = os.path.join(PROJECT_ROOT, output_dir)
    
    if data_file is None:
        data_file = os.path.join(output_dir, 'axios_commits_20260119_123619.csv')
    else:

        if not os.path.isabs(data_file):
            data_file = os.path.join(PROJECT_ROOT, data_file)
    
    # 检查文件是否存在
    if not os.path.exists(data_file):
        print(f"错误：数据文件 {data_file} 不存在")
        print("请先使用以下命令获取数据：")
        print("python -m src.cli fetch --repo-url https://github.com/axios/axios.git --output data --limit 1000")
        sys.exit(1)
    
    try:
        # 加载数据
        print(f"正在加载数据文件 {data_file}...")
        commit_df = pd.read_csv(data_file, parse_dates=['datetime'])
        print(f"成功加载 {len(commit_df)} 条提交记录")
        
        # 创建分析器
        analyzer = RepoAnalyzer(commit_df)
        
        # 执行各种分析
        print("正在执行分析...")
        
        # 1. 提交频率分析
        commit_frequency = analyzer.analyze_commit_frequency(freq='M')
        
        # 2. 开发者活跃度分析
        developer_activity = analyzer.analyze_developer_activity(top_n=10)
        
        # 3. 提交时间分布分析
        commit_time_hour = analyzer.analyze_commit_time_distribution(time_unit='hour')
        commit_time_day = analyzer.analyze_commit_time_distribution(time_unit='dayofweek')
        commit_time_month = analyzer.analyze_commit_time_distribution(time_unit='month')
        
        # 4. 文件修改分析
        file_changes = analyzer.analyze_file_changes()
        
        # 5. 提交消息关键词分析
        keywords = analyzer.analyze_commit_message_keywords(top_n=20)
        
        # 保存分析结果
        analysis_results = {
            'commit_frequency': commit_frequency,
            'developer_activity': developer_activity,
            'commit_time_hour': commit_time_hour,
            'commit_time_dayofweek': commit_time_day,
            'commit_time_month': commit_time_month,
            'file_changes': file_changes,
            'keywords': keywords
        }
        
        # 创建可视化器
        visualizer = RepoVisualizer(output_dir=output_dir)
        
        # 生成图表
        print("正在生成可视化图表...")
        
        # 提交频率图
        visualizer.plot_commit_frequency(commit_frequency, filename=f'commit_frequency.{format}')
        
        # 开发者活跃度图
        visualizer.plot_developer_activity(developer_activity, filename=f'developer_activity.{format}')
        
        # 提交时间分布图
        visualizer.plot_commit_time_distribution(commit_time_hour, time_unit='hour',
                                               filename=f'commit_time_hour.{format}')
        visualizer.plot_commit_time_distribution(commit_time_day, time_unit='dayofweek',
                                               filename=f'commit_time_day.{format}')
        visualizer.plot_commit_time_distribution(commit_time_month, time_unit='month',
                                               filename=f'commit_time_month.{format}')
        
        # 文件修改统计
        visualizer.plot_file_changes_summary(file_changes, filename=f'file_changes_summary.{format}')
        
        # 关键词云图
        try:
            visualizer.plot_keyword_cloud(keywords, filename=f'keyword_cloud.{format}')
        except ImportError:
            print("警告：wordcloud库未安装，跳过关键词云图生成")
        
        # 创建交互式仪表盘
        dashboard_path = visualizer.create_interactive_dashboard(analysis_results)
        
        print("\n分析完成！")
        print(f"图表已保存到 {output_dir} 目录")
        print(f"交互式仪表盘已生成：{dashboard_path}")
        
        # 输出一些关键统计信息
        print("\n=== 关键统计信息 ===")
        print(f"总提交数：{file_changes['total_commits']}")
        print(f"总修改文件数：{file_changes['total_files_changed']}")
        print(f"总添加行数：{file_changes['total_additions']}")
        print(f"总删除行数：{file_changes['total_deletions']}")
        print(f"平均每次提交修改文件数：{file_changes['avg_files_per_commit']:.2f}")
        print(f"平均每次提交添加行数：{file_changes['avg_additions_per_commit']:.2f}")
        print(f"平均每次提交删除行数：{file_changes['avg_deletions_per_commit']:.2f}")
        
        print("\n=== 活跃开发者 ===")
        for i, row in developer_activity.iterrows():
            print(f"{i+1}. {row['developer']}: {row['commit_count']} 次提交")
            
    except Exception as e:
        print(f"分析时出错：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":

    data_file = None
    if len(sys.argv) > 1:
        data_file = sys.argv[1]
    
    analyze_axios_data(data_file=data_file)
