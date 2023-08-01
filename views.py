from django.shortcuts import render

from django.http import HttpResponse, JsonResponse
from .models import FirstWord, FirstPattern, SecondWord, SecondPattern, ThirdWord, ThirdPattern, FourthWord, FourthPattern, FifthWord, FifthPattern, SixthWord, SixthPattern, find_best_start, play_game, AllWords, FinalWords, all_words, hidden_words
import copy
import json

def index(request):
    word_list = FirstWord.objects.all().order_by('word_text')
    context = {'word_list': word_list}
    return render(request, 'wordle/index.html', context)

def best_word(request):
    best = find_best_start()
    return HttpResponse(str(best))

def load_words(request):
    for word_text in all_words:
        try: 
            new = AllWords.objects.get(word = word_text)
        except:
            new = AllWords(word = word_text)
            new.save()

    for word_text in hidden_words:
        try: 
            new = FinalWords.objects.get(word = word_text)
        except:
            new = FinalWords(word = word_text)
            new.save()
    
    JS = json.dumps(FinalWords.objects.all()[-1], indent = 0)
    return HttpResponse(JS)


# will actually be where all the data is put
def create_tree(request):

    try:
        word1 = FirstWord.objects.get(word_text = "salet")
    except:
        word1 = FirstWord(word_text = "salet")
        word1.data = word1.makeJSon()
        word1.save()


    # # testing individal...
    # play_game("abode", word1)
    # JS = json.dumps(FourthWord.objects.all()[0].data, indent = 0 )
    # return HttpResponse(JS)
    
    hidden_words = []
    with open("wordle/hidden_words.txt") as h:
        for line in h:
            hidden_words.append(line.strip())

    errors = []
    for word in hidden_words:
        try:
            play_game(word, word1)
        except:
            errors.append(word)

    JS = json.dumps(errors, indent = 0)
    return HttpResponse(JS)




def first_word(request, first_word):
    # word = FirstWord(word_text=first_word)
    try:
        word = FirstWord.objects.get(word_text = first_word)
        JS = json.dumps(json.loads(word.data.replace("'", '"')))
        return HttpResponse(JS)

    except:
        word = FirstWord(word_text=first_word)
        word.data = word.makeJSon()
        JS = json.dumps(word.data)
        return HttpResponse(JS)    
    


def first_pattern(request, first_word, first_pattern):
    try:
        word1 = FirstWord.objects.get(word_text = first_word)
        pattern1 = FirstPattern.objects.get(first_word = word1, pattern_text = first_pattern)
        JS = json.dumps(json.loads(pattern1.data.replace("'", '"')))
        return HttpResponse(JS)
    except:
        word1 = FirstWord(word_text=first_word)
        pattern1 = FirstPattern(pattern_text=first_pattern)
        pattern1.first_word = word1
        pattern1.data = pattern1.makeJSon()
        JS = json.dumps(pattern1.data, indent = 0 )
        return HttpResponse(JS)
 
    


def second_word(request, first_word, first_pattern, second_word):
    try:
        word1 = FirstWord.objects.get(word_text = first_word)
        pattern1 = FirstPattern.objects.get(first_word = word1, pattern_text = first_pattern)
        word2 = SecondWord.objects.get(word_text = second_word, first_word = word1, first_pattern = pattern1)
        JS = json.dumps(json.loads(word2.data.replace("'", '"')))
        return HttpResponse(JS)
    except:
        word1 = FirstWord(word_text=first_word)
        pattern1 = FirstPattern(pattern_text=first_pattern)
        pattern1.first_word = word1
        word2 = SecondWord(word_text=second_word)
        word2.first_word = word1
        word2.first_pattern = pattern1
        word2.update_rem_words()
        word2.data = word2.makeJSon()
        JS = json.dumps(word2.data, indent = 0 )
        return HttpResponse(JS)


