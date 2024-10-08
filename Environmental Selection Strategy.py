import numpy as np
import pandas as pd
import scipy.io as scio
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import KNeighborsClassifier

def hamming_distance(s1, s2):
    if len(s1) != len(s2):
        raise ValueError("The two strings must have the same length")
    distance = 0
    for i in range(len(s1)):
        if s1[i] != s2[i]:
            distance += 1
    return distance

def load_and_prepare_data(file_path):
    data = scio.loadmat(file_path)
    X = pd.DataFrame(data['X']).values  
    y = pd.DataFrame(data['Y']).values.ravel()  
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)
    return X_scaled, y

def KNN_with_cross_validation(X_scaled, y, xi):
    boolean_array = np.array(xi).astype(bool)  
    X_selected = X_scaled[:, boolean_array]
    knn_classifier = KNeighborsClassifier(n_neighbors=5)
    scores = cross_val_score(knn_classifier, X_selected, y, cv=5)
    mean_accuracy = np.mean(scores)
    return mean_accuracy

def calculate_accuracy(xi):
    file_path = r'your filename.mat'
    X_scaled, y = load_and_prepare_data(file_path)
    mean_accuracy = KNN_with_cross_validation(X_scaled, y, xi)
    return mean_accuracy

def fast_non_dominated_sort(values1, values2):
    size = len(values1)  
    s = [[] for _ in range(size)]  
    n = [0 for _ in range(size)]  
    rank = [0 for _ in range(size)]  
    fronts = [[]]  

    for p in range(size): 
        s[p] = []  
        n[p] = 0
        for q in range(size):  
            if values1[p] <= values1[q] and values2[p] <= values2[q] \
                    and ((values1[q] == values1[p]) + (values2[p] == values2[q])) != 2:
                s[p].append(q)
            elif values1[q] <= values1[p] and values2[q] <= values2[p] \
                    and ((values1[q] == values1[p]) + (values2[p] == values2[q])) != 2:
                n[p] += 1
        if n[p] == 0:
            rank[p] = 0
            fronts[0].append(p)
    i = 0
    while fronts[i]:
        Q = []
        for p in fronts[i]:
            for q in s[p]:
                n[q] = n[q] - 1
                if n[q] == 0:
                    rank[q] = i + 1
                    if q not in Q:
                        Q.append(q)
        i = i + 1
        fronts.append(Q)

    del fronts[-1]
    return fronts

def dominates(individual1, individual2, objectives):
    better_in_one = False
    for obj in objectives:
        if obj(individual1) > obj(individual2): 
            return False
        elif obj(individual1) < obj(individual2):
            better_in_one = True
    return better_in_one

def objective1(xi):
    file_path = r'your filename.mat'
    X_scaled, y = load_and_prepare_data(file_path)
    mean_accuracy = KNN_with_cross_validation(X_scaled, y, xi)
    return 1-mean_accuracy

def objective2(xi):
    return np.sum(xi == 1)  

def init_PSO(pN, dim):
    X = np.zeros((pN, dim))  
    for i in range(pN): 
        for j in range(dim): 
            r = np.random.uniform(0,1)
            if r > 0.5:
                X[i][j] = 1
            else:
                X[i][j] = 0
    return X
    
def calculate_crowding_distance(solutions,ln):
    Cis_list = []
    solution_list = []
    for i in range(len(solutions)):
        total_distance_i = 0
        for j in range(len(solutions)-1):
            distance = hamming_distance(solutions[i], solutions[j + 1])
            total_distance_i = total_distance_i + distance
            Cis = total_distance_i / (len(solutions)-1)
            Cis_list.append(Cis)
    sorted_list = sorted(Cis_list, reverse=True)
    for n in range(ln):
        index = Cis_list.index(sorted_list[n])
        solution_list.append(solutions[index])
    return solution_list


def select_feature_subsets(W, Qe):
    for i in range(len(Qe)):
        TS = Qe[i]  
        population_list = TS
        values1 = []
        values2 = []
        for j in range(len(population_list)):
            values1.append(objective1(population_list[j]))
        values1 = objective1(population_list)
        values2 = objective2(population_list)
        fronts = fast_non_dominated_sort(values1, values2)
        front_min = fronts[0][0]
        solution = population_list[front_min]
        for j in range (W):
            for k in range(W[j]):
                if solution in W[j][k]:
                    rmin = j
        ln = len(TS) // len(Qe) 

        if len(TS) > ln:
            Wrmin = calculate_crowding_distance(TS)
            W[rmin].extend(Wrmin)
        else:
            W[rmin].extend(TS)
    return W,ln
def calculating_Cio(Wm):
    max = 0
    for i in Wm:
        if Wm[i]>max:
            max = Wm[i]
