# Contributing

Thanks for your interest in contributing!
Your suggestions are welcome!

## Development setup

You need those dependencies installed:

- [git](https://git-scm.com/)
- [Python 3](https://www.python.org/)
- [make](https://www.gnu.org/software/make/)
- [pre-commit](https://pre-commit.com/)
- [tox](https://tox.readthedocs.io/en/latest/)

Clone the repository:

```bash
git clone https://github.com/niccokunzmann/python-royal-mail-click-and-drop-api.git
cd python-royal-mail-click-and-drop-api
pre-commit install
```

## Running tests

```sh
tox
```

## Create documentation

Create the site:

```sh
make html
```

View the site with a server:

```sh
make livehtml
```
