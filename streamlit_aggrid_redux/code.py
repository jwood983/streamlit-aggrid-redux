""" This is the class that handles custom JavaScript code that users can embed in AgGrid. Useful
for adding customized number formats (e.g., $1MM instead of $1,000,000)."""
import re

class JsCode:
    def __init__(self, code: str):
        """Wrapper for injecting JavaScript (JS) code into the grid options.
        There is no verification that any embedded code is valid, useful or
        not malicious. Please use at your own risk.
        
        Using this also requires the parameter `allow_unsafe_js=True` in
        the grid_options dictionary.
        
        Parameters
        ----------
        code: str
          The JavaScript code to inject into AgGrid
        """
        self.original_code = code
        
        # this removes comments
        js_comments = r"\/\*[\s\S]*?\*\/|([^\\:]|^)\/\/.*$"
        js_code = re.sub(re.compile(match_js_comment_expression, re.MULTILINE), r"\1", code)
            
        match_js_spaces = r"\s+(?=(?:[^\'\"]*[\'\"][^\'\"]*[\'\"])*[^\'\"]*$)"
        one_line_jscode = re.sub(match_js_spaces, " ", js_code, flags=re.MULTILINE)
        
        one_line_code = re.sub(r"\s+|\r\s*|\n+", " ", one_line_jscode, flags=re.MULTILINE)
        placeholder = "--x_x--0_0--"
        self.injected_code = f"{placeholder}{one_line_code}{placeholder}"

    def __str__(self):
        """ For printing the original code. """
        return self.original_code

    @property
    def code(self):
        """ The code property. """
        return self.injected_code

    def one_liner(self):
        """ Return the one-liner, mostly for verification. """
        return self.injected_code.replace("--x_x--0_0--", "")


def set_date_column(format: str = "YYYY-mm-dd") -> JsCode:
    """ Set the field as a date column. """
    # FIXME: I don't think this is right
    return JsCode("""function(params) {
    if (params) { return params.value.toString('YYYY-mm-dd'); }
    }""")


def set_number_column(is_comma_sep: bool = True) -> Jscode:
    """ Set the field as a number, optionally as not comma separated. """
    return JsCode("""(params) => {
    if (params.value) {
        if (is_comma_sep) {
            return Math.floor(number).toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,')
        }
        return Number(params.value);
    }
    return params.value;
    }"""
