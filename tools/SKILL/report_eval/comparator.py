from typing import Dict, List, Any
from .report_parser import ReportParser
from .evaluator import AchievementEvaluator
from .threshold_parser import ThresholdParser


class ReportComparator:
    def __init__(self, thresholds: ThresholdParser):
        self.thresholds = thresholds
        self.evaluator = AchievementEvaluator(thresholds)
    
    def compare_reports(self, report_files: List[str]) -> Dict[str, Any]:
        reports = []
        for file_path in report_files:
            parser = ReportParser(file_path)
            basic_info = parser.parse_basic_info()
            hardware = parser.parse_hardware_summary()
            test_results = parser.parse_test_results()
            
            report_data = {
                'file': file_path,
                'basic_info': basic_info,
                'hardware': hardware,
                'test_results': test_results,
                'evaluated': {}
            }
            
            self._evaluate_report(report_data)
            reports.append(report_data)
        
        return self._build_comparison(reports)
    
    def _evaluate_report(self, report_data: Dict[str, Any]):
        test_results = report_data['test_results']
        hardware = report_data['hardware']
        evaluated = {}
        
        if test_results.get('cpu') and test_results['cpu'] is not None:
            evaluated['cpu'] = self.evaluator.evaluate_cpu(test_results['cpu'], hardware)
        
        if test_results.get('memory') and test_results['memory'] is not None:
            evaluated['memory'] = self.evaluator.evaluate_memory(test_results['memory'], hardware)
        
        if test_results.get('io') and test_results['io'] is not None:
            evaluated['io'] = self.evaluator.evaluate_io(test_results['io'], hardware)
        
        if test_results.get('threads') and test_results['threads'] is not None:
            evaluated['threads'] = self.evaluator.evaluate_threads(test_results['threads'], hardware)
        
        if test_results.get('mutex') and test_results['mutex'] is not None:
            evaluated['mutex'] = self.evaluator.evaluate_mutex(test_results['mutex'], hardware)
        
        if test_results.get('network') and test_results['network'] is not None:
            evaluated['network'] = self.evaluator.evaluate_network(test_results['network'], hardware)
        
        report_data['evaluated'] = evaluated
    
    def _build_comparison(self, reports: List[Dict]) -> Dict[str, Any]:
        comparison = {
            'reports': reports,
            'summary': {},
            'merged': {
                'hardware': {},
                'cpu': [],
                'memory': [],
                'io': [],
                'threads': [],
                'mutex': [],
                'network': []
            }
        }
        
        comparison['summary'] = self._generate_summary(reports)
        comparison['merged'] = self._merge_reports(reports)
        
        return comparison
    
    def _generate_summary(self, reports: List[Dict]) -> Dict[str, Any]:
        summary = {
            'total_reports': len(reports),
            'total_nodes': 0,
            'test_types': []
        }
        
        all_test_types = set()
        
        for report in reports:
            if report['evaluated'].get('cpu'):
                summary['total_nodes'] += len(report['evaluated']['cpu'])
            
            for test_type in report['evaluated']:
                if report['evaluated'][test_type]:
                    all_test_types.add(test_type)
        
        summary['test_types'] = sorted(list(all_test_types))
        
        return summary
    
    def _merge_reports(self, reports: List[Dict]) -> Dict[str, Any]:
        merged = {
            'hardware': {},
            'cpu': [],
            'memory': [],
            'io': [],
            'threads': [],
            'mutex': [],
            'network': []
        }
        
        ip_mapping = self._build_ip_mapping(reports)
        
        for report_idx, report in enumerate(reports):
            file_name = report['file'].split('/')[-1]
            report_label = f"报告{report_idx+1}"
            
            for ip, info in report['hardware'].items():
                unique_ip = ip_mapping.get(ip, ip)
                merged['hardware'][unique_ip] = info
                merged['hardware'][unique_ip]['source'] = report_label
                merged['hardware'][unique_ip]['file'] = file_name
            
            for test_type in ['cpu', 'memory', 'io', 'threads', 'mutex']:
                if report['evaluated'].get(test_type):
                    for item in report['evaluated'][test_type]:
                        unique_ip = ip_mapping.get(item['ip'], item['ip'])
                        item_copy = item.copy()
                        item_copy['ip'] = unique_ip
                        item_copy['source'] = report_label
                        item_copy['file'] = file_name
                        merged[test_type].append(item_copy)
            
            if report['evaluated'].get('network'):
                for item in report['evaluated']['network']:
                    unique_client_ip = ip_mapping.get(item['client_ip'], item['client_ip'])
                    unique_server_ip = ip_mapping.get(item['server_ip'], item['server_ip'])
                    item_copy = item.copy()
                    item_copy['client_ip'] = unique_client_ip
                    item_copy['server_ip'] = unique_server_ip
                    item_copy['source'] = report_label
                    item_copy['file'] = file_name
                    merged['network'].append(item_copy)
        
        return merged
    
    def _build_ip_mapping(self, reports: List[Dict]) -> Dict[str, str]:
        ip_counter = {}
        ip_mapping = {}
        
        for report in reports:
            all_ips = set()
            
            for ip in report['hardware'].keys():
                all_ips.add(ip)
            
            for test_type in ['cpu', 'memory', 'io', 'threads', 'mutex']:
                if report['evaluated'].get(test_type):
                    for item in report['evaluated'][test_type]:
                        all_ips.add(item['ip'])
            
            if report['evaluated'].get('network'):
                for item in report['evaluated']['network']:
                    all_ips.add(item['client_ip'])
                    all_ips.add(item['server_ip'])
            
            for ip in all_ips:
                if ip not in ip_counter:
                    ip_counter[ip] = 1
                    ip_mapping[ip] = ip
                else:
                    ip_counter[ip] += 1
                    ip_mapping[ip] = f"{ip}_{ip_counter[ip]}"
        
        return ip_mapping