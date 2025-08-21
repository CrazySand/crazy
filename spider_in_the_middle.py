import winreg
import asyncio

from mitmproxy import http
from mitmproxy.options import Options
from mitmproxy.tools.dump import DumpMaster

SERVER_PORT = 8080
UPSTREAM_PROXY: tuple | None = ('localhost', 7890)  # 确保上游代理在此地址运行

def enable_proxy(proxy_address=f'127.0.0.1:{SERVER_PORT}'):
    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r'Software\Microsoft\Windows\CurrentVersion\Internet Settings',
        0, 
        winreg.KEY_SET_VALUE
    )
    winreg.SetValueEx(key, 'ProxyEnable', 0, winreg.REG_DWORD, 1)
    winreg.SetValueEx(key, 'ProxyServer', 0, winreg.REG_SZ, proxy_address)
    winreg.CloseKey(key)

def disable_proxy():
    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r'Software\Microsoft\Windows\CurrentVersion\Internet Settings',
        0, 
        winreg.KEY_SET_VALUE
    )
    winreg.SetValueEx(key, 'ProxyEnable', 0, winreg.REG_DWORD, 0)
    winreg.SetValueEx(key, 'ProxyServer', 0, winreg.REG_SZ, '')
    winreg.CloseKey(key)

class HTTPSniffer:

    def __init__(self):
        self.master = None

    def request(self, flow: http.HTTPFlow):
        if UPSTREAM_PROXY:
            try:
                flow.live.change_upstream_proxy_server(UPSTREAM_PROXY)
            except Exception as e:
                # flow.kill()
                pass
                
    async def response(self, flow: http.HTTPFlow):
        print(flow.request.url)
        if True:
            self.master.shutdown()

async def run_master():

    # 配置mitmproxy选项
    options = Options(
        listen_host='0.0.0.0',
        listen_port=SERVER_PORT,
        # 将mode参数改为列表形式
        mode=[f'upstream:{UPSTREAM_PROXY[0]}:{UPSTREAM_PROXY[1]}'] if UPSTREAM_PROXY else ['regular']
    )
    options.http2 = False
    options.ssl_insecure = True  # 不验证上游代理的SSL证书，生产环境可移除
    
    # 创建mitmproxy实例
    m = DumpMaster(options, with_termlog=False, with_dumper=False)
    
    # 添加我们的嗅探器
    sniffer = HTTPSniffer()
    sniffer.master = m
    m.addons.add(sniffer)
    
    await m.run()

async def main():
    try:
        enable_proxy()
        await run_master()
    finally:
        disable_proxy()

if __name__ == '__main__':
    asyncio.run(main())