def second_pattern(request, first_word, first_pattern, second_word, second_pattern):
    try:
        word1 = FirstWord.objects.get(word_text = first_word)
        pattern1 = FirstPattern.objects.get(first_word = word1, pattern_text = first_pattern)

        word2 = SecondWord.objects.get(word_text = second_word, first_word = word1, first_pattern = pattern1)
        pattern2 = SecondPattern.objects.get(pattern_text = second_pattern, first_word = word1, first_pattern = pattern1, second_word = word2)

        JS = json.dumps(json.loads(pattern2.data.replace("'", '"')))
        return HttpResponse(JS)
    except:
        word1 = FirstWord(word_text=first_word)    
        pattern1 = FirstPattern(pattern_text=first_pattern)
        pattern1.first_word = word1
        word2 = SecondWord(word_text=second_word)
        word2.first_word = word1
        word2.first_pattern = pattern1
        word2.update_rem_words()
        pattern2 = SecondPattern(pattern_text=second_pattern)
        pattern2.first_word = word1
        pattern2.first_pattern = pattern1
        pattern2.second_word = word2
        data = pattern2.makeJSon()
        pattern2.data = data

        JS = json.dumps(pattern2.data, indent = 0 )
        return HttpResponse(JS)





def third_word(request, first_word, first_pattern, second_word, second_pattern, third_word):
    try:
        word1 = FirstWord.objects.get(word_text = first_word)
        pattern1 = FirstPattern.objects.get(first_word = word1, pattern_text = first_pattern)

        word2 = SecondWord.objects.get(word_text = second_word, first_word = word1, first_pattern = pattern1)
        pattern2 = SecondPattern.objects.get(pattern_text = second_pattern, first_word = word1, first_pattern = pattern1, second_word = word2)

        word3 = ThirdWord.objects.get(word_text = third_word, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2)
        
        JS = json.dumps(json.loads(word3.data.replace("'", '"')))
        return HttpResponse(JS)
    except:
        word1 = FirstWord(word_text=first_word)
        pattern1 = FirstPattern(pattern_text=first_pattern)
        pattern1.first_word = word1
        word2 = SecondWord(word_text=second_word)
        word2.first_word = word1
        word2.first_pattern = pattern1
        word2.update_rem_words()
        pattern2 = SecondPattern(pattern_text=second_pattern)
        pattern2.first_word = word1
        pattern2.first_pattern = pattern1
        pattern2.second_word = word2
        word3 = ThirdWord(word_text=third_word)
        word3.first_word = word1
        word3.first_pattern = pattern1
        word3.second_word = word2
        word3.second_pattern = pattern2
        word3.update_rem_words()
        data = word3.makeJSon()
        word3.data = data
        JS = json.dumps(data, indent = 0 )

        return HttpResponse(JS)



def third_pattern(request, first_word, first_pattern, second_word, second_pattern, third_word, third_pattern):
    try:
        word1 = FirstWord.objects.get(word_text = first_word)
        pattern1 = FirstPattern.objects.get(first_word = word1, pattern_text = first_pattern)

        word2 = SecondWord.objects.get(word_text = second_word, first_word = word1, first_pattern = pattern1)
        pattern2 = SecondPattern.objects.get(pattern_text = second_pattern, first_word = word1, first_pattern = pattern1, second_word = word2)

        word3 = ThirdWord.objects.get(word_text = third_word, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2)
        pattern3 = ThirdPattern.objects.get(pattern_text = third_pattern, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2, third_word = word3)

        JS = json.dumps(json.loads(pattern3.data.replace("'", '"')))
        return HttpResponse(JS)
    except:
        word1 = FirstWord(word_text=first_word)
        pattern1 = FirstPattern(pattern_text=first_pattern)
        pattern1.first_word = word1
        word2 = SecondWord(word_text=second_word)
        word2.first_word = word1
        word2.first_pattern = pattern1
        word2.update_rem_words()
        pattern2 = SecondPattern(pattern_text=second_pattern)
        pattern2.first_word = word1
        pattern2.first_pattern = pattern1
        pattern2.second_word = word2
        word3 = ThirdWord(word_text=third_word)
        word3.first_word = word1
        word3.first_pattern = pattern1
        word3.second_word = word2
        word3.second_pattern = pattern2
        word3.update_rem_words()
        pattern3 = ThirdPattern(pattern_text=third_pattern)
        pattern3.first_word = word1
        pattern3.first_pattern = pattern1
        pattern3.second_word = word2
        pattern3.second_pattern = pattern2
        pattern3.third_word = word3
        data = pattern3.makeJSon()
        pattern3.data = data
        JS = json.dumps(data, indent = 0 )

        return HttpResponse(JS)



