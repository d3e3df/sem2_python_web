"""Flask-приложение для UGC-сервиса"""
from flask import Flask, request, jsonify
from flask_pydantic_spec import FlaskPydanticSpec

from .schemas import ReviewCreate
from .services import create_review, get_reviews, update_review_status

app = Flask(__name__)

app.config['DJANGO_API_URL'] = 'http://localhost:8000'

spec = FlaskPydanticSpec('flask', title='UGC API')
spec.register(app)


def error_response(message, code='ERROR', status=400):
    """Единый формат ошибок"""
    return jsonify({
        'success': False,
        'error': {
            'code': code,
            'message': message
        }
    }), status


@app.route('/ugc/reviews/', methods=['POST'])
def api_create_review():
    try:
        data = ReviewCreate(**request.json)
    except Exception as e:
        return error_response(str(e), 'VALIDATION_ERROR', 400)

    try:
        review = create_review(data)
        return jsonify(review.model_dump()), 201
    except ValueError as e:
        return error_response(str(e), 'PRODUCT_NOT_FOUND', 404)


@app.route('/ugc/reviews/', methods=['GET'])
def api_list_reviews():
    product_id = request.args.get('product_id', type=int)
    status = request.args.get('status', type=str)

    reviews = get_reviews(product_id, status)
    return jsonify([r.model_dump() for r in reviews]), 200


@app.route('/ugc/reviews/<int:review_id>/status', methods=['PATCH'])
def api_update_review_status(review_id):
    try:
        data = request.json
        status = data.get('status')
        if status not in ('active', 'hidden', 'pending'):
            return error_response('status должен быть: active, hidden или pending', 'VALIDATION_ERROR', 400)

        review = update_review_status(review_id, status)
        return jsonify(review.model_dump()), 200
    except ValueError as e:
        return error_response(str(e), 'REVIEW_NOT_FOUND', 404)


if __name__ == '__main__':
    app.run(port=5001, debug=True)