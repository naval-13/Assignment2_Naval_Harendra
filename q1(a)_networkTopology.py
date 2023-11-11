# Mininet modules
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import CPULimitedHost, Host, Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.link import TCLink, Intf
from subprocess import call

# Custom LinuxRouter class with IP forwarding
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
        subnet1, subnet2, subnet3 = '188.0.1.0/24', '189.0.1.0/24', '190.0.1.0/24'

        # defining IP address for hosts
        ip_h1, ip_h2, ip_h3, ip_h4, ip_h5, ip_h6 = '188.0.1.11/24', '188.0.1.12/24', '189.0.1.13/24', '189.0.1.14/24', '190.0.1.15/24', '190.0.1.16/24'

        # define IP address for routers
        ip_ra, ip_rb, ip_rc = '188.0.1.1/24', '189.0.1.1/24', '190.0.1.1/24'

        # Making individual subnet
        ra = self.addNode('ra', cls=LinuxRouter, ip=ip_ra)
        s1 = self.addSwitch('s1')
        h1 = self.addHost('h1', cls=Host, ip=ip_h1, defaultRoute='via 188.0.1.1')
        h2 = self.addHost('h2', cls=Host, ip=ip_h2, defaultRoute='via 188.0.1.1')

        rb = self.addNode('rb', cls=LinuxRouter, ip=ip_rb)
        s2 = self.addSwitch('s2')
        h3 = self.addHost('h3', cls=Host, ip=ip_h3, defaultRoute='via 189.0.1.1')
        h4 = self.addHost('h4', cls=Host, ip=ip_h4, defaultRoute='via 189.0.1.1')

        rc = self.addNode('rc', cls=LinuxRouter, ip=ip_rc)
        s3 = self.addSwitch('s3')
        h5 = self.addHost('h5', cls=Host, ip=ip_h5, defaultRoute='via 190.0.1.1')
        h6 = self.addHost('h6', cls=Host, ip=ip_h6, defaultRoute='via 190.0.1.1')

        # Connection between switch and routers
        self.addLink(s1, ra, intfName2='ra-eth0', params2={'ip': ip_ra})
        self.addLink(s2, rb, intfName2='rb-eth0', params2={'ip': ip_rb})
        self.addLink(s3, rc, intfName2='rc-eth0', params2={'ip': ip_rc})

        # adding link among host and switch
        connections = {(h1,s1), (h2,s1),(h3,s2),(h4,s2),(h5,s3),(h6,s3)}
        for i in connections:
            self.addLink(i[0],i[1])

        # Add links between routers 
        self.addLink(ra, rb, intfName1='link1',intfName2='link4', params1={'ip': '188.0.2.1/24'}, params2={'ip': '188.0.2.2/24'})
        self.addLink(rb, rc, intfName1='link2',intfName2='link5', params1={'ip': '189.0.2.1/24'}, params2={'ip': '189.0.2.2/24'})
        self.addLink(ra, rc, intfName1='link3',intfName2='link6',params1={'ip': '190.0.2.1/24'}, params2={'ip': '190.0.2.2/24'})
        



if __name__ == '__main__':
    
    #to see log messages
    setLogLevel('info')

      # Instance of the custom network topology class
    topo = MyNetworkTopology()

     # initialising a Mininet network using the defined topology
    net = Mininet(topo=topo, link=TCLink, waitConnected=True)

    # Add static routes on routers
    net['ra'].cmd('ip route add 189.0.1.0/24 via 188.0.2.2')
    net['ra'].cmd('ip route add 190.0.1.0/24 via 190.0.2.2')
    net['rb'].cmd('ip route add 188.0.1.0/24  via 188.0.2.1')
    net['rb'].cmd('ip route add 190.0.1.0/24 via 189.0.2.2')
    net['rc'].cmd('ip route add 188.0.1.0/24 via 190.0.2.1')
    net['rc'].cmd('ip route add 189.0.1.0/24 via 189.0.2.1')

    # Start the Mininet network
    net.start()


    # Display routing tables on routers
    print('Routing Tables : \n')
    routers = {'ra', 'rb', 'rc'}
    for router in routers:
        info(net[router].cmd('route'))
        print()

    # Start the Mininet CLI for user interaction
    CLI(net)

    # Stop the Mininet network upon CLI exit
    net.stop()

