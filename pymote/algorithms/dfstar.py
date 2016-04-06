from pymote.algorithm import NodeAlgorithm
from pymote.message import Message

class DF(NodeAlgorithm):
    required_params = ('informationKey',)
    default_params = {'neighborsKey': 'Neighbors'}

    def initializer(self):
        for node in self.network.nodes():
            node.memory[self.neighborsKey] = node.compositeSensor.read()['Neighbors']
            node.status = 'IDLE'
            if self.informationKey in node.memory:
                ini_node = node
        ini_node.status = 'INITIATOR'
        self.network.outbox.insert(0, Message(header=NodeAlgorithm.INI, destination=ini_node))

    def initiator(self, node, message):
        node.memory['initiator'] = True
        node.memory['unvisitedNodes'] = list(node.memory[self.neighborsKey])
        next_node = node.memory['unvisitedNodes'][0]
        node.send(Message(destination=next_node, header='Traversal', data=message.data))
        
        for n in range(len(node.memory[self.neighborsKey])):
            if node.memory[self.neighborsKey][n] is not next_node:
                node.send(Message(destination=node.memory[self.neighborsKey][n], header='Visited', data=message.data))
        node.status = 'VISITED'

    def idle(self, node, message):
        if message.header == 'Traversal':
            node.memory['unvisitedNodes'] = list(node.memory[self.neighborsKey])
            self.first_visit(node, message)
        elif message.header == 'Visited':
            node.memory['unvisitedNodes'] = list(node.memory[self.neighborsKey])
            node.memory['unvisitedNodes'].remove(message.source)
            node.status = 'AVAILABLE'

    def available(self, node, message):
        if message.header == 'Traversal':
            self.first_visit(node, message)
        elif message.header == 'Visited':
            node.memory['unvisitedNodes'].remove(message.source)

    def visited(self, node, message):
        if message.header == 'Visited' or message.header == 'Traversal':
            node.memory['unvisitedNodes'].remove(message.source)
            if node.memory['unvisitedNodes'][0] is message.source:
                self.visit(node, message)
        elif message.header == 'Return':
            self.visit(node, message)            

    def first_visit(self, node, message):
        node.memory['initiator'] = False
        node.memory['entry'] = message.source
        node.memory['unvisitedNodes'].remove(message.source)

        if len(node.memory['unvisitedNodes']) != 0:
            next_node = node.memory['unvisitedNodes'][0]
            node.send(Message(destination=next_node,header='Traversal',data=message.data))
            for n in range(len(node.memory[self.neighborsKey])):
                if node.memory[self.neighborsKey][n] is not node.memory['entry'] and node.memory[self.neighborsKey][n] is not next_node:
                    node.send(Message(destination=node.memory[self.neighborsKey][n], header='Visited', data=message.data))
            node.status = 'VISITED'
        else:
            node.send(Message(destination=node.memory['entry'], header='Return', data=message.data))
            for n in range(len(node.memory[self.neighborsKey])):
                if node.memory[self.neighborsKey][n] is not node.memory['entry']:
                    node.send(Message(destination=node.memory[self.neighborsKey][n], header='Visited', data=message.data))
            node.status = 'DONE'

    def visit(self, node, message):
        if len(node.memory['unvisitedNodes']) != 0:
            next_node = node.memory['unvisitedNodes'][0]
            node.send(Message(destination=next_node, header='Traversal', data=message.data))
        else:
            if node.memory['initiator'] == False:
                node.send(Message(destination=node.memory['entry'], header='Return', data=message.data))
            node.status = 'DONE'

    def done(self, node, message):
        pass

    STATUS = {
              'INITIATOR': initiator,
              'IDLE': idle,
              'AVAILABLE': available,
              'DONE': done,
              'VISITED': visited,
             }