def fourth_word(request, first_word, first_pattern, second_word, second_pattern, third_word, third_pattern, fourth_word):
    try:
        word1 = FirstWord.objects.get(word_text = first_word)
        pattern1 = FirstPattern.objects.get(first_word = word1, pattern_text = first_pattern)

        word2 = SecondWord.objects.get(word_text = second_word, first_word = word1, first_pattern = pattern1)
        pattern2 = SecondPattern.objects.get(pattern_text = second_pattern, first_word = word1, first_pattern = pattern1, second_word = word2)

        word3 = ThirdWord.objects.get(word_text = third_word, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2)
        pattern3 = ThirdPattern.objects.get(pattern_text = third_pattern, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2, third_word = word3)

        word4 = FourthWord.objects.get(word_text = fourth_word, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2, third_word = word3, third_pattern = pattern3)
        
        JS = json.dumps(json.loads(word4.data.replace("'", '"')))
        return HttpResponse(JS)

    except:
        word1 = FirstWord(word_text=first_word)
        pattern1 = FirstPattern(pattern_text=first_pattern)
        pattern1.first_word = word1
        
        word2 = SecondWord(word_text=second_word)
        word2.first_word = word1
        word2.first_pattern = pattern1
        word2.update_rem_words()

        pattern2 = SecondPattern(pattern_text=second_pattern)
        pattern2.first_word = word1
        pattern2.first_pattern = pattern1
        pattern2.second_word = word2
        
        word3 = ThirdWord(word_text=third_word)
        word3.first_word = word1
        word3.first_pattern = pattern1
        word3.second_word = word2
        word3.second_pattern = pattern2
        word3.update_rem_words()

        pattern3 = ThirdPattern(pattern_text=third_pattern)
        pattern3.first_word = word1
        pattern3.first_pattern = pattern1
        pattern3.second_word = word2
        pattern3.second_pattern = pattern2
        pattern3.third_word = word3

        word4 = FourthWord(word_text=fourth_word)
        word4.first_word = word1
        word4.first_pattern = pattern1
        word4.second_word = word2
        word4.second_pattern = pattern2
        word4.third_word = word3
        word4.third_pattern= pattern3
        word4.update_rem_words()

        data = word4.makeJSon()
        word4.data = data
        JS = json.dumps(data, indent = 0 )

        return HttpResponse(JS)

