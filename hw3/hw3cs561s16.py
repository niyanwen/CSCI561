import sys
import math
from decimal import Decimal

outputFile = open('output.txt', 'w')

class BayesNet:
    def __init__(self, node_specs=[]):
        self.nodes = []
        self.variables = []
        for node_spec in node_specs:
            self.add(node_spec)

    def add(self, node_spec):
        """Add a node to the net. Its parents must already be in the
        net, and its variable must not."""
        node = BayesNode(*node_spec)
        assert node.variable not in self.variables
        self.nodes.append(node)
        self.variables.append(node.variable)
        for parent in node.parents:
            self.variable_node(parent).children.append(node)

    def variable_node(self, var):
        for n in self.nodes:
            if n.variable == var:
                return n
        raise Exception("No such variable: %s" % var)

    def variable_values(self, var):
        return [True, False]

    def __repr__(self):
        return 'BayesNet(%r)' % self.nodes


class BayesNode:
    """A conditional probability distribution for a boolean variable,
    P(X | parents). Part of a BayesNet."""

    def __init__(self, x, parents, cpt):
        
        if isinstance(parents, str):
            parents = parents.split()

        # We store the table always in the third form above.
        if isinstance(cpt, (float, int)):  # no parents, 0-tuple
            cpt = {(): cpt}
        elif isinstance(cpt, dict):
            # one parent, 1-tuple
            if cpt and isinstance(list(cpt.keys())[0], bool):
                cpt = dict(((v,), p) for v, p in list(cpt.items()))

        assert isinstance(cpt, dict)
        for vs, p in list(cpt.items()):
            # assert isinstance(vs, tuple) and len(vs) == len(parents)
            # assert every(lambda v: isinstance(v, bool), vs)
            assert 0 <= p <= 1

        self.variable = x
        self.parents = parents
        self.cpt = cpt
        self.children = []
    def p(self, value, event):
        assert isinstance(value, bool)
        ptrue = self.cpt[event_values(event, self.parents)]
        return (ptrue if value else 1 - ptrue)

    def __repr__(self):
        return repr((self.variable, ' '.join(self.parents)))

class UtilityNode :
    def __init__(self, x, ut):

        if isinstance(ut, int):  #  0-tuple
            ut = {(): cpt}

        assert isinstance(ut, dict)

        self.variable = x
        self.ut = ut
    
    def utility_function(self, x):
        pass

"Global paramater"
decision_node = []
utility_node = ''
bn = BayesNet()

def processInput():
    f = open(sys.argv[-1], 'r')

    global utility_node
    global decision_node
    global bn

    utility_nodes = []
    query = []
    add_utility = 0
    finish_add_query = 0
    add_node = 1
    

    while 1:
        line = f.readline().translate(None, "\n\r\t")
        if line != '******' and finish_add_query == 0:
            query.append(line)
            continue

        if line == '******' and finish_add_query == 0:
            finish_add_query = 1

        if (finish_add_query == 1 and add_utility == 0):
            if '***' not in line:
                if '|' not in line:  # no parent node
                    node = line
                    p = f.readline().translate(None, "\n\r\t")
                    if p == 'decision':
                        decision_node.append(node)
                        prob = 0.0000000000001
                    else:
                        prob = float(p)
                    # print node, prob , "!!!"
                    bn.add((node, '', prob))
                else:  # parent node
                    cpt = dict()
                    match = line.split(' | ')
                    node = match[0]
                    parents = match[1]
                    line = f.readline().translate(None, "\n\r\t")
                    every_parents = parents.split()

                    for i in range(int(math.pow(2, len(every_parents)))):
                        match = line.split()
                        if len(match) == 2:
                            if match[1] == '+':
                                match[1] = True
                            else:
                                match[1] = False
                            cpt[match[1]] = float(match[0])
                        if len(match) == 3:
                            if match[1] == '+':
                                match[1] = True
                            else:
                                match[1] = False
                            if match[2] == '+':
                                match[2] = True
                            else:
                                match[2] = False
                            cpt[(match[1], match[2])] = float(match[0])
                        if len(match) == 4:
                            if match[1] == '+':
                                match[1] = True
                            else:
                                match[1] = False
                            if match[2] == '+':
                                match[2] = True
                            else:
                                match[2] = False
                            if match[3] == '+':
                                match[3] = True
                            else:
                                match[3] = False
                            cpt[(match[1], match[2], match[3])] = float(match[0])
                        line = f.readline().translate(None, "\n\r\t")

                    if not line:
                        # print cpt
                        bn.add((node, parents, cpt))
                    if line == '***' or line == '******':
                        print node, parents, cpt
                        bn.add((node, parents, cpt))
                    # print cpt
                    if line == '******':
                        add_utility = 1


        if (add_utility == 1):
            if '|' in line:
            	line = line.rstrip()
                group = line.split(' | ')
                small_group = group[1].split()
                if len(small_group) == 1:
                    utility_node = group[1]
                else:
                    for i in range(len(small_group)):
                        utility_node += small_group[i] +', '
                    utility_node = utility_node[:-2]
                ut = dict()
                for i in range(int(math.pow(2, len(small_group)))):
                    line = f.readline().translate(None, "\n\r\t")
                    match = line.split()
                    if len(match) == 2 :
                        symbol = processTF(match[1])
                        value = int(match[0])
                        ut[symbol] = value
                    if len(match) == 3 :
                        ut[processTF(match[1]),processTF(match[2])] = int(match[0])
                    if len(match) == 4 :
                        ut[processTF(match[1]),processTF(match[2]),processTF(match[3])] = int(match[0])
            	
                utility_node = UtilityNode(utility_node, ut)
        
        if not line:
                break

    print query
    print bn.nodes
    # print utility_node.variable, utility_node.ut
    for i in query:
        querySelection(i)
    # process_P_Query('P(Infiltration = - | Infiltration = +, LeakIdea = +)')
    # querySelection(query[2])
    # process_P_Query('P(Demoralize = +, Infiltration = + | Infiltration = -, LeakIdea = +)')
    # process_MEU_Query('MEU(Infiltration)')

