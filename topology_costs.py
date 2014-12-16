class TopologyCosts():
    DEFAULT_COST = 1

    def __init__(self, *args, **kwargs):
        self.costs = {}

    def set_cost(self, source, destination, cost):
        self.costs['%s,%s' % (source, destination)] = cost

    def get_cost(self, source, destination):
        if '%s,%s' % (source, destination) in self.costs:
            return int(self.costs['%s,%s' % (source, destination)])
        elif '%s,%s' % (destination, source) in self.costs:
            return int(self.costs['%s,%s' % (destination, source)])
        else:
            return self.DEFAULT_COST