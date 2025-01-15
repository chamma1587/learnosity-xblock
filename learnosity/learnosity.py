from jinja2 import Template
from xblock.core import XBlock
from xblock.fields import String, Scope
from learnosity_sdk.request import Init
from learnosity_sdk.utils import Uuid
from web_fragments.fragment import Fragment

class LearnosityXBlock(XBlock):
    """
    An XBlock that integrates Learnosity Items API to display assessments or questions.
    """

    # Define necessary fields for the XBlock
    activity_id = String(
        default="test_mcq_with_mr",
        scope=Scope.content,
        help="The Learnosity activity template ID."
    )

    user_id = String(
        default=Uuid.generate(),
        scope=Scope.user_state,
        help="Unique user identifier for Learnosity."
    )

    session_id = String(
        default=Uuid.generate(),
        scope=Scope.user_state,
        help="Unique session identifier for Learnosity."
    )

    # Additional fields for Studio parameters
    parameter_one = String(
        default="Default Parameter One",
        scope=Scope.settings,
        help="An example parameter for the XBlock."
    )

    parameter_two = String(
        default="Default Parameter Two",
        scope=Scope.settings,
        help="Another example parameter for the XBlock."
    )

    @staticmethod
    def workbench_scenarios():
        """
        A scenario for testing the Learnosity in the Workbench.
        """
        return [
            ("Learnosity",
            """<learnosity activity_id="example_activity_id"/>"""
            )
        ]

    def student_view(self, context=None):
        """
        The primary view of the XBlock, shown to students.
        Renders the Learnosity assessment using the Items API.
        """
        # Generate Learnosity initialization options
        learnosity_init_options = self._generate_learnosity_init()

        # Define the page HTML as a Jinja2 template
        template = Template("""
        <!DOCTYPE html>
        <html>
            <body>
                <h1>{{ name }}</h1>
                <!-- Items API will render the assessment app into this div. -->
                <div id="learnosity_assess"></div>
                <!-- Load the Items API library. -->
                <script src="https://items.learnosity.com/?latest-lts"></script>
                <!-- Initiate Items API  -->
                <script>
                    var itemsApp = LearnosityItems.init({{ generated_request }});
                </script>
            </body>
        </html>
        """)

        # Render the template with the required variables
        rendered_html = template.render(
            name='Standalone Items API Example', 
            generated_request=learnosity_init_options
        )

        # Return the generated HTML response as a Fragment
        fragment = Fragment(rendered_html)
        fragment.add_javascript(self._load_learnosity_script())
        fragment.initialize_js('LearnosityXBlock')
        return fragment


    def studio_view(self, context):
        # Render a custom form for the admin interface
        html = """
        <form class="xblock-studio-view">
            <label for="parameter_one">Parameter One:</label>
            <input type="text" name="parameter_one" value="{parameter_one}" />
            <label for="parameter_two">Parameter Two:</label>
            <input type="text" name="parameter_two" value="{parameter_two}" />
            <button type="submit">Save</button>
        </form>
        """.format(parameter_one=self.parameter_one, parameter_two=self.parameter_two)

        frag = Fragment(html)
        frag.add_javascript(self.resource_string("static/js/learnosity-studio.js"))
        frag.initialize_js('LearnosityXBlockStudio')
        return frag

    @XBlock.json_handler
    def save_studio_parameters(self, data, suffix=''):
        """
        Handler to save parameters from the Studio view.
        """
        self.parameter_one = data.get('parameter_one', self.parameter_one)
        self.parameter_two = data.get('parameter_two', self.parameter_two)
        return {"result": "success"}



    def _generate_learnosity_init(self):
        """
        Generate Learnosity initialization options using the Learnosity SDK.
        """
        # Security details for the Learnosity API
        security = {
            'consumer_key': 'bqbq2rmMdNzzKW4p',
            'domain': 'local.openedx.io',  # Replace with your actual domain
        }

        # Request parameters for the Items API
        request = {
            'user_id': self.user_id,  # Dynamically generated user_id
            'activity_template_id': 'test_mcq_with_mr',
            'session_id': self.session_id,  # Dynamically generated session_id
            'type': 'submit_practice',
            'state': 'initial',
            'activity_id': 'test_mcq_with_mr',
            'name': 'Items API Quickstart',
        }

        secret = 'Ml9QTwsa4Ajy3baPKMFKjPLuY35nY0rrQt5ZpIXn'

        # Generate the initialization options using Learnosity SDK
        init = Init(service='items', security=security, secret=secret, request=request)
        return init.generate()

    def _load_learnosity_script(self):
        """
        Load the Learnosity Items API script.
        """
        return """
        (function() {
            var script = document.createElement('script');
            script.src = 'https://items.learnosity.com/';
            script.onload = function() {
                LearnosityItems.init(learnosityInitOptions);
            };
            document.head.appendChild(script);
        })();
        """