def fourth_pattern(request, first_word, first_pattern, second_word, second_pattern, third_word, third_pattern, fourth_word, fourth_pattern):
    try:
        word1 = FirstWord.objects.get(word_text = first_word)
        pattern1 = FirstPattern.objects.get(first_word = word1, pattern_text = first_pattern)

        word2 = SecondWord.objects.get(word_text = second_word, first_word = word1, first_pattern = pattern1)
        pattern2 = SecondPattern.objects.get(pattern_text = second_pattern, first_word = word1, first_pattern = pattern1, second_word = word2)

        word3 = ThirdWord.objects.get(word_text = third_word, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2)
        pattern3 = ThirdPattern.objects.get(pattern_text = third_pattern, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2, third_word = word3)

        word4 = FourthWord.objects.get(word_text = fourth_word, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2, third_word = word3, third_pattern = pattern3)
        pattern4 = FourthPattern.objects.get(pattern_text = fourth_pattern, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2, third_word = word3, third_pattern = pattern3, fourth_word = word4)
        
        JS = json.dumps(json.loads(pattern4.data.replace("'", '"')))
        return HttpResponse(JS)
    except:
        word1 = FirstWord(word_text=first_word)    
        pattern1 = FirstPattern(pattern_text=first_pattern)
        pattern1.first_word = word1
        
        word2 = SecondWord(word_text=second_word)
        word2.first_word = word1
        word2.first_pattern = pattern1
        word2.update_rem_words()

        pattern2 = SecondPattern(pattern_text=second_pattern)
        pattern2.first_word = word1
        pattern2.first_pattern = pattern1
        pattern2.second_word = word2

        word3 = ThirdWord(word_text=third_word)
        word3.first_word = word1
        word3.first_pattern = pattern1
        word3.second_word = word2
        word3.second_pattern = pattern2
        word3.update_rem_words()

        pattern3 = ThirdPattern(pattern_text=third_pattern)
        pattern3.first_word = word1
        pattern3.first_pattern = pattern1
        pattern3.second_word = word2
        pattern3.second_pattern = pattern2
        pattern3.third_word = word3

        word4 = FourthWord(word_text=fourth_word)
        word4.first_word = word1
        word4.first_pattern = pattern1
        word4.second_word = word2
        word4.second_pattern = pattern2
        word4.third_word = word3
        word4.third_pattern= pattern3
        word4.update_rem_words()

        pattern4 = FourthPattern(pattern_text=fourth_pattern)
        pattern4.first_word = word1
        pattern4.first_pattern = pattern1
        pattern4.second_word = word2
        pattern4.second_pattern = pattern2
        pattern4.third_word = word3
        pattern4.third_pattern = pattern3
        pattern4.fourth_word = word4

        data = pattern4.makeJSon()
        pattern4.data = data
        JS = json.dumps(data, indent = 0 )
        return HttpResponse(JS)

    
def fifth_word(request, first_word, first_pattern, second_word, second_pattern, third_word, third_pattern, fourth_word, fourth_pattern, fifth_word):
    try:
        word1 = FirstWord.objects.get(word_text = first_word)
        pattern1 = FirstPattern.objects.get(first_word = word1, pattern_text = first_pattern)

        word2 = SecondWord.objects.get(word_text = second_word, first_word = word1, first_pattern = pattern1)
        pattern2 = SecondPattern.objects.get(pattern_text = second_pattern, first_word = word1, first_pattern = pattern1, second_word = word2)

        word3 = ThirdWord.objects.get(word_text = third_word, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2)
        pattern3 = ThirdPattern.objects.get(pattern_text = third_pattern, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2, third_word = word3)

        word4 = FourthWord.objects.get(word_text = fourth_word, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2, third_word = word3, third_pattern = pattern3)
        pattern4 = FourthPattern.objects.get(pattern_text = fourth_pattern, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2, third_word = word3, third_pattern = pattern3, fourth_word = word4)

        word5 = FifthWord.objects.get(word_text = fifth_word, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2, third_word = word3, third_pattern = pattern3, fourth_word = word4, fourth_pattern = pattern4)

        JS = json.dumps(json.loads(word5.data.replace("'", '"')))
        return HttpResponse(JS)
    except:
        word1 = FirstWord(word_text=first_word)
        pattern1 = FirstPattern(pattern_text=first_pattern)
        pattern1.first_word = word1
        
        word2 = SecondWord(word_text=second_word)
        word2.first_word = word1
        word2.first_pattern = pattern1
        word2.update_rem_words()

        pattern2 = SecondPattern(pattern_text=second_pattern)
        pattern2.first_word = word1
        pattern2.first_pattern = pattern1
        pattern2.second_word = word2
        
        word3 = ThirdWord(word_text=third_word)
        word3.first_word = word1
        word3.first_pattern = pattern1
        word3.second_word = word2
        word3.second_pattern = pattern2
        word3.update_rem_words()

        pattern3 = ThirdPattern(pattern_text=third_pattern)
        pattern3.first_word = word1
        pattern3.first_pattern = pattern1
        pattern3.second_word = word2
        pattern3.second_pattern = pattern2
        pattern3.third_word = word3

        word4 = FourthWord(word_text=fourth_word)
        word4.first_word = word1
        word4.first_pattern = pattern1
        word4.second_word = word2
        word4.second_pattern = pattern2
        word4.third_word = word3
        word4.third_pattern= pattern3
        word4.update_rem_words()

        pattern4 = FourthPattern(pattern_text=fourth_pattern)
        pattern4.first_word = word1
        pattern4.first_pattern = pattern1
        pattern4.second_word = word2
        pattern4.second_pattern = pattern2
        pattern4.third_word = word3
        pattern4.third_pattern = pattern3
        pattern4.fourth_word = word4
        
        word5 = FifthWord(word_text=fifth_word)
        word5.first_word = word1
        word5.first_pattern = pattern1
        word5.second_word = word2
        word5.second_pattern = pattern2
        word5.third_word = word3
        word5.third_pattern= pattern3
        word5.fourth_word = word4
        word5.fourth_pattern= pattern4
        word5.update_rem_words()

        data = word5.makeJSon()
        word5.data = data
        JS = json.dumps(data, indent = 0 )
        return HttpResponse(JS)

    
