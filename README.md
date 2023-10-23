# streamlit-aggrid-redux
For those that are familiar with [Pablo Fonseca's work][old_github_link] integrating the JavaScript package [AgGrid][ag_grid_link] into [streamlit][streamlit_link], you are probably also aware that Pablo has effectively ceased development without naming any maintainers of the module. Hence, many users are left developing their own branches as well as some who have attempted creating their own implementations. This is one of the latter.

**NOTE**: There is significant deviation betweeen Pablo's API and this package's API, it is not a 1:1 mapping between the two but instead a re-implementation of the original code with intent of following Python best practices (e.g., following [pep8][pep8_link]).

# Installation
## From PyPI
Installation from pypi is fairly trivial:

```python
python -m pip install streamlit-aggrid-redux
```

Versioning of this module follows YYYY.MM format, so if you want to install particular versions, you would add the `==YYYY.MM` suffix for the particular version.

I have tested this only on 3.10 an d 3.11 versions of Python, so using an older version may not work.

## From source
This is only recommended if you want to aid in developing this package. Download the repository in whatever means you want (e.g., using the Download > Zip or via `git clone ...`). Make your edits and then, to test your changes, you need to build the JS code using npm. This is done by navidating to the frontend folder in terminal/command prompt an running `npm run build`.

# Usage
After installation, this is used very much like the earlier work

```python
import streamlit as st
import streamlit_aggrid_redux as sgr

frame = load_data(...)

# display without any options
sgr.ag_grid(frame)

# display with default grid options (should be identical to above)
sgr.ag_grid(
    frame,
    sgr.GridOptionsBuilder.from_data(frame)
)
```

# Development
I do have a very nice career that takes up 50-60 hours a week and a (large) family on top, so my free time is mostly limited to nights and weekends. I fully intend to support this module for as long as I can, but be aware that responses to Issues/PRs/etc might take a few days, so please be patient.

I do hope that if, for some reason, I am no longer interested in maintaining this code, that I will name some additional maintainers to help support it long-term.

## Community Support
If you find you want a certain feature added/removed/modified or have discovered a bug, please open up an Issue with a minimum working example (MWE) and explain both the expected and actual behavior. I'm a far better Python programmer than JS programmer, but I'll do my best in working on any recommendations.

That said, if you know how to write the code, please support the package and the community by adding it yourself! You'll probably feel a lot better knowing you helped out (probably) billions of people who will use this or simply see the results!


[ag_grid_link]: https://www.ag-grid.com
[pep8_link]: https://pep8.org
[old_github_link]: https://github.com/PablocFonseca/streamlit-aggrid
[streamlit_link]: https://streamlit.io/