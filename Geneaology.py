'''
Program that calculates the relationship coefficient between two individuals in a family tree.
Author: Meghana Sathish
'''




from prettytable import PrettyTable as pt
import math
from collections import OrderedDict
import re
import unicodedata
import pandas as pd
import pygraphviz as PG


def list_of_individuals():
    '''
    This function is to create an empty list of zeroes
    :return: list
    '''
    temp = [0] * 7
    temp[5] = []
    return temp


def list_of_families():
    '''
    This function creates an empty list of zeroes
    :return: list
    '''
    temp = [0] * 6
    temp[5] = []
    return temp


def table_of_individuals(list_people):
    '''
    It prints the table of individuals in the family
    :param list_people: list that contains the details of individuals
    :return: None
    '''
    table = pt(['Individual_ID', 'Name', 'Sex', 'Birth Year', 'Spouse ID', 'Child ID'])
    for index in list_people:
        spouse = 'NA'
        child = 'NA'
        if (index[5] != []):
            spouse = index[5]
        if (index[6] != 0):
            child = index[6]
        table.add_row([index[0], index[1], index[2], index[3], spouse, child])
    print(table)


def table_of_families(list_family):
    '''
    It prints the details of the families involved in the family
    :param list_family: list that contains the details of families
    :return: None
    '''
    table = pt(['Family_ID', 'Husband ID', 'Wife ID', 'Children'])
    for idx in list_family:
        child = 'NA'
        if (idx[5] != []):
            child = idx[5]
        table.add_row([idx[0], idx[1], idx[2], child])
    print(table)


def get_Name(list_person, id):
    '''
    When ID of an individual is passed, this function returns the name of that individual
    :param list_person: list that contains the details of individuals
    :param id: Individual's ID whose name has to be retrieved
    :return: name of the individual
    '''
    return (i[1] for i in list_person if (i[0]==id))


def get_ID(list_person, name):
    '''
    When name of an individual is passed, this function returns the ID of that individual
    :param list_person: list that contains the details of individuals
    :param name: Individual's name whose name ID to be retrieved
    :return: ID of the individual
    '''
    return (i[0] for i in list_person if (i[1] == name))


def parse_file(file_name):
    '''
    Function to parse the GEDCOM file and store the required values in respective lists
    :param file_name: path to the GEDCOM file
    :return: list of individuals and list of families
    '''
    data = open(file_name, 'r')
    flag_individual, flag_family = 0, 0
    list_person, list_family = [], []
    person, family = list_of_individuals(), list_of_families()
    for line in data:
        record = line.split()
        if record != []:
            if record[0] == '0':
                if flag_individual == 1:
                    list_person.append(person)
                    person = list_of_individuals()
                    flag_individual = 0
                if flag_family == 1:
                    list_family.append(family)
                    family = list_of_families()
                    flag_family = 0
                '''If the line begins with note or head or trlr then ignore'''
                if record[1] in ['NOTE', 'HEAD', 'TRLR']:
                    pass
                else:
                    ''' If the line begins with INDI then it is the details of an individual '''
                    if record[2] == 'INDI':
                        flag_individual = 1
                        person[0] = (record[1])
                    ''' If the line begins with FAM then it is the details of a family '''
                    if record[2] == 'FAM':
                        flag_family = 1
                        family[0] = (record[1])
            if record[0] == '1':
                ''' Name of the individual '''
                if record[1] == 'NAME':
                    if len(record) >= 4:
                        ''' function to remove unwanted characters '''
                        fname = removeCharDigit(' '.join(record[2:-1]))
                        person[1] = fname + " " + removeCharDigit(record[-1])
                        person[1] = person[1].lower()
                    else:
                        ''' if the name is not given then treat it as unknown '''
                        if record[2] == '/?/':
                            person[1] = 'Unknown'
                            person[1] = person[1].lower()
                        else:
                            person[1] = removeCharDigit(record[2])
                            person[1] = person[1].lower()
                # gender of the individual
                if record[1] == 'SEX':
                    person[2] = record[2]
                # family ID of the spouse
                elif record[1] == 'FAMS':
                    person[5].append(record[2])
                # family ID of the children
                elif record[1] == 'FAMC':
                    person[6] = record[2]
                # birth, death, marriage and divorce information of the individuals
                elif (record[1] in ['BIRT', 'DEAT', 'MARR', 'DIV']):
                    date_id = record[1]
                # Husband ID in the family
                elif record[1] == 'HUSB':
                    family[1] = record[2]
                # Wife ID in the family
                elif record[1] == 'WIFE':
                    family[2] = record[2]
                # Child Id in the family
                elif record[1] == 'CHIL':
                    family[5].append(record[2])
            if (record[0] == '2'):
                if (record[1] == 'DATE'):
                    date = record[-1]
                    if (date_id == 'BIRT'):
                        person[3] = date
    return list_person, list_family