def fifth_pattern(request, first_word, first_pattern, second_word, second_pattern, third_word, third_pattern, fourth_word, fourth_pattern, fifth_word, fifth_pattern):
    try:
        word1 = FirstWord.objects.get(word_text = first_word)
        pattern1 = FirstPattern.objects.get(first_word = word1, pattern_text = first_pattern)

        word2 = SecondWord.objects.get(word_text = second_word, first_word = word1, first_pattern = pattern1)
        pattern2 = SecondPattern.objects.get(pattern_text = second_pattern, first_word = word1, first_pattern = pattern1, second_word = word2)

        word3 = ThirdWord.objects.get(word_text = third_word, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2)
        pattern3 = ThirdPattern.objects.get(pattern_text = third_pattern, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2, third_word = word3)

        word4 = FourthWord.objects.get(word_text = fourth_word, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2, third_word = word3, third_pattern = pattern3)
        pattern4 = FourthPattern.objects.get(pattern_text = fourth_pattern, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2, third_word = word3, third_pattern = pattern3, fourth_word = word4)

        word5 = FifthWord.objects.get(word_text = fifth_word, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2, third_word = word3, third_pattern = pattern3, fourth_word = word4, fourth_pattern = pattern4)
        pattern5 = FifthPattern.objects.get(pattern_text = fifth_pattern, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2, third_word = word3, third_pattern = pattern3, fourth_word = word4, fourth_pattern = pattern4, fifth_word = word5)

        JS = json.dumps(json.loads(pattern5.data.replace("'", '"')))
        return HttpResponse(JS)
    except:
        word1 = FirstWord(word_text=first_word)
        pattern1 = FirstPattern(pattern_text=first_pattern)
        pattern1.first_word = word1
        
        word2 = SecondWord(word_text=second_word)
        word2.first_word = word1
        word2.first_pattern = pattern1
        word2.update_rem_words()

        pattern2 = SecondPattern(pattern_text=second_pattern)
        pattern2.first_word = word1
        pattern2.first_pattern = pattern1
        pattern2.second_word = word2

        word3 = ThirdWord(word_text=third_word)
        word3.first_word = word1
        word3.first_pattern = pattern1
        word3.second_word = word2
        word3.second_pattern = pattern2
        word3.update_rem_words()

        pattern3 = ThirdPattern(pattern_text=third_pattern)
        pattern3.first_word = word1
        pattern3.first_pattern = pattern1
        pattern3.second_word = word2
        pattern3.second_pattern = pattern2
        pattern3.third_word = word3

        word4 = FourthWord(word_text=fourth_word)
        word4.first_word = word1
        word4.first_pattern = pattern1
        word4.second_word = word2
        word4.second_pattern = pattern2
        word4.third_word = word3
        word4.third_pattern= pattern3
        word4.update_rem_words()

        pattern4 = FourthPattern(pattern_text=fourth_pattern)
        pattern4.first_word = word1
        pattern4.first_pattern = pattern1
        pattern4.second_word = word2
        pattern4.second_pattern = pattern2
        pattern4.third_word = word3
        pattern4.third_pattern = pattern3
        pattern4.fourth_word = word4

        word5 = FifthWord(word_text=fifth_word)
        word5.first_word = word1
        word5.first_pattern = pattern1
        word5.second_word = word2
        word5.second_pattern = pattern2
        word5.third_word = word3
        word5.third_pattern= pattern3
        word5.fourth_word = word4
        word5.fourth_pattern= pattern4
        word5.update_rem_words()

        pattern5 = FifthPattern(pattern_text=fifth_pattern)
        pattern5.first_word = word1
        pattern5.first_pattern = pattern1
        pattern5.second_word = word2
        pattern5.second_pattern = pattern2
        pattern5.third_word = word3
        pattern5.third_pattern = pattern3
        pattern5.fourth_word = word4
        pattern5.fourth_pattern = pattern4
        pattern5.fifth_word = word5
        pattern5.data = pattern5.makeJSon()

        JS = json.dumps(pattern5.data, indent = 0 )
        return HttpResponse(JS)