def querySelection(query):
    if query[0] == 'P':
        a = process_P_Query(query)
        b = Decimal(str(a)).quantize(Decimal('.01'))
        # print type(a)
        outputFile.write( str(b) + '\n')
    if query[0] == 'E' :
    	a = process_EU_Query(query)
        b = Decimal(str(a)).quantize(Decimal('0.'))
        outputFile.write(str(b) + '\n')
    if query[0] == 'M' :
    	a = process_MEU_Query(query)
        c = 0
        # print a
        # if len(a[0]) >= 2 :
        #     for i in range(len(a)):
        #         if i == range(len(a)-1):
        #             print "!*&^*%"
        #             c = Decimal(str(a[i])).quantize(Decimal('0.'))
        #         else:
        #             b += str(a[i]) + ' '
        #     outputFile.write(b + str(c) + '\n')
        # else:
        #     c = Decimal(str(a[1])).quantize(Decimal('0.'))
        #     outputFile.write(a[0] + str(c) + '\n')

        c = Decimal(str(a[1])).quantize(Decimal('0.'))
        outputFile.write(a[0] + ' '+ str(c) + '\n')


def process_P_Query(query):
    for i in range(len(query)):
        if query[i] == '(':
            l = i
        if query[i] == ')':
            r = i
    content = query[l + 1:r]
    mutiplier = 1.00
    if '|' not in content:
        if ',' in content:
            groups = content.split(', ')
            d = dict()
            for group in groups:
                if '=' in group:
                    small_group = group.split(' = ')
                    x = small_group[0]
                    y = small_group[1]
                    TorF = processTF(y)
                    d[x] = TorF
                    # print x, d 
                    a = enumeration_ask(x, d, bn)
                    # print a.show_approx()
                    mutiplier *= a[TorF]
        else:
            if '=' in content:
                small_group = content.split(' = ')
                x = small_group[0]
                y = small_group[1]
                TorF = processTF(y)
                a = enumeration_ask(x, dict(), bn)
                mutiplier *= a[TorF]

        print mutiplier
        return  mutiplier
        # return Decimal(str(mutiplier)).quantize(Decimal('.01'))
    # has parents |
    else: 
        groups = content.split(' | ')
        children = groups[0]
        # print children   
        parents = groups[1]
        d = dict()
        if ',' in parents:
            parent_groups = parents.split(', ')
            for i in range(len(parent_groups)):
                if '=' in parent_groups[i]:
                    small_group = parent_groups[i].split(' = ')
                    x = small_group[0]
                    y = small_group[1]
                    parents_TorF = processTF(y)
                    d[x] = parents_TorF
                    # print d 
        else:
            if '=' in parents:
                small_group = parents.split(' = ')
                x = small_group[0]
                y = small_group[1]
                parents_TorF = processTF(y)
                d[x] = parents_TorF
        if ',' in children :
            child_group = children.split(', ')
            for i in range(len(child_group)):
                child = child_group[i]
                if '=' in child:
                    small_group = child.split(' = ')
                    child = small_group[0].rstrip()
                    print child
                    y = small_group[1]
                    children_TorF = processTF(y)
                    if child in decision_node:
                        print d,children_TorF
                        if d[child] != children_TorF :
                            mutiplier = 0 
                        else:
                            pass
                    else:      
                        a = enumeration_ask(child, d, bn)
                        mutiplier *= a[children_TorF]
        else:
            if '=' in children:
                small_group = children.split(' = ')
                child = small_group[0].rstrip()
                y = small_group[1]
                children_TorF = processTF(y) 
                if child in decision_node:
                    # print d,children_TorF
                    if d[child] != children_TorF :
                        mutiplier = 0
                    else:
                        pass
                else:
                    a = enumeration_ask(child, d, bn)
                    mutiplier *= a[children_TorF]
        
        print mutiplier
        return  mutiplier
        # return Decimal(str(mutiplier)).quantize(Decimal('.01'))
        

