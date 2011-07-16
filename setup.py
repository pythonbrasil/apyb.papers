from setuptools import setup, find_packages
import os

version = '0.5'

setup(name='apyb.papers',
      version=version,
      description="Conference talks management",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='plone apyb pythonbrasil web event conference',
      author='Erico Andrei <erico@simplesconsultoria.com.br>',
      author_email='products@simplesconsultoria.com.br',
      url='https://github.com/pythonbrasil/apyb.papers',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['apyb'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.dexterity',
          'collective.autopermission',
          # -*- Extra requirements: -*-
          'collective.behavior.contactinfo==0.8',
          'collective.z3cform.datagridfield==0.7',
          'collective.z3cform.datetimewidget==1.0.5',
          'plone.formwidget.autocomplete',
          'plone.namedfile',
          'plone.formwidget.namedfile',
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript"],
      paster_plugins = ["ZopeSkel"],

      )
