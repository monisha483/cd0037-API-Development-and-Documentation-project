import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

# paginate questions
def paginate(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in selection]
    page_questions = questions[start:end]
    return page_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/categories")
    def retrieve_categories():
        selection = Category.query.order_by(Category.id).all()
        categories = {}
        for cat in selection:
            categories[cat.id] = cat.type
        if len(categories) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "categories": categories,
                "total_categories": len(Category.query.all()),
            }
        )

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    # GET endpoint for getting ist of questions, number of total questions, current category, categories
    @app.route('/questions', methods=['GET'])
    def get_questions():
        selection = Question.query.order_by(Question.id).all()
        questions = paginate(request, selection)
        if (len(questions) == 0):
            abort(404)
        CatSelection = Category.query.order_by(Category.id).all()
        categories = {}
        for cat in CatSelection:
            categories[cat.id] = cat.type
        return jsonify({
            'success': True,
            'questions': questions,
            'total_questions': len(selection),
            'categories': categories
            })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    #DELETE endpoint to delete a question
    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate(request, selection)

            return jsonify(
                {
                    "success": True,
                    "deleted": question_id,
                    "current_questions": current_questions,
                    "total_books": len(selection),
                }
            )

        except:
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    #endpoint to create a new question
    @app.route('/questions', methods=['POST'])
    def insert_question():
        body = request.get_json()
        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)
        try:
            question = Question(
            question=new_question,
            answer=new_answer,
            category=new_category,
            difficulty=new_difficulty
            )
            question.insert()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate(request, selection)
            return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(Question.query.all())
            })
        except Exception:
            abort(422)
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    #endpoint to get questions based on a search term
    @app.route("/search", methods=['POST'])
    def search():
        body = request.get_json()
        search = body.get('searchTerm')
        questions = Question.query.filter(
            Question.question.ilike('%'+search+'%')).all()

        if questions:
            currentQuestions = paginate(request, questions)
            return jsonify({
                'success': True,
                'questions': currentQuestions,
                'total_questions': len(questions)
            })
        else:
            abort(404)
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    #GET endpoint to get questions based on category
    @app.route('/categories/<int:cat_id>/questions', methods=['GET'])
    def get_questions_on_category(cat_id):
        category = Category.query.filter(
            Category.id == cat_id).first()

        selection = Question.query.order_by(Question.id).filter(
            Question.category == cat_id).all()
        current_questions = paginate(request, selection)

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(selection),
            'categories': [cat.type for cat in Category.query.all()],
            'current_category': category.format()
        })
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """


    #POST endpoint to get questions to play the quiz.
    @app.route('/quizzes', methods=['POST'])
    def play():
        try:
            print('hi!!')
            body = request.get_json()
            previous_questions = body.get('previous_questions', None)
            quiz_category = body.get('quiz_category', None)
            cat_id = quiz_category['id']
            if (quiz_category['id']== 0):
                print('if!!')
                questions = Question.query.filter().all()
            else:
                print('else!!')
                questions = Question.query.filter(
                    Question.category == quiz_category['id']).all()
            question = None
            flag = 0
            print('prev!!', previous_questions)
            if(len(previous_questions)!=0):
                while(flag==0):
                    #print('in while!!')
                    if(questions):
                        question = random.choice(questions)
                    for x in previous_questions:
                        if(x!=question):
                            flag=1
            else:
                question = random.choice(questions)
            print("hey! called!! ", question.format())
            return jsonify({
                'success': True,
                'question': question.format()})
        except Exception:
            abort(422)


    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            'error': 400,
            "message": "Bad Request"
        }), 400

    @app.errorhandler(404)
    def page_not_found(error):
        return jsonify({
            "success": False,
            'error': 404,
            "message": "Page Not found"
        }), 404

    @app.errorhandler(405)
    def invalid_method(error):
        return jsonify({
            "success": False,
            'error': 405,
            "message": "Invalid method"
        }), 405

    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({
            "success": False,
            'error': 422,
            "message": "Unprocessable Entity"
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            'error': 500,
            "message": "Internal Server Error"
        }), 500



    return app


