from django.db import models
from django.core.exceptions import ObjectDoesNotExist

import math
import copy
import json


class AllWords(models.Model):
    word = models.CharField(max_length=5, default=1)
    class Meta:
        db_table = "All_Words_Options"
    
    def __str__(self):
        return f"{self.word}"


class FinalWords(models.Model):
    word = models.CharField(max_length=5, default=1)
    class Meta:
        db_table = "Final_Words_Options"
    
    def __str__(self):
        return f"{self.word}"

all_words = list(AllWords.objects.values_list('word', flat=True))
# Change top to below when doing migrations
# all_words = []
# with open("wordle/allowed_guesses.txt") as h:
#     for line in h:
#         all_words.append(line.strip())

# all_words are words that can be used as guesses
# hidden_words are words that could be final words

hidden_words = list(FinalWords.objects.values_list('word', flat=True))
# Change top to below when doing migrations
# hidden_words = []
# with open("wordle/hidden_words.txt") as h:
#     for line in h:
#         hidden_words.append(line.strip())

# dictionary where each word in all_words is either 0 (not final word / not in hidden words) or 1 (can be a final word / in hidden words) 
is_final = {}
for word in all_words:
    if word in hidden_words:
        is_final[word] = 1
    else:
        is_final[word] = 0


def makeJSon_word(word):
    # {word:"", exp_entropy:_, num_rem_words:_, patterns: { pattern: freq %}}
    json = {}
    json["word"] = word.word_text
    entropy_and_freq = find_entropy_and_freq(word.word_text, word.rem_words_final)
    json["exp_entropy"] = round(entropy_and_freq[0], 2)
    json["num_rem_words"] = len(word.rem_words_final)
    json["patterns"] = dict(sorted(entropy_and_freq[1].items(), key=lambda x:x[1], reverse=True))
    return json


def makeJSon_pattern(word, pattern, word_num):
    json = {}
    rem_words_final = find_rem_words_final(word.find_rem_words(word.word_text, pattern.pattern_text))    
    num_words = len(rem_words_final)
    entropy_and_freq = find_entropy_and_freq(word.word_text, word.rem_words_final)
    json["pattern"] = pattern.pattern_text
    json["exp_entropy"] = round(entropy_and_freq[0], 2)
    json["actual_entropy"] = find_actual_entropy(word.word_text, pattern.pattern_text, word.rem_words_final)
    json["rem_uncertainty"] = round(math.log2(num_words),2)
    json["best_guess"] = find_best_guess_exp_score(rem_words_final, word_num + 1)
    json["num_rem_words"] = num_words

    json["rem_words"] = rem_words_final
    
    return json



def find_entropy(guess, rem_words):
    freq = {}
    num_words = len(rem_words)
    for word in rem_words:
        pattern = find_pattern(guess, word)
        if pattern in freq:
            freq[pattern] += 1/num_words
        else:
            freq[pattern] = 1/num_words

    entropy = 0
    for pattern in freq:
        p = freq[pattern]
        entropy += p * math.log2(1/p)

    return entropy

def find_exp_rem_guesses(u):
    return 0.15517759*u - 0.8952183 * (2**-u) + 1.9


def find_uncertainty(all_words_final):
    if len(all_words_final) == 0:
        return 0
    return math.log2(len(all_words_final))


def find_expected_score(word, all_words_final, num_guesses):
    EScore = 0
    if word in all_words_final:
        pWord = 1/len(all_words_final)*num_guesses
        EScore += pWord
    else:
        EScore += 0
        pWord = 0
    uncertainty = find_uncertainty(all_words_final)
    uncertainty -= find_entropy(word, all_words_final)
    exp_rem_guesses = find_exp_rem_guesses(uncertainty)
    
    EScore += (1-pWord)*(num_guesses + exp_rem_guesses)
    return EScore


def find_best_guess_exp_score(all_words_final, num_guesses):
    if len(all_words_final) == 1:
        return all_words_final[0]

    best = all_words[0]
    min_score = find_expected_score(best, all_words_final, num_guesses)
    for word in all_words[1:]:
        score = find_expected_score(word, all_words_final, num_guesses)
        if score < min_score:
            min_score = score
            best = word        
    return best


def find_actual_entropy(guess, pattern, rem_words):
    p = 0
    num_words = len(rem_words)
    for word in rem_words:
        if find_pattern(guess, word) == pattern:
            p += 1 / num_words
    return round(math.log2(1/p),2)


def find_entropy_and_freq(guess, rem_words):
    freq = {}
    num_words = len(rem_words)
    for word in rem_words:
        pattern = find_pattern(guess, word)
        if pattern in freq:
            freq[pattern] += 1/num_words
        else:
            freq[pattern] = 1/num_words

    entropy = 0
    for pattern in freq:
        p = freq[pattern]
        entropy += p * math.log2(1/p)
        freq[pattern] = round(p, 4)

    return entropy, freq


def find_entropy(guess, rem_words):
    freq = {}
    num_words = len(rem_words)
    for word in rem_words:
        pattern = find_pattern(guess, word)
        if pattern in freq:
            freq[pattern] += 1/num_words
        else:
            freq[pattern] = 1/num_words

    entropy = 0
    for pattern in freq:
        p = freq[pattern]
        entropy += p * math.log2(1/p)

    return entropy


