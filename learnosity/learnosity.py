from jinja2 import Template
from xblock.core import XBlock
from xblock.fields import String, Scope
from learnosity_sdk.request import Init
from learnosity_sdk.utils import Uuid
from web_fragments.fragment import Fragment

try:
    from xblock.utils.resources import ResourceLoader  # For Open edX versions after Quince
except ModuleNotFoundError:
    from xblockutils.resources import ResourceLoader  # For backward compatibility

RESOURCE_LOADER = ResourceLoader(__name__)


class LearnosityXBlock(XBlock):
    """
    An XBlock that integrates the Learnosity Items API to display assessments or questions.
    """

    # Persistent fields
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

    # Studio-configurable fields
    activity_id = String(
        default="test_mcq_with_mr",
        scope=Scope.settings,
        help="Activity ID for Learnosity Items API."
    )

    activity_name = String(
        default="Quiz Learnosity",
        scope=Scope.settings,
        help="Name of the Learnosity activity."
    )

    def student_view(self, context=None):
        """
        The primary view of the XBlock, shown to students.
        Renders the Learnosity assessment using the Items API.
        """
        # Generate Learnosity initialization options
        learnosity_init_options = self._generate_learnosity_init()

        # HTML template for student view
        template = Template("""
        <!DOCTYPE html>
        <html>
            <body>
                <h1>{{ activity_name }}</h1>
                <div id="learnosity_assess"></div>
                <!-- Load the Items API library -->
                <script src="https://items.learnosity.com/"></script>
                <!-- Initiate Items API -->
                <script>
                    var learnosityInitOptions = {{ generated_request | safe }};
                    var itemsApp = LearnosityItems.init(learnosityInitOptions);
                </script>
            </body>
        </html>
        """)

        # Render the template with required variables
        rendered_html = template.render(
            activity_name=self.activity_name,
            generated_request=learnosity_init_options
        )

        # Return the rendered HTML as a Fragment
        fragment = Fragment(rendered_html)
        return fragment

    def studio_view(self, context=None):
        """
        Studio view for course authors to configure the XBlock.
        """
        # HTML form for Studio configuration
        html = f"""
        <form class="xblock-studio-view" method="POST" action="#">
            <label for="activity_id">Activity ID:</label>
            <input type="text" name="activity_id" value="{self.activity_id}" required/><br/>
            <small>Provide the Learnosity activity template ID (e.g., "activity_xyz").</small><br/>
            <label for="activity_name">Activity Name:</label>
            <input type="text" name="activity_name" value="{self.activity_name}" required/><br/>
            <small>Provide a name for the activity.</small><br/>
            <button type="submit">Save</button>
        </form>
        """

        # Create Fragment for Studio view
        fragment = Fragment(html)
        fragment.add_javascript(RESOURCE_LOADER.load_unicode('static/js/src/learnosity-studio.js'))
        fragment.initialize_js('LearnosityXBlockStudio')
        return fragment

    @XBlock.json_handler
    def studio_submit(self, data, suffix=''):
        """
        Handler to save parameters from the Studio view.
        """
        self.activity_id = data.get('activity_id', self.activity_id)
        self.activity_name = data.get('activity_name', self.activity_name)
        return {"result": "success"}

    def _generate_learnosity_init(self):
        """
        Generate Learnosity initialization options using the Learnosity SDK.
        """
        # Security details (replace with environment variables in production)
        security = {
            'consumer_key': 'bqbq2rmMdNzzKW4p',  # Replace with env variable
            'domain': 'local.openedx.io',        # Replace with your actual domain
        }

        # Request parameters for Learnosity Items API
        request = {
            'user_id': self.user_id,
            'activity_template_id': self.activity_id,
            'session_id': self.session_id,
            'type': 'submit_practice',
            'state': 'initial',
            'activity_id': self.activity_id,
            'name': self.activity_name
        }

        # Secret key (replace with environment variable in production)
        secret = 'Ml9QTwsa4Ajy3baPKMFKjPLuY35nY0rrQt5ZpIXn'

        # Generate the initialization string
        init = Init(service='items', security=security, secret=secret, request=request)
        return init.generate()

    @staticmethod
    def workbench_scenarios():
        """
        A scenario for testing the Learnosity integration in the Workbench.
        """
        return [
            ("Learnosity XBlock Test",
             """<learnosity activity_id="example_activity_id"/>"""
             )
        ]
