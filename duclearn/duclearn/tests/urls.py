from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
urlpatterns = [
        path('login/', auth_views.LoginView.as_view(), name='login'),
        path('logout/', auth_views.LogoutView.as_view(), name='logout'),
        path('register/', views.register, name='register'),
        path('tests/', views.tests, name='tests'),
        path('tests/add', views.add_test, name='add'),
        path('tests/test_details/<int:id>/delete', views.delete_test, name='delete'),
        path('tests/test_details/<int:id>', views.test_details, name='details'),
        path('tests/test_details/<int:id>/add_questions', views.add_questions, name='add_questions'),
        path('tests/test_details/<int:id>/start_test', views.start_test, name = 'start_test'),
        path('tests/test_details/<int:id>/solve_test/<int:questionId>', views.solve_test, name = 'solve_test'),
        path('tests/test_details/<int:id>/solve_test/test_finished', views.test_finished, name = 'test_finished'),
        path('flashcards', views.flashcards, name='flashcards'),
        path('flashcards/<int:setId>/', views.flashcardSet, name='flashcardSet'),
        path('flashcards/<int:setId>/card/<int:cardId>/', views.get_flashcard, name='get_flashcard'),
        path('guess_who/', views.guess_who, name='guess_who'),
        path('guess_who/create/', views.create_game, name="create_guesswho"),
        path('guess_who/join/', views.join_game, name="join_guesswho"),
        path('guess_who/<str:game_code>/choose/', views.choose_character, name="choose_character"),
        path('guess_who/<str:game_code>/play/', views.guess_game, name="guess_game"),
        path('guess_who/<str:game_code>/waiting_room/', views.waiting_room, name="waiting_room"),
        ]
