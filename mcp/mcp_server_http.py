import json
import os
import logging
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
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
        logging.StreamHandler()
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

class MCPRequestHandler(BaseHTTPRequestHandler):
    def send_json_response(self, data, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def send_sse_response(self):
        """Send SSE response for Trae platform"""
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Connection', 'keep-alive')
        self.end_headers()
        
        try:
            tool_desc = capabilities.get('tool_description', {}) if capabilities else get_tool_description()
            init_data = {
                'type': 'tool_list',
                'tools': [tool_desc]
            }
            event_data = json.dumps(init_data)
            event = f'event: tool_list\ndata: {event_data}\n\n'
            self.wfile.write(event.encode('utf-8'))
            self.wfile.flush()
            
            while True:
                time.sleep(30)
                self.wfile.write(b': heartbeat\n\n')
                self.wfile.flush()
                
        except Exception as e:
            logger.info(f'SSE connection closed: {e}')
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def do_GET(self):
        if self.path == '/mcp/tools' or self.path == '/tools':
            self.handle_get_tools()
        elif self.path == '/mcp/health' or self.path == '/health':
            self.handle_health()
        elif self.path == '/' or self.path == '/mcp':
            self.send_sse_response()
        else:
            self.send_json_response({'error': 'Not found'}, 404)
    
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            logger.info(f'Received POST to {self.path}: {body[:200]}...')
            
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                self.send_json_response({'error': 'Invalid JSON'}, 400)
                return
            
            if data.get('jsonrpc') == '2.0':
                self.handle_mcp_protocol(data)
                return
            
            if self.path == '/mcp/invoke' or self.path == '/invoke':
                self.handle_simple_invoke(data)
            elif self.path == '/mcp/discover' or self.path == '/discover':
                self.handle_discover()
            elif self.path == '/' or self.path == '/mcp':
                self.handle_mcp_protocol(data)
            else:
                self.send_json_response({'error': 'Not found'}, 404)
                
        except Exception as e:
            logger.error(f'Error handling POST: {e}')
            import traceback
            logger.error(traceback.format_exc())
            self.send_json_response({'error': str(e)}, 500)
    
    def handle_mcp_protocol(self, data):
        logger.info('Handling MCP protocol request')
        method = data.get('method')
        params = data.get('params', {})
        
        if method == 'initialize':
            result = {
                'protocolVersion': '2024-11-05',
                'capabilities': {
                    'tools': {}
                },
                'serverInfo': {
                    'name': 'oscheckperf-mcp',
                    'version': '1.0.0'
                }
            }
            response = {
                'jsonrpc': '2.0',
                'id': data.get('id'),
                'result': result
            }
            self.send_json_response(response)
        
        elif method == 'tools/list':
            tool_desc = capabilities.get('tool_description', {}) if capabilities else get_tool_description()
            result = {
                'tools': [tool_desc]
            }
            response = {
                'jsonrpc': '2.0',
                'id': data.get('id'),
                'result': result
            }
            self.send_json_response(response)
        
        elif method == 'tools/call':
            tool_name = params.get('name')
            tool_args = params.get('arguments', {})
            
            if tool_name != 'oscheckperf':
                error = {
                    'jsonrpc': '2.0',
                    'id': data.get('id'),
                    'error': {
                        'code': -32602,
                        'message': f'Tool {tool_name} not found'
                    }
                }
                self.send_json_response(error, 400)
                return
            
            servers = tool_args.get('servers', [])
            command = tool_args.get('command', 'all')
            duration = tool_args.get('duration', CONFIG.DEFAULT_DURATION)
            io_tool = tool_args.get('io_tool', CONFIG.DEFAULT_IO_TOOL)
            output_dir = tool_args.get('output_dir', CONFIG.OUTPUT_DIR)
            
            if not servers or not isinstance(servers, list) or len(servers) == 0:
                error = {
                    'jsonrpc': '2.0',
                    'id': data.get('id'),
                    'error': {
                        'code': -32602,
                        'message': 'servers parameter is required'
                    }
                }
                self.send_json_response(error, 400)
                return
            
            logger.info(f'Executing oscheckperf with command={command}, servers={servers}, duration={duration}')
            result = execute_benchmark(servers, command, duration, io_tool, output_dir)
            
            response = {
                'jsonrpc': '2.0',
                'id': data.get('id'),
                'result': {
                    'content': [
                        {
                            'type': 'text',
                            'text': json.dumps(result)
                        }
                    ]
                }
            }
            self.send_json_response(response)
        
        else:
            error = {
                'jsonrpc': '2.0',
                'id': data.get('id'),
                'error': {
                    'code': -32601,
                    'message': f'Unknown method {method}'
                }
            }
            self.send_json_response(error, 400)
    
    def handle_get_tools(self):
        try:
            tool_desc = capabilities.get('tool_description', {}) if capabilities else get_tool_description()
            self.send_json_response({'tools': [tool_desc]})
        except Exception as e:
            logger.error(f'Error getting tools: {str(e)}')
            self.send_json_response({'error': str(e)}, 500)
    
    def handle_health(self):
        self.send_json_response({'status': 'healthy', 'capabilities_loaded': capabilities is not None})
    
    def handle_simple_invoke(self, data):
        try:
            tool_name = data.get('tool') or data.get('name')
            args = data.get('args') or data.get('parameters') or {}
            
            if tool_name and tool_name != 'oscheckperf':
                self.send_json_response({'success': False, 'error': f'Tool {tool_name} not found'}, 404)
                return
            
            servers = args.get('servers', args.get('hosts', []))
            command = args.get('command', args.get('name', 'all'))
            duration = args.get('duration', CONFIG.DEFAULT_DURATION)
            io_tool = args.get('io_tool', CONFIG.DEFAULT_IO_TOOL)
            output_dir = args.get('output_dir', CONFIG.OUTPUT_DIR)
            
            if not servers or not isinstance(servers, list) or len(servers) == 0:
                logger.warning('No servers provided')
                self.send_json_response({'success': False, 'error': 'servers parameter is required'}, 400)
                return
            
            logger.info(f'Executing oscheckperf with command={command}, servers={servers}, duration={duration}')
            result = execute_benchmark(servers, command, duration, io_tool, output_dir)
            
            response = {
                'success': result['success'],
                'command': result['command'],
                'report_path': result['report_path']
            }
            
            if result.get('stdout'):
                response['stdout'] = result['stdout']
            if result.get('stderr'):
                response['stderr'] = result['stderr']
            if not result['success']:
                response['error'] = result.get('stderr', 'Unknown error')
            
            self.send_json_response(response)
        
        except Exception as e:
            logger.error(f'Error during tool invocation: {str(e)}')
            self.send_json_response({'success': False, 'error': str(e)}, 500)
    
    def handle_discover(self):
        global capabilities
        try:
            capabilities = discover_capabilities()
            self.send_json_response({'success': True, 'capabilities': capabilities})
        except Exception as e:
            logger.error(f'Error during discovery: {str(e)}')
            self.send_json_response({'success': False, 'error': str(e)}, 500)
    
    def log_message(self, format, *args):
        logger.info(format % args)

def run_server():
    init_capabilities()
    server_address = (CONFIG.MCP_HOST, CONFIG.MCP_PORT)
    httpd = HTTPServer(server_address, MCPRequestHandler)
    httpd.timeout = 60
    logger.info(f'Starting MCP Server on {CONFIG.MCP_HOST}:{CONFIG.MCP_PORT}')
    logger.info('Supported endpoints:')
    logger.info('  GET  /mcp - SSE endpoint (for Trae platform)')
    logger.info('  GET  /mcp/tools - Get available tools')
    logger.info('  POST /mcp/invoke - Invoke tool (simple format)')
    logger.info('  GET  /mcp/health - Health check')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()