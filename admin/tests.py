from flask_admin.contrib.sqla import ModelView
from flask import url_for, redirect, request
from flask_login import current_user


class TestAdminView(ModelView):
    can_delete = True
    can_edit = True
    can_create = True
    can_view_details = True
    page_size = 20
    column_editable_list = ['title', 'content', 'questions', 'result']
    column_searchable_list = ('title', 'content')

    def is_accessible(self):
        return current_user.is_authenticated and current_user.admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('401', next=request.url))
