from django.test import TestCase

# Create your tests here.
import datetime
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question, Choice

def create_question(question_text, days, choices):
    #Create a question with the given `question_text` and published the given number of `days` offset to now (negative for questions published in the past, positive for questions that have yet to be published).
    time = timezone.now() + datetime.timedelta(days=days)
    question = Question.objects.create(question_text=question_text, pub_date=time)
    if(choices):
        create_choice(Question.objects.get(pk=question.id), "Choice A", 0)
    return question

def create_choice(question, choice_text, votes):
    #Create a question with the given `question_text` and published the given number of `days` offset to now (negative for questions published in the past, positive for questions that have yet to be published).
    return Choice.objects.create(question = question, choice_text=choice_text, votes=0)

class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        #was_published_recently() returns False for questions whose pub_date is in the future.
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date = time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        #was_published_recently() returns False for questions whose pub_date is older than 1 day.
        time = timezone.now() - datetime.timedelta(days=3, seconds=1)
        old_question = Question(pub_date = time)
        self.assertIs(old_question.was_published_recently(), False)
    
    def test_was_published_recently_with_recent_question(self):
        #was_published_recently() returns False for questions whose pub_date is within the last day.
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date = time)
        self.assertIs(recent_question.was_published_recently(), True)

class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        #If no questions exist, an appropriate message is displayed.
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])
    
    def test_past_questions(self):
        #Questions with a pub_date in the past are displayed on the index page.
        question_text = "Past question."
        create_question(question_text, -30, True)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: '+question_text+'>'])
    
    def test_future_questions(self):
        #Questions with a pub_date in the future aren't displayed on the index page.
        question_text = "Future question."
        create_question(question_text, 30, True)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])
    
    def test_future_question_and_past_question(self):
        #Even if both past and future questions exist, only past questions are displayed.
        past_question_text = "Past question."
        future_question_text = "Future question."
        create_question(past_question_text, -30, True)
        create_question(future_question_text, 30, False)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: '+past_question_text+'>']) #JCNM
        #self.assertQuerysetEqual(response.context['latest_question_list'], []) #JCNM
    
    def test_two_past_questions(self):
        #The questions index page may display multiple questions.
        past_question_text_1 = "Past question 1."
        past_question_text_2 = "Past question 2."
        create_question(past_question_text_1, -30, True)
        create_question(past_question_text_2, -5, True)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: '+past_question_text_2+'>','<Question: '+past_question_text_1+'>'])
    
    def test_questions_with_choices(self):
        #Exclude the questions that have two choices.
        question_text = "Question withput choices."
        create_question(question_text, -1, True)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: '+question_text+'>'])
    
    def test_questions_with_no_choices(self):
        #Exclude the questions that have no choices.
        question_text = "Question withput choices."
        create_question(question_text, -1, False)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        #The detail view of a question with a pub_date in the future returns a 404 not found.
        future_question = create_question('Future question.', 5, False)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
    
    def test_past_question(self):
        #The detail view of a question with a pub_date in the past displays the question's text.
        past_question = create_question('Past question.', -5, True)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

class QuestionResultsViewTests(TestCase):
    def test_future_question(self):
        #The results view of a question with a pub_date in the future returns a 404 not found.
        future_question = create_question('Future question.', 5, False)
        url = reverse('polls:results', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
    
    def test_past_question(self):
        #The results view of a question with a pub_date in the past displays the question's text.
        past_question = create_question('Past question.', -5, True)
        url = reverse('polls:results', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)