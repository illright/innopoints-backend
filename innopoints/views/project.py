from flask import abort, request
from flask.views import MethodView
from flask_login import login_required, current_user
from marshmallow import ValidationError
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from innopoints.extensions import db
from innopoints.blueprints import api
from innopoints.models import Activity, LifetimeStage, Project
from innopoints.schemas import ListProjectSchema, ProjectSchema

NO_PAYLOAD = ('', 204)


@api.route('/projects')
def list_projects():
    """List ongoing or past projects."""

    lifetime_stages = {
        'ongoing': LifetimeStage.ongoing,
        'past': LifetimeStage.past,
    }

    try:
        lifetime_stage = lifetime_stages[request.args['type']]
    except KeyError:
        abort(400, {'message': f'A project type must be one of: {", ".join(lifetime_stages)}'})

    db_query = Project.query.filter_by(lifetime_stage=lifetime_stage)
    if 'q' in request.args:
        # pylint: disable=no-member
        like_query = f'%{request.args["query"]}%'
        db_query = db_query.join(Project.activities)
        or_condition = or_(Project.title.ilike(like_query),
                           Activity.name.ilike(like_query),
                           Activity.description.ilike(like_query))
        db_query = db_query.filter(or_condition).distinct()

    if lifetime_stage == LifetimeStage.past:
        # pylint: disable=no-member
        page = int(request.args.get('page', 1))
        db_query = db_query.order_by(Project.id.desc())
        db_query = db_query.offset(10 * (page - 1)).limit(10)

    exclude = ['review_status', 'moderators']
    if current_user.is_authenticated:
        exclude.remove('moderators')
        if not current_user.is_admin:
            exclude.remove('review_status')

    schema = ListProjectSchema(many=True, exclude=exclude)
    return schema.jsonify(db_query.all())


@api.route('/projects/drafts')
@login_required
def list_drafts():
    """Return a list of drafts for the logged in user."""
    db_query = Project.query.filter_by(lifetime_stage=LifetimeStage.draft,
                                       creator=current_user)
    schema = ListProjectSchema(many=True, exclude=(
        'image_url',
        'organizer',
        'moderators',
        'review_status',
        'activities',
    ))
    return schema.jsonify(db_query.all())


@api.route('/projects', methods=['POST'])
@login_required
def create_project():
    """Create a new draft project."""
    if not request.is_json:
        abort(400, {'message': 'The request should be in JSON.'})

    in_schema = ProjectSchema(exclude=('id', 'creation_time', 'creator', 'admin_feedback',
                                       'review_status', 'lifetime_stage', 'files'))

    try:
        new_project = in_schema.load(request.json)
    except ValidationError as err:
        abort(400, {'message': err.messages})

    new_project.lifetime_stage = LifetimeStage.draft
    new_project.creator = current_user
    new_project.moderators.append(current_user)

    try:
        for new_activity in new_project.activities:
            new_activity.project = new_project

        db.session.add(new_project)
        db.session.commit()
    except IntegrityError as err:
        db.session.rollback()
        print(err)  # TODO: replace with proper logging
        abort(400, {'message': 'Data integrity violated.'})

    out_schema = ProjectSchema(exclude=('admin_feedback', 'review_status', 'files', 'image_id'),
                               context={'user': current_user})
    return out_schema.jsonify(new_project)


@api.route('/projects/<int:project_id>/publish', methods=['POST'])
@login_required
def publish_project(project_id):
    """Publish an existing draft project."""

    project = Project.query.get_or_404(project_id)

    if current_user.is_admin or project.creator == current_user:
        project.lifetime_stage = LifetimeStage.ongoing
        db.session.commit()
    else:
        abort(401)

    return NO_PAYLOAD


class ProjectDetailAPI(MethodView):
    """REST views for a particular instance of a Project model."""

    def get(self, project_id):
        """Get full information about the project"""
        project = Project.query.get_or_404(project_id)
        exclude = ['image_id',
                   'files',
                   'moderators',
                   'review_status',
                   'admin_feedback',
                   'activities.applications',
                   'activities.applications.telegram',
                   'activities.applications.comment']

        if current_user.is_authenticated:
            exclude.remove('moderators')
            exclude.remove('activities.applications')
            if current_user.email in project.moderators or current_user.is_admin:
                exclude.remove('review_status')
                exclude.remove('activities.applications.telegram')
                exclude.remove('activities.applications.comment')
                if current_user == project.creator or current_user.is_admin:
                    exclude.remove('admin_feedback')

        schema = ProjectSchema(exclude=exclude, context={'user': current_user})
        return schema.jsonify(project)

    @login_required
    def patch(self, project_id):
        """Edit the information of the project."""
        if not request.is_json:
            abort(400, {'message': 'The request should be in JSON.'})

        project = Project.query.get_or_404(project_id)
        if not current_user.is_admin and current_user != project.creator:
            abort(401)

        in_schema = ProjectSchema(only=('name', 'image_id', 'organizer', 'moderators'))

        try:
            updated_project = in_schema.load(request.json, instance=project, partial=True)
        except ValidationError as err:
            abort(400, {'message': err.messages})

        try:
            db.session.add(updated_project)
            db.session.commit()
        except IntegrityError as err:
            db.session.rollback()
            print(err)  # TODO: replace with proper logging
            abort(400, {'message': 'Data integrity violated.'})

        out_schema = ProjectSchema(only=('id', 'name', 'image_url', 'organizer', 'moderators'))
        return out_schema.jsonify(updated_project)

    @login_required
    def delete(self, project_id):
        """Delete the project entirely."""
        project = Project.query.get_or_404(project_id)
        if not current_user.is_admin and current_user != project.creator:
            abort(401)

        try:
            db.session.delete(project)
            db.session.commit()
        except IntegrityError as err:
            db.session.rollback()
            print(err)  # TODO: replace with proper logging
            abort(400, {'message': 'Data integrity violated.'})
        return NO_PAYLOAD


project_api = ProjectDetailAPI.as_view('project_detail_api')
api.add_url_rule('/projects/<int:project_id>',
                 view_func=project_api,
                 methods=('GET', 'PATCH', 'DELETE'))