def find_all_pattern_freq_final(guess, rem_words_final):
    freq = {}
    num_words = len(rem_words_final)
    for word in rem_words_final:
        pattern = find_pattern(guess, word)
        if pattern in freq:
            freq[pattern] += 1/num_words
        else:
            freq[pattern] = 1/num_words
    return freq


def find_pattern(g, w):
        w_lst = [x for x in w]
        w_dic = {}
        for c in w_lst:
            if c in w_dic:
                w_dic[c] += 1
            else:
                w_dic[c] = 1

        w_dic_copy = copy.deepcopy(w_dic)
        # make reds
        pattern = ["r","r","r","r","r"]
        
        # make yellow
        for i, c in enumerate(g):
            if c in w_dic:
                pattern[i] = "y"
                w_dic[c] -= 1
                if w_dic[c] == 0:
                    w_dic.pop(c)        

        # make green
        for i in range(5):
            if w[i] == g[i]:
                pattern[i] = "g"

        gy_dic = {}
        for i in range(5):
            if pattern[i] == "y" or pattern[i] == "g":
                if g[i] in gy_dic:
                    gy_dic[g[i]] += 1
                else:
                    gy_dic[g[i]] = 1

        for c in gy_dic:
            if w_dic_copy[c] < gy_dic[c]:
                for i in range(5):
                    if g[i] == c and pattern[i] == "y":
                        pattern[i] = "r"

        return "".join(pattern)


def find_best_guess(rem_words):
    # could run 2 (or even 3) step search of best candidates
    best = all_words[0]
    max_entropy = find_entropy(best, rem_words)
    
    for word in all_words[1:]:
        entropy = find_entropy(word, rem_words)
        if entropy > max_entropy:
            max_entropy = entropy
            best = word
    return best


def find_best_start():
    return find_best_guess(hidden_words)

def find_rem_words_final(rem_words):
    rem_words_final = []
    for w in rem_words:
        if is_final[w] == 1:
            rem_words_final.append(w)                
    return rem_words_final



def create_tree():
    # write function that plays wordle

    # starting off with word1 = salet
    word1 = FirstWord.objects.get(word_text = "salet")
    first_pattern = find_pattern(word1.word_text, word)

    pattern1 = FirstPattern(pattern_text=first_pattern)
    pattern1.first_word = word1


