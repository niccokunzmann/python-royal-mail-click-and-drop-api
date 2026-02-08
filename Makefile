
.PHONY: stubs api-definition

#
# Download the API definition file
#
api-definition:
	wget -O click-and-drop-api-v1.yaml https://api.parcel.royalmail.com/doc/v1/click-and-drop-api-v1.yaml

#
# Generate the source code
#
stubs:
	docker pull openapitools/openapi-generator-cli
	docker run --rm -v "${PWD}:/local" openapitools/openapi-generator-cli generate \
		-i /local/click-and-drop-api-v1.yaml \
		-g python \
		-o /local/ \
		--package-name click_and_drop_api \
		--git-host https://github.com \
		--git-user-id niccokunzmann \
		--git-repo-id python-royal-mail-click-and-drop-api

