import sys
import copy

outputFile = open('output.txt', 'w')


class Fact:
    def __init__(self, fact):
        self.predict_name = self.get_predict_name(fact)
        self.args = self.get_args(fact)

    def get_predict_name(self, fact):
        start = 0
        end = fact.index('(')
        return fact[start: end]

    def get_args(self, fact):
        start = fact.index('(')
        end = fact.index(')') 
        paras = fact[start+1: end]
        args  = self.initList(paras)

        return args

    def initList(self, paras):
        strs = paras.split(', ')
        list1 = list()
        for s in strs:
            list1.append(s)
        return list1

    def isAllConst(self):
        for arg in self.args:
            if arg[0].islower():
                return False
        return True

    def Args2String(self):
        sb = ''
        for var in self.args:
            sb = sb + var + ', '

        sb = sb[:len(sb)-2]

        return sb

    def toString(self):
        sb = ''
        sb = sb + self.predict_name + "("
        for arg in self.args:
            sb = sb+arg+', '
        sb = sb[:len(sb)-2]
        sb += ')'

        return sb

'''==================================================================='''

class Rule:
    def __init__(self, implication):
       parts = implication.split(' => ')
       self.rhs = Fact(parts[1])
       self.lhs = self.initLHS(parts[0])

    def initLHS(self, conditions):
        list1 = []
        facts = conditions.split(' && ')
        for fact in facts:
            list1.append(Fact(fact))
        
        return list1

    def getPredicate(self):
        return self.rhs.predict_name

    def rulesToString(self):
        sb = ''
        for fact in self.lhs:
            if len(sb) !=0:
                sb += ' && '
            sb += str(fact.toString())
        sb += ' => ' + self.rhs.toString()
  
        return sb

'''==============================================================='''
class KB(object):
    """build Knowledge Base"""
    def __init__(self):
        self.VARIABLE = 1
        self.CONSTANT = 2
        self.LIST = 4
        
        self.facts = []
        self.rules = []
        self.factMap = dict()
        self.ruleMap = dict()
        self.std_count = 0

    # add new rule to KB
    def update(self, line):
        if ('=>' in line):
            rule = Rule(line)
            self.rules.append(rule)
            predict_name = rule.getPredicate()
            if predict_name in self.ruleMap:
                self.ruleMap[predict_name].append(rule)
            else:
                self.ruleMap[predict_name] = []
                self.ruleMap[predict_name].append(rule)

        else:
            fact = Fact(line)
            self.facts.append(fact)
            predict_name = fact.predict_name
            if predict_name in self.factMap:
                self.factMap[predict_name].append(fact)
            else:
                self.factMap[predict_name] = []
                self.factMap[predict_name].append(fact)


    def FOL_BC_ASK(self, query):
        self.std_count = 0
        visited = set()
        theta = dict()
        generator = list()

        if '&&' in query:
            goals = query.split(' && ')
            for goal in goals:
                goal1 = Fact(goal) 
                generator = self.FOL_BC_OR(goal1, theta, visited)
                if(not generator):
                    return False
            return True
        else:
            goal = Fact(query)
            generator = self.FOL_BC_OR(goal, theta, visited)
            if(not generator):
                return False
            else:
                return True


        


    def FOL_BC_OR(self, goal, theta, visited):
        # test_variable loop detection
               
        temp_goal = self.transfer(goal)
        if temp_goal in visited:
            if not goal.isAllConst():
                print "variable loop"
            return None
        else:
            visited.add(temp_goal)

        find_answer = set()

        substitution = list()
        fetch_facts = list()
        fetch_rules = list()
        
        if(self.factMap.has_key(goal.predict_name)):
            fetch_facts = self.factMap[goal.predict_name]
        else:
            fetch_facts = list()
        if(self.ruleMap.has_key(goal.predict_name)):
            fetch_rules = self.ruleMap[goal.predict_name]
        else:
            fetch_rules = list()
        
        exist_fact = 0
        for fact in fetch_facts:
            if goal.args == fact.args:
                exist_fact = 1

        true_flag = 0
        if len(fetch_facts) != 0:
            print self.ask(goal, theta)
            for fact in fetch_facts:
                assert(fact.predict_name == goal.predict_name)
                unified = self.unify(fact.Args2String(), goal.Args2String(), theta)
                if(not not unified):
                    substitution.append(unified)
                    true_flag =1
                    true_fact = fact.toString()

            if true_flag == 1:
                print "True: " + true_fact
                outputFile.write("True: " + true_fact +'\n')
            else:
                print "False: " + goal.toString()
                outputFile.write("False: " + goal.toString()+'\n')


        if len(fetch_rules) != 0:
            for rule in fetch_rules: 
                if self.transfer(goal) in find_answer:
                    break
                # ask every time in rule
                print self.ask(goal,theta)
                assert(rule.getPredicate() == goal.predict_name)
                std = self.standardize(rule, goal, theta)
                unified = self.unify(std.rhs.Args2String(), goal.Args2String(), theta)
                visited1 = copy.deepcopy(visited)
                list1 = self.FOL_BC_AND(std.lhs, unified, visited1)
                if not list1:
                        continue
                else:
                    for theta_prime in list1:
                        substitution.append(theta_prime)
                    find_answer.add(goal.toString())
                    sb = ''
                    sb = sb + goal.predict_name + '('
                    for arg in goal.args:
                        if self.typeOfStructure(arg) == self.VARIABLE:
                            sb = sb + substitution[0][arg] + ', '
                        else:
                            sb = sb + arg + ', '
                    
                    sb = sb[:len(sb)-2]
                    sb += ')'
                    print "True: " + sb 
                    outputFile.write("True: " + sb +'\n')

        return substitution

    def FOL_BC_AND(self, goals, theta, visited):
        
        find_wrong = 0

        substitution = list()
        if theta == None:
            return None
        elif len(goals) == 0:
            substitution.append(theta)
            return substitution
        else:
            first = goals[0]
            rest = []
            if len(goals) > 1:
                for i in range(1,len(goals)):
                    rest.append(goals[i])

        visited_new = copy.deepcopy(visited)
        theta_primes = self.FOL_BC_OR(self.subst(theta, first), theta, visited_new)

        # one if False, return
        if(not theta_primes):
            return substitution
        for theta_prime in theta_primes:
            visited_new1 = copy.deepcopy(visited_new)
            theta_pps = self.FOL_BC_AND(rest, theta_prime, visited_new1)
            if(not theta_pps):
                continue
            else:
                for theta_pp in theta_pps:
                    substitution.append(theta_pp)


        return substitution

