import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia"
        self.user = 'postgres'
        self.password = 'admin'
        self.hostname = 'localhost:5432'
        self.database_path = "postgresql://{}:{}@{}/{}".format(self.user, self.password, self.hostname, self.database_name)
        setup_db(self.app, self.database_path)
        self.new_question = {
            "answer": "Alexander Fleming",
            "category": 1,
            "difficulty": 3,
            "id": 1,
            "question": "Who discovered penicillin?"
        }
        self.new_category = {"id": 1,
        "type": "Art"}

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_retrieve_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["categories"])

    def test_get_paginated_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get("/questions?page=1000")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Page Not found")
    
    def test_delete_question(self):
        res = self.client().delete('/questions/1')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_delete_question_not_found(self):
        res = self.client().delete('/questions/10000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Unprocessable Entity")

    def test_create_new_question(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)
        pass

    def test_get_question_search_with_results(self):
        res = self.client().post("/search", json={'searchTerm': 'American', })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertEqual(data["total_questions"], 1)

    def test_get_question_search_without_results(self):
        res = self.client().post("/search", json={'searchTerm': 'dfdgdf', })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
    
    def test_questions_categories(self):
        res = self.client().get("/categories/3/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["total_questions"], 2)
        self.assertTrue(data["categories"])
    
    def test_get_questions_categories_abort(self):
        res = self.client().post("/categories/312/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)

    def test_quiz(self):
        quiz = {'previous_questions': [9],'quiz_category': {'type':'History','id': '3'}}
        res = self.client().post('/quizzes', json=quiz)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['question']['category'], 3)

    def test_quiz_not_found_category(self):
        quiz = {'previous_questions': [9],'quiz_category': {'type':'blahblah','id': '11111'}}
        res = self.client().post('/quizzes', json=quiz)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()