def play_game(word, word1):
    # word: str, word1: FirstWord
    first_pattern = find_pattern(word1.word_text, word)

    try:
        pattern1 = FirstPattern.objects.get(first_word = word1, pattern_text = first_pattern)
    except ObjectDoesNotExist:
        pattern1 = FirstPattern(first_word = word1, pattern_text = first_pattern)
        pattern1.data = pattern1.makeJSon()
        pattern1.save()

    if first_pattern == "ggggg":
        return

    # second turn
    if type(pattern1.data) == str:
        best_guess2 = json.loads(pattern1.data.replace("'", '"'))["best_guess"]
    else:
        best_guess2 = pattern1.data["best_guess"]

    try:
        word2 = SecondWord.objects.get(word_text = best_guess2, first_word = word1, first_pattern = pattern1)
    
    except ObjectDoesNotExist:
        word2 = SecondWord(word_text = best_guess2, first_word = word1, first_pattern = pattern1)
        update_rem_words(word2, word1, pattern1)
        word2.data = word2.makeJSon()
        word2.save()


    second_pattern = find_pattern(word2.word_text, word)    
    
    try:
        pattern2 = SecondPattern.objects.get(pattern_text = second_pattern, first_word = word1, first_pattern = pattern1, second_word = word2)
    except ObjectDoesNotExist:
        pattern2 = SecondPattern(pattern_text = second_pattern, first_word = word1, first_pattern = pattern1, second_word = word2)
        update_rem_words(word2, word1, pattern1)
        pattern2.data = pattern2.makeJSon()
        pattern2.save()    

    if second_pattern == "ggggg":
        return

    # third turn
    if type(pattern2.data) == str:
        best_guess3 = json.loads(pattern2.data.replace("'", '"'))["best_guess"]
    else:
        best_guess3 = pattern2.data["best_guess"]

    try:
        word3 = ThirdWord.objects.get(word_text = best_guess3, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2)
    except ObjectDoesNotExist:
        word3 = ThirdWord(word_text = best_guess3, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2)
        update_rem_words(word2, word1, pattern1)
        update_rem_words(word3, word2, pattern2)
        word3.data = word3.makeJSon()
        word3.save()

    
    third_pattern = find_pattern(word3.word_text, word)    

    try:
        pattern3 = ThirdPattern.objects.get(pattern_text = third_pattern, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2, third_word = word3)
    except ObjectDoesNotExist:
        pattern3 = ThirdPattern(pattern_text = third_pattern, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2, third_word = word3)
        update_rem_words(word2, word1, pattern1)
        update_rem_words(word3, word2, pattern2)
        pattern3.data = pattern3.makeJSon()
        pattern3.save()    

    if third_pattern == "ggggg":
        return

    # fourth turn
    # second turn
    if type(pattern3.data) == str:
        best_guess4 = json.loads(pattern3.data.replace("'", '"'))["best_guess"]
    else:
        best_guess4 = pattern3.data["best_guess"]

    try:
        word4 = FourthWord.objects.get(word_text = best_guess4, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2, third_word = word3, third_pattern = pattern3)
    except ObjectDoesNotExist:
        word4 = FourthWord(word_text = best_guess4, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2, third_word = word3, third_pattern = pattern3)
        update_rem_words(word2, word1, pattern1)
        update_rem_words(word3, word2, pattern2)
        update_rem_words(word4, word3, pattern3)
                
        word4.data = word4.makeJSon()
        word4.save()

    fourth_pattern = find_pattern(word4.word_text, word)    

    try:
        pattern4 = FourthPattern.objects.get(pattern_text = fourth_pattern, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2, third_word = word3, third_pattern = pattern3, fourth_word = word4)
    except ObjectDoesNotExist:
        pattern4 = FourthPattern(pattern_text = fourth_pattern, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2, third_word = word3, third_pattern = pattern3, fourth_word = word4)
        update_rem_words(word2, word1, pattern1)
        update_rem_words(word3, word2, pattern2)
        update_rem_words(word4, word3, pattern3)
        pattern4.data = pattern4.makeJSon()
        pattern4.save()    

    if fourth_pattern == "ggggg":
        return

    # fifth turn
    if type(pattern4.data) == str:
        best_guess5 = json.loads(pattern4.data.replace("'", '"'))["best_guess"]
    else:
        best_guess5 = pattern4.data["best_guess"]

    try:
        word5 = FifthWord.objects.get(word_text = best_guess5, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2, third_word = word3, third_pattern = pattern3, fourth_word = word4, fourth_pattern = pattern4)
    except ObjectDoesNotExist:
        word5 = FifthWord(word_text = best_guess5, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2, third_word = word3, third_pattern = pattern3, fourth_word = word4, fourth_pattern = pattern4)
        update_rem_words(word2, word1, pattern1)
        update_rem_words(word3, word2, pattern2)
        update_rem_words(word4, word3, pattern3)
        update_rem_words(word5, word4, pattern4)
        word5.update_rem_words()
        word5.data = word5.makeJSon()
        word5.save()

    fifth_pattern = find_pattern(word5.word_text, word)

    try:
        pattern5 = FifthPattern.objects.get(pattern_text = fifth_pattern, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2, third_word = word3, third_pattern = pattern3, fourth_word = word4, fourth_pattern = pattern4, fifth_word = word5)
    except ObjectDoesNotExist:
        pattern5 = FifthPattern(pattern_text = fifth_pattern, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2, third_word = word3, third_pattern = pattern3, fourth_word = word4, fourth_pattern = pattern4, fifth_word = word5)
        update_rem_words(word2, word1, pattern1)
        update_rem_words(word3, word2, pattern2)
        update_rem_words(word4, word3, pattern3)
        update_rem_words(word5, word4, pattern4)
        pattern5.data = pattern5.makeJSon()
        pattern5.save()    

    if fifth_pattern == "ggggg":
        return

    # sixth turn
    if type(pattern5.data) == str:
        best_guess6 = json.loads(pattern5.data.replace("'", '"'))["best_guess"]
    else:
        best_guess6 = pattern5.data["best_guess"]

    try:
        word6 = SixthWord.objects.get(word_text = best_guess6, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2, third_word = word3, third_pattern = pattern3, fourth_word = word4, fourth_pattern = pattern4, fifth_word = word5, fifth_pattern = pattern5)
    except ObjectDoesNotExist:
        word6 = SixthWord(word_text = best_guess6, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2, third_word = word3, third_pattern = pattern3, fourth_word = word4, fourth_pattern = pattern4, fifth_word = word5, fifth_pattern = pattern5)
        update_rem_words(word2, word1, pattern1)
        update_rem_words(word3, word2, pattern2)
        update_rem_words(word4, word3, pattern3)
        update_rem_words(word5, word4, pattern4)
        update_rem_words(word6, word5, pattern5)
        word6.data = word6.makeJSon()
        word6.save()

    sixth_pattern = find_pattern(word6.word_text, word)

    try:
        pattern6 = SixthPattern.objects.get(pattern_text = sixth_pattern, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2, third_word = word3, third_pattern = pattern3, fourth_word = word4, fourth_pattern = pattern4, fifth_word = word5, fifth_pattern = pattern5, sixth_word = word6)
    except ObjectDoesNotExist:
        pattern6 = SixthPattern(pattern_text = sixth_pattern, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2, third_word = word3, third_pattern = pattern3, fourth_word = word4, fourth_pattern = pattern4, fifth_word = word5, fifth_pattern = pattern5, sixth_word = word6)
        update_rem_words(word2, word1, pattern1)
        update_rem_words(word3, word2, pattern2)
        update_rem_words(word4, word3, pattern3)
        update_rem_words(word5, word4, pattern4)
        update_rem_words(word6, word5, pattern5)
        pattern6.data = pattern6.makeJSon()
        pattern6.save()    




def update_rem_words(word, prev_word, prev_pat):
    remaining_words = []
    for w in prev_word.rem_words:
        if find_pattern(prev_word.word_text, w) == prev_pat.pattern_text:
            remaining_words.append(w)

    word.rem_words = copy.deepcopy(remaining_words)

    remaining_words_final = []
    for w in word.rem_words:
        if is_final[w] == 1:
            remaining_words_final.append(w)                
    word.rem_words_final = copy.deepcopy(remaining_words_final)


