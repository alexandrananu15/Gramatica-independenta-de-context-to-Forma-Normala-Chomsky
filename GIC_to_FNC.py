'''

Pentru a scrie o Gramatica Independenta de Context (GIC) in Forma Normala Chomsky (FNC),
vom urmari cei 5 pasi bine cunoscuti.

Vom retine productiile sub forma unui dictionar, cheile fiind reprezentate de membrul stang al productiei,
iar valorle pentru fiecare de cheie de catre mebrul stang al fiecarei productii.

'''

# citirea si initializarea dictionarului pentru productii

def read_productions(productions):
    f = open("input")

    for line in f:
        mid = line.split("->")
        productions[mid[0].strip()] = [x.strip() for x in mid[1].split("|")]

    f.close()
    print('Start: ', productions)


'''

PASUL 1: eliminam productiile lambda

CAZUL CAND MEMBRUL STANG NU MAI ARE SI ALTE PRODUCTII IN AFARA DE LAMBDA:

1. eliminam productia
2. eliminam membrul drept al productiei cu probleme unde apare ca membru stang 
eg. T → $, A → aT devine A → a
eg. T → $, U → T devine U → $


CAZUL IN CARE MEMBRUL DREPT MAI ARE SI ALTE PRODUCTII IN AFARA DE LAMBDA:

1. eliminam productia
2. Pentru toate productiile in care N apare ca membru drept in compuneri de mai
mult de 2 simboluri adaugam si productia fara N
eg. L → AN devine L → AN | A

'''

def lambda_production_removal(productions):

    ok = 1
    while ok:

        ok = 0
        current = None                  # current este membrul stang al productiei care contine lambda
        for i in productions:
            if "$" in productions[i]:
                current = i
                ok = 1
                break

        if current:
            #cazul 1: daca membrul stang nu mai are si alte productii
            if len(productions[current]) == 1:

                del productions[current]            # eliminam productia

                for i in productions:
                    if current in productions[i]:
                        if len(productions[i]) == 1:
                            productions[i].remove(current)
                            productions[i].push("$")
                        else:
                            for j in productions[i]:
                                j = j.replace(current, "")

            #cazul 2: daca membrul stang mai are si alte productii
            else:

                productions[current].remove("$")    # eliminam productia

                for i in productions:
                    for j in productions[i]:
                        if current in j:
                            nr = j.count(current)
                            for k in range(nr):
                                aux = ""
                                eliminat = False
                                copy = j
                                for chr in copy:
                                    if not eliminat:
                                        if chr == current:
                                            eliminat = True
                                            copy.replace(current, "", 1)
                                        else:
                                            aux += chr
                                    else:
                                        aux += chr
                                productions[i].append(aux)
                                productions[i] = list(set(productions[i]))      #elimin duplicatele

    print('After step 1: ', productions)


'''
PASUL NR. 2: eliminim redenumirile

Inlocuim productiile de tipul:

V → W
W → membru drept W

cu

V -> membru drept W

'''

def renamed_production_removal(productions):

    # trivial: S -> S

    for i in productions:
        if i in productions[i]:
            productions[i].remove(i)

    # A -> B si B -> expresie, devine A -> expresie
    ok = 1

    while ok:

        ok = 0
        for i in productions:
            for j in productions[i]:
                if len(j) == 1 and j.istitle():
                    ok = 1
                    productions[i].remove(j)
                    productions[i].extend(productions[j])

            productions[i] = list(set(productions[i]))  # elimin duplicatele

    print('After step 2: ', productions)


'''
PASUL NR. 3: eliminam productiile inutile

Eliminam productiile neaccesibile din simbolul de start.
    S → ab
    A → bc
Aici il putem elimina pe A in siguranta, deoarece nu este accesibil din S

Eliminam si productiile care nu se termina, de tipul: A → aA, acestea neputand face
parte dintr-un cuvant.

'''


def dfs(chr, productions, viz):         # cautam nodurile accesibile din start cu un dfs

    viz.add(chr)
    for i in productions[chr]:
        for j in i:
            if j.istitle() and j not in viz:
                dfs(j, productions, viz)


def useless_production_removal(productions):

    viz = set()
    dfs("S", productions, viz)

    delete = set()
    for i in productions:
        if i not in viz:
            delete.add(i)

    for i in productions:
        to_del = True
        for production in productions[i]:
            if i not in production:
                to_del = False
                break
        if to_del:
            delete.add(i)

    for i in delete:
        del productions[i]

    for i in productions:
        for j in productions[i]:
            if j in delete:
                productions[i].replace(j, "")
        productions[i] = list(set(productions[i]))

    print('After step 3: ', productions)


'''
PASUL nr. 4: adaugarea de terminale noi pentru terminalele din productii

Pentru toti terminalii care apar in productii in compuneri de mai mult de un simbol, inlocuim
terminalul cu un neterminal nou, si adaugam o productie de la noul neterminal la terminal.

T → aU|ab

Inlocuim a cu Xa si b cu Xb.
T → XaU|XaXb
Xa → a
Xb → b

'''


def add_terminal_productions(chr, productions):

    terminal = []
    for i in productions:
        for j in productions[i]:
            l = False
            u = False
            aux = []
            if len(j) > 1:
                for k in j:
                    if k.islower():
                        l = True
                        aux.append(k)
                    else:
                        u = True
            if l and u:
                terminal.extend(aux)

    terminal = list(set(terminal))

    for ter in terminal:
        while chr in productions:                               # ma asigur ca nu exista deja caracterul in productii
            chr = chr(ord(chr) + 1)

        for i in productions:
            for j in range(len(productions[i])):
                if len(productions[i][j]) > 1:
                    productions[i][j] = productions[i][j].replace(ter, chr)

        productions[chr] = [ter]

    print('After step 4: ', productions)


'''
PASUL NR. 5: adaugam terminale noi pentru productiile de mai mult de doua terminale

1. Gasim o productie T → T0T1...Tn, cu n ≥ 2.
2. Inlocuim T1...Tn cu un nou neterminal T1,2,...,n.
3. Adaugam productia T1,2,...,n → T1...Tn
4. Repeta 1 pana nu mai sunt productii T → T0T1...Tn, cu n ≥ 2.

EXEMPLU:

T → ABC

Inlocuim BC cu X si adaugam productia X → BC.
T → AX
X → BC

'''


def add_non_terminal_productions(next_letter, productions):

    done = False

    while not done:

        done = True
        non_terminal = ''
        for key in productions:
            for production in productions[key]:
                if len(production) > 2:
                    done = False
                    non_terminal = production[1:]
                    break
            if not done:
                break

        if done:
            break

        while next_letter in productions:
            next_letter = chr(ord(next_letter) + 1)

        for key in productions:
            for i in range(len(productions[key])):
                if len(productions[key][i]) > 2:
                    productions[key][i] = productions[key][i].replace(non_terminal, next_letter)
        productions[next_letter] = [non_terminal]
    print('Final: ', productions)


def transform(productions):
    lambda_production_removal(productions)
    renamed_production_removal(productions)
    useless_production_removal(productions)
    letter = 'A'
    add_terminal_productions(letter, productions)
    add_non_terminal_productions(letter, productions)


productions = {}
read_productions(productions)

transform(productions)
