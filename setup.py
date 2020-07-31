from setuptools import setup

VERSION = '0.2.0'
# TODO: xxxxx, hclwriter


# def load_long_description():
#     with open('README.md', 'r') as fh:
#         return fh.read()


if __name__ == '__main__':
    setup(
        name='hclwriter',
        version=VERSION,
        description='xxxxx',
        long_description='xxxxx',
        # long_description=load_long_description(),
        # long_description_content_type='text/markdown',
        author='Daniel Bennett',
        # author_email='',
        url='https://github.com/gulducat/hclwriter',
        keywords=['hcl', 'terraform'],
        classifiers=[
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: Implementation :: CPython',
        ],
        packages=['hclwriter'],
        include_package_data=True,
        package_data={'hclwriter': ['version']},
        # extras_require={
        #     # any version of requests should be fine
        #     'adapter': ['requests']
        # }
    )
