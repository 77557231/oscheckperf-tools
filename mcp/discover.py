import subprocess
import re
import json
import os
from config import get_config

CONFIG = get_config()

class OscheckperfDiscover:
    def __init__(self):
        self.commands = []
        self.options = {}
        self.parameters = {}
        self.capabilities = {}
        self.discovery_cache_file = os.path.join(CONFIG.TEMP_DIR, 'oscheckperf_capabilities.json')
    
    def discover(self):
        result = subprocess.run(
            [CONFIG.OSCHECKPERF_PATH, '--help'],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            self._load_default_capabilities()
            return self.capabilities
        
        help_text = result.stdout
        self._parse_help_text(help_text)
        self._build_capabilities()
        self._save_cache()
        return self.capabilities
    
    def _parse_help_text(self, help_text):
        self.commands = self._extract_commands(help_text)
        self.options = self._extract_options(help_text)
        self.parameters = self._extract_parameters(help_text)
    
    def _extract_commands(self, help_text):
        commands = []
        commands_section = re.search(r'Commands:\n([\s\S]*?)\n\n', help_text)
        if commands_section:
            lines = commands_section.group(1).strip().split('\n')
            for line in lines:
                match = re.match(r'^\s*(\w+)\s+', line.strip())
                if match:
                    commands.append(match.group(1))
        return commands if commands else ['cpu', 'mem', 'io', 'network', 'thread', 'mutex', 'all', 'check', 'hardware']
    
    def _extract_options(self, help_text):
        options = {}
        options_section = re.search(r'Options:\n([\s\S]*?)\n\n', help_text)
        if options_section:
            lines = options_section.group(1).strip().split('\n')
            for line in lines:
                match = re.match(r'^\s*(-\w[\w-]*)\s+(.+)', line.strip())
                if match:
                    options[match.group(1)] = match.group(2).strip()
        return options
    
    def _extract_parameters(self, help_text):
        parameters = {}
        
        parameter_patterns = [
            r'Common parameters \(KEY=VALUE format\):\n([\s\S]*?)(?=\n\n|\Z)',
            r'CPU test parameters:\n([\s\S]*?)(?=\n\n|\Z)',
            r'Memory test parameters:\n([\s\S]*?)(?=\n\n|\Z)',
            r'IO test parameters:\n([\s\S]*?)(?=\n\n|\Z)',
            r'Network test parameters:\n([\s\S]*?)(?=\n\n|\Z)',
            r'Threads test parameters:\n([\s\S]*?)(?=\n\n|\Z)',
            r'Mutex test parameters:\n([\s\S]*?)(?=\n\n|\Z)',
            r'pgbench test parameters:\n([\s\S]*?)(?=\n\n|\Z)'
        ]
        
        for pattern in parameter_patterns:
            match = re.search(pattern, help_text)
            if match:
                lines = match.group(1).strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if line and '=' in line:
                        parts = line.split('=', 1)
                        param_name = parts[0].strip()
                        if param_name:
                            rest = parts[1] if len(parts) > 1 else ''
                            match_def = re.match(r'([^\s]+)\s+(.+)', rest)
                            if match_def:
                                default_val = match_def.group(1).strip()
                                description = match_def.group(2).strip()
                                parameters[param_name] = {
                                    'default': default_val,
                                    'description': description
                                }
                            else:
                                parameters[param_name] = {
                                    'default': None,
                                    'description': rest.strip()
                                }
        
        return parameters
    
    def _build_capabilities(self):
        self.capabilities = {
            'commands': self.commands,
            'options': self.options,
            'parameters': self.parameters,
            'tool_description': self._build_tool_description()
        }
    
    def _build_tool_description(self):
        return {
            'name': 'oscheckperf',
            'description': '集群系统性能基准测试工具，支持CPU/内存/IO/网络/线程/锁测试',
            'parameters': {
                'servers': {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'description': '服务器IP地址列表'
                },
                'command': {
                    'type': 'string',
                    'enum': self.commands if self.commands else ['all'],
                    'default': 'all',
                    'description': '测试命令'
                },
                'duration': {
                    'type': 'integer',
                    'default': CONFIG.DEFAULT_DURATION,
                    'description': '测试时长（秒）'
                },
                'io_tool': {
                    'type': 'string',
                    'enum': ['sysbench', 'fio'],
                    'default': CONFIG.DEFAULT_IO_TOOL,
                    'description': 'IO测试工具'
                },
                'output_dir': {
                    'type': 'string',
                    'default': CONFIG.OUTPUT_DIR,
                    'description': '输出目录'
                }
            }
        }
    
    def _load_default_capabilities(self):
        self.capabilities = {
            'commands': ['cpu', 'mem', 'io', 'network', 'thread', 'mutex', 'all', 'check', 'hardware'],
            'options': {},
            'parameters': {},
            'tool_description': {
                'name': 'oscheckperf',
                'description': '集群系统性能基准测试工具',
                'parameters': {
                    'servers': {
                        'type': 'array',
                        'items': {'type': 'string'},
                        'description': '服务器IP地址列表'
                    },
                    'command': {
                        'type': 'string',
                        'enum': ['cpu', 'mem', 'io', 'network', 'thread', 'mutex', 'all', 'check', 'hardware'],
                        'default': 'all',
                        'description': '测试命令'
                    },
                    'duration': {
                        'type': 'integer',
                        'default': CONFIG.DEFAULT_DURATION,
                        'description': '测试时长（秒）'
                    },
                    'io_tool': {
                        'type': 'string',
                        'enum': ['sysbench', 'fio'],
                        'default': CONFIG.DEFAULT_IO_TOOL,
                        'description': 'IO测试工具'
                    },
                    'output_dir': {
                        'type': 'string',
                        'default': CONFIG.OUTPUT_DIR,
                        'description': '输出目录'
                    }
                }
            }
        }
    
    def _save_cache(self):
        os.makedirs(CONFIG.TEMP_DIR, exist_ok=True)
        with open(self.discovery_cache_file, 'w') as f:
            json.dump(self.capabilities, f, indent=2)
    
    def load_cache(self):
        if os.path.exists(self.discovery_cache_file):
            with open(self.discovery_cache_file, 'r') as f:
                self.capabilities = json.load(f)
            return self.capabilities
        return None

def discover_capabilities():
    discoverer = OscheckperfDiscover()
    return discoverer.discover()

def get_tool_description():
    discoverer = OscheckperfDiscover()
    cached = discoverer.load_cache()
    if cached:
        return cached.get('tool_description', {})
    capabilities = discoverer.discover()
    return capabilities.get('tool_description', {})