def removeAscendingChar(name):
    '''
    Function to remove all the special characters in the name
    :param name: name from which special characters has to be removed
    :return: names with just normal alphabets
    '''
    data = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('utf-8', 'ignore')
    return data


def removeCharDigit(text):
    '''
    Remove certain special characters and digits that could occur in the name
    :param text: input from which digits and characters have to removed
    :return: input clear of all the digits and symbols
    '''
    str = '1234567890();./:\'\"'
    for char in text:
        if char in str:
            text = text.replace(char, '')
    return text


class hierarchy_tree:
    '''
    Class to define family tree functions
    '''

    def __init__(self):
        '''
        Function to initialize the dictionaries and list
        '''
        self.family_list = dict()
        self.paths = []
        self.nodes_list = dict()

    def add(self, name):
        '''
        Function to add individuals to the dictionary
        :param name: name of the individual
        :return: None
        '''
        if name is None:
            raise TypeError
        # print(name not in self.family_list)
        if name not in self.family_list:
            self.family_list[name] = []
            self.nodes_list[name] = []
        else:
            print(str(name) + "is already present")

    def find_parent(self, name):
        '''
        Function to find the parents of the individual
        :param name: name of the person whose parents are to be found
        :return: list containing the parents ID's
        '''
        if name is None:
            print("name is none")
            return None
        temp = []
        for parent, child in self.nodes_list.items():
            for c in child:
                if c == name:
                    temp.append(parent)
        return temp

    def get_ancestor(self, name):
        '''
        Function to get grandparents of an individual
        :param name: name of the person whose grandparents are to be found
        :return: list of grandparents
        '''
        parent = self.findparent(name)
        return self.findparent(parent)

    def link(self, p1, p2):
        '''
        Function to add children as values where parent is the key in the dictionary
        :param p1: name of the first person
        :param p2: name of the second person
        :return: None
        '''
        if p1 == p2:
            # print("Same Person" + p1 + p2)
            return
        if p1 in self.family_list:
            if p2 not in self.family_list[p1]:
                self.family_list[p1].append(p2)
        else:
            self.family_list[p1] = [p2]

    def link_dup(self, p1, p2):
        '''
        Duplicate of a link function to store all the key values in another dictionary which is used for visualization.
        :param p1: name of first person
        :param p2: name of second person
        :return: None
        '''
        if p1 == p2:
            return
        if p1 in self.nodes_list:
            if p2 not in self.nodes_list[p1]:
                # print("all good")
                self.nodes_list[p1].append(p2)
        else:
            self.nodes_list[p1] = [p2]

    def print_all(self):
        '''
        Function to print the dictionary
        :return: None
        '''
        print(self.family_list)

    def find_path(self, person1, person2, path=[]):
        '''
        Function to find the paths existing from one person to another recursively
        :param person1: name of the first person
        :param person2: name of the second person
        :param path: empty list
        :return: list containing the paths if there are any
        '''
        temp = self.family_list
        path = path + [person1]
        ''' no path if it is the same person'''
        if person1 == person2:
            return [path]
        ''' if an individual is not present in the family dictionary then return empty list'''
        if person1 not in temp:
            return []
        paths = []
        ''' check if person1 has any links associated with him/her'''
        for value in temp[person1]:
            # if that link is not in the list of paths, then add it and recursively search again
            if value not in path:
                extended_paths = self.find_path(value, person2, path)
                # add each and every calculated paths to the main paths list
                for p in extended_paths:
                    paths.append(p)
        return paths