# replace the variables in fact with the substitution in theta
    def subst(self, theta, fact):
        sb = ''
        sb = sb + fact.predict_name + '('
        for arg in fact.args:
            if theta.has_key(arg):
                sb = sb + theta[arg] + ', '
            else:
                sb = sb + arg + ', '
        sb = sb[:len(sb)-2]
        sb += ')'
        
        return Fact(sb) 




# Replace all variables' names in the rule that has appeared in theta
    def standardize(self, rule, goal, theta):
        map1 = dict()
        goal_vars = set();
        for arg in goal.args:
            if(self.typeOfStructure(arg) == self.VARIABLE):
                goal_vars.add(arg)

         # record names needed to be replaced in origianl rule
        for fact in rule.lhs:
            for var in fact.args:
                if self.typeOfStructure(var) != self.VARIABLE:
                    continue
                if theta.has_key(var) or var in theta.values() or var in goal_vars :
                    if var not in map1:
                        map1[var] = var + str(self.std_count)
                        self.std_count += 1

        for var in rule.rhs.args:
            if self.typeOfStructure(var) != self.VARIABLE :
                continue
            if theta.has_key(var) or var in theta.values() or var in goal_vars :
                map1[var] = var + str(self.std_count)
                self.std_count += 1

        # build new rule by replacing variable names
        new_rule = ""
        for fact in rule.lhs:
            if len(new_rule) != 0 :
                new_rule += ' && '
            sb = ''
            sb = sb + fact.predict_name + '('
            for arg in fact.args:
                if map1.has_key(arg):
                    sb = sb + map1[arg] + ', '
                else:
                    sb = sb + arg + ', '

            sb = sb[:len(sb)-2]
            sb += ')'

            new_rule = new_rule + sb
            
            
            
        new_rule += ' => '
        sb = ''
        sb = sb + rule.rhs.predict_name + '('
        for arg in rule.rhs.args:
            if map1.has_key(arg):
                sb = sb + map1[arg] + ', '
            else:
                sb = sb + arg + ', '

        sb = sb[:len(sb)-2]
        sb += ')'
        new_rule += sb
        
        # print new_rule

        std_rule = Rule(new_rule)
            
        return std_rule