def sixth_word(request, first_word, first_pattern, second_word, second_pattern, third_word, third_pattern, fourth_word, fourth_pattern, fifth_word, fifth_pattern, sixth_word):
    try:
        word1 = FirstWord.objects.get(word_text = first_word)
        pattern1 = FirstPattern.objects.get(first_word = word1, pattern_text = first_pattern)

        word2 = SecondWord.objects.get(word_text = second_word, first_word = word1, first_pattern = pattern1)
        pattern2 = SecondPattern.objects.get(pattern_text = second_pattern, first_word = word1, first_pattern = pattern1, second_word = word2)

        word3 = ThirdWord.objects.get(word_text = third_word, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2)
        pattern3 = ThirdPattern.objects.get(pattern_text = third_pattern, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2, third_word = word3)

        word4 = FourthWord.objects.get(word_text = fourth_word, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2, third_word = word3, third_pattern = pattern3)
        pattern4 = FourthPattern.objects.get(pattern_text = fourth_pattern, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2, third_word = word3, third_pattern = pattern3, fourth_word = word4)

        word5 = FifthWord.objects.get(word_text = fifth_word, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2, third_word = word3, third_pattern = pattern3, fourth_word = word4, fourth_pattern = pattern4)
        pattern5 = FifthPattern.objects.get(pattern_text = fifth_pattern, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2, third_word = word3, third_pattern = pattern3, fourth_word = word4, fourth_pattern = pattern4, fifth_word = word5)

        word6 = SixthWord.objects.get(word_text = fifth_word, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2, third_word = word3, third_pattern = pattern3, fourth_word = word4, fourth_pattern = pattern4, fifth_word = word5, fifth_pattern = pattern5)

        JS = json.dumps(json.loads(word6.data.replace("'", '"')))
        return HttpResponse(JS)

    except:
        word1 = FirstWord(word_text=first_word)
        pattern1 = FirstPattern(pattern_text=first_pattern)
        pattern1.first_word = word1
        
        word2 = SecondWord(word_text=second_word)
        word2.first_word = word1
        word2.first_pattern = pattern1
        word2.update_rem_words()

        pattern2 = SecondPattern(pattern_text=second_pattern)
        pattern2.first_word = word1
        pattern2.first_pattern = pattern1
        pattern2.second_word = word2
        
        word3 = ThirdWord(word_text=third_word)
        word3.first_word = word1
        word3.first_pattern = pattern1
        word3.second_word = word2
        word3.second_pattern = pattern2
        word3.update_rem_words()

        pattern3 = ThirdPattern(pattern_text=third_pattern)
        pattern3.first_word = word1
        pattern3.first_pattern = pattern1
        pattern3.second_word = word2
        pattern3.second_pattern = pattern2
        pattern3.third_word = word3

        word4 = FourthWord(word_text=fourth_word)
        word4.first_word = word1
        word4.first_pattern = pattern1
        word4.second_word = word2
        word4.second_pattern = pattern2
        word4.third_word = word3
        word4.third_pattern= pattern3
        word4.update_rem_words()

        pattern4 = FourthPattern(pattern_text=fourth_pattern)
        pattern4.first_word = word1
        pattern4.first_pattern = pattern1
        pattern4.second_word = word2
        pattern4.second_pattern = pattern2
        pattern4.third_word = word3
        pattern4.third_pattern = pattern3
        pattern4.fourth_word = word4
        
        word5 = FifthWord(word_text=fifth_word)
        word5.first_word = word1
        word5.first_pattern = pattern1
        word5.second_word = word2
        word5.second_pattern = pattern2
        word5.third_word = word3
        word5.third_pattern= pattern3
        word5.fourth_word = word4
        word5.fourth_pattern= pattern4
        word5.update_rem_words()

        pattern5 = FifthPattern(pattern_text=fifth_pattern)
        pattern5.first_word = word1
        pattern5.first_pattern = pattern1
        pattern5.second_word = word2
        pattern5.second_pattern = pattern2
        pattern5.third_word = word3
        pattern5.third_pattern = pattern3
        pattern5.fourth_word = word4
        pattern5.fourth_pattern = pattern4
        pattern5.fifth_word = word5

        word6 = SixthWord(word_text=sixth_word)
        word6.first_word = word1
        word6.first_pattern = pattern1
        word6.second_word = word2
        word6.second_pattern = pattern2
        word6.third_word = word3
        word6.third_pattern= pattern3
        word6.fourth_word = word4
        word6.fourth_pattern= pattern4
        word6.fifth_word = word5
        word6.fifth_pattern= pattern5    
        word6.update_rem_words()

        data = word6.makeJSon()
        word6.data = data
        JS = json.dumps(data, indent = 0 )
        return HttpResponse(JS)

    
