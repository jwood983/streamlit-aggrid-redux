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
          The JavaScript code to inject into AgGrid.
        """
        self.original_code = code

        # this converts lambdas into full functions
        lambda_pattern = rf"[ \t]*\(([a-zA-Z, ]*)\)[ \t]*=>"
        code_no_lambda = re.sub(re.compile(lambda_pattern), r"function(\1)", code)
        
        # this removes comments
        js_comments = r"\/\*[\s\S]*?\*\/|([^\\:]|^)\/\/.*$"
        code_no_comment = re.sub(re.compile(js_comments, re.MULTILINE),
                                 r"\1",
                                 code_no_lambda)

        # this removes spaces between operators (e.g., 'a = b' -> 'a=b')
        match_js_spaces = r"\s+(?=(?:[^\'\"]*[\'\"][^\'\"]*[\'\"])*[^\'\"]*$)"
        code_no_spaces = re.sub(match_js_spaces, " ", code_no_comment, flags=re.MULTILINE)

        # this converts it into a single line function
        one_line_code = re.sub(r"\s+|\r\s*|\n+", " ", code_no_spaces, flags=re.MULTILINE)
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


def set_date_column(locale: str = "en-US") -> JsCode:
    """ Set the field as a date column. """
    return JsCode(f"""function(params) {{
    return (params.value) ? params.value.toLocaleString('{locale}').split('T')[0] : params.value; 
    }}""")


def set_number_column(is_comma_sep: bool = True) -> JsCode:
    """ Set the field as a number, optionally as not comma separated. """
    return JsCode(f"""(params) => {{
    if (params.value) {{
        if ({is_comma_sep}) {{
            return Math.floor(number).toString().replace(/(\d)(?=(\d{{3}})+(?!\d))/g, '$1,')
        }}
        return Number(params.value);
    }}
    return params.value;
    }}""")

                  
def set_float(decimal_places: int = 2) -> JsCode:
    """ Set the field as a number with decimal places. Useful
    for small number, like 100. """
    return JsCode(
        f"""(params) => {{ return (params.value) ? params.value.toFixed({decimal_places}) : params.value; }}"""
    )
