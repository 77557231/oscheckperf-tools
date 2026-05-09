import subprocess
import os
import tempfile
import uuid
from config import get_config

CONFIG = get_config()

class OscheckperfExecutor:
    def __init__(self):
        self.output_dir = CONFIG.OUTPUT_DIR
    
    def execute(self, servers, command='all', duration=60, io_tool='sysbench', output_dir=None):
        os.makedirs(self.output_dir, exist_ok=True)
        
        servers_file = self._create_servers_file(servers)
        
        args = [CONFIG.OSCHECKPERF_PATH]
        
        if servers_file:
            args.extend(['-f', servers_file])
        
        if output_dir:
            args.extend(['-o', output_dir])
        
        args.append(command)
        
        key_value_args = []
        if duration:
            key_value_args.append(f'DURATION={duration}')
        if io_tool:
            key_value_args.append(f'IO_TOOL={io_tool}')
        if output_dir:
            key_value_args.append(f'OUTPUT_DIR={output_dir}')
        
        args.extend(key_value_args)
        
        try:
            timeout = duration + 60
            
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                cwd=os.path.dirname(CONFIG.OSCHECKPERF_PATH) or '.',
                timeout=timeout
            )
            
            report_path = self._find_report_file(output_dir or self.output_dir)
            
            return {
                'success': result.returncode == 0,
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'command': ' '.join(args),
                'report_path': report_path
            }
        except subprocess.TimeoutExpired:
            report_path = self._find_report_file(output_dir or self.output_dir)
            return {
                'success': False,
                'return_code': -1,
                'stdout': '',
                'stderr': 'Command timeout',
                'command': ' '.join(args),
                'report_path': report_path
            }
        finally:
            if servers_file and os.path.exists(servers_file):
                os.remove(servers_file)
    
    def _create_servers_file(self, servers):
        if not servers or not isinstance(servers, list) or len(servers) == 0:
            return None
        
        fd, path = tempfile.mkstemp(prefix='oscheckperf_servers_', suffix='.txt')
        try:
            with os.fdopen(fd, 'w') as f:
                for server in servers:
                    f.write(f'{server}\n')
            return path
        except:
            if os.path.exists(path):
                os.remove(path)
            return None
    
    def _find_report_file(self, output_dir):
        if not os.path.exists(output_dir):
            return None
        
        latest_report = None
        latest_time = 0
        
        for filename in os.listdir(output_dir):
            if filename.startswith('report_benchmark_') and filename.endswith('.log'):
                filepath = os.path.join(output_dir, filename)
                mtime = os.path.getmtime(filepath)
                if mtime > latest_time:
                    latest_time = mtime
                    latest_report = filepath
        
        return latest_report

def execute_benchmark(servers, command='all', duration=60, io_tool='sysbench', output_dir=None):
    executor = OscheckperfExecutor()
    return executor.execute(servers, command, duration, io_tool, output_dir)