def sixth_pattern(request, first_word, first_pattern, second_word, second_pattern, third_word, third_pattern, fourth_word, fourth_pattern, fifth_word, fifth_pattern, sixth_word, sixth_pattern):
    try:
        word1 = FirstWord.objects.get(word_text = first_word)
        pattern1 = FirstPattern.objects.get(first_word = word1, pattern_text = first_pattern)

        word2 = SecondWord.objects.get(word_text = second_word, first_word = word1, first_pattern = pattern1)
        pattern2 = SecondPattern.objects.get(pattern_text = second_pattern, first_word = word1, first_pattern = pattern1, second_word = word2)

        word3 = ThirdWord.objects.get(word_text = third_word, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2)
        pattern3 = ThirdPattern.objects.get(pattern_text = third_pattern, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2, third_word = word3)

        word4 = FourthWord.objects.get(word_text = fourth_word, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2, third_word = word3, third_pattern = pattern3)
        pattern4 = FourthPattern.objects.get(pattern_text = fourth_pattern, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2, third_word = word3, third_pattern = pattern3, fourth_word = word4)

        word5 = FifthWord.objects.get(word_text = fifth_word, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2, third_word = word3, third_pattern = pattern3, fourth_word = word4, fourth_pattern = pattern4)
        pattern5 = FifthPattern.objects.get(pattern_text = fifth_pattern, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2, third_word = word3, third_pattern = pattern3, fourth_word = word4, fourth_pattern = pattern4, fifth_word = word5)
        
        word6 = SixthWord.objects.get(word_text = fifth_word, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2, third_word = word3, third_pattern = pattern3, fourth_word = word4, fourth_pattern = pattern4, fifth_word = word5, fifth_pattern = pattern5)
        pattern6 = SixthPattern.objects.get(pattern_text = fourth_pattern, first_word = word1, first_pattern = pattern1, second_word = word2, second_pattern = pattern2, third_word = word3, third_pattern = pattern3, fourth_word = word4, fourth_pattern = pattern4, fifth_word = word5, fifth_pattern = pattern5, sixth_word = word6)

        JS = json.dumps(json.loads(pattern6.data.replace("'", '"')))
        return HttpResponse(JS)
    except:
        word1 = FirstWord(word_text=first_word)
        pattern1 = FirstPattern(pattern_text=first_pattern)
        pattern1.first_word = word1
        
        word2 = SecondWord(word_text=second_word)
        word2.first_word = word1
        word2.first_pattern = pattern1
        word2.update_rem_words()

        pattern2 = SecondPattern(pattern_text=second_pattern)
        pattern2.first_word = word1
        pattern2.first_pattern = pattern1
        pattern2.second_word = word2

        word3 = ThirdWord(word_text=third_word)
        word3.first_word = word1
        word3.first_pattern = pattern1
        word3.second_word = word2
        word3.second_pattern = pattern2
        word3.update_rem_words()

        pattern3 = ThirdPattern(pattern_text=third_pattern)
        pattern3.first_word = word1
        pattern3.first_pattern = pattern1
        pattern3.second_word = word2
        pattern3.second_pattern = pattern2
        pattern3.third_word = word3

        word4 = FourthWord(word_text=fourth_word)
        word4.first_word = word1
        word4.first_pattern = pattern1
        word4.second_word = word2
        word4.second_pattern = pattern2
        word4.third_word = word3
        word4.third_pattern= pattern3
        word4.update_rem_words()

        pattern4 = FourthPattern(pattern_text=fourth_pattern)
        pattern4.first_word = word1
        pattern4.first_pattern = pattern1
        pattern4.second_word = word2
        pattern4.second_pattern = pattern2
        pattern4.third_word = word3
        pattern4.third_pattern = pattern3
        pattern4.fourth_word = word4

        word5 = FifthWord(word_text=fifth_word)
        word5.first_word = word1
        word5.first_pattern = pattern1
        word5.second_word = word2
        word5.second_pattern = pattern2
        word5.third_word = word3
        word5.third_pattern= pattern3
        word5.fourth_word = word4
        word5.fourth_pattern= pattern4
        word5.update_rem_words()

        pattern5 = FifthPattern(pattern_text=fifth_pattern)
        pattern5.first_word = word1
        pattern5.first_pattern = pattern1
        pattern5.second_word = word2
        pattern5.second_pattern = pattern2
        pattern5.third_word = word3
        pattern5.third_pattern = pattern3
        pattern5.fourth_word = word4
        pattern5.fourth_pattern = pattern4
        pattern5.fifth_word = word5
        
        word6 = SixthWord(word_text=sixth_word)
        word6.first_word = word1
        word6.first_pattern = pattern1
        word6.second_word = word2
        word6.second_pattern = pattern2
        word6.third_word = word3
        word6.third_pattern= pattern3
        word6.fourth_word = word4
        word6.fourth_pattern= pattern4
        word6.fifth_word = word5
        word6.fifth_pattern= pattern5    
        word6.update_rem_words()

        pattern6 = SixthPattern(pattern_text=sixth_pattern)
        pattern6.first_word = word1
        pattern6.first_pattern = pattern1
        pattern6.second_word = word2
        pattern6.second_pattern = pattern2
        pattern6.third_word = word3
        pattern6.third_pattern = pattern3
        pattern6.fourth_word = word4
        pattern6.fourth_pattern = pattern4
        pattern6.fifth_word = word5
        pattern6.fifth_pattern= pattern5
        pattern6.sixth_word = word6
        
        data = pattern6.makeJSon()
        pattern6.data = data
        JS = json.dumps(data, indent = 0 )
        return HttpResponse(JS)