class member:
    '''
    Class to define and add the names of each individual
    '''

    def __init__(self, name):
        '''
        Initilize the name
        :param name: name of the individual
        '''
        self.name = name

    def get_name(self, name):
        '''
        Get the name of the individual
        :param name: name of the individual
        :return: None
        '''
        self.name = name

    def __hash__(self):
        '''
        Return hash value to compare dictionary keys
        :return: Hash value of the name
        '''
        return hash(self.name)

    def __eq__(self, other):
        '''
        Function to compare the names in the dictionary
        :param other: name to be equated
        :return: boolean
        '''
        return self.name == other.name

    def __str__(self):
        '''
        print the name
        :return: name
        '''
        return self.name

    __repr__ = __str__


def calculate_coefficient(lst_pow):
    '''
    Calculates the coefficient based on the distances of paths
    :param lst_pow: list of integers that represent the distances of paths
    :return: calculated coefficient
    '''
    sum = 0.0
    for num in lst_pow:
        sum += math.pow(0.5, num)
    return sum


def check_duplicates(list_person, name):
    '''
    Check if a name has duplicates. i.e, if other people have same name in the family
    :param list_person: list that contains the details of individuals
    :param name: name to be checked
    :return: list of birth years if duplicates is present
    '''
    dup = []
    for row in list_person:
        dup.append(row[1])
    count_number = dup.count(name)
    if count_number > 1:
        temp = []
        for i in range(len(dup)):
            if dup[i] == name:
                temp.append(i)
        # print(temp)
        date = []
        for i in range(len(temp)):
            date.append(list_person[temp[i]][3])
        print(date)
        print("There are many people in your family tree with the same name.")
        print("Choose their birth year from the given options.")
        year = str(raw_input("Enter the year"))
        idx = date.index(year)
        idx = temp[idx]
        return list_person[idx][0]
    else:
        idx = dup.index(name)
        return list_person[idx][0]


def check_if_spouse(name1, name2, list_family):
    '''
    Function to check if the individuals are spouses
    :param name1: name of the first person
    :param name2: name of the second person
    :param list_family: list of the families
    :return: boolean
    '''
    temp = []
    for i, lst in enumerate(list_family):
        for j, name in enumerate(lst):
            if name == name1:
                temp.append(i)
                temp.append(j)
    for i, lst in enumerate(list_family):
        for j, name in enumerate(lst):
            if name == name2:
                temp.append(i)
                temp.append(j)
    if len(temp) < 3:
        return False
    if temp[0] == temp[2]:
        if (temp[1] == 1 and temp[3] == 2) or (temp[1] == 2 and temp[3] == 1):
            return True
    return False


def parse(dic):
    '''
    Function to parse the dictionary
    :param dic: dictionary
    :return: key-value pair
    '''
    for k, v in dic.items():
        if isinstance(v, dict):
            for p in parse(v):
                yield [k] + p
        else:
            yield [k, v]


