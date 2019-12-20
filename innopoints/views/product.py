from flask import abort, request
from flask.views import MethodView
from flask_login import login_required, current_user
from marshmallow import ValidationError
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from innopoints.extensions import db
from innopoints.blueprints import api
from innopoints.models import Product
from innopoints.schemas import ProductSchema

NO_PAYLOAD = ('', 204)


@api.route('/products')
def list_products():
    """List products available in InnoStore."""
    default_limit = 3
    default_page = 1
    default_order = 'time'
    ordering = {
        'time': Product.addition_time,
        'price': Product.price
    }

    try:
        limit = int(request.args.get('limit', default_limit))
        page = int(request.args.get('page', default_page))
        search_query = request.args.get('q')
        order = request.args.get('order', default_order)
    except ValueError:
        abort(400, {'message': 'Bad query parameters.'})

    if limit < 1 or page < 1:
        abort(400, {'message': 'Limit and page number must be positive.'})

    db_query = Product.query
    if search_query is not None:
        # pylint: disable=no-member
        like_query = f'%{search_query}%'
        or_condition = or_(Product.name.ilike(like_query),
                           Product.description.ilike(like_query))
        db_query = db_query.filter(or_condition)
    db_query = db_query.order_by(ordering[order].asc())
    db_query = db_query.offset(limit * (page - 1)).limit(limit)

    schema = ProductSchema(many=True, exclude=('notifications', 'description',
                                               'varieties.stock_changes',
                                               'varieties.product',
                                               'varieties.product_id'))
    return schema.jsonify(db_query.all())


@api.route('/products', methods=['POST'])
@login_required
def create_product():
    """Create a new product."""
    if not request.is_json:
        abort(400, {'message': 'The request should be in JSON.'})

    if not current_user.is_admin:
        abort(401)

    in_schema = ProductSchema(exclude=('id', 'addition_time', 'notifications',
                                       'varieties.stock_changes.variety_id',
                                       'varieties.product_id',
                                       'varieties.images.variety_id'),
                              context={'user': current_user})

    try:
        new_product = in_schema.load(request.json)
    except ValidationError as err:
        abort(400, {'message': err.messages})

    try:
        for variety in new_product.varieties:
            variety.product = new_product
            for stock_change in variety.stock_changes:
                stock_change.variety_id = variety.id

        db.session.add(new_product)
        db.session.commit()
    except IntegrityError as err:
        db.session.rollback()
        print(err)  # TODO: replace with proper logging
        abort(400, {'message': 'Data integrity violated.'})

    out_schema = ProductSchema(exclude=('notifications',
                                        'varieties.product_id',
                                        'varieties.product',
                                        'varieties.images.variety_id',
                                        'varieties.images.id',
                                        'varieties.stock_changes'))
    return out_schema.jsonify(new_product)


class ProductDetailAPI(MethodView):
    """REST views for the Product model"""

    @login_required
    def patch(self, product_id):
        """Edit the product."""
        if not request.is_json:
            abort(400, {'message': 'The request should be in JSON.'})

        if not current_user.is_admin:
            abort(401)
        product = Product.query.get_or_404(product_id)

        in_out_schema = ProductSchema(exclude=('id', 'varieties', 'notifications', 'addition_time'))

        try:
            updated_product = in_out_schema.load(request.json, instance=product, partial=True)
        except ValidationError as err:
            abort(400, {'message': err.messages})

        try:
            db.session.add(updated_product)
            db.session.commit()
        except IntegrityError as err:
            db.session.rollback()
            print(err)  # TODO: replace with proper logging
            abort(400, {'message': 'Data integrity violated.'})

        return in_out_schema.jsonify(updated_product)

    @login_required
    def delete(self, product_id):
        """Delete the product."""
        if not current_user.is_admin:
            abort(401)
        product = Product.query.get_or_404(product_id)

        try:
            db.session.delete(product)
            db.session.commit()
        except IntegrityError as err:
            db.session.rollback()
            print(err)  # TODO: replace with proper logging
            abort(400, {'message': 'Data integrity violated.'})
        return NO_PAYLOAD


product_api = ProductDetailAPI.as_view('product_api')
api.add_url_rule('/products/<int:product_id>',
                 view_func=product_api,
                 methods=('PATCH', 'DELETE'))