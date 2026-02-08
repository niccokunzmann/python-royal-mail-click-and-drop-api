
.PHONY: stubs api-definition stubs-help image

#
# Download the API definition file
#
api-definition:
	wget -O click-and-drop-api-v1.yaml https://api.parcel.royalmail.com/doc/v1/click-and-drop-api-v1.yaml

image:
	docker pull openapitools/openapi-generator-cli


#
# Generate the source code
#
stubs: image
	docker run --rm -v "$${PWD}:/local" -u $$(id -u):$$(id -g) openapitools/openapi-generator-cli generate \
		-i /local/click-and-drop-api-v1.yaml \
		-g python \
		-o /local/ \
		--package-name click_and_drop_api \
		--git-host https://github.com \
		--git-user-id niccokunzmann \
		--git-repo-id python-royal-mail-click-and-drop-api \
		--minimal-update
# 	sudo chown -R $(id -u):$(id -g) .

stubs-help: image
	docker run --rm openapitools/openapi-generator-cli help generate	