def filterPath(paths, family_tree):
    '''
    Function to the levels of the nodes and filter the wrong paths.
    :param paths: list of all the paths present
    :param family_tree: object of class hierarchy_tree
    :return: list of accurate paths
    '''
    filteredList = []
    for path in paths:
        currentParents = family_tree.find_parent(member(str(path[1])))
        towardsChild = path[0] in currentParents
        addFlag = True
        changedDirection = False
        for i in range(2, len(path)):
            currentParents = family_tree.find_parent(member(str(path[i])))
            if not changedDirection and path[i - 1] in currentParents and not towardsChild:
                towardsChild = True
                changedDirection = True
            elif not changedDirection and path[i - 1] not in currentParents and towardsChild:
                towardsChild = False
                changedDirection = True

            if changedDirection and path[i - 1] in currentParents and not towardsChild:
                addFlag = False
                break
            elif changedDirection and path[i - 1] not in currentParents and towardsChild:
                addFlag = False
                break
        if addFlag:
            filteredList.append(path)
    return filteredList


def main(file_name):
    '''
    Function that accepts user inputs and displays the output
    :param file_name: path of the GEDCOM file
    :return: None
    '''

    list_person, list_family = parse_file(file_name)
    list_person.sort()
    list_family.sort()

    table_of_individuals(list_person)
    table_of_families(list_family)

    """ Add people to the family tree"""
    family_tree = hierarchy_tree()

    for person in list_person:
        person_ID = person[0]
        family_tree.add(member(person_ID))

    """ Link Father and children """

    for individual in list_family:
        temp = individual[-1]
        for kid in temp:

            if individual[1] == 0:
                individual[1] = str(individual[1])

            if member(individual[1].rstrip()) != 0 and member(kid.rstrip()) != 0:
                family_tree.link(member(individual[1].rstrip()), member(kid.rstrip()))
                family_tree.link(member(kid.rstrip()), member(individual[1].rstrip()))

            if individual[2] == 0:
                individual[2] = str(individual[2])

            if member(individual[2].rstrip()) != 0 and member(kid.rstrip()) != 0:
                family_tree.link(member(individual[2].rstrip()), member(kid.rstrip()))
                family_tree.link(member(kid.rstrip()), member(individual[2].rstrip()))

    for individual in list_family:
        temp = individual[-1]
        for kid in temp:

            if individual[1] == 0:
                individual[1] = str(individual[1])

            if member(individual[1].rstrip()) != 0 and member(kid.rstrip()) != 0:
                family_tree.link_dup(member(individual[1].rstrip()), member(kid.rstrip()))

            if individual[2] == 0:
                individual[2] = str(individual[2])

            if member(individual[2].rstrip()) != 0 and member(kid.rstrip()) != 0:
                family_tree.link_dup(member(individual[2].rstrip()), member(kid.rstrip()))

    lst = list(parse(family_tree.nodes_list))

    fam_tree = PG.AGraph(directed=True, strict=True)

    names_list = []
    for row in list_person:
        names_list.append(row[1])

    ID_list = []
    for row in list_person:
        ID_list.append(row[0])

    for small in lst:
        for smallest in small[-1]:
            if str(small[0]) != '0' and str(smallest) != '0':
                fam_tree.add_edge(names_list[ID_list.index(str(small[0]))], names_list[ID_list.index(str(smallest))])

    fam_tree.write('tree_visualization.dot')
    #
    fam_tree.layout(prog='dot')
    #
    fam_tree.draw('tree_visualization.png')

    print("Number of members in the family is:" + str(len(family_tree.nodes_list)))
    # print(family_tree.family_list)

    name1 = str(raw_input("Input the name of the first person"))
    name1 = name1.lower()
    name1 = check_duplicates(list_person, name1)

    name2 = str(raw_input("Input the name of the second person"))
    name2 = name2.lower()
    name2 = check_duplicates(list_person, name2)

    bool_result = check_if_spouse(name1, name2, list_family)

    if bool_result == True:
        print("Relationship Coefficient is : 0")
    else:
        temp = family_tree.find_path(member(name1), member(name2))
        print(temp)
        temp = filterPath(temp, family_tree)
        # print(temp)
        lst = []
        for item in temp:
            lst.append(len(item) - 1)
        print("Relationship Coefficient is" + "\t" + str(calculate_coefficient(lst)))


main('path_to_gedcom_file')

