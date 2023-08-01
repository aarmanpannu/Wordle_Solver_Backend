from django.urls import path

from . import views

urlpatterns = [
    # Landing Page
    # ex: /wordle/
    path('', views.index, name='index'),

    # Best Word
    # ex: /wordle/best
    path('best', views.best_word, name='best'),
    
    # Creates Tree for Given First Word
    # path('createTree', views.create_tree, name='createTree'),

    # Adds all the words to the DB
    # not necessary unless changing DB's
    # path('load_words', views.load_words, name="load_words"),

    # First Word
    # ex: /wordle/abyss
    path('<slug:first_word>/', views.first_word, name='first_word'),

    # First Pattern
    # ex: /wordle/abyss/gyrry
    path('<slug:first_word>/<slug:first_pattern>', views.first_pattern, name='first_pattern'),
    
    # Second Word
    # ex: /wordle/abyss/gyrry/waves
    path('<slug:first_word>/<slug:first_pattern>/<slug:second_word>', views.second_word, name='second_word'),

    # Second Pattern
    # ex: /wordle/abyss/gyrry/waves/ryyyr
    path('<slug:first_word>/<slug:first_pattern>/<slug:second_word>/<slug:second_pattern>', views.second_pattern, name='second_pattern'),

    # Third Word
    path('<slug:first_word>/<slug:first_pattern>/<slug:second_word>/<slug:second_pattern>/<slug:third_word>', views.third_word, name='third_word'),
    
    # Third Pattern
    path('<slug:first_word>/<slug:first_pattern>/<slug:second_word>/<slug:second_pattern>/<slug:third_word>/<slug:third_pattern>', views.third_pattern, name='third_pattern'),

    # Fourth Word
    path('<slug:first_word>/<slug:first_pattern>/<slug:second_word>/<slug:second_pattern>/<slug:third_word>/<slug:third_pattern>/<slug:fourth_word>', views.fourth_word, name='fourth_word'),
    
    # Fourth Pattern
    path('<slug:first_word>/<slug:first_pattern>/<slug:second_word>/<slug:second_pattern>/<slug:third_word>/<slug:third_pattern>/<slug:fourth_word>/<slug:fourth_pattern>', views.fourth_pattern, name='fourth_pattern'),

    # Fifth Word
    path('<slug:first_word>/<slug:first_pattern>/<slug:second_word>/<slug:second_pattern>/<slug:third_word>/<slug:third_pattern>/<slug:fourth_word>/<slug:fourth_pattern>/<slug:fifth_word>', views.fifth_word, name='fifth_word'),
    
    # Fifth Pattern
    path('<slug:first_word>/<slug:first_pattern>/<slug:second_word>/<slug:second_pattern>/<slug:third_word>/<slug:third_pattern>/<slug:fourth_word>/<slug:fourth_pattern>/<slug:fifth_word>/<slug:fifth_pattern>', views.fifth_pattern, name='fifth_pattern'),

    # Sixth Word
    path('<slug:first_word>/<slug:first_pattern>/<slug:second_word>/<slug:second_pattern>/<slug:third_word>/<slug:third_pattern>/<slug:fourth_word>/<slug:fourth_pattern>/<slug:fifth_word>/<slug:fifth_pattern>/<slug:sixth_word>', views.sixth_word, name='sixth_word'),
    
    # Sixth Pattern
    path('<slug:first_word>/<slug:first_pattern>/<slug:second_word>/<slug:second_pattern>/<slug:third_word>/<slug:third_pattern>/<slug:fourth_word>/<slug:fourth_pattern>/<slug:fifth_word>/<slug:fifth_pattern>/<slug:sixth_word>/<slug:sixth_pattern>', views.sixth_pattern, name='sixth_pattern'),


]