import click
import os
import pandas as pd
from datetime import datetime
from src.data_fetcher import RepoDataFetcher
from src.analyzer import RepoAnalyzer
from src.visualizer import RepoVisualizer

@click.group()
def cli():
    """
    开源软件仓库提交历史分析工具
    """
    pass

@cli.command()
@click.option('--repo-url', '-u', type=str, help='GitHub仓库URL')
@click.option('--local-repo', '-l', type=str, help='本地仓库路径')
@click.option('--output', '-o', type=str, default='data', help='输出目录')
@click.option('--limit', '-n', type=int, help='限制获取的提交数量')
def fetch(repo_url, local_repo, output, limit):
    """
    获取仓库提交历史数据
    """
    if not repo_url and not local_repo:
        click.echo('错误：必须提供GitHub仓库URL或本地仓库路径')
        return
    
    fetcher = RepoDataFetcher()
    
    if repo_url:
        # 克隆仓库
        repo_path = fetcher.clone_repo(repo_url, output)
    else:
        # 使用本地仓库
        repo_path = local_repo
        fetcher.repo_path = repo_path
    
    try:
        # 获取提交历史
        click.echo(f"正在获取提交历史数据...")
        commit_df = fetcher.get_commit_history(limit=limit)
        
        # 保存数据
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        repo_name = os.path.basename(repo_path)
        filename = os.path.join(output, f'{repo_name}_commits_{timestamp}.csv')
        fetcher.save_commit_data(commit_df, filename)
        
        click.echo(f"成功获取 {len(commit_df)} 条提交记录")
        click.echo(f"数据已保存到 {filename}")
        
    except Exception as e:
        click.echo(f"获取数据时出错：{e}")

@cli.command()
@click.argument('data_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=str, default='data', help='输出目录')
@click.option('--format', '-f', type=str, default='png', help='图表格式')
def analyze(data_file, output, format):
    """
    分析仓库提交历史数据
    """
    try:
        # 加载数据
        click.echo(f"正在加载数据文件 {data_file}...")
        commit_df = pd.read_csv(data_file, parse_dates=['datetime'])
        click.echo(f"成功加载 {len(commit_df)} 条提交记录")
        
        # 创建分析器
        analyzer = RepoAnalyzer(commit_df)
        
        # 执行各种分析
        click.echo("正在执行分析...")
        
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
        visualizer = RepoVisualizer(output_dir=output)
        
        # 生成图表
        click.echo("正在生成可视化图表...")
        
        # 提交频率图
        visualizer.plot_commit_frequency(commit_frequency, 
                                        filename=f'commit_frequency.{format}')
        
        # 开发者活跃度图
        visualizer.plot_developer_activity(developer_activity, 
                                          filename=f'developer_activity.{format}')
        
        # 提交时间分布图
        visualizer.plot_commit_time_distribution(commit_time_hour, time_unit='hour',
                                               filename=f'commit_time_hour.{format}')
        visualizer.plot_commit_time_distribution(commit_time_day, time_unit='dayofweek',
                                               filename=f'commit_time_day.{format}')
        visualizer.plot_commit_time_distribution(commit_time_month, time_unit='month',
                                               filename=f'commit_time_month.{format}')
        
        # 文件修改统计
        visualizer.plot_file_changes_summary(file_changes, 
                                            filename=f'file_changes_summary.{format}')
        
        # 关键词云图（如果安装了wordcloud库）
        try:
            visualizer.plot_keyword_cloud(keywords, filename=f'keyword_cloud.{format}')
        except ImportError:
            click.echo("警告：wordcloud库未安装，跳过关键词云图生成")
        
        # 创建交互式仪表盘
        dashboard_path = visualizer.create_interactive_dashboard(analysis_results)
        
        click.echo("\n分析完成！")
        click.echo(f"图表已保存到 {output} 目录")
        click.echo(f"交互式仪表盘已生成：{dashboard_path}")
        
        # 输出一些关键统计信息
        click.echo("\n=== 关键统计信息 ===")
        click.echo(f"总提交数：{file_changes['total_commits']}")
        click.echo(f"总修改文件数：{file_changes['total_files_changed']}")
        click.echo(f"总添加行数：{file_changes['total_additions']}")
        click.echo(f"总删除行数：{file_changes['total_deletions']}")
        click.echo(f"平均每次提交修改文件数：{file_changes['avg_files_per_commit']:.2f}")
        click.echo(f"平均每次提交添加行数：{file_changes['avg_additions_per_commit']:.2f}")
        click.echo(f"平均每次提交删除行数：{file_changes['avg_deletions_per_commit']:.2f}")
        
        click.echo("\n=== 活跃开发者 ===")
        for i, row in developer_activity.iterrows():
            click.echo(f"{i+1}. {row['developer']}: {row['commit_count']} 次提交")
            
    except Exception as e:
        click.echo(f"分析时出错：{e}")
        import traceback
        traceback.print_exc()

@cli.command()
def example():
    """
    运行示例分析
    """
    click.echo("正在运行示例分析...")
    
    # 创建示例数据
    sample_data = {
        'sha': ['abc123', 'def456', 'ghi789', 'jkl012', 'mno345'],
        'author_name': ['Alice', 'Bob', 'Alice', 'Charlie', 'Bob'],
        'datetime': ['2023-01-01 10:00:00', '2023-01-02 15:30:00', '2023-01-03 09:15:00', 
                    '2023-01-04 14:45:00', '2023-01-05 11:20:00'],
        'message': ['Fix bug in login', 'Add new feature', 'Update documentation', 
                   'Fix performance issue', 'Add unit tests'],
        'insertions': [10, 20, 5, 15, 8],
        'deletions': [5, 0, 2, 10, 3],
        'lines_changed': [15, 20, 7, 25, 11],
        'files_changed': [2, 1, 3, 2, 4],
        'parents': [1, 1, 1, 1, 1]
    }
    
    sample_df = pd.DataFrame(sample_data)
    sample_df['datetime'] = pd.to_datetime(sample_df['datetime'])
    
    # 保存示例数据
    os.makedirs('data', exist_ok=True)
    sample_file = 'data/sample_commits.csv'
    sample_df.to_csv(sample_file, index=False)
    
    click.echo(f"已创建示例数据文件：{sample_file}")
    click.echo("\n现在可以使用以下命令进行分析：")
    click.echo(f"python -m src.cli analyze {sample_file}")

if __name__ == '__main__':
    cli()