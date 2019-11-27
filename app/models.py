from datetime import datetime
import json
from hashlib import md5

import jsonpickle
import sqlalchemy
from sqlalchemy import String
from sqlalchemy.ext.mutable import Mutable
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import papermill as pm

from app import db
from app import login


class JSONEncodedObj(sqlalchemy.types.TypeDecorator):
    """Represents an immutable structure as a json-encoded string."""

    impl = String

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class MutationObj(Mutable):
    @classmethod
    def coerce(cls, key, value):
        if isinstance(value, dict) and not isinstance(value, MutationDict):
            return MutationDict.coerce(key, value)
        if isinstance(value, list) and not isinstance(value, MutationList):
            return MutationList.coerce(key, value)
        return value

    @classmethod
    def _listen_on_attribute(cls, attribute, coerce, parent_cls):
        key = attribute.key
        if parent_cls is not attribute.class_:
            return

        # rely on "propagate" here
        parent_cls = attribute.class_

        def load(state, *args):
            val = state.dict.get(key, None)
            if coerce:
                val = cls.coerce(key, val)
                state.dict[key] = val
            if isinstance(val, cls):
                val._parents[state.obj()] = key

        def set(target, value, oldvalue, initiator):
            if not isinstance(value, cls):
                value = cls.coerce(key, value)
            if isinstance(value, cls):
                value._parents[target.obj()] = key
            if isinstance(oldvalue, cls):
                oldvalue._parents.pop(target.obj(), None)
            return value

        def pickle(state, state_dict):
            val = state.dict.get(key, None)
            if isinstance(val, cls):
                if "ext.mutable.values" not in state_dict:
                    state_dict["ext.mutable.values"] = []
                state_dict["ext.mutable.values"].append(val)

        def unpickle(state, state_dict):
            if "ext.mutable.values" in state_dict:
                for val in state_dict["ext.mutable.values"]:
                    val._parents[state.obj()] = key

        sqlalchemy.event.listen(parent_cls, "load", load, raw=True, propagate=True)
        sqlalchemy.event.listen(parent_cls, "refresh", load, raw=True, propagate=True)
        sqlalchemy.event.listen(
            attribute, "set", set, raw=True, retval=True, propagate=True
        )
        sqlalchemy.event.listen(parent_cls, "pickle", pickle, raw=True, propagate=True)
        sqlalchemy.event.listen(
            parent_cls, "unpickle", unpickle, raw=True, propagate=True
        )


class MutationDict(MutationObj, dict):
    @classmethod
    def coerce(cls, key, value):
        """
        Convert plain dictionary to MutationDict.
        """
        self = MutationDict((k, MutationObj.coerce(key, v)) for (k, v) in value.items())
        self._key = key
        return self

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, MutationObj.coerce(self._key, value))
        self.changed()

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self.changed()


class MutationList(MutationObj, list):
    @classmethod
    def coerce(cls, key, value):
        """Convert plain list to MutationList"""
        self = MutationList((MutationObj.coerce(key, v) for v in value))
        self._key = key
        return self

    def __setitem__(self, idx, value):
        list.__setitem__(self, idx, MutationObj.coerce(self._key, value))
        self.changed()

    def __setslice__(self, start, stop, values):
        list.__setslice__(
            self, start, stop, (MutationObj.coerce(self._key, v) for v in values)
        )
        self.changed()

    def __delitem__(self, idx):
        list.__delitem__(self, idx)
        self.changed()

    def __delslice__(self, start, stop):
        list.__delslice__(self, start, stop)
        self.changed()

    def append(self, value):
        list.append(self, MutationObj.coerce(self._key, value))
        self.changed()

    def insert(self, idx, value):
        list.insert(self, idx, MutationObj.coerce(self._key, value))
        self.changed()

    def extend(self, values):
        list.extend(self, (MutationObj.coerce(self._key, v) for v in values))
        self.changed()

    def pop(self, *args, **kw):
        value = list.pop(self, *args, **kw)
        self.changed()
        return value

    def remove(self, value):
        list.remove(self, value)
        self.changed()


def JSONAlchemy(sqltype):
    """
    A type to encode/decode JSON on the fly

    sqltype : string
        The string type for the underlying DB column.

    You can use it like:
    Column(JSONAlchemy(Text(600)))
    """

    class _JSONEncodedObj(JSONEncodedObj):
        impl = sqltype

    return MutationObj.as_mutable(_JSONEncodedObj)


class User(UserMixin, db.Model):
    """
    User model.
    """

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    # TODO: we're putting the datetime into the last seen
    # atribute as UTC, we need a write a function to convert
    # the datetime to the timezone and human readable when
    # format before sending back to the frontent.
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode("utf-8")).hexdigest()
        return "https://www.gravatar.com/avatar/{}?d=identicon&s={}".format(
            digest, size
        )

    def __repr__(self):
        return "<User {}>".format(self.username)


class ScriptType(enum.Enum):
    QA = "Quality Assurance Script"
    TASK = "Task Script"
    REPORT = "Reporting Script"


class JupyterNotebook(db.Model):
    """
    Model for jupyter notebook objects.
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True, unique=True)
    script_type = db.Column(db.Enum(ScriptType))
    path = db.Column(db.String(1024), unique=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    parameters = db.Column(JSONAlchemy(db.Text(1024)))
    author = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __repr__(self):
        return f"<Jupyter Notebook: '{self.name}' from {self.timestamp}>"

    def papermill(self, output_path):
        run = PapermillRun(
            notebook=self.id, triggered_by=current_user.id, output_path=output_path,
        )
        try:
            pm.execute_notebook(self.path, output_path, parameters=self.parameters)
            run.ran_successfully = True
        except:
            run.ran_successfully = True
        finally:
            db.session.add(run)
            db.session.commit()


@login.user_loader
def load_user(id):
    """
    User loader for use by flask_login.
    """
    return User.query.get(int(id))


class PapermillRun(db.Model):
    """
    Model to store runs of notebooks using Papermill.
    """

    id = db.Column(db.Integer, primary_key=True)
    notebook = db.Column(db.Integer, db.ForeignKey("jupyternotebook.id"), index=True)
    triggered_by = db.Column(db.Integer, db.ForeignKey("user.id"))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    output_path = db.Column(db.String(1024), unique=True)
    ran_successfully = db.Column(db.Boolean)
    # TODO: do I want to store a trigger type (sheduled or manual?)