class FirstWord(models.Model):
    word_text = models.CharField(max_length=5)
    data = models.TextField(blank=True)
    rem_words = copy.deepcopy(all_words)
    rem_words_final = copy.deepcopy(hidden_words)

    class Meta:
        db_table = "First_Word_Choices"
        
    def find_rem_words(self, guess, pattern):
        feasible = []
        for pos_word in self.rem_words:
            if find_pattern(guess, pos_word) == pattern:
                feasible.append(pos_word)
        return feasible
    
    def makeJSon(self):
        return makeJSon_word(self)

    def __str__(self):
        return self.word_text
    
    def find_best_guess(self):
        best = self.rem_words[0]
        max_entropy = self.find_entropy(best)
        
        for word in self.rem_words[1:]:
            entropy = self.find_entropy(word)
            if entropy > max_entropy:
                max_entropy = entropy
                best = word
        
        return best

    def find_entropy(self, guess):
        freq = {}
        num_words = len(self.rem_words)
        for word in self.rem_words:
            pattern = find_pattern(guess, word)
            if pattern in freq:
                freq[pattern] += 1/num_words
            else:
                freq[pattern] = 1/num_words

        entropy = 0
        for pattern in freq:
            p = freq[pattern]
            entropy += p * math.log2(1/p)

        return entropy
    
    def find_pattern(self, g, w):
        pattern = ""
        for i in range(5):
            if g[i] in w:
                if g[i] == w[i]:
                    pattern += "g"
                else:
                    pattern += "y"
            else:
                pattern += "r"

        return pattern

    def update_rem_words(self, pattern):
        remaining_words = []
        for w in self.rem_words:
            if find_pattern(self.word_text, w) == pattern:
                remaining_words.append(w)

        remaining_words_final = []
        for w in self.rem_words_final:
            if find_pattern(self.word_text, w) == pattern:
                remaining_words_final.append(w)    
        
        self.rem_words_final = copy.deepcopy(remaining_words_final)
        self.rem_words = copy.deepcopy(remaining_words)
        


    def find_all_patterns(self):
        patterns = set()
        for word in self.rem_words:
            patterns.add(find_pattern(self.word_text, word))
        return patterns
        
    def find_all_patterns_and_mapper(self):
        patterns = set()
        pattern_mapper = {}
        
        for word in self.rem_words:
            pattern = find_pattern(self.word_text, word)
            if pattern not in patterns:
                pattern_mapper[pattern] = [word]
            else:
                pattern_mapper[pattern].append(word)
            patterns.add(pattern)
        return (patterns, pattern_mapper)


    

class FirstPattern(models.Model):
    first_word = models.ForeignKey(FirstWord, on_delete=models.CASCADE)
    pattern_text = models.CharField(max_length=5)
    data = models.TextField(blank=True)

    class Meta:
        db_table = "First_Pattern_Choices"
    
    def __str__(self):
        return f"{self.first_word.word_text}: {self.pattern_text}"

    def makeJSon(self):
        return makeJSon_pattern(self.first_word, self, 1)


class SecondWord(models.Model):
    word_text = models.CharField(max_length=5)
    
    first_word =  models.ForeignKey(FirstWord, on_delete=models.CASCADE)
    first_pattern = models.ForeignKey(FirstPattern, on_delete=models.CASCADE)
    
    data = models.TextField(blank=True)
    rem_words = []
    
    class Meta:
        db_table = "Second_Word_Choices"
    
    def __str__(self):
        return f"{self.first_word.word_text}: {self.first_pattern.pattern_text} \n {self.word_text}"

    def makeJSon(self):
        return makeJSon_word(self)


    def find_rem_words(self, guess, pattern):
        feasible = []
        for pos_word in self.rem_words:
            if find_pattern(guess, pos_word) == pattern:
                feasible.append(pos_word)
        return feasible

    def find_best_guess(self):
        best = self.rem_words[0]
        max_entropy = self.find_entropy(best)
        
        for word in self.rem_words[1:]:
            entropy = self.find_entropy(word)
            if entropy > max_entropy:
                max_entropy = entropy
                best = word
        
        return best

    def find_entropy(self, guess):
        freq = {}
        num_words = len(self.rem_words)
        for word in self.rem_words:
            pattern = find_pattern(guess, word)
            if pattern in freq:
                freq[pattern] += 1/num_words
            else:
                freq[pattern] = 1/num_words

        entropy = 0
        for pattern in freq:
            p = freq[pattern]
            entropy += p * math.log2(1/p)

        return entropy
    
    def find_pattern(self, g, w):
        pattern = ""
        for i in range(5):
            if g[i] in w:
                if g[i] == w[i]:
                    pattern += "g"
                else:
                    pattern += "y"
            else:
                pattern += "r"

        return pattern

    def update_rem_words(self):
        remaining_words = []
        for w in self.first_word.rem_words:
            if find_pattern(self.first_word.word_text, w) == self.first_pattern.pattern_text:
                remaining_words.append(w)

        self.rem_words = copy.deepcopy(remaining_words)
        
        remaining_words_final = []
        for w in self.rem_words:
            if is_final[w] == 1:
                remaining_words_final.append(w)                
        self.rem_words_final = copy.deepcopy(remaining_words_final)


    def find_all_patterns(self):
        patterns = set()
        for word in self.rem_words:
            patterns.add(find_pattern(self.word_text, word))
        return patterns
        
    def find_all_patterns_and_mapper(self):
        patterns = set()
        pattern_mapper = {}
        
        for word in self.rem_words:
            pattern = find_pattern(self.word_text, word)
            if pattern not in patterns:
                pattern_mapper[pattern] = [word]
            else:
                pattern_mapper[pattern].append(word)
            patterns.add(pattern)
        return (patterns, pattern_mapper)



