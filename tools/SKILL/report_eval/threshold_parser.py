import os
import re
from typing import Dict, Any, Optional
from .config import ThresholdConfig


class ThresholdParser:
    def __init__(self, skill_dir: str):
        self.skill_dir = skill_dir
        self.config = ThresholdConfig()
        self._load_config()
    
    def _load_config(self):
        skill_md_path = os.path.join(self.skill_dir, 'SKILL.md')
        conf_path = os.path.join(self.skill_dir, 'thresholds.conf')
        
        if os.path.exists(skill_md_path):
            self._parse_skill_md(skill_md_path)
        
        if os.path.exists(conf_path):
            self._parse_conf_file(conf_path)
    
    def _parse_skill_md(self, skill_md_path: str):
        try:
            with open(skill_md_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self._parse_cpu_rules(content)
            self._parse_memory_rules(content)
            self._parse_threads_rules(content)
            self._parse_mutex_rules(content)
            self._parse_network_rules(content)
            self._parse_io_rules(content)
            self._parse_common_thresholds(content)
            
        except Exception as e:
            print(f"Warning: Failed to parse SKILL.md: {e}")
    
    def _parse_conf_file(self, conf_path: str):
        try:
            with open(conf_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip().lower()
                        value = value.strip()
                        self._set_config_value(key, value)
        except Exception as e:
            print(f"Warning: Failed to parse thresholds.conf: {e}")
    
    def _set_config_value(self, key: str, value: str):
        try:
            float_val = float(value)
            if hasattr(self.config, key):
                setattr(self.config, key, float_val)
            elif key == 'report_version':
                self.config.report_version = value
        except ValueError:
            if key == 'report_version':
                self.config.report_version = value
    
    def _parse_cpu_rules(self, content: str):
        match = re.search(r'基线值：\s*[-]\s*ARM\s*\(.*?\):\s*([\d.]+)', content)
        if match:
            self.config.cpu_baseline_arm = float(match.group(1))
        
        match = re.search(r'[-]\s*x86\s*\(.*?\):\s*([\d.]+)', content)
        if match:
            self.config.cpu_baseline_x86 = float(match.group(1))
        
        match = re.search(r'参考频率：\s*[-]\s*ARM:\s*([\d.]+)', content)
        if match:
            self.config.cpu_freq_ref_arm = float(match.group(1))
        
        match = re.search(r'[-]\s*x86:\s*([\d.]+)', content)
        if match:
            self.config.cpu_freq_ref_x86 = float(match.group(1))
    
    def _parse_memory_rules(self, content: str):
        match = re.search(r'读\s*≥?\s*([\d,]+)\s*MiB/s', content)
        if match:
            self.config.mem_vm_read_expect_low = float(match.group(1).replace(',', ''))
        
        match = re.search(r'写\s*≥?\s*([\d,]+)\s*MiB/s', content)
        if match:
            self.config.mem_vm_write_expect_low = float(match.group(1).replace(',', ''))
        
        match = re.search(r'效率系数\)\s*读([\d.]+)%', content)
        if match:
            self.config.mem_phys_read_efficiency = float(match.group(1)) / 100
        
        match = re.search(r'写([\d.]+)%', content)
        if match:
            self.config.mem_phys_write_efficiency = float(match.group(1)) / 100
    
    def _parse_threads_rules(self, content: str):
        match = re.search(r'ARM\s+KVM：\s*[-]\s*单核\s*evt/s\s*期望：\s*([\d,]+)', content)
        if match:
            self.config.threads_baseline_arm_kvm = float(match.group(1).replace(',', ''))
        
        match = re.search(r'x86\s+VMware：\s*[-]\s*单核\s*evt/s\s*期望：\s*([\d,]+)', content)
        if match:
            self.config.threads_baseline_x86_vmware = float(match.group(1).replace(',', ''))
    
    def _parse_mutex_rules(self, content: str):
        match = re.search(r'TPS/core\s+期望：\s*([\d,]+)', content)
        if match:
            self.config.mutex_baseline_arm_kvm = float(match.group(1).replace(',', ''))
    
    def _parse_network_rules(self, content: str):
        match = re.search(r'重传次数\s*≥?\s*([\d,]+)', content)
        if match:
            self.config.net_retrans_warn = float(match.group(1).replace(',', ''))
    
    def _parse_io_rules(self, content: str):
        match = re.search(r'HDD:\s*随机读写\s*IOPS\s*≥\s*([\d,]+)', content)
        if match:
            self.config.io_hdd_iops = float(match.group(1).replace(',', ''))
        
        match = re.search(r'SSD:\s*随机读写\s*IOPS\s*≥\s*([\d,]+)', content)
        if match:
            self.config.io_ssd_iops = float(match.group(1).replace(',', ''))
        
        match = re.search(r'NVMe:\s*随机读写\s*IOPS\s*≥\s*([\d,]+)', content)
        if match:
            self.config.io_nvme_iops = float(match.group(1).replace(',', ''))
    
    def _parse_common_thresholds(self, content: str):
        match = re.search(r'达成率\s*≥?\s*([\d]+)%', content)
        if match:
            self.config.cpu_good_threshold = float(match.group(1))
        
        match = re.search(r'([\d]+)%\s*-\s*([\d]+)%', content)
        if match:
            self.config.cpu_warn_threshold = float(match.group(1))
    
    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self.config, key, default)