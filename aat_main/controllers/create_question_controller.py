from flask import Blueprint

# from aat_main.forms.question_form import question_form

create_question_blueprint = Blueprint('create_question_blueprint', __name__, template_folder='../views/question')


@create_question_blueprint.route('/', methods=['GET', 'POST'])
def create_question():
    pass
    # form = question_form()
    # if form.validate_on_submit():
    #     Question.create_question(form.name.data, form.description.data, form.course.data)
    #     return redirect(url_for('assessment_bp.assessments'))
    #
    # return render_template("create_question.html", form=form)
    # try:
    #     return render_template('question.html')
    # except TemplateError:
    #     raise NotFoundException()