class SecondPattern(models.Model):
    first_word = models.ForeignKey(FirstWord, on_delete=models.CASCADE, default=1)
    first_pattern = models.ForeignKey(FirstPattern, on_delete=models.CASCADE, default=1)

    second_word = models.ForeignKey(SecondWord, on_delete=models.CASCADE, default=1)
    pattern_text = models.CharField(max_length=5, default=1)

    data = models.TextField(blank=True)

    class Meta:
        db_table = "Second_Pattern_Choices"
    
    def __str__(self):
        return f"{self.second_word.first_word.word_text}: {self.second_word.first_pattern.pattern_text} \n {self.second_word.word_text}: {self.pattern_text}"

    def makeJSon(self):
        return makeJSon_pattern(self.second_word, self, 2)
    

class ThirdWord(models.Model):

    first_word =  models.ForeignKey(FirstWord, on_delete=models.CASCADE)
    first_pattern = models.ForeignKey(FirstPattern, on_delete=models.CASCADE)
    
    second_word = models.ForeignKey(SecondWord, on_delete=models.CASCADE)
    second_pattern = models.ForeignKey(SecondPattern, on_delete=models.CASCADE)

    data = models.TextField(blank=True)
    word_text = models.CharField(max_length=5)

    rem_words = []
    
    class Meta:
        db_table = "Third_Word_Choices"
    
    def __str__(self):
        return f"{self.first_word.word_text}: {self.first_pattern.pattern_text} \n {self.second_word.word_text}: {self.second_pattern.pattern_text}"

    def makeJSon(self):
        return makeJSon_word(self)


    def find_rem_words(self, guess, pattern):
        feasible = []
        for pos_word in self.rem_words:
            if find_pattern(guess, pos_word) == pattern:
                feasible.append(pos_word)
        return feasible

    def find_best_guess(self):
        best = self.rem_words[0]
        max_entropy = self.find_entropy(best)
        
        for word in self.rem_words[1:]:
            entropy = self.find_entropy(word)
            if entropy > max_entropy:
                max_entropy = entropy
                best = word
        
        return best

    def find_entropy(self, guess):
        freq = {}
        num_words = len(self.rem_words)
        for word in self.rem_words:
            pattern = find_pattern(guess, word)
            if pattern in freq:
                freq[pattern] += 1/num_words
            else:
                freq[pattern] = 1/num_words

        entropy = 0
        for pattern in freq:
            p = freq[pattern]
            entropy += p * math.log2(1/p)

        return entropy
    
    def find_pattern(self, g, w):
        pattern = ""
        for i in range(5):
            if g[i] in w:
                if g[i] == w[i]:
                    pattern += "g"
                else:
                    pattern += "y"
            else:
                pattern += "r"

        return pattern

    def update_rem_words(self):
        remaining_words = []
        for w in self.second_word.rem_words:
            if find_pattern(self.second_word.word_text, w) == self.second_pattern.pattern_text:
                remaining_words.append(w)

        self.rem_words = copy.deepcopy(remaining_words)

        remaining_words_final = []
        for w in self.rem_words:
            if is_final[w] == 1:
                remaining_words_final.append(w)                
        self.rem_words_final = copy.deepcopy(remaining_words_final)


    def find_all_patterns(self):
        patterns = set()
        for word in self.rem_words:
            patterns.add(find_pattern(self.word_text, word))
        return patterns
        
    def find_all_patterns_and_mapper(self):
        patterns = set()
        pattern_mapper = {}
        
        for word in self.rem_words:
            pattern = find_pattern(self.word_text, word)
            if pattern not in patterns:
                pattern_mapper[pattern] = [word]
            else:
                pattern_mapper[pattern].append(word)
            patterns.add(pattern)
        return (patterns, pattern_mapper)



class ThirdPattern(models.Model):
    first_word = models.ForeignKey(FirstWord, on_delete=models.CASCADE, default=1)
    first_pattern = models.ForeignKey(FirstPattern, on_delete=models.CASCADE, default=1)

    second_word = models.ForeignKey(SecondWord, on_delete=models.CASCADE, default=1)
    second_pattern = models.ForeignKey(SecondPattern, on_delete=models.CASCADE, default=1)

    third_word = models.ForeignKey(ThirdWord, on_delete=models.CASCADE, default=1)
    pattern_text = models.CharField(max_length=5, default=1)

    data = models.TextField(blank=True)
    class Meta:
        db_table = "Third_Pattern_Choices"
    
    def __str__(self):
        return f"{self.second_word.first_word.word_text}: {self.second_word.first_pattern.pattern_text} \n {self.second_word.word_text}: {self.second_pattern.pattern_text} \n {self.third_word.word_text}: {self.pattern_text}"

    def makeJSon(self):
        return makeJSon_pattern(self.third_word, self, 3)