def calculating_Ci(W,N):
    Cio = 0
    k = len(W)
    for m in range(1, k + 1):
        total_solutions_before_m = sum(len(front) for front in W[:m - 1])
        total_solutions_after_m = sum(len(front) for front in W[:m + 1])
        Cio_list = []
        if total_solutions_before_m < N and total_solutions_after_m > N:
            t = []
            for front in W[:m - 1]:
                t.extend(front)
            t_flat = [item for sublist in W for item in sublist]
            objective1_list = []
            objective2_list = []
            for j in range(len(t_flat)):
                objective1_list.append(objective1(t_flat[j]))
                objective2_list.append(objective2(t_flat[j]))
            min_objective1 = min(objective1_list)
            min_objective2 = min(objective2_list)
            max_objective1 = max(objective1_list)
            max_objective2 = max(objective2_list)
            for i in range(len(W)):
                if i == 0 or i == (len(W) - 1):
                    Cio = 1
                    Cio_list.append(Cio)
                else:
                    Cio = objective1(t_flat[i + 1]) - objective1(t_flat[i - 1]) / 2 * (
                                max_objective1 - min_objective1) + objective2(t_flat[i - 1]) - objective2(
                        t_flat[i - 1]) / 2 * (max_objective2 - min_objective2)
                    Cio_list.append(Cio)

        Cis_list = []
        for i in range(len(W[m])):
            total_distance_i = 0
            for j in range(len(W[m]) - 1):
                distance = hamming_distance(W[m][i], W[m][j + 1])
                total_distance_i = total_distance_i + distance
                Cis = total_distance_i / (len(W[m]) - 1)
                Cis_list.append(Cis)
        average_cio = sum(Cio_list)/len(Cio_list)
        average_cis = sum(Cis_list)/len(Cis_list)
        Ci_list = []
        for x in range(len(W[m])):
            if Cio_list[x] > average_cio or Cis_list[x] > average_cis:
                Ci = max(Cio_list, Cis_list)
            else:
                Ci = min(Cio_list, Cis_list)
            Ci_list.append(Ci)
        Ci_list_descending = Ci_list.sort(reverse=True)
        Wm_descending = []
        for y in Ci_list_descending:
            index = Ci_list.index(y)
            Wm_descending.append(W[m][index])
        break
    return Wm_descending



data = scio.loadmat(r'your filename.mat')
dic1 = data['X']
dic2 = data['Y']
df1 = pd.DataFrame(dic1)  
df2 = pd.DataFrame(dic2)  
feats = df1  
labels = df2
dim = len(df1.columns)
MAX_FE = 250
N = 20
population = init_PSO(N, dim)
population_list = population.tolist()
objectives = [objective1, objective2]
def selected_NP_solutions(W,ln,N):
    NP_solutions = []
    Cis_list = []
    for i in range(len(W)):
        Cio = 0
        k = len(W)
        for m in range(1, k + 1):
            total_solutions_before_m = sum(len(front) for front in W[:m - 1])
            total_solutions_after_m = sum(len(front) for front in W[:m + 1])
            Cio_list = []
            if total_solutions_before_m < N and total_solutions_after_m > N:
                t = []
                for front in W[:m - 1]:
                    t.extend(front)
                t_flat = [item for sublist in W for item in sublist]
                objective1_list = []
                objective2_list = []
                for j in range(len(t_flat)):
                    objective1_list.append(objective1(t_flat[j]))
                    objective2_list.append(objective2(t_flat[j]))
                min_objective1 = min(objective1_list)
                min_objective2 = min(objective2_list)
                max_objective1 = max(objective1_list)
                max_objective2 = max(objective2_list)
                for i in range(len(W)):
                    if i == 0 or i == (len(W) - 1):
                        Cio = 1
                        Cio_list.append(Cio)
                    else:
                        Cio = objective1(t_flat[i + 1]) - objective1(t_flat[i - 1]) / 2 * (
                                max_objective1 - min_objective1) + objective2(t_flat[i - 1]) - objective2(
                            t_flat[i - 1]) / 2 * (max_objective2 - min_objective2)
                        Cio_list.append(Cio)
                m1 = m

            Cis_list = []
            for i in range(len(W[m])):
                total_distance_i = 0
                for j in range(len(W[m]) - 1):
                    distance = hamming_distance(W[m][i], W[m][j + 1])
                    total_distance_i = total_distance_i + distance
                    Cis = total_distance_i / (len(W[m]) - 1)
                    Cis_list.append(Cis)
            average_cio = sum(Cio_list) / len(Cio_list)
            average_cis = sum(Cis_list) / len(Cis_list)
            Ci_list = []
            for x in range(len(W[m])):
                if Cio_list[x] > average_cio or Cis_list[x] > average_cis:
                    Ci = max(Cio_list, Cis_list)
                else:
                    Ci = min(Cio_list, Cis_list)
                Ci_list.append(Ci)
            Ci_list_descending = Ci_list.sort(reverse=True)
            Wm_descending = []
            for y in Ci_list_descending:
                index = Ci_list.index(y)
                Wm_descending.append(W[m][index])
    selected_wzero = Wm_descending[:ln]
    for j in range(m1):
        nested_list = W[j]
        flattened_list = [item for sublist in nested_list for item in sublist]
        total_solutions_before_m = sum(len(front) for front in W[:j-1])
        total_solutions_after_m = sum(len(front) for front in W[:j + 1])
        total_solution_m = total_solutions_before_m+ln
        if total_solutions_before_m < N and total_solutions_after_m > N:
            NP_solutions.append(selected_wzero)
        else:
            for k in range(len(flattened_list)):
                NP_solutions.append(flattened_list[k])
    W_rest = W[m1:len(W)-1]
    flat_list = [item for sublist in W_rest for item in sublist]
    for i in range(len(N-total_solution_m)):
        NP_solutions.append(flat_list[i])
    return NP_solutions
def environmental_selection(PO, Qe, N):
    values1 = objective1
    fronts = fast_non_dominated_sort(PO, objectives)
    population_fronts = []
    for front in fronts:
        for i in range(len(front)):
            a = []
            index = i
            a.append((population_list[index]))
        population_fronts.append(a)
    W = population_fronts
    P = []
    W,ln =select_feature_subsets(W, Qe)
    Wm_descending = calculating_Ci(W,N)
    # select NP solutions to P from W1-Wk
    P = selected_NP_solutions(W,ln,N)
    return P