def process_EU_Query(query):
    'EU(Infiltration = + | LeakIdea = +)'
    # new_query = ''
    # for i in range(len(query)):
    #     if query[i] == '(':
    #         l = i
    #     if query[i] == ')':
    #         r = i
    # content = query[l + 1:r]
    # print utility_node
    # if '|' in content:
    #     q = content.replace(' |', ',')
    # new_query = 'P(' + utility_node + ' = +' + ' | ' + q + ')'
    # print new_query
    # process_P_Query(new_query)
    new_query = ""
    for i in range(len(query)):
        if query[i] == '(':
            l = i
        if query[i] == ')':
            r = i
    content = query[l + 1:r]
    if '|' in content:
        content = content.replace(' |', ',')
    

    # formula expression
    print utility_node.variable, utility_node.ut, len(utility_node.ut)
    # print utility_node.ut[(True,True)]
    joint_sum = 0
    print content
    if len(utility_node.ut) == 2 :
        symbol = ('+','-')
        for i in range(len(symbol)):
            new_query += 'P('
            new_query += utility_node.variable + ' = '+ symbol[i]+' | '
            new_query += content + ')'
            p = float(process_P_Query(new_query))
            print p
            u = utility_node.ut[processTF(symbol[i])]
            print u
            joint_sum += p*u
        print joint_sum
        return joint_sum
        # print Decimal(str(joint_sum)).quantize(Decimal('0.'))
        # return Decimal(str(joint_sum)).quantize(Decimal('0.'))

    if len(utility_node.ut) == 4 :
        symbol = []
        symbol.append(('+', '-'))
        symbol.append(('+', '-'))
        if ',' in utility_node.variable:
            nodes = utility_node.variable.split(',')
        for i in range(len(symbol)):
            for j in range(len(symbol[i])):
                new_query = ''
                new_query += 'P('
                new_query += nodes[0] + ' = ' + symbol[i][i] + ',' + nodes[1] + ' = ' + symbol[i][j] + ' | '
                new_query += content + ')'
            
                print new_query 
                p = process_P_Query(new_query)
                # print p
                # print utility_node.ut
                u = utility_node.ut[(processTF(symbol[i][i]),processTF(symbol[i][j]))]
                # print u
                joint_sum += float(p) * u

        print joint_sum
        return joint_sum
        # print Decimal(str(joint_sum)).quantize(Decimal('0.'))
        # return Decimal(str(joint_sum)).quantize(Decimal('0.'))