class FourthWord(models.Model):
    first_word =  models.ForeignKey(FirstWord, on_delete=models.CASCADE)
    first_pattern = models.ForeignKey(FirstPattern, on_delete=models.CASCADE)
    
    second_word = models.ForeignKey(SecondWord, on_delete=models.CASCADE)
    second_pattern = models.ForeignKey(SecondPattern, on_delete=models.CASCADE)

    third_word = models.ForeignKey(ThirdWord, on_delete=models.CASCADE)
    third_pattern = models.ForeignKey(ThirdPattern, on_delete=models.CASCADE)

    word_text = models.CharField(max_length=5)

    rem_words = []
    data = models.TextField(blank=True)

    class Meta:
        db_table = "Fourth_Word_Choices"
    
    def __str__(self):
        return f"{self.first_word.word_text}: {self.first_pattern.pattern_text} \n {self.second_word.word_text}: {self.second_pattern.pattern_text} \n {self.third_word.word_text}: {self.third_pattern.pattern_text} \n {self.word_text}"

    def makeJSon(self):
        return makeJSon_word(self)

    def find_rem_words(self, guess, pattern):
        feasible = []
        for pos_word in self.rem_words:
            if find_pattern(guess, pos_word) == pattern:
                feasible.append(pos_word)
        return feasible

    def find_best_guess(self):
        best = self.rem_words[0]
        max_entropy = self.find_entropy(best)
        
        for word in self.rem_words[1:]:
            entropy = self.find_entropy(word)
            if entropy > max_entropy:
                max_entropy = entropy
                best = word
        
        return best

    def find_entropy(self, guess):
        freq = {}
        num_words = len(self.rem_words)
        for word in self.rem_words:
            pattern = find_pattern(guess, word)
            if pattern in freq:
                freq[pattern] += 1/num_words
            else:
                freq[pattern] = 1/num_words

        entropy = 0
        for pattern in freq:
            p = freq[pattern]
            entropy += p * math.log2(1/p)

        return entropy
    
    def find_pattern(self, g, w):
        pattern = ""
        for i in range(5):
            if g[i] in w:
                if g[i] == w[i]:
                    pattern += "g"
                else:
                    pattern += "y"
            else:
                pattern += "r"

        return pattern

    def update_rem_words(self):
        remaining_words = []
        for w in self.third_word.rem_words:
            if find_pattern(self.third_word.word_text, w) == self.third_pattern.pattern_text:
                remaining_words.append(w)

        self.rem_words = copy.deepcopy(remaining_words)
        
        remaining_words_final = []
        for w in self.rem_words:
            if is_final[w] == 1:
                remaining_words_final.append(w)                
        self.rem_words_final = copy.deepcopy(remaining_words_final)

    def find_all_patterns(self):
        patterns = set()
        for word in self.rem_words:
            patterns.add(find_pattern(self.word_text, word))
        return patterns
        
    def find_all_patterns_and_mapper(self):
        patterns = set()
        pattern_mapper = {}
        
        for word in self.rem_words:
            pattern = find_pattern(self.word_text, word)
            if pattern not in patterns:
                pattern_mapper[pattern] = [word]
            else:
                pattern_mapper[pattern].append(word)
            patterns.add(pattern)
        return (patterns, pattern_mapper)



class FourthPattern(models.Model):
    first_word = models.ForeignKey(FirstWord, on_delete=models.CASCADE, default=1)
    first_pattern = models.ForeignKey(FirstPattern, on_delete=models.CASCADE, default=1)

    second_word = models.ForeignKey(SecondWord, on_delete=models.CASCADE, default=1)
    second_pattern = models.ForeignKey(SecondPattern, on_delete=models.CASCADE, default=1)

    third_word = models.ForeignKey(ThirdWord, on_delete=models.CASCADE, default=1)
    third_pattern = models.ForeignKey(ThirdPattern, on_delete=models.CASCADE, default=1)

    fourth_word = models.ForeignKey(FourthWord, on_delete=models.CASCADE, default=1)
    pattern_text = models.CharField(max_length=5, default=1)
    
    data = models.TextField(blank=True)

    class Meta:
        db_table = "Fourth_Pattern_Choices"
    
    def __str__(self):
        return f"{self.second_word.first_word.word_text}: {self.second_word.first_pattern.pattern_text} \n {self.second_word.word_text}: {self.second_pattern.pattern_text} \n {self.third_word.word_text}: {self.third_pattern.pattern_text} \n {self.fourth_word.word_text}: {self.pattern_text}"

    def makeJSon(self):
        return makeJSon_pattern(self.fourth_word, self, 4)
    

