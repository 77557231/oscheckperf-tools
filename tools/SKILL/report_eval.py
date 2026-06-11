#!/usr/bin/env python3
"""
oscheckperf Report Evaluation Tool
Generate HTML evaluation report from report_benchmark.log

Features:
1. Parse report_benchmark.log to extract test metrics
2. Calculate achievement rates based on predefined thresholds
3. Generate HTML report with color-coded achievement rates
4. Auto-detect test modules and display only available data
5. Support multiple report comparison
6. Load thresholds from SKILL.md and thresholds.conf

Usage:
  python3 report_eval.py [report_files...] [-o output_dir]
  python3 report_eval.py --help

Example:
  python3 report_eval.py output/report_benchmark_20260607_094937.log
  python3 report_eval.py output/report_benchmark_*.log
"""

from report_eval.cli import main

if __name__ == '__main__':
    main()