#   * The unification algorithm.
#   * @param x : a variable, constant, list, or compound expression
#   * @param y : a variable, constant, list, or compound expression
#   * @param theta : the substitution built up so far (optional, defaults to empty)
    # HashMap<String, String> unify(String x, String y, HashMap<String, String> theta)
    def unify(self, x, y, theta):
        if theta == None:
            return None
        
        newTheta = copy.deepcopy(theta)
        
        if x == y:
            # print "True:"+ x +' '+ y
            return newTheta
        # # change to avoid x:y
        # elif self.typeOfStructure(x) == self.VARIABLE and self.typeOfStructure(y) == self.VARIABLE:
        #     return newTheta

        elif self.typeOfStructure(x) == self.VARIABLE:
            return self.unify_VAR(x, y, newTheta)
        elif self.typeOfStructure(y) == self.VARIABLE:
            return self.unify_VAR(y, x, newTheta)
        elif self.typeOfStructure(x) == self.LIST and self.typeOfStructure(y) == self.LIST:
            return self.unify(self.getRest(x), self.getRest(y), self.unify(self.getFirst(x), self.getFirst(y), newTheta))
        else:
            return None


    def unify_VAR(self, var, x, theta):
        if theta.has_key(var):
            return self.unify(theta[var], x, theta)
        elif theta.has_key(x):
            return self.unify(var, theta[x], theta)
        else:
            theta[var] = x
            return theta

    def getFirst(self, str1):
        start = 0
        if ',' in str1:
            end = str1.index(',')
            return str1[start:end]
        else:
            str1

    def getRest(self, str1):
        
        start = str1.index(', ')
        return str1[start+2:]


    #check the type of str
    def typeOfStructure(self, str1):
        if ',' in str1:
            return self.LIST
        elif str1[0].isupper():
            return self.CONSTANT
        else:
            return self.VARIABLE
            
    def transfer(self, goal):
        sb = ''
        sb = sb + goal.predict_name + '('
        for arg in goal.args:
            if(self.typeOfStructure(arg) == self.VARIABLE):
                sb = sb + arg[0] + ', '
            else:
                sb = sb + arg + ', '
        sb = sb[:len(sb)-2]
        sb += ')'
        return sb

    def ask(self, goal, theta):
        replace_goal = ''
        replace_goal = replace_goal + goal.predict_name + '('
        for arg in goal.args:
            if arg.islower():
                if arg in theta:
                    replace_goal = replace_goal + theta[arg] + ', '
                else:
                    replace_goal = replace_goal + '_' + ', '
            else:
                replace_goal = replace_goal + arg + ', '
        replace_goal = replace_goal[:len(replace_goal)-2]
        replace_goal += ')'
        
        line = 'ASK: ' + replace_goal
        outputFile.write(line+'\n')
        return line

    def printKB(self):
        print "Facts:"
        for fact in self.facts:
            print fact.predict_name +'('+ fact.Args2String()+')'
        
        print "Rules:"
        for rule in self.rules:
            for fact in rule.lhs:
                print fact.predict_name + '(' + str(fact.args) + ')'

            fact2 = rule.rhs
            print ' => ' + fact2.predict_name + '(' + str(fact2.args) + ')'
            print

'''=================================================================='''
def main():
    kb = KB()

    f = open('sample05.txt', 'r')
    goal = f.readline().translate(None, "\n\r\t")
    num = int(f.readline().translate(None, "\n\r\t"))
    
    for i in range(num):
        line = f.readline().translate(None, "\n\r\t")
        kb.update(line)

        
    kb.printKB()

    res = kb.FOL_BC_ASK(goal)
    
    line = ''
    outputFile.write(str(res))
    print res    

if __name__ == '__main__':
    main()