class FifthWord(models.Model):
    first_word =  models.ForeignKey(FirstWord, on_delete=models.CASCADE)
    first_pattern = models.ForeignKey(FirstPattern, on_delete=models.CASCADE)
    
    second_word = models.ForeignKey(SecondWord, on_delete=models.CASCADE)
    second_pattern = models.ForeignKey(SecondPattern, on_delete=models.CASCADE)

    third_word = models.ForeignKey(ThirdWord, on_delete=models.CASCADE)
    third_pattern = models.ForeignKey(ThirdPattern, on_delete=models.CASCADE)

    fourth_word = models.ForeignKey(FourthWord, on_delete=models.CASCADE)
    fourth_pattern = models.ForeignKey(FourthPattern, on_delete=models.CASCADE)

    
    word_text = models.CharField(max_length=5)
    data = models.TextField(blank=True)
    
    rem_words = []
    
    class Meta:
        db_table = "Fifth_Word_Choices"
    
    def __str__(self):
        return f"{self.first_word.word_text}: {self.first_pattern.pattern_text} \n {self.second_word.word_text}: {self.second_pattern.pattern_text} \n {self.third_word.word_text}: {self.third_pattern.pattern_text} \n {self.fourth_word.word_text}: {self.fourth_pattern.pattern_text} \n {self.word_text}"

    def makeJSon(self):
        return makeJSon_word(self)

    def find_rem_words(self, guess, pattern):
        feasible = []
        for pos_word in self.rem_words:
            if find_pattern(guess, pos_word) == pattern:
                feasible.append(pos_word)
        return feasible

    def find_best_guess(self):
        best = self.rem_words[0]
        max_entropy = self.find_entropy(best)
        
        for word in self.rem_words[1:]:
            entropy = self.find_entropy(word)
            if entropy > max_entropy:
                max_entropy = entropy
                best = word
        
        return best

    def find_entropy(self, guess):
        freq = {}
        num_words = len(self.rem_words)
        for word in self.rem_words:
            pattern = find_pattern(guess, word)
            if pattern in freq:
                freq[pattern] += 1/num_words
            else:
                freq[pattern] = 1/num_words

        entropy = 0
        for pattern in freq:
            p = freq[pattern]
            entropy += p * math.log2(1/p)

        return entropy
    
    def find_pattern(self, g, w):
        pattern = ""
        for i in range(5):
            if g[i] in w:
                if g[i] == w[i]:
                    pattern += "g"
                else:
                    pattern += "y"
            else:
                pattern += "r"

        return pattern

    def update_rem_words(self):
        remaining_words = []
        for w in self.fourth_word.rem_words:
            if find_pattern(self.fourth_word.word_text, w) == self.fourth_pattern.pattern_text:
                remaining_words.append(w)

        self.rem_words = copy.deepcopy(remaining_words)

        remaining_words_final = []
        for w in self.rem_words:
            if is_final[w] == 1:
                remaining_words_final.append(w)                
        self.rem_words_final = copy.deepcopy(remaining_words_final)

    def find_all_patterns(self):
        patterns = set()
        for word in self.rem_words:
            patterns.add(find_pattern(self.word_text, word))
        return patterns
        
    def find_all_patterns_and_mapper(self):
        patterns = set()
        pattern_mapper = {}
        
        for word in self.rem_words:
            pattern = find_pattern(self.word_text, word)
            if pattern not in patterns:
                pattern_mapper[pattern] = [word]
            else:
                pattern_mapper[pattern].append(word)
            patterns.add(pattern)
        return (patterns, pattern_mapper)



class FifthPattern(models.Model):
    first_word = models.ForeignKey(FirstWord, on_delete=models.CASCADE, default=1)
    first_pattern = models.ForeignKey(FirstPattern, on_delete=models.CASCADE, default=1)

    second_word = models.ForeignKey(SecondWord, on_delete=models.CASCADE, default=1)
    second_pattern = models.ForeignKey(SecondPattern, on_delete=models.CASCADE, default=1)

    third_word = models.ForeignKey(ThirdWord, on_delete=models.CASCADE, default=1)
    third_pattern = models.ForeignKey(ThirdPattern, on_delete=models.CASCADE, default=1)

    fourth_word = models.ForeignKey(FourthWord, on_delete=models.CASCADE, default=1)
    fourth_pattern = models.ForeignKey(FourthPattern, on_delete=models.CASCADE, default=1)

    fifth_word = models.ForeignKey(FifthWord, on_delete=models.CASCADE, default=1)
    pattern_text = models.CharField(max_length=5, default=1)
    data = models.TextField(blank=True)

    class Meta:
        db_table = "Fifth_Pattern_Choices"
    
    def __str__(self):
        return f"{self.second_word.first_word.word_text}: {self.second_word.first_pattern.pattern_text} \n {self.second_word.word_text}: {self.second_pattern.pattern_text} \n {self.third_word.word_text}: {self.third_pattern.pattern_text} \n {self.fourth_word.word_text}: {self.fourth_pattern.pattern_text} \n {self.fifth_word.word_text}: {self.pattern_text}"

    def makeJSon(self):
        return makeJSon_pattern(self.fifth_word, self, 5)
    
