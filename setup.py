from setuptools import setup, find_packages

setup(
    name='shasha4',
    version='0.0.9',
    description='For Scraping Naver Finance',
    url='https://github.com/MoonsRainbow/shasha4.git',
    author='MoonsRainbow',
    author_email='Moons_Rainbow@kakao.com',
    license='MoonsRainbow',
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'requests',
        'tqdm',
        'bs4',
        'pandas',
        'konlpy',
        'wordcloud',
        'matplotlib'
    ]
)
