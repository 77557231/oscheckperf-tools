import json
import os
import logging
import sys
from config import get_config
from discover import discover_capabilities, get_tool_description
from executor import execute_benchmark

CONFIG = get_config()

os.makedirs(CONFIG.LOG_DIR, exist_ok=True)
os.makedirs(CONFIG.TEMP_DIR, exist_ok=True)
os.makedirs(CONFIG.OUTPUT_DIR, exist_ok=True)

logging.basicConfig(
    level=CONFIG.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(CONFIG.LOG_DIR, 'mcp_server.log')),
    ]
)

logger = logging.getLogger('oscheckperf-mcp')

capabilities = None

def init_capabilities():
    global capabilities
    logger.info('Discovering oscheckperf capabilities...')
    capabilities = discover_capabilities()
    logger.info(f'Discovered commands: {capabilities.get("commands", [])}')
    logger.info(f'Discovered parameters: {list(capabilities.get("parameters", {}).keys())}')

def send_message(message):
    """Send message to stdout as JSON"""
    sys.stdout.write(json.dumps(message) + '\n')
    sys.stdout.flush()

def handle_initialize(request):
    """Handle MCP initialize request"""
    logger.info('Received initialize request')
    tool_desc = capabilities.get('tool_description', {}) if capabilities else get_tool_description()
    
    response = {
        'jsonrpc': '2.0',
        'id': request.get('id'),
        'result': {
            'protocolVersion': '2024-11-05',
            'capabilities': {
                'tools': {}
            },
            'serverInfo': {
                'name': 'oscheckperf-mcp',
                'version': '1.0.0'
            }
        }
    }
    send_message(response)

def handle_tools_list(request):
    """Handle MCP tools/list request"""
    logger.info('Received tools/list request')
    tool_desc = capabilities.get('tool_description', {}) if capabilities else get_tool_description()
    
    response = {
        'jsonrpc': '2.0',
        'id': request.get('id'),
        'result': {
            'tools': [tool_desc]
        }
    }
    send_message(response)

def handle_tools_call(request):
    """Handle MCP tools/call request"""
    logger.info('Received tools/call request')
    params = request.get('params', {})
    tool_name = params.get('name')
    tool_args = params.get('arguments', {})
    
    if tool_name != 'oscheckperf':
        error = {
            'jsonrpc': '2.0',
            'id': request.get('id'),
            'error': {
                'code': -32602,
                'message': f'Tool {tool_name} not found'
            }
        }
        send_message(error)
        return
    
    servers = tool_args.get('servers', [])
    command = tool_args.get('command', 'all')
    duration = tool_args.get('duration', CONFIG.DEFAULT_DURATION)
    io_tool = tool_args.get('io_tool', CONFIG.DEFAULT_IO_TOOL)
    output_dir = tool_args.get('output_dir', CONFIG.OUTPUT_DIR)
    
    if not servers or not isinstance(servers, list) or len(servers) == 0:
        error = {
            'jsonrpc': '2.0',
            'id': request.get('id'),
            'error': {
                'code': -32602,
                'message': 'servers parameter is required'
            }
        }
        send_message(error)
        return
    
    logger.info(f'Executing oscheckperf with command={command}, servers={servers}, duration={duration}')
    result = execute_benchmark(servers, command, duration, io_tool, output_dir)
    
    response = {
        'jsonrpc': '2.0',
        'id': request.get('id'),
        'result': {
            'content': [
                {
                    'type': 'text',
                    'text': json.dumps(result)
                }
            ]
        }
    }
    send_message(response)

def main():
    init_capabilities()
    logger.info('oscheckperf MCP Server started')
    
    for line in sys.stdin:
        try:
            line = line.strip()
            if not line:
                continue
            
            request = json.loads(line)
            logger.info(f'Received request: {json.dumps(request)[:200]}')
            
            method = request.get('method')
            
            if method == 'initialize':
                handle_initialize(request)
            elif method == 'tools/list':
                handle_tools_list(request)
            elif method == 'tools/call':
                handle_tools_call(request)
            else:
                error = {
                    'jsonrpc': '2.0',
                    'id': request.get('id'),
                    'error': {
                        'code': -32601,
                        'message': f'Unknown method {method}'
                    }
                }
                send_message(error)
                
        except json.JSONDecodeError as e:
            logger.error(f'Invalid JSON: {e}')
        except Exception as e:
            logger.error(f'Error handling request: {e}', exc_info=True)

if __name__ == '__main__':
    main()