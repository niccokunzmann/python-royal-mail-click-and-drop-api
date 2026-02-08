
.PHONY: stubs

stubs:
	docker pull openapitools/openapi-generator-cli
	docker run --rm -v "${PWD}:/local" openapitools/openapi-generator-cli generate \
		-i /local/click-and-drop-api-v1.yaml \
		-g python \
		-o /local/
