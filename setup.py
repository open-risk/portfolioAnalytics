# encoding: utf-8

# (c) 2017-2024 Open Risk (https://www.openriskmanagement.com)
#
# portfolioAnalytics is licensed under the Apache 2.0 license a copy of which is included
# in the source distribution of portfolioAnalytics. This is notwithstanding any licenses of
# third-party software included in this distribution. You may not use this file except in
# compliance with the License.
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.


from codecs import open

from setuptools import setup

__version__ = '0.4'

ver = __version__

long_descr = open('docs/source/description.rst', 'r', encoding='utf8').read()

setup(name='creditPortfolioAnalytics',
      version=ver,
      description='A Python powered library for calculating semi-analytic credit portfolio loss metrics',
      long_description=long_descr,
      long_description_content_type='text/x-rst',
      author='Open Risk',
      author_email='info@openriskmanagement.com',
      packages=['portfolioAnalytics', 'datasets', 'examples.python'],
      include_package_data=True,
      url='https://github.com/open-risk/portfolioAnalytics',
      install_requires=[
          'pandas',
          'numpy',
          'scipy',
          'statsmodels',
          'sympy',
          'matplotlib'
      ],
      zip_safe=False,
      provides=['portfolioAnalytics'],
      classifiers=[
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'Intended Audience :: Financial and Insurance Industry',
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: Apache Software License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3 :: Only',
          'Programming Language :: Python :: 3.10',
          'Topic :: Scientific/Engineering',
          'Topic :: Scientific/Engineering :: Information Analysis'
      ]

      )