def process_MEU_Query(query):
    "MEU(Infiltration), MEU(Infiltration | LeakIdea = +),      MEU(Infiltration, LeakIdea)"
    for i in range(len(query)):
        if query[i] == '(':
            l = i
        if query[i] == ')':
            r = i
    content = query[l + 1:r] 
    if '|' not in content : 
        # only decision node
        max1 = -9999999.0
        if ',' not in content:
            # only one decision node
            symbol = ('+', '-')
            for i in range(len(symbol)):
                content = content + ' = ' + symbol[i] 
                content = 'EU(' + content +')'
                total = process_EU_Query(content)
                content = query[l+1:r]
                if total > max1:
                    max1 = total
                    symbol1 = symbol[i]
            print symbol1, max1 , "!!"
            return symbol1, max1
        else:
            group = content.split(', ')
            if len(group) == 2:
                symbol = ('+', '-')
                for i in range(len(symbol)):
                    for j in range(len(symbol)):
                        content = group[0] + ' = ' + symbol[i] + ', ' + group[1] + ' = ' + symbol[j]
                        content = 'EU(' + content +')'
                        total = process_EU_Query(content)
                        print content
                        print total , "!!!!!!!!!"
                        if total > max1:
                            max1 = total
                            symbol3 = symbol[i] + ' ' + symbol[j]
                print symbol3, max1
                return symbol3, max1
            if len(group) == 3:
                symbol = ('+', '-')
                for i in range(len(symbol)):
                    for j in range(len(symbol)):
                        for k in range(len(symbol)):
                            content = group[0] + ' = ' + symbol[i] + ', ' + group[1] + ' = ' + symbol[j] + group[2] + ' = ' + symbol[k]
                            content = 'EU(' + content +')'
                            total = process_EU_Query(content)
                            print content
                            print total , "!!!!!!!!!"
                            if total > max1:
                                max1 = total
                                symbol3 = symbol[i] + ' ' + symbol[j] + ' ' + symbol[k]
                print symbol3, max1
                return symbol3, max1

    else:
        group = content.split(' | ')
        children = group[0]
        parents = group[1]
        max1 = -9999999
        
        if ',' not in children:
            # only one decision node
            symbol = ('+', '-')
            for i in range(len(symbol)):
                children = children + ' = ' + symbol[i] 
                children = 'EU(' + children + ' | ' + parents +')'
                total = process_EU_Query(children)
                # print children + "!!"
                children = group[0]
                if total > max1:
                    max1 = total
                    symbol1 = symbol[i]
            print symbol1, max1
            return symbol1, max1
        else:
            group = children.split(', ')
            if len(group) == 2:
                symbol = ('+', '-')
                for i in range(len(symbol)):
                    for j in range(len(symbol)):
                        content = group[0] + ' = ' + symbol[i] + ', ' + group[1] + ' = ' + symbol[j]
                        content = 'EU(' + content + '|' + parents + ')'
                        total = process_EU_Query(content)
                        print content
                        print total , "!!!!!!!!!"
                        if total > max1:
                            max1 = total
                            symbol3 = symbol[i] + ' ' + symbol[j]
                print symbol3, max1
                return symbol3, max1
            if len(group) == 3:
                symbol = ('+', '-')
                for i in range(len(symbol)):
                    for j in range(len(symbol)):
                        for k in range(len(symbol)):
                            content = group[0] + ' = ' + symbol[i] + ', ' + group[1] + ' = ' + symbol[j] + group[2] + ' = ' + symbol[k]
                            content = 'EU(' + content + '|' +parents +')'
                            total = process_EU_Query(content)
                            print content
                            print total , "!!!!!!!!!"
                            if total > max1:
                                max1 = total
                                symbol3 = symbol[i] + ' ' + symbol[j] + ' ' + symbol[k]
                print symbol3, max1
                return symbol3, max1




def processTF(symbol):
    if symbol == "+":
        return True
    else:
        return False

def event_values(event, variables):
    if isinstance(event, tuple) and len(event) == len(variables):
        return event
    else:
        return tuple([event[var] for var in variables])


def enumeration_ask(X, e, bn):
    # assert X not in e
    Q = ProbDist(X)
    for xi in bn.variable_values(X):
        Q[xi] = enumerate_all(bn.variables, extend(e, X, xi), bn)
    return Q.normalize()


def enumerate_all(variables, e, bn):
    if not variables:
        return 1.0
    Y, rest = variables[0], variables[1:]
    Ynode = bn.variable_node(Y)
    if Y in e:
        return Ynode.p(e[Y], e) * enumerate_all(rest, e, bn)
    else:
        return sum(Ynode.p(y, e) * enumerate_all(rest, extend(e, Y, y), bn) for y in bn.variable_values(Y))


class ProbDist:
    def __init__(self, varname='?', freqs=None):
        """If freqs is given, it is a dictionary of value: frequency pairs,
        and the ProbDist then is normalized."""
        self.prob = {}
        self.varname = varname
        self.values = []
        if freqs:
            for (v, p) in list(freqs.items()):
                self[v] = p
            self.normalize()

    def __getitem__(self, val):
        "Given a value, return P(value)."
        try:
            return self.prob[val]
        except KeyError:
            return 0

    def __setitem__(self, val, p):
        "Set P(val) = p."
        if val not in self.values:
            self.values.append(val)
        self.prob[val] = p

    def normalize(self):
        """Make sure the probabilities of all values sum to 1.
        Returns the normalized distribution.
        Raises a ZeroDivisionError if the sum of the values is 0."""
        total = sum(self.prob.values())
        if not isclose(total, 1.0):
            for val in self.prob:
                self.prob[val] /= total
        return self

    def show_approx(self, numfmt='%.3g'):
        """Show the probabilities rounded and sorted by key, for the
        sake of portable doctests."""
        return ', '.join([('%s: ' + numfmt) % (v, p)
                          for (v, p) in sorted(self.prob.items())])


def extend(s, var, val):
    "Copy the substitution s and extend it by setting var to val; return copy."
    s2 = s.copy()
    s2[var] = val
    return s2


def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    "Return true if numbers a and b are close to each other."
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


def main():
    processInput()


if __name__ == '__main__':
    main()
