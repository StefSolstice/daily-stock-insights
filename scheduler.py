#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定时任务调度模块
基于 APScheduler 实现股票分析任务的定时执行
"""

import logging
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from typing import Optional, Callable, Any

logger = logging.getLogger(__name__)


class TaskScheduler:
    """任务调度器"""
    
    def __init__(self, use_background: bool = True):
        """初始化调度器
        
        Args:
            use_background: 是否使用后台调度器（非阻塞），默认 True
        """
        self.use_background = use_background
        if use_background:
            self.scheduler = BackgroundScheduler(
                timezone='Asia/Shanghai',
                job_defaults={
                    'coalesce': True,  # 合并错过的任务
                    'max_instances': 1,  # 同一任务最多 1 个实例
                    'misfire_grace_time': 300  # 错过任务的宽限时间（秒）
                }
            )
        else:
            self.scheduler = BlockingScheduler(
                timezone='Asia/Shanghai',
                job_defaults={
                    'coalesce': True,
                    'max_instances': 1,
                    'misfire_grace_time': 300
                }
            )
        
        self._jobs = {}
        logger.info("任务调度器初始化完成")
    
    def add_job(self, job_id: str, func: Callable, 
                trigger_type: str = 'cron',
                **trigger_kwargs) -> bool:
        """添加定时任务
        
        Args:
            job_id: 任务 ID
            func: 要执行的函数
            trigger_type: 触发器类型 ('cron', 'date', 'interval')
            **trigger_kwargs: 触发器参数
            
        Returns:
            是否添加成功
        """
        try:
            if trigger_type == 'cron':
                trigger = CronTrigger(**trigger_kwargs, timezone='Asia/Shanghai')
            elif trigger_type == 'date':
                trigger = DateTrigger(**trigger_kwargs, timezone='Asia/Shanghai')
            elif trigger_type == 'interval':
                from apscheduler.triggers.interval import IntervalTrigger
                trigger = IntervalTrigger(**trigger_kwargs, timezone='Asia/Shanghai')
            else:
                logger.error(f"不支持的触发器类型：{trigger_type}")
                return False
            
            job = self.scheduler.add_job(
                func,
                trigger,
                id=job_id,
                name=job_id,
                replace_existing=True
            )
            
            self._jobs[job_id] = job
            logger.info(f"任务 '{job_id}' 添加成功：{trigger}")
            return True
            
        except Exception as e:
            logger.error(f"添加任务 '{job_id}' 失败：{e}")
            return False
    
    def remove_job(self, job_id: str) -> bool:
        """移除任务
        
        Args:
            job_id: 任务 ID
            
        Returns:
            是否移除成功
        """
        try:
            self.scheduler.remove_job(job_id)
            if job_id in self._jobs:
                del self._jobs[job_id]
            logger.info(f"任务 '{job_id}' 已移除")
            return True
        except Exception as e:
            logger.error(f"移除任务 '{job_id}' 失败：{e}")
            return False
    
    def start(self):
        """启动调度器"""
        try:
            logger.info("启动任务调度器...")
            if self.use_background:
                self.scheduler.start()
                logger.info("后台调度器已启动")
            else:
                logger.info("阻塞式调度器启动（将阻塞主线程）")
                self.scheduler.start()
        except Exception as e:
            logger.error(f"启动调度器失败：{e}")
            raise
    
    def shutdown(self, wait: bool = True):
        """关闭调度器
        
        Args:
            wait: 是否等待任务完成
        """
        try:
            logger.info("关闭任务调度器...")
            self.scheduler.shutdown(wait=wait)
            logger.info("任务调度器已关闭")
        except Exception as e:
            logger.error(f"关闭调度器失败：{e}")
    
    def get_job(self, job_id: str) -> Optional[Any]:
        """获取任务信息
        
        Args:
            job_id: 任务 ID
            
        Returns:
            任务对象，不存在则返回 None
        """
        try:
            return self.scheduler.get_job(job_id)
        except Exception:
            return None
    
    def list_jobs(self) -> list:
        """列出所有任务
        
        Returns:
            任务信息列表
        """
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            })
        return jobs


def create_default_scheduler() -> TaskScheduler:
    """创建默认调度器（配置股票分析任务）
    
    Returns:
        配置好的调度器实例
    """
    scheduler = TaskScheduler(use_background=True)
    
    # 示例：每个交易日 9:30 执行（周一至周五，排除节假日需要额外配置）
    # scheduler.add_job(
    #     job_id='daily_stock_analysis',
    #     func=None,  # 需要传入实际的分析函数
    #     trigger_type='cron',
    #     hour=9,
    #     minute=30,
    #     day_of_week='mon-fri'
    # )
    
    return scheduler


if __name__ == "__main__":
    # 测试
    import time
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    def test_job():
        logger.info(f"测试任务执行：{datetime.now()}")
    
    scheduler = TaskScheduler(use_background=True)
    scheduler.add_job(
        job_id='test_job',
        func=test_job,
        trigger_type='interval',
        seconds=5
    )
    
    logger.info("当前任务列表：")
    for job in scheduler.list_jobs():
        logger.info(f"  - {job['id']}: {job['name']} (下次执行：{job['next_run']})")
    
    try:
        scheduler.start()
        # 后台调度器需要保持主线程运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("收到中断信号，关闭调度器...")
        scheduler.shutdown()
