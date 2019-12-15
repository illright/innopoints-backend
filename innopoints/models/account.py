from flask_login.mixins import UserMixin

from innopoints.extensions import db, login_manager


class Account(UserMixin, db.Model):
    """Represents an account of a logged in user."""
    __tablename__ = 'accounts'

    full_name = db.Column(db.String(256), nullable=False)
    university_status = db.Column(db.String(64), nullable=True)
    email = db.Column(db.String(128), primary_key=True)
    telegram_username = db.Column(db.String(32), nullable=True)
    is_admin = db.Column(db.Boolean, nullable=False)
    created_projects = db.relationship('Project',
                                       cascade='all, delete-orphan',
                                       backref='creator')
    # property `moderated_projects` created with a backref
    stock_changes = db.relationship('StockChange',
                                    cascade='all, delete-orphan',
                                    passive_deletes=True,
                                    backref='account')
    transactions = db.relationship('Transaction')
    notifications = db.relationship('Notification',
                                    cascade='all, delete-orphan')
    applications = db.relationship('Application',
                                   cascade='all, delete-orphan',
                                   backref='applicant')

    def get_id(self):
        """Return the user's e-mail."""
        return self.email


@login_manager.user_loader
def load_user(email):
    """Return a user instance by the e-mail."""
    return Account.query.get(email)


class Transaction(db.Model):
    """Represents a change in the innopoints balance for a certain user."""
    __tablename__ = 'transactions'
    __table_args__ = (
        db.CheckConstraint('(stock_change_id IS NULL) != (feedback_id IS NULL)',
                           name='feedback xor stock_change'),
    )

    id = db.Column(db.Integer, primary_key=True)
    account_email = db.Column(db.String(128), db.ForeignKey('accounts.email'), nullable=False)
    change = db.Column(db.Integer, nullable=False)
    stock_change_id = db.Column(db.Integer, db.ForeignKey('stock_changes.id'), nullable=True)
    feedback_id = db.Column(db.Integer, db.ForeignKey('feedback.id'), nullable=True)