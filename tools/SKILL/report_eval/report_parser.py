import re
from typing import Dict, List, Any, Optional


class ReportParser:
    TEST_SECTIONS = {
        'cpu': '[CPU Test]',
        'memory': '[Memory Test]',
        'io': '[IO Test]',
        'threads': '[Threads Test]',
        'mutex': '[Mutex Test]',
        'network': '[Network Test]',
    }
    
    def __init__(self, log_path: str):
        self.log_path = log_path
        self.lines = []
        self._load_file()
    
    def _load_file(self):
        with open(self.log_path, 'r', encoding='utf-8') as f:
            self.lines = f.readlines()
    
    def parse_basic_info(self) -> Dict[str, Any]:
        info = {}
        in_section = False
        
        for line in self.lines:
            if '[Basic Information]' in line:
                in_section = True
                continue
            
            if in_section and line.startswith('='):
                break
            
            if in_section:
                line = line.strip()
                if line.startswith('Test Time:'):
                    info['test_time'] = line.split(':', 1)[1].strip()
                elif line.startswith('CPU Cores:'):
                    info['cpu_cores'] = int(line.split(':', 1)[1].strip())
                elif line.startswith('Local IP:'):
                    info['local_ip'] = line.split(':', 1)[1].strip()
                elif line.startswith('Unified Duration:'):
                    info['duration'] = line.split(':', 1)[1].strip()
                elif line.startswith('Cluster Mode:'):
                    info['cluster_mode'] = line.split(':', 1)[1].strip()
                    match = re.search(r'(\d+) nodes', info['cluster_mode'])
                    info['node_count'] = int(match.group(1)) if match else 1
                elif line.startswith('Server List:'):
                    info['servers'] = []
                elif line.startswith('  - ') and 'servers' in info:
                    server_line = line[4:].strip()
                    match = re.match(r'([\d.]+)', server_line)
                    if match:
                        info['servers'].append(match.group(1))
        
        return info
    
    def parse_hardware_info(self) -> Dict[str, Dict[str, Any]]:
        hardware = {}
        current_node = None
        current_section = None
        
        for line in self.lines:
            line_stripped = line.strip()
            
            if 'Hardware Information Report' in line:
                continue
            
            match = re.match(r'  Node \d+: ([\d.]+)', line)
            if match:
                current_node = match.group(1)
                hardware[current_node] = {}
                continue
            
            if current_node is None:
                continue
            
            if line_stripped.startswith('[') and line_stripped.endswith(']'):
                current_section = line_stripped.strip('[]')
                hardware[current_node][current_section] = {}
                continue
            
            if current_section and line.startswith('  ') and not line.startswith('  ['):
                if ':' in line_stripped:
                    key, value = line_stripped.split(':', 1)
                    hardware[current_node][current_section][key.strip()] = value.strip()
            
            if current_section == 'Network Information' and line.startswith('    ') and ':' in line_stripped:
                if line_stripped.startswith('ens') or line_stripped.startswith('eth') or line_stripped.startswith('bond'):
                    parts = line_stripped.split(',')
                    for part in parts:
                        part_stripped = part.strip()
                        if '=' in part_stripped:
                            k, v = part_stripped.split('=', 1)
                            if k == 'Driver':
                                if 'network' not in hardware[current_node]:
                                    hardware[current_node]['network'] = {}
                                hardware[current_node]['network']['driver'] = v
        
        return hardware
    
    def parse_hardware_summary(self) -> Dict[str, Dict[str, Any]]:
        summary = self._parse_hardware_comparison()
        self._fill_memory_freq(summary)
        return summary
    
    def _fill_memory_freq(self, summary: Dict[str, Dict[str, Any]]):
        hardware_info = self.parse_hardware_info()
        if hardware_info:
            for ip, info in hardware_info.items():
                if ip in summary and 'mem' in summary[ip]:
                    mem_info = info.get('Memory Information', {})
                    freq_str = mem_info.get('Frequency', '')
                    if freq_str:
                        match = re.search(r'([\d.]+)\s*MHz', freq_str)
                        if match:
                            summary[ip]['mem']['freq'] = match.group(1)
        else:
            self._fill_memory_freq_single(summary)
    
    def _fill_memory_freq_single(self, summary: Dict[str, Dict[str, Any]]):
        in_mem_section = False
        mem_freq = None
        
        for line in self.lines:
            if '[Memory Information]' in line:
                in_mem_section = True
                continue
            
            if in_mem_section and line.startswith('['):
                break
            
            if in_mem_section and 'Frequency:' in line:
                match = re.search(r'([\d.]+)\s*MHz', line)
                if match:
                    mem_freq = match.group(1)
                    break
        
        local_ip = None
        for line in self.lines:
            if line.startswith('Local IP:'):
                local_ip = line.split(':', 1)[1].strip()
                break
        
        if mem_freq and local_ip and local_ip in summary and 'mem' in summary[local_ip]:
            summary[local_ip]['mem']['freq'] = mem_freq
    
    def _parse_hardware_comparison(self) -> Dict[str, Dict[str, Any]]:
        summary = {}
        current_table = None
        headers = []
        in_table = False
        
        table_mappings = {
            'System Information': 'system',
            'CPU': 'cpu',
            'Memory': 'mem',
            'IO': 'io',
            'Network': 'network'
        }
        
        field_mappings = {
            'Arch': 'arch',
            'Machine Type': 'machine_type',
            'Model': 'model',
            'Physical Cores': 'physical_cores',
            'Logical Cores': 'logical_cores',
            'Frequency': 'freq',
            'Freq': 'freq',
            'Governor': 'governor',
            'Total(MB)': 'total',
            'Total': 'total',
            'Type': 'type',
            'Channels': 'channels',
            'Total Slots': 'total_slots',
            'Used Slots': 'used_slots',
            'Manufacturer': 'manufacturer',
            'NUMA Count': 'numa_count',
            'Mount': 'mount',
            'VENDOR': 'vendor',
            'MODEL': 'model',
            'SCHEDULER': 'scheduler',
            'WCACHE': 'wcache',
            'Bond Interfaces': 'bond',
            'Speed': 'speed',
            'MTU': 'mtu',
            'Driver': 'driver',
            'Interface Count': 'interfaces',
            'Mem Frequency': 'freq'
        }
        
        for line in self.lines:
            line_stripped = line.strip()
            
            if '[Hardware Comparison - ' in line_stripped:
                table_name = line_stripped.replace('[Hardware Comparison - ', '').replace(']', '')
                if table_name in table_mappings:
                    current_table = table_mappings[table_name]
                    headers = []
                    in_table = False
                    in_header_section = False
                continue
            
            if line_stripped.startswith('=') or line_stripped.startswith('['):
                current_table = None
                in_table = False
                continue
            
            if current_table and line_stripped.startswith('---'):
                if in_header_section:
                    in_table = True
                    in_header_section = False
                elif not in_table:
                    in_header_section = True
                continue
            
            if current_table and in_header_section and not line_stripped.startswith('---'):
                headers = [h.strip() for h in line_stripped.split('|')]
                continue
            
            if current_table and in_table and not line_stripped.startswith('---') and line_stripped:
                values = [v.strip() for v in line_stripped.split('|')]
                if len(values) >= 1:
                    ip = values[0]
                    if ip not in summary:
                        summary[ip] = {
                            'system': {},
                            'cpu': {},
                            'mem': {},
                            'io': {},
                            'network': {}
                        }
                    for i, header in enumerate(headers):
                        if i < len(values):
                            mapped_key = field_mappings.get(header, header.lower().replace(' ', '_'))
                            summary[ip][current_table][mapped_key] = values[i]
        
        return summary
    
    def parse_test_results(self) -> Dict[str, List[Dict[str, Any]]]:
        results = {}
        current_test = None
        in_data_section = False
        skip_until_next_test = False
        
        for line in self.lines:
            for test_key, marker in self.TEST_SECTIONS.items():
                if marker in line:
                    current_test = test_key
                    results[current_test] = []
                    in_data_section = False
                    skip_until_next_test = False
                    break
            
            if current_test and line.startswith('[') and line.strip() != marker:
                current_test = None
                skip_until_next_test = False
                continue
            
            if current_test and 'Test not executed' in line:
                results[current_test] = None
                current_test = None
                skip_until_next_test = False
                continue
            
            if skip_until_next_test:
                continue
            
            if current_test is None:
                continue
            
            if line.strip().startswith('---'):
                in_data_section = True
                continue
            
            if not in_data_section:
                continue
            
            line = line.strip()
            if not line:
                continue
            
            if current_test == 'io' and 'FIO Extended Metrics' in line:
                skip_until_next_test = True
                continue
            
            if line.startswith('#') or line.startswith('Server IP') or line.startswith('Client') or line.startswith('发起节点'):
                continue
            
            parts = line.split()
            if len(parts) < 2:
                continue
            
            if not re.match(r'^\d+\.\d+\.\d+\.\d+$', parts[0]):
                continue
            
            try:
                if current_test == 'cpu':
                    self._parse_cpu_result(results, parts)
                elif current_test == 'memory':
                    self._parse_memory_result(results, parts)
                elif current_test == 'io':
                    self._parse_io_result(results, parts)
                elif current_test == 'threads':
                    self._parse_threads_result(results, parts)
                elif current_test == 'mutex':
                    self._parse_mutex_result(results, parts)
                elif current_test == 'network':
                    self._parse_network_result(results, parts)
            except (ValueError, IndexError):
                continue
        
        return results
    
    def _parse_cpu_result(self, results: Dict, parts: List[str]):
        if len(parts) >= 8:
            results['cpu'].append({
                'ip': parts[0],
                'events_sec': float(parts[1]),
                'avg_lat': float(parts[2]),
                'p95_lat': float(parts[3]),
                'max_lat': float(parts[4]),
                'min_lat': float(parts[5]),
                'sum_lat': float(parts[6])
            })
    
    def _parse_memory_result(self, results: Dict, parts: List[str]):
        if len(parts) >= 10:
            results['memory'].append({
                'ip': parts[0],
                'ops_sec': float(parts[1]),
                'mib_sec': float(parts[2]),
                'avg_lat': float(parts[3]),
                'min_lat': float(parts[4]),
                'max_lat': float(parts[5]),
                'p95_lat': float(parts[6]),
                'sum_lat': float(parts[7]),
                'mode': parts[-1]
            })
    
    def _parse_io_result(self, results: Dict, parts: List[str]):
        if len(parts) >= 10:
            results['io'].append({
                'ip': parts[0],
                'read_iops': float(parts[1]) if parts[1] != 'N/A' else None,
                'write_iops': float(parts[2]) if parts[2] != 'N/A' else None,
                'total_iops': float(parts[3]) if parts[3] != 'N/A' else None,
                'read_bw': float(parts[4]) if parts[4] != 'N/A' else None,
                'write_bw': float(parts[5]) if parts[5] != 'N/A' else None,
                'total_bw': float(parts[6]) if parts[6] != 'N/A' else None,
                'latency': float(parts[7]) if parts[7] != 'N/A' else None,
                'p99': float(parts[8]) if parts[8] != 'N/A' else None,
                'mode': parts[-1]
            })
    
    def _parse_threads_result(self, results: Dict, parts: List[str]):
        if len(parts) >= 7:
            results['threads'].append({
                'ip': parts[0],
                'events_sec': float(parts[1]),
                'avg_lat': float(parts[2]),
                'p95_lat': float(parts[3]),
                'min_lat': float(parts[4]),
                'max_lat': float(parts[5]),
                'sum_lat': float(parts[6])
            })
    
    def _parse_mutex_result(self, results: Dict, parts: List[str]):
        if len(parts) >= 7:
            results['mutex'].append({
                'ip': parts[0],
                'transactions': int(parts[1]),
                'tps': float(parts[2]),
                'avg_lat': float(parts[3]),
                'min_lat': float(parts[4]),
                'max_lat': float(parts[5]),
                'p95_lat': float(parts[6]),
                'sum_lat': float(parts[7]) if len(parts) > 7 else 0
            })
    
    def _parse_network_result(self, results: Dict, parts: List[str]):
        if len(parts) >= 5:
            try:
                retrans = int(parts[3])
            except ValueError:
                retrans = 0
            
            rtt_info = parts[4] if len(parts) >= 5 else ''
            
            cpu_info = parts[5] if len(parts) >= 6 else ''
            
            results['network'].append({
                'client_ip': parts[0],
                'server_ip': parts[1],
                'bandwidth': float(parts[2]),
                'retrans': retrans,
                'rtt': rtt_info,
                'cpu': cpu_info
            })