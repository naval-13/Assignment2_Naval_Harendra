from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import CPULimitedHost, Host, Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.link import TCLink, Intf
from subprocess import call
import argparse


class LinuxRouter(Node):
    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        self.cmd('sysctl net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()

class MyNetworkTopology(Topo):
    def build(self, **_opts):
        # Subnets IP
        subnet1, subnet2 = '181.0.1.0/24', '182.0.1.0/24'

        # defining IP address for hosts
        ip_h1, ip_h2, ip_h3, ip_h4 = '181.0.1.11/24', '181.0.1.12/24', '182.0.1.13/24', '182.0.1.14/24'

        # define IP address for routersS
        ip_ra , ip_rb =  '181.0.1.1/24',  '182.0.1.1'

        # Create Nodes
        ra = self.addNode('ra', cls=LinuxRouter, ip=ip_ra)
        s1 = self.addSwitch('s1')
        h1 = self.addHost('h1', cls=Host, ip=ip_h1, defaultRoute='via 181.0.1.1')
        h2 = self.addHost('h2', cls=Host, ip=ip_h2, defaultRoute='via 181.0.1.1')
        
        rb = self.addNode('rb', cls=LinuxRouter, ip=ip_rb)
        s2 = self.addSwitch('s2')
        h3 = self.addHost('h3', cls=Host, ip=ip_h3, defaultRoute='via 182.0.1.1')
        h4 = self.addHost('h4', cls=Host, ip=ip_h4, defaultRoute='via 182.0.1.1')

        self.addLink(s1, ra, intfName2='ra-eth1', params2={'ip': ip_ra})
        self.addLink(s2, rb, intfName2='ra-eth2', params2={'ip': ip_ra})

        # Create Links
        connections = {(h1, s1), (h2, s1), (h3, s2), (h4, s2)}
        for i in connections:
            self.addLink(i[0], i[1])

        self.addLink(ra, rb, intfName1='link1', intfName2='link2', params1={'ip': '181.0.2.1/24'}, params2={'ip': '181.0.2.2/24'})

if __name__ == '__main__':
    setLogLevel('info')

    topo = MyNetworkTopology()
    net = Mininet(topo=topo, link=TCLink)

    # Add static routes on routers
    net['ra'].cmd('ip route add 182.0.1.0/24 via 181.0.2.2')
    net['rb'].cmd('ip route add 181.0.1.0/24 via 181.0.2.1')

    parser = argparse.ArgumentParser(description='Mininet')
    parser.add_argument('--config', type=str)
    parser.add_argument('--congestion_scheme', type=str)
    args = parser.parse_args()
    
    net.start()

    if args.config == 'b':
        server_process = net['h4'].popen(f"iperf -s -t 5 -i 0.5 -p 3000 > h4_server_output.txt", shell=True)
        client_process = net['h1'].popen(f"iperf -c 182.0.1.14 -t 5 -i 0.5 -p 3000 -z {args.congestion_scheme} > h1_client_{args.congestion_scheme}.txt", shell=True)
        client_process.wait()

    elif args.config == 'c':
        for h in ['h1', 'h2', 'h3']:
            server_process = net['h4'].popen(f"iperf -s -t 5 -i 0.5 -p 3000 > h4_server_output.txt", shell=True)
            client_process = net[h].popen(f"iperf -c 182.0.1.14 -t 5 -i 0.5 -p 3000 -z {args.congestion_scheme} > {h}_client_{args.congestion_scheme}.txt", shell=True)
            client_process.wait()
            server_process.wait()
    
    # Display routing tables on routers
    print('Routing Tables : \n')
    routers = {'ra'}
    for router in routers:
        info(net[router].cmd('route'))
        print()

    CLI(net)
    net.stop()