class SixthWord(models.Model):
    first_word =  models.ForeignKey(FirstWord, on_delete=models.CASCADE)
    first_pattern = models.ForeignKey(FirstPattern, on_delete=models.CASCADE)
    
    second_word = models.ForeignKey(SecondWord, on_delete=models.CASCADE)
    second_pattern = models.ForeignKey(SecondPattern, on_delete=models.CASCADE)

    third_word = models.ForeignKey(ThirdWord, on_delete=models.CASCADE)
    third_pattern = models.ForeignKey(ThirdPattern, on_delete=models.CASCADE)

    fourth_word = models.ForeignKey(FourthWord, on_delete=models.CASCADE)
    fourth_pattern = models.ForeignKey(FourthPattern, on_delete=models.CASCADE)

    fifth_word = models.ForeignKey(FifthWord, on_delete=models.CASCADE)
    fifth_pattern = models.ForeignKey(FifthPattern, on_delete=models.CASCADE)

    word_text = models.CharField(max_length=5)
    data = models.TextField(blank=True)

    rem_words = []
    
    class Meta:
        db_table = "Sixth_Word_Choices"
    
    def __str__(self):
        return f"{self.first_word.word_text}: {self.first_pattern.pattern_text} \n {self.second_word.word_text}: {self.second_pattern.pattern_text} \n {self.third_word.word_text}: {self.third_pattern.pattern_text} \n {self.fourth_word.word_text}: {self.fourth_pattern.pattern_text} \n {self.fifth_word.word_text}: {self.fifth_pattern.pattern_text} \n {self.word_text}"

    def makeJSon(self):
        return makeJSon_word(self)

    def find_rem_words(self, guess, pattern):
        feasible = []
        for pos_word in self.rem_words:
            if find_pattern(guess, pos_word) == pattern:
                feasible.append(pos_word)
        return feasible

    def find_best_guess(self):
        best = self.rem_words[0]
        max_entropy = self.find_entropy(best)
        
        for word in self.rem_words[1:]:
            entropy = self.find_entropy(word)
            if entropy > max_entropy:
                max_entropy = entropy
                best = word
        
        return best

    def find_entropy(self, guess):
        freq = {}
        num_words = len(self.rem_words)
        for word in self.rem_words:
            pattern = find_pattern(guess, word)
            if pattern in freq:
                freq[pattern] += 1/num_words
            else:
                freq[pattern] = 1/num_words

        entropy = 0
        for pattern in freq:
            p = freq[pattern]
            entropy += p * math.log2(1/p)

        return entropy
    
    def find_pattern(self, g, w):
        pattern = ""
        for i in range(5):
            if g[i] in w:
                if g[i] == w[i]:
                    pattern += "g"
                else:
                    pattern += "y"
            else:
                pattern += "r"

        return pattern

    def update_rem_words(self):
        remaining_words = []
        for w in self.fifth_word.rem_words:
            if find_pattern(self.fifth_word.word_text, w) == self.fifth_pattern.pattern_text:
                remaining_words.append(w)

        self.rem_words = copy.deepcopy(remaining_words)

        remaining_words_final = []
        for w in self.rem_words:
            if is_final[w] == 1:
                remaining_words_final.append(w)                
        self.rem_words_final = copy.deepcopy(remaining_words_final)

    def find_all_patterns(self):
        patterns = set()
        for word in self.rem_words:
            patterns.add(find_pattern(self.word_text, word))
        return patterns
        
    def find_all_patterns_and_mapper(self):
        patterns = set()
        pattern_mapper = {}
        
        for word in self.rem_words:
            pattern = find_pattern(self.word_text, word)
            if pattern not in patterns:
                pattern_mapper[pattern] = [word]
            else:
                pattern_mapper[pattern].append(word)
            patterns.add(pattern)
        return (patterns, pattern_mapper)



class SixthPattern(models.Model):
    first_word = models.ForeignKey(FirstWord, on_delete=models.CASCADE, default=1)
    first_pattern = models.ForeignKey(FirstPattern, on_delete=models.CASCADE, default=1)

    second_word = models.ForeignKey(SecondWord, on_delete=models.CASCADE, default=1)
    second_pattern = models.ForeignKey(SecondPattern, on_delete=models.CASCADE, default=1)

    third_word = models.ForeignKey(ThirdWord, on_delete=models.CASCADE, default=1)
    third_pattern = models.ForeignKey(ThirdPattern, on_delete=models.CASCADE, default=1)

    fourth_word = models.ForeignKey(FourthWord, on_delete=models.CASCADE, default=1)
    fourth_pattern = models.ForeignKey(FourthPattern, on_delete=models.CASCADE, default=1)

    fifth_word = models.ForeignKey(FifthWord, on_delete=models.CASCADE, default=1)
    fifth_pattern = models.ForeignKey(FifthPattern, on_delete=models.CASCADE, default=1)

    sixth_word = models.ForeignKey(SixthWord, on_delete=models.CASCADE, default=1)
    
    pattern_text = models.CharField(max_length=5, default=1)
    data = models.TextField(blank=True)

    class Meta:
        db_table = "Sixth_Pattern_Choices"
    
    def __str__(self):
        return f"{self.second_word.first_word.word_text}: {self.second_word.first_pattern.pattern_text} \n {self.second_word.word_text}: {self.second_pattern.pattern_text} \n {self.third_word.word_text}: {self.third_pattern.pattern_text} \n {self.fourth_word.word_text}: {self.fourth_pattern.pattern_text} \n {self.fifth_word.word_text}: {self.fifth_pattern.pattern_text} \n  {self.sixth_word.word_text}: {self.pattern_text}"

    def makeJSon(self):
        return makeJSon_pattern(self.sixth_word, self, 6)
    