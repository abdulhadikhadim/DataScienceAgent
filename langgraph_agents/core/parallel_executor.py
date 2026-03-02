import asyncio
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from typing import List, Dict, Any, Callable, Optional
import pandas as pd
from dataclasses import dataclass
import time
from functools import wraps


@dataclass
class ParallelTask:
    """Definition of a parallel task"""
    name: str
    function: Callable
    args: tuple = ()
    kwargs: dict = None
    priority: int = 1
    
    def __post_init__(self):
        if self.kwargs is None:
            self.kwargs = {}


class ParallelExecutor:
    """
    Parallel execution engine for independent preprocessing tasks.
    Implements thread-based and process-based parallelism.
    """
    
    def __init__(self, max_workers: Optional[int] = None, use_processes: bool = False):
        self.max_workers = max_workers
        self.use_processes = use_processes
        self.executor_class = ProcessPoolExecutor if use_processes else ThreadPoolExecutor
    
    def execute_parallel(self, tasks: List[ParallelTask]) -> Dict[str, Any]:
        """
        Execute tasks in parallel using thread pool.
        Returns dict mapping task name to result.
        """
        results = {}
        errors = {}
        
        tasks_sorted = sorted(tasks, key=lambda t: t.priority)
        
        with self.executor_class(max_workers=self.max_workers) as executor:
            future_to_task = {
                executor.submit(task.function, *task.args, **task.kwargs): task
                for task in tasks_sorted
            }
            
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    result = future.result()
                    results[task.name] = result
                except Exception as e:
                    errors[task.name] = str(e)
        
        return {
            "results": results,
            "errors": errors,
            "success_count": len(results),
            "error_count": len(errors)
        }
    
    async def execute_async(self, tasks: List[ParallelTask]) -> Dict[str, Any]:
        """
        Execute tasks asynchronously.
        """
        async def run_task(task: ParallelTask):
            try:
                if asyncio.iscoroutinefunction(task.function):
                    result = await task.function(*task.args, **task.kwargs)
                else:
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(
                        None, 
                        task.function, 
                        *task.args
                    )
                return task.name, result, None
            except Exception as e:
                return task.name, None, str(e)
        
        task_results = await asyncio.gather(*[run_task(task) for task in tasks])
        
        results = {}
        errors = {}
        
        for name, result, error in task_results:
            if error:
                errors[name] = error
            else:
                results[name] = result
        
        return {
            "results": results,
            "errors": errors,
            "success_count": len(results),
            "error_count": len(errors)
        }


class DataFramePartitioner:
    """
    Partitions DataFrames for parallel processing.
    Implements data partitioning strategies for scalability.
    """
    
    @staticmethod
    def partition_by_rows(df: pd.DataFrame, n_partitions: int) -> List[pd.DataFrame]:
        """Partition DataFrame by rows"""
        chunk_size = len(df) // n_partitions
        partitions = []
        
        for i in range(n_partitions):
            start_idx = i * chunk_size
            end_idx = start_idx + chunk_size if i < n_partitions - 1 else len(df)
            partitions.append(df.iloc[start_idx:end_idx].copy())
        
        return partitions
    
    @staticmethod
    def partition_by_column_groups(df: pd.DataFrame, n_partitions: int) -> List[pd.DataFrame]:
        """Partition DataFrame by column groups"""
        cols_per_partition = len(df.columns) // n_partitions
        partitions = []
        
        for i in range(n_partitions):
            start_col = i * cols_per_partition
            end_col = start_col + cols_per_partition if i < n_partitions - 1 else len(df.columns)
            cols = df.columns[start_col:end_col]
            partitions.append(df[cols].copy())
        
        return partitions
    
    @staticmethod
    def partition_by_key(df: pd.DataFrame, key_column: str) -> Dict[Any, pd.DataFrame]:
        """Partition DataFrame by unique values in a key column"""
        return {key: group for key, group in df.groupby(key_column)}
    
    @staticmethod
    def partition_by_date(df: pd.DataFrame, date_column: str, freq: str = 'M') -> Dict[str, pd.DataFrame]:
        """Partition DataFrame by date periods"""
        if not pd.api.types.is_datetime64_any_dtype(df[date_column]):
            df[date_column] = pd.to_datetime(df[date_column])
        
        df['_period'] = df[date_column].dt.to_period(freq)
        partitions = {str(period): group.drop(columns=['_period']) 
                     for period, group in df.groupby('_period')}
        
        return partitions


def parallel_apply(func: Callable, partitions: List[pd.DataFrame], 
                   max_workers: Optional[int] = None) -> pd.DataFrame:
    """
    Apply a function to DataFrame partitions in parallel and combine results.
    """
    executor = ParallelExecutor(max_workers=max_workers)
    
    tasks = [
        ParallelTask(
            name=f"partition_{i}",
            function=func,
            args=(partition,)
        )
        for i, partition in enumerate(partitions)
    ]
    
    result = executor.execute_parallel(tasks)
    
    if result["error_count"] > 0:
        raise Exception(f"Errors in parallel execution: {result['errors']}")
    
    processed_partitions = [result["results"][f"partition_{i}"] 
                           for i in range(len(partitions))]
    
    return pd.concat(processed_partitions, ignore_index=True)


def memoize(func: Callable) -> Callable:
    """
    Memoization decorator for caching function results.
    Optimizes repeated computations.
    """
    cache = {}
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    
    return wrapper


class PerformanceMonitor:
    """
    Monitor and log performance metrics for optimization.
    """
    
    def __init__(self):
        self.metrics = {}
    
    def time_function(self, name: str):
        """Decorator to time function execution"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                start = time.time()
                result = func(*args, **kwargs)
                elapsed = time.time() - start
                
                if name not in self.metrics:
                    self.metrics[name] = []
                self.metrics[name].append(elapsed)
                
                return result
            return wrapper
        return decorator
    
    def get_stats(self, name: str) -> Dict[str, float]:
        """Get statistics for a timed function"""
        if name not in self.metrics:
            return {}
        
        times = self.metrics[name]
        return {
            "count": len(times),
            "total": sum(times),
            "mean": sum(times) / len(times),
            "min": min(times),
            "max": max(times)
        }
    
    def get_all_stats(self) -> Dict[str, Dict[str, float]]:
        """Get all performance statistics"""
        return {name: self.get_stats(name) for name in self.metrics.keys()}


class ChunkProcessor:
    """
    Process large DataFrames in chunks for memory efficiency.
    """
    
    def __init__(self, chunk_size: int = 10000):
        self.chunk_size = chunk_size
    
    def process_in_chunks(self, df: pd.DataFrame, 
                         process_func: Callable[[pd.DataFrame], pd.DataFrame]) -> pd.DataFrame:
        """Process DataFrame in chunks"""
        chunks = []
        
        for start in range(0, len(df), self.chunk_size):
            end = min(start + self.chunk_size, len(df))
            chunk = df.iloc[start:end]
            processed_chunk = process_func(chunk)
            chunks.append(processed_chunk)
        
        return pd.concat(chunks, ignore_index=True)
    
    def read_csv_in_chunks(self, filepath: str, 
                          process_func: Callable[[pd.DataFrame], pd.DataFrame]) -> pd.DataFrame:
        """Read and process CSV file in chunks"""
        chunks = []
        
        for chunk in pd.read_csv(filepath, chunksize=self.chunk_size):
            processed_chunk = process_func(chunk)
            chunks.append(processed_chunk)
        
        return pd.concat(chunks, ignore_index=True)
