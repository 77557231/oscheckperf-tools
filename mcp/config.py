import os

class Config:
    MCP_HOST = os.getenv('MCP_HOST', '0.0.0.0')
    MCP_PORT = int(os.getenv('MCP_PORT', 8080))
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_DIR = os.getenv('LOG_DIR', './logs')
    TEMP_DIR = os.getenv('TEMP_DIR', './tmp')
    OUTPUT_DIR = os.getenv('OUTPUT_DIR', './output')
    
    DEFAULT_DURATION = 60
    DEFAULT_IO_TOOL = 'sysbench'
    
    OSCHECKPERF_PATH = os.getenv('OSCHECKPERF_PATH', './oscheckperf')

config = Config()

def get_config():
    return config