from flask_wtf import FlaskForm


class module_choice_form(FlaskForm):
    pass
    # MODULE_CHOICES = {}
    # MODULE_CHOICES["Please Choose a Module"] = 0
    # #belongs to current account
    # modules = current_user.get_enrolled_modules()
    # for module in modules:
    #     MODULE_CHOICES[module.code + "  :  " + module.name] = module.code
    #
    # def validate_module(form, module):
    #     if module.data == "Please Choose a Module":
    #         raise ValidationError("Please Choose a Module!")
    #
    # module = SelectField(choices=MODULE_CHOICES)
    # submit = SubmitField()
