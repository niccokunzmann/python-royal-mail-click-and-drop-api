# Maintenance

Instructions for maintaining the package.

## Download the API definition

This downloads the current definition for the API.

```sh
make api-definition
```

## Generate the stub files

Install Docker: https://docs.docker.com/get-docker/

```sh
make stubs
```

## Generate the documentation

```sh
make html
```

Or live preview:

```sh
make livehtml
```
