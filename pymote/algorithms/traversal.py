from pymote.algorithm import NodeAlgorithm
from pymote.message import Message


class DFT(NodeAlgorithm):
    required_params = ('informationKey',)
    default_params = {'neighborsKey': 'Neighbors'}

    def initializer(self):
        ini_nodes = []
        for node in self.network.nodes():
            node.memory[self.neighborsKey] = \
                node.compositeSensor.read()['Neighbors']
            node.status = 'IDLE'
            
            if self.informationKey in node.memory:
                node.status = 'INITIATOR'
                ini_nodes.append(node)
        for ini_node in ini_nodes:
            self.network.outbox.insert(0, Message(header=NodeAlgorithm.INI,
                                                 destination=ini_node))

    def initiator(self, node, message):
        node.memory['unvisitedNodes'] = list(node.memory[self.neighborsKey])
        node.memory['initiator'] = True
        self.visit(node, message)

    def idle(self, node, message):
        node.memory['entry'] = message.source
        node.memory['unvisitedNodes'] = list(node.memory[self.neighborsKey])
        node.memory['unvisitedNodes'].remove(message.source)
        node.memory['initiator'] = False
        self.visit(node, message)

    def visited(self, node, message):
        if message.header == 'Traversal':
            node.memory['unvisitedNodes'].remove(message.source)
            node.send(Message(destination=message.source,
                                  header='Backedge',
                                  data=message.data))
        elif message.header == 'Return':
            node.memory['unvisitedNodes'].remove(message.source)
            self.visit(node, message)
        elif message.header == 'Backedge':
            node.memory['unvisitedNodes'].remove(message.source)
            self.visit(node, message)

    def visit(self, node, message):
        if len(node.memory['unvisitedNodes']) != 0:
            next_node = node.memory['unvisitedNodes'][0]
            node.send(Message(destination=next_node,
                                  header='Traversal',
                                  data=message.data))
            node.status = 'VISITED'
        else:
            if node.memory['initiator'] == False:
                node.send(Message(destination=node.memory['entry'],
                                      header='Return',
                                      data=message.data))
            node.status = 'DONE'

    def done(self, node, message):
        pass

    STATUS = {
              'INITIATOR': initiator,
              'IDLE': idle,
              'DONE': done,
              'VISITED': visited,
             }