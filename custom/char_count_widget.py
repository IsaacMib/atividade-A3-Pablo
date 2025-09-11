from django import forms
from django.utils.html import format_html


class CharCounterTextarea(forms.Textarea):

    def render(self, name, value, attrs=None, renderer=None):
        # First, combine the widget's default attributes with any passed to this method.
        # This is the correct and robust way to handle attributes.
        final_attrs = self.build_attrs(self.attrs, attrs)

        # Now, get maxlength from the combined attributes dictionary
        maxlength = final_attrs.get('maxlength')

        # Render the textarea using the final, combined attributes
        textarea_html = super().render(name, value, final_attrs, renderer)

        # Create the counter HTML if maxlength was found
        counter_html = ""
        if maxlength:
            counter_html = format_html(
                """
                <div class="charcount-display" data-maxlength="{}">
                    <span class="count">0</span> / {}
                </div>
                """,
                maxlength,
                maxlength
            )

        # Combine them into the final structure
        return format_html(
            """
            <div class="charcount-wrapper">
                {}
                {}
            </div>
            """,
            textarea_html,
            counter_html
        )
