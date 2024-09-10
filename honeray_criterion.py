'''
honeray_criterion.py written by Benjamin Lee (lee02819@umn.edu)
This program implements the gesture theory understanding of
modulation in traditional Chinese music to evaluate whether
a user-inputted modulation satisfies Honeray's criterion
Latest edit was made on 2024-09-09
'''

# Define human-readable versions of scale degrees and letter notes as global variables
scale_degrees = ['1', '1#', '2', '2#', '3', '4', '4#', '5', '5#', '6', '6#', '7']
letters = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Define functions to get human-readable outputs from cyclic groups S and L
def scale_degree(s):
    if (s < 0 or s > 11):
        return -1
    return scale_degrees[s]
    
def letter(l):
    if (l < 0 or l > 11):
        return -1
    return letters[l]

# Check if a given scale degree is pentatonic
def w(s):
    if (s < 0 or s > 11):
        return False
    return (s in [0, 2, 4, 7, 9])

# Check if a given interval between two letter notes is possible using only pentatonic scale degrees
def i(l1, l2):
    if (l1 < 0 or l1 > 11 or l2 < 0 or l2 > 11): return False
    c = l2 - l1
    if c < 0: c += 12
    return (c in [0, 2, 3, 4, 5, 7, 9]) or (abs(12 - c) in [0, 2, 3, 4, 5, 7, 9])
    

# Check if a given scale degree belongs to the Qingyue, Yayue, or Yanyue heptatonic scales
def n(s):
    if (s < 0  or s > 11):
        return False
    return (s in [0, 2, 4, 5, 6, 7, 9, 10, 11])

# Define a key with some given letter as the tonic
def key(letter):
    # Error check for invalid letter note
    if (letter not in letters):
        return -1

    # Define gesture morphism k set to specific letter
    def k(s):
        if (s < 0 or s > 11):
            return -1
        return (s + letters.index(letter)) % 12

    # Define inverse of k
    def k_inv(s):
        if (s < 0 or s > 11):
            return -1
        return (s - letters.index(letter)) % 12

    # Return gesture morphism and its inverse
    return (k, k_inv)

# Define a tranposition by some specific amount of half-steps
def transpose(c):
    # Define gesture morphism p for a specific transpose amount
    def p(l):
        return (l + c) % 12

    # Return gesture morphism p
    return p

# Define a modulation using k, its inverse, and p
def modulation(k, p, k_inv):
    # Define specific modulation using given gesture morphisms
    def m(s):
        if (s < 0 or s > 11):
            return -1
        return k_inv(p(k(s)))
    
    # Return the specific gesture morphism m
    return m    

# Find whether a modulation obeys Honeray's criterion given the old key, new key, and the two notes surrounding the modulation
def obeys_honerays_crit(start_key, end_key, start_letter, end_letter):
    # Convert starting letter note to scale degree
    s = letters.index(start_letter) - letters.index(start_key)
    if s < 0:
        s += 12

    # Get gesture morphisms
    (kx1, kx1_inv) = key(start_key)
    (kx2, kx2_inv) = key(end_key)
    c = letters.index(end_letter) - letters.index(start_letter)
    if c < 0:
        c += 12
    p = transpose(c)

    # Get modulation
    m = modulation(kx1, p, kx2_inv)

    # Define sections of Honeray's criterion
    isOrigin = w(kx2_inv(kx1(0))) or w(kx1_inv(kx2(0)))
    isInterval = i(kx1(s), kx2(m(s)))
    isNatural = n(s) and n(m(s))
    isCommon = w(s) and w(m(s)) and (s==m(s) or kx1(s)==p(kx1(s)))
    isTransition = (w(kx1_inv(p(kx1(s)))) and w(s)) or (w(kx2_inv(kx1(s))) and w(m(s)))

    # Apply Honeray's criterion and return final boolean conclusion
    result = isOrigin and isInterval and isNatural and (isCommon or isTransition)
    details = [isOrigin, isInterval, isNatural, isCommon, isTransition]
    return result, details

