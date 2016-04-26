from pymote.algorithm import NodeAlgorithm
from pymote.message import Message

class Saturation(NodeAlgorithm):
    required_params = {}
    default_params = {'neighborsKey': 'Neighbors'}

    def initializer(self):
        for node in self.network.nodes():
            node.memory[self.neighborsKey] = node.compositeSensor.read()['Neighbors']
            node.status = 'AVAILABLE'
        ini_node = self.network.nodes()[0]
        self.network.outbox.insert(0, Message(header=NodeAlgorithm.INI, destination=ini_node))


    def send_message(self, node, message, nodeNeighbors):
        for i in range(len(nodeNeighbors)):
            node.send(Message(destination=nodeNeighbors[i], header='Activate', data=message.data))

        self.initialize(node, message)

        node.memory['neighbors'] = list(node.memory[self.neighborsKey])
        if len(node.memory['neighbors']) == 1:
            self.prepare_message(node, message)
            node.memory['parent'] = node.memory['neighbors'].pop()
            node.send(Message(destination=node.memory['parent'], header='Message', data=message.data))
            node.status = 'PROCESSING'
        else:
            node.status = 'ACTIVE'

    def available(self, node, message):
        nodeNeighbors = list(node.memory[self.neighborsKey])

        if message.header == NodeAlgorithm.INI:
            self.send_message(node, message, nodeNeighbors)
        elif message.header == 'Activate':
            nodeNeighbors.remove(message.source)
            self.send_message(node, message, nodeNeighbors)


    def active(self, node, message):

        if message.header == 'Message':
            self.process_message(node, message)
            node.memory['neighbors'].remove(message.source)

            if len(node.memory['neighbors']) == 1:
                self.prepare_message(node, message)
                node.memory['parent'] = node.memory['neighbors'].pop()
                node.send(Message(destination=node.memory['parent'], header='Message', data=message.data))
                node.status = 'PROCESSING'

    def processing(self, node, message):
        if message.header == 'Message':
            self.process_message(node, message)
            self.resolve(node, message)

    def initialize(self, node, message):
        raise NotImplementedError
    def prepare_message(self, node, message):
        m = ['Saturation']
    def process_message(self, node, message):
        raise NotImplementedError
    def resolve(self, node, message):
        node.status = 'SATURATED'

    def saturated(self, node, message):
    	pass

    STATUS = {
                'AVAILABLE': available,
                'ACTIVE': active,
                'PROCESSING': processing,
                'SATURATED': saturated
             }

class Center(Saturation):
    def processing(self, node, message):
        if message.header == 'Center':
            self.process_message(node, message)
            self.resolve(node, message)

    def initialize(self, node, message):
        node.memory['max_value'] = 0
        node.memory['max2_value'] = 0

    def prepare_message(self, node, message):
        node.memory['max_value'] = node.memory['max_value'] + 1
        message.data = node.memory['max_value']

    def process_message(self, node, message):
        if node.memory['max_value'] < message.data:
            node.memory['max2_value'] = node.memory['max_value']
            node.memory['max_value'] = message.data
            node.memory['max_neighbor'] = message.source
        else:
            if node.memory['max2_value'] < message.data:
                node.memory['max2_value'] = message.data

    def resolve(self, node, message):
        if node.memory['max_value'] - node.memory['max2_value'] == 1:
            if node.memory['max_neighbor'] is not node.memory['parent']:
                node.send(Message(destination=node.memory['max_neighbor'], header='Center', data=node.memory['max2_value'] + 1))
            node.status = 'CENTER'
            node.memory['center'] = True
        else:
            if node.memory['max_value'] - node.memory['max2_value'] > 1:
                node.send(Message(destination=node.memory['max_neighbor'], header='Center', data=node.memory['max2_value'] + 1))
            else:
                node.status = 'CENTER'
                node.memory['center'] = True

    def center(self, node, message):
        pass

    STATUS = {
        'AVAILABLE': Saturation.STATUS.get('AVAILABLE'),
        'ACTIVE': Saturation.STATUS.get('ACTIVE'),
        'PROCESSING': processing,
        'SATURATED': Saturation.STATUS.get('SATURATED'),
        'CENTER': center
    }
