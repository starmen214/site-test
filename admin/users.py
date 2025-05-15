from flask_admin.contrib.sqla import ModelView
from flask import url_for, redirect, request
from flask_login import current_user


class UserAdminView(ModelView):
    can_delete = False
    can_edit = True
    can_create = False
    edit_modal = True
    column_searchable_list = ('name', 'email', )
    column_editable_list = ('admin',)

    def is_accessible(self):
        return current_user.is_authenticated and current_user.admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('401', next=request.url))
