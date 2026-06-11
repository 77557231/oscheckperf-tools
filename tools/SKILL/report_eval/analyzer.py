from typing import Dict, List, Any
from .threshold_parser import ThresholdParser


class ReportAnalyzer:
    def __init__(self, thresholds: ThresholdParser):
        self.thresholds = thresholds
    
    def analyze_single_report(self, basic_info: Dict, hardware: Dict,
                              cpu_results: List[Dict], memory_results: List[Dict],
                              io_results: List[Dict], threads_results: List[Dict],
                              network_results: List[Dict]) -> str:
        analysis = []
        
        analysis.extend(self._analyze_cpu(cpu_results, hardware))
        analysis.extend(self._analyze_memory(memory_results))
        analysis.extend(self._analyze_io(io_results, hardware))
        analysis.extend(self._analyze_threads(threads_results))
        analysis.extend(self._analyze_network(network_results))
        analysis.extend(self._analyze_overall(cpu_results, memory_results, io_results, threads_results, network_results))
        
        return '\n'.join(analysis)
    
    def analyze_multi_report(self, comparison: Dict) -> str:
        analysis = []
        
        merged = comparison['merged']
        reports = comparison['reports']
        
        analysis.extend(self._analyze_multi_cpu(merged['cpu']))
        analysis.extend(self._analyze_multi_memory(merged['memory']))
        analysis.extend(self._analyze_multi_io(merged['io']))
        analysis.extend(self._analyze_multi_threads(merged['threads']))
        analysis.extend(self._analyze_multi_network(merged['network']))
        analysis.extend(self._analyze_multi_overall(merged, reports))
        
        return '\n'.join(analysis)
    
    def _analyze_cpu(self, results: List[Dict], hardware: Dict) -> List[str]:
        if not results:
            return []
        
        analysis = []
        fail_count = sum(1 for r in results if r['status'] == 'fail')
        warn_count = sum(1 for r in results if r['status'] == 'warn')
        
        if fail_count > 0:
            analysis.append(f"⚠️ CPU 性能问题：{fail_count} 个节点单核效率低于 75%，建议排查 CPU 配置、虚拟化层开销或资源争用")
        
        for r in results:
            if r['rate'] < 75:
                model = hardware.get(r['ip'], {}).get('cpu', {}).get('model', '')
                freq = hardware.get(r['ip'], {}).get('cpu', {}).get('freq', '')
                if 'VMware' in model:
                    analysis.append(f"  - {r['ip']}: 单核效率 {r['rate']:.1f}%，VMware 虚拟机可能存在 CPU steal time 影响")
                elif 'KVM' in model:
                    analysis.append(f"  - {r['ip']}: 单核效率 {r['rate']:.1f}%，建议检查 KVM 配置和宿主机负载")
                else:
                    analysis.append(f"  - {r['ip']}: 单核效率 {r['rate']:.1f}%，频率 {freq} GHz，建议检查 CPU 降频或节能策略")
        
        return analysis
    
    def _analyze_memory(self, results: List[Dict]) -> List[str]:
        if not results:
            return []
        
        analysis = []
        read_results = [r for r in results if r['mode'] == 'read']
        write_results = [r for r in results if r['mode'] == 'write']
        
        for ip in sorted(set(r['ip'] for r in results)):
            read = next((r for r in read_results if r['ip'] == ip), None)
            write = next((r for r in write_results if r['ip'] == ip), None)
            
            if read and read['is_vm']:
                if read['rate'] < 75:
                    analysis.append(f"⚠️ {ip}: 虚机内存读带宽 {read['rate']:.1f}%，低于预期，建议检查内存配置")
                if write and write['rate'] < 75:
                    analysis.append(f"⚠️ {ip}: 虚机内存写带宽 {write['rate']:.1f}%，低于预期")
            else:
                if read and read['rate'] < 75:
                    analysis.append(f"⚠️ {ip}: 物理机内存读带宽 {read['rate']:.1f}%，低于 JEDEC 理论值，建议检查内存通道配置")
                if write and write['rate'] < 75:
                    analysis.append(f"⚠️ {ip}: 物理机内存写带宽 {write['rate']:.1f}%，低于预期")
        
        return analysis
    
    def _analyze_io(self, results: List[Dict], hardware: Dict) -> List[str]:
        if not results:
            return []
        
        analysis = []
        
        for r in results:
            disk_type = hardware.get(r['ip'], {}).get('io', {}).get('type', 'Unknown')
            
            if disk_type == 'Virtual':
                continue
            
            latency = r.get('latency', 0)
            if latency > 100:
                analysis.append(f"⚠️ {r['ip']} ({r['mode']}): IO 延迟 {latency:.2f}ms，高于 100ms 阈值，建议检查存储配置")
            
            if disk_type == 'HDD' and r['mode'] == 'randread':
                iops = r.get('read_iops', 0)
                if iops < 150:
                    analysis.append(f"⚠️ {r['ip']}: HDD 随机读 IOPS {int(iops)}，低于 150 IOPS 基准")
            elif disk_type == 'SSD' and r['mode'] == 'randread':
                iops = r.get('read_iops', 0)
                if iops < 10000:
                    analysis.append(f"⚠️ {r['ip']}: SSD 随机读 IOPS {int(iops)}，低于 10,000 IOPS 基准")
            elif disk_type == 'NVMe' and r['mode'] == 'randread':
                iops = r.get('read_iops', 0)
                if iops < 50000:
                    analysis.append(f"⚠️ {r['ip']}: NVMe 随机读 IOPS {int(iops)}，低于 50,000 IOPS 基准")
        
        return analysis
    
    def _analyze_threads(self, results: List[Dict]) -> List[str]:
        if not results:
            return []
        
        analysis = []
        
        for r in results:
            if r['rate'] < 75:
                analysis.append(f"⚠️ {r['ip']}: 线程调度性能 {r['rate']:.1f}%，低于预期，建议检查线程数配置和系统调度参数")
        
        return analysis
    
    def _analyze_network(self, results: List[Dict]) -> List[str]:
        if not results:
            return []
        
        analysis = []
        
        for r in results:
            if r.get('retrans_status') == 'warn':
                analysis.append(f"⚠️ {r['client_ip']} → {r['server_ip']}: 网络重传次数 {r['retrans']}，建议检查网络链路稳定性")
            
            if r.get('speed') and r.get('speed') != 'Unknown' and r.get('rate') and r['rate'] < 75:
                analysis.append(f"⚠️ {r['client_ip']} → {r['server_ip']}: 网络带宽 {r['rate']:.1f}%，低于标称速率 {r['speed']}")
        
        return analysis
    
    def _analyze_overall(self, cpu, memory, io, threads, network) -> List[str]:
        analysis = []
        total_nodes = 0
        
        if cpu:
            total_nodes = len(cpu)
        
        fail_items = []
        if cpu:
            fail_items.extend([r for r in cpu if r['status'] == 'fail'])
        if memory:
            fail_items.extend([r for r in memory if r['status'] == 'fail'])
        if io:
            fail_items.extend([r for r in io if r['status'] == 'fail'])
        if threads:
            fail_items.extend([r for r in threads if r['status'] == 'fail'])
        if network:
            fail_items.extend([r for r in network if r['status'] == 'fail'])
        
        warn_items = []
        if cpu:
            warn_items.extend([r for r in cpu if r['status'] == 'warn'])
        if memory:
            warn_items.extend([r for r in memory if r['status'] == 'warn'])
        if io:
            warn_items.extend([r for r in io if r['status'] == 'warn'])
        if threads:
            warn_items.extend([r for r in threads if r['status'] == 'warn'])
        if network:
            warn_items.extend([r for r in network if r['status'] == 'warn'])
        
        if not fail_items and not warn_items:
            analysis.append("✅ 所有测试指标均通过，系统性能良好")
        elif not fail_items and warn_items:
            analysis.append(f"⚠️ 存在 {len(warn_items)} 项指标需要关注，整体性能基本满足要求")
        else:
            analysis.append(f"❌ 存在 {len(fail_items)} 项指标不通过，建议优先排查并优化相关配置")
        
        return analysis
    
    def _analyze_multi_cpu(self, results: List[Dict]) -> List[str]:
        if not results:
            return []
        
        analysis = []
        sources = set(r.get('source', '') for r in results)
        
        for source in sorted(sources):
            source_results = [r for r in results if r.get('source') == source]
            fail_count = sum(1 for r in source_results if r['status'] == 'fail')
            
            if fail_count > 0:
                analysis.append(f"⚠️ {source}: {fail_count} 个节点 CPU 性能不通过")
        
        return analysis
    
    def _analyze_multi_memory(self, results: List[Dict]) -> List[str]:
        if not results:
            return []
        
        analysis = []
        read_results = [r for r in results if r['mode'] == 'read']
        write_results = [r for r in results if r['mode'] == 'write']
        
        for source in sorted(set(r.get('source', '') for r in results)):
            source_read = [r for r in read_results if r.get('source') == source]
            source_write = [r for r in write_results if r.get('source') == source]
            
            avg_read_rate = sum(r['rate'] for r in source_read) / len(source_read) if source_read else 0
            avg_write_rate = sum(r['rate'] for r in source_write) / len(source_write) if source_write else 0
            
            analysis.append(f"📊 {source}: 平均内存读带宽 {avg_read_rate:.1f}%，写带宽 {avg_write_rate:.1f}%")
        
        return analysis
    
    def _analyze_multi_io(self, results: List[Dict]) -> List[str]:
        if not results:
            return []
        
        analysis = []
        
        for source in sorted(set(r.get('source', '') for r in results)):
            source_results = [r for r in results if r.get('source') == source]
            virtual_count = sum(1 for r in source_results if r.get('status') == 'skip')
            analysis.append(f"📊 {source}: {len(source_results)} 项 IO 测试，其中 {virtual_count} 项为虚拟盘（仅供参考）")
        
        return analysis
    
    def _analyze_multi_threads(self, results: List[Dict]) -> List[str]:
        if not results:
            return []
        
        analysis = []
        
        for source in sorted(set(r.get('source', '') for r in results)):
            source_results = [r for r in results if r.get('source') == source]
            avg_rate = sum(r['rate'] for r in source_results) / len(source_results) if source_results else 0
            analysis.append(f"📊 {source}: 平均线程调度性能 {avg_rate:.1f}%")
        
        return analysis
    
    def _analyze_multi_network(self, results: List[Dict]) -> List[str]:
        if not results:
            return []
        
        analysis = []
        
        for source in sorted(set(r.get('source', '') for r in results)):
            source_results = [r for r in results if r.get('source') == source]
            retrans_warn = sum(1 for r in source_results if r.get('retrans_status') == 'warn')
            analysis.append(f"📊 {source}: {len(source_results)} 条网络链路，{retrans_warn} 条存在重传警告")
        
        return analysis
    
    def _analyze_multi_overall(self, merged: Dict, reports: List[Dict]) -> List[str]:
        analysis = []
        
        total_fail = 0
        total_warn = 0
        
        for test_type in ['cpu', 'memory', 'io', 'threads', 'network']:
            if merged.get(test_type):
                total_fail += sum(1 for r in merged[test_type] if r.get('status') == 'fail')
                total_warn += sum(1 for r in merged[test_type] if r.get('status') == 'warn')
        
        if total_fail == 0 and total_warn == 0:
            analysis.append("✅ 所有报告的所有测试指标均通过，系统性能良好")
        elif total_fail == 0:
            analysis.append(f"⚠️ 所有报告中存在 {total_warn} 项指标需要关注")
        else:
            analysis.append(f"❌ 所有报告中存在 {total_fail} 项指标不通过，{total_warn} 项指标需要关注")
        
        analysis.append(f"📈 对比报告总数：{len(reports)} 个，总节点数：{len(merged.get('cpu', []))} 个")
        
        return analysis