"""Some utils for the BluePyParallel package."""

# Copyright 2021-2024 Blue Brain Project / EPFL

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


def replace_values_in_docstring(**kwargs):
    """Decorator to replace keywords in docstrings by the actual value of a variable.

    .. Note::
        The keyword must be enclose by <> in the docstring, like <MyKeyword>.
    """

    def inner(func):
        for k, v in kwargs.items():
            func.__doc__ = func.__doc__.replace(f"<{k}>", str(v))
        return func

    return inner
