from jinja2 import Template
from xblock.core import XBlock
from xblock.fields import String, Scope
from learnosity_sdk.request import Init
from learnosity_sdk.utils import Uuid
from web_fragments.fragment import Fragment

try:
    from xblock.utils.resources import ResourceLoader  # pylint: disable=ungrouped-imports
except ModuleNotFoundError:  # For backward compatibility with releases older than Quince.
    from xblockutils.resources import ResourceLoader

RESOURCE_LOADER = ResourceLoader(__name__)

class LearnosityXBlock(XBlock):
    """
    An XBlock that integrates Learnosity Items API to display assessments or questions.
    """

    user_id = String(
        default=Uuid.generate(),
        scope=Scope.user_state,
        help="Unique user identifier for Learnosity."
    )

    user_info = String(
        default='test',
        scope=Scope.user_state,
        help="Unique user identifier for Learnosity."
    )

    session_id = String(
        default=Uuid.generate(),
        scope=Scope.user_state,
        help="Unique session identifier for Learnosity."
    )

    # Additional fields for Studio parameters
    activity_id = String(
        default="test_mcq_with_mr",
        scope=Scope.settings,
        help="Activity id"
    )

    activity_name = String(
        default="Quiz Learnosity",
        scope=Scope.settings,
        help="Activity name"
    )    
    

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
                <h1>{{ self.activity_name }}</h1>    
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
            name='Learnosity Items',
            generated_request=learnosity_init_options
        )

        # Return the generated HTML response as a Fragment
        fragment = Fragment(rendered_html)
        fragment.add_javascript(self._load_learnosity_script())
        fragment.initialize_js('LearnosityXBlock')
        return fragment


    def studio_view(self, context):
        # Render a custom form for the admin interface           

        print('user_id_data', self.user_id)
        html = """
        <form class="xblock-studio-view">
            <label for="activity_id">Activity Id:</label>
            <input type="text" name="activity_id" value="{activity_id}" /><br/>
            <label for="activity_name">activity_name:</label>
            <input type="text" name="activity_name" value="{activity_name}" /><br/>
            <button type="submit">Save</button>
        </form>
        """.format(activity_id=self.activity_id, activity_name=self.activity_name)

        frag = Fragment(html)
        frag.add_javascript(RESOURCE_LOADER.load_unicode('static/js/src/learnosity-studio.js'))
        frag.initialize_js('LearnosityXBlockStudio')
        return frag

    @XBlock.json_handler
    def save_studio_parameters(self, data, suffix=''):
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
        # Security details for the Learnosity API
        security = {
            'consumer_key': 'bqbq2rmMdNzzKW4p',
            'domain': 'local.openedx.io',  # Replace with your actual domain
        }

        # Request parameters for the Items API
        request = {
            'user_id': self.user_id,
            'activity_template_id': self.activity_id,
            'session_id': self.session_id,
            'type': 'submit_practice',
            'state': 'initial',
            'activity_id': self.activity_id,
            'name': self.activity_name
        }

        secret = 'Ml9QTwsa4Ajy3baPKMFKjPLuY35nY0rrQt5ZpIXn'

        # Generate the initialization options using Learnosity SDK
        init = Init(service='items', security=security, secret=secret, request=request)
        return init.generate()

    def _load_learnosity_script(self):
        """
        Load the Learnosity Items API script. {self.user_id}
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
    
    @staticmethod
    def workbench_scenarios():
        """
        A canned scenario for display in the workbench.
        """
        return [("Learosity", "<vertical_demo><learnosity/></vertical_demo>")]