# Function for finding statistical values
def find_stats():
    # Initialize variables for results
    results = []                                            # length of this should eventually be 12*11*12*12 = 19008
    start_key_freqs = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # will store how many times some starting key satisfies Honeray's criterion
    end_key_freqs = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]    # will store how many times some ending key satisfies Honeray's criterion
    violation_freqs = [0, 0, 0, 0, 0]                       # will store how many times a specific part of Honeray's criterion is violated

    # For every old key,
    for start_key in letters:
        # Create a list of all possible new keys (exclude the old key itself)
        end_keys = letters.copy()
        end_keys.remove(start_key)
        
        # Create a temporary list to store how many times some ending key satisfies Honeray's criterion for this specific starting key
        end_key_freqs_temp = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        # For each possible new key,
        for end_key in end_keys:            
            # For each possible note for the last note of the old key,
            for note_1 in letters:
                # For each possible note for the first note of the new key,
                for note_2 in letters:
                    # Apply Honeray's Criterion
                    result, details = obeys_honerays_crit(start_key, end_key, note_1, note_2)
                    results.append(result)

                    # Increment frequency counts if criterion is satisfied
                    if result:
                        start_key_freqs[letters.index(start_key)] += 1
                        end_key_freqs_temp[letters.index(end_key)] += 1
                    else:
                        for i in range(len(violation_freqs)):
                            if not details[i]:
                                violation_freqs[i] += 1
        
        # Store temporary list in main list of new key frequencies
        end_key_freqs = [end_key_freqs[i] + end_key_freqs_temp[i] for i in range(len(end_key_freqs))]
            
        # Printing frequency distributions of ending keys for current starting key that satisfy Honeray's criterion
        print('Number of valid modulations from ' + start_key + ': ' + str(start_key_freqs[letters.index(start_key)]))
        print('Ending key distribution: ',end='')
        for letter in letters:
            print(letter.ljust(3),end=' ')
        print('\n                         ',end='')
        for end_key_freq_temp in end_key_freqs_temp:
            print(str(end_key_freq_temp).ljust(3),end=' ')
        print('\n------------')


    # Check that all possible modulations have been checked
    assert len(results) == 19008

    # Calculate probability of a modulation being valid under Honeray's criterion
    positives = len([1 for result in results if result])
    rand_prob = positives / len(results)

    return rand_prob, start_key_freqs, end_key_freqs, violation_freqs



# Main algorithm
if __name__ == "__main__":
    # Get user inputs
    start_key = ' '
    while not (start_key in letters):
        start_key = input("Enter the starting key (e.g. C#): ")
    start_letter = ' '
    while not (start_letter in letters):
        start_letter = input("Enter the starting note: ")
    end_key = ' '
    while not (end_key in letters):
        end_key = input("Enter the ending key: ")
    end_letter = ' '
    while not (end_letter in letters):
        end_letter = input("Enter the ending note: ")

    # Apply Honeray's Criterion
    result, details = obeys_honerays_crit(start_key, end_key, start_letter, end_letter)

    # Printing results for user inputted modulation
    print('----------')
    print('INPUTS')
    print('Old key = ' + str(start_key))
    print('Old key letter note = ' + str(start_letter))
    print('New key = ' + str(end_key))
    print('New key letter note = ' + str(end_letter))
    print('----------')
    print('RESULTS')
    print('Origin Pentatonicity: ' + str(details[0]))
    print('Interval Pentatonicity: ' + str(details[1]))
    print('Naturality: ' + str(details[2]))
    print('Pentatonic Commonality: ' + str(details[3]))
    print('Transition Pentatonicity: ' + str(details[4]))
    print('----------')
    print('CONCLUSION: ' + str(result))
    
    # Printing results for statistical analyses
    print('----------')
    print('FINDING STATISTICS')
    prob, start_key_freqs, end_key_freqs, violation_freqs = find_stats()
    print("Honeray's criterion violation frequencies: ")
    print('!Origin'.ljust(10) + '!Interval'.ljust(10) + '!Natural'.ljust(10) + '!Common'.ljust(10) + '!Transition'.ljust(10))
    print(str(violation_freqs[0]).ljust(10) + str(violation_freqs[1]).ljust(10) + str(violation_freqs[2]).ljust(10) + str(violation_freqs[3]).ljust(10) + str(violation_freqs[4]).ljust(10))
    print('----------')
    print("Probability of a random modulation obeying Honeray's Criterion: " + str(prob))