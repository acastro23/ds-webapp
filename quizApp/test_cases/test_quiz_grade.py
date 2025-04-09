from django.test import SimpleTestCase

class TestQuizScoreCalculation(SimpleTestCase):
    def test_all_correct(self):
        user_answers = {1: 101, 2: 202, 3: 303}
        correct_answers = {1: 101, 2: 202, 3: 303}
        score = sum(1 for q, a in user_answers.items() if correct_answers.get(q) == a)
        self.assertEqual(score, 3)

    def test_some_correct(self):
        user_answers = {1: 111, 2: 202, 3: 999}
        correct_answers = {1: 101, 2: 202, 3: 303}
        score = sum(1 for q, a in user_answers.items() if correct_answers.get(q) == a)
        self.assertEqual(score, 1)

    def test_none_correct(self):
        user_answers = {1: 111, 2: 222, 3: 333}
        correct_answers = {1: 101, 2: 202, 3: 303}
        score = sum(1 for q, a in user_answers.items() if correct_answers.get(q) == a)
        self.assertEqual(score, 0)

    def test_user_answer_extra_questions(self):
        user_answers = {1: 101, 2: 202, 3: 303, 4: 404}
        correct_answers = {1: 101, 2: 202, 3: 303}
        score = sum(1 for q, a in user_answers.items() if correct_answers.get(q) == a)
        self.assertEqual(score, 3)