import re
from typing import Dict, List, Any
from .config import Status
from .threshold_parser import ThresholdParser


class AchievementEvaluator:
    def __init__(self, thresholds: ThresholdParser):
        self.thresholds = thresholds
    
    def evaluate_cpu(self, results: List[Dict], hardware: Dict) -> List[Dict]:
        evaluated = []
        for r in results:
            ip = r['ip']
            cores = self._get_cores(ip, hardware)
            single_core = r['events_sec'] / cores
            baseline = self._get_cpu_baseline(ip, hardware)
            rate = (single_core / baseline) * 100
            
            evaluated.append({
                'ip': ip,
                'events_sec': r['events_sec'],
                'cores': cores,
                'single_core': single_core,
                'baseline': baseline,
                'rate': rate,
                'status': self._get_status(rate),
                'avg_lat': r['avg_lat']
            })
        return evaluated
    
    def evaluate_memory(self, results: List[Dict], hardware: Dict) -> List[Dict]:
        evaluated = []
        for r in results:
            ip = r['ip']
            mode = r['mode']
            is_vm = self._is_virtual(ip, hardware)
            
            if is_vm:
                if mode == 'read':
                    baseline = (self.thresholds.get('mem_vm_read_expect_low') + 
                               self.thresholds.get('mem_vm_read_expect_high')) / 2
                else:
                    baseline = (self.thresholds.get('mem_vm_write_expect_low') + 
                               self.thresholds.get('mem_vm_write_expect_high')) / 2
            else:
                baseline = self._calculate_memory_baseline(ip, hardware, mode)
            
            rate = (r['mib_sec'] / baseline) * 100
            
            evaluated.append({
                'ip': ip,
                'mib_sec': r['mib_sec'],
                'mode': mode,
                'baseline': baseline,
                'rate': rate,
                'status': self._get_status(rate),
                'is_vm': is_vm
            })
        return evaluated
    
    def evaluate_io(self, results: List[Dict], hardware: Dict) -> List[Dict]:
        evaluated = []
        for r in results:
            ip = r['ip']
            is_virtual_disk = self._is_virtual(ip, hardware)
            
            evaluated.append({
                'ip': ip,
                'read_iops': r['read_iops'],
                'write_iops': r['write_iops'],
                'total_iops': r['total_iops'],
                'read_bw': r['read_bw'],
                'write_bw': r['write_bw'],
                'total_bw': r['total_bw'],
                'latency': r['latency'],
                'p99': r['p99'],
                'mode': r['mode'],
                'is_virtual_disk': is_virtual_disk,
                'status': Status.SKIP.value if is_virtual_disk else Status.PASS.value
            })
        return evaluated
    
    def evaluate_threads(self, results: List[Dict], hardware: Dict) -> List[Dict]:
        evaluated = []
        for r in results:
            ip = r['ip']
            cores = self._get_cores(ip, hardware)
            single_core = r['events_sec'] / cores
            
            arch = hardware.get(ip, {}).get('cpu', {}).get('arch', '')
            model = hardware.get(ip, {}).get('cpu', {}).get('model', '')
            machine_type = hardware.get(ip, {}).get('cpu', {}).get('machine_type', '')
            
            is_virtual = 'VMware' in model or 'Virtual' in model or 'Virtual' in machine_type or 'KVM' in machine_type
            
            if 'aarch64' in arch.lower() or 'ARM' in model or '鲲鹏' in model:
                if is_virtual:
                    baseline = self.thresholds.get('threads_baseline_arm_kvm')
                else:
                    baseline = self.thresholds.get('threads_baseline_arm_physical')
            else:
                if is_virtual:
                    baseline = self.thresholds.get('threads_baseline_x86_vmware')
                else:
                    baseline = self.thresholds.get('threads_baseline_x86_physical')
            
            rate = (single_core / baseline) * 100
            
            evaluated.append({
                'ip': ip,
                'events_sec': r['events_sec'],
                'cores': cores,
                'single_core': single_core,
                'baseline': baseline,
                'rate': rate,
                'status': self._get_status(rate),
                'is_virtual': is_virtual
            })
        return evaluated
    
    def evaluate_mutex(self, results: List[Dict], hardware: Dict) -> List[Dict]:
        evaluated = []
        for r in results:
            ip = r['ip']
            cores = self._get_cores(ip, hardware)
            tps_per_core = r['tps'] / cores
            
            arch = hardware.get(ip, {}).get('cpu', {}).get('arch', '')
            model = hardware.get(ip, {}).get('cpu', {}).get('model', '')
            machine_type = hardware.get(ip, {}).get('cpu', {}).get('machine_type', '')
            
            is_virtual = 'VMware' in model or 'Virtual' in model or 'Virtual' in machine_type or 'KVM' in machine_type
            
            if 'aarch64' in arch.lower() or 'ARM' in model or '鲲鹏' in model:
                if is_virtual:
                    baseline = self.thresholds.get('mutex_baseline_arm_kvm')
                else:
                    baseline = self.thresholds.get('mutex_baseline_arm_physical')
            else:
                if is_virtual:
                    baseline = self.thresholds.get('mutex_baseline_x86_vmware')
                else:
                    baseline = self.thresholds.get('mutex_baseline_x86_physical')
            
            rate = (tps_per_core / baseline) * 100
            
            evaluated.append({
                'ip': ip,
                'tps': r['tps'],
                'cores': cores,
                'tps_per_core': tps_per_core,
                'baseline': baseline,
                'rate': rate,
                'status': self._get_status(rate),
                'is_virtual': is_virtual
            })
        return evaluated
    
    def evaluate_network(self, results: List[Dict], hardware: Dict) -> List[Dict]:
        evaluated = []
        retrans_warn = self.thresholds.get('net_retrans_warn')
        
        for r in results:
            client_ip = r['client_ip']
            server_ip = r['server_ip']
            
            speed = self._get_network_speed(client_ip, server_ip, hardware)
            client_driver = hardware.get(client_ip, {}).get('network', {}).get('driver', '')
            server_driver = hardware.get(server_ip, {}).get('network', {}).get('driver', '')
            driver = client_driver if client_driver else server_driver
            
            if speed and speed > 0:
                expected = speed / 8
                rate = (r['bandwidth'] / expected) * 100
                status = self._get_status(rate)
            else:
                expected = None
                rate = None
                status = Status.SKIP.value
            
            retrans_status = Status.WARN.value if r['retrans'] > retrans_warn else Status.PASS.value
            
            evaluated.append({
                'client_ip': client_ip,
                'server_ip': server_ip,
                'bandwidth': r['bandwidth'],
                'speed': speed,
                'driver': driver,
                'expected': expected,
                'rate': rate,
                'status': status,
                'retrans': r['retrans'],
                'retrans_status': retrans_status,
                'rtt': r['rtt']
            })
        return evaluated
    
    def _get_cores(self, ip: str, hardware: Dict) -> int:
        cores_str = hardware.get(ip, {}).get('cpu', {}).get('logical_cores', '0')
        try:
            cores = int(cores_str)
            return cores if cores > 0 else 1
        except ValueError:
            return 1
    
    def _is_virtual(self, ip: str, hardware: Dict) -> bool:
        model = hardware.get(ip, {}).get('cpu', {}).get('model', '')
        machine_type = hardware.get(ip, {}).get('cpu', {}).get('machine_type', '')
        return 'VMware' in model or 'Virtual' in model or 'Virtual' in machine_type or 'KVM' in machine_type
    
    def _get_cpu_baseline(self, ip: str, hardware: Dict) -> float:
        arch = hardware.get(ip, {}).get('cpu', {}).get('arch', '')
        model = hardware.get(ip, {}).get('cpu', {}).get('model', '')
        
        baseline = self.thresholds.get('cpu_baseline_x86')
        freq_ref = self.thresholds.get('cpu_freq_ref_x86')
        
        if 'aarch64' in arch.lower() or 'ARM' in model or '鲲鹏' in model:
            baseline = self.thresholds.get('cpu_baseline_arm')
            freq_ref = self.thresholds.get('cpu_freq_ref_arm')
        
        freq_str = hardware.get(ip, {}).get('cpu', {}).get('freq', '')
        try:
            actual_freq = float(freq_str)
            baseline = baseline * (actual_freq / freq_ref)
        except ValueError:
            pass
        
        return baseline
    
    def _calculate_memory_baseline(self, ip: str, hardware: Dict, mode: str) -> float:
        channels = hardware.get(ip, {}).get('mem', {}).get('channels', '0')
        
        try:
            channels = int(channels)
        except ValueError:
            channels = 1
        
        mem_freq_str = hardware.get(ip, {}).get('mem', {}).get('freq', '')
        try:
            mt_s = float(mem_freq_str)
            if mode == 'read':
                efficiency = self.thresholds.get('mem_phys_read_efficiency')
            else:
                efficiency = self.thresholds.get('mem_phys_write_efficiency')
            return channels * mt_s * 8 * efficiency
        except ValueError:
            if mode == 'read':
                return self.thresholds.get('mem_vm_read_expect_high')
            else:
                return self.thresholds.get('mem_vm_write_expect_high')
    
    def _get_network_speed(self, client_ip: str, server_ip: str, hardware: Dict) -> int:
        client_speed = hardware.get(client_ip, {}).get('network', {}).get('speed', '')
        server_speed = hardware.get(server_ip, {}).get('network', {}).get('speed', '')
        
        speed = None
        if client_speed and client_speed != 'Unknown' and client_speed != 'Unknown!':
            match = re.search(r'([\d]+)Mbps', client_speed)
            if not match:
                match = re.search(r'([\d]+)Mb/s', client_speed)
            if match:
                speed = int(match.group(1))
        
        if speed is None and server_speed and server_speed != 'Unknown' and server_speed != 'Unknown!':
            match = re.search(r'([\d]+)Mbps', server_speed)
            if not match:
                match = re.search(r'([\d]+)Mb/s', server_speed)
            if match:
                speed = int(match.group(1))
        
        return speed
    
    def _get_status(self, rate: float) -> str:
        good = self.thresholds.get('cpu_good_threshold')
        warn = self.thresholds.get('cpu_warn_threshold')
        
        if rate >= good:
            return Status.PASS.value
        elif rate >= warn:
            return Status.WARN.value
        else:
            return Status.FAIL.value