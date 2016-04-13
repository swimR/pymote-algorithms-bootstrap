from pymote.networkgenerator import NetworkGenerator
from pymote.simulation import Simulation
from pymote.algorithms import dfstar
from pymote.algorithms import traversal
from pymote.npickle import write_pickle
from pymote.network import Network


def network1():
    net = Network()
    net.add_node(pos=(100, 100), commRange=51)
    net.add_node(pos=(100, 150), commRange=51)
    net.add_node(pos=(100, 200), commRange=51)
    net.add_node(pos=(100, 250), commRange=51)
    net.add_node(pos=(100, 300), commRange=51)
    net.add_node(pos=(100, 350), commRange=51)
    net.add_node(pos=(100, 400), commRange=51)
    net.add_node(pos=(100, 450), commRange=51)
    net.add_node(pos=(100, 500), commRange=51)
    net.add_node(pos=(100, 550), commRange=51)
    return net


def network2():
    net = Network()
    net.add_node(pos=(100, 100), commRange=51)
    net.add_node(pos=(100, 150), commRange=51)
    net.add_node(pos=(100, 200), commRange=51)
    net.add_node(pos=(100, 250), commRange=51)
    net.add_node(pos=(150, 100), commRange=51)
    net.add_node(pos=(200, 100), commRange=51)
    net.add_node(pos=(250, 100), commRange=51)
    net.add_node(pos=(150, 250), commRange=51)
    net.add_node(pos=(200, 250), commRange=51)
    net.add_node(pos=(250, 250), commRange=51)
    net.add_node(pos=(250, 200), commRange=51)
    net.add_node(pos=(250, 150), commRange=51)
    return net


def network3():
    net = Network()
    net.add_node(pos=(0,0), commRange=201)
    net.add_node(pos=(200, 0), commRange=201)
    net.add_node(pos=(0, 200), commRange=201)
    net.add_node(pos=(200, 100), commRange=201)
    net.add_node(pos=(400, 100), commRange=201)
    net.add_node(pos=(400, 200), commRange=201)
    net.add_node(pos=(500, 300), commRange=201)
    net.add_node(pos=(200, 300), commRange=201)
    return net


def network4():
    net = Network()
    net.add_node(pos=(100, 100), commRange=350)
    net.add_node(pos=(100, 500), commRange=501)
    net.add_node(pos=(400, 200), commRange=501)
    net.add_node(pos=(599, 200), commRange=401)
    net.add_node(pos=(500, 50), commRange=401)
    net.add_node(pos=(500, 400), commRange=350)
    return net


def network5():
    net = Network()
    net.add_node(pos=(100,100), commRange=401)
    net.add_node(pos=(100, 500), commRange=501)
    net.add_node(pos=(400, 200), commRange=501)
    net.add_node(pos=(599, 200), commRange=401)
    net.add_node(pos=(500, 50), commRange=401)
    net.add_node(pos=(500,400), commRange=401)
    return net


def network6():
    net_gen = NetworkGenerator(20, comm_range=400)
    net = net_gen.generate_random_network()
    return net


def network7():
    net_gen = NetworkGenerator(10, comm_range=500)
    net = net_gen.generate_random_network()
    return net


def network8():
    net_gen = NetworkGenerator(50, comm_range=300)
    net = net_gen.generate_random_network()
    return net


def network9():
    net_gen = NetworkGenerator(5, commRange=400)
    net = net_gen.generate_random_network()
    return net


def network10():
    net_gen = NetworkGenerator(30, comm_range=500)
    net = net_gen.generate_random_network()
    return net


def test_network():
    algorithmsList = [dfstar.DFStar, traversal.DFT]
    for algorithm in algorithmsList:
        netList = [network1(), network2(), network3(), network4(), network5(), network6(), network7(), network8(),
                   network9(), network10()]
        for net in netList:
            net.algorithms = (algorithm, )
            sim = Simulation(net)
            try:
                sim.run()
            except Exception, e:
                import pdb; pdb.set_trace()
                write_pickle(net, 'net_exception.npc.gz')
                raise e

            for node in net.nodes():
                try:
                    assert node.status == 'DONE'
                    assert len(node.memory['unvisitedNodes']) == 0
                except AssertionError:
                    write_pickle(net, 'net_assertion_error.npc.gz')


if __name__=='__main__':
	test_network()